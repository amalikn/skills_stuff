# Supersession banners

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

Making a superseded fact visible **in the file a reader actually opens**, rather than only in the spec that records the supersession.

## Contents

- [The problem](#the-problem)
- [The three-part contract](#the-three-part-contract)
- [Point at the owner, do not restate it](#point-at-the-owner-do-not-restate-it)
- [Chains that run against the ordering heuristic](#chains-that-run-against-the-ordering-heuristic)
- [Banner placement](#banner-placement)
- [Templates that get copied](#templates-that-get-copied)
- [What not to do](#what-not-to-do)

---

## The problem

An append-only knowledge base is a deliberate and good design: a later document amends an earlier one, and the earlier text stays exactly as written so you can see what was believed on a given day.

The cost is structural. **`docs/03` still reads like a live instruction.** Nothing about opening it signals that its gate figures were replaced twice. A supersession recorded in a spec, a routing
table or a change log does not reach the person who opened `docs/03` — and that person is usually an agent, following the file it was routed to.

So the supersession has to live **in the superseded file**.

## The three-part contract

Every banner states three things. Omitting any one of them produces a specific, predictable failure.

### 1. What changed, when, and who owns the replacement

Dates matter because they let a reader reconstruct the sequence, and because a corpus usually has several supersessions layered on the same section.

### 2. What in this file **still stands**

**This is the part that gets left out, and it does the most damage when it is.** A banner that says only "this is superseded" reads as *ignore this document*, and takes correct content down with the
incorrect. Most superseded documents are mostly still right.

> **What in this file is NOT superseded and remains good practice:** the selection hierarchy (§1), the auction/condition logic (§3 — grade alone is not enough), the market-validation method (§4), the
> compliance-first search order (§5) and the first-import preference (§7).

### 3. A pointer to the live owner

Where the reader goes for the current answer, and — where a tool exists — the command that produces it. `just gate <preset>` beats any prose restatement, because it cannot go stale.

## Point at the owner, do not restate it

**Restating a threshold in a banner creates another surface to keep in sync**, which is the defect you are fixing.

The banner should say *"the gates are owned by `purchase-discipline.rule.md` and implemented in `just gate` — read them there"*, not *"the gate is now max($2,500, 15%)"*.

The exception is a **template at the point of use** (below), where the reader is about to act and cannot be sent elsewhere. Accept the extra surface there, and register it.

## Chains that run against the ordering heuristic

Most supersession in a numbered corpus follows *higher numbers win*. Some does not, and those are the dangerous ones because the heuristic will never find them.

The instance that motivated this section: `docs/03 §2a`'s gate text was superseded by an **`.archcore` rule** — a rule, not a higher-numbered document. An agent applying "check the later file" would
search `docs/04`…`docs/19`, find nothing on point, and conclude `docs/03` was current.

When you find one of these:

1. Register it explicitly in the supersession spec, **flagged as running against the heuristic**.
2. Mirror it in the human router and the machine-readable map.
3. State the operative rule in the agent-facing guidance: **never assemble a gate set from documents of different dates.** A half-set built from `docs/03` plus `docs/18` looks complete and is not.

## Banner placement

| Situation | Placement |
|---|---|
| Whole file superseded on one subject | Top of file, immediately after the `#` heading |
| Several sections superseded by different things | Top-of-file banner with a **table** — one row per section, naming what replaced each |
| One section superseded, rest current | Immediately after the affected section, not at the top |
| A single bullet or line | Strike it through in place and state the current one beside it |

The table form is worth reaching for early. It scales, it forces you to be specific about which section each supersession touches, and it reads as a map rather than a warning:

```markdown
| What this file says | Superseded by | When |
|---|---|---|
| `base margin ≥ 30%` as a gate (§2a, §2b) | Demoted to **advisory** (`docs/17 §5`) | 2026-08-09 |
| `landed cap $10,000` (§2a, §2d) | Raised to **$15,000** (`DM-17`) | 2026-08-10 |
| `target profit ≥ $2,500/car` (§2a) | Became a **dual** test (`docs/07` Q14) | 2026-08-11 |
```

## Templates that get copied

A template is not history — it is an instruction that will be followed. Treat it as code.

- **Amend at the point of use**, not only in a top banner. Strike the old line; state the current one directly beneath it.
- **Add a top banner too**, saying explicitly: *do not run a decision from a copy of this file made before `<date>`.*
- **Reconcile copies already taken.** Find them and give each the same treatment, noting what it additionally inherited — a copy usually carries more than one stale fact.

## What not to do

- **Do not delete the superseded text.** The reasoning is usually the useful part, and deleting it destroys the record of what was believed when a decision was made.
- **Do not rewrite the original to be correct.** That is not supersession, it is falsifying the record — and in an append-only corpus it breaks the one guarantee the design exists to provide.
- **Do not mark a whole document superseded because one section is.** See part 2 of the contract.
- **Do not write the banner only into the spec.** The spec is not what the reader opened.
- **Do not restate thresholds in the banner** unless it is a point-of-use template, and then register the surface.
