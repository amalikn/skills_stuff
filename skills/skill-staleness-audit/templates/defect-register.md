# Defect register — `<project>` staleness audit `<YYYY-MM-DD>`

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

> Working artifact for Phase 1. Write it to a scratch directory, not into the project. It is superseded by the audit report at Phase 7.

**Scope:** `<whole project | subtree | --money-only>`
**Standard applied:** would a careful reader be misled — not "does the suite pass"
**Baseline:** `<check count / test suite state at start>`

---

## Coverage accounting

Reconcile before hunting defects. See `patterns/coverage-manifest.md`.

```text
Total files in scope:            <N>
  Examined:                      <N>
  Exempt (reason stated):        <N>
  Out of scope (stated):         <N>
                                ----
                                 <N>   ✓ reconciles
```

| Class | Files | Verdict / exemption reason |
|---|---:|---|
| Agent governance | | |
| Routing / navigation | | |
| Durable decisions | | |
| Knowledge base | | |
| Process / runbooks | | |
| Code / scripts | | |
| Task runners | | |
| Structured config | | |
| Tabular / binary | | |
| Generated context | | |
| Evidence / captures | | |
| Archives | | Exempt — archives are *supposed* to contain superseded figures |

---

## Findings

Materiality: **M** = could cost money or mislead a third party · **H** = enforcement hole · **G** = governance drift. Ranked M → H → G. Every row cites evidence; a row that cannot cite belongs in the
residual-risk register instead.

| # | Mat | File:line | Defect | Evidence | Latent or realised? | Status |
|---|---|---|---|---|---|---|
| D1 | M | | | | | |
| D2 | M | | | | | |
| D3 | H | | | | | |
| D4 | G | | | | | |

**Latent vs realised** is a required column, not a nicety. A latent defect rounded up to a realised one destroys the report's credibility; a realised one softened to latent is worse. State the exact
condition under which a latent defect becomes real.

---

## Phase 4 — per-artifact reasoning

One line per artifact. "Clear" needs a reason; an unfalsifiable verdict is not a verdict.

| Artifact | Affects what it computes / asserts / prints? |
|---|---|
| | |

---

## Notes

- Anything found that is **not** a defect but is worth recording → residual-risk register.
- Anything found that is a defect **you introduced during this audit** → record it here like any other, and carry it into the report.
