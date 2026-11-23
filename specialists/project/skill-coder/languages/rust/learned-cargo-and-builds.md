---
Title: rust override - learned cargo and builds
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/rust.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned cargo and builds part of the rust override; the entry file holds the tools and the core rule mapping.
---

# rust: learned cargo and builds

Part of [rust.md](../rust.md).

> **Learned 2026-11-19** · Cargo feature unification across dependencies · VERIFIED_PRIMARY (observed: build and `cargo tree`) · Source: Continuum P1 spike
> `spikes/p1-coordinator/rust/Cargo.toml` (tools_stuff 5585b29), jsonschema 0.61.2, reqwest 0.13.5 · Falsifier: the same dependency set starting without the panic. A dependency's default features can
> switch on a feature of a shared crate that your own manifest turned off. Here `jsonschema`'s defaults enabled `reqwest/rustls-no-provider`, so a plain-HTTP client panicked at start ("No rustls
> crypto provider is configured") although the build was green. Before trusting a `default-features = false` line, run `cargo tree -i <crate> -e features` to see who enables what, then either enable a
> provider feature or turn off the dependency's defaults. Test by starting the binary, not only by building.
>
> ```toml
> reqwest = { version = "0.13.5", default-features = false, features = ["json", "rustls"] }  # "rustls" brings the provider jsonschema's defaults assumed
> ```

> **Learned 2026-11-19** · Feature unification inside one workspace (recurred) · VERIFIED_PRIMARY (test run) · Source: continuum-app `apps/agent/Cargo.toml` (b25dbf8) · Falsifier: a workspace build
> where one member's `rustls-no-provider` leaves another member's clients working without installing a provider. The same panic came back the same day from a different direction: a new workspace
> member (the agent) chose `reqwest/rustls-no-provider` and installed ring itself; in `cargo test --workspace` that feature unified into the coordinator's reqwest, whose clients then panicked in unit
> tests. Rule: in a workspace, never choose `rustls-no-provider` in one member unless every member that builds a reqwest client installs a provider; use `rustls` (provider included). Before adding a
> TLS feature, `rg -n reqwest */*/Cargo.toml` across members.
>
> ```toml
> # apps/agent/Cargo.toml (b25dbf8): `rustls-no-provider` here made the coordinator's clients panic in a workspace build
> reqwest = { version = "0.13.5", default-features = false, features = ["json", "rustls"] }
> ```

