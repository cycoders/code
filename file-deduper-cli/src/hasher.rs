use anyhow::Result;
use blake3::Hasher;
use std::fs::File;
use std::io::{self, BufReader};
use std::path::Path;

pub fn hash_file(path: &Path) -> Result<String> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut hasher = Hasher::new();
    io::copy(&mut reader, &mut hasher)?;
    Ok(format!("{:x}", hasher.finalize()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::NamedTempFile;

    #[test]
    fn hashes_file() {
        let mut file = NamedTempFile::new().unwrap();
        fs::write(file.path(), "test content").unwrap();
        let hash = hash_file(file.path()).unwrap();
        assert_eq!(hash.len(), 64);
    }

    #[test]
    fn same_content_same_hash() {
        let content = "duplicate content";
        let mut file1 = NamedTempFile::new().unwrap();
        let mut file2 = NamedTempFile::new().unwrap();
        fs::write(file1.path(), content).unwrap();
        fs::write(file2.path(), content).unwrap();
        let hash1 = hash_file(file1.path()).unwrap();
        let hash2 = hash_file(file2.path()).unwrap();
        assert_eq!(hash1, hash2);
    }
}