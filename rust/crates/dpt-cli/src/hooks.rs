use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::io::{Read, Write};

use crate::advisory;
use crate::cli::HookCmd;
use crate::config::{DptConfig, TokenSaverMode};
use crate::flock;
use crate::paths;
use crate::revision;
use crate::stats;
use crate::stories;

#[derive(Debug, Default, Deserialize)]
#[serde(default)]
struct HookInput {
    cwd: Option<String>,
    tool_name: Option<String>,
    tool_input: Option<Value>,
    tool_response: Option<Value>,
    prompt: Option<String>,
    session_id: Option<String>,
    #[serde(rename = "subagent_type")]
    subagent_type: Option<String>,
    #[serde(default)]
    stop_hook_active: bool,
}

#[derive(Debug, Serialize, Default)]
#[serde(rename_all = "camelCase")]
struct HookSpecificOutput {
    hook_event_name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    additional_context: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    permission_decision: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    permission_decision_reason: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    updated_input: Option<Value>,
}

#[derive(Debug, Serialize, Default)]
#[serde(rename_all = "camelCase")]
struct HookOutput {
    #[serde(skip_serializing_if = "Option::is_none")]
    hook_specific_output: Option<HookSpecificOutput>,
}

pub fn dispatch(cmd: HookCmd) -> Result<()> {
    let input = read_stdin_json();
    let cfg = DptConfig::load().unwrap_or_default();
    match cmd {
        HookCmd::SessionStart => session_start(&input),
        HookCmd::UserPromptSubmit => user_prompt_submit(&input),
        HookCmd::PreToolUse => pre_tool_use(&input, &cfg),
        HookCmd::PostToolUse => post_tool_use(&input),
        HookCmd::Stop => stop(&input),
        HookCmd::SubagentStop => Ok(()),
        HookCmd::SessionEnd => Ok(()),
        HookCmd::PreCompact => Ok(()),
        HookCmd::Notification => Ok(()),
    }
}

fn read_stdin_json() -> HookInput {
    let mut buf = String::new();
    if std::io::stdin().read_to_string(&mut buf).is_err() {
        // Hooks ref: stderr is shown to the user via `droid --debug`. Surface
        // unexpected I/O failures so they're diagnosable instead of silently
        // turning into "hook did nothing".
        eprintln!("dpt-hook: failed to read stdin");
        return HookInput::default();
    }
    if buf.trim().is_empty() {
        return HookInput::default();
    }
    match serde_json::from_str::<HookInput>(&buf) {
        Ok(parsed) => parsed,
        Err(e) => {
            eprintln!("dpt-hook: stdin JSON parse error: {e}");
            HookInput::default()
        }
    }
}

/// Extract the `subagent_type` for a `Task` tool call.
///
/// Per Droid's Custom Droids docs, `subagent_type` is a parameter on the
/// `Task` tool, so it lives inside `tool_input`. We also accept a top-level
/// field as a fallback for testing and for any payload variation Droid may
/// emit.
fn extract_subagent_type(input: &HookInput) -> Option<String> {
    if let Some(s) = input.subagent_type.as_deref() {
        if !s.is_empty() {
            return Some(s.to_string());
        }
    }
    input
        .tool_input
        .as_ref()
        .and_then(|v| v.get("subagent_type"))
        .and_then(|v| v.as_str())
        .filter(|s| !s.is_empty())
        .map(|s| s.to_string())
}

fn write_output(out: &HookOutput) {
    if let Ok(body) = serde_json::to_string(out) {
        let _ = std::io::stdout().write_all(body.as_bytes());
    }
}

fn session_start(input: &HookInput) -> Result<()> {
    // Per Droid hooks reference, SessionStart fires on every session boundary
    // (`startup`, `resume`, `clear`, `compact`). We re-emit the contract on
    // each so it survives auto-compaction; the body is small and is paid for
    // once per session window via cache.
    let project_memory = input
        .cwd
        .as_deref()
        .map(crate::paths::project_memory_path)
        .unwrap_or_else(|| "~/.factory/memory/projects/default".to_string());

    let context = format!("{OPERATING_CONTRACT}\n\n[ProjectMemory: {project_memory}]");

    let out = HookOutput {
        hook_specific_output: Some(HookSpecificOutput {
            hook_event_name: "SessionStart".into(),
            additional_context: Some(context),
            ..Default::default()
        }),
    };
    write_output(&out);
    Ok(())
}

fn user_prompt_submit(input: &HookInput) -> Result<()> {
    // Aggressive prompt-keyword advisory: surface 1-3 sub-droid suggestions
    // when the user prompt matches known patterns. Hints only - the
    // orchestrator decides whether to call Task().
    let prompt = match input.prompt.as_deref() {
        Some(p) => p,
        None => return Ok(()),
    };
    let Some(advisory) = advisory::suggest(prompt) else {
        return Ok(());
    };
    let out = HookOutput {
        hook_specific_output: Some(HookSpecificOutput {
            hook_event_name: "UserPromptSubmit".into(),
            additional_context: Some(advisory),
            ..Default::default()
        }),
    };
    write_output(&out);
    Ok(())
}

