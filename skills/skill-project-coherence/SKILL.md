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
- [Step 1 — Identify the Change](#step-1--identify-the-change)
- [Step 2 — Scan for Affected Files](#step-2--scan-for-affected-files)
- [Step 3 — Update Rules and Order](#step-3--update-rules-and-order)
- [Step 4 — Stale-Reference Validation](#step-4--stale-reference-validation)
- [Step 5 — Edge Cases](#step-5--edge-cases)
- [Step 6 — Final Checklist](#step-6--final-checklist)
- [Tool hazards](#tool-hazards)

---

## Mandatory Start

1. Read this SKILL.md first.
2. **Declare scope before scanning.** Write out the change in this format before touching any files:
   ```
   What changed: <one sentence>
   Old state:    <figure, path, or phrase>
   New state:    <figure, path, or phrase>
   Affected:     <script/file that implements the fix>
   Decision?:    <yes/no — an operator decision or rule, wherever it was recorded>
   Duties:       <each "update X when Y" duty from the parent policies that this change triggers>
   Siblings:     <each skill package or sibling repo that restates facts this change touches>
   Live data:    <each system of record holding prose this change makes stale, e.g. Nautobot descriptions>
   ```
3. Scan the project root to inventory what exists:
   ```bash
   find . -maxdepth 2 -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "justfile" -o -name "*.json" \) | grep -v node_modules | grep -v __pycache__ | grep -v .git/ | grep -v .serena | sort
   ```
4. Check the **parent folder** for governance context — read parent `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, and `CHANGELOG.md` for inherited rules, routing patterns, and naming
   conventions. **Then list the parent policies' duties and carry out the ones this change triggers** — reading them is not doing them. Walk every `AGENTS.md` from the project up to the workspace
   root:
   ```bash
   d=$PWD
   while [ "$d" != / ]; do
     [ -f "$d/AGENTS.md" ] && grep -Hn -iE \
       "update .* when|whenever|when (adding|creating|moving|renaming)|in the same pass" "$d/AGENTS.md"
     d=$(dirname "$d")
   done
   ```
Each hit is a duty ("update the wiki project page when creating new project areas"). Put the triggered ones in the scope declaration's `Duties:` line; each is done or reported as not done.

---

## Step 1 — Identify the Change

Scope declaration (from Mandatory Start step 2) must be complete before proceeding. Then identify:

- **Affected figures/phrases** — exact strings to sweep for in Step 4 (old values, old paths, old terms)
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
| **Live system of record** (Nautobot, a CMDB, a database the project writes to) | Do descriptions, comments or custom fields of objects the change touched restate the old fact? | Read back the |
|  |   List objects changed since the change or holding the old value (Nautobot: `?last_updated__gte=`, `?q=`) and read their free text |   prose; fix it through the project's named writer, not by hand |

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
| **Reader-first page** (`ARCHITECTURE.md` "Key decisions", or the page `AI_NAVIGATION.md` sends readers to first) | Does every operator decision this change carries appear there — | Add it with a |
|  |   whether it was recorded in the register, in `AGENTS.md`, in a `.archcore/` rule, or only in the CHANGELOG? |   pointer to its record |
| **Sibling skill packages and repos** (every skill the project invokes: `AGENTS.md` "Required skills", `CLAUDE.md`, `SIBLING_ROOTS` in `scripts/check_governance.py`) | Do their | Fix in the |
|  |   `SKILL.md`, `references/` or docs restate the old value? Sweep them with `stale_refs.py --also <path>` |   package's own canonical repo, with its own changelog and version |
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

After updating all files, sweep for the old figures/phrases from your scope declaration — this project **and** every sibling on the `Siblings:` line:

```bash
python3 <skill>/scripts/stale_refs.py --old "OLD_FIGURE" --old "OLD PHRASE" --also <sibling-skill-path> [-i]
```

`<skill>` is this skill's own directory (its canonical source, or the installed symlink to it).

Every hit lands in one class, counted separately, so history is excluded by rule rather than by eye:

- **`active`** — a live statement of the old value. Zero is the target; exit 1 while any remain. Fix each, or frame it as history ("was", "previously", a dated line).
- **`history-path`** — `CHANGELOG*`, `archive/`, `.remember/`, snapshots, source captures, backups.
- **`history-dated`** — under a dated heading (`## 2026-09-20 session`), on a line starting with a date, or carrying an as-at / superseded marker. Spot-check a few: a live sentence that happens to sit
  under a dated heading is still live.
- **`history-superseded`** — a document whose top carries a supersession banner (`> **Superseded <date>** by …`, Step 3 rule 7). A dated report with the old figure and **no** banner stays `active`:
  give it the banner (Tier 2) rather than editing its figures.
- **`generated`** — `.ai-context/`, `graphify-out/`: regenerate in Tier 5, never edit.

Without the script, the fallback is `grep -rn` per root with `grep -v` for each history path above — and then the dated sections are still yours to judge by eye.

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
| **The change is a decision with no register entry** | It still reaches the reader-first page (Tier 3). A rule recorded only in `AGENTS.md` or `.archcore/` is invisible to someone who opens ARCHITECTURE first |
| **A sibling skill restates the fact** | Fix it in that skill's canonical source, bump its version and changelog; never edit an installed copy. It is another repo: commit it there separately, and only when asked |
| **No read access to the system of record** | Report the objects you could not read back as not done; do not mark the tier complete |
| **The project names no writer for the system of record** | Report the stale objects and ask the operator; do not write with an admin account by default |
| **A parent duty may or may not be triggered** | Quote it and say which way you judged it on the `Duties:` line, so the operator can correct the call |

---

## Step 6 — Final Checklist

Check only what exists in this project (skip missing files without marking):

- [ ] **Every script reasoned about individually** — one line each on why the change does or does not affect what it computes, asserts or prints. Not satisfied by a clean Step 4 grep
- [ ] Script/data files fixed
- [ ] Live system of record read back — descriptions and notes of the objects the change touched
- [ ] Generators checked, not just their output — a generated file re-emits the old model on every rebuild
- [ ] justfile / task runner updated (if stale)
- [ ] Current report routers updated
- [ ] Dated reports updated or superseded
- [ ] Every operator decision in this change reaches the reader-first page (ARCHITECTURE "Key decisions"), register or not
- [ ] Skill hard safety rules updated
- [ ] Skill references updated — this project's skills **and** every sibling skill package it invokes
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
- [ ] Stale-reference sweep has zero `active` hits across the project and its siblings (Step 4)
- [ ] Parent governance reviewed, and every triggered duty on the `Duties:` line done or reported as not done

---

## Tool hazards

- **The markdown rewrap tool rebuilds any `## Contents` section as a table of contents.** Never put a folder index or file list under `## Contents`; use `## Index`. A list written there is erased.
- **An unquoted heredoc (`<<EOF`) runs every backticked word as a command.** Write markdown with `<<'EOF'`, or with the Write tool, and read the result back.
