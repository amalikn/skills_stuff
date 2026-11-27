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
- [Topic files](#topic-files)

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

| Item                | Value                                                                | Reason                                                                                                  |
| ------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Module and function | Core defaults                                                        | No change                                                                                               |
| Line length         | rustfmt's `max_width` (default 100, UNVERIFIED in the                | Do not hand-format                                                                                      |
|                     |   fetched README)                                                    |                                                                                                         |
| Indentation         | rustfmt's default (`tab_spaces`; its value is not in the stored      | Loosens the core two-space rule: the formatter's default wins, no `rustfmt.toml` override (operator,    |
|                     |   README, UNVERIFIED)                                                |   2026-11-19, USER_STATED)                                                                              |

## Learning Rust

A reading guide for the operator, built from continuum-app's real code with links to the official docs: [part 1, the language](rust/guide-basics.md) and [part 2, services and tests](rust/guide-services.md), [part 3, keys and secrets](rust/guide-keys.md) and [part 4, tooling and a Python phrasebook](rust/guide-tooling.md).

Rule (operator, 2026-11-19: "I want to learn that language ... proper documentation there which I can read at any time"): every session that writes Rust adds its lessons to the
`learned-*.md` files and, when a concept is new to the guide, a part with a real excerpt, what to notice and the official chapter to read.

## Topic files

The rest of this override lives in [rust/](rust/) (split 2026-11-19 by scripts/language_split.py: one topic per file).

| File | Blocks |
| --- | --- |
| [learned-async-and-tests.md](rust/learned-async-and-tests.md) | 1 |
| [learned-cargo-and-builds.md](rust/learned-cargo-and-builds.md) | 3 |
| [learned-crates.md](rust/learned-crates.md) | 3 |
| [learned-platform.md](rust/learned-platform.md) | 1 |
| [open-items.md](rust/open-items.md) | 1 |
