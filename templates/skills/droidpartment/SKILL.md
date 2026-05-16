---
name: droidpartment
description: Overview skill for the Droidpartment toolkit. Loads automatically when the user mentions Droidpartment, dpt, the token saver, sub-droids (dpt-*), wave execution, or the orchestration workflow.
---

# Droidpartment

Droidpartment v4 is a token-saving multi-agent toolkit for Factory's Droid CLI.

## What is wired

- Native binary `dpt` at `~/.factory/bin/dpt(.exe)`.
- 9 hooks in `~/.factory/settings.json` per [Droid hooks reference](https://docs.factory.ai/reference/hooks-reference.md):
  - `SessionStart` injects the operating contract + `[ProjectMemory: <abs path>]` marker.
  - `PreToolUse` auto-rewrites noisy `Execute` commands through `dpt run --` (token compaction).
  - `PostToolUse` records stats and re-injects a plan summary on every `TodoWrite` call.
  - `Stop` reads `<ProjectMemory>/artifacts/STORIES.md` and blocks premature termination if rows remain pending or `needs_revision`. Honors `stop_hook_active` to avoid loops.
  - `UserPromptSubmit`, `SubagentStop`, `SessionEnd`, `PreCompact`, `Notification` are silent.
- 18 specialist sub-droids in `~/.factory/droids/dpt-*.md`.
- 5 skill bundles (this one + `dpt-token-saver`, `dpt-bugfix`, `dpt-audit`, `dpt-fullstack`).
- YAML learning store under `~/.factory/memory/`.

## Three things to know

1. **Token saver is automated.** The `PreToolUse` hook auto-rewrites noisy commands (`cargo test`, `pytest`, `git status`, `rg`, `npm run build`, etc.) to run through `dpt run -- <cmd>`. Full output is saved to `~/.factory/raw-output/<date>/<id>/`; only a semantic summary enters context. Recover with `dpt raw <id>`. Token counts are exact via `tiktoken-rs` (`o200k_base`).

2. **Plan ledger is automated.** Use `TodoWrite` for any multi-step task; the `PostToolUse:TodoWrite` hook re-injects a fresh `Plan: X/Y completed, Z in progress` summary on every call. Sub-droids that drive multi-wave work (`dpt-scrum`) also persist `<ProjectMemory>/artifacts/STORIES.md`.

3. **Sub-droids are optional.** The `dpt-*` sub-droids are delegation targets for the `Task` tool. Use them when isolated context or expert framing helps. The orchestrator does **not** auto-dispatch; you are responsible for routing via the `Follow-up:` text contract each sub-droid returns.

## Quick reference

```bash
# Verify install
dpt --version
dpt config
npx droidpartment doctor

# Use the compactor explicitly (PreToolUse already does this for you)
dpt run -- cargo test --workspace
dpt run --json -- pytest tests -q
dpt raw <id>

# See savings + droid usage
dpt stats
dpt stats --by-adapter --daily
```

## Wave execution playbooks

| Skill              | When                                                              |
|--------------------|-------------------------------------------------------------------|
| `dpt-fullstack`    | Multi-component feature, touches >2 files, needs PRD + architecture |
| `dpt-bugfix`       | Specific bug, regression, or failing test in known scope           |
| `dpt-audit`        | Security / quality / readiness review on a branch or PR           |
| `dpt-token-saver`  | Anything about the compactor itself                                |

For multi-feature projects with milestones: prefer Droid's `/missions`. For plan-heavy single-feature work: prefer Droid's `/spec` (Shift+Tab).

## Specialists (18 sub-droids)

| Group     | Sub-droids                                                                  |
|-----------|-----------------------------------------------------------------------------|
| Memory    | `dpt-memory`, `dpt-output`                                                  |
| Planning  | `dpt-product`, `dpt-research`, `dpt-arch`, `dpt-scrum`                      |
| Code      | `dpt-dev`, `dpt-data`, `dpt-api`, `dpt-ux`, `dpt-ops`                       |
| Quality   | `dpt-qa`, `dpt-sec`, `dpt-perf`, `dpt-lead`, `dpt-review`                   |
| Docs      | `dpt-docs`, `dpt-grammar`                                                   |

Use `[P]` for parallel work and `[S]` for sequential when planning waves.

## Output contract (every sub-droid returns this)

```
Summary: <one line>

Findings:
- <bullet>

Artifacts:
- <abs path or relative to ProjectMemory> (created|read)

Follow-up:
- next_agent: <name|null>
- needs_revision: <true|false>
- revision_reason: "<why>"          # only if needs_revision: true
- revision_agent: <name>             # default dpt-dev, only if needs_revision
- confidence: <0-100>
```

The orchestrator parses this and decides the next `Task()`. Audit lanes returning `needs_revision: true` are capped at 3 revision rounds per `dpt-audit` policy.

## Where to look when something feels wrong

- `npx droidpartment status` -- install version + binary path + savings
- `npx droidpartment doctor` -- diagnostics
- `~/.factory/dpt-config.json` -- token-saver and behavior config
- `~/.factory/raw-output/` -- full output of compacted runs
- `~/.factory/memory/stats/compaction.json` -- cumulative savings
