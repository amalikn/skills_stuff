---
Title: Feature inventory
Category: reference
Status: current
Authority: local-supplement; both source documents, operator decisions 2026-10-27, enhancements added in the first build
Scope: Every feature from the three source documents and the enhancements added beyond them, with disposition (built, deferred, rejected) and invariant coverage
Last reviewed: 2026-11-01
Summary: >-
  What exists now, what was added beyond the documents and why, what is deferred and on what trigger, the v2 staged roadmap (stages 1-7, nothing
  built), and where each design invariant is enforced.
---

# Feature inventory

## Contents

- [Built in v1](#built-in-v1)
- [Added beyond the source documents](#added-beyond-the-source-documents)
- [Deferred](#deferred)
- [v2 staged roadmap](#v2-staged-roadmap)
- [Fixes from the Continuum pilot](#fixes-from-the-continuum-pilot)
- [Invariants and where they are enforced](#invariants-and-where-they-are-enforced)

## Built in v1

Inventory with hashes, renames, removals, exclusions and byte-duplicate groups; Markdown block parsing with line spans; agent claim intake with verified evidence; coverage accounting; candidate
generation (FTS5, RapidFuzz, signals, optional NLI); relation intake with policy-limited automatic dispositions; conflicts with P0-P3; review cards; five decision actions, append-only, revalidated;
deterministic rendering of category, history, open-issues and index pages plus `index.json`; promotion with four gates and revocation; archive plan with referrers and restore rehearsal; query;
slurp-style intake; validate; report; single-writer lock; path containment; secret scan on output.

## Added beyond the source documents

| Feature                                                                            | Why                                                                                          |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Promotion stage (derived -> promoted -> archive) with digest-bound approval        | Operator, 2026-10-27: start derived, promote by a process, then archive                      |
| `evidence_verified` promotion gate on by default                                   | A source edited after render would otherwise be promoted stale (review, 2026-10-27)          |
| `kc worksheet`: pending sections in bounded batches with an `imperative-text` flag | Makes extraction incremental and resumable, and keeps injection text visibly data            |
| Automatic `context` for front matter and lone `Status:` lines                      | Removes busywork without guessing: only certain cases                                        |
| `kc query` with `settled` and `--history`                                          | Agent retrieval that cannot present a disputed or superseded claim as current (T07, INV-013) |
| `kc intake` implemented now                                                        | The slurp contract is testable before slurp is wired                                         |
| Rename detection keeps `source_id`                                                 | Moving a file must not orphan its claims                                                     |
| Section IDs keyed on content, not line numbers                                     | Unchanged blocks keep their coverage when the file changes elsewhere                         |
| `USE_OTHER` instead of "use earlier"                                               | Earlier or later is not always the frame; the operator names the claim                       |
| `elapsed_s` on every command                                                       | Efficiency is part of done                                                                   |

## Deferred

| Item                                                         | Trigger to build                                                  |
| ------------------------------------------------------------ | ----------------------------------------------------------------- |
| Real archive run (`archive --apply`, restore command, T-008) | Pilot passes and the operator asks ([archive-safety.md](archive-safety.md)) |
| skill-slurp-chat Step 4b wiring                              | Pilot passes (operator, 2026-10-27)                               |
| Gold-set semantic evaluation harness                         | Before release ([evaluation.md](evaluation.md))                   |
| Topic-level locks for concurrent writers (design 11)         | A second writer actually appears; one project lock today          |
| Persisted FTS cache under `.kc/cache/`                       | Candidate runs exceed the 2 s budget                              |
| SilverBullet, Quartz, LLM Wiki one-way compile, MCP facade   | A usability test shows a gap; never a second writable truth store |
| CI workflow for structural checks                            | A project asks for it                                             |
| Non-Markdown formats beyond inventory (`unsupported` today)  | A pilot project needs one                                         |
| External verification: `kc links` (every URL with citing claims and sections, status, redirect) and an external-fact verification record (upstream URL, date, upstream excerpt, verdict) with a promotion gate | Proven on the Continuum pilot first: `tools_stuff/continuum/scripts/check_links.py` (operator, 2026-10-30: "should that feature be added to skill-kc?"); blocked pages go through all-scraper |

Rejected for v1: vector database, daemon or crawler, knowledge graph, autonomous fact approval, edits to governing files, cross-portfolio federation (apn and personal records are never cross-indexed;
INV-015). The v2 roadmap below narrows two of these (operator, 2026-10-27): a relationship graph within one portfolio (stage 5), and vector search only as an optional engine on measured need (stage
7). Cross-portfolio links stay rejected.

## v2 staged roadmap

Source: [v2 spec](../docs/knowledge-curator-foss-implementation-spec-v2.md), build order from its section 12; decisions V1-V9 in [catalog](../docs/catalog.md) (operator,
2026-10-27). v2 tests are cited `V2-T01` to `V2-T18` so they never collide with the handoff's T01-T14. Nothing below is built.

Rules for every stage:

- **Gate 0:** failed three attempts 2026-11-01: precision 37.5% against 70%, recall 51.1% against 80% ([evaluation.md](evaluation.md)); v2 stages and slurp Step 4b are held.
- One stage at a time; a stage is done when its listed V2 tests pass, `just check` is green and its runtime is measured against a stated budget.
- Before any new dependency: pin the exact version and check its current licence, platforms and transitive runtime from upstream (v2 section 4); record it in `requirements*.txt` and a seam module.
- v1 stays the base: two-axis status (C3), jsonschema, the single `ledger.py` writer, `--apply` gating, promotion gates. v2 additions are optional fields, optional installs or new seams.
- Diagram edges and static-code findings enter as candidates (`INFERRED`, `REVIEW_REQUIRED`), never as verified dependencies or runtime behaviour.

| Stage | Name                     | Builds                                                                                                                                     | Exit tests           |
| ----- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------- |
| 1     | Gap matrix               | Code-level gap matrix of v2 sections 2-11 against `knowledge_curator_lib/` (the doc-level one is catalog V1-V9); no edits                  | Matrix reviewed by   |
|       |                          |                                                                                                                                            |   the operator       |
| 2     | Deterministic            | Optional `subject`/`predicate`/`object` claim fields; v2-to-v1 kind and status mapping; run envelope from `kc intake` (claims,             | V2-T03, V2-T04,      |
|       |   baseline additions     |   relationships, conflicts, `proposed_updates`, `unresolved`, `audit`); `.kc/` config with `offline_only` and `model_allowlist`            |   V2-T12, V2-T13     |
| 3     | Semantic reasoning       | Embedding seam behind an optional install (as NLI is); optional model adapter in `kc`, default local Ollama, off unless configured,        | V2-T01, V2-T02,      |
|       |                          |   refused by `offline_only` or a model not on the allowlist; adapter output passes the same schema and evidence checks; semantic gold set  |   V2-T14, V2-T18     |
|       |                          |   (design 13.2)                                                                                                                            |                      |
| 4a    | Code and Mermaid         | Tree-sitter seam: definitions, imports, references with spans, `repo`/`commit`/`path`/method recorded; Mermaid nodes, edges, subgraphs;    | V2-T07, V2-T09       |
|       |                          |   unsupported diagram types `unparsed`                                                                                                     |                      |
| 4b    | draw.io and ASCII        | `mxfile`/`mxGraphModel` reader with compressed pages, page and layer scope (reuse skill-drawio's reader where it fits); ASCII box/arrow    | V2-T10, V2-T11       |
|       |                          |   heuristic, original span kept, edges proposed only                                                                                       |                      |
| 4c    | PDF and Office           | Format router: MarkItDown or Docling (or skill-anydoc's converter), original path and extractor version kept, tables located by page;      | V2-T06               |
|       |                          |   ast-grep only on demonstrated need                                                                                                       |                      |
| 5     | Federated linking,       | Shared reference index (IDs, aliases, candidate relations, no copied facts); NetworkX over relation records; alias table with evidence;    | V2-T08, V2-T15       |
|       |   one portfolio          |   portfolio boundary check (INV-015 narrowed: apn and personal never linked); proposals to the owning project, no cross-repo write         |                      |
| 6     | slurp Step 4b            | Conditional Step 4b with v2's invoke and skip triggers (skip reported, never silent); curator-status column in the coverage table; Steps   | V2-T05,              |
|       |                          |   5-7 unchanged; proposals never become `record_decision`                                                                                  |   V2-T16, V2-T17     |
| 7     | Optional engines         | LightRAG trial against the stage 2-5 baseline on identical fixtures; Qdrant, GLiNER, Joern, DuckDB only on measured need. CodeQL excluded  | Trial report; adopt  |
|       |                          |   (not FOSS)                                                                                                                               |   only on gain       |

Open before stage 1 (v2 section 13): which Mermaid families and draw.io encodings the operator's projects use (a read-only survey answers it); whether a shared SQLite index already exists and where it
sits under the data, cache and runtime routing; whether any slurp step already indexes symbols or relations.

## Fixes from the Continuum pilot

From [evaluation.md](evaluation.md), "Pilot on the Continuum corpus" (2026-10-30). **Built 2026-11-01** (tests `tests/test_continuum_recall.py`, `test_continuum_tooling.py`, each failing first):
P1-P4, P8-P10, P12-P16, P19, P20, and P18, P21, P25-P28 and P30-P32 the same day. **Not built:** P5, P6, P7, P17, P22-P24; each needs a test that fails first.

P1 went beyond the row below: same-topic cross-source pairs need only a shared subject word, because fuzzy predicates missed the real wording. P12 also ignores provenance keys when comparing
scopes, which repairs existing ledgers. P15 dropped `archive` from the default and excludes `archive_dir` by path, and warns on any other excluded folder holding Markdown.

| Finding | Fix |
| ------- | --- |
| P1 | `kc vocabulary`: subjects, predicates and topic keys already in the ledger, served with every worksheet batch; `claims` warns when a new subject or predicate is a near match (RapidFuzz) of an existing one; `candidates` also blocks on `topic_key` and on subject with a fuzzy predicate match |
| P2 | Rank cross-source pairs first; suppress same-source pairs whose subjects differ unless a negation signal fires; report same-source and cross-source counts |
| P3 | `query` and pages show `unreviewed candidate pairs: n` per claim; `validate` warns while pairs touching `CURRENT` claims are unclassified |
| P4 | `HISTORICAL`/`SUPERSEDED` need a relation, a `successor` or a source-stated supersession in the evidence; render links successor and predecessor both ways |
| P5 | Render by project subcategory into folders (one page per subcategory or topic group), category pages becoming indexes |
| P6 | Granularity rule in claim-model-and-taxonomy.md: one claim per independently changeable decision; a table row is one claim unless its cells change independently; a list of chosen tools is one claim |
| P7 | Topic-key convention `<source-short-id>.<local-key>` for source-local numbering (ADR-001), plus a shared key for the subject it decides |
| P8 | `validate --strict`: fail while any section is `pending` |
| P9 | `claims` dry run reports the sections it would close |
| P10 | Evidence errors quote the cited lines and the nearest match |
| P12 | `claims` warns when a scope key names provenance (`source`, `author`, `document`, `file`) rather than the situation a claim holds in; provenance belongs in evidence and labels |
| P13 | `kc decision-points`: group claims by subject and predicate (and by topic) across two or more sources with differing objects; serve groups to the relate step instead of raw pairs; measure `candidates` against its budget at 3,500 claims |
| P14 | `CORRECTED` reuses the existing operator claim when the wording matches, or takes a project-wide scope |
| P15 | Remove `archive` from the default, or warn loudly when an excluded folder holds Markdown |
| P16 | `worksheet --path`, `claims --coverage`, and a `kc sections --path` listing |
| P17 | Port the Continuum register and coverage scripts as `kc registers` and `kc page-coverage` (reference: `tools_stuff/continuum/scripts/`) |
| P18 | Lint claim text against its excerpt: numbers, negation and names in the text must appear in the excerpt; flag, never refuse, because a paraphrase can be right |
| P19 | `kc amend <cf> --add-claim <id> --supersede/--keep --reason`: append-only, links `previous_decision_id`, `successor` is the ruling's current claim; `--supersede` needs a decided conflict |
| P20 | `settled` is `CURRENT` with no open conflict of any severity; publishing still uses `effective()` |
| P21 | `review` flags open conflicts whose claims were touched by a later decision, and a recommendation naming a superseded claim |
| P22 | `kc page-claims`: facts on an authored page with no claim id, offered as a batch to extract |
| P23 | Vocabulary proposal records with a merge step in `kc vocabulary` |
| P25 | Mark multi-valued predicates in config so a differing object alone is no signal, without exempting them from conflict detection: `must` holds 17 Continuum conflict memberships and `must not` 4. Start from `must`, `must not`, `is tested by`, `has open question`, `has risk`, `is out of scope`, `serves`; not `is implemented with`, `contains`, `exposes`, `has exit criterion`, `has decision`, `is defined as`. Let a reviewed group be recorded as one classification |
| P26 | `decide` refuses to revive a claim superseded outside this conflict unless `--override-supersession`, which the decision records; `validate` warns on past revivals with no override |
| P27 | `decide` keeps a successor set by another conflict and lists it in `kept_successors`; `kc amend <cf> --set-successor <claim> --successor <id>` repairs a link, append-only |
| P28 | Built: `decision-points` returns `word_groups` around a rare subject word (operator chose this over a consolidation pass or sequential batches). Recall stays low; a consolidation pass is the next option |
| P29 | Pair same-source claims on one rare subject word with differing objects, ranked low |
| P30 | `relate` warns when a conflict opens on a claim no longer live, in the ledger or earlier in the batch |
| P31 | `time-evolution` with `basis: dated-order` needs no excerpt, supersedes nothing and opens a `time-evolution-proposed` conflict recommending the later claim |
| P32 | `kc topics` cites one path per byte group and lists `byte_copies`; `--by-file` repeats no claim |
| P33 | Built as `kc triage`, `kc status-map`, `kc sample`; proposals until a blind sample is 95% right (92.5% so far). Next by the research: B3 `kc roots`, then B4 `kc verify` |
| P24 | Port with P17: conformance into `claims`, verification into the external-fact record |

## Invariants and where they are enforced

| Invariant                                | Enforced by                                                                  |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| INV-001 immutable originals              | Sources only read; hashes and sizes recorded; archive is plan-only           |
| INV-002 source accounting                | `inventory`: every in-scope file has a state; exclusions listed with reasons |
| INV-003 section accounting               | `coverage`, `worksheet`, `validate` warning                                  |
| INV-004 one disposition                  | Fold keeps the last disposition event per claim                              |
| INV-005 evidence                         | `claims` intake refusal; `validate`                                          |
| INV-006 conflict blocking                | `State.effective`; render's Not settled; promotion gate                      |
| INV-007 human authority                  | Only `decide` resolves conflicts; only explicit answers. Narrowing agreed, not built: evidence-backed, reversible automatic resolution, proposals until 95% right on 40+ samples (AGENTS.md, Triage) |
| INV-008 no newest-wins                   | Claim IDs include the object; candidates pair same-key claims                |
| INV-009 no loss by dedupe                | Restatements merge evidence; DUPLICATE keeps its evidence and link           |
| INV-010 safe archive                     | Plan only, rehearsal, referrers                                              |
| INV-011 idempotence                      | Content-derived IDs; skip-if-recorded in every intake; deterministic render  |
| INV-012 fail closed                      | Whole-batch rejection, write lock, atomic replace, exit 5 on changed sources |
| INV-013 read precedence                  | `query` hides history unless asked; `settled` flag                           |
| INV-014 no exhaustiveness claim          | Coverage is accounting; semantic recall measured separately                  |
| INV-015 no cross-project contamination   | Ledgers per project; IDs include `project_id`                                |
| INV-016 attributed, reversible decisions | `previous_decision_id`; revocation records; nothing overwritten              |
