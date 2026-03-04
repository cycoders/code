use anyhow::{Context, Result};
use clap::Parser;
use file_deduper_cli::{config::Config, scanner::scan_duplicates, tui::run_tui};
use std::path::{Path, PathBuf};

#[derive(Parser)]
#[command(name = "file-deduper-cli", about = "Fast duplicate file finder with TUI", version = "0.1.0")]
struct Args {
    /// Path to scan (default: .)
    #[arg(default_value = ".")]
    path: PathBuf,

    /// Dry run (list only)
    #[arg(short, long)]
    dry_run: bool,

    /// Minimum file size (e.g., 1kb, 10mb)
    #[arg(short, long, default_value = "1kb")]
    min_size: String,

    /// Config file path
    #[arg(short, long)]
    config: Option<PathBuf>,

    /// Export to JSON/CSV
    #[arg(short, long)]
    export: Option<PathBuf>,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let mut config = Config::default();
    if let Some(config_path) = args.config {
        config = Config::load(&config_path).context("Failed to load config")?;
    }
    config.min_size = parse_size(&args.min_size)?;

    let path = args.path.canonicalize().context("Invalid path")?;

    println!("Scanning {} for duplicates...", path.display());

    let dupes = scan_duplicates(&path, &config)?;

    if let Some(export_path) = args.export {
        serde_json::to_writer_pretty(&std::fs::File::create(&export_path)?, &dupes)?;
        println!("Exported to {:?}", export_path);
        return Ok(());
    }

    if dupes.is_empty() {
        println!("No duplicates found.");
        return Ok(());
    }

    println!("Found {} duplicate groups. Starting TUI...", dupes.len());

    let total_savings = dupes.values().map(|group| group.iter().map(|f| f.size).sum::<u64>()).sum::<u64>() - dupes.values().map(|group| group[0].size).sum::<u64>();
    println!("Potential savings: {:.2} GB", total_savings as f64 / 1e9);

    run_tui(dupes, args.dry_run)
}

fn parse_size(s: &str) -> Result<u64> {
    let s = s.to_lowercase();
    let num: f64 = s[..s.len() - 2].parse()?;
    let unit = &s[s.len() - 2..];
    Ok(match unit {
        "kb" => (num * 1024.0) as u64,
        "mb" => (num * 1024.0 * 1024.0) as u64,
        "gb" => (num * 1024.0 * 1024.0 * 1024.0) as u64,
        _ => num as u64,
    })
}