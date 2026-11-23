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

> **Learned 2026-11-20** · Temporal Rust SDK 1.2.0 workflows and activities · VERIFIED_PRIMARY (compiler; 10 workflow tests on the dev server) · Source: continuum-app
> `apps/coordinator/src/handoff/{flow,acts}.rs` (fb09703); temporalio-macros 1.2.0 `activities_definitions.rs` · Falsifier: an SDK release whose macros accept `&self`. Activities that need state (a
> database pool) take `self: Arc<Self>` as receiver; the macro rejects `&self` and `self`. In a workflow, `?` converts activity errors but not `serde_json::Error` into `WorkflowTermination`, so parse
> activity answers with `unwrap_or_default()` and treat `Null` as "not ok". Keep business outcomes as data (`{"ok": false, "why": ...}`) and raise only on infrastructure errors, so Temporal's default
> retry rides out a database restart without retrying a refusal. Read the clock with `ctx.workflow_time()` (replay-safe) and loop short activities toward a deadline instead of one long-running
> activity.
>
> ```rust
> #[activity]
> pub async fn wait_result(self: Arc<Self>, _ctx: ActivityContext, input: String) -> Result<String, ActivityError> {
>   let i: Value = serde_json::from_str(&input)?;
>   match orders::result_of(&self.pool, s(&i, "order_id")).await {
>     Ok(Some(r)) => answer(Ok(r)),             // data
>     Err(store::StoreError::Db(e)) => Err(e.into()), // infrastructure: Temporal retries
>     ...
> ```

> **Learned 2026-11-20** · clippy `result_large_err` on axum handlers · VERIFIED_PRIMARY (clippy, rust 1.100.0) · Source: continuum-app `apps/coordinator/src/handoff/mod.rs`
> (fb09703) · Falsifier: an axum `Response` under clippy's 128-byte threshold. A helper returning `Result<T, axum::response::Response>` trips `result_large_err` (the response is at least 128 bytes).
> Return `Result<T, Box<Response>>`, build errors with a small `refuse(status, code, detail) -> Box<Response>` helper, and unbox at the handler with `return *r`.

> **Learned 2026-11-22** · throwaway test databases that leak · VERIFIED_PRIMARY (765 leaked databases, 6.2 GB, filled a Docker VM; after the fix `just test` 122 pass, 0 left) ·
> Source: continuum-app `crates/continuum-store/src/testdb.rs` (8d528a2) · Falsifier: a runner that aborts test threads without unwinding (Drop never runs). A per-test database dropped only by an
> explicit `finish().await` leaks whenever a test returns early, fails or never calls it (a shared kit that forgot it leaked one per test for weeks). Drop it on `Drop` too, from a thread with its own
> runtime because `Drop` cannot await, and keep it only when the thread is panicking (a failed assertion, kept for inspection). Pair it with a sweep that matches only the generated name pattern
> (`t_<32 hex>`).
>
> ```rust
> impl Drop for TestDb {
>   fn drop(&mut self) {
>     if self.dropped || std::thread::panicking() { return; }
>     let (url, name) = (self.admin_url.clone(), self.name.clone());
>     let _ = std::thread::spawn(move || {
>       let Ok(rt) = tokio::runtime::Builder::new_current_thread().enable_all().build() else { return };
>       rt.block_on(async { /* connect to url; drop the database `name` WITH (FORCE) */ });
>     }).join();
>   }
> }
> ```

> **Learned 2026-11-22** · testing code that reads an environment variable (edition 2024) · VERIFIED_PRIMARY (test passes) · Source: continuum-app `apps/cli/src/keystore.rs`
> `mirror_to` (00c1f1f) · Falsifier: none. `std::env::set_var` is `unsafe` in edition 2024 and races between parallel tests. Keep the env read in a thin wrapper and test an inner
> function that takes the value: `fn mirror(r, t) { mirror_to(mirror_dir().as_deref(), r, t); }`, then `assert!(!mirror_to(Some(&absent), ..))` and `mirror_to(None, ..)`.

> **Learned 2026-11-22** · `?` from `Box<dyn Error + Send + Sync>` into `Box<dyn Error>` · VERIFIED_PRIMARY (E0277 "`dyn Error + Send + Sync: Sized` is not satisfied") ·
> Source: continuum-app `apps/coordinator/tests/handoff_kit/mod.rs` (cbffb5a) · Falsifier: a std release with that conversion. A test helper returning `Box<dyn Error>`
> cannot `?` a library error typed `Box<dyn Error + Send + Sync>`; convert through a string (`.map_err(|e| e.to_string())?`) or make the helper's error type
> `Send + Sync` too. Related: clippy's `large_enum_variant` fired when one field grew a struct; box that field (`Box<Restic>`) rather than allow the lint.

> **Learned 2026-11-23** · tokio task_local for a value every request in one operation must carry · VERIFIED_PRIMARY (cargo build, artefact tests 9/9) · Source: continuum-app
> `apps/agent/src/transfer.rs`, `steps.rs` (TASK-492) · Falsifier: a nested spawn inside the scope losing the value (task_local does not cross `tokio::spawn`). To add a header
> to every upload of one capture without threading a parameter through five call sites, declare `tokio::task_local! { pub static CAPTURE: String; }`, wrap the operation in
> `CAPTURE.scope(id, fut).await`, and read it where the request is built with `CAPTURE.try_with(Clone::clone).unwrap_or_default()` (outside a scope: empty, the server ignores it).

