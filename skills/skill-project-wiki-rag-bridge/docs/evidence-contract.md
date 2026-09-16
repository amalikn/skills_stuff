# Evidence Contract

**Authority:** skill-project-wiki-rag-bridge docs layer
**Mirrors:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/docs/evidence-contract.md`
**Purpose:** Explains the EvidenceBundle contract, answer rules, and citation requirements
for skill users and agents.

---

## What Is EvidenceBundle?

`EvidenceBundle` is a Pydantic model defined in `rag_tools.evidence`. Every rag-tools retrieval
command (`structured-lookup`, `lookup-section`, `lookup-table`, and vector RAG) returns a list
of EvidenceBundle objects.

The bundle contains:

- The verbatim excerpt from the source file
- The source file path (authoritative citation)
- The retrieval mode used
- Section ID, heading, table ID (where applicable)
- Matched terms
- Score or confidence
- Retrieval warnings

The LLM must answer only from evidence bundle content. It must not fill gaps with training
knowledge.

---

## Required Fields

| Field | Required | Purpose |
|---|---|---|
| `query` | Yes | The original lookup query |
| `retrieval_mode` | Yes | Mode that produced this bundle |
| `source_file` | Yes | Absolute path to the canonical source |
| `excerpt` | Yes | Verbatim text from source — only basis for answer |
| `retrieval_warnings` | Yes (list) | Populated when evidence is partial or low-confidence |

---

## How Agents Should Answer From EvidenceBundle

**Rule 1: Answer only from `excerpt`.**

Do not add facts from training knowledge. Do not infer amounts, dates, rates, clause text, or
identifiers that are not present verbatim in the excerpt.

**Rule 2: Cite the source.**

Every answer must include at minimum `source_file`. Preferred citation includes
`section_id` or `heading` or `table_id`.

**Rule 3: Surface warnings.**

If `retrieval_warnings` is non-empty, include a note in the answer. Low-confidence or fallback
evidence must be flagged, not silently used.

**Rule 4: Report gaps honestly.**

If no EvidenceBundle is returned, or if the excerpt is empty, state:
"not found in retrieved evidence" — do not synthesize a plausible answer.

**Rule 5: Do not merge conflicting excerpts.**

If two bundles contain conflicting values, report the conflict rather than resolving it.

---

## What to Do When Evidence Is Weak

| Situation | Response |
|---|---|
| No bundle returned | Report `RETRIEVAL_NOT_READY` and stop |
| Bundle returned but excerpt is empty | Report "not found in retrieved evidence"; surface warning |
| `score_or_confidence < 0.5` (RAG) | Flag as low-confidence; do not answer as fact |
| `retrieval_warnings` contains fallback note | Surface the warning; qualify the answer |
| Multiple bundles with conflicting excerpts | Report conflict; cite both sources |
| Exact amount not in excerpt | State "exact value not found in retrieved evidence" |

---

## Citation Requirements

Minimum citation (required):
```
Source: <source_file>
```

Preferred citation:
```
Source: <source_file>
Section: <section_id> — <heading>
```

Full citation:
```
Source: <source_file>
Path: <section_path as breadcrumb>
Section: <section_id>
Excerpt: "<verbatim excerpt>"
Mode: <retrieval_mode>
```

For table results:
```
Source: <source_file>
Table: <table_id>
Row: <row_keys>
Excerpt: "<verbatim cell content>"
```

---

## Examples of Good and Bad Answers

### Good answer — grounded in evidence

Query: "What is the rebate for period 3?"

EvidenceBundle excerpt:
```
| Period | Rebate |
|---|---|
| Period 3 | $18,420 |
```

Answer:
> The rebate for period 3 is $18,420.
> Source: /project/rag/docs/rate-card.md | Table: rate-rebate-table

---

### Bad answer — invented value not in evidence

Query: "What is the rebate for period 3?"

EvidenceBundle excerpt:
```
Rate adjustments are applied quarterly based on volume thresholds.
```

Bad answer:
> The rebate for period 3 is approximately $18,000 based on typical quarterly rates.

Problem: The amount "$18,000" is not in the excerpt. The answer uses training knowledge to
fill a gap. This is forbidden.

Good answer:
> The retrieved evidence does not contain the period 3 rebate amount. The nearest evidence
> found was: "Rate adjustments are applied quarterly based on volume thresholds."
> Source: /project/rag/docs/rate-card.md

---

### Good answer — warning surfaced

Query: "What is the grace period for late payment?"

EvidenceBundle excerpt:
```
Payment terms are described in Schedule B.
```

retrieval_warnings: ["no exact section ID match; nearest heading used"]

Answer:
> The retrieved evidence references Schedule B for payment terms but does not include the grace
> period value. The retrieval used the nearest heading match (not an exact section ID).
> Warning: no exact section ID match; nearest heading used.
> Source: /project/docs/agreement.md | Heading: Payment Terms

---

### Bad answer — warning silenced

Same situation as above, but the answer states:
> The grace period is 14 days.

Problem: The value is invented. The warning was not surfaced.
