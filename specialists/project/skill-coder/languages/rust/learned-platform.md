---
Title: rust override - learned platform
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/rust.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned platform part of the rust override; the entry file holds the tools and the core rule mapping.
---

# rust: learned platform

Part of [rust.md](../rust.md).

> **Learned 2026-11-19** · Unix socket path length · VERIFIED_PRIMARY (macOS error "path must be shorter than SUN_LEN") · Source: continuum-app
> `crates/continuum-adapter-host/src/lib.rs` (182e164) · Falsifier: none expected; sockaddr_un is fixed. A Unix socket path must fit sockaddr_un: 104 bytes on macOS, 108 on Linux. macOS temp folders
> (`/var/folders/...`) plus a UUID exceed it. Check the length before binding and fail with a clear message; tests use a short folder such as `/tmp/<prefix>-<12 hex>`.

> **Learned 2026-11-19** · a timeout around `std::process::Command` · VERIFIED_PRIMARY (std has no `wait_timeout`; tests run) · Source: continuum-app `apps/agent/src/bundle.rs` `git()` (1a7521e) ·
> Falsifier: a std `Child` method that waits with a deadline
> `std::process::Child` can only `wait()` forever, so a hung child (git on a stalled network mount) blocks the caller. Without adding a crate, poll `try_wait()` against a deadline,
> then `kill()` and `wait()` to reap it and report the timeout. In async code prefer `tokio::process` with `tokio::time::timeout`.
>
> ```rust
> let mut child = Command::new("git").args(args).stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn()?;
> let start = Instant::now();
> loop {
>   if child.try_wait()?.is_some() { break; }
>   if start.elapsed() > GIT_TIMEOUT { let _ = child.kill(); let _ = child.wait(); return Err("git timed out".into()); }
>   std::thread::sleep(Duration::from_millis(20));
> }
> ```
> Caveat: a child that fills its stdout pipe before exiting would stall this loop; it is fine for git's short outputs, not for large ones (read the pipes on a thread then).
