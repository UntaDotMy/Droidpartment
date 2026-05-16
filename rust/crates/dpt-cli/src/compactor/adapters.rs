pub struct Compacted {
    pub summary: String,
}

pub trait Adapter {
    fn name(&self) -> &'static str;
    fn matches(&self, cmd: &str) -> bool;
    fn compact(&self, stdout: &str, stderr: &str, exit: i32, max_lines: usize) -> Compacted;
}

pub fn select_adapter(cmd: &str) -> Box<dyn Adapter> {
    let candidates: Vec<Box<dyn Adapter>> = vec![
        Box::new(TestAdapter),
        Box::new(BuildAdapter),
        Box::new(LintAdapter),
        Box::new(GitAdapter),
        Box::new(SearchAdapter),
        Box::new(DockerAdapter),
        Box::new(LogAdapter),
    ];
    for a in candidates {
        if a.matches(cmd) {
            return a;
        }
    }
    Box::new(GenericAdapter)
}

fn first_words(cmd: &str, n: usize) -> Vec<&str> {
    cmd.split_whitespace().take(n).collect()
}

fn keep_signal_lines<'a>(
    lines: impl Iterator<Item = &'a str>,
    signals: &[&str],
    limit: usize,
) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for line in lines {
        if out.len() >= limit {
            break;
        }
        let lower = line.to_ascii_lowercase();
        if signals.iter().any(|s| lower.contains(s)) {
            out.push(line.to_string());
        }
    }
    out
}

fn head_tail(stdout: &str, stderr: &str, max_lines: usize) -> String {
    let merged: Vec<&str> = stdout.lines().chain(stderr.lines()).collect();
    if merged.len() <= max_lines {
        return merged.join("\n");
    }
    let head = max_lines / 4;
    let tail = max_lines - head;
    let mut out: Vec<String> = Vec::with_capacity(max_lines + 2);
    for line in merged.iter().take(head) {
        out.push((*line).to_string());
    }
    out.push(format!(
        "... [{} lines elided, recover with `dpt raw <id>`]",
        merged.len() - head - tail
    ));
    let start = merged.len().saturating_sub(tail);
    for line in &merged[start..] {
        out.push((*line).to_string());
    }
    out.join("\n")
}

pub struct TestAdapter;
impl Adapter for TestAdapter {
    fn name(&self) -> &'static str {
        "test"
    }
    fn matches(&self, cmd: &str) -> bool {
        let head = first_words(cmd, 3).join(" ");
        let lower = cmd.to_ascii_lowercase();
        head == "cargo test"
            || head.starts_with("cargo test ")
            || head == "cargo nextest run"
            || lower.starts_with("pytest")
            || lower.starts_with("python -m pytest")
            || lower.starts_with("npm test")
            || lower.starts_with("npm run test")
            || lower.starts_with("pnpm test")
            || lower.starts_with("pnpm run test")
            || lower.starts_with("yarn test")
            || lower.starts_with("jest")
            || lower.starts_with("vitest")
            || lower.starts_with("go test")
            || lower.starts_with("mvn test")
            || lower.starts_with("gradle test")
            || lower.starts_with("phpunit")
            || lower.starts_with("rspec")
    }
    fn compact(&self, stdout: &str, stderr: &str, exit: i32, max_lines: usize) -> Compacted {
        let signals = [
            "fail",
            "error",
            "panic",
            "assertion",
            "test result",
            "passed",
            "failed",
            "skipped",
            "warning:",
            "expected",
            "got",
            "===",
            "---",
        ];
        let merged_lines = stdout.lines().chain(stderr.lines());
        let kept = keep_signal_lines(merged_lines, &signals, max_lines);
        let status = if exit == 0 { "PASS" } else { "FAIL" };
        let mut out = String::new();
        out.push_str(&format!("{status} (exit {exit})\n"));
        if kept.is_empty() {
            out.push_str(&head_tail(stdout, stderr, max_lines));
        } else {
            out.push_str(&kept.join("\n"));
        }
        Compacted { summary: out }
    }
}

