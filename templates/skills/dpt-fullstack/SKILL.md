---
name: dpt-fullstack
description: Wave-execution playbook for non-trivial features. Use when the user asks for a multi-component feature, a new system, or anything that touches more than two files and benefits from PRD/architecture/stories/code/audit phases.
---

# Full-feature wave execution

Use this playbook when the request is complex enough that jumping straight to
code would waste tokens (per Droid's token-efficiency guide). It mirrors
Factory's Specification Mode pattern but coordinates the dpt-* sub-droids.

## How waves actually run

The orchestrator (this assistant) is the only thing that issues `Task()` calls; sub-droids run in isolated context windows and return text. Wave execution is a text contract, not a runtime primitive:

1. `dpt-scrum` writes `<ProjectMemory>/artifacts/STORIES.md` with one row per task and per-wave grouping. Each row carries a status column (`pending|in_progress|done|needs_revision|blocked`) and is mirrored to `TodoWrite`.
2. The orchestrator batches all `[P]` rows of the current wave into one assistant turn (parallel `Task()` calls), waits for them all to return, then advances to the next wave.
3. Audit lanes return `needs_revision: <bool>` and `revision_agent: <name>`. The orchestrator runs the revision then re-invokes the audit lane. Hard cap: **3 rounds per audit lane**, then escalate to the user.
4. The Stop hook reads STORIES.md before every termination; if any row is `pending`, `in_progress`, or `needs_revision` it returns `decision: block` with a reason listing the open work. The hook honors `stop_hook_active` so it never loops infinitely.
5. The PostToolUse:TodoWrite hook re-injects a fresh plan summary on every TodoWrite call, so the orchestrator always sees current todo state.

For larger work consider Droid's official surfaces:
- `/spec` (Shift+Tab) for plan-then-implement loops on a single feature.
- `/missions` for multi-feature projects with milestone-based validation.
- For massive refactors (>30 files or >5 phases), prefer fresh sessions per phase.

## When to invoke this skill

- Touches more than two files
- Crosses backend / frontend / infra boundaries
- Requires understanding existing patterns
- Has unclear requirements
- Is security-sensitive

## Wave plan

```
Wave 1 [INIT]   Task(dpt-memory, "START: <feature>")
                Task(dpt-research, "<scope> best practices")     # parallel

Wave 2 [PLAN]   Task(dpt-product, "create PRD.md for <feature>")

Wave 3 [DESIGN] Task(dpt-arch, "create ARCHITECTURE.md")

Wave 4 [STORIES] Task(dpt-scrum, "STORIES.md with [P]/[S] markers")

Wave 5 [CODE]   Task(dpt-dev, "implement <component-1>")          # parallel per component
                Task(dpt-dev, "implement <component-2>")

Wave 6 [AUDIT]  Task(dpt-qa, "run tests, verify behaviour")       # all parallel
                Task(dpt-sec, "OWASP audit on changed surface")
                Task(dpt-lead, "SOLID review")

Wave 7 [FINISH] Task(dpt-memory, "END: capture lessons")
                Task(dpt-output, "synthesize final report")
```

`[P]` = parallel-safe, `[S]` = must wait for predecessor.

## Artifacts produced

- `PRD.md`        - dpt-product
- `ARCHITECTURE.md` - dpt-arch
- `STORIES.md`    - dpt-scrum
- Code            - dpt-dev (one per component, parallel)

## Token-efficiency notes

- Use `dpt run -- <cmd>` for every test/build/lint command (the PreToolUse hook
  does this for you, but issuing it explicitly is also fine).
- After Wave 5, before Wave 6, kick off the audit lanes in parallel rather than
  sequentially. Three parallel reads of the same diff is cheaper than three
  sequential reads with re-built context.
- Skip waves whose output is not needed. Bug fixes can usually drop Wave 2-4.

## Output contract

Each sub-droid returns:

```
Summary: <one-liner>

Findings:
- <bullet>

Follow-up:
- next_agent: <name or null>
- confidence: <0-100>
```

## Skip-list

Do **not** invoke this playbook when:

- The change is a one-line edit / typo / config tweak.
- The user explicitly says "just do it" / "no plan".
- The work is in an unfamiliar repo without an AGENTS.md and the agent should
  use Spec Mode instead.
