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
Last rotated: 20261028_2101
---

# Changelog

## 20261101_0103 — Gate output in recipes

- `references/testing.md`: Learned 2026-11-01, a gate must keep its output in the recipe (Continuum).

## 20261030_1721 — Pattern P-47 (decide once from facts, persist it); Learned: run_once set_fact freezes templates, 2.21 Jinja quirks

Learned 2026-10-30 (ansible-wifi chat 0a7b835b, smc_change conditions and loop, local-knowledge-ansible 7ef59c7) in
`references/design-patterns.md` P-47 and `languages/ansible.md` (d: a run_once `set_fact` renders host templates once, use a lookup-backed
default; e: empty macro returns None, boolean `when`, no `length` test, JSON out of Jinja blocks).

- `references/design-patterns.md`: Learned 2026-10-30, P-47
- `languages/ansible.md`: Learned 2026-10-30 (d), (e)

## 20261030_1249 — Pattern P-46: audience words at the output boundary, with a leak guard

Learned 2026-10-30 (apn unified-network-controller, site workbook for the site team) in `references/design-patterns.md` P-46: translate the
internal platform's words where the file is written, phrase table then fallback, and refuse the write if the term survives.

- `references/design-patterns.md`: Learned 2026-10-30, P-46

## 20261030_1224 — Learned: filter precedence, free-form shell splitting, import_tasks placement, pipefail with grep -q

Learned 2026-10-30 (ansible-wifi chat cad11710) in `languages/ansible.md` (a: a filter binds tighter than `+`; b: free-form `shell:` splits
arguments, use `cmd:`; c: `import_tasks` only inside a play) and `languages/shell.md` (`pipefail` turns a passing `grep -q` into SIGPIPE 141).

- `languages/ansible.md`: Learned 2026-10-30 (a), (b), (c)
- `languages/shell.md`: Learned 2026-10-30

## 20261029_2035 — Write-back log index (backfill)

Learned entries whose CHANGELOG line was rotated away or never named the file, indexed so the write-back contract test can trace each:

- `languages/ansible.md`: Learned 2026-10-23
- `languages/python.md`: Learned 2026-10-19, 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23
- `languages/shell.md`: Learned 2026-10-19, 2026-10-20, 2026-10-21, 2026-10-22, 2026-10-23
- `languages/yaml-json-toml.md`: Learned 2026-10-23
- `references/errors-and-timeouts.md`: Learned 2026-10-20
- `references/evolution-and-write-back.md`: Learned 2026-10-19
- `references/generated-artifacts.md`: Learned 2026-10-21, 2026-10-22, 2026-10-23
- `references/refactoring-and-promotion.md`: Learned 2026-10-20, 2026-10-21, 2026-10-27
- `references/safety-and-writes.md`: Learned 2026-10-27
- `references/security.md`: Learned 2026-10-20
- `references/testing.md`: Learned 2026-10-20, 2026-10-21, 2026-10-26
- `references/tooling-and-runtime.md`: Learned 2026-10-20
- `references/version-control-and-review.md`: Learned 2026-10-20, 2026-10-21, 2026-10-26, 2026-10-27

## 20261029_2030 — Backfilled log line for an existing write-back

`languages/ansible.md` Learned 2026-10-20 (ansible-core 2.21.5, smc-resiliency render spike) was written without its CHANGELOG line; logged now so the
write-back contract test passes.

## 20261029_2012 — Harvest write-back: patterns P-41 to P-45 and twelve Learned entries

From the 2026-10-29 knowledge harvest of the apn and personal projects (read-only), every entry generic, sources named per entry:

- `references/design-patterns.md` Learned 2026-10-29 to (f): P-41 writing into files live sessions edit (marked region, CAS, settle
  window, idempotent ids; apn project_sync.py), P-42 FOUND / NOT_FOUND / CHECK_FAILED with a negative only from a complete walk, P-43
  classify a captured body before storing it as evidence, P-44 surface the unclassified, P-45 an edited document as a contract with a
  fixture; P-01 gains a second shape (one analysis engine, a frozen config per supplier, a written column contract).
- `references/testing.md` Learned 2026-10-29 (b)-(f): prove which mechanism refused; incident regressions assert the refusal; layer
  invariants by AST scan plus an isolated-interpreter import and a negative control; pinned verifier baselines move with provenance;
  profile source files before analysis.
