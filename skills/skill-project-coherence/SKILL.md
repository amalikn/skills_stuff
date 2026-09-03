---
name: skill-project-coherence
description: >-
  Coherence sweep after a fix that changes durable project facts — updates
  governance, routing, reports, and generated context proportionally.
  NOT for bootstrapping (use skill-ai-it).
---

# Skill: Project Coherence

**When to use:** After making a fix that changes numbers, methodology, data classification, file locations, or any durable project fact. Examples: fixing a script bug that changes output, correcting a
rate card, updating a data source, resolving an investigation item.

**Do NOT use for:** Simple cosmetic edits, typos, or adding a new report without changing existing facts. Do NOT use for bootstrapping governance (use `skill-ai-it` for that).

---

## Contents

- [Mandatory Start](#mandatory-start)
- [Step 1 — Identify the Change](#step-1-identify-the-change)
- [Step 2 — Scan for Affected Files](#step-2-scan-for-affected-files)
- [Step 3 — Update Rules and Order](#step-3-update-rules-and-order)
- [Step 4 — Stale-Reference Validation](#step-4-stale-reference-validation)
- [Step 5 — Edge Cases](#step-5-edge-cases)
- [Step 6 — Final Checklist](#step-6-final-checklist)

---

## Mandatory Start

1. Read this SKILL.md first.
2. **Declare scope before scanning.** Write out the change in this format before touching any files:
   ```
   What changed: <one sentence>
   Old state:    <figure, path, or phrase>
   New state:    <figure, path, or phrase>
   Affected:     <script/file that implements the fix>
   ```
3. Scan the project root to inventory what exists:
   ```bash
   find . -maxdepth 2 -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "justfile" -o -name "*.json" \) | grep -v node_modules | grep -v __pycache__ | grep -v .git/ | grep -v .serena | sort
   ```
4. Check the **parent folder** for governance context — read parent `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, and `CHANGELOG.md` for inherited rules, routing patterns, and naming
   conventions.

---

## Step 1 — Identify the Change

Scope declaration (from Mandatory Start step 2) must be complete before proceeding. Then identify:

- **Affected figures/phrases** — exact strings to grep for in Step 5 (old values, old paths, old terms)
- **Affected file types** — which tiers in Step 2 are in scope

---

## Step 2 — Scan for Affected Files

The project may have some, all, or none of these. Check which exist, then update in dependency order.

### Tier 1 — Source of truth (update first)

| Component | Check | Action |
|---|---|---|
| **Data/Pipeline scripts** (`scripts/*.py`, `*.py`) | Does the script embed the old assumption? | Fix the script |
| **Data files** (`csv/*.csv`, `db/*.parquet`) | Are data files affected? Rebuild? | Rebuild if needed |
| **Task runner** (`justfile`, `Taskfile.yml`, `Makefile`) | Does it reference old scripts, stale task names, or outdated descriptions? | Update references |
| **CI config** (`.github/workflows/*.yml`) | Does it reference old scripts or commands? | Update |

**Tier 1 requires per-script reasoning, and the Step 4 grep does not discharge it.** List every script in the project and write one line each on why the change does or does not affect what that script
*computes, asserts, or prints*. Skipping a script is fine; skipping the question is not.

This is stated because collapsing Tier 1 into "did the grep hit it" is the observed failure mode. **A phrase-grep finds a stale string; it cannot find a stale assumption.** A real example: after a
correction establishing that an approval's renewability depends on its category rather than its expiry date, a grep for the old wording found and fixed two scripts that literally contained it — and
missed a break-even script that printed a "steady state" row assuming the business line still existed next year. There was no old string to search for. The assumption was in the *shape of the output*.

Two prompts that catch this class:
- Does this script print or compute anything whose **meaning** changed, even though its wording did not?
- Does it assume **continuity, completeness, or availability** that the change has just invalidated?

### Tier 2 — Report-level truth (update second)

| Component | Check | Action |
|---|---|---|
| **Current report routers** (`reports/*-current.md`) | Do they point to the right dated reports? | Update pointers |
| **Dated reports** (`reports/<topic>-YYYYMMDD_hhmm.md`) | Does the report contain the now-stale figure? | Overwrite or add supersession note |
| **Historical/stale reports** (`reports/archive/` or other dated reports) | Are older versions correctly flagged? | Add supersession note at top, or move to archive/ |

### Tier 3 — Routing and governance (update third)

| Component | Check | Action |
|---|---|---|
| **Skill entrypoint** (`skills/*/SKILL.md`) | Hard safety rules mention old approach? Stale figures? | Add/update hard safety rules |
| **Skill references** (`skills/*/references/*.md`) | Old methodology, figures, or file paths? | Update routing guidance |
| **Context router** (`AI_NAVIGATION.md`) | Old methodology, blockers, or stale routing? | Update relevant sections |
| **Machine-readable routing** (`context-map.yaml`) | Stale constraints, drift policy figures, or routing paths? | Update |
| **Agent instructions** (`AGENTS.md`) | Scripts table, key anchors, or hard rules stale? | Update |
| **Claude-specific** (`CLAUDE.md`) | Any stale instructions? | Update if needed |
| **Working memory** (`SCRATCHPAD.md`) | Current state, session history, or open items stale? | Update current state, add session entry |
| **Milestones** (`ROADMAP.md`) | Any open milestone now completed? Any new milestone implied by the | Tick completed items; add new |
|  |   change? Any future item that needs reframing given new facts? |   milestones; reframe stale future items |
| **Project overview** (`README.md`) | Status table, folder index, or key files stale? | Update |
| **Change history** (`CHANGELOG.md`) | Append entry documenting what changed and which files were updated | Append entry |
| **Memory files** (`.remember/now.md`, `.remember/recent.md`, `.remember/today-*.md`) | Do they reference old state? | Update if needed |
| **Subdirectory docs** (`scripts/README.md`, `docs/README.md`, `<subdir>/README.md`) | Row counts, filenames, scripts listed, or methodology descriptions | Update in the same pass |
|  |   stale? |  |

### Tier 4 — Permanent rules (if `.archcore/` exists)

| Component | Check | Action |
|---|---|---|
| **Archcore rules** (`.archcore/rules/*.md`) | Should a rule be created or updated to prevent regression? | Create/update |
| **Archcore guides** (`.archcore/guides/*.md`) | Do session-start or coherence-audit guides need updating? | Update |
| **Archcore settings** (`.archcore/settings.json`) | Needs updating? | Update if needed |

### Tier 5 — Regenerate generated context (do last)

| Component | Check | Action |
|---|---|---|
| **Repomix** (`repomix.config.json` exists, CLI available) | Regenerate `.ai-context/governance-pack.md` | `repomix --config repomix.config.json` |
| **Graphify** (CLI available) | Regenerate navigation graph | `graphify update .` |

---

## Step 3 — Update Rules and Order

**Always update Tier 1 → 2 → 3 → 4 → 5 in order.** This prevents incoherence where a routing file claims new truth before the underlying report is updated.

1. **Never overwrite an existing file wholesale** unless the change is trivial (one figure, one place).
2. **Use managed blocks** for repeat-refreshable content — wrap sections you own in these markers so reruns are safe:
   ```markdown
   <!-- BEGIN project-coherence:status -->
   Current match rate: 100% (updated 2026-05-23)
   <!-- END project-coherence:status -->
   ```
Applicable files: `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md` status sections.
3. **`KEEP` means durable, NOT immutable.** Never delete a `KEEP` block. But a `KEEP` block that contradicts current state **must be superseded in place** — strike the stale claim, add a dated banner
   naming what replaced it, and leave the reasoning below it. Treating `KEEP` as "do not touch" is how stale durable state survives a coherence sweep: on 2026-08-12 a block asserting a skill was
   unbuilt outlived **two runs of this skill and a full staleness audit** while the project's own ROADMAP recorded it complete. This rule was the reason — the instruction protecting durable state was
   read as protecting it from correction. Supersede-in-place is the same treatment append-only docs get, and for the same reason: the superseded reasoning is usually the useful part.
4. **CHANGELOG.md** is append-only — never rewrite historical entries.
5. **For risky YAML/JSON rewrites**, write a `.proposed` file instead of editing in place.
6. **Prefer targeted patch edits** over full-file rewriting for single-figure changes.
7. **Supersession notes go at the top** of historical reports, not the bottom.
8. **When a fix partially supersedes a report**, leave with scope note: "Findings on [topic A] remain current. Findings on [topic B] were superseded on [date] by [new report path]."

---

## Step 4 — Stale-Reference Validation

After updating all files, validate with targeted greps using the old figures/phrases from your scope declaration:

```bash
grep -rn "OLD_FIGURE_1\|OLD_FIGURE_2" --include="*.md" --include="*.yaml" --include="*.py" . | grep -v archive/ | grep -v .git/ | grep -v node_modules

grep -rn "OLD_PHRASE\|OLD_TERM" --include="*.md" --include="*.yaml" . | grep -v archive/ | grep -v .git/ | grep -v node_modules
```

Expected results:
- **Active files:** Zero hits (new figures only, or correctly framed as "old/was/previously")
- **Historical files:** Hits acceptable in `archive/`, clearly labelled as superseded, or CHANGELOG/SCRATCHPAD audit trail entries

**If grep finds unexpected hits in active files after updates:** patch those files before declaring done — do not skip.

**A clean grep is not evidence that the sweep is complete.** It proves the old strings are gone and nothing more. It cannot see an assumption that was never written as a phrase, a generated file whose
generator still emits the old model, or a script whose output shape encodes the superseded fact. Do not report a pass as complete on the strength of this step alone — Tier 1's per-script reasoning is
the part that finds those, and this step only confirms the string-level cleanup that followed.

---

## Step 5 — Edge Cases

| Scenario | Handling |
|---|---|
| **File doesn't exist** | Skip it — update only what's present |
| **Fix affects a shared script** | Check if other scripts/analysis also depend on the old assumption |
| **Old figure persists in historical report** | Add ⚠️ supersession note at the **top** |
| **Fix partially supersedes a report** | Leave with scope note on what's still valid vs what changed |
| **No generated context tools** | Skip; note in CHANGELOG |
| **Parent governance exists** | Check parent `AGENTS.md`, `AI_NAVIGATION.md` for inherited conventions |
| **Generated files need updating** | `.ai-context/`, `graphify-out/` are disposable — always regenerable, never canonical truth |

---

## Step 6 — Final Checklist

Check only what exists in this project (skip missing files without marking):

- [ ] **Every script reasoned about individually** — one line each on why the change does or does not affect what it computes, asserts or prints. Not satisfied by a clean Step 4 grep
- [ ] Script/data files fixed
- [ ] Generators checked, not just their output — a generated file re-emits the old model on every rebuild
- [ ] justfile / task runner updated (if stale)
- [ ] Current report routers updated
- [ ] Dated reports updated or superseded
- [ ] Skill hard safety rules updated
- [ ] Skill references updated
- [ ] AI_NAVIGATION.md updated
- [ ] context-map.yaml updated
- [ ] AGENTS.md / CLAUDE.md updated
- [ ] SCRATCHPAD.md updated
- [ ] ROADMAP.md updated
- [ ] README.md updated
- [ ] CHANGELOG.md entry appended
- [ ] .archcore/ rules updated (if exists)
- [ ] Subdirectory docs updated (scripts/README.md, docs/README.md, .archcore/ guides/ADRs) (if stale)
- [ ] .remember/ files updated (if exists)
- [ ] Generated context regenerated (if tools available)
- [ ] Stale-reference grep passes (Step 4)
- [ ] Parent governance reviewed
