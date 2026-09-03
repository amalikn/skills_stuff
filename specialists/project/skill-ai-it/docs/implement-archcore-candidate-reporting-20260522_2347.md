# Implementation Plan: Archcore Promotion Candidate Reporting

> Revised after Codex review of initial plan. 7 corrections applied — see end of document.

## Context

`skill-ai-it` bootstrap runs `archcore init` (creates empty `.archcore/` container) but never
surfaces what *should* go into Archcore. Existing governance files (AGENTS.md, ARCHITECTURE.md,
SCRATCHPAD.md `KEEP` blocks, ROADMAP.md) often contain durable decisions and rules invisible to
the Archcore workflow.

Two Codex consultations (2026-05-22) resolved all design gaps:
- Feature name: **"Archcore promotion candidate reporting"**
- `promote` is the **only** mode that writes `.archcore/` content
- Bootstrap/refresh emit a candidates report (`ARCHCORE_PROMOTION_CANDIDATES.md`) only
- Extraction heuristics defined (two-part test: durability signal + normative language)
- CHANGELOG.md excluded from seeding sources
- Fix doc: [`docs/fix-archcore-bootstrap-seeding-20260522_2331.md`](fix-archcore-bootstrap-seeding-20260522_2331.md)

## Files to Modify (in execution order)

| # | File | Change type | Target |
|---|---|---|---|
| 1 | `patterns/archcore-routing.md` | Full replacement | Entire file |
| 2 | `SKILL.md` | Edit section | Lines 283–292 (Archcore initialization) |
| 3 | `SKILL.md` | Edit table row | Line ~56 (promote mode) |
| 4 | `templates/AI_NAVIGATION.md` | Edit table | Project context files table (line 44+) |
| 5 | `AI_NAVIGATION.md` | Edit 2 targets | Context map table (line 48+) + Archcore routing block (line 82+) |
| 6 | `README.md` | Edit bullet | Tool-stack Archcore bullet (lines 82–83) + promote row (line 28) |
| 7 | `ARCHITECTURE.md` | Edit section | Archcore section (lines 98–104) + flow diagram |
| 8 | `context-map.yaml` | Edit routing | Add `ARCHCORE_PROMOTION_CANDIDATES.md` to `routing.guidance_patterns.generated_output` |
| 9 | `templates/context-map.yaml` | Edit 2 targets | Add to `authority_order` + `routing.governance.read` / `routing.planning.read` |
| 10 | `CHANGELOG.md` | Append + TOC | New entry + TOC entry |

Sync to `~/.claude/skills/skill-ai-it/SKILL.md` is a **separate operational step** after the
package patch is complete — not part of this canonical change set.

---

## Change 1 — `patterns/archcore-routing.md` (full content replacement)

Replace current 27-line file with expanded version. New structure:

```
# Archcore Routing Pattern
## Core principle
  report-first: bootstrap/refresh emit ARCHCORE_PROMOTION_CANDIDATES.md only.
  promote-writes: only promote mode creates .archcore/ content files.
## Source mapping table (categories unchanged)
## Extraction heuristics
  ### .archcore/adr/ candidates
    - Headings: Decision, Key decisions, ADR, Accepted decision, Architecture decision
    - Decision language: "we will", "chosen approach", "accepted", "decided",
      "source of truth is"
    - Must have subject + rationale + affected area. Missing rationale → confidence: low
  ### .archcore/rules/ candidates
    - Source: AGENTS.md, CONVENTIONS.md, AI_NAVIGATION.md, governance sections
    - Normative language: must, never, always, do not, treat X as source of truth
    - Managed policy blocks are strong candidates
    - EXCLUDE: rules inherited from parent/global AGENTS.md
  ### .archcore/specs/ candidates
    - Source: ARCHITECTURE.md, CONVENTIONS.md, docs/*.md
    - Stable contracts: schemas, interfaces, boundaries, invariants, data flow
    - EXCLUDE: narrative architecture description without constraint
  ### .archcore/guides/ candidates
    - Stable, reusable procedures (not one-off troubleshooting)
  ### .archcore/plans/ candidates
    - Source: ROADMAP.md, approved phase plans
    - EXCLUDE: draft / completed / obsolete items
## Exclusion table (8 categories with rationale)
## CHANGELOG.md policy (evidence/corroboration only, never direct source)
## Candidate report format (ARCHCORE_PROMOTION_CANDIDATES.md structure)
## Rules (existing 5 + 3 new: no parent-AGENTS duplicates, no generated files,
         promote mode is the only write path)
```

