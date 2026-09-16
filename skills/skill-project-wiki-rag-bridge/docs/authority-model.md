# Authority Model

## Source of truth hierarchy

When an agent needs to answer a question or retrieve a fact, it must apply this hierarchy:

```
Priority  Source                              Scope
────────  ──────────────────────────────────  ─────────────────────────────────────────
1         Project-local files                 Project-specific facts ONLY
2         Wiki authoritative markdown         Shared reference facts ONLY
3         Qdrant retrieval results            Search results — cite original, don't treat as canonical
4         Generated summaries / reports       Secondary — do not override primary sources
5         Nav YAML                            Routing metadata ONLY — never factual content
```

## Rules

### Rule 1 — Project-specific facts come from project-local files

If the question is about this project's invoices, calculated profitability, internal decisions,
customer mappings, or analysis results, the answer must come from:

```
<project>/reports/
<project>/docs/
<project>/db/
<project>/scripts/
<project>/communications/ (if reviewed and indexed)
```

Do NOT use the wiki for project-specific facts — the wiki does not know this project's data.

### Rule 2 — Shared reference facts come from wiki markdown

If the question is about a standard, a policy definition, a rate card interpretation, or any
knowledge that applies across multiple projects, the answer comes from:

```
_wiki/wiki_stuff/domains/<domain>/references/*.md
_wiki/wiki_stuff/domains/<domain>/index.md
```

The markdown source file is always authoritative — not the Qdrant payload.

### Rule 3 — Qdrant payloads are retrieval artefacts

A Qdrant result is a pointer back to a source file. When citing, cite:
- The source file (`source_file` metadata field)
- The section (`section_path`, `heading` fields)
- The collection it came from

Never treat a Qdrant payload as more authoritative than the markdown source it was indexed from.

### Rule 4 — Nav YAML is routing metadata only

Files such as `context-map.yaml`, `project-context.yaml`, `AI_NAVIGATION.md`, and domain
`index.md` routing tables define WHERE to look — they are not factual sources themselves.

An agent must never answer a factual question by citing a routing file.

### Rule 5 — No unsupported conclusions

If the retrieved evidence is insufficient or ambiguous, the agent must say so explicitly:

> "I searched project-local files, the project Qdrant collection, and wiki domains [nbn, vocus].
> I found insufficient evidence to answer this question confidently. Can you point me to the
> relevant document or provide additional context?"

Do not speculate or blend sources without clearly labelling each.

### Rule 6 — Conflict resolution

When project-local files and wiki markdown disagree:

| Conflict type | Resolution |
|---|---|
| Project fact vs wiki general reference | Project-local wins |
| Wiki standard vs project interpretation | Report the conflict; ask user |
| Two wiki articles disagree | Report the conflict; cite both; ask user |
| Qdrant result vs source markdown | Source markdown wins — re-read the file |

---

## Source labels used in metadata

| `authority` value | Meaning |
|---|---|
| `shared_reference_authoritative_markdown` | Wiki domain article — shared, curated, sourced |
| `project_local` | Project-specific document — authoritative for that project |
| `project_generated` | Output of a script or pipeline — secondary, verify source |
| `routing_metadata_only` | Nav YAML or context file — not a factual source |
