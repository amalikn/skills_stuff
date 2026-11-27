---
Title: Rust for this operator, part 4 - tooling, a Python phrasebook and further reading
Category: reference
Status: current
Authority: local-supplement
Scope: Human-readable Rust guide for the operator, parts 12 to 14 (fmt and clippy, a Python to Rust phrasebook, further reading), built from continuum-app's code
Last reviewed: 2026-11-27
Summary: The lints met in continuum-app and how to read them, a Python to Rust phrasebook and where to read next. Split from guide-services.md on 2026-11-27.
---

# Rust, from the code you already run (part 4 of 4)

Written for: you, learning Rust. Part 1 is [guide-basics.md](guide-basics.md), part 2 [guide-services.md](guide-services.md), part 3 [guide-keys.md](guide-keys.md).

## 12. fmt, clippy and the messages you will meet

`cargo fmt` formats the code (this repo keeps rustfmt's defaults); `cargo clippy` is the linter, and `just ci` runs it with warnings as errors. Ones met in this project:

| Message                             | What it means                                      | Fix used here                               |
| ----------------------------------- | -------------------------------------------------- | ------------------------------------------- |
| `unwrap_used`                       | `.unwrap()` would crash on an error                | `?` and a Result-returning function or test |
| `result_large_err`                  | the error type is big (an axum `Response`)         | return `Option<Response>`, or box the error |
| `E0277 ... doesn't implement Debug` | `derive(Debug)` on a struct with a non-Debug field | drop the derive, or implement Debug by hand |
| `E0063 missing field`               | a struct literal lacks a newly added field         | add it at every place the struct is built   |

Read next: [the clippy lint list](https://rust-lang.github.io/rust-clippy/).

## 13. Python to Rust phrasebook

| Python                         | Rust                                             |
| ------------------------------ | ------------------------------------------------ |
| `None`                         | `Option::None` (and `Some(x)` for a value)       |
| `raise` / `try: except:`       | return `Err(e)` / `?` and `match`                |
| `@dataclass`                   | `struct` with `#[derive(Debug, Clone)]`          |
| `def f(self)`                  | `fn f(&self)` inside `impl`                      |
| `bytes`, `memoryview`          | `Vec<u8>`, `&[u8]`                               |
| `str` (argument)               | `&str`; build new text as `String` (`format!`)   |
| `subprocess.run(..., timeout)` | `Command` plus the poll-and-kill loop (part 10)  |
| `asyncio`                      | tokio (`async fn`, `.await`, `spawn_blocking`)   |
| `pip`, `venv`, `pytest`        | cargo (`cargo add`, `cargo build`, `cargo test`) |
| `ruff format`, `ruff check`    | `cargo fmt`, `cargo clippy`                      |

## 14. Further reading

- [The Rust Programming Language](https://doc.rust-lang.org/book/): the official book, start here.
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/): the same ground as short runnable examples.
- [Rustlings](https://rust-lang.github.io/rustlings/): exercises.
- [The standard library](https://doc.rust-lang.org/std/): search it for any type you meet (`Option`, `Result`, `Path`, `Command`).
- [The Cargo Book](https://doc.rust-lang.org/cargo/), [the tokio tutorial](https://tokio.rs/tokio/tutorial), [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/), [axum](https://docs.rs/axum/latest/axum/), [sqlx](https://docs.rs/sqlx/latest/sqlx/), [clippy lints](https://rust-lang.github.io/rust-clippy/).

Continue with [part 3: keys and secrets](guide-keys.md).

All links checked 2026-11-19 (HTTP 200). New Rust learned in any project goes into the `learned-*.md` files; when it teaches a concept worth reading, a part here gains an excerpt too.
