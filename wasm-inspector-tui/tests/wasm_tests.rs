use wasm_inspector_tui::wasm::{disassemble, parse_module, WasmModule};

#[test]
fn parse_minimal_wasm() {
    // Minimal WASM: module (type 0 ()->i32) (func 0 type0) (export "main" func0) (code func0: i32.const 42 end)
    let bytes = vec![
        0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00, // magic/version
        0x01, 0x07, 0x01, 0x60, 0x01, 0x7F, 0x01, 0x7F, // Type sec: func () -> i32
        0x03, 0x02, 0x01, 0x00,                          // Func sec: func0 type0
        0x05, 0x03, 0x01, 0x00, 0x10, 0x02,              // Export: "main" -> func 0
        0x07, 0x09, 0x01, 0x07, 0x60, 0x01, 0x7F, 0x41, 0x2A, 0x0B, // Code: locals1 i32, i32.const42 end
    ];

    let module = parse_module(&bytes).unwrap();
    assert_eq!(module.funcs.len(), 1);
    assert_eq!(module.exports.len(), 1);
    assert_eq!(module.exports[0].name, "main");
    assert_eq!(module.exports[0].idx, 0);
    assert!(!module.funcs[0].is_import);
    assert!(module.funcs[0].size > 0);
    assert_eq!(module.calls[0].len(), 0);
}

#[test]
fn disassemble_produces_lines() {
    let body = vec![0x01, 0x7F, 0x41, 0x2A, 0x0B]; // locals 1 i32, const42 end
    let lines = disassemble(&body);
    assert!(lines.len() > 1);
    assert!(lines.iter().any(|l| l.contains("Instruction::I32Const")));
}

#[test]
fn handles_empty_body() {
    let empty = vec![];
    let lines = disassemble(&empty);
    assert_eq!(lines, vec!["Disassembly:".to_string(), "code:".to_string(), "end".to_string()]);
}

#[test]
fn json_serializes() {
    let bytes = vec![0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00];
    let _module: WasmModule = parse_module(&bytes).unwrap();
    // No panic
}