fn pre_tool_use(input: &HookInput, cfg: &DptConfig) -> Result<()> {
    if cfg.token_saver.mode == TokenSaverMode::Off {
        return Ok(());
    }
    let tool = input.tool_name.as_deref().unwrap_or("");

    if tool == "Task" {
        if let Some(name) = extract_subagent_type(input) {
            let _ = stats::record_droid_call(&name);
            // Hard deny on revision cap. Audit lanes only; non-audit droids
            // are not subject to the cap.
            if revision::is_audit_lane(&name) {
                if let Some(cwd) = input.cwd.as_deref() {
                    let slug = paths::project_slug(cwd);
                    if revision::cap_reached(&slug, &name) {
                        let count = revision::count(&slug, &name);
                        let reason = format!(
                            "Revision cap reached for {name} ({count}/{max} rounds). \
                             Escalate by changing approach, asking the user, or reverting \
                             the contested changes - re-running the same audit lane will not help.",
                            max = revision::MAX_REVISIONS
                        );
                        let out = HookOutput {
                            hook_specific_output: Some(HookSpecificOutput {
                                hook_event_name: "PreToolUse".into(),
                                permission_decision: Some("deny".into()),
                                permission_decision_reason: Some(reason),
                                ..Default::default()
                            }),
                        };
                        write_output(&out);
                        return Ok(());
                    }
                }
            }
            // Allowed - mark the matching STORIES.md row in_progress.
            if let Some(cwd) = input.cwd.as_deref() {
                mark_story_in_progress(cwd, &name);
            }
        }
        return Ok(());
    }

    if tool != "Execute" {
        return Ok(());
    }

    let command = input
        .tool_input
        .as_ref()
        .and_then(|v| v.get("command"))
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if command.is_empty() {
        return Ok(());
    }
    // Skip-list: only the actual `dpt` invocation. Tightened from the previous
    // `starts_with("dpt ")` which caught unrelated `dpt-foo` aliases.
    let first = command.split_whitespace().next().unwrap_or("");
    if first == "dpt"
        || first.ends_with("/dpt")
        || first.ends_with("/dpt.exe")
        || first.ends_with(r"\dpt.exe")
    {
        return Ok(());
    }
    if !cfg.token_saver.matches(command) {
        return Ok(());
    }

    let dpt_bin = std::env::current_exe()
        .map(|p| {
            let s = p.to_string_lossy().replace('\\', "/");
            if s.contains(' ') {
                format!("\"{s}\"")
            } else {
                s
            }
        })
        .unwrap_or_else(|_| "dpt".to_string());

    match cfg.token_saver.mode {
        TokenSaverMode::Rewrite => {
            let rewritten = format!("{dpt_bin} run -- {command}");
            let updated = json!({ "command": rewritten });
            let out = HookOutput {
                hook_specific_output: Some(HookSpecificOutput {
                    hook_event_name: "PreToolUse".into(),
                    permission_decision: Some("allow".into()),
                    permission_decision_reason: Some(
                        "Rewriting through `dpt run --` for token compaction".into(),
                    ),
                    updated_input: Some(updated),
                    ..Default::default()
                }),
            };
            write_output(&out);
        }
        TokenSaverMode::Deny => {
            let suggestion = format!("Rerun that as: {dpt_bin} run -- {command}");
            let out = HookOutput {
                hook_specific_output: Some(HookSpecificOutput {
                    hook_event_name: "PreToolUse".into(),
                    permission_decision: Some("deny".into()),
                    permission_decision_reason: Some(suggestion),
                    ..Default::default()
                }),
            };
            write_output(&out);
        }
        TokenSaverMode::Off => {}
    }
    Ok(())
}

