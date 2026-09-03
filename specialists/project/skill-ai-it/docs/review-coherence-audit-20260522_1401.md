# skill-ai-it — Coherence Audit Feedback

Date: 2026-05-22
Prepared by: Malik Ahmad
Scope: Full file-by-file review of the skill-ai-it package for coherence, completeness, and structural consistency.

---

## Overall Verdict

The package is **functionally solid but structurally drifted**. Today's session added significant capability (script inventory, Archcore init, CHANGELOG governance, ARCHITECTURE.md, mise templates) but didn't fully close the loop on all navigation surfaces. Six concrete drift gaps need fixing before next use.

---

## File-by-File Findings

### SKILL.md ⚠️ structural issue

**Biggest problem:** Phase 4 has no `Conditionally-created files` section. The CHANGELOG says ARCHITECTURE.md, CONVENTIONS.md, and ROADMAP.md were "restored" as conditional files, but they don't appear in the Phase 4 heading hierarchy. They are either:

- Genuinely missing (regression), or
- Buried inside `Always-created files` with conditional notes — wrong section name

The old `.bak` correctly separated `Always-created` vs `Conditionally-created`. That distinction matters — agents reading a flat `Always-created` section will try to create everything.

**Secondary structural issue:** `AI_NAVIGATION.md`, `context-map.yaml`, `repomix.config.json`, `.graphifyignore`, and `memory-bank/` all sit under the `Always-created files` heading but have their own conditional creation rules. The heading is now misleading. Rename it `File generation rules` or split it properly.

**Frontmatter description:** Likely unchanged from the `.bak` version — still says "Creates README.md, AGENTS.md, CLAUDE.md, and SCRATCHPAD.md always" without mentioning CHANGELOG.md (now always created) or the new operating modes (navigation-add, refresh, audit, promote). Update it.

---

### SKILL.md.bak ❌ should not exist

Old backup, not referenced anywhere. AGENTS.md maintenance boundaries say "Do not add runtime/cache/generated outputs to the skill package." Delete it.

---

### README.md ⚠️ package layout stale

The package layout tree is missing five actual files:

| Missing from README layout | Present on disk |
|---|---|
| `ARCHITECTURE.md` | Yes |
| `SCRATCHPAD.md` | Yes |
| `templates/mise.toml` | Yes |
| `templates/scripts-README.md` | Yes |
| `patterns/script-task-audit-checklist.md` | Yes |

The README tool stack section was updated but the layout tree was not. Anyone using README as the package map will get the wrong picture.

---

### AI_NAVIGATION.md ⚠️ context map incomplete

The context map table lists 13 files. Missing entries:

| File | Should be |
|---|---|
| `ARCHITECTURE.md` | High |
| `templates/mise.toml` | Medium |
| `templates/scripts-README.md` | Medium |
| `patterns/script-task-audit-checklist.md` | Medium-high |
| `SCRATCHPAD.md` | Low (ephemeral, but worth noting) |

The CHANGELOG says ARCHITECTURE.md was added to the navigation surface — but it's not in the context map table. That's a direct coherence failure against the changelog's own claim.

The "Script and Task Navigation" section was added (good), and the two "Audit package consistency" checklists differ slightly — one (in Task routing) has 5 steps, one (in Script and Task Navigation) has 6 steps. Duplicate section; pick one location or consolidate.

---

### context-map.yaml ⚠️ likely incomplete

Based on the codex_prompt_fix prescriptions (add CHANGELOG.md to authority_order, documentation routing, update rules), these changes should have been applied. The CHANGELOG confirms it. But the same new files missing from AI_NAVIGATION.md (mise.toml, scripts-README.md, script-task-audit-checklist.md) are also likely missing from context-map.yaml's include list and routing sections. Needs a targeted check.

---

### AGENTS.md ✅ good

Working rules were correctly updated with script inventory guidance (inspect mise.toml, .mise/tasks/, scripts/README.md; prefer cataloged tasks; treat uncatalogued scripts as unknown safety). Maintenance boundaries are clean. The preflight section is correct. No issues.

---

### CLAUDE.md ✅ clean

Thin wrapper, nothing stale. Fine.

---

### CHANGELOG.md ✅ well-structured

Entries are granular, cover the right changes, follow the append-only contract. One concern: the CHANGELOG says "Restored conditional templates for ARCHITECTURE.md, CONVENTIONS.md, ROADMAP.md" but those files aren't visible in SKILL.md Phase 4. If that entry is inaccurate, it erodes CHANGELOG trust as the authoritative ledger.

---

### ARCHITECTURE.md ✅ good

Package roles, flow diagrams, tool stack (Archcore, Graphify, Repomix), Script/Task Inventory Layer, runtime model, and repeat-safety model are all there. The Script and Task Inventory Layer section clearly articulates what each tool does and doesn't do. No issues.

