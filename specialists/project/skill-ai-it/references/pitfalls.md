---
Title: skill-ai-it reference: pitfalls observed in practice
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-14
Summary: >-
  Pitfalls observed in practice; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: pitfalls observed in practice

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Pitfalls observed in practice

**Path references in prose are tried against the stating file's folder first, then the project root.** The governance checker extracts backticked spans and markdown link targets and reports a
reference as broken only when it resolves by neither route. So a cross-project reference like `../../health/` in a project that is a direct child of the target's parent fails both ways, where
`../health/` succeeds — and a root-level file differs from one inside a subfolder, because `../.archcore/...` resolves from `decisions/` but not from the project root. Write each reference so it
resolves by one of the two routes, and confirm with the checker rather than by eye.

**A document describing a broken reference is itself a broken reference.** The checker reads the whole surface, including open-items, changelog prose and roadmap tables. Quoting a bad path in order to
explain it re-introduces the failure, and this bites twice in a row if the first fix is written in prose rather than as the corrected path. Describe the defect in words; quote only paths that resolve.

**Never hand-edit a managed block to make a check pass.** The managed navigation block is canonical and is replaced wholesale on the next upgrade, so any local edit is lost. When it names a file the
project legitimately does not have (`ARCHITECTURE.md`, `roadmap.md`, `memory-bank/*`, `Taskfile.yml`), register the path in `CONDITIONAL_PATHS` with a per-entry reason — that is the sanctioned escape
hatch, and it keeps the exemption reviewable instead of silently ignored.

**Recipe interpreters must come from a task-runner variable, never typed inline.** A literal `uv run --with pyyaml python3 ...` in a recipe trips the interpreter-pinning check even though it is
already uv-routed. Bind it to a variable and interpolate, and keep one variable per dependency set so stdlib-only recipes do not resolve a dependency they do not use.

**Leave a registry empty rather than filling it with plausible entries.** Each `COUNT_CLAIMS` / `CONSTANT_SURFACES` entry asserts a real comparison, so a wrong entry claims coverage the project does
not have. An empty registry contributes zero assertions and reads honestly as "not covered yet". When a fact is already enforced executably by a test, say that in the comment instead of duplicating
the assertion in prose.

**Agents may be unable to write `AGENTS.md`.** Some host agents treat agent-instruction files as protected and require explicit user approval. If a write is refused, do not route around it through a
shell, a script or a direct file edit — leave the edit pending, report it, and let the checker keep failing on it. A green check bought by an unapproved edit is worse than a red one.

**The Markdown wrap and contents hook runs on Write and Edit only, and reflows the whole file** (learned 2026-10-10/11 in unified-network-controller). An edit
made from a shell (sed, a heredoc, a script) does not trigger it, so the file is left as written: wrap it yourself and run the checker. An Edit or Write
triggers it, and it reflows every paragraph of the file, not just the one touched: it has rewrapped tables, split a path across table rows (failing the
split-path check) and joined two managed-block marker comments onto one line. For a governed file with tables or managed blocks, edit through a script with
a whitespace-tolerant match and an abort guard, then run the checker; restore from git if a hook pass damaged it.

**A rule that says "invoke skill X before Y work" is not followed under load; enforce it with a hook** (learned 2026-10-13, unified-network-controller). An agent
did platform work for hours without invoking the platform skills its AGENTS.md required, so no write-back happened. A PreToolUse hook in the project's
`.claude/settings.json` (`scripts/agent_hooks/require_skill.py` there, map `scripts/registries/skill-domains.json`) reads the session transcript for Skill
calls and refuses an Edit, Write or writing Bash command on a skill-owned path until the owner was invoked (exit 2, reason on stderr). Check Bash only when
it names an owned path and writes, or reads get blocked; let the hook pass on its own errors, and give a session-level off switch. Observed: a project
`.claude/settings.json` created mid-session took effect at once in Claude Code (the hook blocked the next matching call), with no restart.

**`just check` passes on files git does not track yet (2026-10-14, smc-resiliency bootstrap).** `doc_freshness.py` scans tracked files, so a new project's
AI_NAVIGATION.md and two moved plans without a header summary passed `just check`, then failed the pre-commit hook once staged. Before the first commit of
new or moved files, stage them (or `git add -N`) and run the check again; the template AI_NAVIGATION.md now carries a header for this reason.

**The navigation upgrade re-serialises `context-map.yaml` and drops its comments (2026-10-14, smc-resiliency refresh).** When the `update_rules`
merge adds a rule, the upgrader warns "re-serialised the whole file" and writes it back without comments or quoting, so the line diff is
hundreds of lines (532 there) while the real change was one version key and one rule. The lost lines included the file's purpose header, which the
header standard requires. After applying: `just nav-check-context-map`
(`scripts/navigation/yaml_key_diff.py`) compares the old (`git show HEAD:./context-map.yaml`) and new files by key and lists the comments lost; put the
purpose header and any rationale comments back by script. A lost `# skill-ai-it-version:` comment is expected: the key replaces it.

