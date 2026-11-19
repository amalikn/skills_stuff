---
Title: Rust for this operator, part 1 - the language, from real code
Category: reference
Status: current
Authority: local-supplement
Scope: Human-readable Rust guide for the operator, parts 0 to 6 (cargo, ownership, enums, errors, structs and traits, modules), built from continuum-app's code
Last reviewed: 2026-11-19
Summary: >-
  Learn Rust from code you already run: each part explains one concept with an excerpt from continuum-app (path given), what to notice, and the official chapter to read next. Part 2 covers async,
  axum, sqlx, processes, tests and tooling.
---

# Rust, from the code you already run (part 1 of 2)

Written for: you, learning Rust, with Python, shell and Ansible behind you. Every example below is real code from `continuum-app` (paths are relative to that repository), so you can open the file and
see it in context. Rules for agents live in [../rust.md](../rust.md) and the `learned-*.md` files beside this one; this file is for reading.

Part 2, services, tests and tooling: [guide-services.md](guide-services.md).

## Contents

- [0. How to learn with this guide](#0-how-to-learn-with-this-guide)
- [1. Cargo, crates and the workspace](#1-cargo-crates-and-the-workspace)
- [2. Ownership and borrowing: String versus &str](#2-ownership-and-borrowing-string-versus-str)
- [3. Enums and match](#3-enums-and-match)
- [4. Errors: Result, Option and the question mark](#4-errors-result-option-and-the-question-mark)
- [5. Structs, impl blocks, derive and traits](#5-structs-impl-blocks-derive-and-traits)
- [6. Modules and visibility](#6-modules-and-visibility)

## 0. How to learn with this guide

1. Read [The Rust Programming Language](https://doc.rust-lang.org/book/) ("the Book"), chapters 1 to 11. They cover everything in parts 1 to 6 and 11 here.
2. Do [Rustlings](https://rust-lang.github.io/rustlings/) alongside: small exercises that fail until you fix them, the fastest way to make ownership stick.
3. Then the [tokio tutorial](https://tokio.rs/tokio/tutorial) for part 7, and [axum's docs](https://docs.rs/axum/latest/axum/) for part 8.
4. Open the file each excerpt names and read the code around it. Change something, run `just test`, and read what the compiler says: Rust's error messages usually tell you the fix.

## 1. Cargo, crates and the workspace

A **crate** is one library or program; **Cargo** builds, tests and fetches dependencies (Python's pip, venv and pytest in one tool). A **workspace** is several crates built together with one lock
file. continuum-app is a workspace: `apps/coordinator` (the API server), `apps/agent` (the endpoint program), and `crates/*` (shared libraries such as `continuum-store`).

```toml
# apps/agent/Cargo.toml (dependencies, trimmed)
[dependencies]
reqwest = { version = "0.13.5", default-features = false, features = ["json", "rustls"] }
serde_json = "1.0.154"
sha2 = "0.10"
tokio = { version = "1.54.1", features = ["macros", "rt-multi-thread", "time", "fs"] }
```

What to notice: **features** switch optional parts of a crate on. In a workspace, features unify: if two crates use reqwest with different features, both get the union (see
`learned-cargo-and-builds.md` for the bug this caused). Always build through `just` here, because the justfile sets `CARGO_TARGET_DIR` to the working cache; a bare `cargo build` makes a stray
`./target`.

Read next: [Cargo workspaces](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html), [The Cargo Book](https://doc.rust-lang.org/cargo/).

## 2. Ownership and borrowing: String versus &str

Every value has one owner; when the owner goes out of scope the value is freed. You can lend it out as a **reference** (`&`) without giving it away. `String` is an owned, growable string; `&str` is a
borrowed view of one. Most functions take `&str` (they only look) and return `String` when they make something new.

```rust
// crates/continuum-store/src/artefacts.rs
pub fn digest_of(bytes: &[u8]) -> String {            // borrows the bytes, returns a new owned String
  format!("sha256:{:x}", Sha256::digest(bytes))
}

fn hex_of(digest: &str) -> Result<&str, Error> {      // returns a view INTO the caller's string
  let hex = digest.strip_prefix("sha256:").ok_or(Error::BadDigest)?;
  // ...
}
```

What to notice: `hex_of` returns `&str` that points inside `digest`, so the compiler makes sure `digest` outlives the result (that is what lifetimes check; here it infers them for you). `&[u8]` is a
borrowed slice of bytes, like a read-only memoryview in Python. When you see `.clone()` in this code, it makes an owned copy so two places can each own one (for example the store handed to a
background thread in part 7).

Read next: [What is ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html), then chapters 4.2 and 4.3.

## 3. Enums and match

A Rust **enum** is a type that is exactly one of several variants, and a variant can carry data. `match` must handle every variant, so the compiler tells you when you forget a case: this is the
feature that replaces most `if/elif` chains and sentinel values.

```rust
// crates/continuum-store/src/artefacts.rs
pub enum Error {
  BadDigest,
  Mismatch { actual: String },   // a variant with a named field
  NotFound,
  Corrupt,
  Io(std::io::Error),            // a variant wrapping another error
}

// apps/coordinator/src/artefact.rs: every store error becomes one HTTP answer
match e {
  StoreError::BadDigest => problem(StatusCode::BAD_REQUEST, "schema_invalid", e.to_string()),
  StoreError::Mismatch { .. } => problem(StatusCode::UNPROCESSABLE_ENTITY, "digest_mismatch", e.to_string()),
  StoreError::NotFound => problem(StatusCode::NOT_FOUND, "not_found", e.to_string()),
  StoreError::Corrupt | StoreError::Io(_) => problem(StatusCode::INTERNAL_SERVER_ERROR, "store_error", e.to_string()),
}
```

What to notice: `{ .. }` ignores the fields, `_` ignores a value, `|` joins two variants in one arm. Add a sixth variant and this `match` stops compiling until you decide what it means.

Read next: [Enums and pattern matching](https://doc.rust-lang.org/book/ch06-00-enums.html).

## 4. Errors: Result, Option and the question mark

Rust has no exceptions. A function that can fail returns `Result<T, E>`: `Ok(value)` or `Err(error)`. A value that may be absent is `Option<T>`: `Some(value)` or `None`. The `?` operator means "if
this is an error, return it from my function now; otherwise give me the value", which is most of what `try/except: raise` does in Python, but visible at every call.

```rust
// apps/agent/src/bundle.rs
pub fn capture(repo: &Path, out: &Path) -> Result<String, Error> {
  git(&["-C", s(repo)?, "bundle", "create", s(out)?, "--all"])?;   // any failure returns early
  git(&["-C", s(repo)?, "bundle", "verify", s(out)?])?;
  file_digest(out)                                                  // last expression = the return value
}
```

```rust
// apps/coordinator/src/artefact.rs: Option used as "a refusal, or nothing"
async fn refusal(/* ... */) -> Option<Response> { /* Some(problem(..)) means refuse */ }

if let Some(r) = refusal(&pool, &a, &edge, peer, &h, &capsule).await {
  return r;     // refused: send that answer
}               // None: carry on
```

What to notice: no semicolon on the last line means "return this". `if let Some(x) = ...` runs only when there is a value. `.ok_or(Error::BadDigest)?` turns an `Option` into a `Result` and returns on
`None`. Never use `.unwrap()` in this project: it panics (crashes) on `Err`/`None`, and the lints forbid it.

Read next: [Recoverable errors with Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html).

## 5. Structs, impl blocks, derive and traits

A **struct** groups named fields (a Python dataclass without methods). Methods go in an `impl` block. A **trait** is a set of methods a type promises to have (like a Python protocol or abstract base
class). `#[derive(...)]` asks the compiler to write common trait implementations for you.

```rust
// crates/continuum-store/src/artefacts.rs
#[derive(Debug, Clone)]
pub struct Store {
  root: PathBuf,                 // private field: only this module can touch it
}

impl Store {
  pub fn new(root: impl Into<PathBuf>) -> Self {   // accepts &str, String, PathBuf...
    Self { root: root.into() }
  }
  pub fn put(&self, digest: &str, bytes: &[u8]) -> Result<Put, Error> { /* ... */ }
}

impl From<std::io::Error> for Error {              // lets `?` turn an io::Error into our Error
  fn from(e: std::io::Error) -> Self { Self::Io(e) }
}
```

What to notice: `&self` is Python's `self`, borrowed. `Debug` gives `{:?}` printing, `Clone` gives `.clone()`. `derive(Debug)` only works when every field implements `Debug` too (the artefact routes'
struct could not derive it because the OpenFGA client does not). `impl Into<PathBuf>` means "any type that can become a PathBuf".

Read next: [Traits](https://doc.rust-lang.org/book/ch10-02-traits.html).

## 6. Modules and visibility

Each file is a module. `mod bundle;` in `main.rs` pulls in `bundle.rs`. Everything is private unless marked `pub`; `pub(crate)` means visible anywhere in this crate but not outside it.

```rust
// apps/agent/src/main.rs
mod bundle;                                   // the file apps/agent/src/bundle.rs

// apps/coordinator/src/heartbeat.rs
pub(crate) fn normalise(fp: &str) -> Option<String> { /* shared with artefact.rs, not exported */ }
```

What to notice: `use crate::heartbeat::normalise;` imports by path from the crate root, like a Python absolute import.

Continue with [part 2: services, tests and tooling](guide-services.md).