- `references/safety-and-writes.md` Learned 2026-10-29: per-run scratch files, never a fixed path; (b) a fetch cache is not a filter.
- `references/errors-and-timeouts.md` Learned 2026-10-29: caps, confirmation, pacing and backoff for fan-out fetchers; (b) missing, zero
  and filtered-empty never render the same. Contents block added (the file passed 100 lines).
- `languages/sql.md` Learned 2026-10-29: cast text money at ingestion and assert row counts after every filter.
- `references/configuration-and-literals.md` Learned 2026-10-29: bootstrap applies, rendered files hold persistent state (cloud-init).
- `references/generated-artifacts.md` Learned 2026-10-29: a copied lab VM definition, without keys, drift-checked against its canonical file.
- Skipped as already covered: polling speed-up (efficiency rules), capability-gated write pipeline (P-13, write rules), vendor contract
  and plug-ins (P-17), folder-scoped commits (version-control Learned 2026-10-21), runtime pinning (tooling-and-runtime), fixes go into
  the generator (generated-artifacts).

## 20261029_1925 — Pattern P-40: hold citations by a check (ledger, local store, rules as findings)

`references/design-patterns.md` P-40, Learned 2026-10-29 from skill-network-architect (check_ledger, fetch_sources, sources_ledger).

## 20261029_2027 — Learned: know what the commit gate runs

Learned 2026-10-29 in `references/version-control-and-review.md`: a gate without tests passed 14 failing tests (unified-network-controller e6dee23).

## 20261029_1915 — Pattern P-39: carry a placement over proven edges, narrow by direction

Learned 2026-10-29 in `references/design-patterns.md`: placement over a typed evidence graph, no site convention (unified-network-controller a8c58f9).

## 20261029_1424 — Patterns P-37 and P-38 (skill-drawio speed and quality work)

Learned 2026-10-29 in `references/design-patterns.md`: a cache proved by a differential assert, keyed so an undo hits (skill-drawio 73017a9,
811c918); an estimate nominates, the real measure decides, never worse than the start (skill-drawio 1e6557d).

## 20261029_1420 — Pattern P-36: widen a name's scope by renaming in place

Learned 2026-10-29 in `references/design-patterns.md` (P-36), from unified-network-controller `smc_uplink_circuits.rename_legacy`
(e62633c): Circuits and NTDs named per site renamed to per box, never recreated.

## 20261029_1257 — Patterns P-33 to P-35 (multi-SMC build)

`references/design-patterns.md`: read all then write once; pick a moving leader once per cycle; place by evidence with a listed ledger (unified-network-controller, 2026-10-29).

## 20261029_1220 — Learned: a check that skips when its tool is missing cannot fail

Learned 2026-10-29 in `references/testing.md`: report a missing tool, never skip silently (unified-network-controller pre-commit hook, 27 to 29 Oct).

## 20261028_2306 — Learned: optimise the real outcome, not a proxy

references/design-patterns.md: proxy ranks candidates, the real computation chooses, current state always a candidate (skill-drawio overview placement, 2026-10-28).

## 20261028_2237 — Learned: shared justfile recipes and the editor

references/configuration-and-literals.md: an imported recipe file defines no variables (justfile_directory, source_directory); the VS Code just extension does not follow import for names but flags duplicates (ansible-wifi change.just, 2026-10-28).

## 20261028_2229 — Learned: a symlinked source ships whatever is checked out

references/safety-and-writes.md: pin a copy from the commit when a deploy needs a specific version; a link only when the target cannot vary by branch (ansible-wifi apt-info-no-update, 2026-10-28).

## 20261028_2101 — Learned: freeing a lock another process holds

`references/safety-and-writes.md`: Learned 2026-10-28 "freeing a lock another process holds": decide by the locks the holder has (end a refresh,
never a writer), never delete lock files, owner by device and inode. From the ansible-wifi apt lock guard (plans/apt-lock-guard-20261028_2055).

## 20261028_1942 — cpuprofile_summary helper

Added `scripts/cpuprofile_summary.py` (recipe `just cpuprofile-summary`, tests `tests/test_cpuprofile_summary.py`): reads V8 .cpuprofile files and
prints self time per extension, the hottest functions and the hottest stacks of the busiest (or `--ext`) extension. Read-only, stdlib only. Promoted
from the ansible-wifi session of 2026-10-28, where VS Code's Git view went stale because Foam pinned the extension host; the summary traced it to
Foam's orphans/placeholders refresh. Pre-existing, not from this change: `test_write_back_entries_logged` fails on a 2026-10-27 entry.

