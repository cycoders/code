use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Config {
    pub min_size: u64,
    pub max_depth: usize,
    pub ignore_git: bool,
    pub excludes: Vec<String>,
}

impl Config {
    pub fn load(path: &Path) -> Result<Self> {
        let content = std::fs::read_to_string(path)?;
        Ok(toml::from_str(&content)?)
    }

    pub fn save(&self, path: &Path) -> Result<()> {
        let content = toml::to_string_pretty(self)?;
        std::fs::write(path, content)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn load_config() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "min_size = 1024").unwrap();
        writeln!(file, "max_depth = 3").unwrap();
        file.as_ref().sync_all().unwrap();

        let config = Config::load(file.path()).unwrap();
        assert_eq!(config.min_size, 1024);
        assert_eq!(config.max_depth, 3);
    }
}