fn post_tool_use(input: &HookInput) -> Result<()> {
    let tool = input.tool_name.as_deref().unwrap_or("");
    if !tool.is_empty() {
        let _ = stats::record_tool_use(tool, true);
    }
    // PostToolUse:TodoWrite re-injects a fresh plan summary so the orchestrator
    // sees current todo state on every turn, per Droid's PostToolUse decision
    // control spec (https://docs.factory.ai/reference/hooks-reference.md).
    if tool == "TodoWrite" {
        // Persist the todos to a session-scoped file so the Stop hook can
        // detect unfinished work even when STORIES.md is absent (lighter
        // workflows that never invoke dpt-scrum).
        if let (Some(sid), Some(todos)) = (
            input.session_id.as_deref(),
            input.tool_input.as_ref().and_then(|v| v.get("todos")),
        ) {
            let _ = persist_session_todos(sid, todos);
        }
        if let Some(summary) = summarize_todos(input.tool_input.as_ref()) {
            let out = HookOutput {
                hook_specific_output: Some(HookSpecificOutput {
                    hook_event_name: "PostToolUse".into(),
                    additional_context: Some(summary),
                    ..Default::default()
                }),
            };
            write_output(&out);
        }
        return Ok(());
    }
    // PostToolUse:Task -- the heart of Scope-C automation. Parse signals
    // returned by the sub-droid, sync STORIES.md, manage revision counters,
    // and inject wave progress + next-step hint as additionalContext.
    if tool == "Task" {
        if let Some(droid) = extract_subagent_type(input) {
            let cwd = input.cwd.as_deref();
            let signals = parse_task_signals(input.tool_response.as_ref());
            let new_status = pick_status_for_signals(&signals);

            // Update revision counter for audit lanes.
            if let Some(cwd) = cwd {
                if revision::is_audit_lane(&droid) {
                    let slug = paths::project_slug(cwd);
                    match new_status {
                        "needs_revision" => {
                            let _ = revision::record_revision(
                                &slug,
                                &droid,
                                signals.revision_agent.as_deref(),
                                signals.revision_reason.as_deref(),
                            );
                        }
                        "done" => {
                            let _ = revision::reset(&slug, &droid);
                        }
                        _ => {}
                    }
                }

                // Sync STORIES.md row state.
                let updated_text = sync_story_row(cwd, &droid, new_status);
                // Compute and inject wave progress from the (possibly updated)
                // table contents.
                let context = build_task_post_context(
                    cwd,
                    &droid,
                    new_status,
                    &signals,
                    updated_text.as_deref(),
                );
                if let Some(ctx) = context {
                    let out = HookOutput {
                        hook_specific_output: Some(HookSpecificOutput {
                            hook_event_name: "PostToolUse".into(),
                            additional_context: Some(ctx),
                            ..Default::default()
                        }),
                    };
                    write_output(&out);
                }
            }
        }
        return Ok(());
    }
    Ok(())
}

fn summarize_todos(tool_input: Option<&Value>) -> Option<String> {
    let todos = parse_todos(tool_input)?;
    if todos.is_empty() {
        return None;
    }
    let mut pending = 0usize;
    let mut in_progress = 0usize;
    let mut completed = 0usize;
    let mut current: Option<String> = None;
    for (status, content) in &todos {
        match status.as_str() {
            "pending" => pending += 1,
            "in_progress" => {
                in_progress += 1;
                if current.is_none() {
                    current = Some(content.clone());
                }
            }
            "completed" => completed += 1,
            _ => {}
        }
    }
    let total = pending + in_progress + completed;
    let mut s = format!(
        "Plan: {completed}/{total} completed, {in_progress} in progress, {pending} pending"
    );
    if let Some(c) = current {
        if !c.is_empty() {
            s.push_str(&format!(". Current: {c}"));
        }
    }
    Some(s)
}

/// Normalize the `tool_input.todos` value into `(status, content)` pairs.
///
/// Droid's TodoWrite documents `todos` as a multi-line numbered string with
/// `[status]` markers (`1. [pending] foo`). The hook layer historically
/// expected the parsed array form, so we accept both:
///   1. `todos: [{status: "pending", content: "foo"}, ...]`
///   2. `todos: "1. [pending] foo\n2. [in_progress] bar"`
fn parse_todos(tool_input: Option<&Value>) -> Option<Vec<(String, String)>> {
    let raw = tool_input?.get("todos")?;
    if let Some(arr) = raw.as_array() {
        let mut out = Vec::with_capacity(arr.len());
        for t in arr {
            let status = t
                .get("status")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let content = t
                .get("content")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            out.push((status, content));
        }
        return Some(out);
    }
    if let Some(s) = raw.as_str() {
        return Some(parse_todos_string(s));
    }
    None
}

/// Parse the documented multi-line numbered todo string into pairs. Lines
/// without a recognizable `[status]` marker are skipped.
fn parse_todos_string(s: &str) -> Vec<(String, String)> {
    let mut out = Vec::new();
    for line in s.lines() {
        // Drop leading number + dot + whitespace.
        let trimmed = line.trim_start();
        let after_num = match trimmed.find(|c: char| !c.is_ascii_digit()) {
            Some(i) if i > 0 => trimmed[i..].trim_start_matches(['.', ')']),
            _ => trimmed,
        }
        .trim_start();

        if !after_num.starts_with('[') {
            continue;
        }
        let close = match after_num.find(']') {
            Some(i) => i,
            None => continue,
        };
        let raw_status = &after_num[1..close];
        let normalized = match raw_status.trim().to_ascii_lowercase().as_str() {
            "pending" | "todo" | "open" => "pending".to_string(),
            "in_progress" | "in-progress" | "doing" | "wip" => "in_progress".to_string(),
            "completed" | "done" | "complete" => "completed".to_string(),
            other => other.to_string(),
        };
        let content = after_num[close + 1..].trim().to_string();
        out.push((normalized, content));
    }
    out
}

#[derive(Debug, Default)]
struct TaskSignals {
    needs_revision: Option<bool>,
    revision_agent: Option<String>,
    revision_reason: Option<String>,
    next_agent: Option<String>,
    confidence: Option<u32>,
}

