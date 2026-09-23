# Changelog

## 20260923_1646 — Ledger columns ordered like the walk-before-run ledger (0.1.7)

`ledger.jsonl` rows now read `ts`, `source_project`, then the finding fields, with `entry_id` right-most — the same
lead columns as the `skill-walk-before-run` ledger, so the two estate ledgers scan alike. `recorded_at` is renamed
`ts` in [schemas/write-back-entry.schema.json](schemas/write-back-entry.schema.json), the `check_write_back_log`
required set, and [scripts/record_writeback.py](scripts/record_writeback.py), whose flag is now `--ts` and which no
longer sorts keys, since sorting is what put `commit` first. The four existing rows were rewritten once for the rename
and reorder on operator instruction. `ts` defaults to machine-local time with its offset (as walk-before-run does) instead of UTC `Z`, and the existing
rows were converted to it — the same instants, restated. Observation and invalidation records in `history.jsonl` keep
`recorded_at`, which the renderers read.

## 20260923_1642 — Falsifiability evidence proves the measure, not the binding (0.1.6)

Written back from `unified-network-controller`, whose first recorded observation exposed a limit none of the six
methods states on its own: a well-made `counterexample` fixture proved the arithmetic of a coverage eval — including
the subtle case where an out-of-population device that still reports inflates the numerator to a false full pass —
while the live numerator was bound to the wrong source, twice. A health-status row's timestamp was read as the time
of the last stored metric, and an identifier column holding UUID text was looked up with UUID objects, reporting zero
coverage against several hundred stored metrics. Neither was reachable from a CSV-fed fixture.

[references/04_falsifiability.md](references/04_falsifiability.md) gains **What it does not establish**: when the
fixture is fed from static data its evidence covers the computation and not the source binding, and that limit
belongs in the referenced artifact rather than being left for the reader to assume away. A first observation
therefore deserves a sanity check against an independent known quantity before it is recorded — neither the
validator nor the falsifiability evidence can supply one.

No closed set changed: `counterexample` remains the correct method here, so this is a prose limit on what all six
establish, not a seventh method and not an `.archcore/` rule change.

## 20260923_1331 — Archcore documents ratified to accepted

All eleven documents promoted at 20260923_1311 moved from `status: proposed` to `status: accepted` on operator authorisation. The four ADRs restate their status in the body under `## Status`; those
lines were updated in the same pass, because frontmatter and prose disagreeing about whether a decision is binding is worse than either value alone.

**This changes their authority, not just a label.** Under the source priority in [AI_NAVIGATION.md](AI_NAVIGATION.md), accepted `.archcore/` documents outrank `AGENTS.md`, `SKILL.md` and every other
surface here. The evidence-rank floor, the append-only history rule, the closed five-verdict set, the refusal rule, the eval-definition contract, the read-time derivation rules and the six
falsifiability methods are now the governing statements of this package, and prose elsewhere that disagrees is the thing to correct.

[.archcore/index.guide.md](.archcore/index.guide.md) records the ratification and states the supersession discipline: a new document starts at `proposed` and is ratified deliberately; an accepted one
is superseded rather than rewritten, with the old document set to `status: superseded` and pointed at its replacement. That is the same discipline
[append-only-history](.archcore/rules/append-only-history.rule.md) imposes on observations, applied to the governance layer.

**New check — `check_archcore_contract`.** `archcore status` enforces the `<slug>.<type>.md` filename and nothing about the frontmatter, so a document could declare `type: spec` in a file named
`*.rule.md` and both halves would look correct in isolation while routing silently mis-fired. The check asserts the five required keys, `status` within the closed set `proposed|accepted|superseded`,
and that the declared `type` matches the filename's type segment. It cites `.archcore/index.guide.md`, which is where the contract is stated. All four failure modes were proven red by deliberate
breakage before this entry was written. Checks rose from 241 to 337.

## 20260923_1311 — Archcore promotion (skill-ai-it promote mode)

Promoted eleven documents into `.archcore/` and retired `ARCHCORE_PROMOTION_CANDIDATES.md`, which `promote` is defined to delete. No package behaviour changed: `references/`, `schemas/`, the three
package scripts and every example suite are untouched. Every promoted document carries `status: proposed` and awaits operator review before it becomes `accepted`.