---

## Change 2 — `SKILL.md` lines 283–292: Archcore initialization section

**Current heading + boundary statement:**
```
### Archcore initialization
...
`archcore init` is a setup action. Do not populate ADRs, rules, specs, guides, or plans
unless the user explicitly authorizes those content changes.
```

**New heading + expansion (append after existing boundary statement):**

Change heading to:
```
### Archcore initialization and promotion candidate reporting
```

Keep all existing bullets unchanged. After the boundary statement, append:

```markdown
#### Promotion candidate reporting

After `archcore init` (or when `.archcore/` already exists in `bootstrap` or `refresh` mode),
inspect existing governance files and emit `ARCHCORE_PROMOTION_CANDIDATES.md`:

**Source files to inspect:**
`README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CONVENTIONS.md`,
`SCRATCHPAD.md`, `memory-bank/decisionLog.md`

**Do not inspect:** `CHANGELOG.md` (history only, not truth source), generated files
(`.ai-context/`, `graphify-out/`, `repomix-output.md`).

**Extraction rules:** apply heuristics from [`patterns/archcore-routing.md`](patterns/archcore-routing.md).

**Output:** write `ARCHCORE_PROMOTION_CANDIDATES.md` in the project root. Format per
`patterns/archcore-routing.md`. Do not create any `.archcore/` content files — report only.

**Tell the user:** "Review `ARCHCORE_PROMOTION_CANDIDATES.md`, then run
`/skill-ai-it promote` to authorize writing Archcore content."

- On `refresh`: re-scan and update `ARCHCORE_PROMOTION_CANDIDATES.md`; do not overwrite
  existing `.archcore/` content.
- On `audit`: report what candidates would be surfaced; do not write the file.
- On `promote`: read `ARCHCORE_PROMOTION_CANDIDATES.md`; write or propose `.archcore/`
  content files with provenance headers and `status: proposed`.
```

---

## Change 3 — `SKILL.md` line ~56: promote mode table row

**Current:**
```
| `promote` | Scratchpad/memory/docs contain durable decisions or rules | Propose promotion into `.archcore/`, ADRs, rules, specs, guides, plans, ROADMAP, or memory-bank. Do not silently promote. |
```

**Replace with:**
```
| `promote` | User authorizes promotion from `ARCHCORE_PROMOTION_CANDIDATES.md` or explicitly requests durable promotion | Write or propose `.archcore/` content files (adr, rules, specs, guides, plans). Only mode that creates `.archcore/` content. Do not silently promote. |
```

---

## Change 4 — `templates/AI_NAVIGATION.md`: Project context files table

Table is at line 44+. Add one row after the `.archcore/plans/` row (line ~57):

```markdown
| `ARCHCORE_PROMOTION_CANDIDATES.md` | Generated list of Archcore promotion candidates from governance markdown. Read before running promote mode. | Generated support |
```

---

## Change 5 — `AI_NAVIGATION.md` (package-level, for skill maintainers)

This file governs maintaining the skill-ai-it package — it does NOT mirror the target-project
context files table. Two precise targets:

**1. Context map table (lines 48–60):** Add a row for `ARCHCORE_PROMOTION_CANDIDATES.md`
noting it is a target-project generated artifact:
```markdown
| `ARCHCORE_PROMOTION_CANDIDATES.md` | Generated in target projects by bootstrap/refresh — durable content candidates for Archcore promotion | Generated artifact |
```

