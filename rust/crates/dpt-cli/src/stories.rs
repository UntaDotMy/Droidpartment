//! STORIES.md parser, mutator, and wave-progress derivator.
//!
//! `dpt-scrum` writes a markdown table at `<ProjectMemory>/artifacts/STORIES.md`
//! with the columns
//!   `| ID | Wave | Type | Agent | Task | Depends | Status |`
//!
//! The hook layer parses this table to:
//!   1. Mark rows `in_progress` from `PreToolUse:Task` and `done` /
//!      `needs_revision` / `blocked` from `PostToolUse:Task`.
//!   2. Compute per-wave progress for context injection.
//!   3. Block premature `Stop` while rows remain unfinished.
//!
//! Mutation works directly on raw text rather than parse-then-render so the
//! agent's hand-written formatting is preserved (column widths, surrounding
//! sections, comments).

use std::collections::BTreeMap;
use std::path::Path;

const COL_ID: usize = 0;
const COL_WAVE: usize = 1;
const COL_TYPE: usize = 2;
const COL_AGENT: usize = 3;
const COL_TASK: usize = 4;
const COL_DEPENDS: usize = 5;
const COL_STATUS: usize = 6;
const N_COLUMNS: usize = 7;

/// Parsed view of a single STORIES.md row.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Row {
    pub id: String,
    pub wave: String,
    pub type_: String,
    pub agent: String,
    pub task: String,
    pub depends: String,
    pub status: String,
}

#[derive(Debug, Clone, Default)]
pub struct WaveSummary {
    pub current_wave: String,
    pub current_label: Option<String>,
    pub total_waves: usize,
    pub current_done: usize,
    pub current_in_progress: usize,
    pub current_pending: usize,
    pub current_needs_revision: usize,
    pub current_blocked: usize,
    pub current_total: usize,
    pub overall_done: usize,
    pub overall_total: usize,
    pub current_rows: Vec<Row>,
}

/// Read STORIES.md text from the given project-memory path. Returns `None`
/// if the file does not exist; surfaces other IO errors as `Some(Err(_))`
/// so the caller can decide whether to ignore them silently.
pub fn read_stories(project_memory: &str) -> Option<std::io::Result<String>> {
    let path = Path::new(project_memory)
        .join("artifacts")
        .join("STORIES.md");
    if !path.exists() {
        return None;
    }
    Some(std::fs::read_to_string(&path))
}

pub fn write_stories(project_memory: &str, text: &str) -> std::io::Result<()> {
    let dir = Path::new(project_memory).join("artifacts");
    std::fs::create_dir_all(&dir)?;
    let path = dir.join("STORIES.md");
    let tmp = dir.join("STORIES.md.tmp");
    std::fs::write(&tmp, text)?;
    std::fs::rename(&tmp, &path)
}

/// Parse all rows. Skips the header row (`| ID | Wave | ...`) and the
/// separator (`| --- | --- | ...`). Any line that does not split into at
/// least 7 cells is ignored.
pub fn parse_rows(text: &str) -> Vec<Row> {
    let mut out = Vec::new();
    for line in text.lines() {
        if let Some(cells) = split_row_cells(line) {
            if cells.len() < N_COLUMNS {
                continue;
            }
            // Header detection: first cell is literally "ID" (case-insensitive).
            if cells[COL_ID].eq_ignore_ascii_case("ID") {
                continue;
            }
            // Separator detection: every cell is dashes (with optional colons).
            if cells
                .iter()
                .all(|c| !c.is_empty() && c.chars().all(|ch| ch == '-' || ch == ':'))
            {
                continue;
            }
            out.push(Row {
                id: cells[COL_ID].to_string(),
                wave: cells[COL_WAVE].to_string(),
                type_: cells[COL_TYPE].to_string(),
                agent: cells[COL_AGENT].to_string(),
                task: cells[COL_TASK].to_string(),
                depends: cells[COL_DEPENDS].to_string(),
                status: cells[COL_STATUS].to_string(),
            });
        }
    }
    out
}

