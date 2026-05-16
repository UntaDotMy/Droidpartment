# Droidpartment v4

**Token-saving multi-agent orchestration for Factory's Droid CLI.** Native Rust compactor, auto-rewrite hooks, 18 expert sub-droids, learning memory.

```bash
npx droidpartment install
```

[![npm](https://img.shields.io/npm/v/droidpartment?style=flat-square&logo=npm&color=CB3837)](https://www.npmjs.com/package/droidpartment)
[![downloads](https://img.shields.io/npm/dm/droidpartment?style=flat-square&color=blue)](https://www.npmjs.com/package/droidpartment)
[![stars](https://img.shields.io/github/stars/UntaDotMy/Droidpartment?style=flat-square&logo=github)](https://github.com/UntaDotMy/Droidpartment)

---

## What v4 changes

The Python hook layer in v3 has been rewritten in Rust. Distribution moves to npm `optionalDependencies` (esbuild-style platform packages). The hook lifecycle is tuned for prompt-cache hygiene per Droid's official reference: `SessionStart` emits once and is cached, every other lifecycle event is silent unless action is required. The headline new feature is **the token saver**:

- The PreToolUse hook auto-rewrites noisy commands (`cargo test`, `pytest`, `git status`, `rg`, `npm run build`, etc.) to run through `dpt run --`.
- Full output is captured offline to `~/.factory/raw-output/<date>/<id>/`.
- Only a semantic summary enters the agent context.
- Recover any compacted run with `dpt raw <id>`.

Existing v3 installs are migrated automatically on `npx droidpartment update`. Learning YAMLs (`lessons.yaml`, `patterns.yaml`, `mistakes.yaml`) and per-project memory are preserved.

---

## Why

Without Droidpartment, the agent reads the full output of every test run, lint, search, and git command. A single `cargo test --workspace` can be 5-15 KB of context noise. With Droidpartment v4:

| Before | After |
|---|---|
| Full test output enters context | Compacted summary + raw recovery id |
| Every hook emits text per turn | Cache-friendly silent hooks |
| Hooks call `python <path>/hook-*.py` | Native Rust binary, ~10x faster |
| One agent jumps straight to coding | Wave-execution skills (PRD -> arch -> stories -> code) |

---

## Quick start

```bash
# 1. Install
npx droidpartment install

# 2. Enable Custom Droids in Factory
#    /settings -> Experimental -> Custom Droids

# 3. Restart the Droid CLI

# 4. Verify
npx droidpartment status
npx droidpartment doctor

# 5. Try the compactor
~/.factory/bin/dpt run -- echo hello
~/.factory/bin/dpt stats
```

---

## How the token saver works

```
User asks Droid to run `cargo test --workspace`
           |
           v
  Droid Execute tool fires
           |
           v
  PreToolUse hook (~5ms)  -- dpt hook pre-tool-use
           |
           v
  hook returns:
    permissionDecision: allow
    updatedInput.command: dpt run -- cargo test --workspace
           |
           v
  Droid runs the rewritten command
           |
           v
  dpt run -- cargo test --workspace
           |
           +-- captures stdout/stderr to ~/.factory/raw-output/.../<id>/
           |
           +-- selects test adapter
           |
           +-- prints compacted summary + `raw: dpt raw <id>`
           |
           v
  Only the summary enters the agent context.
```

Recover the full output any time:

```bash
dpt raw 20260514-093321-7a4b
```

See cumulative savings:

```bash
dpt stats
```

Configurable via `~/.factory/dpt-config.json`:

```json
{
  "tokenSaver": {
    "mode": "rewrite",
    "maxLines": 40,
    "rawRetentionDays": 14,
    "excludeCommands": ["git status", "rg"]
  }
}
```

`mode` accepts `rewrite` (default), `deny` (block + suggest, claude-core style), or `off`. `excludeCommands` is a per-command opt-out that wins over the built-in compact list.

---

## What gets installed

```
~/.factory/
  bin/dpt(.exe)               native Rust binary
  droids/dpt-*.md             18 sub-droid definitions (Custom Droids)
  skills/                     5 skill bundles
    droidpartment/SKILL.md
    dpt-token-saver/SKILL.md
    dpt-bugfix/SKILL.md
    dpt-audit/SKILL.md
    dpt-fullstack/SKILL.md
  memory/                     YAML learning store + projects/
  raw-output/                 compacted-run recovery (auto-pruned)
  AGENTS.md                   personal-scope agent contract
  settings.json               9 hook registrations
  dpt-config.json             token-saver + hook configuration
```

---

## Sub-droids

18 specialist Custom Droids that you (or the orchestrator) can invoke via the `Task` tool.

| Group   | Droids                                                                       |
|---------|------------------------------------------------------------------------------|
| Memory  | `dpt-memory`, `dpt-output`                                                   |
| Plan    | `dpt-product`, `dpt-research`, `dpt-arch`, `dpt-scrum`                       |
| Build   | `dpt-dev`, `dpt-data`, `dpt-api`, `dpt-ux`, `dpt-ops`                        |
| Audit   | `dpt-qa`, `dpt-sec`, `dpt-perf`, `dpt-lead`, `dpt-review`                    |
| Docs    | `dpt-docs`, `dpt-grammar`                                                    |

Each ships with its own frontmatter (`reasoningEffort`, scoped `tools`). Sub-droids run in isolated context windows and return a `Follow-up:` text contract; **there is no automatic dispatch** - the main orchestrator decides which (if any) to invoke via the `Task` tool. See `templates/AGENTS.md` for the full operating contract.

---

## Hook lifecycle (cache-friendly)

| Event              | Behavior                                                                                                              |
|--------------------|-----------------------------------------------------------------------------------------------------------------------|
| `SessionStart`     | Emits the operating contract + `[ProjectMemory: <abs path>]` once. Cached for the session window.                     |
| `UserPromptSubmit` | Aggressive keyword advisory. Injects 1-3 sub-droid suggestions when the prompt mentions audit/bug/feature/security/perf/etc. Hints only - the orchestrator still decides whether to call Task(). |
| `PreToolUse`       | On `Execute`: auto-rewrites noisy commands to `dpt run -- <cmd>` (or `deny` mode). On `Task`: hard-denies a 4th revision attempt against any audit lane (cap = 3 rounds), and marks the matching STORIES.md row `in_progress`. |
| `PostToolUse`      | Records tool stats. On `TodoWrite`: re-injects a fresh `Plan: X/Y completed, Z in progress. Current: ...` summary and persists todos to a session-scoped file. On `Task`: parses `Follow-up:` signals (`needs_revision`, `revision_agent`, `revision_reason`, `next_agent`, `confidence`), updates the matching STORIES.md row, manages the per-lane revision counter, and injects wave progress + the next `[P]` Task() calls. |
| `Stop`             | Reads `<ProjectMemory>/artifacts/STORIES.md` and the session todos snapshot. Returns `decision: block` when work remains pending / in_progress / needs_revision. Honors `stop_hook_active` to avoid loops. Silent when both sources are clean or absent. |
| `SubagentStop`     | Silent.                                                                                                               |
| `SessionEnd`       | Silent.                                                                                                               |
| `PreCompact`       | Silent (reserved for memory checkpoint).                                                                              |
| `Notification`     | Silent.                                                                                                               |

Per Droid's hooks reference, output written by post-prompt-cache events is paid for every prompt. The hook events that emit text (`UserPromptSubmit` advisory, `PostToolUse:Task` wave update, `PostToolUse:TodoWrite` plan summary, `Stop` block) are intentional control-plane signals; everything else stays silent.

## Wave automation (real, not advisory)

What actually runs in code rather than relying on the agent following instructions:

- **STORIES.md state machine.** When `dpt-scrum` writes a STORIES.md table, the hook layer mutates the `Status` column as Tasks fire. `pending` -> `in_progress` (PreToolUse:Task) -> `done` or `needs_revision` (PostToolUse:Task signal parsing). Parallel `[P]` waves with the same agent (e.g., two `dpt-dev` rows) are handled correctly because the predicate picks the first matching row in each transition.
- **Hard revision cap.** Audit lanes (`dpt-qa`, `dpt-sec`, `dpt-perf`, `dpt-lead`, `dpt-review`) get one persistent counter per `(project_slug, lane)` tracked in `~/.factory/memory/stats/revision_state.json`. Three `needs_revision` rounds is the cap; the 4th attempt is denied at PreToolUse with `permissionDecision: deny`. The agent has to escalate, change approach, or ask the user instead of looping.
- **Wave progress injection.** After every `Task` returns, PostToolUse computes the current wave (lowest unfinished), counts of done/pending/in_progress/needs_revision, and the next `[P]` calls. The orchestrator gets this as `additionalContext`, so wave advancement is concrete instead of guessed.
- **Stop backstop.** STORIES.md unfinished rows or session-scoped TodoWrite items both block Stop. The agent can still terminate with `stop_hook_active=true` per Droid's loop-prevention contract.

What we honestly cannot do: **hooks cannot synthesize `Task()` calls**. That is a Factory hook contract limitation (hooks return decisions, not new tool calls). The orchestrator is still the one issuing the `Task()`; the hook layer enforces the workflow shape around it.

---

## Commands

```
npx droidpartment install         install to ~/.factory
npx droidpartment update          refresh (migrates v3 Python -> v4 Rust)
npx droidpartment status          version + binary path + hook count
npx droidpartment doctor          full diagnostics
npx droidpartment uninstall       remove (preserves YAMLs unless --purge)
```

The `dpt` binary itself:

```
dpt run -- <cmd>                  run with compaction
dpt raw <id> | --list | --prune-older-than-days N
dpt stats                         compaction + droid + tool stats
dpt config                        resolved config
dpt install-hooks                 print the settings.json block
```

---

## Migration from v3

If you have v3 (Python hooks) installed:

```bash
npx droidpartment update
```

The installer detects the Python hook layer, removes `~/.factory/memory/hooks/` and the top-level `*.py` modules, copies the Rust binary into `~/.factory/bin/`, rewrites `~/.factory/settings.json` to call `dpt hook <event>` instead of `python <path>.py`, and preserves your learning YAMLs and per-project memory unchanged.

If anything goes wrong:

```bash
npx droidpartment doctor    # diagnose
npx droidpartment uninstall # clean slate (YAMLs preserved unless --purge)
```

---

## Build from source

```bash
git clone https://github.com/UntaDotMy/Droidpartment
cd Droidpartment
cd rust && cargo build --release
cd ..
node bin/install.js install --project
```

The installer falls back to `rust/target/release/dpt(.exe)` if no platform npm package is resolvable.

---

## Requirements

- **Factory AI** Droid CLI with Custom Droids enabled
- **Node.js** 16+ (for the installer only)
- **Rust** is **not** required at install time (binary ships via npm); only required if you build from source

No Python required. v4 has no Python in the runtime path.

---

## License

MIT - see [LICENSE](LICENSE)

---

<p align="center"><sub>Made for the Factory Droid community</sub></p>