/// Extract the textual body from `tool_response`. Sub-droids return their
/// final message, but Factory may wrap it in any of a few JSON shapes
/// (`output`, `text`, `message`, `content[].text`). Fall back to the raw
/// stringified value when no shape matches.
fn extract_response_text(value: Option<&Value>) -> String {
    let Some(v) = value else {
        return String::new();
    };
    if let Some(s) = v.as_str() {
        return s.to_string();
    }
    if let Some(obj) = v.as_object() {
        for k in &["output", "text", "message", "result", "summary"] {
            if let Some(inner) = obj.get(*k) {
                if let Some(s) = inner.as_str() {
                    return s.to_string();
                }
            }
        }
        if let Some(arr) = obj.get("content").and_then(|c| c.as_array()) {
            let mut combined = String::new();
            for item in arr {
                if let Some(s) = item.get("text").and_then(|x| x.as_str()) {
                    combined.push_str(s);
                    combined.push('\n');
                } else if let Some(s) = item.as_str() {
                    combined.push_str(s);
                    combined.push('\n');
                }
            }
            if !combined.is_empty() {
                return combined;
            }
        }
    }
    v.to_string()
}

/// Parse the `Follow-up:`-style key/value lines that sub-droids emit. Lines
/// like `- needs_revision: true` and `* revision_agent: dpt-dev` are both
/// recognized. Both the JSON object form (`{"needs_revision": true, ...}`)
/// and the text form are accepted.
fn parse_task_signals(value: Option<&Value>) -> TaskSignals {
    let mut sig = TaskSignals::default();

    // Direct JSON form (sub-droid returned an object whose keys are the
    // signals themselves).
    if let Some(obj) = value.and_then(|v| v.as_object()) {
        if let Some(b) = obj.get("needs_revision").and_then(|v| v.as_bool()) {
            sig.needs_revision = Some(b);
        }
        if let Some(s) = obj.get("revision_agent").and_then(|v| v.as_str()) {
            sig.revision_agent = Some(s.to_string());
        }
        if let Some(s) = obj.get("revision_reason").and_then(|v| v.as_str()) {
            sig.revision_reason = Some(s.to_string());
        }
        if let Some(s) = obj.get("next_agent").and_then(|v| v.as_str()) {
            sig.next_agent = Some(s.to_string());
        }
        if let Some(n) = obj.get("confidence").and_then(|v| v.as_u64()) {
            sig.confidence = Some(n as u32);
        }
    }

    // Text form (default for the documented `Follow-up:` block).
    let text = extract_response_text(value);
    for line in text.lines() {
        if let Some(rest) = extract_kv(line, "needs_revision") {
            let v = rest.trim().to_ascii_lowercase();
            if v.starts_with("true") {
                sig.needs_revision = Some(true);
            } else if v.starts_with("false") {
                sig.needs_revision = Some(false);
            }
        } else if let Some(rest) = extract_kv(line, "revision_agent") {
            let v = clean_value(rest);
            if !v.is_empty() && v != "null" && v != "none" {
                sig.revision_agent = Some(v);
            }
        } else if let Some(rest) = extract_kv(line, "revision_reason") {
            let v = clean_value(rest);
            if !v.is_empty() {
                sig.revision_reason = Some(v);
            }
        } else if let Some(rest) = extract_kv(line, "next_agent") {
            let v = clean_value(rest);
            if !v.is_empty() && v != "null" && v != "none" {
                sig.next_agent = Some(v);
            }
        } else if let Some(rest) = extract_kv(line, "confidence") {
            if let Ok(n) = rest.trim().trim_end_matches('%').parse::<u32>() {
                sig.confidence = Some(n);
            }
        }
    }
    sig
}

/// Case-insensitive `key:` extractor. Strips leading bullet markers and
/// whitespace, then matches the key prefix and returns the trimmed value.
fn extract_kv<'a>(line: &'a str, key: &str) -> Option<&'a str> {
    let trimmed = line
        .trim_start()
        .trim_start_matches(|c: char| c == '-' || c == '*' || c == '+' || c.is_whitespace());
    if trimmed.len() < key.len() {
        return None;
    }
    if !trimmed[..key.len()].eq_ignore_ascii_case(key) {
        return None;
    }
    let after = trimmed[key.len()..].trim_start();
    if !after.starts_with(':') {
        return None;
    }
    Some(after[1..].trim())
}

fn clean_value(v: &str) -> String {
    v.trim()
        .trim_matches(|c: char| c == '"' || c == '\'' || c == '`')
        .to_string()
}

fn pick_status_for_signals(s: &TaskSignals) -> &'static str {
    match s.needs_revision {
        Some(true) => "needs_revision",
        Some(false) => "done",
        // No explicit signal: assume the lane completed successfully. The
        // orchestrator can manually flip the row if that turns out to be
        // wrong; refusing to update would leave rows stuck in_progress.
        None => "done",
    }
}

