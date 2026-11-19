---
Title: rust override - learned crates
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/rust.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned crates part of the rust override; the entry file holds the tools and the core rule mapping.
---

# rust: learned crates

Part of [rust.md](../rust.md).

> **Learned 2026-11-19** · sqlx 0.9 dynamic SQL; temporalio 1.2 macros; per-test databases · VERIFIED_PRIMARY (compiler and test runs) · Source: continuum-app
> `crates/continuum-store/src/testdb.rs`, `apps/coordinator/src/workflow.rs` (tools_stuff/continuum-app 9e22774) · Falsifier: a later sqlx accepting a `&str` built at run time. sqlx 0.9 `execute`
> wants a `'static` SQL string; built SQL (a generated database name) goes through `sqlx::raw_sql(sqlx::AssertSqlSafe(format!(...)))`, never with input in it. The temporalio `#[workflow_methods]` and
> `#[activities]` macros emit undocumented associated constants, so `missing_docs = deny` fails: allow it for that module with a comment. Give each database test its own database and drop it at the
> end (`DROP DATABASE ... WITH (FORCE)` after closing the pool); otherwise every run leaves databases behind.

> **Learned 2026-11-19** · sqlx `migrate!` and new migration files · VERIFIED_PRIMARY (test run: "relation device does not exist") · Source: continuum-app
> `crates/continuum-store/build.rs` (9322816) · Falsifier: a sqlx release whose `migrate!` macro tracks the folder itself. `sqlx::migrate!("../../migrations")` embeds the folder at compile time, and
> cargo does not rebuild the crate when a file is added there: the binary silently lacked the new migration. Give the crate a `build.rs` with `cargo:rerun-if-changed` on the folder (what `sqlx migrate
> build-script` writes).
>
> ```rust
> fn main() {
>   println!("cargo:rerun-if-changed=../../migrations");
> }
> ```

> **Learned 2026-11-19** · jsonwebtoken 12 defaults · VERIFIED_PRIMARY (crate docs, test) · Source: continuum-app `apps/coordinator/src/identity.rs` (555a276) · Falsifier: a
> release with zero default leeway. `Validation` defaults to 60 s of leeway, so a token replayed up to a minute after `exp` still passes (a replay test with a 60 s leeway fails); set `leeway = 0`
> where replay matters. The upstream example builds `Validation::new(header.alg)` from the token's own header: that lets the token pick its algorithm (HS256 signed with the public key). Pin it.
>
> ```rust
> let mut v = Validation::new(Algorithm::RS256); // never header.alg
> v.leeway = 0;
> ```

> **Learned 2026-11-19** · axum 0.8 request body limit · VERIFIED_PRIMARY (axum-core source `DEFAULT_LIMIT: usize = 2_097_152`; docs.rs `DefaultBodyLimit`) · Source: continuum-app
> `apps/coordinator/src/lib.rs` artefact routes (TASK-216) · Falsifier: a `Bytes` extractor accepting a body over 2 MiB without a layer
> Every body extractor (`Bytes`, `String`, `Json`, `Form`) stops at 2 MiB by default, so an upload route needs its own limit, set on that route only, never `disable()` for
> untrusted callers. Docs: https://docs.rs/axum/latest/axum/extract/struct.DefaultBodyLimit.html
>
> ```rust
> d = d.route("/v1/capsules/{capsule_id}/artefacts/{digest}", axum::routing::put(artefact::put).get(artefact::get))
>   .layer(axum::extract::DefaultBodyLimit::max(artefact::MAX_BODY_BYTES)) // 256 MiB, this route only
>   .layer(axum::Extension(a));
> ```

> **Learned 2026-11-19** · axum handlers and std::fs · VERIFIED_PRIMARY (code review against tokio docs) · Source: continuum-app `apps/coordinator/src/artefact.rs` · Falsifier: none, a rule
> A handler that reads or writes files with `std::fs` blocks a runtime worker for the whole call. Move the blocking store call into `tokio::task::spawn_blocking`, clone what it
> needs into the closure, and map a `JoinError` to a 500 like any store error.
>
> ```rust
> let store = Store::new(a.root.join(&capsule));
> match tokio::task::spawn_blocking(move || store.put(&d, &body)).await {
>   Ok(Ok(put)) => { /* 201 or 200 */ }
>   Ok(Err(e)) => store_problem(&e),
>   Err(e) => problem(StatusCode::INTERNAL_SERVER_ERROR, "store_error", e.to_string()),
> }
> ```
