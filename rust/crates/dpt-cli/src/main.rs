use anyhow::Result;
use clap::Parser;

mod advisory;
mod cli;
mod compactor;
mod config;
mod flock;
mod hooks;
mod paths;
mod revision;
mod stats;
mod stories;
mod tokens;

fn main() -> Result<()> {
    let cli = cli::Cli::parse();
    cli::dispatch(cli)
}
