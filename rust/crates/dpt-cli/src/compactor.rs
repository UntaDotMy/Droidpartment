use anyhow::{anyhow, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

use crate::config::DptConfig;
use crate::paths;
use crate::stats;

mod adapters;

use adapters::{select_adapter, Adapter, Compacted};

#[derive(Debug, Serialize, Deserialize)]
pub struct RunMeta {
    pub raw_id: String,
    pub command: String,
    pub exit_code: i32,
    pub started_at: String,
    pub finished_at: String,
    pub adapter: String,
    pub bytes_in: usize,
    pub bytes_out: usize,
    pub tokens_in: usize,
    pub tokens_out: usize,
    pub compacted: bool,
}

pub fn run_cmd(
    cmd: Vec<String>,
    no_compact: bool,
    json: bool,
    max_lines: Option<usize>,
) -> Result<()> {
    if cmd.is_empty() {
        return Err(anyhow!("dpt run requires a command"));
    }
    let cfg = DptConfig::load().unwrap_or_default();
    let max_lines = max_lines.unwrap_or(cfg.token_saver.max_lines);

    let joined = cmd.join(" ");
    let started = Utc::now();

    let output = exec_shell(&cmd)?;

    let finished = Utc::now();
    let exit_code = output.status.code().unwrap_or(-1);
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    let raw_id = format!("{}-{:x}", started.format("%Y%m%d-%H%M%S"), rand_suffix());
    let raw_dir = paths::raw_output_dir()?
        .join(started.format("%Y-%m-%d").to_string())
        .join(&raw_id);
    paths::ensure_dir(&raw_dir)?;

    std::fs::write(raw_dir.join("stdout.log"), &stdout)?;
    std::fs::write(raw_dir.join("stderr.log"), &stderr)?;
    std::fs::write(raw_dir.join("command.txt"), &joined)?;

    let bytes_in = stdout.len() + stderr.len();
    let adapter: Box<dyn Adapter> = select_adapter(&joined);
    let adapter_name = adapter.name().to_string();

    let compact: Compacted = if no_compact {
        Compacted {
            summary: format!("{stdout}{stderr}"),
        }
    } else {
        adapter.compact(&stdout, &stderr, exit_code, max_lines)
    };

    let bytes_out = compact.summary.len();
    let did_compact = !no_compact && bytes_out < bytes_in;

    let tokens_in = crate::tokens::count(&format!("{stdout}{stderr}"));
    let tokens_out = crate::tokens::count(&compact.summary);

    let head = joined.split_whitespace().next().unwrap_or("").to_string();
    let _ = stats::record_compaction(
        &adapter_name,
        &head,
        bytes_in as u64,
        bytes_out as u64,
        tokens_in as u64,
        tokens_out as u64,
        did_compact,
    );

    let meta = RunMeta {
        raw_id: raw_id.clone(),
        command: joined.clone(),
        exit_code,
        started_at: started.to_rfc3339(),
        finished_at: finished.to_rfc3339(),
        adapter: adapter_name.clone(),
        bytes_in,
        bytes_out,
        tokens_in,
        tokens_out,
        compacted: did_compact,
    };
    std::fs::write(
        raw_dir.join("meta.json"),
        serde_json::to_string_pretty(&meta)?,
    )?;
    std::fs::write(raw_dir.join("compact.txt"), &compact.summary)?;

    if json {
        let envelope = serde_json::json!({
            "command": joined,
            "exit_code": exit_code,
            "adapter": adapter_name,
            "compacted": did_compact,
            "raw_id": raw_id,
            "raw_path": raw_dir.to_string_lossy(),
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "tokens_saved": tokens_in.saturating_sub(tokens_out),
            "summary": compact.summary,
        });
        println!("{}", serde_json::to_string_pretty(&envelope)?);
    } else {
        print!("{}", compact.summary);
        if !compact.summary.ends_with('\n') {
            println!();
        }
        if did_compact {
            println!();
            println!("raw: dpt raw {raw_id}");
            let saved = tokens_in.saturating_sub(tokens_out);
            let pct = saved
                .checked_mul(100)
                .and_then(|v| v.checked_div(tokens_in))
                .unwrap_or(0);
            println!(
                "saved: {saved} tokens ({pct}%) [exact, o200k_base] via {adapter_name} adapter"
            );
        }
    }

    std::process::exit(exit_code);
}

pub fn raw(id: Option<String>, list: bool, prune: Option<u32>) -> Result<()> {
    let root = paths::raw_output_dir()?;
    if let Some(days) = prune {
        let cutoff = Utc::now() - chrono::Duration::days(days as i64);
        let mut removed = 0u64;
        if root.exists() {
            for date_dir in std::fs::read_dir(&root)?.flatten() {
                let path = date_dir.path();
                if !path.is_dir() {
                    continue;
                }
                let name = path.file_name().and_then(|s| s.to_str()).unwrap_or("");
                if let Ok(parsed) = chrono::NaiveDate::parse_from_str(name, "%Y-%m-%d") {
                    let parsed_dt = parsed
                        .and_hms_opt(0, 0, 0)
                        .map(|n| n.and_utc())
                        .unwrap_or_else(Utc::now);
                    if parsed_dt < cutoff {
                        std::fs::remove_dir_all(&path).ok();
                        removed += 1;
                    }
                }
            }
        }
        println!("pruned {removed} day folder(s)");
        return Ok(());
    }

    if list {
        if !root.exists() {
            println!("(no raw output yet)");
            return Ok(());
        }
        for date_dir in std::fs::read_dir(&root)?.flatten() {
            let dpath = date_dir.path();
            if !dpath.is_dir() {
                continue;
            }
            for run in std::fs::read_dir(&dpath)?.flatten() {
                let rpath = run.path();
                if !rpath.is_dir() {
                    continue;
                }
                let id = rpath.file_name().and_then(|s| s.to_str()).unwrap_or("?");
                let cmd = std::fs::read_to_string(rpath.join("command.txt"))
                    .unwrap_or_default()
                    .trim()
                    .to_string();
                println!("{id} {cmd}");
            }
        }
        return Ok(());
    }

    let id =
        id.ok_or_else(|| anyhow!("usage: dpt raw <id> | --list | --prune-older-than-days <N>"))?;
    let dir = locate_raw(&root, &id)?;
    print_section("# command", &dir.join("command.txt"));
    print_section("# meta", &dir.join("meta.json"));
    print_section("# stdout", &dir.join("stdout.log"));
    print_section("# stderr", &dir.join("stderr.log"));
    Ok(())
}

fn locate_raw(root: &Path, id: &str) -> Result<PathBuf> {
    if !root.exists() {
        return Err(anyhow!("no raw output directory at {}", root.display()));
    }
    for date_dir in std::fs::read_dir(root)?.flatten() {
        let p = date_dir.path().join(id);
        if p.is_dir() {
            return Ok(p);
        }
    }
    Err(anyhow!("raw id {id} not found"))
}

fn print_section(label: &str, path: &Path) {
    println!("{label}");
    if path.exists() {
        if let Ok(content) = std::fs::read_to_string(path) {
            print!("{content}");
            if !content.ends_with('\n') {
                println!();
            }
        }
    }
    println!();
}

fn exec_shell(cmd: &[String]) -> Result<std::process::Output> {
    // Pass argv directly to avoid double-shell evaluation. The outer shell that
    // invoked `dpt run -- ...` already tokenized the user's command, so we run
    // the program via Command::new(argv[0]).args(&argv[1..]) instead of
    // re-feeding the joined string to `sh -c` / `cmd /C` (which would re-expand
    // any `$(...)` literals that survived the first parse).
    let program = &cmd[0];
    let args = &cmd[1..];
    let output = std::process::Command::new(program).args(args).output()?;
    Ok(output)
}

fn rand_suffix() -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    use std::time::{SystemTime, UNIX_EPOCH};
    let mut h = DefaultHasher::new();
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0)
        .hash(&mut h);
    h.finish()
}
