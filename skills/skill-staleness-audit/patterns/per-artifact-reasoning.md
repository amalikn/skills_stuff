# Per-artifact reasoning

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

Phase 4 in full: the pass that finds what a grep structurally cannot.

## Contents

- [Why this cannot be delegated to grep](#why-this-cannot-be-delegated-to-grep)
- [The method](#the-method)
- [The two prompts](#the-two-prompts)
- [Worked pass](#worked-pass)
- [Clearing an artifact is a real output](#clearing-an-artifact-is-a-real-output)
- [Generators need a second question](#generators-need-a-second-question)

---

## Why this cannot be delegated to grep

**A grep finds a stale string. It cannot find a stale assumption.**

Collapsing this phase into "did the Phase 1 greps hit it" is the observed failure mode, and it is seductive because a clean grep *feels* like completion. Five of the nine patterns in
`defect-taxonomy.md` produce no string to match. The two most expensive findings in the originating run were both in that category:

- A max-bid back-solved against a flat target. Nothing in the source said `$2,500` in a way any guard would flag — the constant was a legitimate default for a different question. **The defect was in
  what the output meant**, and only above a threshold that no preset in routine use crossed.
- A projection whose verdict line encoded a superseded gate *shape*. The wording was fine. The logic tested one limb of a test that now had two.

Neither would ever have surfaced from a phrase sweep, however thorough.

## The method

List **every** script, generator, data file and template in scope. Write **one line each** on whether the audited change affects what that artifact *computes, asserts, or prints*.

Skipping an artifact is fine. **Skipping the question is not.** The discipline is that every artifact appears in the output with a verdict beside it, including the boring ones — because "I looked and
it does not apply" and "I did not look" are different states, and only the first is an audit.

A useful accelerator: dump each artifact's docstring plus a signal scan for the values under audit, then reason over that table rather than opening twenty files. `scripts/stale_scan.py --signals`
produces it. The table tells you where to look; it does not answer the question.

## The two prompts

Ask both of every artifact:

### 1. Does it print or compute anything whose **meaning** changed, though its wording did not?

Catches: back-solves against changed floors, verdict lines testing an outdated rule shape, ratios whose denominator moved, thresholds passed as defaults.

### 2. Does it assume **continuity, completeness, or availability** that is no longer true?

Catches: a "steady state" row for a business line with a hard terminus; a projection assuming next year exists; a scan assuming a source still responds; a median over a population that no longer
matches the other side of the comparison.

The second prompt found, in an earlier pass on the same project, a break-even script printing an annual steady-state figure for a track whose regulatory pathway closes in 2028 — *"describes a year
that will not arrive"*. No stale string; the assumption was in the shape of the output.

## Worked pass

Abridged from the originating run — 22 scripts, all reasoned about, two findings:

| Artifact | Verdict |
|---|---|
| `run_scenario.py` | **FINDING.** `Max bid AUD` back-solved against a flat `target`, default 2500. Gate is dual since 2026-08-11. Below $16,667 landed they coincide; above, the ceiling is too |
|  |   generous — $3,805 on the camper preset. No stale string. |
| `verify_model.py` | **FINDING.** Docstring claims 39 checks; the two lists total 56; six other files claim 57. |
| `evaluate_candidate.py` | Clear. "The adopted gates **were** ≥30%…" is historical framing and correct. Implements the dual gate. |
| `breakeven_volume.py` | Clear. Already solves against the dual floor; already refuses a steady-state row for a terminal criterion. |
| `cashflow.py` | Fixed in Phase 2 — printed a single-limb gate into a filed artifact, and hard-wrapped generated prose, reverting wrap governance on every run. |
| `comparables_series.py` | Clear. Its `100000` is an odometer threshold, unrelated to the cap. |
| `auction_snapshot.py` | Clear. Its `15,000` is a docstring example. |
| `sevs_*.py` (5), | Clear. Touch no gate, verdict or cap. |
|   `fx_rate.py`, |  |
|   `cell_map.py`, |  |
|   `class_profiles.py` |  |

Note how much of that table is "clear". That is the expected shape, and the two findings are only trustworthy *because* the rest were examined rather than assumed.

## Clearing an artifact is a real output

Write the reason, not just the verdict. "Clear" is unfalsifiable; **"its `15,000` is a docstring example, not the cap"** can be checked by the next reader and corrected if wrong.

These lines belong in the change-log entry. They are what lets a future session skip re-deriving the same conclusions, and what makes a wrong clearance visible later.

## Generators need a second question

For anything that writes a file, ask additionally: **would running it now revert something?**

Run it. Diff. A clean diff proves the output is current; it proves nothing about the generator's assumptions. Read what it emits.

The cash-flow generator produced a byte-clean diff on its numbers while re-emitting both a superseded gate statement and an ~85-column wrap that undid the project's 200-column rule. The numbers were
never the problem.
