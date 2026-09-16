# Prompt 04 — Validate Project Retrieval Policy

**Purpose:** Validate the project's retrieval policy against YAML syntax rules, rag-tools
flat validator, and collection-naming policy. No indexing.

**Parameters:**

```
PROJECT_ROOT: <PROJECT_ROOT>    # e.g. "/Volumes/Data/_ai/_project/project_stuff/apn/vocus-profitability"
PROJECT_SLUG: <PROJECT_SLUG>    # e.g. "vocus_profitability"
```

**Copy this prompt into Codex or Claude Code. Replace parameters before pasting.**

---

## Check 1 — Files exist

```bash
PROJECT_ROOT="<PROJECT_ROOT>"

for f in "rag/retrieval-policy.yaml" "rag/project-context.yaml" "rag/manifests/project-documents.yaml" "docs/ai/wiki-bridge.md"; do
  test -f "$PROJECT_ROOT/$f" \
    && echo "PASS: $f" \
    || echo "FAIL: $f missing — run prompt 03 first"
done
```

## Check 2 — YAML parse (all rag/ files)

```bash
python3 -c "
import yaml, pathlib, sys
root = pathlib.Path('<PROJECT_ROOT>')
errors = []
for f in ['rag/retrieval-policy.yaml', 'rag/project-context.yaml', 'rag/manifests/project-documents.yaml']:
    path = root / f
    if not path.exists():
        errors.append(f'MISSING: {f}')
        continue
    try:
        yaml.safe_load(path.read_text())
        print(f'PASS: {f} parses')
    except Exception as e:
        errors.append(f'FAIL: {f} — {e}')
for e in errors:
    print(e)
if errors:
    sys.exit(1)
"
```

## Check 3 — Flat validator keys present in retrieval-policy.yaml

```bash
python3 -c "
import yaml
required_keys = [
    'version', 'project_slug', 'project_collection',
    'allowed_wiki_domains', 'allowed_wiki_collections',
    'forbidden_collections', 'required_filters', 'citation_rules'
]
with open('<PROJECT_ROOT>/rag/retrieval-policy.yaml') as f:
    policy = yaml.safe_load(f)
missing = [k for k in required_keys if k not in policy]
if missing:
    print(f'FAIL: missing flat validator keys: {missing}')
else:
    print('PASS: all required flat validator keys present')
slug = policy.get('project_slug', '')
if slug != '<PROJECT_SLUG>':
    print(f'FAIL: project_slug mismatch — got {slug!r}, expected <PROJECT_SLUG>')
else:
    print(f'PASS: project_slug = {slug!r}')
"
```

## Check 4 — rag-tools validate-policy

```bash
cd "<PROJECT_ROOT>" && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python \
  -m rag_tools.cli validate-policy rag/retrieval-policy.yaml
```

Expected: validator exits 0 with no errors.

## Check 5 — Collection name compliance

```bash
python3 -c "
import yaml, re
with open('<PROJECT_ROOT>/rag/retrieval-policy.yaml') as f:
    policy = yaml.safe_load(f)

allowed_pattern = re.compile(r'^rag__(project|wiki|test)_[a-z0-9_]+$')
forbidden = set(policy.get('forbidden_collections', []))

# Check project collection
pc = policy.get('project_collection', '')
if allowed_pattern.match(pc) and pc not in forbidden:
    print(f'PASS: project_collection = {pc!r}')
else:
    print(f'FAIL: project_collection {pc!r} invalid or forbidden')

# Check wiki collections
for c in policy.get('allowed_wiki_collections', []):
    if allowed_pattern.match(c) and c not in forbidden:
        print(f'PASS: wiki collection = {c!r}')
    else:
        print(f'FAIL: wiki collection {c!r} invalid or forbidden')
"
```

## Check 6 — Qdrant reachable and collection audit

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
echo "---"
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections
```

Note whether declared collections exist in Qdrant (they may not yet — that is OK at this stage).
Flag if any forbidden collection names exist in Qdrant.

## Check 7 — Justfile tasks (if justfile present)

```bash
test -f "<PROJECT_ROOT>/justfile" && \
  grep -n 'rag-' "<PROJECT_ROOT>/justfile" || echo "SKIP: no justfile"
```

---

## Output format

```
Verdict: PROJECT_RAG_POLICY_VALIDATED | PROJECT_RAG_POLICY_PARTIAL | PROJECT_RAG_POLICY_NOT_READY

Check 1 — files exist:         PASS | FAIL (list missing)
Check 2 — YAML parse:          PASS | FAIL
Check 3 — flat validator keys: PASS | FAIL (list missing)
Check 4 — rag-tools validate:  PASS | FAIL
Check 5 — collection names:    PASS | FAIL
Check 6 — Qdrant status:       running | down
           Existing collections: <list>
           Forbidden found:      <list or "none">
Check 7 — justfile tasks:      PASS | SKIP | MISSING

Next prompt: 07-add-wiki-reference-article.md  (add content before indexing)
             05-index-wiki-domain.md           (if content already exists)
```