> **Learned 2026-11-19** · `cargo clean --target-dir` from a script; build-folder growth · VERIFIED_PRIMARY (cargo 1.100.0 runs) · Source: continuum-app `scripts/target_size_cap.sh` (0aa992a) ·
> Falsifier: `cargo clean --target-dir D` succeeding outside any package, or cleaning a folder with no `CACHEDIR.TAG`
> A Cargo target folder only grows: each build adds artifacts and none are removed (20 GiB after a day of agent builds; 0.9 to 5.7 GiB in two builds after a clean). A script that caps it must pass
> `--manifest-path`: run outside a package, `cargo clean --target-dir D` fails "could not find `Cargo.toml`" (exit 101). Cargo also refuses a folder without `CACHEDIR.TAG` ("cleaning has been aborted
> to prevent accidental deletion of unrelated files"), a free guard against a wrong path; test the clean on a copy that carries the tag.
>
> ```sh
> manifest=$(cd "$(dirname "$0")/.." && pwd)/Cargo.toml
> kib=$(du -sk "$dir" | cut -f1)
> [ "$kib" -gt $((cap * 1048576)) ] || exit 0
> cargo clean --manifest-path "$manifest" --target-dir "$dir"
> ```

> **Learned 2026-11-19** · clippy `result_large_err` on axum helpers · VERIFIED_PRIMARY (clippy 1.100 `-D warnings`) · Source: continuum-app `apps/coordinator/src/artefact.rs` `refusal` (TASK-216) ·
> Falsifier: clippy accepting `Result<T, axum::response::Response>` A helper that returns `Result<T, Response>` so handlers can `?` an early refusal trips `clippy::result_large_err` (Response is at
> least 128 bytes). Never silence it: when the success value carries nothing, return `Option<Response>` (`Some` = refuse); otherwise box the error (`Result<T, Box<Response>>`).
>
> ```rust
> async fn refusal(pool: &PgPool, a: &Artefacts, edge: &Edge, peer: Option<SocketAddr>, h: &HeaderMap, capsule: &str) -> Option<Response> { /* Some(problem(..)) to refuse */ }
> if let Some(r) = refusal(&pool, &a, &edge, peer, &h, &capsule).await { return r; }
> ```

> **Learned 2026-11-19** · workspace lints and tests · VERIFIED_PRIMARY (clippy `unwrap_used` denied in a test module) · Source: continuum-app `crates/continuum-store/src/artefacts.rs` tests ·
> Falsifier: a workspace whose `[lints]` excludes test code Workspace `[lints]` (here `unwrap_used = "deny"`) apply to `#[cfg(test)]` modules too. Write tests that return `Result` and use `?`; match
> error variants with `matches!` rather than `unwrap_err()`.
>
> ```rust
> type R = Result<(), Box<dyn std::error::Error>>;
> #[test]
> fn a_tampered_file_is_refused_on_read() -> R {
>   let s = temp_store(); let d = digest_of(b"good");
>   s.put(&d, b"good")?; fs::write(s.path(hex_of(&d)?), b"evil")?;
>   assert!(matches!(s.get(&d), Err(Error::Corrupt)));
>   Ok(())
> }
> ```

> **Learned 2026-11-22** · a test that compiles only in a workspace build · VERIFIED_PRIMARY (cargo test -p continuum-cli failed: "no testkit in the root", `cargo test --workspace`
> passed) · Source: continuum-app `apps/cli/Cargo.toml` (2b2eb8f) · Falsifier: none expected; Cargo unifies features across a build. A crate's tests that use another crate's feature-gated helpers
> (`test-support`) compile in `cargo test --workspace` because some other crate turned the feature on, then fail alone. Declare the feature in the crate's own dev-dependency (`continuum-coordinator =
> { path = "../coordinator", features = ["test-support"] }`).

> **Learned 2026-11-22** · release size: strip, LTO, codegen-units · VERIFIED_PRIMARY (measured, macOS arm64) · Source: continuum-app `Cargo.toml` [profile.release] (bb17d15) ·
> Falsifier: a crate set where LTO grows the binary. `strip = "symbols"`, `lto = "fat"`, `codegen-units = 1` cut an axum/tokio service 37.4 -> 18.9 MB and a CLI 7.2 -> 4.3 MB; the release build went
> 110 -> 203 s; `lto = "thin"` gave 21.2 / 5.2 MB in 157 s. Keep opt-level 3 where hot paths matter, and unwinding where a panic in one request must not stop a server.

> **Learned 2026-11-22** · one program under two binary names · VERIFIED_PRIMARY (cargo build; `just test` 122 pass) · Source: continuum-app `apps/agent/src/{lib,main,c7m_agent}.rs`,
> `apps/coordinator/src/c7m_coordinator.rs`, `apps/*/Cargo.toml` (db6a16e, dca1a91) · Falsifier: a Cargo release that allows one `path` in several `[[bin]]` without a warning. Two `[[bin]]` entries
> with the same `path` build but warn "found to be present in multiple build targets". Without a warning: move the program into the library (`pub async fn run()`) and make each binary a three-line
> `main` calling it; or, when `main.rs` only uses the library's paths, load it in the second binary with `#[path = "main.rs"] mod entry;` and call `entry::main()` (fails when `main.rs` declares `mod`s
> that use `crate::` paths). Either way add `default-run` to the package: with two binaries `cargo run -p <pkg>` refuses to pick one (a dev recipe broke on it).
>
> ```toml
> [package]
> default-run = "continuum-agent"
> [[bin]]
> name = "continuum-agent"
> path = "src/main.rs"
> [[bin]]
> name = "c7m-agent"
> path = "src/c7m_agent.rs"   # #[tokio::main] async fn main() -> ... { continuum_agent::run().await }
> ```


> **Learned 2026-11-22** · sccache 0.19 on a clean workspace build · VERIFIED_PRIMARY (measured: continuum-app `cargo build --workspace`, Mac arm64) · Source: continuum Pad TASK-380,
> ASK-427 · Falsifier: a build where the warm run is not faster. sccache needs `CARGO_INCREMENTAL=0` (incremental artefacts are not cacheable), so it only pays where the target
> starts empty (CI, gates, after a clean): 70 s plain, 79 s with an empty cache, 25 s warm; the warm run hit every crate it had seen; build scripts and links (224 calls) are never
> cached. Target 3.1 GiB without incremental against 4.5 GiB with it; cache 455 MiB. Keep it out of the edit-build loop.

```bash
CARGO_INCREMENTAL=0 RUSTC_WRAPPER=sccache SCCACHE_DIR=<working-cache>/sccache CARGO_TARGET_DIR=<scratch-target> cargo build --workspace
```

> **Learned 2026-11-22** · cargo-dist 0.34 on a workspace of `publish = false` packages · VERIFIED_PRIMARY (dry run) · Source: continuum `spikes/p5-dist/README.md` (6a5aaa2) ·
> Falsifier: a dist release where `init --target` is honoured. `dist init` finds nothing to release until each package has `[package.metadata.dist] dist = true`; it ignored
> `--target` and wrote its five defaults (edit `targets` in `dist-workspace.toml`); GitHub hosting needs `repository = "..."` in each package; cross targets need rustup
> (mise-managed toolchains are not found); it compiles the whole workspace; binaries are only ad-hoc signed (macOS notarisation is separate). Try it in a throwaway clone:
> `init` edits the root Cargo.toml (`[profile.dist]`).

> **Learned 2026-11-22** · a module over the size limit after a small change · VERIFIED_PRIMARY (code-size gate) · Source: continuum-app `apps/coordinator/src/userkey/rotate.rs`
> `replay`, `approve.rs` `SELF_APPROVAL` (4e18e20) · Falsifier: none. Adding one guard pushed a handler from 58 to 64 lines; rustfmt's line splits did the rest. Extract a
> cohesive step into a helper returning `Option<Response>` (None = carry on) and hoist long message strings to a `const`; never raise the limit for it.

> **Learned 2026-11-22** · key derivation in unoptimised dev builds · VERIFIED_PRIMARY (measured: 4 live store tests 121 s -> 15.9 s) · Source: continuum-app `Cargo.toml`
> `[profile.dev.package.scrypt]` (f04865d) · Falsifier: none. A crate that derives keys with scrypt (rustic_core opening a restic repository) takes tens of seconds per call
> in a debug build. Optimise only the crypto crates in the dev profile (`[profile.dev.package.<name>] opt-level = 3` for scrypt, salsa20, pbkdf2, aes, poly1305, sha2);
> everything else keeps fast debug compiles.

> **Learned 2026-11-22** · sccache beside an incremental dev target · VERIFIED_PRIMARY (measured: gate rebuild 35 s from cache vs 94 s cold) · Source: continuum-app
> `.githooks/pre-push`, `justfile` (144bf3f) · Falsifier: a cargo that caches incremental artefacts. sccache needs `CARGO_INCREMENTAL=0`; running it on the dev target
> makes the push gate and everyday builds rebuild each other's work. Give the gate its own target (`CARGO_TARGET_DIR=<cache>/target-gate`) behind sccache, and let the
> justfile honour an exported target: `export CARGO_TARGET_DIR := env("CARGO_TARGET_DIR", "<default>")`.

> **Learned 2026-11-23** · cargo 1.100 build-dir layout and trimming a target · VERIFIED_PRIMARY (measured on continuum-app targets, Mac arm64) · Source: continuum-app
> `scripts/target_size_cap.py` (TD-412) · Falsifier: a cargo whose fresh build does not read `fingerprint/<kind>-<name>`. The target has no `deps/`: each compilation unit is
> `<profile>/build/<package>/<hash>/` holding `fingerprint/` and `out/` (rlib, rmeta, `.d`, and `*.rcgu.o`, the unpacked macOS debug info, about 30% of the size). Variants pile up
> per package (98 hashes of one workspace crate in a push-gate target), so the "only grows" note above still holds, but a whole unit folder can be removed safely: cargo reads
> each unit's fingerprint on every build, so its access time says when it was last used, and a removed unit is just rebuilt. Lock while trimming: holding any of
> `.cargo-lock`, `.cargo-build-lock`, `.cargo-artifact-lock` in `<profile>/` makes cargo print "Blocking waiting for file lock". Pattern: design-patterns.md P-83.

