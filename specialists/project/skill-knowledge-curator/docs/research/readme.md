---
Title: External research index
Category: index
Status: current
Authority: local-supplement; the five reports themselves are external and unverified
Scope: Five web-research reports on tools and models for kc, supplied by the operator, with the points to check before relying on them
Last reviewed: 2026-11-05
Summary: Index of five verbatim external reports, where they disagree, and what to explore next.
---

# External research index

Supplied by the operator on 2026-11-01 and 2026-11-02 from the research prompt in that chat, for exploring in a later chat. Each report is verbatim below its front matter. Nothing here is verified by
this pack; our own report, which did open sources, is `skills-data/skill-knowledge-curator/research-20261101/foss-accuracy-options-20261101_2335.md`.

## Reports

| #   | File                                   | Leads with                                                           | Evidence it claims                                 |
| --- | -------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------- |
| 1   | [Deterministic filter and local routing](external-research-1-deterministic-filter-and-local-routing-20261102_0000.md) | Rule filter, a small Ollama model, cleanlab                          | Says VERIFIED_PRIMARY; check it                    |
| 2   | [Cleanlab, NLI, truth discovery](external-research-2-cleanlab-nli-truthdiscovery-20261102_0000.md) | cleanlab, cross-encoder NLI, status rules                            | Mixed labels                                       |
| 3   | [Status, lineage, NLI gate](external-research-3-status-lineage-nli-gate-20261102_0000.md) | Status detector, NLI gate, lineage grouping, ssbc                    | Mixed labels; has build scripts                    |
| 5   | [Source context and root cause](external-research-5-source-context-root-cause-20261102_0015.md) | Source-context gate, root-cause rollup, evaluation, retrieval shadow | Primary register; says nothing was run. Start here |
| 4   | [Verified limits and process candidates](external-research-4-verified-limits-process-candidates-20261102_0000.md) | Rule filter, root grouping, source-backed resolver                   | Says it opened no primary source                   |

## Read these with care

- **All five predate the triage result.** They use 27.5% precision and 66.7% recall. Measured since: `kc triage` built, precision of kept conflicts 37.5%, clears 92.5% right, recall 51.1%. Rule
  filtering is no longer untested: it fell far short of "100% of banner noise" with nothing real lost.
- **A figure was misread.** Reports 1, 3 and 4 say 10 of 11 false positives share one cause, and report 2 is vague; report 5 reads it correctly. Our 10 of 11 are real conflicts sharing the `mcp-data`
  cause. Plans built on the misreading should be rethought.
- **Reports disagree, and these need checking at the source:**

| Point                  | Report 1           | Report 2       | Report 3                         | Report 4          | Report 5                                  | Our research                       |
| ---------------------- | ------------------ | -------------- | -------------------------------- | ----------------- | ----------------------------------------- | ---------------------------------- |
| cleanlab licence       | MIT                | Apache-2.0     | Apache-2.0                       | Not checked       | Apache-2.0                                | Check                              |
| cleanlab on 50 labels  | Defer until 50     | Rank 1, works  | Rank 8, wrong fit                | Needs over 200    | Do not deploy                             | Not sound on 40 verdicts           |
| NLI cross-encoders     | Unstable on 3.14   | Rank 2         | Rank 2, 16% to 89% with an       | Not ready         | Shadow only                               | 16.0% alone; rank only, never      |
|                        |                    |                |   LLM judge                      |                   |                                           |   a gate                           |
| truthdiscovery licence | Not covered        | GPL-3.0        | None listed                      | Not checked       | Not covered; method rejected              | Check                              |
| Local LLM              | Small Ollama model | For hard cases | Not needed                       | Optional verifier | Existing LLM on hard cases; Ollama        | Hard cases only                    |
|                        |                    |                |                                  |                   |   not needed                              |                                    |

- **Names to confirm before any install:** the Ollama tag in report 1, `ssbc`, `cavaquinho`, `consistency-checker`, `model-shunt`, `Lynkr`, DocChecker, GVD, FineCat models. Any benchmark figure needs
  its primary source. Code in the reports is untested; for example report 1's fallback returns "no conflict" on any failure, which would hide errors.

Report 5 raises four points against our own work, to check first:

- **Our samples are not independent.** (Answered 2026-11-05 by `kc roots`: report decisions per cause.) All 15 real kept conflicts share one cause, so the 37.5% interval is too narrow as stated.
  Sample root groups, or report decisions per cause.
- **Dismissal may be the wrong verb for history.** It routes to documented evolution, kept and queryable, and treats a contradiction inside a superseded report as a real historical finding. `kc
  triage` has one outcome, `dismissed`.
- **The answer key has been reused.** Keep a held-out or prospectively labelled set, which matches the new-corpus decision.
- **Its step12 quote settled the `mcp-data` cause.** It quotes `/Volumes/Data/_ai/mcp-data` as retired, while our copy reads `/Volumes/Data/_ai/_mcp/mcp-data`. Confirmed in project_stuff history:
  commit `ea698f0` (migration audit) rewrote that line, so the old top-level root and the live data root became one string. The 2026-11-01 README warning called this inferred; since 2026-11-05 it says
  confirmed, and the nine rewritten reports carry correction notes. Our corpus copy holds the rewrite, so the MCP labels and every `mcp-data` conflict rest on it. The original reports had no such
  contradiction there.

## To explore next

1. Check the disagreements above at their primary sources.
2. Whether ssbc abstention (report 3) fits our 80 verdicts, and an NLI gate as a ranking signal on them.
3. Lineage grouping (report 3) and root grouping (report 4) against research item B3, `kc roots`. Done 2026-11-05: built as root grouping on shared identifiers; 23 of 24 real MCP conflicts in one
   group ([evaluation](../../references/evaluation.md#kc-roots-and-kc-verify-2026-11-05)).
4. The canonical registry and citation-constrained verifier (report 4) against `kc aliases` and B4, `kc verify`. Done 2026-11-05: built citation-constrained (a not-conflict must quote the pair's own
   words) on a local oMLX model; safe, clears little on the MCP pilot. Report 5's "documented evolution" verb adopted in triage.
