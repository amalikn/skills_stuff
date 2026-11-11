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
Last rotated: 20261111_1100
---

# Changelog

## Unreleased

- 2026-11-11: front-matter description shortened to cut startup tokens; the full original text is kept verbatim in the new `## Full description` section of SKILL.md.
- 2026-11-11 (c) write-back from the token-optimizer session: languages/python/learned-other.md, splitting front matter on "\n---" drops the last line's newline (a line regex misses the final description line); check JSON dump round-trips byte for byte before rewriting a config
- 2026-11-11 (b) write-back from ansible-wifi (smc_lynis NO_PUBKEY): languages/ansible/learned-other.md, `apt_key` with `url` and no `id` never refreshes a key whose primary is present (a new vendor subkey stays missing); pin the subkey `id` or use `get_url` plus `signed-by=`
- 2026-11-11 languages/yaml-json-toml.md: Learned, TOML vs YAML for registries keyed by id (duplicate tables fail at parse, YAML keeps the last key silently), no stdlib TOML writer, JSON Lines for appended data (unified-network-controller session)
- 2026-11-11 templates/ruff.toml: a project's ruff config (two-space, 160 columns, the skills' rule set, existing files excluded until reformatted, Markdown excluded); languages/python.md names it (operator approved, from smc-resiliency)
- 2026-11-11 write-back from smc-resiliency (docs/history standard): references/design-patterns.md P-67 (move files and repoint references by resolving links), languages/python.md (ruff 0.17 formats Markdown: exclude `*.md`)
- 2026-11-11 write-back from smc-resiliency (Pad links): references/design-patterns.md P-66 (a localhost redirect for a link scheme a web app strips; skill-pad c931f50)
- 20261110 references/tooling-and-runtime.md: Learned 2026-11-10 (skill-pad): a dataclass module loaded by path needs a sys.modules entry; flush progress lines so errors stay in order.

