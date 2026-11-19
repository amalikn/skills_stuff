---
Title: Rust override
Category: reference
Status: current
Authority: local-supplement
Scope: Rust crates, libraries and binaries
Last reviewed: 2026-11-19
Summary: >-
  Rust API Guidelines; rustfmt via cargo fmt and Clippy; doc comments with Errors, Panics and Safety sections and examples;
  Result for recoverable errors and the question-mark operator; meaningful error types; cargo test including doc tests;
  Cargo feature unification (rustls providers), sqlx 0.9 and per-test databases, migration build scripts, tokio test
  threads, jsonwebtoken leeway and algorithm, Unix socket path length.
---

# Rust override

## Contents

- [Authoritative sources](#authoritative-sources)
- [Tools](#tools)
- [Core rule mapping](#core-rule-mapping)
- [Size and limit tweaks](#size-and-limit-tweaks)
- [Feature unification](#feature-unification)
- [Tests, build scripts and limits](#tests-build-scripts-and-limits)
- [Open items](#open-items)

## Authoritative sources

The Rust API Guidelines (checklist and documentation chapter), The Rust Programming Language chapter 9 (error handling), Clippy documentation, the rustfmt README, `cargo test` documentation. Copies:
`../documents/research-sources-20261019/`.

## Tools

| Job       | Tool                                                        | Note                                               |
| --------- | ----------------------------------------------------------- | -------------------------------------------------- |
| Toolchain | `rust-toolchain.toml`, `rust-version` in `Cargo.toml`       | The project's pin                                  |
| Format    | `cargo fmt` (rustfmt)                                       | VERIFIED_PRIMARY                                   |
| Lint      | `cargo clippy`; deny warnings in CI where the project does  | Clippy groups lints by category (VERIFIED_PRIMARY) |
| Tests     | `cargo test` runs unit, integration and documentation tests | VERIFIED_PRIMARY                                   |

## Core rule mapping

| Core reference               | In Rust                                                                                                                                                               |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| documentation-and-headers    | `//!` crate and module docs; `///` on public items with examples (C-EXAMPLE); "Errors", "Panics" and "Safety" sections where they apply (C-FAILURE, VERIFIED_PRIMARY) |
| errors-and-timeouts          | `Result<T, E>` for recoverable errors, `panic!` for unrecoverable bugs (The Book, VERIFIED_PRIMARY); error types are meaningful and implement `std::error::Error`     |
|                              |   (C-GOOD-ERR); examples use `?`, not `unwrap` (C-QUESTION-MARK); no `unwrap`/`expect` in library paths that can fail on input                                        |
| design-principles            | Traits at seams; newtypes for units and identifiers; keep `unsafe` in one small module with a Safety comment                                                          |
| security                     | Bound parameters in DB drivers; `std::process::Command` with `.arg()`                                                                                                 |
| testing                      | Unit tests in `#[cfg(test)]` modules; integration tests in `tests/`; doc tests double as examples                                                                     |
| documentation-and-headers    | No item-level `#[allow(clippy::...)]` to pass a check without a comment saying why; prefer crate-level config with a reason                                           |
|   (suppression)              |                                                                                                                                                                       |

## Size and limit tweaks

| Item                | Value                                                                 | Reason             |
| ------------------- | --------------------------------------------------------------------- | ------------------ |
| Module and function | Core defaults                                                         | No change          |
| Line length         | rustfmt's `max_width` (default 100, UNVERIFIED in the fetched README) | Do not hand-format |

## Feature unification

> **Learned 2026-11-19** · Cargo feature unification across dependencies · VERIFIED_PRIMARY (observed: build and `cargo tree`) · Source: Continuum P1 spike
> `spikes/p1-coordinator/rust/Cargo.toml` (tools_stuff 5585b29), jsonschema 0.61.2, reqwest 0.13.5 · Falsifier: the same dependency set starting without the panic. A dependency's default features can
> switch on a feature of a shared crate that your own manifest turned off. Here `jsonschema`'s defaults enabled `reqwest/rustls-no-provider`, so a plain-HTTP client panicked at start ("No rustls
> crypto provider is configured") although the build was green. Before trusting a `default-features = false` line, run `cargo tree -i <crate> -e features` to see who enables what, then either enable a
> provider feature or turn off the dependency's defaults. Test by starting the binary, not only by building.
>
> ```toml
> reqwest = { version = "0.13.5", default-features = false, features = ["json", "rustls"] }  # "rustls" brings the provider jsonschema's defaults assumed
> ```

> **Learned 2026-11-19 (recurred)** · Feature unification inside one workspace · VERIFIED_PRIMARY (test run) · Source: continuum-app `apps/agent/Cargo.toml` (b25dbf8) · Falsifier: a workspace build
> where one member's `rustls-no-provider` leaves another member's clients working without installing a provider. The same panic came back the same day from a different direction: a new workspace
> member (the agent) chose `reqwest/rustls-no-provider` and installed ring itself; in `cargo test --workspace` that feature unified into the coordinator's reqwest, whose clients then panicked in unit
> tests. Rule: in a workspace, never choose `rustls-no-provider` in one member unless every member that builds a reqwest client installs a provider; use `rustls` (provider included). Before adding a
> TLS feature, `rg -n reqwest */*/Cargo.toml` across members.
>
> ```toml
> # apps/agent/Cargo.toml (b25dbf8): `rustls-no-provider` here made the coordinator's clients panic in a workspace build
> reqwest = { version = "0.13.5", default-features = false, features = ["json", "rustls"] }
> ```

> **Learned 2026-11-19** · sqlx 0.9 dynamic SQL; temporalio 1.2 macros; per-test databases · VERIFIED_PRIMARY (compiler and test runs) · Source: continuum-app
> `crates/continuum-store/src/testdb.rs`, `apps/coordinator/src/workflow.rs` (tools_stuff/continuum-app 9e22774) · Falsifier: a later sqlx accepting a `&str` built at run time. sqlx 0.9 `execute`
> wants a `'static` SQL string; built SQL (a generated database name) goes through `sqlx::raw_sql(sqlx::AssertSqlSafe(format!(...)))`, never with input in it. The temporalio `#[workflow_methods]` and
> `#[activities]` macros emit undocumented associated constants, so `missing_docs = deny` fails: allow it for that module with a comment. Give each database test its own database and drop it at the
> end (`DROP DATABASE ... WITH (FORCE)` after closing the pool); otherwise every run leaves databases behind.

## Tests, build scripts and limits

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

> **Learned 2026-11-19** · `#[tokio::test]` and blocking child processes · VERIFIED_PRIMARY (test run) · Source: continuum-app `apps/coordinator/tests/agent_e2e.rs` (b25dbf8)
> · Falsifier: the stand-in server answering while the test thread blocks on `Command::output()`. `#[tokio::test]` runs on one thread. A test that serves something in-process (a stand-in JWKS server)
> and then runs a child with the blocking `std::process::Command::output()` starves that server: the child's request timed out ("signing keys unavailable"). Use `#[tokio::test(flavor = "multi_thread",
> worker_threads = 2)]` or `tokio::process`.

> **Learned 2026-11-19** · jsonwebtoken 12 defaults · VERIFIED_PRIMARY (crate docs, test) · Source: continuum-app `apps/coordinator/src/identity.rs` (555a276) · Falsifier: a
> release with zero default leeway. `Validation` defaults to 60 s of leeway, so a token replayed up to a minute after `exp` still passes (a replay test with a 60 s leeway fails); set `leeway = 0`
> where replay matters. The upstream example builds `Validation::new(header.alg)` from the token's own header: that lets the token pick its algorithm (HS256 signed with the public key). Pin it.
>
> ```rust
> let mut v = Validation::new(Algorithm::RS256); // never header.alg
> v.leeway = 0;
> ```

> **Learned 2026-11-19** · Unix socket path length · VERIFIED_PRIMARY (macOS error "path must be shorter than SUN_LEN") · Source: continuum-app
> `crates/continuum-adapter-host/src/lib.rs` (182e164) · Falsifier: none expected; sockaddr_un is fixed. A Unix socket path must fit sockaddr_un: 104 bytes on macOS, 108 on Linux. macOS temp folders
> (`/var/folders/...`) plus a UUID exceed it. Check the length before binding and fail with a clear message; tests use a short folder such as `/tmp/<prefix>-<12 hex>`.

## Open items

- Async runtime and timeout patterns (for example `tokio::time::timeout`): UNVERIFIED stub.
