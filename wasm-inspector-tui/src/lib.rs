pub mod wasm;
pub mod tui;

pub use wasm::{disassemble, parse_module, WasmModule};
pub use tui::run_tui;