## 20261028_1311 — process_match.py: unanchored pgrep/pkill -f patterns become a check

- `scripts/process_match.py` (new): reports `pgrep -f` / `pkill -f` literal patterns not anchored with `^` in shell, YAML, Python and Jinja;
  comments and run-time patterns skipped. Tests in `tests/test_quality_helpers.py`; recipe `just process-match`; catalogued; `[process_match]` code-map section.
- `references/safety-and-writes.md` Learned 2026-10-28: anchor process patterns at the program and check them (four self-matches in ansible-wifi smc_change).
- `SKILL.md`: standing rule for anchored process patterns; tools table row.

## 20261027_1501 — Ansible include_tasks and lockstep batches, bash 3.2 empty arrays

- `languages/ansible.md` Learned 2026-10-27 (l) `include_tasks` loads when reached, so editing task files changes a running play; (m)
  `serial` batches run in lockstep, so stage-marker timers measure the batch, not the host.
- `languages/shell.md` Learned 2026-10-27: bash 3.2 `set -u` with an empty array; use `${arr[@]+"${arr[@]}"}` (verified on /bin/bash 3.2.57).

## 20261027_1213 — Ansible: to_json in debug output is escaped twice

- `languages/ansible.md`: Learned 2026-10-27 (k) - `to_json` inside a `debug` message list is escaped twice; write operator lines as words.

## 20261027_1115 — Design patterns harvested from unified-network-controller and smc-resiliency (P-13 to P-29)

- `references/design-patterns.md`: Learned 2026-10-27 (m)-(z) and three more: P-13 to P-29 harvested from unified-network-controller
  (capability table, rollback classes and end states, ownership axes, neutral contract by two consumers, stale-lock proof, class rules with
  deny-wins exceptions, ranked-evidence evals, migration ratchet) and smc-resiliency (fallback chain, destroy-what-changed, scratch build and
  sandbox validation, signed newer-only config, self-guarding probe, verdict ledger; recovery on immutable parts and clock floor as design
  only). Dead-man revert timer (P-15) found in both projects; P-02 and P-10 gained a second project. Every key line was checked against its
  source before writing (17 of 17 found).

## 20261027_1049 — Design patterns reference: out-of-the-box logic from smc_change, per language

- `references/design-patterns.md` (new, operator 2026-10-27: capture the out-of-the-box logic so projects without SMCs benefit; like
  skill-nautobot's capability patterns): Learned 2026-10-27 (a-l), twelve patterns from the smc_change engine (generic engine, baseline
  gates, write-ahead journal with fingerprint, done ledger by target hash, prepare once then partition, detached long step, evidence tree,
  shared pool, joined plug-in probe, fail-open filters, code freeze under open transactions, plan then apply), each with Ansible and Python
  realisations. `SKILL.md`: routing row and a write-back contract paragraph making patterns owed by calling projects; pointers from
  `languages/ansible.md` and `languages/python.md`.
- `references/safety-and-writes.md`: Learned 2026-10-26 entry given its missing `Source:` field (contract test failed since 0918fc0) and its
  site name removed.

## 20261027_1045 — Ansible: once-per-run play, test precedence, ssh retry backoff, include apply; git -C paths

- `languages/ansible.md`: Learned 2026-10-27 (g) once-per-run play before the serial play with group_by keeps batches dense; (h) parenthesise a filter chain before a Jinja test; (i) ssh retries only
  rc 255, pauses 2^n-1 capped 30 s, 8 retries ride out ~117 s, per-play `ansible_ssh_retries`; (j) `run_once` on include_tasks needs `apply`, a skipped task still registers.
- `languages/python.md`: Learned 2026-10-27 `git -C` resolves a relative destination under its directory; resolve paths first.

## 20261026_2222 — Ansible: run_once is per serial batch, results reach every host

- `languages/ansible.md`: Learned 2026-10-26 (f) - run_once applies include_vars, set_fact and register to all batch hosts; when judged on the first host; once per batch, not per run.

## 20261026_2146 — Ansible: until does not retry unreachable; async drop-proof waits; callbacks_enabled in 2.21

- `languages/ansible.md`: Learned 2026-10-26 (e) - until/retries and unreachable hosts, async + await pattern, async shell in check mode, callback_whitelist ignored in 2.21, callback options are a literal DOCUMENTATION (local-knowledge-ansible `76b0f86`).
