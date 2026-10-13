---
Title: skill-ai-it reference: pitfalls observed in practice
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
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