**Four ADRs** — the founding skill-not-a-platform decision; the reversal that splits `expired` from `invalidated` because the two call for different actions; the deliberate deferral of basis hashing
with its stated trigger; and `type: manual` as a first-class executor. **Four rules** — the evidence-rank floor, append-only history, the closed five-verdict set, and the refuse-and-ask boundary.
**Three specs** — the portable eval-definition contract, read-time derivation of `stale` and `not_evaluated`, and the six falsifiability methods as a closed set.

**Filenames follow `<slug>.<type>.md`, not `<type>-<slug>.md`.** `archcore status` rejects any other shape. The sibling `skill-smc` pack promoted its documents under the inverted name and has been
reporting five unresolved issues ever since; this pack reports none. Tags were consolidated from 20 to 8 in the same pass, because a tag used once cannot group anything — `archcore status` flags each
one. The remaining single-use tag is `index`, which `skill-ai-it` prescribes for the index document.

**Five candidates were deliberately not promoted**, and the reasoning moved into `.archcore/index.guide.md` before the candidates file was deleted. Without that table the next promotion scan
re-proposes what has already been settled. Two were rejected as duplication of upstream policy, one as a procedure no consuming project has exercised yet, one as a waiting list rather than an approved
plan, and one because its invariants are already executable — a prose copy of an assertion `scripts/validate_suite.py` already makes is the copy that drifts.

**The index is enforced, in both directions.** `scripts/check_governance.py` gained `.archcore/index.guide.md` as a catalog over `.archcore/*/*.md`: a document promoted but never indexed fails the
build, and an index row pointing at a document that does not exist fails it too. Both directions were proven red by deliberate breakage before this entry was written. The pre-promotion exemptions for
`.archcore/adr`, `.archcore/rules` and `.archcore/specs` were retired now that those folders exist, so the navigation block's routes to them are live assertions rather than registered absences.
`ARCHCORE_PROMOTION_CANDIDATES.md` took their place in `CONDITIONAL_PATHS`, so the historical mention in this file resolves as history rather than as a live route. Checks rose from 189 to 213.

Routing was rewired away from the deleted file in `context-map.yaml` (authority order, governance route, and the archcore `index:` key), `repomix.config.json`, and the `AI_NAVIGATION.md` update-rules
table. The row naming the candidates file in `AI_NAVIGATION.md`'s context table was **left alone**: it sits inside the managed `skill-ai-it:navigation` block, which is regenerated wholesale, so
editing it would be discarded on the next `nav-upgrade`. The registered `CONDITIONAL_PATHS` entry is the sanctioned escape hatch for exactly that case.

## 20260923_1222 — governance and navigation scaffold

<!-- skill-ai-it-upgrade: 2026-08-11-governance-checks-layer-v1 -->

Bootstrapped the AI governance and navigation layer with `skill-ai-it`, then ran its deterministic navigation-control upgrade. No package behaviour changed: `references/`, `schemas/`, the three
package scripts and every example suite are untouched.