/// Mark the first STORIES.md row matching `droid` (status `pending` or
/// `needs_revision`) as `in_progress`. Silent no-op when no STORIES.md
/// exists or no eligible row is found.
///
/// Uses an exclusive file lock around the read-modify-write cycle so
/// concurrent `[P]` Task calls do not pick the same row twice.
fn mark_story_in_progress(cwd: &str, droid: &str) {
    let pm = paths::project_memory_path(cwd);
    let stories_path = std::path::Path::new(&pm)
        .join("artifacts")
        .join("STORIES.md");
    if !stories_path.exists() {
        return;
    }
    let _ = flock::with_exclusive_lock(&stories_path, || {
        let Some(Ok(text)) = stories::read_stories(&pm) else {
            return Ok(());
        };
        if let Some(updated) =
            stories::update_first_matching_row(&text, droid, "in_progress", |r| {
                matches!(
                    stories::status_kind(&r.status),
                    stories::StatusKind::Pending | stories::StatusKind::NeedsRevision
                )
            })
        {
            let _ = stories::write_stories(&pm, &updated);
        }
        Ok(())
    });
}

/// Mark the first `in_progress` row for `droid` with `new_status`. Returns
/// the updated text body when something changed, allowing the caller to
/// reuse it for wave-progress derivation without re-reading the file.
///
/// Locked the same way as `mark_story_in_progress` so PostToolUse calls in
/// the same `[P]` wave don't race.
fn sync_story_row(cwd: &str, droid: &str, new_status: &str) -> Option<String> {
    let pm = paths::project_memory_path(cwd);
    let stories_path = std::path::Path::new(&pm)
        .join("artifacts")
        .join("STORIES.md");
    if !stories_path.exists() {
        return None;
    }
    flock::with_exclusive_lock(&stories_path, || {
        let Some(Ok(text)) = stories::read_stories(&pm) else {
            return Ok(None);
        };
        let Some(updated) = stories::update_first_matching_row(&text, droid, new_status, |r| {
            matches!(
                stories::status_kind(&r.status),
                stories::StatusKind::InProgress
            )
        }) else {
            return Ok(None);
        };
        if stories::write_stories(&pm, &updated).is_ok() {
            Ok(Some(updated))
        } else {
            Ok(None)
        }
    })
    .ok()
    .flatten()
}

/// Build the `additionalContext` body for `PostToolUse:Task`. Combines:
///   1. The wave progress line (when STORIES.md is present).
///   2. A next-step routing hint when the sub-droid signaled a revision.
///   3. The remaining revision budget when relevant.
///
/// Returns `None` when there is nothing useful to inject (avoids paying for
/// empty turns).
fn build_task_post_context(
    cwd: &str,
    droid: &str,
    new_status: &str,
    signals: &TaskSignals,
    updated_text: Option<&str>,
) -> Option<String> {
    let mut lines: Vec<String> = Vec::new();

    // Source the STORIES.md text either from the in-memory copy returned by
    // sync_story_row (post-update) or from disk when no row was updated.
    let pm = paths::project_memory_path(cwd);
    let stories_text: Option<String> = match updated_text {
        Some(t) => Some(t.to_string()),
        None => stories::read_stories(&pm).and_then(|r| r.ok()),
    };

    if let Some(text) = stories_text.as_deref() {
        if let Some(summary) = stories::wave_progress(text) {
            lines.push(format!(
                "Droidpartment wave update: {} -> {}.",
                droid, new_status
            ));
            lines.push(stories::render_wave_summary(&summary));

            // List the next [P]/[S] rows the orchestrator should call so
            // wave advancement is concrete, not vague.
            let next_calls = next_calls_for_wave(&summary);
            if !next_calls.is_empty() {
                lines.push(format!("Next in wave: {}", next_calls.join(", ")));
            }
        }
    }

    // Revision routing: when an audit lane returned dirty, point at the
    // revision_agent (default dpt-dev) explicitly.
    if let Some(true) = signals.needs_revision {
        let agent = signals.revision_agent.as_deref().unwrap_or("dpt-dev");
        let reason = signals
            .revision_reason
            .as_deref()
            .unwrap_or("(reason not provided by sub-droid)");
        let slug = paths::project_slug(cwd);
        let count = revision::count(&slug, droid);
        let remaining = revision::MAX_REVISIONS.saturating_sub(count);
        lines.push(format!(
            "{droid} requested revision (round {count}/{max}, {remaining} round(s) left). \
             Run Task('{agent}') with reason: {reason}",
            max = revision::MAX_REVISIONS
        ));
    } else if let Some(next) = signals.next_agent.as_deref() {
        if !next.is_empty() && next != "null" {
            lines.push(format!("{droid} suggests next: Task('{next}')"));
        }
    }

    if lines.is_empty() {
        None
    } else {
        Some(lines.join("\n"))
    }
}

/// Format the next pending/in_progress rows in the current wave so the
/// orchestrator can batch the next `[P]` Task() calls.
fn next_calls_for_wave(s: &stories::WaveSummary) -> Vec<String> {
    let mut out = Vec::new();
    for r in &s.current_rows {
        match stories::status_kind(&r.status) {
            stories::StatusKind::Pending | stories::StatusKind::NeedsRevision => {
                out.push(format!("Task('{}') [{}]", r.agent, r.id));
            }
            _ => {}
        }
    }
    out
}

