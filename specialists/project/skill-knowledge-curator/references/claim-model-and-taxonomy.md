---
Title: Claim model and taxonomy
Category: reference
Status: current
Authority: local-supplement; schemas/claim-input.schema.json is the enforced form; design doc sections 5-6, handoff section 6 (taxonomy, record schema)
Scope: Atomic claims, their fields and three independent classifications, scope, claim IDs, evidence spans, section coverage and the shared taxonomy
Last reviewed: 2026-10-27
Summary: >-
  One proposition per claim with subject, predicate, object and scope; topic (category), kind and epistemic status, and disposition are separate axes;
  evidence spans are verified against source bytes; every parsed section is accounted for. Settles source conflicts C3 and C11.
---

# Claim model and taxonomy

## Contents

- [Atomic claim](#atomic-claim)
- [Three axes, never one status field](#three-axes-never-one-status-field)
- [Scope](#scope)
- [Identity and restatement](#identity-and-restatement)
- [Evidence spans](#evidence-spans)
- [Section coverage](#section-coverage)
- [Taxonomy](#taxonomy)
- [Settled source conflicts](#settled-source-conflicts)

## Atomic claim

One claim is one proposition: a subject, a predicate, an object, qualifiers (scope) and its kind. Split conjunctions that can change independently.

Bad: "SMC uses 24.04, has A/B partitions, and always uses WireGuard." Better: three claims, each with its own kind and evidence.

The agent writes claims as JSON records (`"record": "claim"`) that must pass [schemas/claim-input.schema.json](../schemas/claim-input.schema.json). Required: `subject`, `predicate`, `object`, `claim_text`, `kind`, `epistemic_status`,
`primary_category`, `topic_key`, `disposition`, `evidence`. Optional: `subcategories`, `labels`, `scope`, `valid_time`, `recorded_time`, `confidence`, `inference`, `decision_id`, `claim_id` (only to
revise an existing claim).

## Three axes, never one status field

| Axis             | Values                                                                                                                 | Question it answers           |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Topic            | `primary_category` (one), `subcategories`, `labels`, `topic_key`                                                       | What is it about?             |
| Kind             | `observed`, `target`, `requirement`, `proposal`, `decision`, `hypothesis`, `test_result`, `external_fact`, `procedure` | What sort of statement is it? |
| Epistemic status | `OBSERVED`, `PROPOSED`, `APPROVED`, `INFERRED`, `DISPUTED`                                                             | How well is it established?   |
| Disposition      | `CURRENT`, `HISTORICAL`, `SUPERSEDED`, `DUPLICATE`, `REJECTED`, `REVIEW_REQUIRED`                                      | Where does it belong now?     |

Rules enforced in code: `CURRENT` needs a verified evidence span or a `decision_id` (INV-005); `inference: true` needs `INFERRED`. A disproven observation stays as history, not deleted. The
**effective** disposition used for publishing drops `CURRENT` to `REVIEW_REQUIRED` while a P0/P1 conflict on the claim is open (INV-006).

Handoff mapping: its `kind` values map to the kind axis (`fact` -> `observed` or `external_fact`, `assumption` -> `hypothesis`); its `lifecycle` values map to disposition plus epistemic status
(`current` -> `CURRENT`, `proposed` -> `PROPOSED`, `disputed` -> open conflict, `unverified` -> `REVIEW_REQUIRED` or `INFERRED`, `superseded` -> `SUPERSEDED`).

## Scope

`scope` is a flat map such as `{"environment": "live", "image": "target", "version": "24.04"}`. Two scopes overlap when every key both name has the same value; a missing key matches anything. Only
claims with overlapping scope can truly conflict. "The edge currently runs 22.04" (`state=current`) and "the target image runs 24.04" (`state=target`) are different scope, not a conflict (design 6.3).
Normalise at least: subject, property, layer, environment, site or hardware variant, target versus observed, effective version or date.

## Identity and restatement

- `claim_id` = hash of project, subject, predicate, object and scope (normalised). The source path is not part of it.
- The same proposition from another source is a restatement: it keeps the first wording and gains the new evidence span (INV-009).
- Different objects give different claims, which candidates then pairs for review. Same-key-different-object never silently replaces (INV-008).
- `independent_sources` counts distinct source byte hashes, so ten copies of one file are one source (design case F).
- Supplying `claim_id` revises that claim's body; it must already exist.

## Evidence spans

Each span is `{source_path, line_start, line_end, excerpt}`. Intake refuses it unless the file is inventoried, its bytes still match the inventory hash, the lines exist, and the whitespace-normalised
excerpt occurs inside them. The stored evidence record adds `source_id`, `source_version_id`, `source_sha256`, `excerpt_sha256`, the overlapping `section_ids` and an `evidence_id`. Later checks
(`validate`, `decide`, the `evidence_verified` gate) re-read the file: `valid`, `relocated` (found elsewhere: warning), `broken` or `missing` (error, exit 5).

> **Learned 2026-10-29** · claim extraction from design documents · VERIFIED_SECONDARY (harvest 2026-10-29 of a cloud-repatriation design programme) ·
> Source: aws-to-local `.archcore/rules/single-source-and-restraint.rule.md`, `methodology-freeze.rule.md`, `audit-copy-integrity.rule.md`;
> `docs/platform-approach-revision-plan-rev06-20260728_1723.md:41-42` · Falsifier: a design corpus where present-tense descriptions of
> unbuilt systems never produced a wrong CURRENT claim
> Tense is an existence claim: a design written in the present tense about a system not yet built reads as `CURRENT` when it is
> `PROPOSED`, so extract tense with the claim and treat "will be" as proposed. An uncaveated product name is a decision claim, not a
> neutral mention. A total copied from a source sheet is a claim to verify, not evidence: re-add the rows before sizing from it (one sheet's
> stated total omitted two rows, 63 against a true 72). The same programme's rules match this skill's model: one authoritative home per
> fact (a duplicated table is worse than a missing one), superseded revisions kept as immutable audit copies, and a method that reopens
> only on new evidence, a scope decision or an uncovered gate failure.

> **Learned 2026-10-29 (b)** · provenance figures · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal corpus project) · Source: project_stuff/me
> corpus project `ARCHITECTURE.md` (failure modes) · Falsifier: a figure copied from upstream metadata that always matched the files
> Record counts and sizes measured from the artefact on disk, never copied from an upstream card or catalogue entry: a provenance figure
> taken from a dataset card was contradicted by the data files themselves. A measured figure carries the command or hash that produced it.


## Section coverage

Inventory splits each Markdown file into top-level blocks (paragraph, list, table, code, blockquote, html, front matter) with their heading path. Every block of a live source ends in one status
(INV-003):

| Status                          | Set by                                                                                                               |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `claims-extracted`              | A claim's evidence overlaps it                                                                                       |
| `context`                       | The agent, with a reason (`"record": "section_status"`), or automatically for front matter and a lone `Status:` line |
| `unreadable` / `pending-review` | The agent, with a reason                                                                                             |
| `pending`                       | Nobody yet; `kc worksheet` serves these in bounded batches                                                           |

Code blocks and tables can hold facts and are never skipped automatically. Coverage proves accounting, not that every fact was extracted (INV-014); semantic recall is measured in [evaluation.md](evaluation.md).

## Taxonomy

| Category     | Shared subcategories                        |
| ------------ | ------------------------------------------- |
| architecture | components, topology, integration, security |
| requirements | functional, nonfunctional, acceptance       |
| technical    | protocols, api, configuration, limitations  |
| governance   | decisions, rationale, policy, risks         |
| operations   | deployment, troubleshooting, recovery       |

A project adds subcategories in `.kc/config.yaml` as `taxonomy_extensions: {technical: ["smc:wireguard"]}`, namespaced `project:name`. An unknown subcategory is refused with that hint: a new category
is a proposed taxonomy change, never silent growth. Labels are free.

## Settled source conflicts

- **C3, status vocabulary:** the design's separate axes, with the handoff's kind folded in (mapping above).
- **C11, taxonomy:** the handoff's five categories, enforced; namespaced project extensions.