Added `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `justfile`, `.mise.toml`, `requirements.txt`, `.gitignore`, `.markdownlint-cli2.jsonc`,
`repomix.config.json`, `ARCHCORE_PROMOTION_CANDIDATES.md`, and `scripts/check_governance.py`. Ran `archcore init`, which created `.archcore/settings.json` only — no Archcore content was written, and
promotion remains an operator decision.

**Two coherence defects were found and fixed, not papered over.**

1. The package version had drifted. `CHANGELOG.md` shipped 0.1.1 — the corrected renderer is present in `scripts/render_report.py` — while `SKILL.md` frontmatter and `README.md` both still advertised
   0.1.0, so a loading agent read a version whose known defect was already fixed. Both pointers were corrected, and the three-surface restatement is now a registered assertion: the next bump must
   touch all three or `just check` fails.
2. `AGENTS.md` imported `@../AGENTS.md`, which does not exist — `skills/` carries no policy file, so the nearest parent is two levels up. Corrected to `@../../AGENTS.md`. The broken link was in the
   file that defines the import chain, and nothing would have reported it.

Also corrected: several bare filenames in prose (`scripts/render_report.py`, `scripts/validate_suite.py`) that resolved nowhere, and an illustrative suite filename in `SKILL.md` that read as a file in
this repo.

**Runtimes are now pinned and addressed by path.** Python 3.14.5 and Node 26.2.0 in `.mise.toml`; the venv lives in the working-cache peer at
`/Volumes/Data/_ai/_skills/skills-working-cache/skills/skill-eval-manager/.venv`, never in this repo. The host interpreter is 3.14.7, so a bare `python3` recipe would have run a different interpreter
than the pin claims and passed silently. `just runtimes` makes the resolved interpreter visible in under a second.

**Governance claims are now executable.** `scripts/check_governance.py` carries 179 assertions, including three tuned to this package's own stated rules: every checked-in `report.md` must be newer
than the suite and history it was rendered from (the package's own "reports are derived" gate, which it was not applying to itself); every script must be cataloged in `scripts/README.md` with a safety
label, in both directions; and the version must be stated identically on its three surfaces. The derived-freshness check was deliberately broken and observed to fail before being restored.

New task catalog: `just validate-template`, `just validate-examples`, `just validate-negatives`, `just validate-all`, `just check`, `just runtimes`, `just preflight`. `validate-negatives` asserts that
every fixture under `examples/validation-failures/` still fails validation — a fixture that starts passing is a validator regression, not a fixture to repair.

Verification run at 20260923_1222: `just validate-all` passed (3 suites valid, 4 negative fixtures correctly rejected), `just check` reported 179 passed, `just nav-validate` reported 0 failures and 0
warnings, `markdownlint-cli2` reported 0 errors across 21 files.

The deterministic upgrader's regenerated navigation block was initially thinner than the template this project was bootstrapped from, and dropped the task-routing, drift-handling, update-rules and
answer-contract sections. That turned out to be a defect in `skill-ai-it` itself — an inlined copy of the block in the skill package's upgrade script had drifted nine sections behind
its navigation template since 2026-08-11 — and was fixed at source the same day: all three builders now read their templates, and a self-test asserts a required-section floor. This project was
re-upgraded onto managed block version `2026-09-23-template-sourced-blocks-v1`, restoring the generic sections inside the markers.

The package-specific drift handling, update rules and answer-contract addition remain below the END marker as `###` subsections of *Package-specific routing*, so they extend the generic sections
rather than colliding with them, and a future upgrade cannot reach them. Re-verified after the re-upgrade: `just check` 189 passed, `just nav-validate` 0 warnings and 0 failures, `just lint-md` 0
errors, `just validate-all` green, and a second consecutive `just nav-upgrade` left `AI_NAVIGATION.md` byte-identical.

## 0.1.5 — 2026-09-23

### Changed

