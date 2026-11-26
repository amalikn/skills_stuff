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

> **Learned 2026-11-21** · age 0.12.1 tag recipients and plugins · VERIFIED_PRIMARY (crate source, tests) · Source: continuum-app `apps/agent/src/device_key.rs` (d1b08b0); age-0.12.1
> `src/native/tag.rs`, `src/plugin.rs` · Falsifier: an age 0.12 build that cannot encrypt to an `age1tag1` recipient without a plugin binary.
> - age 0.12 encrypts to P-256 tag recipients (`age1tag1...`, `age::tag::Recipient`) natively, so devices without the Secure Enclave plugin can seal to a Mac's enclave key; only
>   decryption needs the plugin (`age::plugin::IdentityPluginV1`, feature `plugin`), which finds `age-plugin-<name>` on `$PATH` and needs an `age::Callbacks` impl.
> - The project forbids `unsafe`, and in edition 2024 `std::env::set_var` is unsafe, so the agent cannot add the plugin folder to its own PATH: the launcher sets PATH.
> - A README's example recipient may not be a real one: age-plugin-se's examples fail the Bech32 checksum. Make test vectors from a known point (the P-256 generator) instead.
>
> ```rust
> if recipient.starts_with("age1tag1") {
>   let r = age::tag::Recipient::from_str(recipient).map_err(|e| format!("not an age tag recipient: {e}"))?;
>   return Ok(age::encrypt_and_armor(&r, secret.to_string().expose_secret().as_bytes())?);
> }
> ```

