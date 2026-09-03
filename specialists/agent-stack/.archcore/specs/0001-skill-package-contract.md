Title: Spec 0001 — Skill package contract
Category: design-contract
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: SKILL_STANDARD.md
Summary: Pointer to the authoritative standard: SKILL.md procedural, knowledge in references/, helpers in scripts/, templates in assets/.

# Spec 0001 — Skill package contract

## Contract

Authoritative text: [SKILL_STANDARD.md](../../SKILL_STANDARD.md). Summarised, not restated, so the two cannot drift:

Every skill package carries a `SKILL.md` that stays **procedural**. Detailed reusable knowledge goes in `references/`, deterministic helpers in `scripts/`, output
templates in `assets/`.

## Note

Individual `skills/*/SKILL.md` content is upstream-derived and is deliberately **not** promoted — promoting it would fork the library.
