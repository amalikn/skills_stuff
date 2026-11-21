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

> **Learned 2026-11-20** · restoring a Git repository to a new path · VERIFIED_PRIMARY (seen: P2 gate run p2-gate-20261120_161642; fixed and re-run green) · Source: continuum-app
> `apps/agent/src/tree/restore.rs` `link_worktrees` (a775069), BUG-247 · Falsifier: a `git worktree repair` that never writes outside the paths given on its command line.
> `git worktree repair` follows the absolute paths already stored in the worktree links. When a restored copy still names the source's path and that path
> resolves on the target (a VM's shared mount of the host, a same-named checkout), git 2.43 rewrote the *source's* link files. macOS git did not, so a unit
> test on the Mac cannot catch it. Rewrite the two link files yourself in the staged copy and make the gate hash the source tree before and after.
>
> ```rust
> fs::write(&dot_git, format!("gitdir: {}\n", into.join(main).join(".git/worktrees").join(&name).display()))?;
> fs::write(admin.join("gitdir"), format!("{}\n", into.join(wt).join(".git").display()))?;
> ```
>
> Also from the same gate: symlink permission bits are not portable (macOS keeps 0755 from lchmod, Linux reports 0777, Git ignores them), so a cross-OS file
> listing records mode 0 for links. An integration test's submodule file lives beside the test: `#[path = "agent_e2e/p2_gate.rs"] mod p2_gate;` in
> `tests/agent_e2e.rs` (without `#[path]` rustc looks for `tests/p2_gate.rs`).

> **Learned 2026-11-22** · a process-wide memo of "already checked" facts · VERIFIED_PRIMARY (tests run; a store call dropped from 2.29 s to 1.52 s) · Source: continuum-app
> `crates/continuum-store/src/restic/mod.rs` `known`/`remember` (1f44449) · Falsifier: the fact can become false while the process runs (then the memo must be cleared on the failure).
> When every call re-checks something that, once true, stays true for the process (a restic repository exists; repositories are never deleted under it), keep a `static` set behind `OnceLock` and a
> `Mutex`, record the fact only after it was seen true, and treat a poisoned lock as "not known":

```rust
static KNOWN: std::sync::OnceLock<std::sync::Mutex<std::collections::HashSet<String>>> = std::sync::OnceLock::new();
fn known(url: &str) -> bool { KNOWN.get_or_init(Default::default).lock().is_ok_and(|k| k.contains(url)) }
fn remember(url: &str) { if let Ok(mut k) = KNOWN.get_or_init(Default::default).lock() { k.insert(url.to_string()); } }
```

> **Learned 2026-11-22** · a tar in memory with the `tar` crate · VERIFIED_PRIMARY (round-trip test) · Source: continuum-app `apps/agent/src/wsbundle.rs` (1f44449) · Falsifier: none expected.
> `tar::Builder::new(Vec::new())` writes to memory; each entry needs a header with its size, mode and checksum set before `append_data`, and `into_inner()` returns the bytes. Reading back,
> `tar::Archive::new(&bytes[..]).entries()` yields entries whose `path()` and `read_to_end` give name and contents. Recognise the format by its first entry's name, which a tar starts with.

```rust
let mut h = tar::Header::new_gnu();
h.set_size(bytes.len() as u64);
h.set_mode(0o600);
h.set_cksum();
t.append_data(&mut h, name, bytes)?;
```

