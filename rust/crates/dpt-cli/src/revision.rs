//! Revision-loop state with a hard cap of 3 rounds per audit lane.
//!
//! When `PostToolUse:Task` parses `needs_revision: true` from a sub-droid's
//! output, we increment that lane's counter. `PreToolUse:Task` checks the
//! same counter on the next invocation of the same lane and emits
//! `permissionDecision: deny` once the cap is reached, forcing the
//! orchestrator to escalate or change approach instead of looping forever.
//!
//! State is persisted to a JSON file under `<factory_home>/memory/stats/`
//! using the same atomic temp+rename pattern as `stats.rs`. The file is
//! keyed by `(project_slug, lane_droid)` so unrelated projects never
//! collide.
//!
//! IO is parameterized on an explicit `state_path: &Path` so tests can use
//! a tempfile per test without touching the process-global
//! `DROIDPARTMENT_HOME` env var (which would race against `paths::tests`).

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use crate::flock;
use crate::paths;

pub const MAX_REVISIONS: u32 = 3;

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct RevisionState {
    pub lanes: BTreeMap<String, LaneState>,
}

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct LaneState {
    pub count: u32,
    pub last_revision_agent: Option<String>,
    pub last_reason: Option<String>,
    pub last_at: Option<String>,
}

fn default_state_path() -> Result<PathBuf> {
    Ok(paths::stats_dir()?.join("revision_state.json"))
}

fn key(project_slug: &str, lane: &str) -> String {
    format!("{project_slug}::{lane}")
}

fn load_at(path: &Path) -> RevisionState {
    std::fs::read_to_string(path)
        .ok()
        .and_then(|s| serde_json::from_str::<RevisionState>(&s).ok())
        .unwrap_or_default()
}

fn save_at(path: &Path, state: &RevisionState) -> Result<()> {
    if let Some(parent) = path.parent() {
        paths::ensure_dir(parent)?;
    }
    let body = serde_json::to_string_pretty(state)?;
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, body)?;
    std::fs::rename(&tmp, path)?;
    Ok(())
}

fn record_at(
    path: &Path,
    project_slug: &str,
    lane: &str,
    revision_agent: Option<&str>,
    reason: Option<&str>,
) -> Result<u32> {
    let mut state = load_at(path);
    let entry = state.lanes.entry(key(project_slug, lane)).or_default();
    entry.count = entry.count.saturating_add(1);
    entry.last_revision_agent = revision_agent.map(|s| s.to_string());
    entry.last_reason = reason.map(|s| s.to_string());
    entry.last_at = Some(chrono::Utc::now().to_rfc3339());
    let new_count = entry.count;
    save_at(path, &state)?;
    Ok(new_count)
}

fn reset_at(path: &Path, project_slug: &str, lane: &str) -> Result<()> {
    let mut state = load_at(path);
    if state.lanes.remove(&key(project_slug, lane)).is_some() {
        save_at(path, &state)?;
    }
    Ok(())
}

fn count_at(path: &Path, project_slug: &str, lane: &str) -> u32 {
    let state = load_at(path);
    state
        .lanes
        .get(&key(project_slug, lane))
        .map(|e| e.count)
        .unwrap_or(0)
}

/// Increment the count for `(project_slug, lane)` and persist. Returns the
/// new count.
///
/// Wrapped in an exclusive file lock so concurrent PostToolUse calls cannot
/// drop increments via interleaved read-modify-write.
pub fn record_revision(
    project_slug: &str,
    lane: &str,
    revision_agent: Option<&str>,
    reason: Option<&str>,
) -> Result<u32> {
    let p = default_state_path()?;
    flock::with_exclusive_lock(&p, || {
        record_at(&p, project_slug, lane, revision_agent, reason)
    })
}

/// Reset the counter for a lane (called when an audit returns clean).
pub fn reset(project_slug: &str, lane: &str) -> Result<()> {
    let p = default_state_path()?;
    flock::with_exclusive_lock(&p, || reset_at(&p, project_slug, lane))
}

