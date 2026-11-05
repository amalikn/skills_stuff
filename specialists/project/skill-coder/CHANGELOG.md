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
Last rotated: 20261106_1030
---

# Changelog

## Unreleased

- references/design-patterns.md: P-58 Hold changes while blind; recover alone only by trials that undo themselves (Learned 2026-11-06, apn smc-resiliency 1dc80235).
- references/version-control-and-review.md: shared-index sweep confirmed 2026-11-05; Learned 2026-11-05, rerun tracked-only checks after the first commit and before the push (Continuum).
- languages/python.md: Learned 2026-11-05, `\b` matches at a hyphen; anchor names with `(?=[ \t:])` (skill-ai-it).
- references/version-control-and-review.md: Learned 2026-11-05, testing the exported index catches a file a local exclude kept out of git (skill-knowledge-curator fixture).
- references/design-patterns.md: P-56 trust a model verdict only after known controls, in words that cannot be read backwards; P-57 group by each item's most widely shared key, not single-link chaining (Learned 2026-11-05, skill-knowledge-curator).
- languages/shell.md: Learned 2026-11-05 (ii), remote half on stdin rather than a quoted string or declare -f; parallel checks with a line per host.
- languages/ansible.md: Learned 2026-11-05 (iii), facts and group_by groups outlive import_playbook; reset per run, test by value, name groups per run.
- languages/ansible.md: Learned 2026-11-05 (j), find with depth still reads every depth-N dir (slow on NFS/EFS; use GNU find -maxdepth); async is the hard limit, not retries x delay; extra vars beat set_fact, so tests must pass inputs, not outputs.
- languages/shell.md: Learned 2026-11-05, a delimiter inside a sed replacement turns the rest into flags (w writes stray files).
- languages/ansible.md: Learned 2026-11-05 (ii), strategy free drops run_once, any_errors_fatal and max_fail_percentage and refuses pause; YAML reads 20261105_120000 as an int.
- 20261105 tests/test_package_contract.py: write-back entries count as logged in rotated docs/history/changelog-*.md too (budget rotation had failed the test).
- 20261105 Learned 2026-11-05 in languages/ansible.md: (i) a failed run_once assert fails only the first host; a run-wide gate needs any_errors_fatal.
- 20261104 Learned 2026-11-04 in languages/ansible.md: (h) facts persist across plays per host, so one host per test case; quote assert items holding ': '.
- 20261104 Backfilled: Learned 2026-10-27 in languages/python.md, `git -C <dir>` reads relative paths after changing directory (a relative destination lands under <dir>); written without its CHANGELOG line.
- 20261104 Backfilled: Learned 2026-10-26 in references/safety-and-writes.md, an interrupted transaction finishes only on a completed marker and a repeated cleanup keeps the backup manifest; and process matching from automation kills or waits on itself (anchor pgrep -f); written without their CHANGELOG lines.
- 20261104 Backfilled: Learned 2026-10-26 in languages/ansible.md, (e) until/retries do not retry an unreachable host (use async + poll 0 and an await), (f) run_once applies the first host's result to the whole batch; written that day without its CHANGELOG line.
- 20261104 Learned 2026-11-04 in references/design-patterns.md: P-55 state a run can empty (one dict per run, old names read through role vars).
- 20261102 Learned 2026-11-02 in languages/python.md: lock before the read in a rebuild writer; prove it without timing.

- 20261102 Learned 2026-11-02 in languages/shell.md: crontab rewrite through a checked file; a guard around a scheduled job covers just after the tick too.

- 20261102 Learned 2026-11-02 in references/testing.md: a closing check without the tests; review text applied by script.

- 20261102 references/engine-composition.md: how a many-language engine interlocks (who does what, the seam table with a check per seam, a parser with no parser, seven moves, build order). Patterns P-50 to P-54 in references/design-patterns.md, and the index brought up to P-54. Learned 2026-11-02 in references/engine-composition.md and references/design-patterns.md.

## 20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records

`languages/shell.md`, `languages/python.md`, `references/design-patterns.md` P-49, from ansible-wifi (2026-11-02).

## 20261102_1132 — Learned: one write frame for many fields

`references/design-patterns.md` P-48, from ansible-wifi (2026-11-02).

## 20261101_2353 — Learned: guard first and dry-run a gate that hides records

`references/testing.md`, from skill-knowledge-curator (2026-11-01).

## 20261101_2307 — Learned: a predicate answering a second question

`references/testing.md`, from skill-knowledge-curator (2026-11-01).

## 20261101_1937 — Learned: Jinja dict keys through JSON, filtered loop index, folded newlines, CRLF edits

Learned 2026-11-01 in `languages/ansible.md`, from ansible-wifi smc_change.

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
