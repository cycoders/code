use anyhow::Result;
use crossterm::event::{self, KeyCode, KeyEvent};
use crossterm::terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen};
use crossterm::{execute, ExecutableCommand};
use file_deduper_cli::scanner::FileInfo;
use ratatui::backend::CrosstermBackend;
use ratatui::Terminal;
use std::collections::HashMap;
use std::io;
use std::path::PathBuf;

pub mod app;
pub use app::App;

pub fn run_tui(mut dupes: HashMap<String, Vec<FileInfo>>, dry_run: bool) -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let mut app = App::new(dupes, dry_run);

    loop {
        terminal.draw(|f| app.draw(f))?;

        if let event::Event::Key(key) = event::read()? {
            if app.handle_key(key) {
                break;
            }
        }
    }

    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    Ok(())
}
