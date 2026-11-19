---
Title: rust override - learned async and tests
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/rust.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned async and tests part of the rust override; the entry file holds the tools and the core rule mapping.
---

# rust: learned async and tests

Part of [rust.md](../rust.md).

> **Learned 2026-11-19** · `#[tokio::test]` and blocking child processes · VERIFIED_PRIMARY (test run) · Source: continuum-app `apps/coordinator/tests/agent_e2e.rs` (b25dbf8)
> · Falsifier: the stand-in server answering while the test thread blocks on `Command::output()`. `#[tokio::test]` runs on one thread. A test that serves something in-process (a stand-in JWKS server)
> and then runs a child with the blocking `std::process::Command::output()` starves that server: the child's request timed out ("signing keys unavailable"). Use `#[tokio::test(flavor = "multi_thread",
> worker_threads = 2)]` or `tokio::process`.
