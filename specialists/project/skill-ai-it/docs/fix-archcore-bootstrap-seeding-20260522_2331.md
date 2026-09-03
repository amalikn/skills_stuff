# Fix: Archcore Promotion Candidate Reporting

> Renamed from "Archcore Bootstrap Seeding" based on dual Codex consultation (2026-05-22).
> Direct seeding during bootstrap crosses the line from setup into durable truth creation.
> `promote` is the only mode that writes `.archcore/` content.

## Summary

Add an **Archcore promotion candidate reporting** phase to `skill-ai-it`. During `bootstrap` and
`refresh`, after `archcore init`, inspect existing governance markdown and emit
`ARCHCORE_SEED_CANDIDATES.md` — a grouped, sourced list of promotion candidates. Do not write
`.archcore/adr/`, `.archcore/rules/`, or any other `.archcore/` content during bootstrap or refresh.
Only `promote` mode creates or proposes `.archcore/` content files.

## Core Principle

```
bootstrap / refresh
  → archcore init (if needed)
  → inspect governance markdown
  → emit ARCHCORE_SEED_CANDIDATES.md
  → user authorizes /skill-ai-it promote

promote
  → read ARCHCORE_SEED_CANDIDATES.md
  → write / propose .archcore/adr, .archcore/rules, .archcore/specs, etc.
```

## Key Changes

### SKILL.md — Archcore initialization section (lines 283–292)

After `archcore init` succeeds, add the candidate reporting step:

1. Inspect governance files (see source list below).
2. Apply extraction heuristics (see below).
3. Write `ARCHCORE_SEED_CANDIDATES.md` with grouped candidates.
4. Do NOT create any `.archcore/` content files — report only.
5. Tell the user: "Run `/skill-ai-it promote` to authorize writing Archcore content."

### Mode behavior

| Mode | Archcore behavior |
|---|---|
| `bootstrap` | `archcore init` if missing; emit candidates report only |
| `refresh` | Re-scan; update candidates report; no `.archcore/` file writes |
| `audit` | Report what would be in candidates report; no file writes |
| `promote` | Read candidates report; write / propose `.archcore/` content files |
| `navigation-add` | `archcore init` if missing; emit candidates report if new init occurred |

### patterns/archcore-routing.md

Add extraction heuristics, source-to-target mapping, exclusion rules, and candidate report format.

### Governance file updates

- `CHANGELOG.md`: append behavior change entry
- `AI_NAVIGATION.md` + `templates/AI_NAVIGATION.md`: note that `.archcore/` may be
  initialized-only or seeded; agents should check `ARCHCORE_SEED_CANDIDATES.md` when present
- `context-map.yaml` + `templates/context-map.yaml`: add routing for candidates file

## Extraction Heuristics

### `.archcore/adr/` candidates
- Headings: `Decision`, `Key decisions`, `ADR`, `Accepted decision`, `Architecture decision`
- Text with decision language: "we will", "chosen approach", "accepted", "decided",
  "source of truth is"
- Must include or infer subject + rationale + affected area. If rationale missing → report
  as candidate, mark confidence low (not ready for promotion)

### `.archcore/rules/` candidates
- Source files: `AGENTS.md`, `CONVENTIONS.md`, `AI_NAVIGATION.md`, governance sections
- Imperative policy language: `must`, `never`, `always`, `do not`, `treat X as source of truth`
- Managed policy blocks are strong candidates
- **Exclude**: rules already inherited from parent/global `AGENTS.md` (no duplication)

### `.archcore/specs/` candidates
- Source files: `ARCHITECTURE.md`, `CONVENTIONS.md`, `docs/*.md`
- Stable contracts: schemas, interfaces, boundaries, invariants, data flow, required file formats
- **Exclude**: narrative architecture descriptions unless they define a constraint

### `.archcore/guides/` candidates
- Setup/runbook/procedure sections with step-by-step operational workflows
- Stable and reusable procedures only — exclude one-off troubleshooting notes
- Script/task procedures only if stable

### `.archcore/plans/` candidates
- Source files: `ROADMAP.md`, approved implementation plans, phase plans
- **Exclude**: items marked draft / completed / obsolete — must be current and active

### Weak or excluded signals (never seed these)

| Content | Reason |
|---|---|
| TODOs, brainstorming, terminal logs | Not durable |
| Old session summaries | Session-specific |
| `SCRATCHPAD.md` without `KEEP` mark | Temporary by default |
| `CHANGELOG.md` as direct source | Records history including reversals |
| Generated files (`.ai-context/`, `graphify-out/`) | Rebuildable, not canonical truth |
| Local scratchpad/session state | Not project-level truth |
| Rules already in parent/global `AGENTS.md` | Avoid duplication |
| Stale roadmap items (draft/completed/obsolete) | Not current plans |

## CHANGELOG.md Policy

**Exclude as a seeding source. Use as supporting evidence only.**

- May corroborate or timestamp a candidate found in a primary source.
- CHANGELOG alone must not create an accepted Archcore candidate.
- If a CHANGELOG entry points to a rule/decision, verify it in `AGENTS.md`,
  `ARCHITECTURE.md`, `ROADMAP.md`, `README.md`, or existing `.archcore/` before promoting.
- Never seed entries marked `Reverted`, `Superseded`, `Deprecated`, `Rolled back`, `Removed`.

## Candidate Report Format (`ARCHCORE_SEED_CANDIDATES.md`)

```markdown
# Archcore Promotion Candidates

Generated by skill-ai-it on <TIMESTAMP>. Authorize with: /skill-ai-it promote

## adr
- [ ] **<subject>** | source: `<file>:<heading>` | confidence: high/medium/low
  Rationale: <one line>
  Proposed: `.archcore/adr/<slug>.md`

## rules
- [ ] **<rule summary>** | source: `<file>:<line>` | confidence: high/medium/low
  Proposed: `.archcore/rules/<slug>.md`

## specs
...
```

Group order: `adr` → `rules` → `specs` → `guides` → `plans` → `docs` → `rfc`
(rfc = uncertain/ambiguous candidates — proposed status only)

## Safety Rules

- Never infer hidden decisions from vague prose.
- Never write `.archcore/` content in bootstrap or refresh — report only.
- Do not promote `SCRATCHPAD.md` content unless marked `KEEP` and clearly stable.
- If two source files disagree on the same rule/decision, stop and report conflict.
- Do not duplicate rules already present in parent/global `AGENTS.md`.
- Do not promote generated file content (`.ai-context/`, `graphify-out/`).
- If rationale is missing for an ADR candidate, mark confidence low, not ready.
- Always include source file + heading reference in every candidate entry.

## Validation

Run after implementation:

- `bash -n templates/context-preflight.sh`
- YAML parse: `context-map.yaml`, `templates/context-map.yaml`
- JSON parse: `templates/repomix.config.json`
- Markdown heading sanity on changed `.md` files
- Grep checks:
  - `Archcore promotion candidate`
  - `ARCHCORE_SEED_CANDIDATES`
  - `archcore init`
  - `.archcore/adr`
  - `.archcore/rules`
  - `promote` (mode behavior)
  - `proposed`

## Assumptions

- `promote` is the only mode that writes `.archcore/` content files.
- Bootstrap emitting a candidates report is the default and does not require user pre-authorization.
- Archcore CLI currently provides init/status only; the skill creates categorized markdown files
  after `archcore init` when in `promote` mode.
- `CHANGELOG.md` is excluded from candidate sources by default.
- Rules inherited from parent `AGENTS.md` must not be duplicated into `.archcore/rules/`.
