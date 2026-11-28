---
Title: skill-coder changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-coder pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Summary: Release history and governance changes of skill-coder; the release heading holds the version of record.
Last rotated: 20261127_1745
---

# Changelog

## Contents

- [Unreleased](#unreleased)
- [20261124_2216 — P-87 merge by unpacking beside the live copy](#20261124_2216--p-87-merge-by-unpacking-beside-the-live-copy)
- [20261124_2215 — Rust guide: names from outside become paths; justfile exports and bare cargo test](#20261124_2215--rust-guide-names-from-outside-become-paths-justfile-exports-and-bare-cargo-test)
- [20261124_1948 — Write-backs from continuum 2026-11-24 evening](#20261124_1948--write-backs-from-continuum-2026-11-24-evening)
- [20261122_2341 — Write-backs from continuum 2026-11-22 late](#20261122_2341--write-backs-from-continuum-2026-11-22-late)
- [20261122_2044 — Write-backs from continuum 2026-11-22 night](#20261122_2044--write-backs-from-continuum-2026-11-22-night)
- [20261122_0219 — Feature unification in tests; release size profile](#20261122_0219--feature-unification-in-tests-release-size-profile)
- [20261122_0059 — sqlx dynamic SQL refusal; calling an axum handler directly](#20261122_0059--sqlx-dynamic-sql-refusal-calling-an-axum-handler-directly)
- [20261122_0031 — Editor second windows; OnceLock memo; tar in memory](#20261122_0031--editor-second-windows-oncelock-memo-tar-in-memory)
- [20261119_1734 — Go and Rust keep their formatter's indentation (operator)](#20261119_1734--go-and-rust-keep-their-formatters-indentation-operator)
- [20261119_1659 — Learned: stop-at-first tests, minute-stamped names, diff before re-render](#20261119_1659--learned-stop-at-first-tests-minute-stamped-names-diff-before-re-render)
- [20261119_1657 — Write-back test reads every entry; topic-file headers repaired; scripts promoted](#20261119_1657--write-back-test-reads-every-entry-topic-file-headers-repaired-scripts-promoted)
- [20261119_1646 — design-patterns: misplaced patterns moved into Patterns; exact-commit gate is P-77](#20261119_1646--design-patterns-misplaced-patterns-moved-into-patterns-exact-commit-gate-is-p-77)
- [20261119_1631 — Periodic review; 90-day review window](#20261119_1631--periodic-review-90-day-review-window)

---

## Unreleased

- 2026-11-28 (me/nas): languages/javascript-typescript.md Learned: live activity rows keyed and updated in place, adaptive polling, runner step notes for a button's long job.
- 2026-11-28 (me/nas): references/design-patterns.md P-93 last good answer, marked stale; index row added. languages/javascript-typescript.md Learned: no secrets in prompt(), masked dialog and its browser test, strict-mode locators, `hidden` vs display.
- 2026-11-28 (ansible-wifi): languages/shell/learned-other.md Learned: `findmnt -n -o` pads its value; trim before a /sys path (disk_grow_guest.sh).
- 2026-11-27: references/design-patterns.md P-92 audit against an outside truth, fix only the unambiguous, list the rest (from me/nas DL-100); index row added.
- 2026-11-27: references/design-patterns.md P-91 progress by payload growth, completion from the writer's own record (from me/nas TASK-195); index row added.
- 2026-11-27: check green again: ROADMAP done item rotated (docs/history/roadmap-20261127_1602.md); languages/python/learned-other.md split (5 entries to learned-imports-and-cli.md) and languages/rust/guide-services.md split (parts 12-14 to guide-tooling.md, the guide is now 4 parts); language_split.py --lang python would have overwritten learned-other.md (17 lines), so the splits were done by entry boundary.
- 2026-11-27: Learned entry in languages/shell/learned-format-and-lint.md: remote SSH commands as quoted heredocs instead of single-quoted strings (SC2016 without a suppression), from me/nas.

- 2026-11-26 (continuum BUG-702): languages/python/learned-other.md: `python -I` drops the script's folder; ssh joins argv (quote with shlex.join); a justfile `export` beats an env-first fallback. languages/rust/learned-crates.md: reqwest `tls_certs_only` vs `add_root_certificate` (one client per trust rule); guide-services.md section on the same.
- 2026-11-26 (me/nas): references/design-patterns.md P-90: one-way mirror that never overwrites an edit made at the destination (ETag guard, temp name then MOVE, --verify).
- 2026-11-26 (me/nas): references/design-patterns.md (pull-model action queue); languages/shell.md (macOS install and pipes, grep -v under pipefail, systemd template cat, quoted-heredoc stubs).
- 2026-11-26 references/version-control-and-review.md: printing a check's exit code is not gating on it (a red commit, continuum).
- 2026-11-26 references/design-patterns.md P-89: configuration capture as stable files with churn removed; identical-twice acceptance (home NAS).
- 2026-11-26 languages/shell/learned-other.md: `install /dev/stdin` over an existing file fails, use /dev/null then tee; findmnt with two targets exits 1; references/testing.md: unittest file paths under `python -I` (continuum).
- 2026-11-26 languages/shell/learned-safety.md (a)-(c): EXIT trap and function locals under set -u; `&&` as a function's last line under set -e; single-file bind mounts keep the old inode (home NAS).
- 2026-11-26 references/safety-and-writes.md: pick a device by its defining property with exactly one match; secret into a tmux paste buffer (home NAS).
- 2026-11-25 references/design-patterns.md P-88 a streaming reader that is never silent (gap marker, bounded restart); languages/shell/learned-processes-and-timeouts.md, Learned 2026-11-25 (e): macOS `sync <file>` is a global sync that waits on a busy network share (smc-resiliency).
- 2026-11-25 scripts/table_width.py (`just table-width`, 6 tests): markdown tables at or over the hook's 200-column aligned width or already split; languages/python/learned-data-formats.md (new topic file; learned-other.md was at its budget): plistlib naive UTC dates (home NAS).
- 2026-11-25 languages/shell/learned-safety.md and learned-format-and-lint.md: `| grep -q` under pipefail fails by SIGPIPE; check must run lint; `*.sh` globs miss extension-less scripts (home NAS).
- 2026-11-25 references/testing.md, Learned 2026-11-25 (c): after a live failure, stubs carry the failing state and tests assert the outcome; a closing check verifies the property, not existence (home NAS zram).

- 2026-11-25 languages/shell/learned-processes-and-timeouts.md, Learned 2026-11-25 (d): `timeout` cannot end a process in state U (wedged SMB mount); check state first, count by state with awk (SC2009) (home NAS).

- 2026-11-25 languages/python/learned-network.md (new topic file; learned-other.md was at its budget), Learned 2026-11-25: fetch a known key list by GET, not a filtered `aws s3 cp --recursive` (582 s to 37 s; continuum FR-655).

- references/errors-and-timeouts.md, Learned 2026-11-25: nested timeouts (inner limit inside the caller's) and keeping the last stderr line of a killed
  process (continuum BUG-641). references/tooling-and-runtime.md, Learned 2026-11-25: exact-text edit scripts assert one match and re-read after a formatter.

- 2026-11-25 languages/shell/learned-safety.md, Learned 2026-11-25 (c): `read -r` returns 1 at EOF without a trailing newline and stops `set -e` scripts silently (home NAS).

- 2026-11-25 languages/shell.md: shell function comment blocks carry no `#####` banner lines (operator); languages/shell/learned-format-and-lint.md, Learned 2026-11-25 (b): `.shellcheckrc` `external-sources=true` so the IDE follows `source=` directives (home NAS).

- 2026-11-25 (continuum write-back): references/version-control-and-review.md, Learned 2026-11-25: HTTPS push sends the ref by name, guard the gated sha after pre-push; references/testing.md, Learned 2026-11-25: port-0 server start races parallel tests (try_wait, retry, stderr, probe timeout, forced-failure proof); languages/python/learned-other.md, Learned 2026-11-25: Python 3.13+ VERIFY_X509_STRICT extensions for test CAs; references/tooling-and-runtime.md, Learned 2026-11-25: launchd PATH and python3, cloud-folder hang.

- 2026-11-25 references/design-patterns.md P-65: third adopter (home NAS), compact single-file form and its limit.

- 2026-11-24 languages/hcl.md: OpenTofu-only blocks in `.tofu` files (HashiCorp tooling and tflint skip them), their variables with them, official OpenTofu VS Code extension (home NAS project).

- 2026-11-24 languages/shell/learned-format-and-lint.md: `# shellcheck source=SCRIPTDIR/...` for siblings sourced via dirname (home NAS project).

- 2026-11-24: scripts/agent_timing_backfill.py (promoted from a continuum one-off, operator request: any project, any past days); references/efficiency-and-measurement.md, Learned 2026-11-24: time every activity, the agent included (continuum DL-213)
- 2026-11-23: references/design-patterns.md P-85 (test identity bot with software credentials driving the real flows) and P-86 (run log attached to the work item), from continuum-app devbot and runlog; index rows for P-83 to P-86.

- 2026-11-23: references/design-patterns.md, P-84 (retention by membership with a time-rule fallback); references/testing.md, Learned 2026-11-23: a gate check must run in every mode it guards (continuum-app TASK-492, TASK-493).
- 2026-11-23: languages/rust/learned-async-and-tests.md, Learned 2026-11-23: tokio task_local to carry a per-operation header (continuum TASK-492).
- 2026-11-23: references/design-patterns.md, P-83 (trim a build cache by its own read trace before wiping it); languages/rust/learned-cargo-and-builds.md, Learned 2026-11-23: cargo 1.100 build-dir layout, fingerprint access time as last use, the three cargo locks (continuum-app TD-412); languages/rust/guide-keys.md section 20 (FromStr for a setting, TASK-454).
- 2026-11-22: languages/rust/learned-async-and-tests.md, Learned 2026-11-22: per-test databases dropped on Drop unless panicking (765 leaked in continuum-app); languages/rust/learned-cargo-and-builds.md, Learned 2026-11-22: one program under two binary names (lib + thin bins or #[path] wrapper; default-run).
- 2026-11-21: references/errors-and-timeouts.md (Timeouts), Learned 2026-11-21: upload timeouts scale with size when the server answers after storing.
- 2026-11-21: languages/rust/guide-keys.md (new, part 3 of the operator's Rust guide: enums with data, a library trait, let chains, secrets, module folders); languages/rust/learned-crates.md, Learned 2026-11-21: age tag recipients natively, plugin identities need PATH, README test vectors.
- 2026-11-21: references/design-patterns.md, P-82 (encrypt before a content-addressed store: address the ciphertext), from continuum FR-237.
- 2026-11-21: references/testing.md (Checks that can fail), Learned 2026-11-21: a gate verdict read from a summary line misses checks printed after it.
- 2026-11-20: references/design-patterns.md, P-80 (work order withdrawn at its deadline) and P-81 (approval marked per item from an evidence file, with a check), from continuum.
- 2026-11-20: languages/shell/learned-processes-and-timeouts.md, Learned 2026-11-20: never edit a running script (a git hook edited mid-push failed with unexpected EOF); exec a separate body file.
- 2026-11-20: languages/rust/learned-async-and-tests.md, Learned 2026-11-20: Temporal Rust SDK 1.2.0 (self: Arc<Self> activities, serde_json errors, data vs infrastructure errors, workflow_time); clippy result_large_err with axum Response -> Box<Response>.
- 2026-11-20: languages/ansible/learned-execution.md, Learned 2026-11-20: on ansible-core 2.18 a self-referencing variable fails with a recursive loop; 2.19+ resolves it.
- 2026-11-20: references/design-patterns.md, P-79 (Learned 2026-11-20): delegated rewrite proved word-preserving before it is applied (skill-pad pad_spec_words.py).
- 2026-11-20: languages/ansible/learned-execution.md, Learned 2026-11-20: on ansible-core 2.18 reading a variable templates it whole and `default()` swallows an undefined error elsewhere in it.
- 2026-11-20: languages/javascript-typescript.md, Learned 2026-11-20: isolating VS Code/VSCodium test editors (HOME for shared storage, mock keychain, stripped ELECTRON_/VSCODE_ variables, per-window extension sockets, SIGKILL after the save prompt); continuum BUG-271.
- 2026-11-20: languages/ansible/learned-execution.md, Learned 2026-11-20: a skipped task under --check registers rc 0 and empty stdout (default() never applies); `until` is evaluated on a skipped result, `changed_when`/`failed_when` are not; a `check_mode: no` reboot runs for real under --check.
- 2026-11-20: languages/rust/learned-platform.md, Learned 2026-11-20: `git worktree repair` writes through old absolute paths (rewrote a source over a VM shared mount; BUG-247); symlink modes are not portable; `#[path]` for an integration test's submodule.
- 2026-11-19: languages/shell/learned-safety.md Disputed 2026-11-19 entry reordered to the entry format (Conflicts last; `just test` caught it) and its source cited as commit 0ffd12f.
- 2026-11-19: languages/rust/ folder (operator: Rust needs its own folder and a readable guide): rust.md split by topic (topics.toml; learned-cargo-and-builds, learned-crates,
  learned-async-and-tests, learned-platform, open-items); five new Learned entries (axum body limit, spawn_blocking, clippy result_large_err, lints in tests, Command timeout);
  guide-basics.md and guide-services.md, an operator reading guide from continuum-app's code with checked links; standing rule in rust.md to grow both.
- 2026-11-19: scripts/language_split.py wrote a hard-coded 2026-11-07 into split files' Last reviewed and index line; now today's date.
- 2026-11-19: references/module-and-function-shape.md Learned 2026-11-19, over the hard limit split along a seam (or move to Python or Rust), never squeeze (operator); root-run shell sources a
  root-owned library only after an owner and mode check.
- 2026-11-19: languages/shell/learned-safety.md Learned 2026-11-19, `| head -c` under pipefail kills the reader with SIGPIPE and set -e skips the compare; macOS mounts a freshly written FAT partition
  mid-run (write sector 0 last).
- 2026-11-19: references/tooling-and-runtime.md Learned 2026-11-19, a justfile `export` does not reach direct tool calls (stray ./target).
- 2026-11-19: references/tooling-and-runtime.md Learned 2026-11-19, act's cache server binds to the LAN address by default; loopback + external URL; its client CONNECTs through a proxy.
- 2026-11-19: languages/rust.md Learned 2026-11-19, `cargo clean --target-dir` needs `--manifest-path` outside a package and refuses a folder without CACHEDIR.TAG; target folders only grow.
- 2026-11-19: references/tooling-and-runtime.md Learned 2026-11-19, act 0.2.98 keeps cache archives 7 days unused; deleting archive files is safe; prune by count.
- 2026-11-19: references/design-patterns.md P-78 offline image overlay as data, each edit point matched exactly once (smc-resiliency fieldprep).
- 2026-11-19: references/safety-and-writes.md Learned 2026-11-19, a root-run device write keeps its allowlist in the root-owned install and calls system binaries only (promoted from smc-resiliency's
  parked entry).
- 2026-11-19: languages/shell/learned-other.md Learned 2026-11-19, `grep -c` prints 0 and exits 1 on no match, so `|| echo 0` doubles the output.
- 2026-11-19: languages/ansible/learned-lint-and-tests.md Learned 2026-11-19, a one-line edit inside an old task brings all its findings into an ansible-lint delta gate.
- 2026-11-19: languages/ansible/learned-execution.md Learned 2026-11-19 (o), `git` with `update: no` never fetches and never rewrites the remote URL; updating on repoints it.
- 2026-11-19: languages/shell/learned-safety.md Disputed 2026-11-19, the `rc=$?` EXIT-trap snippet still exits 0 on macOS `/bin/sh` after a `set -u` failure; use a finished flag.
- 2026-11-19: languages/python/learned-other.md Learned 2026-11-19, `__doc__` is `str | None` (argparse description fallback).
- 2026-11-19: references/version-control-and-review.md Learned 2026-11-19, `--cacheinfo` path from the repo top; commit from a private index when another session's entries are staged; then reset your
  paths in the shared index.
- 2026-11-19: logged late (no line existed): references/design-patterns.md Learned 2026-11-05, model judgement call and MCP pilot chaining (two entries).
- 2026-11-19: logged late: references/errors-and-timeouts.md Learned 2026-11-10, stopping the process that holds an `flock`.
- 2026-11-19: logged late: references/generated-artifacts.md Learned 2026-11-12, a second easier-to-read format of a data file (JSON source, YAML view).
- 2026-11-19: logged late: references/security.md Learned 2026-11-09, release digest before unpacking and disposable config for a CLI with a cloud default (two entries).
- 2026-11-19: write-back headers repaired to the ledger format (no words changed): languages/rust.md, references/design-patterns.md (6), design-principles.md, tooling-and-runtime.md.
## 20261124_2216 — P-87 merge by unpacking beside the live copy

- references/design-patterns.md (Learned 2026-11-24): P-87 Merge by unpacking beside the live copy, never into it (CANDIDATE, continuum-app 41d77c8).

## 20261124_2215 — Rust guide: names from outside become paths; justfile exports and bare cargo test

- languages/rust/guide-keys.md: part 3 section 21, a name from outside becomes a path (allow-list check, Path::parent/file_name, ok_or), from continuum-app 41d77c8; Further reading renumbered 22.
- languages/rust/learned-cargo-and-builds.md: Learned 2026-11-24, justfile exports reach only recipes, so a bare cargo test fails with NotPresent; passthrough recipe or export loop.

## 20261124_1948 — Write-backs from continuum 2026-11-24 evening

Rust (languages/rust/learned-crates.md, 2026-11-24): PostgreSQL FOR UPDATE deadlocks with FK inserts, FOR NO KEY UPDATE does not (BUG-570); sqlx 0.8 refuses
`query(&format!(...))`. Rust (languages/rust/learned-async-and-tests.md, 2026-11-24): nextest test groups for tests sharing one external service; a "nothing goes to X"
assertion racing a later follow-up; `macro_rules!` paths in child modules. Tooling (references/tooling-and-runtime.md, 2026-11-24): a local CI image for act (pinned tag,
`--var` skips, PATH and layer-order traps, cold first run). Shell (languages/shell/learned-other.md, 2026-11-24): pipefail with `| head` recurred in a Dockerfile RUN.
Logged late (the contract test found them unlogged): 2026-11-22 entries in languages/python.md, languages/rust/learned-crates.md, languages/rust/learned-platform.md, references/version-control-and-review.md.

## 20261122_2341 — Write-backs from continuum 2026-11-22 late

Rust: rustic_core inside a server (staged file with as_path, non_exhaustive BackendOptions, opendal:s3 options, spawn_blocking works, test the library path, not only through a fallback); crypto crates optimised in dev builds; sccache with its own gate target; ? from Send+Sync boxed errors; boxing a grown enum variant.

## 20261122_2044 — Write-backs from continuum 2026-11-22 night

Rust: age + zstd streaming pass and its finish order (learned-crates; guide-keys new section for the reader), rustic_core 0.14 API and cost, tar Complete mode without atime against git archive's commit times, fastcdc v2020; sccache measured and its CARGO_INCREMENTAL=0 limit, cargo-dist 0.34 quirks, extract-a-helper for the size gate (learned-cargo-and-builds); env reads tested through an injected value in edition 2024 (learned-async-and-tests). Git: bundles against a basis omit refs the basis reaches; gate commits on the check's exit code, again (version-control-and-review). Python: set-but-empty env vars (python.md).

## 20261122_0219 — Feature unification in tests; release size profile

- languages/rust/learned-cargo-and-builds.md: feature unification hides a missing dev-dependency feature; release size with strip/LTO/codegen-units (measured).

## 20261122_0059 — sqlx dynamic SQL refusal; calling an axum handler directly

- languages/rust/learned-crates.md: sqlx refuses `query(&format!(...))` (bind instead); calling an axum handler from another handler by building its extractors (continuum FR-342).

## 20261122_0031 — Editor second windows; OnceLock memo; tar in memory

- languages/javascript-typescript.md (isolated editor tests): a second window opened through the editor's CLI comes up in Restricted Mode (turn trust off in the profile's settings.json); on Linux the CLI needs the running Xvfb's DISPLAY and XAUTHORITY (continuum TASK-276).
- languages/rust/learned-platform.md: a process-wide OnceLock<Mutex<HashSet>> memo for facts that stay true (restic repository known: 2.29 s to 1.52 s per store); the tar crate in memory (Builder<Vec<u8>>, header size, mode and checksum).

## 20261119_1734 — Go and Rust keep their formatter's indentation (operator)

- languages/go.md and languages/rust.md: an Indentation row loosens the two-space rule with its reason (gofmt cannot be set otherwise; the tool default wins, operator 2026-11-19); SKILL.md's standing
  rule names the exception; sources.yaml C-C86 (USER_STATED).

## 20261119_1659 — Learned: stop-at-first tests, minute-stamped names, diff before re-render

- references/testing.md Learned 2026-11-19 (b): a contract test collects every problem and re-reads its globs after a split.
- references/safety-and-writes.md Learned 2026-11-19: a minute-stamped output name collides; check and suffix.
- references/generated-artifacts.md Learned 2026-11-19: diff a generated file by meaning, with the format's reader, before overwriting.

## 20261119_1657 — Write-back test reads every entry; topic-file headers repaired; scripts promoted

- `tests/test_package_contract.py` test_write_back_entries_logged now collects every problem (it stopped at the first and hid 19 for a week) and reads `languages/<lang>/` topic files (split
  2026-11-07, never checked since); an entry moved by the split may be logged under its parent `<lang>.md`.
- Headers repaired, no body words changed: languages/ansible/learned-execution.md Learned 2026-11-05 (ii) -> (k), (iii) -> (l); languages/shell/learned-format-and-lint.md 2026-11-05 (ii) -> (k) (the
  format takes one letter; archived log lines still say ii/iii); two-space blockquote lines made one-space (execution, shell format-and-lint, shell other); languages/ansible/learned-lint-and-tests.md
  2026-11-17 (b) evidence parenthesised; languages/ansible/learned-templating.md 2026-11-06 (k) and the shell entry falsifier rejoined; languages/python/learned-other.md 2026-11-06 label CANDIDATE.
- Logged late: languages/python/learned-other.md Learned 2026-11-06 (hand-written list items), 2026-11-12 (sibling imports; markdown tables with a formatter), 2026-11-16 (local WebSocket API).

## 20261119_1646 — design-patterns: misplaced patterns moved into Patterns; exact-commit gate is P-77

- 2026-11-19: references/design-patterns.md (operator: "Renumber design patterns"), P-59, P-60, P-63, P-64, P-68, P-69, P-74, P-75 and P-76 moved verbatim from under Language realisations into
  Patterns in number order; the exact-commit pre-push gate section is now P-77 with an Index row; Language realisations is the last section. No existing P number changed; the old anchor
  #exact-commit-pre-push-gate had no links.

## 20261119_1631 — Periodic review; 90-day review window

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19; references, Summaries and Scopes fixed, body rules aligned with their Learned entries. Review window now
  90 days (`--window-days 90` in the justfile).
