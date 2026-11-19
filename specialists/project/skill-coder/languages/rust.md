---
Title: Rust override
Category: reference
Status: current
Authority: local-supplement
Scope: Rust crates, libraries and binaries
Last reviewed: 2026-10-19
Summary: >-
  Rust API Guidelines; rustfmt via cargo fmt and Clippy; doc comments with Errors, Panics and Safety sections and examples;
  Result for recoverable errors and the question-mark operator; meaningful error types; cargo test including doc tests.
---

# Rust override

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
> `spikes/p1-coordinator/rust/Cargo.toml` (tools_stuff 5585b29), jsonschema 0.61.2, reqwest 0.13.5 · Falsifier: the same dependency set starting without the panic.
> A dependency's default features can switch on a feature of a shared crate that your own manifest turned off. Here `jsonschema`'s defaults enabled `reqwest/rustls-no-provider`, so a
> plain-HTTP client panicked at start ("No rustls crypto provider is configured") although the build was green. Before trusting a `default-features = false` line, run
> `cargo tree -i <crate> -e features` to see who enables what, then either enable a provider feature or turn off the dependency's defaults. Test by starting the binary, not only by building.
>
> ```toml
> reqwest = { version = "0.13.5", default-features = false, features = ["json", "rustls"] }  # "rustls" brings the provider jsonschema's defaults assumed
> ```

> **Learned 2026-11-19** · sqlx 0.9 dynamic SQL; temporalio 1.2 macros; per-test databases · VERIFIED_PRIMARY (compiler and test runs) · Source: continuum-app
> `crates/continuum-store/src/testdb.rs`, `apps/coordinator/src/workflow.rs` (tools_stuff/continuum-app 9e22774) · Falsifier: a later sqlx accepting a `&str` built at run time.
> sqlx 0.9 `execute` wants a `'static` SQL string; built SQL (a generated database name) goes through `sqlx::raw_sql(sqlx::AssertSqlSafe(format!(...)))`, never with input in it.
> The temporalio `#[workflow_methods]` and `#[activities]` macros emit undocumented associated constants, so `missing_docs = deny` fails: allow it for that module with a comment.
> Give each database test its own database and drop it at the end (`DROP DATABASE ... WITH (FORCE)` after closing the pool); otherwise every run leaves databases behind.

## Open items

- Async runtime and timeout patterns (for example `tokio::time::timeout`): UNVERIFIED stub.
