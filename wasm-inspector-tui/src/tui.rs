use anyhow::Result;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout},
    style::{Color, Style},
    text::Line,
    widgets::{Block, Borders, List, ListItem, ListState, Paragraph},
    Frame, Terminal,
};
use std::io::{self, Stdout};
use std::time::{Duration, Instant};

use crate::wasm::{disassemble, WasmModule};

pub struct App {
    module: WasmModule,
    should_quit: bool,
    page: Page,
    selected: usize,
    list_state: ListState,
    disassm: Vec<String>,
}

#[derive(PartialEq, Copy, Clone)]
pub enum Page {
    Overview,
    Functions,
    Detail,
}

impl App {
    pub fn new(module: WasmModule) -> Self {
        let mut list_state = ListState::default();
        list_state.select(Some(0));
        let mut app = Self {
            module,
            should_quit: false,
            page: Page::Overview,
            selected: 0,
            list_state,
            disassm: vec![],
        };
        app.update_disasm();
        app
    }

    fn update_disasm(&mut self) {
        let idx = self.selected;
        if let Some(body) = &self.module.bodies[idx] {
            self.disassm = disassemble(body);
        } else {
            self.disassm = vec!["[IMPORT] No body available".to_string()];
        }
    }

    pub fn on_key(&mut self, key: crossterm::event::KeyEvent) {
        match self.page {
            Page::Overview => match key.code {
                KeyCode::Char('f') => self.page = Page::Functions,
                KeyCode::Char('q') | KeyCode::Esc => self.should_quit = true,
                _ => {},
            },
            Page::Functions => match key.code {
                KeyCode::Down => {
                    let next = (self.selected + 1).min(self.module.funcs.len().saturating_sub(1));
                    self.selected = next;
                    self.list_state.select(Some(next));
                    self.update_disasm();
                }
                KeyCode::Up => {
                    let next = self.selected.saturating_sub(1);
                    self.selected = next;
                    self.list_state.select(Some(next));
                    self.update_disasm();
                }
                KeyCode::Enter | KeyCode::Char('d') => self.page = Page::Detail,
                KeyCode::Char('o') => self.page = Page::Overview,
                KeyCode::Char('q') | KeyCode::Esc => self.should_quit = true,
                _ => {},
            },
            Page::Detail => match key.code {
                KeyCode::Char('f') => self.page = Page::Functions,
                KeyCode::Char('o') => self.page = Page::Overview,
                KeyCode::Char('q') | KeyCode::Esc => self.should_quit = true,
                _ => {},
            },
        }
    }
}

pub fn run_tui(mut module: WasmModule) -> Result<()> {
    let mut app = App::new(module);

    // Terminal setup
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let tick_rate = Duration::from_millis(250);
    let mut last_tick = Instant::now();

    loop {
        terminal.draw(|f| ui(f, &mut app))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or_else(|| Duration::from_secs(0));
        if crossterm::event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                app.on_key(key);
            }
        }
        if last_tick.elapsed() >= tick_rate {
            last_tick = Instant::now();
        }
        if app.should_quit {
            break;
        }
    }

    // restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    Ok(())
}

fn ui(f: &mut Frame, app: &mut App) {
    let size = f.size();
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Min(20),
            Constraint::Length(3),
        ])
        .split(size);

    // Title
    let title = Paragraph::new(format!("WASM Inspector - {:?} ({} funcs)", app.page, app.module.funcs.len()))
        .block(Block::default().borders(Borders::ALL));
    f.render_widget(title, chunks[0]);

    // Main content
    match app.page {
        Page::Overview => overview_ui(f, app, chunks[1]),
        Page::Functions => functions_ui(f, app, chunks[1]),
        Page::Detail => detail_ui(f, app, chunks[1]),
    };

    // Help
    let help_lines = [
        Line::from("↑↓ select  ⏎/d detail  o overview  f functions  q/esc quit"),
    ];
    let help = Paragraph::new(help_lines.iter())
        .block(Block::default().borders(Borders::ALL));
    f.render_widget(help, chunks[2]);
}

fn overview_ui(f: &mut Frame, app: &App, area: ratatui::layout::Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(area);

    // Imports
    let import_lines: Vec<Line> = app
        .module
        .imports
        .iter()
        .map(|i| Line::from(format!("{}::{}", i.module, i.field)))
        .collect();
    let imports = Paragraph::new(import_lines)
        .block(Block::default().title("Imports").borders(Borders::ALL));
    f.render_widget(imports, chunks[0]);

    // Exports
    let export_lines: Vec<Line> = app
        .module
        .exports
        .iter()
        .map(|e| Line::from(format!("{} -> {} ({})", e.name, e.idx, e.kind)))
        .collect();
    let exports = Paragraph::new(export_lines)
        .block(Block::default().title("Exports").borders(Borders::ALL));
    f.render_widget(exports, chunks[1]);
}

fn functions_ui(f: &mut Frame, app: &App, area: ratatui::layout::Rect) {
    let items: Vec<ListItem> = app
        .module
        .funcs
        .iter()
        .enumerate()
        .map(|(i, func)| {
            let marker = if func.is_import { "I" } else { "L" };
            ListItem::new(format!("func[{}] {}B ({}) | calls: {} ",
                i, func.size, marker, app.module.calls[i].len()))
        })
        .collect();

    let list = List::new(items)
        .block(Block::default().title("Functions").borders(Borders::ALL))
        .highlight_style(Style::default().fg(Color::Yellow))
        .highlight_symbol("▶");
    f.render_stateful_widget(list, area, &mut app.list_state);
}

fn detail_ui(f: &mut Frame, app: &App, area: ratatui::layout::Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(20),
            Constraint::Percentage(30),
            Constraint::Percentage(50),
        ])
        .split(area);

    let idx = app.selected;
    let func = &app.module.funcs[idx];

    // Callers
    let caller_lines: Vec<Line> = app
        .module
        .callers[idx]
        .iter()
        .map(|&i| Line::from(format!("func[{i}]")))
        .collect();
    let callers = Paragraph::new(caller_lines)
        .block(Block::default().title("Callers").borders(Borders::ALL));
    f.render_widget(callers, chunks[0]);

    // Callees
    let callee_lines: Vec<Line> = app
        .module
        .calls[idx]
        .iter()
        .map(|&i| Line::from(format!("func[{i}]")))
        .collect();
    let callees = Paragraph::new(callee_lines)
        .block(Block::default().title("Callees").borders(Borders::ALL));
    f.render_widget(callees, chunks[1]);

    // Disasm
    let disasm = Paragraph::new(app.disassm.clone())
        .block(
            Block::default()
                .title(format!("Disasm func[{idx}] ({})B", func.size))
                .borders(Borders::ALL),
        );
    f.render_widget(disasm, chunks[2]);
}