**2. "Change Archcore/memory/Graphify/Repomix guidance" routing block (line 82+):** Add that
changes to Archcore guidance affect candidate report output and should be validated:
```markdown
### Change Archcore/memory/Graphify/Repomix guidance

Read:

1. `patterns/archcore-routing.md`
2. `patterns/memory-bank-structure.md`
3. Relevant sections of `SKILL.md`

Note: changes to Archcore extraction heuristics affect `ARCHCORE_PROMOTION_CANDIDATES.md`
output in target projects. Validate candidate report content after heuristic changes.
```

---

## Change 6 — `README.md`

**Line ~28 (promote row in modes table):** update trigger:
```
| `promote` | Authorize promotion of candidates from `ARCHCORE_PROMOTION_CANDIDATES.md` or explicitly request durable promotion into `.archcore/` |
```

**Lines ~82–83 (tool-stack Archcore bullet):** update to describe both init and candidate
reporting:
```
- In `skill-ai-it`: initialized under `.archcore/` during bootstrap, navigation-add, or refresh.
  After init, emits `ARCHCORE_PROMOTION_CANDIDATES.md` with durable content candidates extracted
  from governance markdown. Content is written into `.archcore/` only via `promote` mode.
```

---

## Change 7 — `ARCHITECTURE.md`

**Lines ~98–104 (Archcore section body):** append after the existing boundary statement:
```
During `bootstrap` and `refresh`, after `archcore init`, `skill-ai-it` scans existing
governance files and writes `ARCHCORE_PROMOTION_CANDIDATES.md` — a structured report of
durable content candidates (decisions, rules, specs, guides, plans) with source references
and confidence ratings. This bridges the gap between `archcore init` (setup) and `promote`
(content creation). No `.archcore/` content files are created until `promote` mode is
explicitly invoked.
```

**Flow diagram (line ~62 area):** update the `.archcore/` node label to reflect two-phase:
```
.archcore/
  init → candidates report
  promote → content files
```
(exact ASCII depends on current diagram structure — match surrounding style)

---

## Change 8 — `context-map.yaml` (package-level)

`ARCHCORE_PROMOTION_CANDIDATES.md` is generated in **target projects**, not in the skill
package itself. Do NOT add it to `authority_order` here.

Instead, add it to `routing.guidance_patterns.read` so that agents maintaining the skill's
Archcore guidance know their changes affect what candidates the skill surfaces:

```yaml
guidance_patterns:
  description: "Changes to optional guidance modules such as Archcore, Memory Bank, or drift audit."
  read:
    - "patterns/**/*.md"
    - "patterns/script-task-audit-checklist.md"
    - "SKILL.md"
    - "AI_NAVIGATION.md"
    - "ARCHITECTURE.md"
    - "CHANGELOG.md"
  generated_output:
    - "ARCHCORE_PROMOTION_CANDIDATES.md"   # emitted in target projects; validate candidate output when changing Archcore heuristics
```

---

## Change 9 — `templates/context-map.yaml` (deployed to target projects)

This template defines routing for target-project files. `ARCHCORE_PROMOTION_CANDIDATES.md`
IS a target-project file — add it in two places:

**1. `authority_order`** — append after the existing entries:
```yaml
- path: "ARCHCORE_PROMOTION_CANDIDATES.md"
  type: promotion_candidates
  authority: generated_support
```

**2. Any `routing.governance.read` or `routing.planning.read` sections** in the template —
add `ARCHCORE_PROMOTION_CANDIDATES.md` to those read lists so agents working on
governance/planning tasks know to check it before invoking promote mode.

---

## Change 10 — `CHANGELOG.md`

**TOC entry** (insert at top, newest-first):
```
- [20260522_2347 — feat: Archcore promotion candidate reporting](#20260522_2347--feat-archcore-promotion-candidate-reporting)
```

