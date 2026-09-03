# Staleness audit — `<project>` — `<YYYY-MM-DD>`

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

> Final report shape. Lead with what could cost money; put reconciliation and method after. A reader who stops at the third paragraph should already know the worst of it.

**Scope:** `<whole project | subtree | --money-only>`
**Standard:** would a careful reader be misled — not "does the suite pass"
**Validation:** `<N>` checks before → `<N>` after · `<suite state>`

---

## What was found that could cost money

Lead here. One paragraph per band-M finding: what it was, **whether it was latent or realised**, and the exact condition that makes a latent one real.

> **`<Finding>`.** `<What it was, in a sentence.>` **`<No filed figure was wrong / this was realised>`** — `<the proof, by re-running rather than reasoning>`. The exposure was **`<latent|realised>`**:
> `<the precise condition under which it bites>`.

**Never round a latent defect up to a realised one.** The next reader calibrates on you.

## Why it survived

The reusable part. A defect that passed every check for a long time says something about the checks, and that is worth more than the fix.

> `<e.g. the guard matched one word order; widening it immediately surfaced two more surfaces.>`

## What was corrected

| Area | Change |
|---|---|
| | |

## Coverage

```text
Total files in scope:            <N>
  Examined:                      <N>
  Exempt (reason stated):        <N>
  Out of scope (stated):         <N>
                                ----
                                 <N>   ✓ reconciles
```

Binary and tabular files (`.xlsx`, `.parquet`, `.csv`) were audited by provenance, schema and freshness-against-source — **not skipped for being ungreppable**. `<state which, and the verdict>`

## Claim verification

```text
Checkable claims:                <N>
  VERIFIED against source:       <N>
  MARKED-HISTORICAL:             <N>
  RESIDUAL (see register):       <N>
                                ----
                                 <N>   ✓ reconciles
```

## New checks, and proof they can fail

Each was negative-tested in both directions. **A check that never fires breaks nothing and passes forever.**

| Check | Defect it exists for | Negative-tested |
|---|---|---|
| | | ✓ red on `<injected defect>`, green on restore |

## Errors made during this audit

`<List them, or state plainly that none occurred.>` An audit reporting only other people's mistakes is not an audit.

## What this run does NOT prove

Every checkable claim is now verified, marked historical, or listed as residual. **That does not establish that any external fact is still true** — market prices, regulations, vendor terms and
third-party behaviour cannot be settled by reading the project. For those, the audit verified the provenance label and as-at date, so a reader knows what to re-check and when it was last checked.

## Residual risks

`<Pointer to the residual-risk register in the session-anchor file.>` Summarised: `<the one or two that matter most>`.

## Next actions

1. `<the highest-materiality unresolved item>`
2. `<…>`
