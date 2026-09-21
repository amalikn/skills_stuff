---
Title: skill-walk-before-run — CHANGELOG
Status: current
Last reviewed: 2026-09-17
Summary: Behavioural revisions to skill-walk-before-run between versions.
---

# Changelog

## Unreleased — canary refinement, 2026-09-22

No behaviour change. The parked "1 + 4 canary" note in [`BRIEF.md`](BRIEF.md) gains the operator's refinement: all five devices must be online and complete. Dry-run candidates first, replace an
offline pick with an online one of the same type (it does not count toward the five), and retry one failed handshake before calling a device offline. Source: the unified-network-controller hope-vale
XV2 canary.

## Unreleased — pending revision note, 2026-09-21

No behaviour change; `SKILL.md` and the version are untouched. On operator request, a detailed note on a gap the v0.1 gate cannot see is parked in [`BRIEF.md`](BRIEF.md) under "Parked for v0.2":
**breadth before depth**. Work widened across five device families, then toward a 3,100-device fleet, before one type was proven end to end. Success was measured at the transport layer (HTTP 200)
rather than the outcome the operator sees. Every step had real reality contact, so signals 1–4 stayed quiet. The note carries the incident timeline, why v0.1 reads it as GREEN or AMBER, and five
candidate changes to judge at the next revision: a width-before-depth signal, outcome-layer reality contact, a batch ladder (one unit, then a small batch per type, then a site, then the fleet), Step 0
wording for this case, and a required definition of done.

## v0.1.2 — 2026-09-17

Incident-driven, not a design round — a project-side script bypassed this skill and wrote straight into `ledger.jsonl` (wrong location, no schema validation, no mirror/SCRATCHPAD write-back). See
[`BRIEF.md`](BRIEF.md) decision #16.

- Added `scripts/append_entry.py` as the only sanctioned writer to `ledger.jsonl`: validates the entry against `schemas/ledger-entry.md`, appends to the canonical ledger, and performs the project
  mirror + SCRATCHPAD pointer write-back in the same call.
- Added an OPA policy rule (`agent_authz.rego`, in the workspace's existing PreToolUse gate) that hard-blocks any Bash write-pattern targeting `ledger.jsonl`/`.wbr-ledger.jsonl` unless it invokes
  `append_entry.py`, and hard-blocks Write/Edit targeting either filename outright.
- Rewrote SKILL.md's Ledger and Project write-back sections to call the script instead of describing a manual append.

## v0.1.1 — 2026-09-16

Trial-evidence-driven refinement, made after running all three trial projects (cambium-swap, jdm, atar) — not a pre-trial design round. See [`BRIEF.md`](BRIEF.md) open decisions #6, #7, #8, and #9.

- Invocation now defaults to the calling project (the project of the invoking session) as the Step 0 target, instead of falling back to whatever's live in the invoking session with no explicit anchor.
  Naming a different project explicitly still overrides the default. Fixes the exact failure observed in the first live invocation, where the gate evaluated its own construction instead of the
  intended target because no project was named and none was inferred.
- Naming rule for the `project` field, added after the operator spotted "japan-jdm" (entry 3) matching no canonical source: prefer the matching `mcp-project-context` registered project name, else the
  working directory's leaf name. Tested and rejected git-toplevel-directory-name as the rule — in this workspace it resolves to `apn` for cambium-swap and `me` for atar, both shared by unrelated
  projects. `ledger.jsonl` entry 3 corrected in place from `"japan-jdm"` to `"jdm"` on operator instruction, overriding the original plan to leave it as historical record.
- New: per-project mirror. On RED or RESOLVED — same condition as the ledger — the full entry is also appended verbatim to `.wbr-ledger.jsonl` in the target project's own root (created if absent).
  Recovery copy only, read only if `ledger.jsonl` here is ever lost; not consulted while it exists. Raised by the operator as a single-point-of-failure concern: every project's findings currently live
  in one file, in one repo, that isn't the project they're about.
- New: project write-back. On RED or RESOLVED — the same condition as the ledger — a one-line pointer is appended to the target project's own `SCRATCHPAD.md` under `## Open items`, if that file
  exists; never created if absent. `ledger.jsonl` remains the sole source of truth; the pointer is discoverability only, so the target project's own governance can see a RED was raised without needing
  to know this skill's ledger exists.
- `schemas/ledger-entry.md`'s `project` field description updated to match: calling project by default, not "as used elsewhere in this skill's output."
- Step 0 now checks `ledger.jsonl` for prior entries on the calling project before deriving a fresh assumption; an existing unresolved RED is surfaced as-is instead of re-derived. No new file — the
  ledger's own `project` field is already the index. Unlike the two items above, no repeat invocation on the same project has actually occurred yet in the trial (each of the three has exactly one
  entry); added anyway since it's a read-only step against an already-existing single source of truth, not a new mechanism. See BRIEF.md open decision #8.
