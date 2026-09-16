# Operating Runbook

Step-by-step commands and sequences for all standard operations.
All commands assume you are in the project root unless stated otherwise.

---

## 1. New wiki domain

```bash
# Verify wiki is ready
# Run: prompts/00-verify-wiki-operational-state.md

DOMAIN="<domain_slug>"
WIKI_STUFF="/Volumes/Data/_ai/_wiki/wiki_stuff"
WIKI_DATA="/Volumes/Data/_ai/_wiki/wiki-data"

# 1. Create directory
mkdir -p "$WIKI_STUFF/domains/$DOMAIN/references"

# 2. Create index.md (use templates/wiki-domain-index.md)

# 3. Register in domain-registry.yaml (append entry from templates/wiki-domain-registry-entry.yaml)

# 4. Update wiki log
echo "$(date +%Y-%m-%d)  Created domain: $DOMAIN" >> "$WIKI_STUFF/log.md"

# 5. Validate
python3 -c "
import yaml
with open('$WIKI_DATA/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)
found = [d for d in reg['domains'] if d['slug'] == '$DOMAIN']
print('PASS' if found else 'FAIL: not registered')
"
```

---

## 2. New project bridge

```bash
# Run after: prompts/00, 01 (if domain needed), 02
# Use: prompts/03-create-project-bridge.md

PROJECT_ROOT="<absolute-path-to-project>"
PROJECT_SLUG="<project_slug>"

# Create dirs
mkdir -p "$PROJECT_ROOT/rag/manifests" "$PROJECT_ROOT/docs/ai"

# Create files (fill from templates):
#   rag/project-context.yaml
#   rag/retrieval-policy.yaml
#   rag/manifests/project-documents.yaml
#   docs/ai/wiki-bridge.md

# Validate
python3 -c "
import yaml, pathlib
root = pathlib.Path('$PROJECT_ROOT')
for f in ['rag/retrieval-policy.yaml', 'rag/project-context.yaml', 'rag/manifests/project-documents.yaml']:
    try: yaml.safe_load((root/f).read_text()); print(f'PASS: {f}')
    except Exception as e: print(f'FAIL: {f} — {e}')
"
```

---

## 3. Validate project policy

```bash
cd <PROJECT_ROOT>

# YAML parse + flat key check
python3 -c "
import yaml
required = ['version','project_slug','project_collection','allowed_wiki_domains',
            'allowed_wiki_collections','forbidden_collections','required_filters','citation_rules']
with open('rag/retrieval-policy.yaml') as f:
    p = yaml.safe_load(f)
missing = [k for k in required if k not in p]
print('FAIL: missing keys:', missing) if missing else print('PASS: all flat keys present')
"

# rag-tools validator
/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli validate-policy rag/retrieval-policy.yaml
```

---

## 4. Index wiki domain

```bash
RAG_BIN="/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python"
RAG_ROOT="/Volumes/Data/_ai/_tool/tools_stuff/rag-tools"
DOMAIN="<domain_slug>"

# Dry-run first (REQUIRED)
cd "$RAG_ROOT" && $RAG_BIN -m rag_tools.cli index-domain --domain $DOMAIN --dry-run

# Review output — chunk count reasonable? No cross-domain bleed?
# Then live index:
cd "$RAG_ROOT" && $RAG_BIN -m rag_tools.cli index-domain --domain $DOMAIN

# Verify
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_$DOMAIN')
print(f'rag__wiki_$DOMAIN: {info.vectors_count} vectors, status={info.status}')
"
```

---

## 5. Add reference article

```bash
DOMAIN="<domain_slug>"
ARTICLE_SLUG="<article-slug>"
WIKI_STUFF="/Volumes/Data/_ai/_wiki/wiki_stuff"

mkdir -p "$WIKI_STUFF/domains/$DOMAIN/references"

# Create article using templates/wiki-reference-article.md
# Required frontmatter: title, type, domain, status, authority, source, tags, updated
# Required sections: Purpose, Summary, Key rules/facts, Eligibility/scope,
#                    Exclusions/caveats, Interactions, Source references, Related pages

# Validate frontmatter
python3 -c "
import yaml, pathlib
path = pathlib.Path('$WIKI_STUFF/domains/$DOMAIN/references/$ARTICLE_SLUG.md')
text = path.read_text()
end = text.index('---', 3)
fm = yaml.safe_load(text[3:end])
required = ['title','type','domain','status','authority','source','updated']
missing = [k for k in required if k not in fm]
print('FAIL: missing:', missing) if missing else print('PASS: frontmatter valid')
"

# Append to log
echo "$(date +%Y-%m-%d)  Added reference: $DOMAIN/$ARTICLE_SLUG" >> \
  "$WIKI_STUFF/log.md"
```

---

## 6. Run retrieval validation

```bash
# Run: prompts/06-post-index-retrieval-validation.md
# Ensure Qdrant is running and collection is indexed first

/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status

python3 -c "
from qdrant_client import QdrantClient
from rag_tools.embeddings import get_embedding_model

client = QdrantClient(host='localhost', port=6333)
model = get_embedding_model()

query = '<your test query>'
vector = model.encode(query).tolist()
results = client.search(
    collection_name='rag__wiki_<domain>',
    query_vector=vector,
    query_filter={'must':[{'key':'wiki_domain','match':{'value':'<domain>'}}]},
    limit=3, with_payload=True
)
for r in results:
    p = r.payload or {}
    print(f'score={r.score:.3f} | {p.get(\"source_file\")} | {p.get(\"heading\")}')
"
```

---

## 7. Rollback / remove bad collection

```bash
BAD_COLLECTION="<collection_name>"

# Confirm before deleting
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('$BAD_COLLECTION')
print(f'About to delete: $BAD_COLLECTION ({info.vectors_count} vectors)')
print('Confirm with: curl -X DELETE http://localhost:6333/collections/$BAD_COLLECTION')
"

# Delete
curl -X DELETE "http://localhost:6333/collections/$BAD_COLLECTION"

# Re-index under correct name (if needed)
# Run: prompts/05-index-wiki-domain.md or prompts/08-index-project-documents.md
```

---

## 8. Full health check

```bash
# Wiki
python3 -c "import yaml; yaml.safe_load(open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml'))" \
  && echo "PASS: domain registry" || echo "FAIL: domain registry"

# RAG tools
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python -m rag_tools.cli doctor

# Qdrant
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections

# Embeddings
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/embedding-smoke-test
```
