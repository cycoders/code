use crate::scanner::FileInfo;
use crate::tui::DupeTable;
use crossterm::event::KeyCode::{Char, Esc};
use crossterm::event::KeyEvent;
use ratatui::layout::{Constraint, Direction, Layout};
use ratatui::style::{Color, Style};
use ratatui::widgets::{Block, Borders, Paragraph};
use ratatui::Frame;
use std::collections::HashMap;

pub struct App {
    dupes: Vec<(String, Vec<FileInfo>)>,
    current_group: usize,
    selected_files: Vec<bool>,
    dry_run: bool,
    message: String,
    deleted_count: usize,
}

impl App {
    pub fn new(dupes: HashMap<String, Vec<FileInfo>>, dry_run: bool) -> Self {
        let mut dvec: Vec<(String, Vec<FileInfo>)> = dupes.into_iter().collect();
        dvec.sort_by_key(|(_, g)| std::cmp::Reverse(g[0].size * g.len() as u64));
        let selected_files = vec![false; dvec[0].1.len()];
        Self {
            dupes: dvec,
            current_group: 0,
            selected_files,
            dry_run,
            message: "Use ↑↓ to navigate, space to select, d to delete".to_string(),
            deleted_count: 0,
        }
    }

    pub fn draw(&mut self, f: &mut Frame) {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Percentage(80), Constraint::Percentage(20)].as_ref())
            .split(f.size());

        let group_info = format!(
            "Group {}/{} ({} files, {} GB total)",
            self.current_group + 1,
            self.dupes.len(),
            self.dupes[self.current_group].1.len(),
            self.dupes[self.current_group].1.iter().map(|fi| fi.size).sum::<u64>() as f64 / 1e9
        );

        let table = DupeTable::new(&self.dupes[self.current_group].1, &self.selected_files);
        f.render_widget(table, chunks[0]);

        let help = Paragraph::new(&self.message)
            .block(Block::default().title(group_info).borders(Borders::ALL));
        f.render_widget(help, chunks[1]);
    }

    pub fn handle_key(&mut self, key: KeyEvent) -> bool {
        match key.code {
            Char('q') | Esc => true,
            Char('j') | crossterm::event::KeyCode::Down => {
                self.current_group = (self.current_group + 1).min(self.dupes.len() - 1);
                self.selected_files = vec![false; self.dupes[self.current_group].1.len()];
            }
            Char('k') | crossterm::event::KeyCode::Up => {
                if self.current_group > 0 {
                    self.current_group -= 1;
                    self.selected_files = vec![false; self.dupes[self.current_group].1.len()];
                }
            }
            Char(' ') => {
                let idx = self.selected_files.len().min(10); // simplistic
                self.selected_files[idx % self.selected_files.len()] = !self.selected_files[idx % self.selected_files.len()];
            }
            Char('d') => {
                let group = &mut self.dupes[self.current_group].1;
                let mut to_delete = vec![];
                for (i, sel) in self.selected_files.iter().enumerate() {
                    if *sel {
                        if !self.dry_run {
                            if let Err(e) = std::fs::remove_file(&group[i].path) {
                                self.message = format!("Delete failed: {}", e);
                            } else {
                                self.deleted_count += 1;
                            }
                        }
                        to_delete.push(i);
                    }
                }
                for i in to_delete.iter().rev() {
                    group.remove(*i);
                }
                if group.is_empty() {
                    self.dupes.remove(self.current_group);
                }
                self.message = if self.dry_run { "Dry run: would delete".to_string() } else { format!("Deleted {} files", self.deleted_count) };
            }
            _ => {},
        }
        false
    }
}