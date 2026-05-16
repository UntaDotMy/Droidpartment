# Droidpartment v4 active

This file is installed at `~/.factory/AGENTS.md`. Project-level `./AGENTS.md` always wins on conflicting rules (per [Droid AGENTS.md docs](https://docs.factory.ai/cli/configuration/agents-md.md)).

## What is wired

- Native binary at `~/.factory/bin/dpt(.exe)`. Run `dpt --help` for surfaces.
- 9 hooks registered in `~/.factory/settings.json` per [Droid hooks reference](https://docs.factory.ai/reference/hooks-reference.md):
  - `SessionStart` injects this contract + a deterministic `[ProjectMemory: <abs path>]` marker.
  - `UserPromptSubmit` injects sub-droid suggestions when prompt keywords match (audit, bug, feature, security, perf, etc.). Aggressive matching, advisory only.
  - `PreToolUse` auto-rewrites noisy `Execute` commands through `dpt run --` for compaction. On `Task`: hard-denies a 4th revision attempt against any audit lane (cap = 3 rounds per lane per project), and marks the matching STORIES.md row `in_progress`.
  - `PostToolUse` records stats. On `TodoWrite`: re-emits a fresh plan summary and persists todos to a session-scoped file. On `Task`: parses `Follow-up:` signals (`needs_revision`, `revision_agent`, `revision_reason`, `next_agent`, `confidence`), updates the matching STORIES.md row, manages the revision counter, and injects wave progress + the next `[P]` Task() calls.
  - `Stop` reads STORIES.md and the session todos snapshot. Returns `decision: block` with row details when work remains. Honors `stop_hook_active` to avoid loops.
  - `SubagentStop`, `SessionEnd`, `PreCompact`, `Notification` are silent (zero per-turn token cost).
- 18 specialist sub-droids in `~/.factory/droids/dpt-*.md`, invoked via the `Task` tool.
- 5 skill bundles in `~/.factory/skills/`.
- YAML learning data under `~/.factory/memory/` (preserved across updates).
- Revision state in `~/.factory/memory/stats/revision_state.json` (per-lane per-project counter).

## Token saver

The `PreToolUse` hook auto-rewrites noisy commands (test/build/lint/grep/git/docker/etc.) to run through `dpt run --`. The compactor captures full output to `~/.factory/raw-output/<date>/<id>/`, applies a semantic adapter, and returns a short summary. Recover full output with `dpt raw <id>`. Track savings with `dpt stats`, `dpt stats --by-adapter`, `dpt stats --daily`.

Token counts are exact via `tiktoken-rs` (`o200k_base` BPE). Configurable in `~/.factory/dpt-config.json`: `tokenSaver.mode` is `rewrite` (default), `deny`, or `off`. `tokenSaver.excludeCommands` is a per-command opt-out.

Cache framing: the SessionStart `additionalContext` is the only Droid-documented "load once per session" surface ([Droid hooks reference](https://docs.factory.ai/reference/hooks-reference.md)). Beyond that, prompt-cache TTL/breakpoint specifics are vendor-side and not promised by Factory docs. We keep per-turn hooks silent so each turn's transcript stays small.

## Sub-droid roster

The orchestrator (this assistant) is the only thing that can issue `Task()` calls. Sub-droids run in isolated context windows ([Custom Droids docs](https://docs.factory.ai/cli/configuration/custom-droids.md)), return a `Follow-up:` text contract, and the orchestrator routes the next call. **There is no automatic dispatch.**

| Group   | Droids                                                                       |
|---------|------------------------------------------------------------------------------|
| Memory  | `dpt-memory`, `dpt-output`                                                   |
| Plan    | `dpt-product`, `dpt-research`, `dpt-arch`, `dpt-scrum`                       |
| Build   | `dpt-dev`, `dpt-data`, `dpt-api`, `dpt-ux`, `dpt-ops`                        |
| Audit   | `dpt-qa`, `dpt-sec`, `dpt-perf`, `dpt-lead`, `dpt-review`                    |
| Docs    | `dpt-docs`, `dpt-grammar`                                                    |

Use `[P]` for parallel-safe Task() batches, `[S]` for sequential-only steps.

## Operating contract

1. **Project AGENTS.md and README.md win.** This file is the personal-scope baseline.
2. **Iterative loop** for non-trivial work: Memory(START) -> Research -> Plan/Spec -> Implement -> Test -> Audit -> Memory(END) -> Output. Each step is a sub-droid; you decide whether to invoke based on scope.
3. **Research before code in unfamiliar territory.** Route through `dpt-research` for current best practices and official docs.
4. **Hook rerun discipline.** If `PreToolUse` denies with `Rerun that as: <cmd>`, run that exact command. It is not a failure.
5. **TodoWrite is the live ledger.** Use it for any multi-step task: mark items `[in_progress]` before starting, `[completed]` immediately after each finishes. The PostToolUse hook re-injects the current plan after every TodoWrite call.
6. **Completion reconciliation.** Before final answer, re-read the user's brief and confirm every explicit requirement has evidence (test passing, file changed, command run). Partial work is not done.
7. **Restart Droid CLI** after `npx droidpartment install` or `update` so hook changes take effect.

## Wave + revision loop (enforced by hooks)

For multi-component work the orchestrator drives waves directly via Task() batching. The hook layer enforces the workflow shape so you cannot accidentally skip steps:

- `dpt-scrum` writes `<ProjectMemory>/artifacts/STORIES.md` with the schema `| ID | Wave | Type | Agent | Task | Depends | Status |`. Status values: `pending | in_progress | done | needs_revision | blocked`.
- The hook layer mutates `Status` automatically: `pending` -> `in_progress` (PreToolUse:Task) -> `done` or `needs_revision` (PostToolUse:Task signal parsing). Parallel `[P]` waves with the same agent are handled correctly because each transition picks the first matching row.
- Audit lanes (`dpt-qa`, `dpt-sec`, `dpt-perf`, `dpt-lead`, `dpt-review`) signal `needs_revision: <bool>` plus optional `revision_agent` (default `dpt-dev`) and `revision_reason` in their `Follow-up:` block. PostToolUse parses both the text form and JSON object form.
- Hard cap: 3 rounds per `(project, lane)`. The 4th `Task('<audit-lane>')` call is denied at PreToolUse with `permissionDecision: deny`. Counter persists in `~/.factory/memory/stats/revision_state.json`. A successful audit (`needs_revision: false`) resets the counter.
- After every `Task` returns, PostToolUse injects wave progress (`Wave 3/5 [DESIGN]: 1/3 done, 1 in_progress`) plus the next `[P]` Task() calls so wave advancement is concrete.
- `Stop` blocks termination while STORIES.md or session todos contain unfinished work, unless `stop_hook_active=true` (Droid loop-prevention contract).

Hooks cannot synthesize Task() calls (Factory contract limitation). The orchestrator is still responsible for issuing the actual `Task()`, but the hook layer enforces the workflow around it: status mutates, the cap is real, Stop blocks, advisory hints route attention.

For multi-feature projects with milestones, prefer Droid's official `/missions` ([Missions docs](https://docs.factory.ai/cli/features/missions.md)). For plan-heavy single-feature work, prefer Droid's `/spec` (Shift+Tab; [Specification Mode docs](https://docs.factory.ai/cli/user-guides/specification-mode.md)). For massive refactors (>30 files or >5 phases), prefer fresh sessions per phase ([Implementing Large Features](https://docs.factory.ai/cli/user-guides/implementing-large-features.md)).

## Useful commands

```
npx droidpartment status     # version, hooks, savings
npx droidpartment doctor     # full health check
dpt stats                    # cumulative compaction stats
dpt stats --by-adapter --daily
dpt raw <id>                 # recover full output of a compacted run
dpt config                   # show resolved config
```

Native Droid commands: `/cost`, `/compact`, `/spec`, `/missions`, `/readiness-report`, `/hooks`.

## Layout

```
~/.factory/
  bin/dpt(.exe)               native binary
  droids/dpt-*.md             18 sub-droid definitions
  skills/                     5 skill bundles
  memory/                     YAML learning + per-project memory
  raw-output/<date>/<id>/     compacted-run recovery (auto-pruned)
  AGENTS.md                   this file
  settings.json               hook registrations
  dpt-config.json             token saver + behavior config
```