/// Map of `Wave` column value -> optional `[LABEL]` from a `### Wave N [LABEL]`
/// section header earlier in the document.
pub fn parse_wave_labels(text: &str) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    for line in text.lines() {
        let trimmed = line.trim_start();
        if !trimmed.starts_with('#') {
            continue;
        }
        // Examples of valid headers:
        //   "### Wave 3 [DESIGN]"
        //   "## Wave 1 [INIT]"
        let after_hash = trimmed.trim_start_matches('#').trim_start();
        let lower = after_hash.to_ascii_lowercase();
        if !lower.starts_with("wave ") {
            continue;
        }
        let rest = &after_hash[5..];
        let mut parts = rest.splitn(2, char::is_whitespace);
        let wave_num = match parts.next() {
            Some(s) => s.trim().to_string(),
            None => continue,
        };
        let label_part = parts.next().unwrap_or("").trim();
        let label = label_part
            .trim_start_matches('[')
            .trim_end_matches(']')
            .trim()
            .to_string();
        if !label.is_empty() {
            out.insert(wave_num, label);
        }
    }
    out
}

/// Compute wave progress. The "current wave" is the lowest-numbered wave
/// whose rows are not all `done`/`blocked`. Returns `None` if the table
/// has no parseable rows.
pub fn wave_progress(text: &str) -> Option<WaveSummary> {
    let rows = parse_rows(text);
    if rows.is_empty() {
        return None;
    }
    let labels = parse_wave_labels(text);

    // Group by wave (preserve numeric ordering when possible)
    let mut waves: BTreeMap<String, Vec<Row>> = BTreeMap::new();
    for r in &rows {
        waves.entry(r.wave.clone()).or_default().push(r.clone());
    }
    let total_waves = waves.len();

    let mut overall_done = 0usize;
    let mut current_wave: Option<String> = None;
    for (wave, ws) in &waves {
        let all_settled = ws
            .iter()
            .all(|r| matches_status(&r.status, "done") || matches_status(&r.status, "blocked"));
        for r in ws {
            if matches_status(&r.status, "done") {
                overall_done += 1;
            }
        }
        if !all_settled && current_wave.is_none() {
            current_wave = Some(wave.clone());
        }
    }
    // If everything is done, surface the last wave so callers can render
    // a "all waves complete" summary.
    let current_wave = current_wave.unwrap_or_else(|| {
        waves
            .keys()
            .next_back()
            .cloned()
            .unwrap_or_else(|| "?".to_string())
    });

    let current_rows = waves.get(&current_wave).cloned().unwrap_or_default();
    let mut summary = WaveSummary {
        current_wave: current_wave.clone(),
        current_label: labels.get(&current_wave).cloned(),
        total_waves,
        overall_done,
        overall_total: rows.len(),
        current_total: current_rows.len(),
        current_rows: current_rows.clone(),
        ..Default::default()
    };
    for r in &current_rows {
        match status_kind(&r.status) {
            StatusKind::Done => summary.current_done += 1,
            StatusKind::InProgress => summary.current_in_progress += 1,
            StatusKind::Pending => summary.current_pending += 1,
            StatusKind::NeedsRevision => summary.current_needs_revision += 1,
            StatusKind::Blocked => summary.current_blocked += 1,
            StatusKind::Other => {}
        }
    }
    Some(summary)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StatusKind {
    Pending,
    InProgress,
    Done,
    NeedsRevision,
    Blocked,
    Other,
}

pub fn status_kind(status: &str) -> StatusKind {
    let s = status.trim().to_ascii_lowercase();
    match s.as_str() {
        "pending" => StatusKind::Pending,
        "in_progress" | "in-progress" | "inprogress" => StatusKind::InProgress,
        "done" | "complete" | "completed" => StatusKind::Done,
        "needs_revision" | "needs-revision" => StatusKind::NeedsRevision,
        "blocked" => StatusKind::Blocked,
        _ => StatusKind::Other,
    }
}

fn matches_status(status: &str, target: &str) -> bool {
    status.trim().eq_ignore_ascii_case(target)
}

/// Update the first row that matches `(agent, predicate)` so its `Status`
/// column becomes `new_status`. Returns the rewritten document text on
/// success; returns `None` if no matching row was found.
///
/// The predicate is applied to each candidate row and lets the caller pick,
/// for example, "first row with status pending" (PreToolUse) or "first row
/// with status in_progress" (PostToolUse), which is required to handle
/// parallel `[P]` waves where the same agent appears multiple times.
pub fn update_first_matching_row<F>(
    text: &str,
    agent: &str,
    new_status: &str,
    predicate: F,
) -> Option<String>
where
    F: Fn(&Row) -> bool,
{
    let agent_norm = agent.trim().to_ascii_lowercase();
    let mut out = String::with_capacity(text.len() + 16);
    let mut updated = false;
    let mut last_pushed_newline = true;
    for line in text.split_inclusive('\n') {
        if updated {
            out.push_str(line);
            last_pushed_newline = line.ends_with('\n');
            continue;
        }
        // Strip the trailing newline for parsing, keep it for output.
        let trimmed_nl = line.trim_end_matches('\n');
        if let Some(cells) = split_row_cells(trimmed_nl) {
            if cells.len() >= N_COLUMNS && !cells[COL_ID].eq_ignore_ascii_case("ID") {
                let row = Row {
                    id: cells[COL_ID].to_string(),
                    wave: cells[COL_WAVE].to_string(),
                    type_: cells[COL_TYPE].to_string(),
                    agent: cells[COL_AGENT].to_string(),
                    task: cells[COL_TASK].to_string(),
                    depends: cells[COL_DEPENDS].to_string(),
                    status: cells[COL_STATUS].to_string(),
                };
                let row_agent = row.agent.trim().to_ascii_lowercase();
                if row_agent == agent_norm && predicate(&row) {
                    let rewritten = replace_last_cell(trimmed_nl, new_status);
                    out.push_str(&rewritten);
                    if line.ends_with('\n') {
                        out.push('\n');
                    }
                    updated = true;
                    last_pushed_newline = line.ends_with('\n');
                    continue;
                }
            }
        }
        out.push_str(line);
        last_pushed_newline = line.ends_with('\n');
    }
    if !last_pushed_newline {
        // ensure trailing newline so subsequent edits append cleanly
        out.push('\n');
    }
    if updated {
        Some(out)
    } else {
        None
    }
}

/// Split a markdown-table row line into trimmed cell strings. Returns
/// `None` if the line is not a table row (does not start with `|`).
fn split_row_cells(line: &str) -> Option<Vec<&str>> {
    let trimmed = line.trim();
    if !trimmed.starts_with('|') {
        return None;
    }
    let cells: Vec<&str> = trimmed
        .split('|')
        .map(|s| s.trim())
        .filter(|s| !s.is_empty())
        .collect();
    Some(cells)
}

/// Replace the content of the last `|`-delimited cell on `line`, preserving
/// the leading text and the trailing `|`. The new cell is single-space-padded
/// (` <new_status> `) for legibility; we don't try to match the column's
/// original width because the table is regenerated on the next `dpt-scrum`
/// run anyway.
fn replace_last_cell(line: &str, new_status: &str) -> String {
    let bytes = line.as_bytes();
    let pipes: Vec<usize> = bytes
        .iter()
        .enumerate()
        .filter_map(|(i, b)| if *b == b'|' { Some(i) } else { None })
        .collect();
    if pipes.len() < 2 {
        return line.to_string();
    }
    let last = pipes[pipes.len() - 1];
    let prev = pipes[pipes.len() - 2];
    let mut out = String::with_capacity(line.len() + 8);
    out.push_str(&line[..=prev]);
    out.push(' ');
    out.push_str(new_status.trim());
    out.push(' ');
    out.push_str(&line[last..]);
    out
}

/// Render a one-line summary of wave progress suitable for `additionalContext`.
pub fn render_wave_summary(s: &WaveSummary) -> String {
    let label = match &s.current_label {
        Some(l) if !l.is_empty() => format!(" [{}]", l),
        _ => String::new(),
    };
    let mut head = format!(
        "Wave {}/{} {}: {}/{} done",
        s.current_wave, s.total_waves, label, s.current_done, s.current_total
    );
    if s.current_in_progress > 0 {
        head.push_str(&format!(", {} in_progress", s.current_in_progress));
    }
    if s.current_pending > 0 {
        head.push_str(&format!(", {} pending", s.current_pending));
    }
    if s.current_needs_revision > 0 {
        head.push_str(&format!(", {} needs_revision", s.current_needs_revision));
    }
    if s.current_blocked > 0 {
        head.push_str(&format!(", {} blocked", s.current_blocked));
    }
    head.push_str(&format!(
        " (overall {}/{})",
        s.overall_done, s.overall_total
    ));
    head
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = r#"# Stories

## Wave Plan

### Wave 1 [INIT]

| ID  | Wave | Type | Agent        | Task              | Depends | Status      |
|-----|------|------|--------------|-------------------|---------|-------------|
| 1.1 | 1    | [P]  | dpt-memory   | START init        | -       | done        |
| 1.2 | 1    | [P]  | dpt-research | best practices    | -       | done        |

### Wave 2 [PLAN]

| ID  | Wave | Type | Agent        | Task              | Depends | Status      |
|-----|------|------|--------------|-------------------|---------|-------------|
| 2.1 | 2    | [S]  | dpt-product  | create PRD        | 1       | in_progress |

### Wave 3 [DESIGN]

| ID  | Wave | Type | Agent        | Task              | Depends | Status      |
|-----|------|------|--------------|-------------------|---------|-------------|
| 3.1 | 3    | [S]  | dpt-arch     | architecture      | 2       | pending     |
"#;

    #[test]
    fn parse_rows_extracts_all_data_rows() {
        let rows = parse_rows(SAMPLE);
        assert_eq!(rows.len(), 4);
        assert_eq!(rows[0].id, "1.1");
        assert_eq!(rows[0].agent, "dpt-memory");
        assert_eq!(rows[0].status, "done");
        assert_eq!(rows[2].agent, "dpt-product");
        assert_eq!(rows[2].status, "in_progress");
    }

    #[test]
    fn parse_skips_header_and_separator() {
        let rows = parse_rows(SAMPLE);
        assert!(rows.iter().all(|r| r.id != "ID"));
        assert!(rows.iter().all(|r| !r.id.starts_with('-')));
    }

    #[test]
    fn parse_wave_labels_finds_section_headers() {
        let labels = parse_wave_labels(SAMPLE);
        assert_eq!(labels.get("1").map(String::as_str), Some("INIT"));
        assert_eq!(labels.get("2").map(String::as_str), Some("PLAN"));
        assert_eq!(labels.get("3").map(String::as_str), Some("DESIGN"));
    }

    #[test]
    fn wave_progress_picks_lowest_unfinished_wave() {
        let s = wave_progress(SAMPLE).expect("has rows");
        assert_eq!(s.current_wave, "2");
        assert_eq!(s.current_label.as_deref(), Some("PLAN"));
        assert_eq!(s.current_in_progress, 1);
        assert_eq!(s.current_total, 1);
        assert_eq!(s.overall_done, 2);
        assert_eq!(s.overall_total, 4);
    }

    #[test]
    fn wave_progress_falls_back_when_all_done() {
        let all_done = SAMPLE
            .replace("in_progress", "done")
            .replace("pending", "done");
        let s = wave_progress(&all_done).expect("has rows");
        assert_eq!(s.overall_done, 4);
        assert_eq!(s.overall_total, 4);
        // The fallback exposes the last wave so the caller can render
        // "all waves complete" without panicking.
        assert_eq!(s.current_wave, "3");
    }

    #[test]
    fn update_first_matching_row_flips_in_progress_to_done() {
        let updated = update_first_matching_row(SAMPLE, "dpt-product", "done", |r| {
            status_kind(&r.status) == StatusKind::InProgress
        })
        .expect("matched");
        assert!(updated.contains("dpt-product  | create PRD        | 1       | done"));
        assert!(!updated.contains("create PRD        | 1       | in_progress"));
    }

    #[test]
    fn update_first_matching_row_returns_none_when_no_match() {
        let updated = update_first_matching_row(SAMPLE, "dpt-data", "done", |_| true);
        assert!(updated.is_none());
    }

    #[test]
    fn update_handles_parallel_same_agent() {
        let parallel = r#"
| ID  | Wave | Type | Agent   | Task     | Depends | Status      |
|-----|------|------|---------|----------|---------|-------------|
| 4.1 | 4    | [P]  | dpt-dev | api impl | 3       | pending     |
| 4.2 | 4    | [P]  | dpt-dev | ui impl  | 3       | pending     |
"#;
        let after_first = update_first_matching_row(parallel, "dpt-dev", "in_progress", |r| {
            status_kind(&r.status) == StatusKind::Pending
        })
        .expect("first match");
        // Only the first dpt-dev row should be touched.
        let rows = parse_rows(&after_first);
        assert_eq!(rows[0].status, "in_progress");
        assert_eq!(rows[1].status, "pending");

        let after_second = update_first_matching_row(&after_first, "dpt-dev", "in_progress", |r| {
            status_kind(&r.status) == StatusKind::Pending
        })
        .expect("second match");
        let rows = parse_rows(&after_second);
        assert_eq!(rows[0].status, "in_progress");
        assert_eq!(rows[1].status, "in_progress");
    }

    #[test]
    fn render_wave_summary_includes_label_and_counts() {
        let s = wave_progress(SAMPLE).unwrap();
        let line = render_wave_summary(&s);
        assert!(line.contains("Wave 2/3"));
        assert!(line.contains("[PLAN]"));
        assert!(line.contains("0/1 done"));
        assert!(line.contains("1 in_progress"));
        assert!(line.contains("overall 2/4"));
    }
}
