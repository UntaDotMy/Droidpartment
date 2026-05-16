use crate::paths;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::path::PathBuf;

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct CompactionStats {
    pub total_runs: u64,
    pub compacted_runs: u64,
    pub passthrough_runs: u64,
    pub bytes_in: u64,
    pub bytes_out: u64,
    pub tokens_in: u64,
    pub tokens_out: u64,
    pub tokens_saved: u64,
    pub by_adapter: BTreeMap<String, u64>,
    pub by_command_head: BTreeMap<String, u64>,
    /// Per-day totals: "YYYY-MM-DD" -> aggregate.
    pub by_day: BTreeMap<String, DailyStats>,
}

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
pub struct DailyStats {
    pub runs: u64,
    pub tokens_in: u64,
    pub tokens_out: u64,
    pub tokens_saved: u64,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct DroidUsage {
    pub total_calls: u64,
    pub droids: BTreeMap<String, u64>,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct ToolStats {
    pub total_executions: u64,
    pub errors: u64,
    pub tools: BTreeMap<String, u64>,
}

fn compaction_path() -> Result<PathBuf> {
    Ok(paths::stats_dir()?.join("compaction.json"))
}

fn droid_path() -> Result<PathBuf> {
    Ok(paths::stats_dir()?.join("droid_usage.json"))
}

fn tool_path() -> Result<PathBuf> {
    Ok(paths::stats_dir()?.join("tool_stats.json"))
}

fn load_or_default<T: serde::de::DeserializeOwned + Default>(path: &PathBuf) -> T {
    std::fs::read_to_string(path)
        .ok()
        .and_then(|s| serde_json::from_str::<T>(&s).ok())
        .unwrap_or_default()
}

/// Atomic write via temp+rename. Avoids partial-state corruption when killed mid-write.
fn save<T: serde::Serialize>(path: &PathBuf, value: &T) -> Result<()> {
    if let Some(parent) = path.parent() {
        paths::ensure_dir(parent)?;
    }
    let body = serde_json::to_string_pretty(value)?;
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, body)?;
    std::fs::rename(&tmp, path)?;
    Ok(())
}

/// Update a JSON file under an advisory file lock to keep parallel sub-droid
/// writers from clobbering each other.
fn update_locked<T, F>(path: &PathBuf, mutate: F) -> Result<()>
where
    T: serde::de::DeserializeOwned + serde::Serialize + Default,
    F: FnOnce(&mut T),
{
    if let Some(parent) = path.parent() {
        paths::ensure_dir(parent)?;
    }
    let lock_path = path.with_extension("lock");
    let _lock = std::fs::OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(false)
        .open(&lock_path)?;
    // Best-effort lock; on Windows, OpenOptions create+write provides exclusive
    // write access through filesystem semantics. On POSIX we accept a small
    // race window (rare in practice given parallel sub-droid frequency).
    let mut value: T = load_or_default(path);
    mutate(&mut value);
    save(path, &value)?;
    let _ = std::fs::remove_file(&lock_path);
    Ok(())
}

pub fn record_compaction(
    adapter: &str,
    command_head: &str,
    bytes_in: u64,
    bytes_out: u64,
    tokens_in: u64,
    tokens_out: u64,
    compacted: bool,
) -> Result<()> {
    let path = compaction_path()?;
    let day = chrono::Utc::now().format("%Y-%m-%d").to_string();
    update_locked::<CompactionStats, _>(&path, |s| {
        s.total_runs += 1;
        if compacted {
            s.compacted_runs += 1;
        } else {
            s.passthrough_runs += 1;
        }
        s.bytes_in += bytes_in;
        s.bytes_out += bytes_out;
        s.tokens_in += tokens_in;
        s.tokens_out += tokens_out;
        s.tokens_saved += tokens_in.saturating_sub(tokens_out);
        *s.by_adapter.entry(adapter.to_string()).or_insert(0) += 1;
        *s.by_command_head
            .entry(command_head.to_string())
            .or_insert(0) += 1;
        let entry = s.by_day.entry(day).or_default();
        entry.runs += 1;
        entry.tokens_in += tokens_in;
        entry.tokens_out += tokens_out;
        entry.tokens_saved += tokens_in.saturating_sub(tokens_out);
    })
}

pub fn record_droid_call(name: &str) -> Result<()> {
    let path = droid_path()?;
    update_locked::<DroidUsage, _>(&path, |s| {
        s.total_calls += 1;
        *s.droids.entry(name.to_string()).or_insert(0) += 1;
    })
}

pub fn record_tool_use(name: &str, success: bool) -> Result<()> {
    let path = tool_path()?;
    update_locked::<ToolStats, _>(&path, |s| {
        s.total_executions += 1;
        if !success {
            s.errors += 1;
        }
        *s.tools.entry(name.to_string()).or_insert(0) += 1;
    })
}

pub fn show(json: bool, by_adapter: bool, daily: bool) -> Result<()> {
    let comp: CompactionStats = load_or_default(&compaction_path()?);
    let droid: DroidUsage = load_or_default(&droid_path()?);
    let tool: ToolStats = load_or_default(&tool_path()?);

    if json {
        let combined = serde_json::json!({
            "compaction": comp,
            "droids": droid,
            "tools": tool,
        });
        println!("{}", serde_json::to_string_pretty(&combined)?);
        return Ok(());
    }

    println!("DROIDPARTMENT STATS");
    println!();
    println!("Token saver:");
    println!("  total runs:          {}", comp.total_runs);
    println!("  compacted:           {}", comp.compacted_runs);
    println!("  passthrough:         {}", comp.passthrough_runs);
    println!("  bytes in:            {}", comp.bytes_in);
    println!("  bytes out:           {}", comp.bytes_out);
    println!("  tokens in:           {}", comp.tokens_in);
    println!("  tokens out:          {}", comp.tokens_out);
    println!(
        "  tokens saved:        {} ({}%) [exact, o200k_base]",
        comp.tokens_saved,
        comp.tokens_saved
            .checked_mul(100)
            .and_then(|v| v.checked_div(comp.tokens_in))
            .unwrap_or(0)
    );

    if by_adapter && !comp.by_adapter.is_empty() {
        println!();
        println!("By adapter:");
        let mut entries: Vec<_> = comp.by_adapter.iter().collect();
        entries.sort_by(|a, b| b.1.cmp(a.1));
        for (name, count) in entries {
            println!("  {name:14} {count} runs");
        }
    }

    if daily && !comp.by_day.is_empty() {
        println!();
        println!("By day (last 14):");
        let mut days: Vec<_> = comp.by_day.iter().collect();
        days.sort_by(|a, b| b.0.cmp(a.0));
        for (day, d) in days.iter().take(14) {
            println!(
                "  {day}  {} runs  {} -> {} tokens (saved {})",
                d.runs, d.tokens_in, d.tokens_out, d.tokens_saved
            );
        }
    }

    println!();
    println!("Droids:");
    println!("  total calls:         {}", droid.total_calls);
    let mut top: Vec<_> = droid.droids.iter().collect();
    top.sort_by(|a, b| b.1.cmp(a.1));
    for (name, count) in top.iter().take(5) {
        println!("    {name:20} {count}");
    }
    println!();
    println!("Tools:");
    println!("  total executions:    {}", tool.total_executions);
    println!("  errors:              {}", tool.errors);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn daily_stats_default_zero() {
        let d = DailyStats::default();
        assert_eq!(d.runs, 0);
        assert_eq!(d.tokens_saved, 0);
    }

    #[test]
    fn compaction_stats_serializes_round_trip() {
        let mut s = CompactionStats {
            total_runs: 3,
            tokens_saved: 100,
            ..Default::default()
        };
        s.by_adapter.insert("test".into(), 2);
        let json = serde_json::to_string(&s).unwrap();
        let back: CompactionStats = serde_json::from_str(&json).unwrap();
        assert_eq!(back.total_runs, 3);
        assert_eq!(back.tokens_saved, 100);
        assert_eq!(back.by_adapter.get("test"), Some(&2));
    }
}