**A pack bootstrapped by hand tends to write `.archcore/` decisions as `accepted`.** Building skill-coder (2026-10-19), the agent wrote an ADR and a rule
straight into `.archcore/` during bootstrap and marked them `accepted`, because the operator had just decided them in chat. That skips `promote`, the only
mode that writes Archcore content, and the operator's authorization it requires ([../patterns/archcore-routing.md](../patterns/archcore-routing.md)). It
surfaced only when that pattern's review date fell due and was read. In bootstrap, list the decisions as promotion candidates and ask; a decision made
in chat is a candidate until the operator approves its promotion. Re-read `.archcore/` before editing it after a gap: a parallel session added seven
documents to the same folder within the hour.

**`promote` deletes the candidates file but leaves the routing that names it (2026-10-19, skill-drawio and skill-coder).** After promotion both packs'
`context-map.yaml` still listed `ARCHCORE_PROMOTION_CANDIDATES.md` in `authority_order` and the `planning` and `governance` routing lists, and
`repomix.config.json` still included it; `just check` passed because the name sits in `CONDITIONAL_PATHS`. In the same pass as the delete: drop the
`authority_order` entry, replace the routing-list entries with `.archcore/index.guide.md`, drop the repomix include, and remove the promoted folders
(`.archcore/adr`, `.archcore/rules`) from `CONDITIONAL_PATHS`. Keep `promotion_rules.archcore.candidates_report`: it names where the next refresh writes.

**`nav_upgrade_dry_run` exits 2 when changes are pending (2026-10-20, smc-resiliency).** `upgrade_navigation_control_layer.py` exits 0 when
nothing would change, 2 when it would change files and 3 when a change needs manual review; `just` reports exit 2 as "recipe failed". Read the
"Changed files" line, not the exit code: on 2026-10-20 it was the template recipes' rename to kebab-case, which `govern` then applied.
`govern` also stops on any uncommitted governed file, so a refresh after a working session starts with a commit (ask; never `GOVERN_ALLOW_DIRTY` unasked).

```python
# skill-ai-it scripts/navigation/upgrade_navigation_control_layer.py (end of main)
final_changed = bool(report_data["changed_files"])
if report_data.get("requires_manual_review"):
    sys.exit(3)
elif final_changed:
    sys.exit(2)
else:
    sys.exit(0)
```

**A promoted document's title with a colon breaks `archcore status` (2026-10-27, skill-goal-guard promote).** Titles such as `D1: one apn repository` are invalid
unquoted YAML, and archcore reports "invalid YAML in frontmatter"; it also flags every tag used only once as a possible typo, a few per run. Quote every `title:`
and give the documents a small shared tag vocabulary (decision, governance, contract, procedure, plus a few domain tags) before running `archcore status`.

```python
# skill-goal-guard promote, 2026-10-27: quote titles once, for every promoted document
t = re.sub(r'^title: (?!")(.+)$', lambda m: 'title: "' + m.group(1).replace('"', '\\"') + '"', t, count=1, flags=re.M)
```

**A "folder readme indexes its folder" catalog rule must skip the project root (2026-10-27, skill-goal-guard governance checker).** The catalog check treated a
file as listed when its folder's `readme.md` was linked; the root readme is always linked, so every root file passed. The checker's own negative test (a stray
root file) caught it, and the fix then found two real gaps (`AI_NAVIGATION.md`, `context-map.yaml`). Write the negative test first for every coverage rule.

```python
# skill-goal-guard scripts/govcheck/checks/catalog.py (commit 8f76730)
if not covered and (path.parent == root() or (path.parent / "readme.md").resolve() not in linked):
    fail("catalog", f"{config.CATALOG} does not list {rel(path)} (link it, its folder, or its folder's readme.md)")
```

**Freshness reads only tracked files, so the first commit of a bootstrap can raise new findings (2026-10-27, skill-goal-guard).** `doc_freshness.py` scanned
`context-map.yaml` only after it was committed, then failed it for a header with no summary line. Give every file the bootstrap creates its header summary
before the first commit (`context-map.yaml`: one `#` line naming what it is), and run `just check` again after that commit.

**Several projects under one umbrella need a single route for cross-project messages (learned 2026-10-29, harvest of a multi-project
workspace root).** Projects that write into each other's SCRATCHPADs drift and collide with live sessions. The arrangement that held: spokes
address only the hub, never each other; one tool delivers, writing only between per-project markers with compare-and-swap writes and a
settle window, and gives each item an id it looks for (including in rotated history) before delivering; the hub keeps a register of
directives, and a directive closes only when every recipient has ticked it. An item marked sent but now missing is reported, never re-sent.
The mechanics are skill-coder design pattern P-41; the governance point is one route and a register that knows who has acted.

**Route facts by class, or two projects describe one fleet two ways (learned 2026-10-29, same workspace root).** Device, firmware, access
and fleet facts belong to the domain skill pack; site facts and decisions belong to the project. The rule that keeps them apart: invoke the
domain pack before answering, write a confirmed device fact back to the pack's references in the same session, and have projects cite the
pack rather than restate it. The pack's write-back contract binds once its domain is touched, invoked or not; the hook above enforces the
invocation half.
