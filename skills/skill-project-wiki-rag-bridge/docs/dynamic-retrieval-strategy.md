# Dynamic Retrieval Strategy

**Authority:** skill-project-wiki-rag-bridge docs layer
**Mirrors:** `/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/docs/dynamic-retrieval-strategy.md`
**Purpose:** Explains the profile-first retrieval model for skill users and agents.

---

## Why Pure Vector RAG Is Not Always Correct

Vector RAG works by embedding chunks of text and matching query embeddings to document chunk
embeddings. This works well for broad, semantic, cross-document questions where the answer does
not have a single canonical location.

It does not work well for:

- **Exact fact extraction** — a rate card amount, a contract clause, a rebate percentage, a date.
  Vector similarity finds "nearby" chunks, not the exact row.
- **Structured document navigation** — a long reference doc with section IDs (C2.11, 3.4.2).
  The relevant clause might not be the highest-similarity chunk.
- **Table lookups** — invoice line items, rate grids, pricing tables. Vector RAG does not
  understand row/column structure; it treats table text as undifferentiated prose.
- **Short documents** — a YAML config or a small policy file may return high-confidence chunks
  that are not the most relevant row or field.

Using vector RAG by default for all sources increases hallucination risk for exact facts because
the model may construct a plausible answer from adjacent chunks without verifying the exact value.

---

## Direct Lookup vs Table Lookup vs Vector RAG

### Direct (structured) lookup

`rag-tools structured-lookup` or `rag-tools lookup-section` parses the document's heading tree
and section IDs, then scores sections by term overlap with the query.

**Best for:**
- Long structured markdown with headings and section IDs
- Legal contracts and policy documents (clause navigation)
- Reference documents with numbered sections
- Questions with a known section reference ("what does clause C2.11 say?")

**Not for:**
- Cross-document semantic search
- Summarization questions

### Table lookup

`rag-tools lookup-table` extracts markdown tables, tokenizes headers and rows, and scores by
query term overlap against header text and cell values.

**Best for:**
- Rate cards with period/tier rows
- Invoice line items
- Rebate tables, discount grids
- Pricing schedules

**Not for:**
- Non-tabular content
- Questions requiring row aggregation or arithmetic (use tabular_analytics)

### Vector RAG

Best for knowledge articles, wiki content, meeting notes, broad cross-document questions.

**Best for:**
- Questions whose answer spans multiple sections or documents
- Semantic questions without a precise term match ("what generally applies to service X?")
- Wiki domain content (knowledge_article class)

**Not for:**
- Exact amounts, dates, identifiers
- Structured clause references
- Invoice line items
- Any document where table or section lookup is available

---

## Source Files as Authority

Source files are always authoritative. Qdrant collections and wiki articles are retrieval
artifacts — they are search indices built from source files, not replacements for them.

Rules:
- Answer from `source_file` content in the EvidenceBundle, not from the collection name.
- If a source file and a Qdrant result conflict, prefer the source file.
- Do not duplicate full source files into wiki articles to make RAG work. Use direct lookup.

---

## Profile-First Workflow

Before choosing a retrieval route:

1. Run `rag-tools profile-file <file>` → get `document_class` and `recommended_retrieval_modes`
2. Run `rag-tools recommend-strategy <file>` → get `primary`, `secondary`, `fallback`, `rag_suitability`
3. For structured/tabular/exact-fact documents: run `rag-tools benchmark-file` before committing
   to a default route
4. Record the strategy in `rag/retrieval-strategy.yaml`
5. Only consider vector RAG indexing if strategy says `rag_suitability: suitable` or
   `partially_suitable` AND benchmark supports it

This profile-before-index pattern prevents the most common mistake: indexing everything into
vector RAG and then getting unreliable answers for structured/exact-fact content.

---

## Benchmark Before Default Route

The benchmark runs all applicable modes against a representative query set and returns a
recommendation label:

| Label | Meaning |
|---|---|
| `DIRECT_FIRST` | Structured lookup wins — use as primary |
| `TABLE_LOOKUP_FIRST` | Table lookup wins — use as primary |
| `HYBRID_DIRECT_FIRST` | Direct primary, RAG secondary |
| `HYBRID_RAG_FIRST` | RAG primary, direct fallback |
| `RAG_FIRST` | RAG outperforms direct modes |
| `NOT_READY_NEEDS_EXTRACTION` | PDF — extraction required |
| `NOT_READY_NEEDS_MORE_INDEXED_CONTENT` | No mode passed — source needs rework |

A `DIRECT_FIRST` or `TABLE_LOOKUP_FIRST` result means vector RAG is not needed for that document.
Indexing it into Qdrant would add operational cost with no retrieval benefit.

---

## Wiki Domains

Wiki domains contain `knowledge_article` class content — curated reference articles written
for broad semantic retrieval. These are the right content type for vector RAG.

Wiki articles should:
- Be written as standalone reference material, not as extracts of long source files
- Have `source:` references linking back to authoritative sources
- Not duplicate full source file content (rate cards, contract clauses)

If a wiki domain contains only scaffold pages (headings, no body), indexing it will produce
low-value retrieval. Add curated content (prompt 07) before indexing.

---

## How the Project Bridge Uses Strategy Output

The `rag/retrieval-strategy.yaml` file records the chosen route per document. Agents use it to:

1. Route exact-fact queries to `rag-tools structured-lookup` or `rag-tools lookup-table`
2. Route semantic/cross-document queries to vector RAG (if index exists)
3. Respect the `index_allowed` flag before calling any indexing command
4. Select the appropriate EvidenceBundle-returning command for each query type

The retrieval policy (`rag/retrieval-policy.yaml`) continues to govern which Qdrant collections
are accessible and with what filters. The strategy file adds per-document routing on top.
