---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261119_1640
---

# Changelog

## 20261119_1640 — Periodic review; 90-day review window

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19; references, Summaries and Scopes fixed, stale status statements and body rules aligned with their Learned entries and the code. Review window now 90 days (`--window-days 90` in the justfile).

## 20261102_0002 — Learned: say what a briefed figure counts

`references/04_falsifiability.md`, from the skill-knowledge-curator external research (2026-11-02).

## 20261101_2353 — Learned: three measures for a filter, blind mixed audit

`references/04_falsifiability.md`, from the skill-knowledge-curator triage measure (2026-11-01).

## 20261101_2307 — Learned: probes inherit assumptions; blind keys and pre-committed marks

`references/04_falsifiability.md`, from the skill-knowledge-curator gate 0 result (2026-11-01).

## 20261029_2028 — blind_ab.py: blind A/B grading packet and unblinded per-criterion scoring (0.1.10)

New `scripts/blind_ab.py` (`just blind-ab`), catalogued in scripts/README.md; promoted from the skill-network-architect evaluation
(2026-10-29), including `--drop-criterion` for a criterion one side cannot earn. Smoke-tested on 22 real cases.

## 20261029_2013 — Method write-back from the 2026-10-29 harvest (0.1.9)

- `references/02_defining-evals.md` Common failures: the wrong observable (a neighbouring layer's count), the oracle inside the search
  space and inputs that differ from production, and one averaged figure where per-phase slices and outcome claims are needed.
- `references/04_falsifiability.md` What does not count: a zero exit with non-empty output (an unknown subcommand did that).
- `references/05_reporting.md`: each result carries its as-at date and component versions, golden fixtures change only by decision with an
  `oracle_change` invalidation; technical and substantive readiness are separate axes with human-declared blockers.
- Sources: harvest notes of a service-provider lab, a cloud-repatriation plan and a personal research project (method only, no project
  content); routed in `ledger.jsonl` with `scripts/record_writeback.py`.

## 20261010_1805 — Governed-file standard: recipes, records rotated

- Workspace standard (operator, 2026-10-10; skill-ai-it "Governed files: headers, budgets, rotation and the checker's shape"): `justfile` gains
  `ai_it`, a second `check` line running skill-ai-it's `doc_freshness.py --check`, and the `stale`, `docs`, `history`, `history-show` and `rotate`
  recipes; `AGENTS.md` Working rules gain the triage line (`just docs <folder>`, `just stale`, `just history`); `doc_freshness.py --write-baseline`
  grandfathers existing findings (scripts/doc-freshness-baseline.json, 28 entries), so only new ones fail.
- CHANGELOG.md rotated 247 -> 186 lines (two passes, the second after this entry; 5 entries) and SCRATCHPAD.md 205 -> 195 lines (7 entries),
  all to `docs/history/`.

## 2026-10-07 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-07-snake-case-recipes-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-07-snake-case-recipes-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md, justfile, AI_NAVIGATION.md, SCRATCHPAD.md

## 20260923_1720 — Own-package lessons are promoted, not logged (0.1.8)

[SKILL.md](SKILL.md) (the standing write-back contract) and [AGENTS.md](AGENTS.md) gain a rule for lessons this package learns about itself: they are written in the same session into the file
that would have prevented them, never into the ledger — which stays reserved for consuming-project findings — and never left in memory,
which nothing obliges anyone to read. A lesson owned by another repository gets a tracked item there instead.

Applied at once to the two lessons from the 0.1.7 session that were sitting in memory only:

- `AGENTS.md` is excluded from git in `skills_stuff`, so a rule stated only there never leaves this machine; `SKILL.md` is the tracked copy.
- The version lives in **four** places, not three (`SKILL.md` step 4 and the `AGENTS.md` working rule both said
  three): the `package-version` pattern in `scripts/check_governance.py` is the fourth, and a
  bump that misses it fails with a message that does not name it. The working rule now says so, and forbids stating the live version anywhere else.
- `ts` in [schemas/write-back-entry.schema.json](schemas/write-back-entry.schema.json) now describes itself: machine-local time with its
  offset, so rows across a DST change must be ordered by parsed instant, never by string.

The third lesson — the OPA ledger guard's substring matching lets a pathlib rewrite, a `>` truncate and an `mv` through, exempts any command
that merely names a writer, and blocks prose that mentions the ledger — was confirmed with `opa eval` and belongs to `tools_stuff`; it is
tracked there, not here.

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
