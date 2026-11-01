---
Title: External research index
Category: index
Status: current
Authority: local-supplement; the four reports themselves are external and unverified
Scope: Four web-research reports on tools and models for kc, supplied by the operator, with the points to check before relying on them
Last reviewed: 2026-11-02
Summary: Index of four verbatim external reports, where they disagree, and what to explore next.
---

# External research index

Supplied by the operator on 2026-11-01 from the research prompt in that chat, for exploring in a later chat. Each report is verbatim below its front matter. Nothing here is verified by this pack; our own
report, which did open sources, is `skills-data/skill-knowledge-curator/research-20261101/foss-accuracy-options-20261101_2335.md`.

## Reports

| # | File | Leads with | Evidence it claims |
| --- | --- | --- | --- |
| 1 | [Deterministic filter and local routing](external-research-1-deterministic-filter-and-local-routing-20261102_0000.md) | Rule filter, a small Ollama model, cleanlab | Says VERIFIED_PRIMARY; check it |
| 2 | [Cleanlab, NLI, truth discovery](external-research-2-cleanlab-nli-truthdiscovery-20261102_0000.md) | cleanlab, cross-encoder NLI, status rules | Mixed labels |
| 3 | [Status, lineage, NLI gate](external-research-3-status-lineage-nli-gate-20261102_0000.md) | Status detector, NLI gate, lineage grouping, ssbc | Mixed labels; has build scripts |
| 4 | [Verified limits and process candidates](external-research-4-verified-limits-process-candidates-20261102_0000.md) | Rule filter, root grouping, source-backed resolver | Says it opened no primary source |

## Read these with care

- **All four predate the triage result.** They use 27.5% precision and 66.7% recall. Measured since: `kc triage` built, precision of kept conflicts 37.5%, clears 92.5% right, recall 51.1%. Rule filtering is no longer untested: it fell far short of "100% of banner noise" with nothing real lost.
- **A figure was misread.** Reports 1, 3 and 4 say 10 of 11 false positives share one cause, and report 2 is vague. Our 10 of 11 are real conflicts sharing the `mcp-data` cause. Plans built on the misreading should be rethought.
- **Reports disagree, and these need checking at the source:**

| Point | Report 1 | Report 2 | Report 3 | Report 4 | Our research |
| --- | --- | --- | --- | --- | --- |
| cleanlab licence | MIT | Apache-2.0 | Apache-2.0 | Not checked | Check |
| cleanlab on 50 labels | Defer until 50 | Rank 1, works | Rank 8, wrong fit | Needs over 200 | Not sound on 40 verdicts |
| NLI cross-encoders | Unstable on 3.14 | Rank 2 | Rank 2, 16% to 89% with an LLM judge | Not ready | 16.0% alone; rank only, never a gate |
| truthdiscovery licence | Not covered | GPL-3.0 | None listed | Not checked | Check |
| Local LLM | Small Ollama model | For hard cases | Not needed | Optional verifier | Hard cases only |

- **Names to confirm before any install:** the Ollama tag in report 1, `ssbc`, `cavaquinho`, `consistency-checker`, `model-shunt`, `Lynkr`, DocChecker, GVD, FineCat models. Any benchmark figure needs its primary source. Code in the reports is untested; for example report 1's fallback returns "no conflict" on any failure, which would hide errors.

## To explore next

1. Check the disagreements above at their primary sources.
2. Whether ssbc abstention (report 3) fits our 80 verdicts, and an NLI gate as a ranking signal on them.
3. Lineage grouping (report 3) and root grouping (report 4) against research item B3, `kc roots`.
4. The canonical registry and citation-constrained verifier (report 4) against `kc aliases` and B4, `kc verify`.