**Body entry:**
```markdown
### 20260522_2347 — feat: Archcore promotion candidate reporting

Added Archcore promotion candidate reporting to `bootstrap` and `refresh` modes. After
`archcore init`, the skill inspects governance files and emits `ARCHCORE_PROMOTION_CANDIDATES.md`
— a grouped, sourced list of durable content candidates (adr, rules, specs, guides, plans).
No `.archcore/` content files are written during bootstrap or refresh. Only `promote` mode
creates `.archcore/` content (direct user instruction also triggers promote).

**Extraction heuristics added to `patterns/archcore-routing.md`:** two-part test (durability
signal + normative language); category-specific rules for adr/rules/specs/guides/plans;
exclusion list (TODOs, session notes, unmarked SCRATCHPAD, CHANGELOG as direct source,
generated files, inherited parent rules, stale roadmap items).

**Design basis:** dual Codex consultation (2026-05-22) via codex-bridge MCP. See
[`docs/fix-archcore-bootstrap-seeding-20260522_2331.md`](fix-archcore-bootstrap-seeding-20260522_2331.md).
```

---

## Verification

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it

# 1. Syntax checks
bash -n templates/context-preflight.sh
python3 -c "import yaml,sys; yaml.safe_load(open('context-map.yaml'))"
python3 -c "import yaml,sys; yaml.safe_load(open('templates/context-map.yaml'))"
python3 -c "import json,sys; json.load(open('templates/repomix.config.json'))"

# 2. Filename consistency — ARCHCORE_PROMOTION_CANDIDATES everywhere (not SEED)
grep -r "ARCHCORE_SEED" . --include="*.md" --include="*.yaml"   # must return nothing

# 3. Key term presence
grep -r "ARCHCORE_PROMOTION_CANDIDATES" SKILL.md patterns/archcore-routing.md context-map.yaml templates/context-map.yaml
grep "Archcore promotion candidate" CHANGELOG.md README.md ARCHITECTURE.md
grep "only mode\|Only mode" SKILL.md
grep "\.archcore/adr\|\.archcore/rules\|\.archcore/specs" patterns/archcore-routing.md
grep "normative" patterns/archcore-routing.md

# 4. YAML schema shape — verify correct placement per file
# Package context-map.yaml: entry under routing.guidance_patterns.generated_output
grep -A10 "guidance_patterns" context-map.yaml | grep "ARCHCORE_PROMOTION"
# templates/context-map.yaml: entry in authority_order (NOT generated_support)
grep -A3 "promotion_candidates" templates/context-map.yaml   # expect type + authority entries

# 5. Markdown link validity — spot-check key links render correctly
grep "\[patterns/archcore-routing" SKILL.md     # should be a markdown link not bare path
grep "\[docs/fix-archcore" CHANGELOG.md         # relative markdown link

# 6. CHANGELOG TOC anchor matches body heading
grep "20260522_2347" CHANGELOG.md | wc -l       # expect >= 2 (TOC + body)

# 7. README / ARCHITECTURE updated
grep "ARCHCORE_PROMOTION_CANDIDATES\|candidate report\|promote mode" README.md
grep "ARCHCORE_PROMOTION_CANDIDATES\|candidate report\|promote mode" ARCHITECTURE.md
```

---

## Revisions Applied (vs initial plan)

| # | Correction | Change made |
|---|---|---|
| 1 | Rename ARCHCORE_SEED → ARCHCORE_PROMOTION | All occurrences updated |
| 2 | README + ARCHITECTURE in scope | Added as Changes 6 and 7 |
| 3 | context-map schema — no loose list under scripts | Package: targets `routing.guidance_patterns.generated_output`; template: targets `authority_order` + planning/governance routing |
| 4 | AI_NAVIGATION package-level targets were wrong | Now targets Context map table (line 48+) + Archcore routing block (line 82+), not target-project tables |
| 5 | promote trigger too narrow | Updated to allow direct instruction too |
| 6 | Sync step removed from package patch | Noted as separate operational step only |
| 7 | Validation — add schema shape + MD links | Checks 4 and 5 added |
| 8 | context-map package vs template distinction | Package file: ARCHCORE_PROMOTION_CANDIDATES.md is a target-project artifact — not in authority_order, only in routing.guidance_patterns |
| 9 | AI_NAVIGATION package vs template distinction | Package file governs skill maintenance only; template file governs target projects |
