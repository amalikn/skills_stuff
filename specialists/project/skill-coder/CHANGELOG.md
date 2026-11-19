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
Last rotated: 20261119_1554
---

# Changelog

## Contents

- [Unreleased](#unreleased)
- [20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records](#20261102_1347--learned-exit-trap-exit-code-ruff-through-a-symlink-tracker-from-records)
- [20261102_1132 — Learned: one write frame for many fields](#20261102_1132--learned-one-write-frame-for-many-fields)
- [20261101_2353 — Learned: guard first and dry-run a gate that hides records](#20261101_2353--learned-guard-first-and-dry-run-a-gate-that-hides-records)
- [20261101_2307 — Learned: a predicate answering a second question](#20261101_2307--learned-a-predicate-answering-a-second-question)

---

## Unreleased

- 2026-11-19: periodic review (30-day doc-freshness): 31 files re-read in full and dated 2026-11-19, plus SETUP.md; body rules aligned with their Learned entries, Summaries, Scopes and
  Contents fixed, lifted UNVERIFIED labels where captures and tests now exist, ROADMAP restated (default since 2026-10-20; write-back test red, full scan). No Learned or Disputed entry changed.
- 2026-11-19: languages/rust.md, the `rustls-no-provider` unification recurred from a sibling workspace member (rule tightened), and a new section "Tests, build scripts and limits" (sqlx `migrate!`
  build script, `#[tokio::test]` starvation, jsonwebtoken leeway and algorithm, Unix socket path length); references/testing.md, mutation checks that never mutated; references/design-patterns.md,
  exact-commit pre-push gate (continuum-app).
- 2026-11-19: references/tooling-and-runtime.md Learned entries, act on macOS (socket flag only on the command line, host network, image gaps, pinning) and mise into the working cache;
  languages/rust.md Learned entry, sqlx 0.9 dynamic SQL, temporalio macros and missing_docs, per-test databases (Continuum).
- 2026-11-19: languages/rust.md Learned entry under Feature unification, a dependency's default features enabling reqwest `rustls-no-provider` (runtime panic on a green build; Continuum P1 spike).
- 2026-11-18: references/testing.md Learned entry, a fault-test harness that rescues the target must report ASSISTED, not PASS (smc-resiliency bench run).
- 2026-11-18: references/testing.md Learned entry, a justfile catalog check that read variables as recipes, masked by fake catalog rows (Continuum).

- 2026-11-18 new `scripts/reflow_lossless.py` and `tests/test_reflow_lossless.py` (eight cases), recipe `just reflow-lossless`: proves a re-wrapped markdown file changed no table cell and no word
  (operator, 2026-11-18: a lossless check, accept re-wraps); catalogued in scripts/README.md and SKILL.md; named in the Disputed entry of `references/safety-and-writes.md`

- 2026-11-18 `references/safety-and-writes.md`: Disputed, the same day's formatter-hook entry called a lossless re-wrap damage; compare tables un-wrapped cell by cell, not by tokens; a proven-lossless
  reflow is committable (unified-network-controller)

- 2026-11-18 `references/safety-and-writes.md`: Learned, a post-edit formatter hook rewrote a governed file far beyond the edit; compare tokens with HEAD, restore, re-apply by guarded exact
  replacement (unified-network-controller)

- 2026-11-18 `references/tooling-and-runtime.md`: Learned, a closing check recipe runs every step and fails at the end (unified-network-controller)
- 2026-11-18 `references/testing.md`: Learned, smoke-test a changed read-only script on the real host by piping the module over stdin (no file on the host), with the I/O injected for the offline test
  (unified-network-controller)
- 2026-11-18 write-back from apn smc-resiliency (staleness audit 20261118_1715): references/design-patterns.md P-76 (refuse a repeated key when loading YAML; `get_single_data()` instead of a
  suppressed S506).
- 2026-11-18 write-back from apn enterprise-strategy and smc-resiliency (chat 6128bdd9): references/design-patterns.md P-74 (add what a generator cannot write after it saves; prove it in the consuming
  application: slide motion and PowerPoint's own report) and P-75 (learn a person's hand edits: diff against the last build, sort by rule, make habits defaults).
- 2026-11-17 write-back from ansible-wifi (chat f516e57d): languages/ansible/learned-execution.md Learned 2026-11-17 (n) (note unfinished hosts, fail them in the wrapper's last play so they keep the
  later plays).
- 2026-11-17 write-back from ansible-wifi (chat f516e57d, smc_change playbooks): languages/ansible/learned-connections.md Learned 2026-11-17 (m) (`ansible_ssh_timeout` is the connect timeout behind
  "banner exchange"; a play var outranks `-T`).
- 2026-11-17 write-back from ansible-wifi (chat f516e57d, rise 9f17dd64): languages/ansible/learned-lint-and-tests.md Learned 2026-11-17 (a) (a lint delta gate brings a rewritten file's old findings
  in as new) and (b) (`shell` with a pipe: `pipefail` plus `executable: /bin/bash`).

- 2026-11-17 write-back from skill-ascii-diagrams: references/testing.md Learned 2026-11-17 (c) (sweep a repair tool over real files against an independent checker).
- 2026-11-17 write-back from skill-drawio ascii-fix work: references/testing.md Learned 2026-11-17 (b) (same-length mutation reuses a stale `.pyc`; run with `python3 -B`, `touch` after restoring).
- 2026-11-17 write-back from apn smc-resiliency (S1 outlet fault cases, 1eb7ff15): references/design-patterns.md P-73 (fault in the standby side, idempotent restore in `finally`, mount-act-unmount
  keeping rc, harness-owned hard reset); references/testing.md Learned 2026-11-17 (formatter-tolerant fixture edits).
- 2026-11-16 write-back from apn enterprise-strategy (17 Nov meeting deck): references/design-patterns.md P-72 (a short derived deck: reused builders, wording table with must-match rules,
  byte-identical refactor proof); languages/javascript-typescript.md Learned 2026-11-16 (`require.main` run guard; pptxgenjs Company and Subject defaults).
- 2026-11-16 write-back from apn smc-resiliency (ASCII renderer promoted to skill-drawio): SKILL.md Standing rules, a lint config for every project or skill worked on that lacks one (operator,
  2026-11-16); references/refactoring-and-promotion.md Learned (promoting into a pack with no lint config: add ruff.toml with existing files excluded, never re-indent the promoted file; B905 strict
  zip).
- 2026-11-16 write-back from scripts_stuff vscode_extensions (link width and soft wrap): languages/javascript-typescript.md Learned (VS Code soft wrap measures raw text plus injected text; a hiding
  decoration cannot change wrap points).
- 2026-11-16 write-back from scripts_stuff vscode_extensions (table-reflow path rule): references/safety-and-writes.md Learned (a shared tool's default change reaches every hook that calls it: ship
  opt-in, prove with a flag-off run, mtime marker for the live window).
- 2026-11-16 write-back from scripts_stuff vscode_extensions (mermaid full-size patch to markdown-inline-editor): references/design-patterns.md P-71 (anchor-guarded, re-runnable patch of a shipped
  bundle); languages/javascript-typescript.md Learned (load a VS Code extension bundle under Node with a permissive `vscode` stub; compile-only check of an inline script; security-hook false
  positives).
- 2026-11-16 write-back from smc-resiliency (bench power through a Matter strip, afe4f03b): references/design-patterns.md P-70 (physical map as data, the consumer named on each slot);
  languages/python/learned-other.md Learned (a stdlib WebSocket client for a local API).
- 2026-11-13 write-back from enterprise-strategy (weekly update builder, program pack menu card and keys): references/generated-artifacts.md Learned (a second renderer reads the first one's data
  module; a colour key from the states in use; yearless date labels sorted against the plan's first month, a label with no month refused).
- 2026-11-12 write-back from enterprise-strategy (scripts and slides arranged, d7bc439e; YAML view, 64a64b0c): references/refactoring-and-promotion.md Learned (what a text rewrite of moved paths
  misses: a sentence's full stop, links in a moved file, paths built from parts) and references/generated-artifacts.md Learned (a second format is a generated view with a `--check`, never a copy);
  design-patterns.md P-65 given its missing `· Source:` field; ROADMAP item for the red write-back contract test (13 entries the parser rejects).
- 2026-11-12 references/testing.md: Learned entry, planting a bad value in a real input to prove a test fails leaves the input newer, so an mtime-based derived check goes red; plant into a copy or
  restore the timestamp (from apn enterprise-strategy).
- 2026-11-12 write-back from enterprise-strategy (one-pager pack and strategy deck, apn a3e29af7, ee9046df, 6c262ea9): languages/javascript-typescript.md Learned, pptxgenjs text-box margins are
  points; convert in the one text helper.
- 2026-11-12 write-back from enterprise-strategy (skill-ai-it new-skill, d3132c2): references/design-patterns.md P-69 (a seed, a plan-first scaffold and a guard on the shared output) and
  languages/python/learned-other.md (load a sibling module by path; parse wrapped markdown table rows by indentation).
- 2026-11-11 (f) write-back from enterprise-strategy: references/version-control-and-review.md, run the check as well as the tests before a commit (a module budget and a write-back header form are
  check rules, not test rules).
- 2026-11-11 (e) promoted enterprise-strategy's two parked candidates of 2026-11-06: references/design-patterns.md P-68 (baseline beside forecast in a generated report) and
  languages/python/learned-other.md (accept the decoration hand-typed lines carry).
- 2026-11-11 (d) write-back from enterprise-strategy (apn project_sync, cc69e7c1): references/design-principles.md, principle 4: two lookups for the same thing share one search-scope function;
  fixtures carry every folder layout.
- 2026-11-11: front-matter description shortened to cut startup tokens; the full original text is kept verbatim in the new `## Full description` section of SKILL.md.
- 2026-11-11 (c) write-back from the token-optimizer session: languages/python/learned-other.md, splitting front matter on "\n---" drops the last line's newline (a line regex misses the final
  description line); check JSON dump round-trips byte for byte before rewriting a config
- 2026-11-11 (b) write-back from ansible-wifi (smc_lynis NO_PUBKEY): languages/ansible/learned-other.md, `apt_key` with `url` and no `id` never refreshes a key whose primary is present (a new vendor
  subkey stays missing); pin the subkey `id` or use `get_url` plus `signed-by=`
- 2026-11-11 languages/yaml-json-toml.md: Learned, TOML vs YAML for registries keyed by id (duplicate tables fail at parse, YAML keeps the last key silently), no stdlib TOML writer, JSON Lines for
  appended data (unified-network-controller session)
- 2026-11-11 templates/ruff.toml: a project's ruff config (two-space, 160 columns, the skills' rule set, existing files excluded until reformatted, Markdown excluded); languages/python.md names it
  (operator approved, from smc-resiliency)
- 2026-11-11 write-back from smc-resiliency (docs/history standard): references/design-patterns.md P-67 (move files and repoint references by resolving links), languages/python.md (ruff 0.17 formats
  Markdown: exclude `*.md`)
- 2026-11-11 write-back from smc-resiliency (Pad links): references/design-patterns.md P-66 (a localhost redirect for a link scheme a web app strips; skill-pad c931f50)
- 20261110 references/tooling-and-runtime.md: Learned 2026-11-10 (skill-pad): a dataclass module loaded by path needs a sys.modules entry; flush progress lines so errors stay in order.

- 2026-11-10 (c) write-back from smc-resiliency (urlcapture-prune change): languages/ansible/learned-templating.md (a wrapper template that includes another: values by `set`, two lost newlines, prove
  with `cmp`)
- 2026-11-10 (b) write-back from smc-resiliency (versions record, fleet survey, N05): references/design-patterns.md P-65 (one version record, pins found by pattern; adopted by UNC),
  languages/shell/learned-processes-and-timeouts.md (Go programs survive SIGALRM: fork and TERM then KILL; recurrence of editing a running script), references/errors-and-timeouts.md (stop an flock
  holder and judge by taking the lock)
- 2026-11-10 write-back from unified-network-controller (Nautobot 3.2.9 upgrade): languages/shell/learned-processes-and-timeouts.md (a `bash -s` script loses its remainder to a child reading stdin);
  the `{{args}}` interpolation rule in references/tooling-and-runtime.md (Learned 2026-10-20) recurred in a new recipe and was fixed with `[positional-arguments]`, no new entry
- 2026-11-10 write-back from smc-resiliency (flash step): references/testing.md (fakes from real tool output; smoke a refusal against a real wrong target)
- 2026-11-09 (e) write-back from smc-resiliency (N03 and the S1 bench): references/design-patterns.md P-64 (a fixed-length record overwritten in place), languages/shell/learned-other.md (stdout errors
  with exit 0; ssh host-key, ControlPath, agent and askpass traps; macOS screen, sync, sudo), references/testing.md (vfat inodes are made up at mount)
- 2026-11-09 (d) write-back from tools_stuff cline (benchmark and prompt-cost tools): references/design-patterns.md P-63 (agent benchmark: known answers in a throwaway copy, a watch on real repos and
  their submodules), references/security.md (a disposable CLI config can fall back to a cloud default URL; guard egress)
- 2026-11-09 (c) write-back from smc-resiliency (follow-up audit fixes): references/testing.md (an end state needs its cause on record; test a shell function cut out of its script; printf %q fakes),
  references/security.md (pin a release tarball to its GitHub asset digest; check a cached tool's executable, not a marker), languages/python.md (legacy files outside ruff include lose F821),
  references/design-patterns.md P-62 (bind a multi-part answer with one signature)
- 2026-11-09 (b) write-back from skill-vagrant: references/errors-and-timeouts.md (a streamed download can end short without an error; check Content-Length)
- 2026-11-09 write-back from skill-vagrant: references/efficiency-and-measurement.md (a pipe filter holds a long job's progress lines)
- 2026-11-09 write-back from unified-network-controller (three entries parked in its audit follow-up, promoted): (the errors-and-timeouts.md entry is dated 2026-11-08) references/safety-and-writes.md
  (a rollback verifies restored state, not reachability), references/testing.md (a negative assertion needs a probe that ran; cleanup is part of the verdict), references/errors-and-timeouts.md (held
  alarms reach derived projections; delivery needs a durable pending record)
- 2026-11-09 write-back from skill-proxmox: references/testing.md (a token lookahead that excludes '.' misses a sentence-final token; write the negative test as prose)
- 2026-11-08 (c) write-back from smc-resiliency: references/testing.md (read_text hides \r\n; a raw pty for serial tests; termios without pyserial)
- 2026-11-08 (b) write-back from smc-resiliency S1V: references/safety-and-writes.md (write, fsync, rename is not crash-safe on FAT)
- 2026-11-08 write-back from smc-resiliency: references/testing.md (read an injected fault back before judging the case; retry only the transport's failure)
- 2026-11-07 (b) write-back from smc-resiliency: languages/python.md (default-argument binding, wrapper recursion, stale cache), references/design-patterns.md (JWS with openssl, P-59 view hash)

- scripts/scaffold.py: Python skeletons now two-space (they printed four, against the pack's own rule; found by skill-vagrant's build agent, 2026-11-07); tests/test_language_split.py (new)
- scripts/language_split.py (new), languages/readme.md (When a language file splits): ansible.md and shell.md split into ansible/ and shell/ topic files (operator, 2026-11-07); `just check` holds
  every language file to 200 lines
- languages/hcl.md (new, Learned 2026-11-07), languages/python.md, shell.md, yaml-json-toml.md: Learned 2026-11-07 from smc-resiliency's lab package and linters
- references/design-patterns.md: Learned 2026-11-07, logic over adapters for a test rig, profile chosen by what the box reports
- references/engine-composition.md: Learned 2026-11-07, the language per boot environment
- references/testing.md: Learned 2026-11-06 (b), a timed case counts only with its setup read back and its fault overlapping the work (smc-resiliency s3_case.sh)
- languages/shell.md: Learned 2026-11-06, editing a script a running job executes; prlctl exec has no shell; refuse an empty derived argument
- languages/ansible.md: Learned 2026-11-06 (l), extra vars with spaces go as JSON; the interpreter pin is per OS
- references/design-patterns.md: P-59 export a spec to plain code with provenance hashes and a hand-edit guard; P-60 order resumed records by attempt (Learned 2026-11-06, local-knowledge-ansible
  7056782, c7cb38b)
- languages/ansible.md: Learned 2026-11-06 (k), lint-clean generated task YAML (one template at a name's end, joined templates, fold then read back)
- references/efficiency-and-measurement.md: Learned 2026-11-06, a per-check budget inside a suite, a render keyed by its inputs, profile with workers off (apn unified-network-controller).
- references/testing.md: Learned 2026-11-06, prove the instrument before trusting what it measures; languages/shell.md: Learned 2026-11-06, never edit a script while it runs (apn smc-resiliency S3).
- languages/javascript-typescript.md: Learned 2026-11-06, Playwright: real clicks on canvas, includeHidden for filtered rows, charset, skip guard (apn unified-network-controller d49d2043).
- references/design-patterns.md: P-58 second use (an evaluator holds what an unread or half-written input proves; Learned 2026-11-06, apn unified-network-controller 5c563f8b); no longer a candidate.
- references/design-patterns.md: P-58 Hold changes while blind; recover alone only by trials that undo themselves (Learned 2026-11-06, apn smc-resiliency 1dc80235).
- references/version-control-and-review.md: shared-index sweep confirmed 2026-11-05; Learned 2026-11-05, rerun tracked-only checks after the first commit and before the push (Continuum).
- languages/python.md: Learned 2026-11-05, `\b` matches at a hyphen; anchor names with `(?=[ \t:])` (skill-ai-it).
- references/version-control-and-review.md: Learned 2026-11-05, testing the exported index catches a file a local exclude kept out of git (skill-knowledge-curator fixture).
- references/design-patterns.md: P-56 trust a model verdict only after known controls, in words that cannot be read backwards; P-57 group by each item's most widely shared key, not single-link
  chaining (Learned 2026-11-05, skill-knowledge-curator).
- languages/shell.md: Learned 2026-11-05 (ii), remote half on stdin rather than a quoted string or declare -f; parallel checks with a line per host.
- languages/ansible.md: Learned 2026-11-05 (iii), facts and group_by groups outlive import_playbook; reset per run, test by value, name groups per run.
- languages/ansible.md: Learned 2026-11-05 (j), find with depth still reads every depth-N dir (slow on NFS/EFS; use GNU find -maxdepth); async is the hard limit, not retries x delay; extra vars beat
  set_fact, so tests must pass inputs, not outputs.
- languages/shell.md: Learned 2026-11-05, a delimiter inside a sed replacement turns the rest into flags (w writes stray files).
- languages/ansible.md: Learned 2026-11-05 (ii), strategy free drops run_once, any_errors_fatal and max_fail_percentage and refuses pause; YAML reads 20261105_120000 as an int.
- 20261105 tests/test_package_contract.py: write-back entries count as logged in rotated docs/history/changelog-*.md too (budget rotation had failed the test).
- 20261105 Learned 2026-11-05 in languages/ansible.md: (i) a failed run_once assert fails only the first host; a run-wide gate needs any_errors_fatal.
- 20261104 Learned 2026-11-04 in languages/ansible.md: (h) facts persist across plays per host, so one host per test case; quote assert items holding ': '.
- 20261104 Backfilled: Learned 2026-10-27 in languages/python.md, `git -C <dir>` reads relative paths after changing directory (a relative destination lands under <dir>); written without its CHANGELOG
  line.
- 20261104 Backfilled: Learned 2026-10-26 in references/safety-and-writes.md, an interrupted transaction finishes only on a completed marker and a repeated cleanup keeps the backup manifest; and
  process matching from automation kills or waits on itself (anchor pgrep -f); written without their CHANGELOG lines.
- 20261104 Backfilled: Learned 2026-10-26 in languages/ansible.md, (e) until/retries do not retry an unreachable host (use async + poll 0 and an await), (f) run_once applies the first host's result to
  the whole batch; written that day without its CHANGELOG line.
- 20261104 Learned 2026-11-04 in references/design-patterns.md: P-55 state a run can empty (one dict per run, old names read through role vars).
- 20261102 Learned 2026-11-02 in languages/python.md: lock before the read in a rebuild writer; prove it without timing.

- 20261102 Learned 2026-11-02 in languages/shell.md: crontab rewrite through a checked file; a guard around a scheduled job covers just after the tick too.

- 20261102 Learned 2026-11-02 in references/testing.md: a closing check without the tests; review text applied by script.

- 20261102 references/engine-composition.md: how a many-language engine interlocks (who does what, the seam table with a check per seam, a parser with no parser, seven moves, build order). Patterns
  P-50 to P-54 in references/design-patterns.md, and the index brought up to P-54. Learned 2026-11-02 in references/engine-composition.md and references/design-patterns.md.

## 20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records

`languages/shell.md`, `languages/python.md`, `references/design-patterns.md` P-49, from ansible-wifi (2026-11-02).

## 20261102_1132 — Learned: one write frame for many fields

`references/design-patterns.md` P-48, from ansible-wifi (2026-11-02).

## 20261101_2353 — Learned: guard first and dry-run a gate that hides records

`references/testing.md`, from skill-knowledge-curator (2026-11-01).

## 20261101_2307 — Learned: a predicate answering a second question

`references/testing.md`, from skill-knowledge-curator (2026-11-01).