- 2026-11-10 (c) write-back from smc-resiliency (urlcapture-prune change): languages/ansible/learned-templating.md (a wrapper template that includes another: values by `set`, two lost newlines, prove with `cmp`)
- 2026-11-10 (b) write-back from smc-resiliency (versions record, fleet survey, N05): references/design-patterns.md P-65 (one version record, pins found by pattern; adopted by UNC), languages/shell/learned-processes-and-timeouts.md (Go programs survive SIGALRM: fork and TERM then KILL; recurrence of editing a running script), references/errors-and-timeouts.md (stop an flock holder and judge by taking the lock)
- 2026-11-10 write-back from unified-network-controller (Nautobot 3.2.9 upgrade): languages/shell/learned-processes-and-timeouts.md (a `bash -s` script loses its remainder to a child reading stdin); the `{{args}}` interpolation rule in references/tooling-and-runtime.md (Learned 2026-10-20) recurred in a new recipe and was fixed with `[positional-arguments]`, no new entry
- 2026-11-10 write-back from smc-resiliency (flash step): references/testing.md (fakes from real tool output; smoke a refusal against a real wrong target)
- 2026-11-09 (e) write-back from smc-resiliency (N03 and the S1 bench): references/design-patterns.md P-64 (a fixed-length record overwritten in place), languages/shell/learned-other.md (stdout errors with exit 0; ssh host-key, ControlPath, agent and askpass traps; macOS screen, sync, sudo), references/testing.md (vfat inodes are made up at mount)
- 2026-11-09 (d) write-back from tools_stuff cline (benchmark and prompt-cost tools): references/design-patterns.md P-63 (agent benchmark: known answers in a throwaway copy, a watch on real repos and their submodules), references/security.md (a disposable CLI config can fall back to a cloud default URL; guard egress)
- 2026-11-09 (c) write-back from smc-resiliency (follow-up audit fixes): references/testing.md (an end state needs its cause on record; test a shell function cut out of its script; printf %q fakes), references/security.md (pin a release tarball to its GitHub asset digest; check a cached tool's executable, not a marker), languages/python.md (legacy files outside ruff include lose F821), references/design-patterns.md P-62 (bind a multi-part answer with one signature)
- 2026-11-09 (b) write-back from skill-vagrant: references/errors-and-timeouts.md (a streamed download can end short without an error; check Content-Length)
- 2026-11-09 write-back from skill-vagrant: references/efficiency-and-measurement.md (a pipe filter holds a long job's progress lines)
- 2026-11-09 write-back from unified-network-controller (three entries parked in its audit follow-up, promoted): (the errors-and-timeouts.md entry is dated 2026-11-08) references/safety-and-writes.md (a rollback verifies restored state, not reachability), references/testing.md (a negative assertion needs a probe that ran; cleanup is part of the verdict), references/errors-and-timeouts.md (held alarms reach derived projections; delivery needs a durable pending record)
- 2026-11-09 write-back from skill-proxmox: references/testing.md (a token lookahead that excludes '.' misses a sentence-final token; write the negative test as prose)
- 2026-11-08 (c) write-back from smc-resiliency: references/testing.md (read_text hides \r\n; a raw pty for serial tests; termios without pyserial)
- 2026-11-08 (b) write-back from smc-resiliency S1V: references/safety-and-writes.md (write, fsync, rename is not crash-safe on FAT)
- 2026-11-08 write-back from smc-resiliency: references/testing.md (read an injected fault back before judging the case; retry only the transport's failure)
- 2026-11-07 (b) write-back from smc-resiliency: languages/python.md (default-argument binding, wrapper recursion, stale cache), references/design-patterns.md (JWS with openssl, P-59 view hash)

- scripts/scaffold.py: Python skeletons now two-space (they printed four, against the pack's own rule; found by skill-vagrant's build agent, 2026-11-07); tests/test_language_split.py (new)
- scripts/language_split.py (new), languages/readme.md (When a language file splits): ansible.md and shell.md split into ansible/ and shell/ topic files (operator, 2026-11-07); `just check` holds every language file to 200 lines
- languages/hcl.md (new, Learned 2026-11-07), languages/python.md, shell.md, yaml-json-toml.md: Learned 2026-11-07 from smc-resiliency's lab package and linters
- references/design-patterns.md: Learned 2026-11-07, logic over adapters for a test rig, profile chosen by what the box reports
- references/engine-composition.md: Learned 2026-11-07, the language per boot environment
- references/testing.md: Learned 2026-11-06 (b), a timed case counts only with its setup read back and its fault overlapping the work (smc-resiliency s3_case.sh)
- languages/shell.md: Learned 2026-11-06, editing a script a running job executes; prlctl exec has no shell; refuse an empty derived argument
- languages/ansible.md: Learned 2026-11-06 (l), extra vars with spaces go as JSON; the interpreter pin is per OS
- references/design-patterns.md: P-59 export a spec to plain code with provenance hashes and a hand-edit guard; P-60 order resumed records by attempt (Learned 2026-11-06, local-knowledge-ansible 7056782, c7cb38b)
- languages/ansible.md: Learned 2026-11-06 (k), lint-clean generated task YAML (one template at a name's end, joined templates, fold then read back)
- references/efficiency-and-measurement.md: Learned 2026-11-06, a per-check budget inside a suite, a render keyed by its inputs, profile with workers off (apn unified-network-controller).
- references/testing.md: Learned 2026-11-06, prove the instrument before trusting what it measures; languages/shell.md: Learned 2026-11-06, never edit a script while it runs (apn smc-resiliency S3).
- languages/javascript-typescript.md: Learned 2026-11-06, Playwright: real clicks on canvas, includeHidden for filtered rows, charset, skip guard (apn unified-network-controller d49d2043).
- references/design-patterns.md: P-58 second use (an evaluator holds what an unread or half-written input proves; Learned 2026-11-06, apn unified-network-controller 5c563f8b); no longer a candidate.
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
