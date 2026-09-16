# SCRATCHPAD — skill-walk-before-run

Agent working memory for the `skill-walk-before-run` skill, colocated with the package. Moved 2026-09-16 from the parent `skills_stuff/SCRATCHPAD.md` — every entry below was relevant to this skill
only and has been removed from the parent file, not copied. See `BRIEF.md` for the numbered design-decision record; this file is session/status tracking, not provenance.

---

## Contents

- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history](#session-history)
- [Memory pointers](#memory-pointers)

---

## Open items

- [x] **Build `skill-walk-before-run`** — done 2026-09-16. Package at `skills/skill-walk-before-run/` (SKILL.md, README.md, CHANGELOG.md, BRIEF.md — the brief moved here from `pending_skills/` as the
  colocated provenance record). Symlinked into `~/.claude/skills` and `~/.codex/skills`. Invocation is `/skill-walk-before-run` (alias `/skill-wbr`).
- [ ] **Acceptance tests 2/3/4/5 still unvalidated, 0 RESOLVED entries yet.** The 3-project trial itself has run for real (cambium-swap, jdm, atar — all RED, all well-formed per review), but the
  negative-control, adversarial, Step-0-visibility, and assumption-stability acceptance tests were never separately exercised, and no RED has yet been closed out to RESOLVED. The real hypothesis under
  test — does a RED verdict actually change behaviour — isn't tested until the three named cheap tests get run and logged. That's the next real action, not more invocations. (Status as of 2026-09-16;
  supersedes the original "run acceptance tests, then trial" framing now that the trial has run.)
- [ ] **cambium-swap: which device family is the confirmed bench/demo unit?** Gates the current `next_test`'s track (b) — GenieACS/CWMP applies only if it's cnPilot/CPE; otherwise track (a), direct
  SNMP/cnMaestro-API against the bench unit, applies. Not yet identified. See `ledger.jsonl`, project `cambium-swap`, entry `ts` `2026-09-16T16:32:36+10:00`.

---

## Key anchors

| Item                  | Detail                                                                                                                                                                       |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ledger                | `skills/skill-walk-before-run/ledger.jsonl` — JSONL, one object/line. 6 entries as of 2026-09-16 (skill self-invocation, jdm, atar, psy-assess, and 2 for cambium-swap — the |
|                       |   second, `ts` `16:32:36`, is a proper append superseding the first, not an edit of it). Field reference: `skills/skill-walk-before-run/schemas/ledger-entry.md`.            |
| Trial project ledgers | `.wbr-ledger.jsonl` mirror + `SCRATCHPAD.md` § Open items pointer, in each of `project_stuff/apn/cambium-swap`, `project_stuff/me/uae/atar`,                                 |
|                       |   `project_stuff/me/japan/tracks/jdm` — recovery copies, canonical stays `ledger.jsonl` above. Uncommitted in their own repos as of 2026-09-16.                              |

---

## Recent decisions

- 2026-09-16 — decision #13: when a project holds multiple unresolved REDs that form a genuine dependency chain, the gate's next action must name the earliest untested step, never a later one that
  merely looks more relevant — output-only tie-break, scoped to genuinely sequential REDs (independent ones stay under #12). Documented in BRIEF.md, not encoded into `SKILL.md` logic.
- 2026-09-16 — decision #14 **RETRACTED**: a cambium-swap `next_test` correction was applied as an in-place edit of an existing ledger entry, wrongly citing #6's typo-fix amendment as precedent.
  Operator caught the contradiction directly. Reverted both `ledger.jsonl` and the cambium-swap mirror to original text. Lesson: a correction is always a new appended entry, never a rewrite of an old
  one, regardless of how minor it looks.
- 2026-09-16 — decision #15: a parallel session then properly appended (not edited) a new cambium-swap ledger entry, also correcting a deeper error — "no production access" had been read as meeting
  the third-party-gated stand-down condition, but the operator confirmed a physical bench/demo unit is actually available. Verdict stays RED; `next_test` is now two-track (SNMP/API direct vs.
  GenieACS/CWMP only if the bench unit turns out to be cnPilot/CPE — device family not yet identified).
- 2026-09-16 — declined (not actioned): splitting BRIEF.md's parked items into a separate `ROADMAP.md`. BRIEF.md already rejects a duplicate design-rationale doc for the same reason; no earned trigger
  exists yet. Revisit only if BRIEF.md becomes genuinely unwieldy, not for tidiness alone.
- 2026-09-16 — v0.1.1 hardened same-session: default targeting to the calling project, project write-back (mirror + SCRATCHPAD pointer), a naming rule for the `project` field (mcp-project-context name
  else leaf dirname, never git top-level — tested against real data, `apn`/`me` collide), and a ledger-check before re-deriving. Then four follow-up operator questions each caught a real bug in that
  same-session work: stale REDs never auto-resolving, no two-way sync needed (rejected, documented a manual recovery procedure instead), a deleted mirror losing history on next write, and a sequencing
  bug where the ledger-check ran before Step 0 named the current assumption. All fixed same day. `SKILL.md` now 128 lines (from a 60-100 target); `/skill-wbr` alias also fixed (was never registered,
  added to `~/.claude/CLAUDE.md`'s alias-block pattern). Full detail: memory-keeper channel `wbr`.
- 2026-09-16 — fact-checked and pushed back on a ChatGPT comparison against `github.com/Teycir/Assumptions` (verified real via `gh api`). Rejected adopting its two suggested additions
  (OBSERVED/INFERRED/UNKNOWN evidence vocabulary; Step 0 as an explicit chain diagram) now — both judged redundant with WBR's existing RED/AMBER/GREEN/UNKNOWN-signal + reality-contact model, and
  adopting either pre-trial would itself be the design-round pattern BRIEF.md prohibits before the trial. Parked all four resulting candidates (the two above, plus two self-generated ones — Output
  scope-limitation, ledger evidence-locator) in BRIEF.md's existing "Parked for v0.2" list rather than creating a new `roadmap.md`, matching that file's own precedent for refusing duplicate design
  docs. Full detail: memory-keeper channel `wbr`.
- 2026-09-16 — ledger format hardened pre-first-write (zero ledger entries existed): colon-delimited text (`ledger.md`) → one-JSON-object-per-line (`ledger.jsonl`), with `ts` (ISO 8601, local UTC
  offset) and `branch` (git branch at invocation) fields added. JSONL chosen over TOML for append-only single-writer log semantics and per-line failure isolation. New file `schemas/ledger-entry.md`
  holds the field reference — the brief's own earn-in trigger for that file fired for real. Recorded as BRIEF.md open decision #5, explicitly reconciled against the brief's "no fields mid-experiment"
  caution (judged pre-first-write, not mid-trial churn). Full detail: memory-keeper channel `wbr`.
- 2026-09-16 — v0.1 built and shipped: package at `skills/skill-walk-before-run/` is SKILL.md (88 lines) + README.md + CHANGELOG.md + BRIEF.md, symlinked into `~/.claude/skills` and `~/.codex/skills`.
  Built by hand rather than via `skill-creator`'s own instructions, which turned out to be the generic Codex-flavoured convention (`$CODEX_HOME`, `init_skill.py`, `agents/openai.yaml`) and contradict
  this repo's actual pattern.
- 2026-09-16 — Ledger path changed from the brief's original `skills-data/skill-walk-before-run/ledger.md` proposal to colocated `skill-walk-before-run/ledger.md` (operator instruction). Kept tracked
  in git, not gitignored — operator's call: "this is my personal skill and I can put my data in that." No revisit trigger; this is the final state, not a placeholder pending a decision.
- 2026-09-16 — Brief relocated from `pending_skills/skill-walk-before-run-brief-20260916_1303.md` to `skill-walk-before-run/BRIEF.md` (operator instruction), resolving the brief's own open decision
  #4. Renamed to the stable ALL-CAPS convention since it is now a permanent colocated reference, not a pending-review doc. Invocation command also renamed mid-build: `/walk-before-run` →
  `/skill-walk-before-run` (alias `/skill-wbr` unchanged).
- 2026-09-16 — brief frozen at v0.1 after five review rounds, and deliberately kept small: three-file package (SKILL.md 60-100 lines, README, CHANGELOG), no scripts/evals/references/schemas until each
  earns in. Trial is manual-invocation-only across three projects so the experiment measures one intervention. Full detail in memory-keeper channel `wbr`.

---

## Session history

### 2026-09-16 (continued V) — decision #13, a self-caught append-only violation, decision #15, local SCRATCHPAD.md
- Added decision #13 (RED-ordering priority for genuinely sequential unresolved REDs) to BRIEF.md at operator request, documentation-only.
- While correcting the cambium-swap RED's `next_test` (portal login gives docs, not live data — the original test was wrong), applied the fix as an in-place edit of the ledger entry, wrongly citing #6
  as precedent. Operator caught the contradiction ("you yourself said an entry cannot be edited"); reverted both `ledger.jsonl` and the project mirror, rewrote decision #14 as RETRACTED rather than
  deleting it.
- A parallel session then properly appended a corrected entry (decision #15): the "third-party gated" stand-down read was itself wrong — a bench/demo unit is confirmed available. `next_test` now
  two-track, device family of the bench unit still unidentified.
- Created this file (moved, not copied, from the parent `skills_stuff/SCRATCHPAD.md`) at operator request; declined a `ROADMAP.md` split from BRIEF.md when asked (no earned trigger).
- Evidence basis: memory-keeper channel `wbr`, 6 new keys. Checkpoint `slurp-20260916-wbr-decision13-cambium-revert-scratchpad-split`.

### 2026-09-16 (continued IV) — v0.1.1: trial-driven hardening, then four self-caught bugs
- Ran all 3 trial projects for real (cambium-swap, jdm, atar — all RED). Operator overrode earlier pushback and directed default project-targeting plus project write-back; fixed the never-registered
  `/skill-wbr` alias; investigated and fixed the `project` field naming rule (git-toplevel collides in this workspace's monorepos); backfilled mirrors/pointers into all 3 target projects' own repos.
- Operator then asked four "what if" design questions in sequence, each exposing a real bug in the work just shipped: stale REDs never auto-resolving to RESOLVED, whether mirrors need two-way sync
  (rejected, recovery procedure documented instead), a deleted mirror silently losing history, and a sequencing bug where the ledger-check ran before Step 0 could name the current assumption. Fixed
  all four same session.
- `SKILL.md` grew from 89 to 128 lines across the session; each step documented in BRIEF.md's numbered open-decisions list (now #1–#15) rather than left implicit.
- Evidence basis: memory-keeper channel `wbr`, 11 new keys across 3 slurps this session. Checkpoints: `slurp-20260916-wbr-ledger-jsonl`, `slurp-20260916-wbr-teycir-review-parked`,
  `slurp-20260916-wbr-v011-hardening`.

### 2026-09-16 (continued III) — Teycir/Assumptions comparison reviewed, candidates parked
- Operator had ChatGPT compare skill-walk-before-run against `github.com/Teycir/Assumptions` and recommend two adoptions. Fact-checked the repo via `gh api` first (confirmed real, every specific
  mechanism cited genuinely present) before opining.
- Agreed with ChatGPT's long reject list; pushed back on both its "adopt" recommendations as redundant with WBR's existing RED/AMBER/GREEN/UNKNOWN-signal + reality-contact model, and as themselves an
  instance of the pre-trial design-round pattern BRIEF.md prohibits.
- Operator asked where to file the resulting candidate ideas: decided BRIEF.md's existing "Parked for v0.2" list, explicitly declined a new `roadmap.md` (would duplicate structure BRIEF.md already
  refuses to duplicate for itself). Added 2 candidates from the review plus 2 self-generated ones (Output scope-limitation; ledger evidence-locator, folded into the existing Ledger-schema bullet).
- Evidence basis: memory-keeper channel `wbr`, 2 new keys. Checkpoint `slurp-20260916-wbr-teycir-review-parked`.

### 2026-09-16 (continued II) — ledger format hardened to JSONL
- Reviewed the skill on operator request (design assessment: sound, two calibration risks flagged for post-trial revisit — Step 0 scoping subjectivity, signal 3 likely dead weight). Operator then
  pushed on the ledger format specifically: wanted a defined schema, local time not date-only, git branch capture, and a text-vs-TOML-vs-JSONL recommendation.
- Recommended and implemented JSONL over TOML (append-only, per-line failure isolation, trivial for the parked SessionStart hook), added `ts` (local UTC offset) and `branch` fields, and promoted the
  field reference to new `schemas/ledger-entry.md`. Updated SKILL.md, README.md, CHANGELOG.md, and BRIEF.md (new revision note, open decision #5).
- Self-correction recorded: characterized the table-reflow hook's blank-first-cell continuation rows on the new schema table as "corruption" needing a fix; this channel's own prior session already
  retracted that framing (KNOWN AND ACCEPTED, not a bug) — see `wbr.tooling.table-reflow-continuation-rows-not-a-bug-20260916`.
- Evidence basis: memory-keeper channel `wbr`, 4 new keys. Checkpoint `slurp-20260916-wbr-ledger-jsonl`.

### 2026-09-16 (continued) — v0.1 built, installed, and refined
- Built the three-file-plus-brief package by hand (`SKILL.md`, `README.md`, `CHANGELOG.md`, `BRIEF.md`) after `skill-creator`'s own loaded instructions proved to be the generic Codex convention (wrong
  install root, wrong file list) rather than this repo's actual pattern — confirmed against `skill-project-coherence` and `skill-code-context-notes` first. Symlinked into `~/.claude/skills` and
  `~/.codex/skills`.
- Operator then directed two refinements: ledger path moved from the brief's `skills-data` proposal to colocated `ledger.md`, and the brief itself moved from `pending_skills/` into the skill directory
  as `BRIEF.md`, with its open decisions #2 and #4 marked decided in place. Mid-slurp, the invocation command was also renamed `/walk-before-run` → `/skill-walk-before-run`.
- Evidence basis: memory-keeper channel `wbr`, 14 keys total (6 new this session, 3 corrected in place). Checkpoint `slurp-20260916-wbr-build-shipped`.

### 2026-09-16 — brief authored and frozen
- Operator named a recurring pattern (framework/design before verifying basics; JDM and ATAR abandoned that way) and asked for a skill that detects it and gates further scaffolding. Wrote the creation
  brief; skill not yet built.
- v1 of the brief was itself an instance of the pattern (8 signals, 6 prerequisites, telemetry, install policy, pre-trial) and was cut to a minimum testable v0.1: Step 0 names the assumption, four RED
  signals, scope-relative GREEN, a four-step gate, an episode-only ledger.
- Corrected my own account twice while verifying: `gfm_anchor` does not collapse whitespace runs (my re-implementation was the defect, and auto-memory already said not to re-implement it), and table
  continuation rows come from `table-reflow`, not `rewrap.py`, and are an accepted operator trade-off rather than a bug.
- Evidence basis: memory-keeper channel `wbr` (7 keys), checkpoint `slurp-20260916-wbr-brief-frozen`.

---

## Memory pointers

- memory-keeper channel `wbr` (2026-09-16), 33 keys total: 27 from prior sessions (see below) + 6 new this session (`wbr.decision.brief-decision-13-red-ordering-priority-20260916`,
  `wbr.error.inplace-edit-violated-append-only-20260916`, `wbr.decision.cambium-swap-stand-down-inference-wrong-20260916`, `wbr.progress.local-scratchpad-created-20260916`,
  `wbr.decision.no-roadmap-split-from-brief-20260916`, `wbr.task.cambium-swap-bench-unit-family-unknown-20260916`). Checkpoint, both backends:
  `slurp-20260916-wbr-decision13-cambium-revert-scratchpad-split` (MK `65de3460`, PC `94a16588-a087-4d86-a9fb-4c3d381e9c29`).
- memory-keeper channel `wbr` (2026-09-16), 27 keys total: original 8 + 6 from the build session (see prior checkpoints below) + 4 from the ledger-JSONL session + 2 from the Teycir/Assumptions review
  + 7 new from the v0.1.1 hardening session (`wbr.error.skill-wbr-alias-never-registered-20260916`, `wbr.decision.v011-default-targeting-and-writeback-20260916`,
`wbr.decision.ledger-check-before-rederiving-20260916`, `wbr.decision.project-naming-rule-and-jdm-fix-20260916`, `wbr.decision.resilience-mirror-20260916`,
`wbr.progress.backfill-target-projects-20260916`, `wbr.decision.stale-red-and-sync-questions-20260916`). Checkpoints, both backends: `slurp-20260916-wbr-brief-frozen` (MK `df575ee5`, PC
`ba6b9ec8-62d6-4e29-9d24-b5fb0808a3ab`), `slurp-20260916-wbr-promotion-and-scratchpad` (MK `1154a452`, PC `03ed00d7-504b-4173-8c16-8986a121a144`), `slurp-20260916-wbr-build-shipped` (MK `461cd6d3`, PC
`bac99a7b-1684-44e7-847c-d8927eb7c2d0`), `slurp-20260916-wbr-ledger-jsonl` (MK `389da624`, PC `19997b84-5741-4301-9113-f1e2c7f7df48`), `slurp-20260916-wbr-teycir-review-parked` (MK `f629015a`, PC
`1a15dad2-054d-4f21-a61f-59aa86a32906`), and `slurp-20260916-wbr-v011-hardening` (MK `66306bf8`, PC `7336bb20-7a49-4a7c-9f0a-f2df03c39c40`). Project `skills_stuff`, channel `wbr`.
- Trial project ledgers (outside skills_stuff): `.wbr-ledger.jsonl` + `SCRATCHPAD.md` § Open items pointer in each of `project_stuff/apn/cambium-swap`, `project_stuff/me/uae/atar`,
  `project_stuff/me/japan/tracks/jdm` — all uncommitted in their own repos as of 2026-09-16.
