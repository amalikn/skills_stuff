# Evidence integrity

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

The rules governing **inputs**, as distinct from the arithmetic performed on them. This is where the expensive defects live, in every domain, because an internally consistent system will carry a wrong
input all the way to a confident conclusion without a single check firing.

## Contents

- [The core claim](#the-core-claim)
- [1. Both sides of a comparison must describe the same population](#1-both-sides-of-a-comparison-must-describe-the-same-population)
- [2. Record count is mandatory](#2-record-count-is-mandatory)
- [3. Filter before aggregating, never at display time](#3-filter-before-aggregating-never-at-display-time)
- [4. A search result is not evidence until verified](#4-a-search-result-is-not-evidence-until-verified)
- [5. Label the input, at the input](#5-label-the-input-at-the-input)
- [6. Report the gap; never fill it with an estimate](#6-report-the-gap-never-fill-it-with-an-estimate)
- [What is and is not automatable](#what-is-and-is-not-automatable)

---

## The core claim

**Internal-consistency checking cannot detect a wrong input, and a mature project will mistake one for the other.**

The evidence: a project ran 550+ governance checks, repeated coherence passes, and threshold propagation across a dozen registered surfaces. All of it validated that documents **agreed with each
other**. They agreed perfectly, twice, about purchase prices nobody had checked — one derived from a single observation, one never checked at all and later found to be less than half the real figure.
Both produced confident, precise, wrong recommendations that survived every check that existed.

The six rules below each trace to a specific way that happened.

## 1. Both sides of a comparison must describe the same population

Whenever you compare two figures — cost against price, before against after, treatment against control, this quarter against last — **both sides must be filtered identically**.

The asymmetry is not random. It **always flatters**, because the side you filtered carefully is the side you were paying attention to, and the unfiltered side silently includes everything cheap,
everything old, everything out of scope.

The instance: one side of a margin was carefully matched to a specific model generation and build window. The other was a substring match on a model name across every generation. The resulting margin
described no car that exists.

**Check:** for every comparison, state the filter applied to each side. If they differ, the comparison is invalid until they do not.

Domain translations: eval set versus training distribution; this month's incidents versus last month's under a changed definition; a benchmark on different hardware; a cost from one contract period
against a price from another.

## 2. Record count is mandatory

**A figure without a count is not a measurement.** A single observation may shortlist something; it may never clear a decision gate.

The reason is not merely small-sample noise, it is **selection bias in the specific direction that hurts**: ranking candidates by the cheapest observed price, over thin noisy data, systematically
selects for measurement error. The winner is the one whose data was most wrong.

**Check:** every aggregate reports `n`. Any gate has a minimum `n` and states it. A field named `avg_*` holding a single observation is a defect regardless of the value.

The instance: a field named `avg_hammer_jpy` contained exactly one sale for every row, and two headline returns were built on it.

## 3. Filter before aggregating, never at display time

A quality filter applied when rendering is not a filter — the aggregate has already been computed over the unfiltered set.

**Check:** trace where the filter is applied relative to the aggregation. If the median is taken and *then* rows are hidden, the median is wrong.

Domain translations: excluding outliers in the chart but not the mean; filtering a dashboard view while the alert threshold reads the raw table; grade or quality floors applied to a display query but
not the summary.

## 4. A search result is not evidence until verified

A search returning results is not the same as a search finding what you asked for. This is the general "plausible answer with no signal that it is wrong" family, and it is the most common
automation-era defect.

The instance: a search for a model name returned **285 results across 12 pages**. Sanity-checking the text around each of the first 24 listings found **zero** containing the model name. The search had
silently fallen back to unrelated inventory — same page structure, same result cards, same confident total.

**Check:** verify a sample of results against ground truth before counting any of them. Where possible, make the verification part of the collection code, not a manual step — and say in the code's
docstring that the verification *is* the point, so nobody optimises it away.

Domain translations: an API returning 200 with an error body; a query matching on a fallback index; a log search matching a substring of a different field; an LLM returning a fluent citation to a
paper that does not exist.

## 5. Label the input, at the input

**A caveat in a document nobody re-reads does not discharge the obligation, while the number lives in a config everybody runs.**

This is the rule that would have prevented both originating defects. In each case the caveat existed — in documentation, in a scratchpad, in a memory entry — and it did not help, because the caveat
and the number lived in different files and only one of them was read at the moment of decision.

**Check:** every input feeding a decision carries a provenance token *in the same file as the value*, from a fixed vocabulary — for example `OBSERVED` / `REAL` / `ESTIMATED` / `UNVERIFIED` /
`CONTESTED` / `SEED`. Enforce presence, not a particular answer: **being honest about a guess passes; silence is the defect.**

**Then make the label print.** A provenance label that no code path surfaces is inert — the label existed and was invisible at the exact moment someone read the result. Verify by running the tool and
looking at the output, not by checking that the label is in the file.

## 6. Report the gap; never fill it with an estimate

When filtered evidence does not exist, the correct output is **"no qualifying records found"** — not a plausible number derived from unqualifying ones.

A sub-quality anchor produces an optimistic ceiling, not a real figure, and it will be quoted later without its caveat. The instance: two candidates whose only price anchors were below the project's
own quality floor "passed" gates on numbers that described a different, worse item than the one that would actually be bought.

**Check:** an aggregate computed over zero qualifying records must return an explicit gap, and a gate must treat a gap as a failure rather than a pass.

## What is and is not automatable

Be honest about this in whatever you write, because overstating enforcement is itself a staleness defect waiting to happen.

| Rule | Automatable? |
|---|---|
| 2 — record count present | **Yes** — assert `n` exists and meets a floor |
| 3 — filter before aggregate | **Partly** — reviewable in code; not detectable from output alone |
| 4 — search verified | **Yes** — build verification into the collector |
| 5 — provenance label present | **Yes**, and label surfaced is testable by running the tool |
| 6 — gap reported | **Yes** — zero-qualifying-record path must be explicit |
| **1 — population matching** | **No.** Requires understanding what each side means |

**Rule 1 is not automatable and it is the one that has failed most often.** It is the reviewer's obligation, and it must be stated as such wherever the rules are recorded — an enforcement table that
quietly implies full coverage is worse than one that names its own gap.
