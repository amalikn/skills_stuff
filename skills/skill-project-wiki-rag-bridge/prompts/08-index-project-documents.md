# Prompt 08 — Index Project Documents

**Purpose:** Index project-specific documents into the project Qdrant collection.
Only indexes documents explicitly declared with `index: true` in the project manifest.
Raw, sensitive, and communications data require additional approval before indexing.

**Parameters:**

```
PROJECT_ROOT:    <PROJECT_ROOT>
PROJECT_SLUG:    <PROJECT_SLUG>
```

**Copy this prompt into Codex or Claude Code. Replace parameters before pasting.**

---

## Pre-flight — BLOCKING

### PF-0: Profile / strategy gate

Every candidate project document must have a profile and a recorded retrieval strategy before
this prompt proceeds. This gate is non-negotiable.

**Checks:**

- [ ] BLOCKING: `rag/retrieval-strategy.yaml` exists in the project root.
- [ ] BLOCKING: Every document with `index: true` in the manifest has a corresponding entry in
  `rag/retrieval-strategy.yaml` with `document_class` and `rag_suitability` recorded.
- [ ] BLOCKING: `index: true` is only present in the manifest if `rag_suitability` is `suitable`
  or `partially_suitable` in `retrieval-strategy.yaml`. Documents with `rag_suitability:
  not_suitable` must have `index: true` removed before proceeding.
- [ ] BLOCKING: Structured, tabular, or exact-fact documents (`structured_markdown_reference`,
  `financial_rate_card`, `invoice_or_billing_report`, `tabular_dataset`) must use direct or
  table lookup as primary route. These documents may only be indexed if:
    (a) `rag_suitability: partially_suitable` is confirmed by `recommend-strategy`, AND
    (b) `benchmark_status: passed` is recorded in `retrieval-strategy.yaml`, AND
    (c) The benchmark result was `HYBRID_RAG_FIRST`, `HYBRID_DIRECT_FIRST`, or `RAG_FIRST`.
- [ ] BLOCKING: Raw or sensitive documents remain blocked unless explicitly approved (existing
  PF-2 gate applies in addition to this gate).
- [ ] WARN: If `benchmark_status: not_run` for any candidate, run prompt 02c before proceeding.

**How to verify:**

```bash
python3 -c "
import yaml
from pathlib import Path

root = Path('<PROJECT_ROOT>')
strategy_path = root / 'rag/retrieval-strategy.yaml'
manifest_path = root / 'rag/manifests/project-documents.yaml'

strategy = yaml.safe_load(strategy_path.read_text()) if strategy_path.exists() else {}
manifest = yaml.safe_load(manifest_path.read_text()) if manifest_path.exists() else {}

strategy_docs = {d['document_id']: d for d in strategy.get('documents', [])}
manifest_docs = [d for d in manifest.get('documents', []) if d.get('index') == True]

print(f'Candidate documents (index: true): {len(manifest_docs)}')
for d in manifest_docs:
    doc_id = d.get('id', d.get('document_id', '?'))
    strat = strategy_docs.get(doc_id, {})
    suitability = strat.get('rag_suitability', 'NOT_FOUND')
    bench = strat.get('benchmark_status', 'NOT_FOUND')
    ok = suitability in ('suitable', 'partially_suitable') and bench != 'failed'
    print(f'  {\"PASS\" if ok else \"FAIL\"}: {doc_id} | suitability={suitability} | benchmark={bench}')
"
```

**PF-0 verdict:**

```
PF-0: PASS — all candidates have strategy confirmed; structured/tabular docs benchmarked
PF-0: PARTIAL — some candidates pending benchmark; do not index those until 02c complete
PF-0: FAIL — candidates with not_suitable or failed benchmark in indexable set
```

---

### PF-1: Manifest exists and is valid

