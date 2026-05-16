use crate::paths;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct DptConfig {
    pub token_saver: TokenSaverConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default, rename_all = "camelCase")]
pub struct TokenSaverConfig {
    pub mode: TokenSaverMode,
    pub max_lines: usize,
    pub raw_retention_days: u32,
    pub compact_commands: Vec<String>,
    pub exclude_commands: Vec<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum TokenSaverMode {
    Rewrite,
    Deny,
    Off,
}

const DEFAULT_COMPACT_COMMANDS: &[&str] = &[
    // tests
    "pytest",
    "cargo",
    "cargo test",
    "go test",
    "go build",
    "npm test",
    "npm run",
    "pnpm test",
    "pnpm run",
    "yarn test",
    "jest",
    "vitest",
    "mvn",
    "gradle",
    "phpunit",
    "rspec",
    // search
    "rg",
    "ripgrep",
    "grep",
    "egrep",
    "fgrep",
    "ag",
    "ack",
    "find",
    "git grep",
    // git
    "git log",
    "git diff",
    "git status",
    "git show",
    "git blame",
    "git branch",
    // build/lint
    "tsc",
    "eslint",
    "prettier",
    "ruff",
    "flake8",
    "mypy",
    "pylint",
    "black",
    "rubocop",
    "golangci-lint",
    "make",
    // infra
    "docker",
    "podman",
    "kubectl",
    "helm",
    "terraform",
    "ansible",
    // platforms
    "gh",
    "glab",
    "aws",
    "az",
    "gcloud",
    // logs
    "tail",
    "journalctl",
];

impl Default for TokenSaverConfig {
    fn default() -> Self {
        Self {
            mode: TokenSaverMode::Rewrite,
            max_lines: 40,
            raw_retention_days: 14,
            compact_commands: DEFAULT_COMPACT_COMMANDS
                .iter()
                .map(|s| (*s).to_string())
                .collect(),
            exclude_commands: Vec::new(),
        }
    }
}

impl DptConfig {
    pub fn load() -> Result<Self> {
        Self::load_from(paths::config_path()?)
    }

    pub fn load_from(path: PathBuf) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let raw = std::fs::read_to_string(&path)?;
        let cfg: Self = serde_json::from_str(&raw)?;
        Ok(cfg)
    }
}

impl TokenSaverConfig {
    pub fn matches(&self, command: &str) -> bool {
        let trimmed = command.trim_start();
        // exclude_commands wins over compact_commands so users can opt out per command.
        for ex in &self.exclude_commands {
            if matches_head(trimmed, ex) {
                return false;
            }
        }
        for c in &self.compact_commands {
            if matches_head(trimmed, c) {
                return true;
            }
        }
        false
    }
}

/// Match `pattern` against the head of `cmd` (first 1-2 whitespace tokens).
fn matches_head(cmd: &str, pattern: &str) -> bool {
    if pattern.contains(' ') {
        let pat_words: Vec<&str> = pattern.split_whitespace().collect();
        let cmd_words: Vec<&str> = cmd.split_whitespace().take(pat_words.len()).collect();
        cmd_words == pat_words
    } else {
        cmd.split_whitespace()
            .next()
            .map(|w| w == pattern)
            .unwrap_or(false)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matches_single_word_commands() {
        let cfg = TokenSaverConfig::default();
        assert!(cfg.matches("cargo test --workspace"));
        assert!(cfg.matches("pytest"));
        assert!(cfg.matches("rg foo"));
        assert!(cfg.matches("docker ps -a"));
        assert!(cfg.matches("gh pr list"));
        assert!(cfg.matches("kubectl get pods"));
        assert!(cfg.matches("ruff check ."));
        assert!(cfg.matches("mypy src"));
        assert!(cfg.matches("tsc --noEmit"));
    }

    #[test]
    fn matches_two_word_commands() {
        let cfg = TokenSaverConfig::default();
        assert!(cfg.matches("git log --oneline"));
        assert!(cfg.matches("git diff --staged"));
        assert!(cfg.matches("npm test"));
        assert!(cfg.matches("npm run lint"));
        assert!(cfg.matches("git grep needle"));
    }

    #[test]
    fn matches_ignores_unrelated() {
        let cfg = TokenSaverConfig::default();
        assert!(!cfg.matches("echo hello"));
        assert!(!cfg.matches("ls -la"));
        assert!(!cfg.matches("python script.py"));
    }

    #[test]
    fn matches_skips_dpt_self_invocations() {
        // Inner skip-list lives in hooks::pre_tool_use; the matcher itself
        // should not match plain `dpt run` since `dpt` isn't in the list.
        let cfg = TokenSaverConfig::default();
        assert!(!cfg.matches("dpt run -- cargo test"));
        assert!(!cfg.matches("dpt stats"));
    }

    #[test]
    fn matches_handles_leading_whitespace() {
        let cfg = TokenSaverConfig::default();
        assert!(cfg.matches("   cargo build"));
    }

    #[test]
    fn matches_excludes_user_opt_outs() {
        let mut cfg = TokenSaverConfig::default();
        cfg.exclude_commands.push("git status".into());
        cfg.exclude_commands.push("rg".into());
        assert!(!cfg.matches("git status"));
        assert!(!cfg.matches("rg foo"));
        // siblings still match
        assert!(cfg.matches("git diff"));
        assert!(cfg.matches("grep foo"));
    }

    #[test]
    fn default_mode_is_rewrite() {
        let cfg = DptConfig::default();
        assert_eq!(cfg.token_saver.mode, TokenSaverMode::Rewrite);
    }
}
