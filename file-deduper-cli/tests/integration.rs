use file_deduper_cli::scanner::{scan_duplicates, FileInfo};
use file_deduper_cli::config::Config;
use std::fs;
use tempfile::tempdir;

#[test]
fn full_scan_workflow() {
    let dir = tempdir().unwrap();
    let dup1 = dir.path().join("dup1.txt");
    let dup2 = dir.path().join("dup2.txt");
    let unique = dir.path().join("unique.txt");
    fs::write(&dup1, "duplicate").unwrap();
    fs::write(&dup2, "duplicate").unwrap();
    fs::write(&unique, "unique").unwrap();

    let config = Config::default();
    let dupes = scan_duplicates(dir.path(), &config).unwrap();

    assert_eq!(dupes.len(), 1);
    let group = dupes.values().next().unwrap();
    assert_eq!(group.len(), 2);
    assert!(group.iter().any(|f| f.path == dup1));
    assert!(group.iter().any(|f| f.path == dup2));
}

#[test]
#[should_panic]
fn invalid_path() {
    scan_duplicates(std::path::Path::new("/nonexistent"), &Config::default()).unwrap();
}