```bash
python3 -c "
import yaml
with open('<PROJECT_ROOT>/rag/manifests/project-documents.yaml') as f:
    manifest = yaml.safe_load(f)
rules = manifest.get('rules', {})
print('default_index:', rules.get('default_index'))
if rules.get('default_index') != False:
    print('FAIL: default_index must be false')
else:
    print('PASS: default_index is false')
docs = manifest.get('documents', [])
indexable = [d for d in docs if d.get('index') == True and not d.get('sensitive', False)]
print(f'Documents eligible for indexing: {len(indexable)}')
for d in indexable:
    print(f'  - {d[\"id\"]}: {d[\"path\"]}')
"
```

### PF-2: No sensitive or communications documents in indexable set

```bash
python3 -c "
import yaml
with open('<PROJECT_ROOT>/rag/manifests/project-documents.yaml') as f:
    manifest = yaml.safe_load(f)
docs = manifest.get('documents', [])
problems = [
    d for d in docs
    if d.get('index') == True and (
        d.get('sensitive', False) or
        d.get('type') in ('communication', 'raw')
    )
]
if problems:
    print('FAIL: sensitive/communications documents are flagged index: true — requires explicit approval:')
    for d in problems:
        print(f'  - {d[\"id\"]}: {d[\"path\"]} [type={d.get(\"type\")}, sensitive={d.get(\"sensitive\")}]')
else:
    print('PASS: no sensitive or communications documents in indexable set')
"
```

If any sensitive or communications documents appear in the indexable set, **stop** and report.
Do not proceed until these are either removed from the indexable set or have explicit written approval in the manifest `notes` field.

### PF-3: Source files exist

```bash
python3 -c "
import yaml, pathlib
root = pathlib.Path('<PROJECT_ROOT>')
with open(root / 'rag/manifests/project-documents.yaml') as f:
    manifest = yaml.safe_load(f)
docs = [d for d in manifest.get('documents', []) if d.get('index') == True]
for d in docs:
    path = root / d['path']
    print('PASS' if path.exists() else 'FAIL (missing)', d['id'], d['path'])
"
```

### PF-4: Policy validated

Run prompt 04 and confirm `PROJECT_RAG_POLICY_VALIDATED` before proceeding.

### PF-5: Qdrant running

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
```

---

## Step 1 — Dry-run

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli index-project \
  --project-slug <PROJECT_SLUG> \
  --manifest "<PROJECT_ROOT>/rag/manifests/project-documents.yaml" \
  --dry-run
```

Review output:
- Chunk count reasonable?
- No raw/sensitive file paths appearing?
- Collection shown as `rag__project_<PROJECT_SLUG>`?

**Stop if dry-run output looks wrong.**

## Step 2 — Confirm before live index

- [ ] Dry-run chunk count is sensible
- [ ] No raw/sensitive paths in dry-run
- [ ] Collection name correct
- [ ] Operator confirmed

## Step 3 — Live index

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli index-project \
  --project-slug <PROJECT_SLUG> \
  --manifest "<PROJECT_ROOT>/rag/manifests/project-documents.yaml"
```

## Step 4 — Verify

```bash
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__project_<PROJECT_SLUG>')
print(f'Collection: rag__project_<PROJECT_SLUG>')
print(f'Vectors count: {info.vectors_count}')
"
```

---

## Output format

```
Verdict: WIKI_DOMAIN_INDEXED (project collection) | WIKI_DOMAIN_INDEX_PARTIAL | WIKI_DOMAIN_INDEX_FAILED

Collection:     rag__project_<PROJECT_SLUG>
Documents indexed: <count>
Chunks:         <count>

Pre-flight checks:
  PF-1 manifest valid:        PASS | FAIL
  PF-2 no sensitive in set:   PASS | FAIL
  PF-3 files exist:           PASS | FAIL (list missing)
  PF-4 policy validated:      PASS | ASSUMED
  PF-5 Qdrant running:        PASS | FAIL

Next prompt: 06-post-index-retrieval-validation.md
```
