use anyhow::Result;
use clap::{Parser, Subcommand};

use crate::compactor;
use crate::config::DptConfig;
use crate::hooks;
use crate::stats;

#[derive(Parser, Debug)]
#[command(
    name = "dpt",
    version,
    about = "Droidpartment CLI: token-saving multi-agent orchestration for Factory AI",
    long_about = None,
    propagate_version = true
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Subcommand, Debug)]
pub enum Command {
    /// Run a command through the token-saving compactor
    Run {
        /// Command and args to execute (use -- to pass through flags)
        #[arg(trailing_var_arg = true, allow_hyphen_values = true, num_args = 1..)]
        cmd: Vec<String>,

        /// Skip compaction and stream raw output
        #[arg(long)]
        no_compact: bool,

        /// Output JSON envelope with token stats and raw recovery id
        #[arg(long)]
        json: bool,

        /// Override the max number of lines kept after compaction
        #[arg(long)]
        max_lines: Option<usize>,
    },

    /// Show or list raw output from a previous compacted run
    Raw {
        /// Raw recovery id printed by `dpt run`
        id: Option<String>,

        /// List recent raw runs instead of printing one
        #[arg(long)]
        list: bool,

        /// Prune raw entries older than this many days (e.g. 30)
        #[arg(long)]
        prune_older_than_days: Option<u32>,
    },

    /// Print compaction and learning stats
    Stats {
        /// Output stats as JSON
        #[arg(long)]
        json: bool,
        /// Break down compactions by adapter
        #[arg(long)]
        by_adapter: bool,
        /// Show per-day totals (last 14 days)
        #[arg(long)]
        daily: bool,
    },

    /// Hook handlers invoked by Factory's settings.json hook entries
    #[command(subcommand)]
    Hook(HookCmd),

    /// Show resolved config (mode, compactCommands, retention)
    Config {
        #[arg(long)]
        json: bool,
    },

    /// Print the hook block that should be merged into ~/.factory/settings.json
    InstallHooks {
        /// Print as compact one-line JSON
        #[arg(long)]
        compact: bool,
    },
}

#[derive(Subcommand, Debug)]
pub enum HookCmd {
    SessionStart,
    SessionEnd,
    UserPromptSubmit,
    PreToolUse,
    PostToolUse,
    Stop,
    SubagentStop,
    PreCompact,
    Notification,
}

pub fn dispatch(cli: Cli) -> Result<()> {
    match cli.command {
        Command::Run {
            cmd,
            no_compact,
            json,
            max_lines,
        } => compactor::run_cmd(cmd, no_compact, json, max_lines),
        Command::Raw {
            id,
            list,
            prune_older_than_days,
        } => compactor::raw(id, list, prune_older_than_days),
        Command::Stats {
            json,
            by_adapter,
            daily,
        } => stats::show(json, by_adapter, daily),
        Command::Hook(event) => hooks::dispatch(event),
        Command::Config { json } => {
            let cfg = DptConfig::load()?;
            if json {
                println!("{}", serde_json::to_string_pretty(&cfg)?);
            } else {
                println!("token saver mode: {:?}", cfg.token_saver.mode);
                println!("max lines:         {}", cfg.token_saver.max_lines);
                println!("retention days:    {}", cfg.token_saver.raw_retention_days);
                println!(
                    "compact commands:  {}",
                    cfg.token_saver.compact_commands.len()
                );
            }
            Ok(())
        }
        Command::InstallHooks { compact } => {
            let block = hooks::settings_block();
            if compact {
                println!("{}", serde_json::to_string(&block)?);
            } else {
                println!("{}", serde_json::to_string_pretty(&block)?);
            }
            Ok(())
        }
    }
}