fn session_todos_path(session_id: &str) -> Option<std::path::PathBuf> {
    let id = sanitize_session(session_id);
    let dir = paths::memory_dir().ok()?.join("sessions").join(&id);
    Some(dir.join("todos.json"))
}

fn sanitize_session(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for ch in s.chars() {
        if ch.is_ascii_alphanumeric() || ch == '-' || ch == '_' {
            out.push(ch);
        } else {
            out.push('_');
        }
    }
    if out.is_empty() {
        "default".to_string()
    } else {
        out
    }
}

fn persist_session_todos(session_id: &str, todos: &Value) -> Result<()> {
    let Some(path) = session_todos_path(session_id) else {
        return Ok(());
    };
    if let Some(parent) = path.parent() {
        paths::ensure_dir(parent)?;
    }
    let body = serde_json::to_string_pretty(todos)?;
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, body)?;
    std::fs::rename(&tmp, &path)?;
    Ok(())
}

fn unfinished_session_todos(session_id: &str) -> Option<Vec<String>> {
    let path = session_todos_path(session_id)?;
    let body = std::fs::read_to_string(&path).ok()?;
    // The persisted value is whatever shape Droid passed in tool_input.todos
    // (array or string). Wrap it in a synthetic `{ "todos": ... }` envelope
    // and reuse the same parser as `summarize_todos` so both shapes work.
    let raw: Value = serde_json::from_str(&body).ok()?;
    let envelope = serde_json::json!({ "todos": raw });
    let pairs = parse_todos(Some(&envelope))?;
    let mut out: Vec<String> = Vec::new();
    for (status, content) in pairs {
        if status == "pending" || status == "in_progress" {
            out.push(format!("  - [{status}] {content}"));
        }
    }
    Some(out)
}

fn stop(input: &HookInput) -> Result<()> {
    // Stop-hook backstop: if STORIES.md exists and has unfinished rows, return
    // decision: "block" with a reason listing the open work. Per Droid hooks
    // reference, `stop_hook_active` MUST be checked to prevent infinite loops.
    if input.stop_hook_active {
        return Ok(());
    }
    let Some(cwd) = input.cwd.as_deref() else {
        return Ok(());
    };

    // Source A: STORIES.md (multi-wave plans persisted by dpt-scrum).
    let pm = crate::paths::project_memory_path(cwd);
    let stories = std::path::Path::new(&pm).join("artifacts/STORIES.md");
    if let Ok(text) = std::fs::read_to_string(&stories) {
        let mut open: Vec<String> = Vec::new();
        for row in stories::parse_rows(&text) {
            match stories::status_kind(&row.status) {
                stories::StatusKind::Pending
                | stories::StatusKind::InProgress
                | stories::StatusKind::NeedsRevision => {
                    open.push(format!("  - [{}] {} ({})", row.id, row.task, row.status));
                }
                _ => {}
            }
        }
        if !open.is_empty() {
            let count = open.len();
            let preview: String = open.iter().take(5).cloned().collect::<Vec<_>>().join("\n");
            let reason = format!(
                "STORIES.md has {count} unfinished row(s). Continue the wave plan or \
                 update statuses before stopping:\n{preview}"
            );
            let out = serde_json::json!({ "decision": "block", "reason": reason });
            let _ = std::io::stdout().write_all(out.to_string().as_bytes());
            return Ok(());
        }
    }

    // Source B: session-scoped TodoWrite snapshot (lighter workflows).
    if let Some(sid) = input.session_id.as_deref() {
        if let Some(open) = unfinished_session_todos(sid) {
            if !open.is_empty() {
                let count = open.len();
                let preview: String = open.iter().take(5).cloned().collect::<Vec<_>>().join("\n");
                let reason = format!(
                    "TodoWrite has {count} unfinished todo(s). Continue or mark done \
                     before stopping:\n{preview}"
                );
                let out = serde_json::json!({ "decision": "block", "reason": reason });
                let _ = std::io::stdout().write_all(out.to_string().as_bytes());
                return Ok(());
            }
        }
    }

    Ok(())
}

pub fn settings_block() -> Value {
    let bin = std::env::current_exe()
        .map(|p| p.to_string_lossy().replace('\\', "/"))
        .unwrap_or_else(|_| "dpt".to_string());
    // Only wrap in quotes when the path has spaces; otherwise the outer quotes
    // can be double-escaped by some shells (cmd.exe via Droid) and break exec.
    let q = if bin.contains(' ') {
        format!("\"{bin}\"")
    } else {
        bin
    };

    let events: &[(&str, &str, &str, u32)] = &[
        ("SessionStart", "*", "session-start", 15),
        ("UserPromptSubmit", "*", "user-prompt-submit", 5),
        ("PreToolUse", "*", "pre-tool-use", 5),
        ("PostToolUse", "*", "post-tool-use", 5),
        ("Stop", "*", "stop", 5),
        ("SubagentStop", "*", "subagent-stop", 5),
        ("SessionEnd", "*", "session-end", 10),
        ("PreCompact", "*", "pre-compact", 5),
        ("Notification", "", "notification", 5),
    ];

    let mut hooks_map = serde_json::Map::new();
    for (event, matcher, sub, timeout) in events {
        hooks_map.insert(
            (*event).into(),
            json!([{
                "matcher": matcher,
                "hooks": [{
                    "type": "command",
                    "command": format!("{q} hook {sub}"),
                    "timeout": timeout,
                }],
            }]),
        );
    }
    json!({ "hooks": Value::Object(hooks_map) })
}

