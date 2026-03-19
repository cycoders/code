use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use wasmparser::{
    BinaryReader, ExternalKind, Import as WasmImport, Instruction, Parser, Payload, SectionReader,
};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Import {
    pub module: String,
    pub field: String,
    pub sig: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Export {
    pub name: String,
    pub kind: String,
    pub idx: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct FuncInfo {
    pub idx: usize,
    pub is_import: bool,
    pub size: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WasmModule {
    pub imports: Vec<Import>,
    pub exports: Vec<Export>,
    pub funcs: Vec<FuncInfo>,
    pub calls: Vec<Vec<usize>>,
    pub callers: Vec<Vec<usize>>,
    #[serde(skip)]
    pub bodies: Vec<Option<Vec<u8>>>,
}

impl std::fmt::Display for WasmModule {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        serde_json::to_writer_pretty(f, self)
    }
}

pub fn parse_module(bytes: &[u8]) -> Result<WasmModule> {
    let mut imports = vec![];
    let mut exports = vec![];
    let mut num_import_funcs = 0usize;
    let mut func_bodies = vec![];

    let mut parser = Parser::new(0);
    for payload in parser.parse_all(bytes) {
        let payload = payload.context("Invalid WASM payload")?;
        match payload {
            Payload::ImportSection(reader) | Payload::ImportSectionWithRange(reader) => {
                for imp in reader {
                    let imp = imp.context("Invalid import")?;
                    if imp.kind.tag() == ExternalKind::Func as u8 {
                        num_import_funcs += 1;
                        imports.push(Import {
                            module: String::from_utf8_lossy(imp.module).to_string(),
                            field: String::from_utf8_lossy(imp.field).to_string(),
                            sig: format!("func[{}]", imp.ty),
                        });
                    }
                }
            }
            Payload::ExportSection(reader) => {
                for exp in reader {
                    let exp = exp.context("Invalid export")?;
                    exports.push(Export {
                        name: String::from_utf8_lossy(exp.name).to_string(),
                        kind: format!("{:?}", exp.kind),
                        idx: exp.index,
                    });
                }
            }
            Payload::CodeSectionStart { .. } | Payload::CodeSection(reader) => {
                for code in reader {
                    let (_, body) = code.context("Invalid code")?;
                    func_bodies.push(body.code.to_vec());
                }
            }
            _ => {}
        }
    }

    let num_local_funcs = func_bodies.len();
    let total_funcs = num_import_funcs + num_local_funcs;

    let mut funcs = vec![FuncInfo::default(); total_funcs];
    let mut bodies_all = vec![None; total_funcs];

    // Imports
    for i in 0..num_import_funcs {
        funcs[i].idx = i;
        funcs[i].is_import = true;
    }

    // Locals
    for i in 0..num_local_funcs {
        let idx = num_import_funcs + i;
        funcs[idx].idx = idx;
        funcs[idx].is_import = false;
        funcs[idx].size = func_bodies[i].len();
        bodies_all[idx] = Some(func_bodies[i]);
    }

    // Build call graph (only direct Call, ignore indirect)
    let mut calls = vec![vec![]; total_funcs];
    let mut callers = vec![vec![]; total_funcs];
    for local_idx in 0..num_local_funcs {
        let caller_idx = num_import_funcs + local_idx;
        let Some(body) = &func_bodies[local_idx] else { continue };

        let mut reader = BinaryReader::new(body, 0);
        let mut skip_locals = reader.read_var_u32().unwrap_or(0) as usize;
        for _ in 0..skip_locals {
            let _ = reader.read_var_u32();
            let _ = reader.read_var_u7();
        }

        while let Ok(Some(instr)) = reader.read_operator() {
            if let Instruction::Call(idx) = instr {
                let callee = idx.0 as usize;
                if callee < total_funcs {
                    calls[caller_idx].push(callee);
                    callers[callee].push(caller_idx);
                }
            }
        }
    }

    // Dedup
    for edges in [&mut calls, &mut callers] {
        for edge_list in edges.iter_mut() {
            edge_list.sort_unstable();
            edge_list.dedup();
        }
    }

    Ok(WasmModule {
        imports,
        exports,
        funcs,
        calls,
        callers,
        bodies: bodies_all,
    })
}

pub fn disassemble(body: &[u8]) -> Vec<String> {
    let mut lines = vec!["Disassembly:".to_string()];
    let mut reader = BinaryReader::new(body, 0);

    if let Ok(num_locals) = reader.read_var_u32() {
        lines.push(format!("locals: {} groups", num_locals));
        for _ in 0..num_locals as usize {
            if let (Ok(count), Ok(ty)) = (reader.read_var_u32(), reader.read_var_u7()) {
                lines.push(format!("  {} x {:?}", count, ty));
            } else {
                break;
            }
        }
    }

    lines.push("code:".to_string());
    while let Ok(Some(instr)) = reader.read_operator() {
        lines.push(format!("  {:?}", instr));
    }
    lines.push("end".to_string());

    lines
}