> **Learned 2026-11-22** · sqlx refuses a query string built with `format!` · VERIFIED_PRIMARY (compile error E0277 "dynamic SQL strings should be audited for possible
> injections") · Source: continuum-app `apps/coordinator/tests/portal/actions.rs` (909c00e) · Falsifier: a sqlx version that accepts `&String` from `format!` in `query`.
> `sqlx::query(&format!(...))` does not compile in this sqlx version, even in tests; keep the SQL literal and bind the value:

```rust
sqlx::query("INSERT INTO user_key (owner_subject, generation, recipient, created_by_device, created_at) VALUES ('alice', 1, $1, 'mac-1', now())")
  .bind(format!("age1{}", "q".repeat(58)))
  .execute(&pool)
  .await?;
```

> **Learned 2026-11-22** · calling one axum handler from another · VERIFIED_PRIMARY (tests run) · Source: continuum-app `apps/coordinator/src/portal/actions.rs` `launch` (909c00e) ·
> Falsifier: none expected; handlers are plain async functions. To reuse an API handler's whole logic (checks, transaction, workflow start) from a form handler, build its
> extractors yourself and call it, then read the `Response`: `axum::body::to_bytes(resp.into_body(), limit)` gives the JSON body. One code path, no copy of the rules.

```rust
let actor = Actor { subject: s.subject.clone(), acr: None, auth_time: Some(s.auth_time) };
let resp = crate::handoff::start(State(pool.clone()), Extension(actor), Extension(rt), Path(capsule.to_string()), headers, axum::Json(plan)).await;
let body: Value = serde_json::from_slice(&axum::body::to_bytes(resp.into_body(), 1 << 20).await?)?;
```


> **Learned 2026-11-22** · age + zstd as one streaming pass · VERIFIED_PRIMARY (unit test both directions; P4 gate 13/13) · Source: continuum-app `apps/agent/src/stream.rs` `encrypt_file`
> (82fffef) · Falsifier: an age release whose `StreamWriter::finish` no longer returns the inner writer. Compress-then-encrypt a file of any size without holding it in memory: stack the
> writers inside out (file ← hashing wrapper ← age `wrap_output` ← zstd `Encoder`), `std::io::copy` into the outermost, then finish from the outside in: `z.finish()?` returns the age
> writer, whose `.finish()?` returns the hashing writer. Forgetting the inner `finish` leaves a truncated, undecryptable file with no error. To read, sniff the magic with
> `BufReader::fill_buf` (no bytes consumed) and wrap `age::Decryptor::new_buffered(..)?.decrypt(ids)` in `zstd::stream::read::Decoder::with_buffer`; cap with `take(MAX + 1)`.

```rust
let enc = age::Encryptor::with_recipients(std::iter::once(recipient as &dyn age::Recipient))?;
let mut sealed = enc.wrap_output(out)?;              // out: BufWriter<File> inside a hashing wrapper
let mut z = zstd::stream::write::Encoder::new(sealed, LEVEL)?;
std::io::copy(&mut input, &mut z)?;
let mut sealed_out = z.finish()?.finish()?;         // zstd, then age: both finishes are needed
```

> **Learned 2026-11-22** · rustic_core 0.14 reads and writes a restic repository · VERIFIED_PRIMARY (spike PASS both ways against restic 0.19.1) · Source: continuum
> `spikes/p5-rustic/src/main.rs` (dfa0d76) · Falsifier: a rustic_core minor release that renames these calls (it is pre-1.0). Open, index, find a snapshot by tag, dump one path:
> `BackendOptions::default().repository(path).to_backends()?`, `Repository::new(&RepositoryOptions::default(), &backends)?.open(&Credentials::Password(pw))?.to_indexed()?`,
> `get_all_snapshots()`, `node_from_snapshot_path("<id>:/<path>", |_| true)`, `repo.dump(&node, &mut w)`. Writing: `PathList::from_string(p)?.sanitize()?`,
> `SnapshotOptions::default().add_tags("k:v")?.to_snapshot()?`, `repo.backup(&BackupOptions::default(), &paths, snap)`. All calls are blocking: use `spawn_blocking` under tokio.
> A small read cost 0.2 ms once open, against about 0.7 s per `restic --no-cache` process (key derivation and index load each time).

> **Learned 2026-11-22** · tar 0.4.46 `HeaderMode::Complete` writes no atime · VERIFIED_PRIMARY (`src/header.rs` `fill_platform_from`: mtime, uid, gid, mode only) · Source: tar
> crate source; used by continuum-app `apps/agent/src/tree/capture.rs` · Falsifier: a tar release that adds atime/ctime to Complete GNU headers. So an unchanged file gives a
> byte-identical header between two captures, which content-defined chunking and dedup depend on. `git archive`, by contrast, stamps every entry with the commit time (use
> `--mtime=<fixed>` when comparing archives of two commits): the first FastCDC run read 90-98 % of a tree as "changed" for a nine-file commit for that reason.

> **Learned 2026-11-22** · fastcdc 3.2.1 (`v2020`) · VERIFIED_PRIMARY (spike) · Source: continuum `spikes/p5-fastcdc/src/main.rs` (c8f4971) · Falsifier: a 4.x API change.
> `fastcdc::v2020::FastCDC::new(&data, min, avg, max)` iterates `Chunk { offset, length, hash }`; min = avg / 4 and max = avg * 4 are the usual ratios. At 16 KiB average a
> 719 MB tar chunked twice in about 4.5 s on one core; 16 KiB sent about half of what 64 KiB did for small edits. Hash chunks with SHA-256 for identity: `hash` is a gear hash.

> **Learned 2026-11-22** · rustic_core 0.14 inside a server · VERIFIED_PRIMARY (live tests on SeaweedFS: rustic and the restic CLI read each other's snapshots) · Source:
> continuum-app `crates/continuum-store/src/restic/rustic.rs` (f04865d) · Falsifier: a rustic_core release that backs up from a reader. `BackupOptions` with stdin
> reads the process's own stdin (useless in a server): write the bytes to a private staged file (0700 folder, 0600 file, removed on drop) and set
> `opts.as_path = Some("/<name>".into())` so the snapshot path matches `restic backup --stdin --stdin-filename <name>`. `BackendOptions` is `#[non_exhaustive]`:
> no struct literal, but its pub fields can be assigned on a `default()` value. S3 is `repository = "opendal:s3"` with options `endpoint`, `bucket`, `root`,
> `access_key_id`, `secret_access_key`, `region`. opendal keeps its own static tokio runtime, and calling it from `tokio::task::spawn_blocking` works (no nested-runtime
> panic). Keep the CLI as a fallback, but test the library path directly: a fallback hides every library failure from end-to-end tests.

```rust
let mut opts = BackupOptions::default();
opts.as_path = Some(PathBuf::from(format!("/{hex}")));
let mut snap = SnapshotOptions::default().add_tags(&format!("{digest},capsule:{capsule}")).map_err(err)?;
snap.host = Some("continuum-coordinator".into());
r.backup(&opts, &PathList::from_string(&staged.to_string_lossy())?.sanitize()?, snap.to_snapshot()?)?;
```

> **Learned 2026-11-24** · PostgreSQL row locks: `FOR UPDATE` deadlocks with FK inserts, `FOR NO KEY UPDATE` does not · VERIFIED_PRIMARY (gate body "deadlock
> detected"; a test that holds the lock and inserts an FK row under `lock_timeout` fails 55P03 on FOR UPDATE and passes on NO KEY UPDATE) · Source: continuum-app
> `apps/coordinator/src/checkpoints/settle.rs`, `tests/handoff/lock_modes.rs` (5e7c46c, BUG-570) · Falsifier: a PostgreSQL release changing the row-lock conflict table.
> Every insert into a table with a foreign key takes `FOR KEY SHARE` on the referenced row, and `FOR UPDATE` conflicts with it. A transaction that locked the parent
> `FOR UPDATE` and then waited on a unique index (another transaction's uncommitted row) deadlocked with that other transaction's FK insert (outbox) waiting on the parent
> lock; Postgres aborted one and the API answered 500 instead of 409. A serialising lock that does not change the key wants `FOR NO KEY UPDATE`: it still excludes another
> `FOR NO KEY UPDATE` / `FOR UPDATE` but lets FK inserts through. Prove the mode with a test that holds the lock and tries an FK insert under `SET LOCAL lock_timeout`.

```rust
// BUG-570: NO KEY UPDATE, not UPDATE: still excludes the other start and a checkpoint record, but no longer blocks an FK insert's FOR KEY SHARE.
sqlx::query("SELECT 1 FROM capsule WHERE capsule_id = $1 FOR NO KEY UPDATE").bind(capsule).execute(&mut **tx).await?;
```

> **Learned 2026-11-24** · sqlx 0.8 refuses `query(&format!(...))` · VERIFIED_PRIMARY (compile error E0277 "dynamic SQL strings should be audited for possible
> injections", `SqlSafeStr` not implemented for `&String`) · Source: continuum-app `apps/coordinator/src/lost.rs` and `tests/handoff/recover.rs` (3f988ff) ·
> Falsifier: an sqlx release relaxing `SqlSafeStr`. Write the SQL as a literal and pass values with `.bind()`, intervals as `make_interval(days => $n)`; a shared
> fragment (a `to_char` timestamp) is repeated in each literal rather than spliced. Tests too: fixtures built with `format!` fail to compile.

> **Learned 2026-11-26** · reqwest 0.13 `tls_certs_only` versus `add_root_certificate` · VERIFIED_PRIMARY (agent enrol against Keycloak behind Let's Encrypt:
> `InvalidCertificate(UnknownIssuer)` with `tls_certs_only([private root])`; a device link came back with `add_root_certificate`) · Source: continuum-app
> `apps/agent/src/tls.rs` `keycloak_client` (b3a3772) · Falsifier: a reqwest release where `add_root_certificate` replaces the platform roots. `tls_certs_only`
> makes the given roots the only trust; `add_root_certificate` adds one to the platform verifier's roots (feature `rustls`). When one program talks to a private
> service and a public identity provider, use two clients: the pinned one for the private service, platform-plus-extra for the provider. Never widen the pinned
> client with a public bundle to make the provider work: the pin is what the device saves and reuses, so it would then trust every public CA for the private
> service. `Certificate::from_pem` also reads only the first certificate of a bundle.
