# Residual risks after the `<YYYY-MM-DD>` staleness audit

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

> Place this in the project's session-anchor file (`SCRATCHPAD.md` or equivalent), not only in the report. It has to be where the next session looks first.

These are stated because the audit did **not** resolve them, and **a clean check run must not be read as saying otherwise.** A passing suite means the copies agree; it says nothing about whether the
originals are true.

---

## 1. Unverified inputs still in use

Anything feeding a decision whose provenance is `ESTIMATED`, `UNVERIFIED` or `CONTESTED`.

| Input | Where | Label | What would settle it |
|---|---|---|---|
| `<value>` | `<file>` | `<token>` | `<the specific record or quote needed>` |

> State the consequence, not just the fact: *"this is the closest-to-viable candidate and its purchase price has never been checked."*

## 2. Reconstructed rather than recovered

Content rewritten after loss, accurate in substance but **not the original wording**. Each is labelled as such **in the file itself**, not only here.

| Artifact | What was recoverable | What was reconstructed |
|---|---|---|

## 3. Unset parameters

Decisions the project has acknowledged but not made. **Not stale — undecided**, and must not be silently treated as having a value.

| Parameter | Owner / reference | Consequence of it being unset |
|---|---|---|

## 4. Structural limitations

Cases where a tool or schema **cannot** comply with a rule the project now holds. Declared in the artifact itself, not only here.

| Artifact | Limitation | Why not fixed now |
|---|---|---|

## 5. Thin evidence

Figures resting on fewer observations than the weight placed on them.

| Figure | Records behind it | Weight it carries |
|---|---|---|

## 6. External facts not verifiable from inside the project

Per `patterns/completeness-verification.md`: market prices, regulations, vendor terms, third-party behaviour. The audit verified the **label and as-at date**, not the fact.

| Claim | As at | Re-check when |
|---|---|---|

## 7. Errors made during this audit

**Own them here.** An audit that reports only other people's mistakes is not an audit, and the next reader calibrates on whether this section exists.

| What | Impact | Resolution |
|---|---|---|
| `<mis-citation / destroyed work / wrong claim>` | `<what it affected>` | `<corrected where, or still outstanding>` |

---

## Scope of this run

- **Covered:** `<subtrees / file classes>`
- **Not covered:** `<what, and why>`
- **Check count:** `<before>` → `<after>`
- **What a passing run does and does not prove:** the copies agree and every checkable claim was verified against its source; it does not establish that any external fact is still true.
