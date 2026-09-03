# Supersession banner templates

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

Copy, fill, place per `patterns/supersession-banners.md`. Every banner states three things: **what changed**, **what still stands**, and **where the live answer is**.

## Contents

- [A. Whole file, several supersessions](#a-whole-file-several-supersessions)
- [B. One section](#b-one-section)
- [C. A single line or bullet](#c-a-single-line-or-bullet)
- [D. A copy-me template](#d-a-copy-me-template)
- [E. A copy already taken](#e-a-copy-already-taken)
- [F. An accepted decision later contradicted](#f-an-accepted-decision-later-contradicted)
- [G. A chain running against the ordering heuristic](#g-a-chain-running-against-the-ordering-heuristic)

---

## A. Whole file, several supersessions

Place immediately after the `#` heading. The table form scales and forces specificity about which section each supersession touches.

```markdown
> **Every numeric gate and figure in §2, §2a and §2d is SUPERSEDED — file-level pointer added <DATE>.** The text stays as written because this corpus is append-only, but **do not run a decision from
> this file.** What reached it:
>
> | What this file says | Superseded by | When |
> |---|---|---|
> | `<old claim>` (§X) | `<new position>` (`<owner>`) | `<date>` |
> | `<old claim>` (§Y) | `<new position>` (`<owner>`) | `<date>` |
>
> The live values are owned by [`<owner path>`](<owner path>) and implemented in `<command>`. Read them there. **Do not reconstruct a rule by combining this file with a later one** — a half-set
> assembled from two dates looks complete and is not.
>
> **What in this file is NOT superseded and remains good practice:** `<§N — what>`, `<§N — what>`, `<§N — what>`.
```

## B. One section

Place immediately after the affected section, not at the top of the file.

```markdown
> **`<section>` is superseded — pointer added <DATE>.** `<what it says>` was replaced on `<date>` by `<what replaced it>` (`<owner>`, `<decision ref>`). Read the live value from
> [`<owner path>`](<owner path>) or run `<command>`.
>
> **The reasoning in this section still stands** — `<what remains valid and why>`. Only the `<figure / verdict / threshold>` moved.
```

## C. A single line or bullet

Strike in place; state the current value beside it. Do not delete.

```markdown
- ~~`<old claim>`~~ — **superseded <DATE>**, see `<owner>`. Current: `<new claim>`.
```

## D. A copy-me template

Two parts: a top banner **and** an amendment at the point of use. The top banner alone is insufficient, because the reader acts at the point of use.

```markdown
> **Gate text amended in place <DATE> — this file is a template that gets COPIED, so a stale figure in it is an operating instruction, not history.** `<Step N>` and `<the summary line>` originally
> read `<old text>`. That has been superseded: `<what changed, when, by whom>`. The current set is restated at the point of use below. **Do not run a decision from a copy of this file made before
> <DATE>.**
>
> The method above the decision rule — `<what the method is>` — is unchanged and still correct. What changed is only what the collected result is tested against.
```

At the point of use:

```markdown
5. **<Step name>:** <method, unchanged>
   - ~~`<old rule>`~~ — **superseded, see the banner at the top of this file.**
   - Current: `<new rule stated in full>`.
```

## E. A copy already taken

```markdown
> **This copy was taken from `<source>` BEFORE the <DATE> amendment — reconciled <DATE>.** Two things it inherited are no longer current, and both are decision rules rather than method:
>
> 1. **`<inherited rule 1>`** — superseded by `<what>` on `<date>` (`<owner>`). The section below now carries the current set.
> 2. **`<inherited rule 2>`** — `<what changed and why it matters>`. Read the note below as *what was believed on `<original date>`*, not as a current conclusion.
>
> The collection method is unaffected and the observations below stand as recorded.
```

## F. An accepted decision later contradicted

For decision records where acceptance froze a claim at the confidence it held that day. **Mark in place; never rewrite an accepted claim.**

```markdown
> **Figures here are as-at `<original date>` and have since changed; the decision has not** (note added `<DATE>`). `<What moved>`, so neither figure above is the live test — read the current values
> from `<owner>`.
>
> **The conclusion is unaffected and is if anything stronger:** `<why the decision survives the new figures>`.
>
> A decision record states what was adopted on its date; its figures are historical by design.
```

## G. A chain running against the ordering heuristic

Use where the replacement is **not** found by the project's normal ordering rule — for example a rule superseding a numbered document, so "later wins" never reaches it.

```markdown
> **This chain runs the other way from the rest.** `<this file/section>` is superseded by [`<owner>`](<owner>) — a **<rule / policy / spec>**, not a higher-numbered document — so the
> `<higher numbers win>` heuristic will never find it. Registered in `<supersession registry>`, `<router>` and `<machine-readable map>`.
```
