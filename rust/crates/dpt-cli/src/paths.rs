use anyhow::{anyhow, Result};
use std::path::PathBuf;

pub fn factory_home() -> Result<PathBuf> {
    if let Ok(custom) = std::env::var("DROIDPARTMENT_HOME") {
        return Ok(PathBuf::from(custom));
    }
    let home = dirs::home_dir().ok_or_else(|| anyhow!("could not resolve user home directory"))?;
    Ok(home.join(".factory"))
}

pub fn memory_dir() -> Result<PathBuf> {
    Ok(factory_home()?.join("memory"))
}

pub fn raw_output_dir() -> Result<PathBuf> {
    Ok(factory_home()?.join("raw-output"))
}

pub fn config_path() -> Result<PathBuf> {
    Ok(factory_home()?.join("dpt-config.json"))
}

pub fn stats_dir() -> Result<PathBuf> {
    Ok(memory_dir()?.join("stats"))
}

pub fn ensure_dir(path: &std::path::Path) -> Result<()> {
    if !path.exists() {
        std::fs::create_dir_all(path)?;
    }
    Ok(())
}

/// Compute the absolute project-memory path for a given working directory.
///
/// Returns `<factory_home>/memory/projects/<sanitized-cwd>` so droids that
/// need to read or write per-project artifacts can derive a deterministic
/// path from cwd alone, no `[Artifacts: ...]` injection required.
pub fn project_memory_path(cwd: &str) -> String {
    let slug = sanitize_path(cwd);
    factory_home()
        .map(|h| {
            h.join("memory")
                .join("projects")
                .join(&slug)
                .to_string_lossy()
                .replace('\\', "/")
        })
        .unwrap_or_else(|_| format!("~/.factory/memory/projects/{slug}"))
}

/// Slugified form of a working directory, suitable as a key for revision
/// state and other per-project data. Same algorithm as the project memory
/// path component so callers can map between them without re-deriving.
pub fn project_slug(cwd: &str) -> String {
    sanitize_path(cwd)
}

fn sanitize_path(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut last_dash = false;
    for ch in s.chars() {
        if ch.is_ascii_alphanumeric() {
            out.push(ch.to_ascii_lowercase());
            last_dash = false;
        } else if !last_dash && !out.is_empty() {
            out.push('-');
            last_dash = true;
        }
    }
    while out.ends_with('-') {
        out.pop();
    }
    if out.is_empty() {
        "default".to_string()
    } else {
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn project_memory_is_deterministic() {
        let a = project_memory_path("/Users/alice/projects/myapp");
        let b = project_memory_path("/Users/alice/projects/myapp");
        assert_eq!(a, b);
        assert!(a.ends_with("users-alice-projects-myapp"));
    }

    #[test]
    fn project_memory_handles_windows_paths() {
        let p = project_memory_path("C:\\Users\\alice\\My Project");
        assert!(p.ends_with("c-users-alice-my-project"));
    }

    #[test]
    fn project_memory_for_empty_cwd_falls_back() {
        let p = project_memory_path("");
        assert!(p.ends_with("default"));
    }
}