One gap: `mise` isn't named in the tool stack section header alongside Archcore/Graphify/Repomix, only mentioned inside the Script Inventory Layer. Fine for now but worth noting.

---

### SCRATCHPAD.md ⚠️ partially stale

Open items that are already resolved:

- "Decide whether to implement script inventory / `mise tasks` support in `skill-ai-it`" — **decided and implemented** (templates/mise.toml + templates/scripts-README.md exist). Mark done or remove.

Still-valid open items:
- Apply refresh to OpenBB — pending
- Apply refresh to invoice-finance-analyst — pending
- Decide on `codex_prompt_fix_...md` and `.DS_Store` — pending (see below)

---

### codex_prompt_fix_skill_ai_it_changelog_governance.md ❌ should not be in package root

This is a one-time Codex session prompt used to drive the CHANGELOG governance integration. Its work is done. It's not referenced in any navigation file, AGENTS.md, or context-map.yaml. Leaving it here:

- Pollutes the package root
- Confuses agents reading the directory (what is this file's authority?)
- Contains proposed content that may differ from what was actually applied

The SCRATCHPAD explicitly flags it as needing a decision. Decision: **archive or delete**. If archival is preferred, move to `docs/` or `.archive/`.

---

### patterns/archcore-routing.md, memory-bank-structure.md, drift-audit.md ✅ good

These are guidance modules with clear scope. No issues observed.

---

### patterns/script-task-audit-checklist.md ✅ solid addition

Well-structured checklist covering discovery, catalog coverage, safety classification, inputs/outputs, idempotency, agent routing, and validation commands. Useful as an audit reference. No issues.

---

### templates/AI_NAVIGATION.md ⚠️ wording issue

The mandatory read order section says "Before editing **this skill package**, read:" — but this is a *target-project* template. That phrase is skill-package-centric language that leaked in. Should read "Before editing **this project**, read:".

Also: the mandatory read order includes `SKILL.md` as item 4. A target project won't have a SKILL.md. Replace with a project-appropriate entrypoint.

---

### templates/context-map.yaml ✅ mostly good

Has `{{PROJECT_NAME}}` placeholders, reasonable structure. Verify CHANGELOG.md appears in `authority_order` (per the fix that was supposed to be applied).

---

### templates/AGENTS-navigation-block.md ✅ fine

Clean managed-block template. The codex_prompt_fix said to add "Read recent entries in CHANGELOG.md" as step 3. Verify this was applied.

---

### templates/context-preflight.sh ✅ good

Covers Archcore check and auto-init. Fixed for Archcore and Graphify CLI compatibility per CHANGELOG. No issues.

---

### templates/mise.toml ✅ good, one note

Good structure: purpose comment, optional tool/env sections, example tasks with safety labels. The example Python version is `3.12` — global AGENTS.md policy says Python 3.14.4 default. Consider updating the example to `3.14` or adding a note that the version should match project requirements.

---

### templates/scripts-README.md ✅ solid

Task Inventory table, Safety Labels, Maintenance Rules, and preferred execution notes are all present. No issues.

---

## Cross-Cutting Coherence Issues

| Surface | Issue | Severity |
|---|---|---|
| SKILL.md Phase 4 | ARCHITECTURE.md/CONVENTIONS.md/ROADMAP.md invisible or missing | High |
| SKILL.md Phase 4 heading | "Always-created files" contains conditional items | Medium |
| SKILL.md frontmatter | Description stale vs current capability | Medium |
| README.md | Package layout missing 5 files | Medium |
| AI_NAVIGATION.md | Context map missing 4 new entries including ARCHITECTURE.md | Medium |
| AI_NAVIGATION.md | Duplicate "Audit package consistency" checklist | Low |
| templates/AI_NAVIGATION.md | "skill package" phrasing + SKILL.md in read order | Medium |
| SCRATCHPAD.md | Script inventory open item still listed as pending despite being done | Low |
| Package root | codex_prompt_fix file + SKILL.md.bak + .DS_Store present | Low |

---

## Priority Actions

1. **Verify SKILL.md Phase 4** — confirm ARCHITECTURE.md, CONVENTIONS.md, ROADMAP.md are present. If missing, restore the `Conditionally-created files` section from `.bak`. If present under "Always-created", fix the section heading.
2. **Update README.md package layout** — add the 5 missing files.
3. **Update AI_NAVIGATION.md context map** — add ARCHITECTURE.md + 3 new templates/patterns entries.
4. **Fix templates/AI_NAVIGATION.md wording** — "this project" not "this skill package"; remove SKILL.md from mandatory read order.
5. **Delete SKILL.md.bak and codex_prompt_fix file** — or move them into `docs/` if archival is preferred.
6. **Update SCRATCHPAD** — mark script inventory decision as done.
7. **Update SKILL.md frontmatter description** — reflect CHANGELOG.md as always-created and the five operating modes.
8. **templates/mise.toml** — update Python example version from 3.12 → 3.14 or add a version note.