pub struct BuildAdapter;
impl Adapter for BuildAdapter {
    fn name(&self) -> &'static str {
        "build"
    }
    fn matches(&self, cmd: &str) -> bool {
        let lower = cmd.to_ascii_lowercase();
        let head = first_words(cmd, 3).join(" ");
        head == "cargo build"
            || head == "cargo check"
            || head == "cargo clippy"
            || head.starts_with("cargo build ")
            || head.starts_with("cargo check ")
            || lower.starts_with("go build")
            || lower.starts_with("npm run build")
            || lower.starts_with("pnpm run build")
            || lower.starts_with("yarn build")
            || lower.starts_with("tsc")
            || lower.starts_with("make")
            || lower.starts_with("mvn package")
            || lower.starts_with("mvn install")
            || lower.starts_with("gradle build")
            || lower.starts_with("dotnet build")
            || lower.starts_with("webpack")
            || lower.starts_with("vite build")
    }
    fn compact(&self, stdout: &str, stderr: &str, exit: i32, max_lines: usize) -> Compacted {
        let signals = [
            "error[",
            "error:",
            "warning:",
            "fail",
            "compiling",
            "finished",
            "linking",
            "tsc:",
            "build successful",
            "build failed",
            "task ",
        ];
        let merged_lines = stdout.lines().chain(stderr.lines());
        let kept = keep_signal_lines(merged_lines, &signals, max_lines);
        let status = if exit == 0 { "BUILD OK" } else { "BUILD FAIL" };
        let mut out = String::new();
        out.push_str(&format!("{status} (exit {exit})\n"));
        if kept.is_empty() {
            out.push_str(&head_tail(stdout, stderr, max_lines));
        } else {
            out.push_str(&kept.join("\n"));
        }
        Compacted { summary: out }
    }
}

pub struct LintAdapter;
impl Adapter for LintAdapter {
    fn name(&self) -> &'static str {
        "lint"
    }
    fn matches(&self, cmd: &str) -> bool {
        let lower = cmd.to_ascii_lowercase();
        lower.starts_with("eslint")
            || lower.starts_with("npx eslint")
            || lower.starts_with("prettier")
            || lower.starts_with("npx prettier")
            || lower.starts_with("ruff")
            || lower.starts_with("flake8")
            || lower.starts_with("mypy")
            || lower.starts_with("pylint")
            || lower.starts_with("black")
            || lower.starts_with("rubocop")
            || lower.starts_with("golangci-lint")
            || lower.starts_with("cargo fmt")
    }
    fn compact(&self, stdout: &str, stderr: &str, exit: i32, max_lines: usize) -> Compacted {
        let signals = [
            "error",
            "warning",
            "problem",
            "violation",
            "fix",
            "note:",
            "would reformat",
            "reformatted",
        ];
        let merged_lines = stdout.lines().chain(stderr.lines());
        let kept = keep_signal_lines(merged_lines, &signals, max_lines);
        let status = if exit == 0 { "LINT OK" } else { "LINT ISSUES" };
        let mut out = format!("{status} (exit {exit})\n");
        if kept.is_empty() {
            out.push_str(&head_tail(stdout, stderr, max_lines));
        } else {
            out.push_str(&kept.join("\n"));
        }
        Compacted { summary: out }
    }
}

pub struct GitAdapter;
impl Adapter for GitAdapter {
    fn name(&self) -> &'static str {
        "git"
    }
    fn matches(&self, cmd: &str) -> bool {
        let head = first_words(cmd, 2).join(" ");
        matches!(
            head.as_str(),
            "git status"
                | "git log"
                | "git diff"
                | "git show"
                | "git blame"
                | "git branch"
                | "git stash"
                | "git reflog"
        )
    }
    fn compact(&self, stdout: &str, stderr: &str, _exit: i32, max_lines: usize) -> Compacted {
        let lines: Vec<&str> = stdout.lines().chain(stderr.lines()).collect();
        let total = lines.len();
        let trimmed = if total <= max_lines {
            lines.join("\n")
        } else {
            let mut out = lines
                .iter()
                .take(max_lines)
                .map(|s| s.to_string())
                .collect::<Vec<_>>();
            out.push(format!("... [{} more lines elided]", total - max_lines));
            out.join("\n")
        };
        Compacted { summary: trimmed }
    }
}

