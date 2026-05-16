---
name: dpt-token-saver
description: Explains and operates the Droidpartment token-saving compactor. Use when the user asks about token usage, savings, compaction, the dpt run command, or how the PreToolUse hook auto-rewrites noisy commands.
---

# Droidpartment token saver

The Droidpartment token saver is a native Rust compactor that prevents noisy
shell-command output from entering the agent context.

## How it works

1. The PreToolUse hook (`dpt hook pre-tool-use`) inspects every `Execute` tool
   call.
2. If the command head matches a known noisy pattern (test, build, lint, search,
   git, docker, kubectl, etc.), the hook returns
   `permissionDecision: "allow"` with `updatedInput.command` rewritten to
   `dpt run -- <original>`.
3. Factory's Droid CLI runs the rewritten command. The compactor executes it,
   captures full stdout/stderr to `~/.factory/raw-output/<date>/<id>/`, and
   returns a short summary plus a recovery id.
4. The agent only sees the compacted summary. Full output is one command away
   via `dpt raw <id>`.

## Commands

| Command                                | Purpose                                            |
|----------------------------------------|----------------------------------------------------|
| `dpt run -- <cmd>`                     | Run a command through the compactor               |
| `dpt run --no-compact -- <cmd>`        | Bypass compaction, still record raw output        |
| `dpt run --json -- <cmd>`              | Emit a JSON envelope with token stats             |
| `dpt run --max-lines <N> -- <cmd>`     | Override the line cap for this run                |
| `dpt raw <id>`                         | Print full raw output of a compacted run          |
| `dpt raw --list`                       | List recent raw runs                              |
| `dpt raw --prune-older-than-days 30`   | Prune the raw store                               |
| `dpt stats`                            | Show cumulative compaction + droid + tool stats   |
| `dpt config`                           | Show resolved config                              |
| `dpt config --json`                    | Same, JSON                                        |

## Configuration

Edit `~/.factory/dpt-config.json`:

```json
{
  "tokenSaver": {
    "mode": "rewrite",
    "maxLines": 40,
    "rawRetentionDays": 14,
    "compactCommands": ["pytest", "cargo", "rg", "git", "docker", "..."]
  }
}
```

Per-event silence is hard-coded in the binary; not user-configurable. Only the tokenSaver section above can be configured.

| Field                     | Default     | Effect                                                                         |
|---------------------------|-------------|--------------------------------------------------------------------------------|
| `tokenSaver.mode`         | `"rewrite"` | `rewrite` = auto-rewrite (recommended). `deny` = block + suggest. `off` = disabled. |
| `tokenSaver.maxLines`     | `40`        | Max lines in compact summary                                                  |
| `tokenSaver.rawRetentionDays` | `14`    | Auto-prune raw entries older than this                                         |
| `tokenSaver.compactCommands`  | (list)  | Command heads that trigger auto-rewrite                                       |

## Adapter selection

The compactor picks a semantic adapter by command head:

- `cargo test` / `pytest` / `jest` / `go test` → **test** adapter (signal lines, status, exit code)
- `cargo build` / `npm run build` / `tsc` / `make` → **build** adapter
- `eslint` / `prettier` / `ruff` / `mypy` / `cargo fmt` → **lint** adapter
- `git status|log|diff|show|...` → **git** adapter
- `rg` / `grep` / `find` / `git grep` → **search** adapter (count + truncated matches)
- `docker` / `kubectl` / `helm` / `terraform` → **docker** adapter
- `tail` / `cat` / `journalctl` → **logs** adapter
- anything else → **generic** adapter (signal lines + head/tail)

## Verifying it is working

```
dpt --version             # should print "dpt 4.0.0" or higher
dpt config                # shows current mode
dpt run -- echo hello     # exits 0 with a tiny summary
dpt stats                 # populated after a few runs
```
