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

## Open items

- Async runtime and timeout patterns (for example `tokio::time::timeout`): UNVERIFIED stub.