- `SKILL.md` grew past its original 60-100 line design target (now ~115 lines, partly from the new Project write-back section, partly from the Contents block this repo's markdown governance requires
  once a file crosses 100 lines). Noted, not hidden — see BRIEF.md decision #6.
- Bug fix in #8's own ledger-check: it would re-surface a stale RED forever if the test had actually been run since but nobody logged RESOLVED. Now checks for that first and appends RESOLVED instead.
  See BRIEF.md open decision #10.
- Bug fix in the mirror write: a deleted `.wbr-ledger.jsonl` would silently come back with only the newest entry, losing prior history that `ledger.jsonl` still has. Now self-heals — seeds from
  canonical, filtered by project, before appending. See BRIEF.md open decision #11.
- Added a documented one-time manual recovery procedure for `ledger.jsonl` itself (concatenate all project mirrors, sorted by `ts`) — not automatic sync, which was considered and rejected. See
  BRIEF.md decision #9's amendment.
- Sequencing bug fix: the ledger-check ran before Step 0 named the current assumption, so it had nothing to compare against and could wrongly treat any unresolved RED on a project as a status check.
  Reordered — Step 0 names the assumption first, ledger-check matches against that specifically. A project can now explicitly hold more than one unresolved RED at once if the assumptions differ. See
  BRIEF.md open decision #12.

## v0.1 — 2026-09-16

Initial build from the frozen brief, now colocated as [`BRIEF.md`](BRIEF.md).

- Step 0 (name the assumption) runs first, always, and is fixed for the run: assumption → signals → verdict → gate against the same assumption.
- RED/AMBER/GREEN verdict logic with four RED signals, each scope-relative to the current proposed expansion, not the project as a whole.
- Four-step gate on RED only: confirm Step 0, define the cheapest real-world test, state the disconfirming result before running it, run it before adding anything else.
- Reality-contact definition: dated raw output from the real target system counts; mocks, docs, plans, self-written tests and governance checks do not.
- Stand-down cases for irreversible-foundation work, design-as-deliverable, third-party-blocked contact, deliberate learning projects, and cheap throwaway work.
- Episode ledger format, appended only on RED, waiver, and RED-to-resolved, stored as `ledger.md` colocated in the skill's own directory (decided over the brief's original `skills-data` proposal
  before first write — see open decision #2 in the brief).
- No scripts, telemetry, config file, or `references/`/`evals/`/`docs/` directories. Manual invocation only (`/skill-walk-before-run`, `/skill-wbr`); no session-start auto-fire; no self-modification.
- Ledger format hardened before first write (no trial entries existed yet): switched from a colon-delimited text block to one JSON object per line in `ledger.jsonl`, and added `ts` (ISO 8601, local
  UTC offset, replacing date-only) and `branch` (git branch at invocation) fields. Field reference split out to `schemas/ledger-entry.md` — see open decision #5 in the brief.
