use anyhow::{Context, Result};
use clap::Parser;
use std::fs;
use wasm_inspector_tui::{parse_module, run_tui, WasmModule};

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Path to .wasm file
    wasm_file: String,

    #[arg(short, long, help = "Export as JSON instead of TUI")]
    json: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let bytes = fs::read(&args.wasm_file)
        .with_context(|| format!("Failed to read {}", args.wasm_file))?
        .into_boxed_slice();

    let module: WasmModule = parse_module(&bytes)
        .with_context(|| "Failed to parse WASM module")?;

    if args.json {
        println!("{module}");
    } else {
        run_tui(module)?;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verify_cli() {
        use clap::CommandFactory;
        Args::command().debug_assert();
    }
}