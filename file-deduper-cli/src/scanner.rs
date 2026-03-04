use anyhow::{Context, Result};
use file_deduper_cli::config::Config;
use file_deduper_cli::hasher::hash_file;
use ignore::WalkBuilder;
use rayon::prelude::*;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub struct FileInfo {
    pub path: PathBuf,
    pub size: u64,
    pub modified: String,
}

pub fn scan_duplicates(root: &Path, config: &Config) -> Result<HashMap<String, Vec<FileInfo>>> {
    let mut dupes: HashMap<String, Vec<FileInfo>> = HashMap::new();

    let walker = WalkBuilder::new(root)
        .max_depth(config.max_depth)
        .git_ignore(config.ignore_git)
        .git_exclude(config.ignore_git)
        .build_parallel();

    walker.run(|| {
        let tx = rayon::ThreadPoolBuilder::new().num_threads(num_cpus::get()).build_global().unwrap();

        tx.scope(|s| {
            walker.into_iter().for_each(|entry| {
                let entry = entry.context("Invalid entry").unwrap();
                if entry.path().is_file() {
                    let metadata = std::fs::metadata(entry.path()).unwrap();
                    let size = metadata.len();
                    if size >= config.min_size {
                        s.spawn(|_| {
                            if let Ok(hash) = hash_file(entry.path()) {
                                let info = FileInfo {
                                    path: entry.path().to_path_buf(),
                                    size,
                                    modified: entry.path().metadata().unwrap().modified().unwrap().elapsed().unwrap().as_secs().to_string(),
                                };
                                dupes.entry(hash).or_default().push(info);
                            }
                        });
                    }
                }
            });
        });
    });

    let mut filtered_dupes: HashMap<String, Vec<FileInfo>> = HashMap::new();
    for (hash, group) in dupes {
        if group.len() > 1 {
            filtered_dupes.insert(hash, group);
        }
    }

    Ok(filtered_dupes)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn detects_duplicates() {
        let dir = tempdir().unwrap();
        let path1 = dir.path().join("file1.txt");
        let path2 = dir.path().join("file2.txt");
        fs::write(&path1, "hello").unwrap();
        fs::write(&path2, "hello").unwrap();

        let config = Config { min_size: 1, ..Default::default() };
        let dupes = scan_duplicates(dir.path(), &config).unwrap();

        assert_eq!(dupes.len(), 1);
        assert_eq!(dupes.values().next().unwrap().len(), 2);
    }

    #[test]
    fn ignores_small_files() {
        let dir = tempdir().unwrap();
        fs::write(dir.path().join("small.txt"), "a").unwrap();
        fs::write(dir.path().join("big.txt"), "hello world").unwrap();

        let config = Config { min_size: 5, ..Default::default() };
        let dupes = scan_duplicates(dir.path(), &config).unwrap();
        assert!(dupes.is_empty());
    }
}