const OPERATING_CONTRACT: &str = r#"# Droidpartment v4 active

Hook-driven automation (real, not advisory):
- PreToolUse auto-rewrites noisy shell commands through `dpt run -- <cmd>`. Recover full output with `dpt raw <id>`. See savings with `dpt stats`.
- UserPromptSubmit injects sub-droid suggestions when prompts match keyword patterns (audit, bug, feature, security, perf, etc.). Hints only - the orchestrator decides whether to call Task().
- PreToolUse:Task hard-denies a 4th revision attempt against any audit lane (dpt-qa, dpt-sec, dpt-perf, dpt-lead, dpt-review). Cap is 3 rounds per lane per project; counter persists in `~/.factory/memory/stats/revision_state.json`.
- PostToolUse:Task parses `Follow-up:` signals from sub-droid output (`needs_revision`, `revision_agent`, `revision_reason`, `next_agent`, `confidence`), updates the matching STORIES.md row (`pending` -> `in_progress` -> `done` / `needs_revision`), and injects wave progress + the next [P] Task() calls for the orchestrator to batch.
- PostToolUse:TodoWrite re-injects the current plan after every TodoWrite call and persists todos to a session-scoped file for the Stop backstop.
- Stop reads STORIES.md and the session todos snapshot; returns `decision: block` when work remains pending / in_progress / needs_revision. Honors `stop_hook_active` to avoid loops.
- SubagentStop / SessionEnd / PreCompact / Notification stay silent (zero per-turn token cost).

18 specialist sub-droids are available via the Task tool. They run in isolated context windows and return a `Follow-up:` text contract. Hooks cannot synthesize Task() calls (Factory contract limitation); the orchestrator is responsible for the actual delegation, but the hook layer enforces the workflow shape: STORIES.md status mutates as Tasks complete, the revision cap is enforced, Stop blocks premature exits, advisory hints route attention.

For multi-component work: `dpt-scrum` writes STORIES.md with status column. The orchestrator batches `[P]` rows in one turn and advances when all return; PostToolUse computes wave progress automatically. Audit lanes signal `needs_revision: <bool>` + `revision_agent`; the cap is enforced in code. For multi-feature projects with milestones use Droid's `/missions`. For plan-heavy single-feature work use `/spec` (Shift+Tab).

`[ProjectMemory: <abs path>]` below is a deterministic absolute path under `~/.factory/memory/projects/<sanitized-cwd>/`. Sub-droids read or write artifacts (PRD.md, ARCHITECTURE.md, STORIES.md, RESEARCH.md, lessons.yaml) there. Path is the same across resumes.

