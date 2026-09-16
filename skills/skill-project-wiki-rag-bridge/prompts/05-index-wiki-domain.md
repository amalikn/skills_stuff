# Prompt 05 — Index Wiki Domain

**Purpose:** Index exactly one wiki domain into its Qdrant collection.
Always dry-run first. Never index multiple domains in one operation.

**Parameters:**

```
DOMAIN:     <domain_slug>               # e.g. "nbn"
COLLECTION: rag__wiki_<domain_slug>     # e.g. "rag__wiki_nbn"
```

**Copy this prompt into Codex or Claude Code. Replace parameters before pasting.**

---

## Pre-flight checklist (blocking — must all pass before live indexing)

### PF-0: Profile / strategy gate

This gate must pass before any further pre-flight checks. If the wiki domain content has not
been profiled or if strategy has not confirmed vector RAG is suitable for this domain, do not
proceed.

**Checks:**

- [ ] BLOCKING: Domain content has been profiled (profile-file or profile-project run on domain
  articles, or explicitly waived if all articles are `knowledge_article` class).
- [ ] BLOCKING: `recommend-strategy` output (or manual classification) confirms that vector RAG
  is `suitable` or `partially_suitable` for this domain's content class. If content is exclusively
  structured reference files, stop and use structured/section lookup instead.
- [ ] WARN: If all articles in the domain are scaffold pages (no body, no source references),
  indexing will produce low-value retrieval. Add curated content (prompt 07) before indexing.
- [ ] BLOCKING: If the primary source for this domain is a single long structured markdown file,
  do not index derived wiki summaries as a substitute for direct lookup of the source. Use
  `rag-tools structured-lookup` or `rag-tools lookup-section` on the source directly.
- [ ] The dry-run gate (PF-5 onwards) still applies — this gate does not replace it.

**How to profile domain content:**

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin
WIKI_DOMAIN="/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<domain_slug>"

# Profile all articles in the domain
$VENV/rag-tools profile-project "$WIKI_DOMAIN"

# Or profile a specific article
$VENV/rag-tools profile-file "$WIKI_DOMAIN/<article>.md"

# Recommend strategy for a specific article
$VENV/rag-tools recommend-strategy "$WIKI_DOMAIN/<article>.md"
```

If all articles return `document_class: knowledge_article` and
`rag_suitability: suitable` → proceed.

If any articles return `document_class: structured_markdown_reference` and
`rag_suitability: partially_suitable` → note in output and consider whether direct lookup
is more appropriate for those articles.

**PF-0 verdict:**

```
PF-0: PASS — strategy confirms vector RAG suitable for this wiki domain
PF-0: PASS_WITH_WARNING — partially_suitable; note which articles may under-perform in RAG
PF-0: FAIL — structured/tabular content detected; use direct lookup, not wiki indexing
```

---

### PF-1: Content exists

```bash
DOMAIN="<domain_slug>"
WIKI_DOMAIN="/Volumes/Data/_ai/_wiki/wiki_stuff/domains/$DOMAIN"

test -d "$WIKI_DOMAIN" && echo "PASS: domain dir exists" || echo "FAIL: domain dir missing — run prompt 01"
find "$WIKI_DOMAIN" -name '*.md' | wc -l | xargs -I{} echo "Markdown files: {}"
```

Must have at least 1 markdown file. If empty, add content (prompt 07) before indexing.

### PF-2: Source references exist

```bash
find "$WIKI_DOMAIN" -name '*.md' | head -5 | while read f; do
  python3 -c "
import pathlib
text = pathlib.Path('$f').read_text()
if 'source:' in text or 'Source references' in text:
    print('PASS: $f has source reference')
else:
    print('WARN: $f has no source reference')
"
done
```

Articles without source references should not be indexed — they may be scaffold/invented content.

### PF-3: Policy validated

Confirm prompt 04 has been run and passed. Collection name must be `rag__wiki_<DOMAIN>`.

### PF-4: No forbidden collection

```bash
echo "Collection to create: rag__wiki_<domain_slug>"
python3 -c "
forbidden = {'rag__global_all_docs', 'rag__wiki_all', 'rag__all', 'default', 'documents', 'knowledge', 'main'}
c = 'rag__wiki_<domain_slug>'
print('PASS: collection name allowed' if c not in forbidden else 'FAIL: forbidden collection name')
import re
print('PASS: name matches pattern' if re.match(r'^rag__wiki_[a-z0-9_]+$', c) else 'FAIL: name does not match pattern')
"
```

### PF-5: Qdrant running

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
```

Must be running before proceeding.

---

## Step 1 — Dry-run index

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli index-domain --domain <domain_slug> --dry-run
```

Review the dry-run output:
- Chunk count reasonable for the domain content?
- No files from other domains included?
- No project files included?
- Collection name shown as `rag__wiki_<domain_slug>`?

**Stop here if dry-run output looks wrong. Do not proceed to live indexing.**

---

## Step 2 — Confirm before live index

Before proceeding to live indexing, confirm:
- [ ] Dry-run chunk count is reasonable (not 0, not suspiciously high)
- [ ] No cross-domain or project files in the dry-run output
- [ ] Collection name is correct
- [ ] Operator has reviewed and approved

If running in an automated session without operator review, stop here and report the dry-run results.
Do not auto-proceed to live indexing.

---

## Step 3 — Live index

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli index-domain --domain <domain_slug>
```

This upserts idempotently — re-running is safe if content has not changed.

---

## Step 4 — Verify collection

```bash
# Check collection exists and has chunks
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_<domain_slug>')
print(f'Collection: rag__wiki_<domain_slug>')
print(f'Vectors count: {info.vectors_count}')
print(f'Status: {info.status}')
"
```

---

## Output format

```
Verdict: WIKI_DOMAIN_INDEXED | WIKI_DOMAIN_INDEX_PARTIAL | WIKI_DOMAIN_INDEX_FAILED

Domain:          <domain_slug>
Collection:      rag__wiki_<domain_slug>
Dry-run chunks:  <count>
Live chunks:     <count after indexing>
Collection status: <green/yellow/red from Qdrant>

Checks passed:   <list>
Checks failed:   <list or "none">

Next prompt: 06-post-index-retrieval-validation.md
```