pub struct SearchAdapter;
impl Adapter for SearchAdapter {
    fn name(&self) -> &'static str {
        "search"
    }
    fn matches(&self, cmd: &str) -> bool {
        let first = cmd.split_whitespace().next().unwrap_or("");
        matches!(
            first,
            "rg" | "ripgrep" | "grep" | "egrep" | "fgrep" | "ag" | "ack" | "find"
        ) || cmd.starts_with("git grep")
    }
    fn compact(&self, stdout: &str, stderr: &str, _exit: i32, max_lines: usize) -> Compacted {
        let lines: Vec<&str> = stdout.lines().collect();
        let total = lines.len();
        let mut summary = String::new();
        summary.push_str(&format!("{total} matching lines\n"));
        let kept = if total <= max_lines {
            lines.iter().map(|s| s.to_string()).collect::<Vec<_>>()
        } else {
            let mut k: Vec<String> = lines
                .iter()
                .take(max_lines)
                .map(|s| s.to_string())
                .collect();
            k.push(format!(
                "... [{} more matches elided, recover with `dpt raw <id>`]",
                total - max_lines
            ));
            k
        };
        summary.push_str(&kept.join("\n"));
        if !stderr.trim().is_empty() {
            summary.push_str("\n--- stderr ---\n");
            summary.push_str(&head_tail("", stderr, 5));
        }
        Compacted { summary }
    }
}

pub struct DockerAdapter;
impl Adapter for DockerAdapter {
    fn name(&self) -> &'static str {
        "docker"
    }
    fn matches(&self, cmd: &str) -> bool {
        let first = cmd.split_whitespace().next().unwrap_or("");
        matches!(
            first,
            "docker" | "kubectl" | "podman" | "helm" | "terraform" | "ansible"
        )
    }
    fn compact(&self, stdout: &str, stderr: &str, exit: i32, max_lines: usize) -> Compacted {
        let signals = [
            "error",
            "warning",
            "fail",
            "ready",
            "running",
            "started",
            "restarting",
            "completed",
            "applied",
            "destroyed",
            "rollout",
        ];
        let merged_lines = stdout.lines().chain(stderr.lines());
        let kept = keep_signal_lines(merged_lines, &signals, max_lines);
        let status = if exit == 0 { "OK" } else { "FAIL" };
        let mut out = format!("{status} (exit {exit})\n");
        if kept.is_empty() {
            out.push_str(&head_tail(stdout, stderr, max_lines));
        } else {
            out.push_str(&kept.join("\n"));
        }
        Compacted { summary: out }
    }
}

pub struct LogAdapter;
impl Adapter for LogAdapter {
    fn name(&self) -> &'static str {
        "logs"
    }
    fn matches(&self, cmd: &str) -> bool {
        let lower = cmd.to_ascii_lowercase();
        lower.starts_with("tail ")
            || lower.starts_with("less ")
            || lower.starts_with("cat ")
            || lower.contains(" | tail")
            || lower.contains(" | less")
            || lower.contains("journalctl")
    }
    fn compact(&self, stdout: &str, stderr: &str, _exit: i32, max_lines: usize) -> Compacted {
        let combined = format!("{stdout}{stderr}");
        let summary = head_tail(&combined, "", max_lines);
        Compacted { summary }
    }
}

