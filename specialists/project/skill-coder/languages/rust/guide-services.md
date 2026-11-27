---
Title: Rust for this operator, part 2 - services, tests and tooling, from real code
Category: reference
Status: current
Authority: local-supplement
Scope: Human-readable Rust guide for the operator, parts 7 to 11 (tokio, axum, sqlx, processes, tests), built from continuum-app's code
Last reviewed: 2026-11-27
Summary: >-
  The second half of the operator's Rust guide: async with tokio, a web API with axum, a database with sqlx, running programs with a timeout, tests, the lints met in this project, and a
  Python to Rust phrasebook. Start with part 1 (guide-basics.md).
---

# Rust, from the code you already run (part 2 of 4)

Written for: you, learning Rust. Part 1 (cargo, ownership, enums, errors, structs, modules) is [guide-basics.md](guide-basics.md); read it first.

## Contents

- [7. Async with tokio](#7-async-with-tokio)
- [8. A web API with axum](#8-a-web-api-with-axum)
- [Calling other services: one client per trust rule](#calling-other-services-one-client-per-trust-rule)
- [9. A database with sqlx](#9-a-database-with-sqlx)
- [10. Running other programs, with a timeout](#10-running-other-programs-with-a-timeout)
- [11. Tests](#11-tests)
- Parts 12 to 14 (fmt and clippy, the Python phrasebook, further reading): [guide-tooling.md](guide-tooling.md)

## 7. Async with tokio

`async fn` returns a task that does nothing until awaited; `.await` waits for it without blocking the thread, so one server thread can serve many slow network calls. **tokio** is the runtime that runs
those tasks. Ordinary blocking work (file reads, CPU-heavy hashing) must be moved off the async threads with `spawn_blocking`, or it stalls every other request.

```rust
// apps/coordinator/src/artefact.rs
let store = Store::new(a.root.join(&capsule));
match tokio::task::spawn_blocking(move || store.put(&d, &body)).await {
  Ok(Ok(put)) => { /* stored */ }
  Ok(Err(e)) => store_problem(&e),        // the store said no
  Err(e) => problem(/* ... */),           // the background task itself failed
}
```

What to notice: `move ||` is a closure that takes ownership of what it uses (`store`, `d`, `body`), which is why `store` was made just before. The double `Ok(Ok(..))` is a Result inside a
Result: the outer one says whether the task ran, the inner one is the store's answer.

Read next: [tokio tutorial](https://tokio.rs/tokio/tutorial), [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/).

## 8. A web API with axum

An axum **handler** is an `async fn` whose arguments are **extractors**: each one pulls a piece out of the request (path segments, headers, body, shared state). A **router** maps paths and methods to
handlers; **layers** wrap routes with shared behaviour (limits, authentication, injected state).

```rust
// apps/coordinator/src/artefact.rs (trimmed: the edge and peer extractors left out)
pub async fn put(
  State(pool): State<PgPool>,                          // the database pool shared by every request
  Extension(a): Extension<Arc<Artefacts>>,             // the store, OpenFGA and OPA clients
  Path((capsule, digest)): Path<(String, String)>,     // /v1/capsules/{capsule_id}/artefacts/{digest}
  h: HeaderMap,                                        // all headers
  body: Bytes,                                         // the raw body
) -> Response { /* ... */ }

// apps/coordinator/src/lib.rs
d = d.route("/v1/capsules/{capsule_id}/artefacts/{digest}", axum::routing::put(artefact::put).get(artefact::get))
  .layer(axum::extract::DefaultBodyLimit::max(artefact::MAX_BODY_BYTES))   // 256 MiB for this route only
  .layer(axum::Extension(a));
```

What to notice: the argument types are the API: `Path<(String, String)>` both parses and declares the URL shape. `Arc` is a shared, reference-counted pointer, so many requests use one client. Body
extractors stop at 2 MiB unless a route raises the limit.

Read next: [axum docs](https://docs.rs/axum/latest/axum/).

### Calling other services: one client per trust rule

A reqwest `Client` carries its own rule for which certificates it trusts. The agent needs two rules: the coordinator is private (signed by the project's own root, and
only that root may vouch for it), while the sign-in server is public (Let's Encrypt). So it builds two clients instead of loosening one.

```rust
// apps/agent/src/tls.rs (continuum-app b3a3772)
pub fn client(ca: &[u8], identity: Option<&[u8]>) -> Result<reqwest::Client, Error> {
  let mut b = reqwest::Client::builder()
    .timeout(Duration::from_secs(15))
    .tls_certs_only([reqwest::Certificate::from_pem(ca)?]);   // ONLY this root: the pin
  if let Some(id) = identity { b = b.identity(reqwest::Identity::from_pem(id)?); }
  Ok(b.build()?)
}

pub fn keycloak_client(ca: &[u8]) -> Result<reqwest::Client, Error> {
  Ok(reqwest::Client::builder()
    .timeout(Duration::from_secs(15))
    .add_root_certificate(reqwest::Certificate::from_pem(ca)?)  // the system's roots PLUS this one
    .build()?)
}
```

What to notice: the builder pattern: each call returns the builder, `build()` ends it, and `?` turns a bad PEM or a TLS setup error into the function's error.
`Result<reqwest::Client, Error>` with `Ok(...)` around the last expression is how a function that can fail returns its value. Python's `requests` puts the same
choice in `verify=` (a path replaces the trusted set, like `tls_certs_only`), which is why "just point it at a bigger bundle" is the tempting and wrong fix here.

Read next: [reqwest ClientBuilder](https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html).

## 9. A database with sqlx

sqlx sends SQL you write yourself (no ORM) with `$1`-style parameters, and embeds the migration files into the binary.

```rust
// apps/coordinator/src/artefact.rs
let device = sqlx::query("SELECT owner_subject, revoked_at IS NOT NULL FROM device WHERE cert_sha256 = $1")
  .bind(&fp)                       // never format values into SQL: bind them
  .fetch_optional(pool)            // Ok(None) when no row matches
  .await;
```

What to notice: `fetch_optional` returns `Result<Option<Row>>`: the Result is "did the query run", the Option is "was there a row". `row.get::<String, _>(0)` reads column 0 as a String. Migrations are
plain SQL files in `migrations/` (for example `0004_capsule_creator.sql`).

Read next: [sqlx docs](https://docs.rs/sqlx/latest/sqlx/).

## 10. Running other programs, with a timeout

`std::process::Command` is Python's `subprocess`. The standard library cannot wait with a deadline, so the agent polls and kills a child that runs too long.

```rust
// apps/agent/src/bundle.rs
let mut child = Command::new("git").args(args).stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn()?;
let start = Instant::now();
loop {
  if child.try_wait()?.is_some() { break; }                       // finished
  if start.elapsed() > GIT_TIMEOUT { let _ = child.kill(); let _ = child.wait(); return Err("timed out".into()); }
  std::thread::sleep(Duration::from_millis(20));
}
```

What to notice: `let _ = ...` deliberately ignores a result (killing a process that already exited can fail harmlessly). `.into()` converts the string into the function's error type.

### Cleaning up with Drop

When a value goes out of scope Rust runs its `Drop` implementation, so cleanup can be tied to ownership instead of remembered: the artefact tests start an OPA server and it is
always stopped, even when an assertion fails half-way (Python needs `try/finally` or a context manager for the same).

```rust
// apps/coordinator/tests/artefact.rs
struct OpaServer(Child, String);          // a tuple struct: the process and its URL
impl Drop for OpaServer {
  fn drop(&mut self) {
    let _ = self.0.kill();                // runs automatically when the test ends, pass or fail
    let _ = self.0.wait();
  }
}
```

Read next: [Running code on cleanup with Drop](https://doc.rust-lang.org/book/ch15-03-drop.html).

## 11. Tests

Unit tests sit in a `#[cfg(test)] mod tests` block at the bottom of the file they test; integration tests are files in `tests/`. A test that returns `Result` can use `?`.

```rust
// apps/agent/src/bundle.rs
#[test]
fn a_bundle_with_the_wrong_digest_is_refused_before_cloning() -> R {
  let (r, _) = repo()?;
  let b = tmp("y.bundle");
  capture(&r, &b)?;
  let into = tmp("never");
  let wrong = format!("sha256:{}", "0".repeat(64));
  assert!(restore(&b, &wrong, &into).is_err());
  assert!(!into.exists());       // and nothing was cloned
  Ok(())
}
```

What to notice: test names are sentences. `#[ignore]` marks tests that need live services (Keycloak, the TLS edge); `just test-keycloak` and `just test-e2e` run them with `--ignored`. Run one test
with `cargo test -p continuum-agent a_bundle_with` (through `just` or with `CARGO_TARGET_DIR` set).

Read next: [Writing tests](https://doc.rust-lang.org/book/ch11-01-writing-tests.html).