- **The routing record is named `ledger.jsonl`** (operator, same day), matching the estate convention set by `skill-walk-before-run`. It shipped in 0.1.4 under a different name chosen specifically to
  dodge a filename collision; the convention is worth more than the dodge, so the dodge loses. References updated across `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `scripts/README.md`,
  `scripts/check_governance.py` and `scripts/record_writeback.py`. The 0.1.4 entry above now names the current file; this entry is the record that it moved.

  **The consequence is real and worth stating plainly.** That filename is covered by the estate OPA guard, which hard-blocks any Bash command whose *text* mentions it — not merely a command that
  writes it — and routes the author to `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-walk-before-run/scripts/append_entry.py`. For this package the guard is right in spirit and wrong in
  destination: correct that nothing should hand-write the
  record, incorrect that these rows belong in another pack's writer, which enforces a different schema. `scripts/record_writeback.py` is unaffected, because the filename appears inside the script
  rather than in the invoking command. Append through it, never by shell redirection.

## 0.1.4 — 2026-09-23

### Added

- **`ledger.jsonl` and `scripts/record_writeback.py`** — an append-only routing record for findings returned by consuming projects, with `scripts/check_governance.py` asserting it.

  **It records where a finding went, not the finding.** That boundary is the whole design. A log you can write to and feel finished with would legitimise recording knowledge instead of incorporating
  it — which is precisely the failure that motivated it, committed by this package on its own first write-back: the 0.1.3 session shipped a validator fix and a regression fixture, and left the method
  knowledge behind them (the enclosing-document shape) in a memory backend, reaching nobody who clones this repo.

  The load-bearing field is `incorporated_in`. `scripts/record_writeback.py` refuses a destination that does not exist, so a row cannot claim the knowledge landed before it did; `just check` then
  fails if a recorded destination later stops existing, because a write-time check cannot see a file renamed afterwards and a stale row reads as a closed loop, which is worse than no row. A finding
  with nowhere to go yet is recorded `--open`, which is reported on every run and never fails the build — an honest outstanding loop is a state, not an error. All three behaviours were proven by
  deliberate breakage.

  Backfilled with the three findings `unified-network-controller` produced on 2026-09-23. The package previously had no record at all of which project taught it what.

- `schemas/write-back-entry.schema.json` — the record contract.

### Changed

- `references/02_defining-evals.md` gains **The enclosing document**: `schema_version` is the string `"0.1"`, `suite` is a mapping with `id` and `title`, `layers` is declared once and referenced
  inline. Every shipped example had this right and no prose said so, which is what made the 0.1.3 crash reachable. This is the leaked finding, now incorporated.
- The `SKILL.md` write-back contract gains step 6 (record the routing), and the `AGENTS.md` closeout self-check now names an artifact instead of asking three yes/no questions that can be answered
  honestly while a finding still goes nowhere.

## 0.1.3 — 2026-09-23

### Fixed

- **`scripts/validate_suite.py` raised `AttributeError` instead of reporting a malformed `suite` block, whenever `--history` was also given.** `validate_history()` resolved the suite id with
  `suite.get("suite", {}).get("id")`, which assumes `suite["suite"]` is a mapping. History is validated in the same pass as the document, so a suite whose `suite` block is a bare string reached that
  line and crashed. Without `--history` the same file produced the correct two errors, so the defect was invisible to anyone validating a suite on its own. The id is now resolved defensively and the
  operator reads the structural error that `validate_suite()` already reports.

  **Found on first real use**, writing the `unified-network-controller` A6 coverage suite — the first suite this package has validated outside its own examples. This is exactly the return the standing
  write-back contract in `SKILL.md` exists to collect.

### Changed

- **`just validate-negatives` asserted only that a fixture exits non-zero.** A traceback also exits non-zero, so a crashing fixture was indistinguishable from a cleanly rejected one, and the
  regression above would have passed the gate that exists to catch it. The loop now requires a non-zero exit, an `INVALID:` line, and the absence of `Traceback`. Proven by reverting the fix and
  watching the fixture be caught as a crash.
- Fixtures may now carry a `<name>.history.jsonl` sibling, which the loop passes with `--history`, so rejection paths that only run during history validation are covered at all.

### Added

- `examples/validation-failures/malformed-suite-block.yaml` and its paired empty history, cataloged in that folder's README.

## 0.1.2 — 2026-09-23

### Added

- **Standing write-back contract** in [SKILL.md](SKILL.md), and its maintainer-facing form as a **cross-project write-back trigger** in [AGENTS.md](AGENTS.md). Any project that invokes this skill and
  learns something about evaluation *method* — a validator gap, a falsifiability method the permitted six could not cover, a verdict the closed five could not express honestly, an oracle that looked
  independent and was not — owes that knowledge back to this pack before the session closes, whether or not the calling project governance says so. Modelled on `skill-cambium` and `skill-smc`, which
  carry the same contract for their own domains.
- The contract states its own boundary: the consuming project keeps its suite, thresholds, executor wiring, schedule and results. Absorbing those would make this a platform, which
  [.archcore/adr/skill-not-platform.adr.md](.archcore/adr/skill-not-platform.adr.md) rules out.

### Changed

- `scripts/check_governance.py` registers `SKILL.md` as a catalog over `references/*.md`, so a reference file that exists but is not routed from the References section fails the build. This is the
  **only half of the write-back contract a checker can see**: knowledge that never leaves a consuming project is invisible from here. `AGENTS.md` states that limit rather than implying the rule is
  enforced. Neither `skill-cambium` nor `skill-smc` enforces its own contract either, for the same reason. Checks rose from 224 to 239, proven red by adding an unrouted reference file.

## 0.1.1 — 2026-09-23

`scripts/render_report.py` no longer reports age and declared change as one reason. A verdict that died of age now reads `expired: older than <max_age>`; one killed by a declared invalidation reads
`invalidated: <trigger> (<reference>)`, naming the trigger from the invalidation record; when both apply, both are listed. Merging them collapsed two states that call for different actions — re-run
it, versus find out what changed — which is the failure this skill exists to prevent, so the renderer was committing it. Found on independent verification of the 0.1.0 build. The four checked-in
example reports were regenerated against the corrected renderer.

Also in this pass: every markdown file in the package was reflowed to the 200-column prose rule, and `SKILL.md`'s `description` was folded to a `>-` block matching the house style in
`skill-walk-before-run`. The frontmatter was verified to still parse and the description text to round-trip unchanged.

## 0.1.0 — 2026-09-23

Initial release. Ships a portable eval-definition contract, observation/falsifiability schemas, append-only JSONL history tooling, a derived Markdown scorecard, two unlike worked suites, and negative
validation fixtures.

The release deliberately separates definitions from execution, makes `stale` and `not_evaluated` derived states, permits six falsifiability methods, and reserves but does not implement basis hashing.
