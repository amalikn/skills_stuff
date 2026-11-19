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
> Falsifier: clippy accepting `Result<T, axum::response::Response>`
> A helper that returns `Result<T, Response>` so handlers can `?` an early refusal trips `clippy::result_large_err` (Response is at least 128 bytes). Never silence it: when the
> success value carries nothing, return `Option<Response>` (`Some` = refuse); otherwise box the error (`Result<T, Box<Response>>`).
>
> ```rust
> async fn refusal(pool: &PgPool, a: &Artefacts, edge: &Edge, peer: Option<SocketAddr>, h: &HeaderMap, capsule: &str) -> Option<Response> { /* Some(problem(..)) to refuse */ }
> if let Some(r) = refusal(&pool, &a, &edge, peer, &h, &capsule).await { return r; }
> ```

> **Learned 2026-11-19** · workspace lints and tests · VERIFIED_PRIMARY (clippy `unwrap_used` denied in a test module) · Source: continuum-app `crates/continuum-store/src/artefacts.rs` tests ·
> Falsifier: a workspace whose `[lints]` excludes test code
> Workspace `[lints]` (here `unwrap_used = "deny"`) apply to `#[cfg(test)]` modules too. Write tests that return `Result` and use `?`; match error variants with `matches!` rather than
> `unwrap_err()`.
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
