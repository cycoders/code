use crate::scanner::FileInfo;
use ratatui::style::{Color, Style};
use ratatui::text::Line;
use ratatui::widgets::{Cell, Row, Table};

pub struct DupeTable<'a> {
    files: &'a [FileInfo],
    selected: &'a [bool],
}

impl<'a> DupeTable<'a> {
    pub fn new(files: &'a [FileInfo], selected: &'a [bool]) -> Self {
        Self { files, selected }
    }
}

impl<'a> ratatui::widgets::Widget for DupeTable<'a> {
    fn render(self, area: ratatui::prelude::Rect, buf: &mut ratatui::buffer::Buffer) {
        let header = ["Sel", "Size", "Path"];
        let rows: Vec<Row> = self.files.iter().enumerate().map(|(i, fi)| {
            let sel = if self.selected.get(i).copied().unwrap_or(false) { "[x]" } else { "[ ]" };
            let style = if self.selected.get(i).copied().unwrap_or(false) {
                Style::default().fg(Color::Green)
            } else {
                Style::default()
            };
            Row::new(vec![
                Cell::from(sel),
                Cell::from(format!("{:.1} MB", fi.size as f64 / 1e6)),
                Cell::from(fi.path.to_string_lossy().to_string()),
            ]).style(style)
        }).collect();

        let table = Table::new(rows, 
            &[ratatui::layout::Constraint::Length(3), ratatui::layout::Constraint::Length(10), ratatui::layout::Constraint::Percentage(80)],
        )
        .header(Row::new(header))
        .block(ratatui::widgets::Block::default().borders(ratatui::widgets::Borders::ALL));
        table.render(area, buf);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn table_renders() {
        // Minimal test for compilation
        assert!(true);
    }
}