This contract is delivered via SessionStart additionalContext. See `~/.factory/AGENTS.md` for the full operating contract."#;

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn parse_signals_from_text_form() {
        let body = json!(
            "Follow-up:\n- needs_revision: true\n- revision_agent: dpt-dev\n- revision_reason: tests fail\n- confidence: 75"
        );
        let s = parse_task_signals(Some(&body));
        assert_eq!(s.needs_revision, Some(true));
        assert_eq!(s.revision_agent.as_deref(), Some("dpt-dev"));
        assert_eq!(s.revision_reason.as_deref(), Some("tests fail"));
        assert_eq!(s.confidence, Some(75));
    }

    #[test]
    fn parse_signals_from_object_form() {
        let body = json!({
            "needs_revision": false,
            "next_agent": "dpt-output",
            "confidence": 90
        });
        let s = parse_task_signals(Some(&body));
        assert_eq!(s.needs_revision, Some(false));
        assert_eq!(s.next_agent.as_deref(), Some("dpt-output"));
        assert_eq!(s.confidence, Some(90));
    }

    #[test]
    fn parse_signals_from_anthropic_content_form() {
        let body = json!({
            "content": [{"text": "- needs_revision: true\n- revision_agent: dpt-dev\n"}]
        });
        let s = parse_task_signals(Some(&body));
        assert_eq!(s.needs_revision, Some(true));
        assert_eq!(s.revision_agent.as_deref(), Some("dpt-dev"));
    }

    #[test]
    fn pick_status_defaults_to_done_when_unsignaled() {
        let s = TaskSignals::default();
        assert_eq!(pick_status_for_signals(&s), "done");
    }

    #[test]
    fn pick_status_respects_explicit_signals() {
        let s = TaskSignals {
            needs_revision: Some(true),
            ..Default::default()
        };
        assert_eq!(pick_status_for_signals(&s), "needs_revision");
        let s = TaskSignals {
            needs_revision: Some(false),
            ..Default::default()
        };
        assert_eq!(pick_status_for_signals(&s), "done");
    }

    #[test]
    fn extract_kv_handles_bullet_markers() {
        assert_eq!(
            extract_kv("- needs_revision: true", "needs_revision"),
            Some("true")
        );
        assert_eq!(
            extract_kv("* needs_revision: false", "needs_revision"),
            Some("false")
        );
        assert_eq!(
            extract_kv("  needs_revision : true", "needs_revision"),
            Some("true")
        );
        assert_eq!(extract_kv("status: ok", "needs_revision"), None);
    }

    #[test]
    fn clean_value_strips_quotes() {
        assert_eq!(clean_value(" \"foo\" "), "foo");
        assert_eq!(clean_value("`bar`"), "bar");
        assert_eq!(clean_value("baz"), "baz");
    }

    #[test]
    fn sanitize_session_keeps_alnum() {
        assert_eq!(sanitize_session("abc-123_xyz"), "abc-123_xyz");
        assert_eq!(sanitize_session("a/b\\c d"), "a_b_c_d");
        assert_eq!(sanitize_session(""), "default");
    }

    #[test]
    fn extract_subagent_type_from_tool_input() {
        // Real Droid shape: subagent_type is a Task tool parameter, nested
        // inside tool_input. This is the canonical case per Custom Droids
        // docs.
        let input = HookInput {
            tool_input: Some(json!({
                "subagent_type": "dpt-sec",
                "description": "audit auth",
                "prompt": "audit the auth flow"
            })),
            ..Default::default()
        };
        assert_eq!(extract_subagent_type(&input).as_deref(), Some("dpt-sec"));
    }

    #[test]
    fn extract_subagent_type_falls_back_to_top_level() {
        let input = HookInput {
            subagent_type: Some("dpt-dev".into()),
            ..Default::default()
        };
        assert_eq!(extract_subagent_type(&input).as_deref(), Some("dpt-dev"));
    }

    #[test]
    fn extract_subagent_type_prefers_top_level_when_both_set() {
        // Top-level wins; this avoids surprising substitutions when tests
        // explicitly pass the canonical value.
        let input = HookInput {
            subagent_type: Some("top".into()),
            tool_input: Some(json!({"subagent_type": "nested"})),
            ..Default::default()
        };
        assert_eq!(extract_subagent_type(&input).as_deref(), Some("top"));
    }

    #[test]
    fn extract_subagent_type_returns_none_when_missing() {
        let input = HookInput::default();
        assert!(extract_subagent_type(&input).is_none());
        // Empty strings count as missing.
        let input = HookInput {
            tool_input: Some(json!({"subagent_type": ""})),
            ..Default::default()
        };
        assert!(extract_subagent_type(&input).is_none());
    }

    #[test]
    fn parse_todos_handles_array_form() {
        let input = json!({
            "todos": [
                {"status": "pending", "content": "first"},
                {"status": "in_progress", "content": "second"},
                {"status": "completed", "content": "third"}
            ]
        });
        let todos = parse_todos(Some(&input)).unwrap();
        assert_eq!(todos.len(), 3);
        assert_eq!(todos[0], ("pending".into(), "first".into()));
        assert_eq!(todos[1], ("in_progress".into(), "second".into()));
    }

    #[test]
    fn parse_todos_handles_string_form() {
        // Documented TodoWrite shape per the system reminder: a numbered
        // multi-line string with `[status]` markers.
        let input = json!({
            "todos": "1. [pending] write tests\n2. [in_progress] implement\n3. [completed] design"
        });
        let todos = parse_todos(Some(&input)).unwrap();
        assert_eq!(todos.len(), 3);
        assert_eq!(todos[0], ("pending".into(), "write tests".into()));
        assert_eq!(todos[1], ("in_progress".into(), "implement".into()));
        assert_eq!(todos[2], ("completed".into(), "design".into()));
    }

    #[test]
    fn parse_todos_string_normalizes_status_aliases() {
        let s = "1. [todo] foo\n2. [doing] bar\n3. [done] baz";
        let todos = parse_todos_string(s);
        assert_eq!(todos[0].0, "pending");
        assert_eq!(todos[1].0, "in_progress");
        assert_eq!(todos[2].0, "completed");
    }

    #[test]
    fn parse_todos_string_skips_unmarked_lines() {
        let s = "Header\n1. [pending] real\nblank line\n2. [in_progress] also real";
        let todos = parse_todos_string(s);
        assert_eq!(todos.len(), 2);
        assert_eq!(todos[0].1, "real");
        assert_eq!(todos[1].1, "also real");
    }

    #[test]
    fn summarize_todos_works_with_string_form() {
        // Regression: if Droid passes the string form of `todos`, the plan
        // summary still produces the canonical output.
        let input = json!({
            "todos": "1. [completed] alpha\n2. [in_progress] beta\n3. [pending] gamma"
        });
        let s = summarize_todos(Some(&input)).unwrap();
        assert!(s.contains("1/3 completed"));
        assert!(s.contains("1 in progress"));
        assert!(s.contains("1 pending"));
        assert!(s.contains("Current: beta"));
    }
}
