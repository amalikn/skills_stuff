Title: Archcore Index — skill-cambium
Category: durable-truth-index
Status: current
Last reviewed: 20260917
Summary: Index of skill-cambium's 6 accepted durable decisions, rules, and contracts, with the never-promote list carried out of the deleted candidate queue.

# Archcore — skill-cambium

Durable pack truth: decisions that are settled, rules that are enforced, contracts other work must satisfy. Proposed 20260917 by `skill-ai-it promote` from `ARCHCORE_PROMOTION_CANDIDATES.md`
(generated the same day during a `refresh` run), which is now deleted — it was a proposal queue, not a record.

**All 6 documents below were ACCEPTED by the operator on 20260917**, the same day they were proposed. They are now the highest-authority statement of what this pack has decided per
`AI_NAVIGATION.md`'s source-priority list. An accepted document is not immutable — supersede it in place with a dated banner naming what replaced it and what still stands, rather than deleting it,
since the superseded reasoning is usually the part a later reader needs.

## Contents

- [Decisions](#decisions)
- [Rules](#rules)
- [Contracts](#contracts)
- [Never promoted, and why](#never-promoted-and-why)
- [Proposing another](#proposing-another)

## Decisions

| Document                                           | Governs                                                          |
| -------------------------------------------------- | ---------------------------------------------------------------- |
| [Separate pack from skill-smc](adr/adr-separate-pack-from-skill-smc.md) | Why this pack exists independently of skill-smc                  |
| [Vault reference file avoids OPA-blocked path words](adr/adr-vault-file-avoids-opa-blocked-words.md) | Why `references/02_device-access-and-vault.md` is named as it is |

## Rules

| Document                                           | Enforced by                                                                                                                                     |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [Vault reference convention, never plaintext values](rules/rule-vault-reference-convention.md) | Operator review only — no automated check yet; a real candidate is a `check_governance.py` grep for the blocked words appearing in a tracked    |
|                                                    |   path, not just content                                                                                                                        |
| [Cambium/SMC cross-pack boundary](rules/rule-cambium-smc-cross-pack-boundary.md) | Operator review only; enforces the ADR above                                                                                                    |
| [Manifest version discipline](rules/rule-manifest-version-discipline.md) | Partially automated 2026-09-17: `scripts/check_governance.py`'s `check_manifest_freshness` enforces `updated_at` is not older than the latest   |
|                                                    |   `CHANGELOG.md` entry. Still operator review only for the version-bump-per-change and no-duplicate-version-number parts of the rule            |

## Contracts

| Document                   | Defines                                                  |
| -------------------------- | -------------------------------------------------------- |
| [Specialist pack file roles](specs/spec-specialist-pack-file-roles.md) | Role and authority of every governance file in this pack |

## Never promoted, and why

Carried out of the candidate queue before it was deleted, so a future `skill-ai-it refresh` does not re-propose these.

| Item                                                             | Why not                                                                                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `AGENTS.md` naming convention bullet (`<slug>-YYYYMMDD_hhmm.md`) | Restates the parent/global `AGENTS.md` markdown-naming policy verbatim — already governed upstream.                          |
| `AGENTS.md` "Keep CHANGELOG.md current" bullet                   | Generic housekeeping instruction, not a durable project-specific rule or decision.                                           |
| `SCRATCHPAD.md` "Open items" and "Next actions"                  | Transient working-session state, not marked `KEEP`, and inherently time-bound.                                               |
| `CHANGELOG.md` (entire file)                                     | History/corroboration only — never a direct promotion source.                                                                |
| Spec/plan candidates                                             | None existed at promotion time — no stable schema/interface contract or accepted phased plan was in any governance file yet. |

## Proposing another

1. Write the candidate into the source it belongs to first — `AGENTS.md`, `SCRATCHPAD.md` (marked `KEEP`), or a reference file.
2. Run `/skill-ai-it refresh` to regenerate a candidate queue (`ARCHCORE_PROMOTION_CANDIDATES.md`), or add the document here directly with a provenance header, starting at `status: proposed`.
3. Apply the test: would it still read as true after the next real device-access/inventory-extraction session? If not, it belongs in `SCRATCHPAD.md` instead.
4. Avoid the OPA-blocked path words in every filename — see `adr/adr-vault-file-avoids-opa-blocked-words.md`.
