# Prompt 09 — Troubleshoot RAG Bridge

**Purpose:** Diagnose failures in the wiki/RAG bridge pipeline. Work through each section
that matches the symptom. Do not apply fixes without confirming the diagnosis.

**Copy this prompt into Codex or Claude Code to execute.**

---

## Symptom A — Missing or broken venv

**Symptom:** `ModuleNotFoundError: No module named 'rag_tools'` or venv not found.

```bash
# Check venv exists
test -d /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv \
  && echo "venv exists" || echo "venv MISSING"

# Check UV knows the project
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && uv sync --dry-run
```

**Fix:** Rebuild the venv:
```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools
UV_PROJECT_ENVIRONMENT=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv uv sync
```

## Symptom B — UV ignores venv / wrong environment

**Symptom:** UV warns about conflicting `VIRTUAL_ENV` environment variable.

```bash
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
echo "UV_PROJECT_ENVIRONMENT=$UV_PROJECT_ENVIRONMENT"
```

**Fix:** Set `UV_PROJECT_ENVIRONMENT` explicitly in your shell or justfile. UV warns but respects `UV_PROJECT_ENVIRONMENT` over the shell's `VIRTUAL_ENV`.

## Symptom C — Qdrant down / unreachable

**Symptom:** `Connection refused` on localhost:6333.

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
docker ps | grep qdrant
```

**Fix:** Start Qdrant:
```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-up
sleep 5
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
```

If qdrant-up fails, check Docker context:
```bash
docker context ls
docker context use orbstack  # or colima, depending on what's running
```

## Symptom D — Domain registry missing or invalid

**Symptom:** `KeyError: 'domains'` or registry file not found.

```bash
test -f /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml \
  && echo "EXISTS" || echo "MISSING"
python3 -c "import yaml; yaml.safe_load(open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml'))" \
  && echo "VALID YAML" || echo "INVALID YAML"
```

**Fix:** If missing, bootstrap from the `domain-registry.yaml` in wiki-data (run prompt 00 first to understand what should be there).

## Symptom E — Policy validator fails

**Symptom:** `rag-tools validate-policy` exits non-zero.

```bash
cd <PROJECT_ROOT>
/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli validate-policy rag/retrieval-policy.yaml 2>&1
```

Common causes:
- Missing flat validator keys (check `schemas/retrieval-policy.schema.yaml`)
- `project_slug` mismatch
- `allowed_wiki_collections` not matching `allowed_wiki_domains`
- Forbidden collection name in `allowed_wiki_collections`

## Symptom F — Forbidden collection referenced

**Symptom:** Policy references `default`, `documents`, `rag__wiki_all`, etc.

```bash
python3 -c "
import yaml
forbidden = {'rag__global_all_docs','rag__wiki_all','rag__all','default','documents','knowledge','main'}
with open('<PROJECT_ROOT>/rag/retrieval-policy.yaml') as f:
    policy = yaml.safe_load(f)
hits = []
for k in ['project_collection'] + policy.get('allowed_wiki_collections', []):
    if k in forbidden: hits.append(k)
print('FORBIDDEN FOUND:', hits) if hits else print('OK: no forbidden collection names')
"
```

**Fix:** Rename the collection in the policy. The collection must not exist with that name in Qdrant either — delete and re-index if needed.

## Symptom G — Missing required metadata in results

**Symptom:** Query results missing `source_file`, `heading`, `section_path`, or `collection` fields.

```bash
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
results = client.scroll('rag__wiki_<domain>', limit=3, with_payload=True)
required = ['collection', 'source_file', 'heading', 'section_path', 'authority']
for point, _ in zip(*results):
    p = point.payload or {}
    missing = [k for k in required if k not in p]
    print(f'ID {point.id}: missing={missing}')
"
```

**Fix:** Re-index with updated rag-tools that emits all required fields. Check `rag_tools.collections` module for payload construction.

## Symptom H — Empty collection (scaffold-only)

**Symptom:** Collection exists with 0 vectors.

```bash
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
for c in client.get_collections().collections:
    info = client.get_collection(c.name)
    print(c.name, '→', info.vectors_count, 'vectors')
"
```

**Fix:** Domain content exists but indexing failed or was not run. Check domain directory for markdown files, then re-run prompt 05.

## Symptom I — No useful retrieval (low scores)

**Symptom:** Queries return results but scores are all < 0.3.

Likely causes:
- Domain content is too sparse or too generic
- Query is not semantically similar to indexed content
- Wrong embedding model (model mismatch between index and query time)

```bash
# Check embedding model used
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/embedding-smoke-test
```

All queries and indexing must use the same model (`all-MiniLM-L6-v2`, 384 dimensions).

## Symptom J — Project accidentally indexed raw data

**Symptom:** Sensitive file paths visible in collection payloads.

```bash
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
results, _ = client.scroll('rag__project_<PROJECT_SLUG>', limit=50, with_payload=True)
sensitive_types = {'raw', 'communication'}
for p in results:
    payload = p.payload or {}
    if payload.get('source_type') in sensitive_types:
        print('ALERT: sensitive doc in collection:', payload.get('source_file'))
"
```

**Fix:**
1. Delete the collection: `curl -X DELETE http://localhost:6333/collections/rag__project_<PROJECT_SLUG>`
2. Fix the manifest — set all sensitive/raw docs to `index: false`
3. Re-index using prompt 08 with corrected manifest

---

## Output format

```
Symptom identified:  <A through J or custom description>
Root cause:          <diagnosis>
Fix applied:         <what was done>
Fix verified:        PASS | FAIL | PENDING

Verdict: RAG_TOOLS_READY | RAG_TOOLS_PARTIAL | RAG_TOOLS_NOT_READY
```