pub struct GenericAdapter;
impl Adapter for GenericAdapter {
    fn name(&self) -> &'static str {
        "generic"
    }
    fn matches(&self, _cmd: &str) -> bool {
        true
    }
    fn compact(&self, stdout: &str, stderr: &str, exit: i32, max_lines: usize) -> Compacted {
        // Try to highlight error/warn/fail lines first, then head+tail.
        let signals = ["error", "warn", "fail", "panic", "exception", "traceback"];
        let merged_lines = stdout.lines().chain(stderr.lines());
        let kept_signal = keep_signal_lines(merged_lines, &signals, max_lines / 2);
        let mut out = format!("(exit {exit})\n");
        if !kept_signal.is_empty() {
            out.push_str("# signals\n");
            out.push_str(&kept_signal.join("\n"));
            out.push('\n');
        }
        out.push_str("# head/tail\n");
        out.push_str(&head_tail(stdout, stderr, max_lines));
        Compacted { summary: out }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn pick(cmd: &str) -> &'static str {
        select_adapter(cmd).name()
    }

    #[test]
    fn test_adapter_routing_test() {
        assert_eq!(pick("cargo test --workspace"), "test");
        assert_eq!(pick("pytest tests/ -v"), "test");
        assert_eq!(pick("npm test"), "test");
        assert_eq!(pick("jest --watch"), "test");
        assert_eq!(pick("go test ./..."), "test");
    }

    #[test]
    fn test_adapter_routing_build() {
        assert_eq!(pick("cargo build --release"), "build");
        assert_eq!(pick("npm run build"), "build");
        assert_eq!(pick("tsc --noEmit"), "build");
        assert_eq!(pick("go build ."), "build");
    }

    #[test]
    fn test_adapter_routing_lint() {
        assert_eq!(pick("eslint src"), "lint");
        assert_eq!(pick("ruff check ."), "lint");
        assert_eq!(pick("cargo fmt --all -- --check"), "lint");
    }

    #[test]
    fn test_adapter_routing_git() {
        assert_eq!(pick("git status"), "git");
        assert_eq!(pick("git log --oneline"), "git");
        assert_eq!(pick("git diff --staged"), "git");
    }

    #[test]
    fn test_adapter_routing_search() {
        assert_eq!(pick("rg foo"), "search");
        assert_eq!(pick("grep -r needle ."), "search");
        assert_eq!(pick("find . -name '*.rs'"), "search");
        assert_eq!(pick("git grep needle"), "search");
    }

    #[test]
    fn test_adapter_routing_docker() {
        assert_eq!(pick("docker ps"), "docker");
        assert_eq!(pick("kubectl get pods"), "docker");
        assert_eq!(pick("terraform plan"), "docker");
    }

    #[test]
    fn test_adapter_routing_logs() {
        assert_eq!(pick("tail -f /var/log/syslog"), "logs");
        assert_eq!(pick("journalctl -u nginx"), "logs");
    }

    #[test]
    fn test_adapter_routing_generic_fallback() {
        assert_eq!(pick("echo hello"), "generic");
        assert_eq!(pick("ls -la"), "generic");
        assert_eq!(pick("python script.py"), "generic");
    }

    #[test]
    fn test_test_adapter_status_pass_fail() {
        let a = TestAdapter;
        let pass = a.compact("test result: ok. 5 passed", "", 0, 40);
        assert!(pass.summary.starts_with("PASS"));
        let fail = a.compact("FAILED tests/foo", "1 failed", 1, 40);
        assert!(fail.summary.starts_with("FAIL"));
    }

    #[test]
    fn test_search_adapter_truncates() {
        let a = SearchAdapter;
        let many = (0..1000)
            .map(|i| format!("match{i}"))
            .collect::<Vec<_>>()
            .join("\n");
        let r = a.compact(&many, "", 0, 10);
        assert!(r.summary.contains("1000 matching lines"));
        assert!(r.summary.contains("more matches elided"));
    }

    #[test]
    fn test_generic_adapter_signals() {
        let a = GenericAdapter;
        let r = a.compact("starting...\nerror: oops\ndone", "panic: bad", 1, 40);
        assert!(r.summary.contains("(exit 1)"));
        assert!(r.summary.contains("error: oops"));
        assert!(r.summary.contains("panic: bad"));
    }

    #[test]
    fn test_head_tail_short_input_kept_in_full() {
        let a = GenericAdapter;
        let r = a.compact("a\nb\nc", "", 0, 40);
        assert!(r.summary.contains("a\nb\nc"));
        assert!(!r.summary.contains("elided"));
    }
}
