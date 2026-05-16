//! Cross-platform file locking helpers backed by `fs2`.
//!
//! Hooks fire concurrently on parallel `[P]` Tasks (per Droid's hooks
//! reference: "All matching hooks run in parallel"), so any read-modify-write
//! against a shared file (STORIES.md, revision_state.json, session todos)
//! needs an exclusive lock around the full cycle to avoid lost updates.
//!
//! `fs2::FileExt::lock_exclusive` provides that on Windows (LockFileEx),
//! Linux (flock LOCK_EX), and macOS. The lock is held only while `with_lock`
//! is on the stack; dropping the file handle releases the OS lock.
//!
//! The lock file is a separate sidecar (`<path>.lock`) so the locked file
//! can still be opened with normal file APIs (atomic temp+rename works
//! around any concurrent open).

use anyhow::{Context, Result};
use fs2::FileExt;
use std::fs::OpenOptions;
use std::path::Path;

/// Acquire an exclusive lock on `<target>.lock` for the duration of `f`.
/// Creates the lock file (and parent directory) if missing.
pub fn with_exclusive_lock<F, T>(target: &Path, f: F) -> Result<T>
where
    F: FnOnce() -> Result<T>,
{
    if let Some(parent) = target.parent() {
        std::fs::create_dir_all(parent).with_context(|| {
            format!("failed to create parent directory for lock at {:?}", parent)
        })?;
    }
    let lock_path = lock_path_for(target);
    let lock_file = OpenOptions::new()
        .create(true)
        .read(true)
        .write(true)
        .truncate(false)
        .open(&lock_path)
        .with_context(|| format!("failed to open lock file at {:?}", lock_path))?;
    lock_file
        .lock_exclusive()
        .with_context(|| format!("failed to acquire exclusive lock on {:?}", lock_path))?;
    let result = f();
    // Best-effort unlock on success and error paths. The drop of `lock_file`
    // would release the lock automatically, but unlocking explicitly clears
    // the OS handle eagerly.
    let _ = FileExt::unlock(&lock_file);
    result
}

fn lock_path_for(target: &Path) -> std::path::PathBuf {
    let mut s = target.as_os_str().to_owned();
    s.push(".lock");
    std::path::PathBuf::from(s)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Arc, Mutex};
    use std::thread;
    use std::time::Duration;

    fn tempfile(suffix: &str) -> std::path::PathBuf {
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!("dpt-flock-{nanos}-{suffix}"))
    }

    #[test]
    fn lock_serializes_concurrent_writers() {
        let target = tempfile("serial");
        std::fs::write(&target, "0").unwrap();
        let target = Arc::new(target);
        let order = Arc::new(Mutex::new(Vec::<u32>::new()));

        let handles: Vec<_> = (0..8)
            .map(|i| {
                let target = Arc::clone(&target);
                let order = Arc::clone(&order);
                thread::spawn(move || {
                    with_exclusive_lock(&target, || {
                        let body = std::fs::read_to_string(&*target).unwrap();
                        let n: u32 = body.trim().parse().unwrap();
                        // Hold the lock briefly to make any race observable.
                        thread::sleep(Duration::from_millis(5));
                        std::fs::write(&*target, format!("{}", n + 1)).unwrap();
                        order.lock().unwrap().push(i);
                        Ok(())
                    })
                    .unwrap();
                })
            })
            .collect();
        for h in handles {
            h.join().unwrap();
        }
        let final_n: u32 = std::fs::read_to_string(&*target)
            .unwrap()
            .trim()
            .parse()
            .unwrap();
        assert_eq!(final_n, 8, "every writer's increment must land");
        let _ = std::fs::remove_file(&*target);
        let _ = std::fs::remove_file(lock_path_for(&target));
    }

    #[test]
    fn lock_path_appends_lock_suffix() {
        let p = std::path::Path::new("/tmp/foo.json");
        assert_eq!(
            lock_path_for(p),
            std::path::PathBuf::from("/tmp/foo.json.lock")
        );
    }
}
