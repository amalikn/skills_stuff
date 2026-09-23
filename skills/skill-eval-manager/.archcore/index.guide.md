---
title: Archcore index
type: guide
status: accepted
tags: [index]
provenance: written by skill-ai-it promote on 20260923_1311; supersedes ARCHCORE_PROMOTION_CANDIDATES.md
---

# Archcore index

Durable project truth for `skill-eval-manager`. This index is the entry point: it says what each document governs, what is deliberately not here, and how to propose another.

Every content document below carries `status: accepted`, ratified by the operator on 20260923_1331 after the 20260923_1311 promotion pass. They are therefore **authoritative**: under the source
priority in [AI_NAVIGATION.md](../AI_NAVIGATION.md), accepted `.archcore/` documents outrank `AGENTS.md`, `SKILL.md` and every other surface in this package. Where one of them disagrees with
prose elsewhere, the document wins and the prose is the thing to correct.

A new document starts at `status: proposed` and is ratified deliberately, never automatically. Supersede rather than rewrite an accepted one: set the old document to `status: superseded` with a
pointer to its replacement, so the reasoning that was once agreed stays readable — the same discipline
[append-only-history](rules/append-only-history.rule.md) imposes on observations.

## Decisions

| Document | Governs |
|---|---|
| [skill-not-platform](adr/skill-not-platform.adr.md) | Why this is a skill and not an executor or platform. The boundary every scope question resolves against |
| [split-expired-and-invalidated](adr/split-expired-and-invalidated.adr.md) | Why a stale verdict names its cause, and why the two causes are never merged |
| [defer-basis-hashing](adr/defer-basis-hashing.adr.md) | Why `validity.basis` is reserved but not implemented in v0.1, and what triggers revisiting it |
| [manual-executor-first-class](adr/manual-executor-first-class.adr.md) | Why a procedure is a valid executor, and where the safety boundary lives instead |

## Rules

| Document | Governs |
|---|---|
| [evidence-rank-floor](rules/evidence-rank-floor.rule.md) | Lower-ranked evidence never proves a higher-ranked claim |
| [append-only-history](rules/append-only-history.rule.md) | History is append-only, corrections supersede, reports are derived |
| [recorded-verdict-set](rules/recorded-verdict-set.rule.md) | The five recorded verdicts, and why three of them are not system failures |
| [refuse-and-ask](rules/refuse-and-ask.rule.md) | When to stop and ask rather than record a result that looks valid and is not |

## Specs

| Document | Governs |
|---|---|
| [eval-definition-contract](specs/eval-definition-contract.spec.md) | The portable contract: what every eval definition must carry and why |
| [derived-states](specs/derived-states.spec.md) | How `stale` and `not_evaluated` are derived at read time |
| [falsifiability-methods](specs/falsifiability-methods.spec.md) | The six permitted methods as a closed set |

## Deliberately not promoted

Carried out of `ARCHCORE_PROMOTION_CANDIDATES.md` before that file was deleted. Without this table, the next promotion scan re-proposes the same rejected candidates.

| Item | Why not |
|---|---|
| Markdown column rule, `YYYYMMDD_hhmm` naming, symlink-not-copy install discipline | Already governed by the global and parent `AGENTS.md`. Promoting them would duplicate upstream policy |
| Shipped scripts stay standard-library only | Local to this repo and already stated in [AGENTS.md](../AGENTS.md). Belongs there, not in cross-project durable truth |
| Rendering and re-rendering a scorecard, as an operating guide | A stable procedure, but no consuming project has exercised it yet. Promote once one has, so the guide records real practice rather than intent |
| The v0.2 deferred set | A waiting list, not an approved plan. Promote to `plans/` only if and when v0.2 is scheduled. The one part already decided — reserving `validity.basis` — is promoted as an ADR instead |
| The six numbered operator decisions | Open questions, not decisions. They live in `SCRATCHPAD.md` until answered. Promote the answer, never the question |
| `CHANGELOG.md` entries | History, not a truth source. Excluded by promotion policy |
| Example suites and their reports | Fixtures and derived output. Their invariants are already executable via `just validate-all` and `just check`; restating them in prose would be a second, weaker copy |

## Proposing another document

1. State the candidate and its source file in `SCRATCHPAD.md`.
2. Check it against the table above — a rejected candidate needs a reason the rejection no longer holds, not a second attempt.
3. Check it is not already enforced executably. A fact `validate_suite.py` or `check_governance.py` already asserts does not become truer in prose, and the prose copy is what drifts.
4. Write it as `<slug>.<type>.md` with `title`, `type`, `status`, `tags`, and `provenance` frontmatter. `archcore status` rejects any other filename shape.
5. Add a row to the matching table above. `scripts/check_governance.py` fails until the document is indexed here.