/// Read the current count without mutating state. Returns 0 when no entry
/// exists.
pub fn count(project_slug: &str, lane: &str) -> u32 {
    let Ok(p) = default_state_path() else {
        return 0;
    };
    count_at(&p, project_slug, lane)
}

/// Returns true when calling `lane` again would exceed the cap. Specifically:
/// the lane is at-or-above MAX_REVISIONS rounds. The orchestrator should
/// escalate (different approach, human help) rather than retry.
pub fn cap_reached(project_slug: &str, lane: &str) -> bool {
    count(project_slug, lane) >= MAX_REVISIONS
}

/// Heuristic: which sub-droid names act as audit lanes (the ones for which
/// the cap applies). Build/plan droids are excluded since they don't have
/// the iterative review semantics.
pub fn is_audit_lane(droid: &str) -> bool {
    matches!(
        droid,
        "dpt-qa" | "dpt-sec" | "dpt-perf" | "dpt-lead" | "dpt-review"
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tempfile(suffix: &str) -> PathBuf {
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!("dpt-revision-{nanos}-{suffix}.json"))
    }

    #[test]
    fn record_increments_count() {
        let p = tempfile("inc");
        assert_eq!(count_at(&p, "proj", "dpt-sec"), 0);
        let n = record_at(&p, "proj", "dpt-sec", Some("dpt-dev"), Some("missing test")).unwrap();
        assert_eq!(n, 1);
        assert_eq!(count_at(&p, "proj", "dpt-sec"), 1);
        let n2 = record_at(&p, "proj", "dpt-sec", None, None).unwrap();
        assert_eq!(n2, 2);
        let _ = std::fs::remove_file(&p);
    }

    #[test]
    fn reset_clears_count() {
        let p = tempfile("reset");
        record_at(&p, "proj", "dpt-perf", None, None).unwrap();
        record_at(&p, "proj", "dpt-perf", None, None).unwrap();
        assert_eq!(count_at(&p, "proj", "dpt-perf"), 2);
        reset_at(&p, "proj", "dpt-perf").unwrap();
        assert_eq!(count_at(&p, "proj", "dpt-perf"), 0);
        let _ = std::fs::remove_file(&p);
    }

    #[test]
    fn cap_reached_at_three_rounds() {
        let p = tempfile("cap");
        assert_eq!(count_at(&p, "proj", "dpt-lead"), 0);
        for _ in 0..3 {
            record_at(&p, "proj", "dpt-lead", None, None).unwrap();
        }
        assert!(count_at(&p, "proj", "dpt-lead") >= MAX_REVISIONS);
        let _ = std::fs::remove_file(&p);
    }

    #[test]
    fn projects_isolated_from_each_other() {
        let p = tempfile("isoproj");
        record_at(&p, "alpha", "dpt-sec", None, None).unwrap();
        record_at(&p, "alpha", "dpt-sec", None, None).unwrap();
        assert_eq!(count_at(&p, "alpha", "dpt-sec"), 2);
        assert_eq!(count_at(&p, "beta", "dpt-sec"), 0);
        let _ = std::fs::remove_file(&p);
    }

    #[test]
    fn lanes_isolated_from_each_other() {
        let p = tempfile("isolane");
        record_at(&p, "proj", "dpt-sec", None, None).unwrap();
        assert_eq!(count_at(&p, "proj", "dpt-sec"), 1);
        assert_eq!(count_at(&p, "proj", "dpt-perf"), 0);
        let _ = std::fs::remove_file(&p);
    }

    #[test]
    fn audit_lane_classification() {
        assert!(is_audit_lane("dpt-sec"));
        assert!(is_audit_lane("dpt-perf"));
        assert!(is_audit_lane("dpt-review"));
        assert!(is_audit_lane("dpt-lead"));
        assert!(is_audit_lane("dpt-qa"));
        assert!(!is_audit_lane("dpt-dev"));
        assert!(!is_audit_lane("dpt-arch"));
        assert!(!is_audit_lane("dpt-product"));
    }
}
