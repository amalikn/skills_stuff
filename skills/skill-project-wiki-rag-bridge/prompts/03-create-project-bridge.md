# Prompt 03 — Create Project Bridge Files

**Purpose:** Create all RAG bridge files for a project. Does NOT index anything.

**Parameters — set all of these before running:**

```
PROJECT_ID:           <project-id>           # e.g. "apn-vocus-profitability"
PROJECT_SLUG:         <project_slug>          # e.g. "vocus_profitability"
PROJECT_NAME:         <Project Name>          # e.g. "Vocus Profitability"
PROJECT_ROOT:         <absolute-path>         # e.g. "/Volumes/Data/_ai/_project/project_stuff/apn/vocus-profitability"
ALLOWED_DOMAINS:      [<domain1>, <domain2>]  # e.g. ["nbn", "vocus"]
DOMAIN_REASONS:       <reason per domain>     # e.g. "NBN DCR reference" / "Vocus billing interpretation"
```

**Copy this prompt into Codex or Claude Code. Replace all parameters before pasting.**

---

## Pre-flight check

```bash
PROJECT_ROOT="<PROJECT_ROOT>"

# Verify project root exists
test -d "$PROJECT_ROOT" && echo "PASS: project root exists" || echo "FAIL: project root not found"

# Check what already exists
ls "$PROJECT_ROOT/rag/" 2>/dev/null && echo "WARN: rag/ already exists" || echo "OK: rag/ will be created"
ls "$PROJECT_ROOT/docs/ai/" 2>/dev/null && echo "OK: docs/ai/ exists" || echo "NOTE: docs/ai/ will be created"
```

---

## Step 1 — Create rag/ directory structure

```bash
mkdir -p "$PROJECT_ROOT/rag/manifests"
mkdir -p "$PROJECT_ROOT/docs/ai"
echo "Created: rag/, rag/manifests/, docs/ai/"
```

## Step 2 — Create rag/project-context.yaml

Use `templates/project-context.yaml` as the base. Fill in all parameters:

- `project.id`: `<PROJECT_ID>`
- `project.slug`: `<PROJECT_SLUG>`
- `project.name`: `<PROJECT_NAME>`
- `project.root`: `<PROJECT_ROOT>`
- `project.collection`: `rag__project_<PROJECT_SLUG>`
- `wiki_dependencies`: one entry per domain in `ALLOWED_DOMAINS`
- `retrieval_policy.collections`: list all `rag__wiki_<domain>` for each allowed domain

Write to: `<PROJECT_ROOT>/rag/project-context.yaml`

## Step 3 — Create rag/retrieval-policy.yaml

Use `templates/retrieval-policy.yaml` as the base. Fill in:

- `project_slug`: `<PROJECT_SLUG>`
- `project_collection`: `rag__project_<PROJECT_SLUG>`
- `allowed_wiki_domains`: list of allowed domain slugs
- `allowed_wiki_collections`: list of `rag__wiki_<domain>` for each
- Keep the full `forbidden_collections` list unchanged

Write to: `<PROJECT_ROOT>/rag/retrieval-policy.yaml`

## Step 4 — Create rag/manifests/project-documents.yaml

Use `templates/project-documents.yaml` as the base. Fill in:
- `project_slug`: `<PROJECT_SLUG>`
- Add known project documents with `index: false` (no indexing without explicit review)

Write to: `<PROJECT_ROOT>/rag/manifests/project-documents.yaml`

## Step 5 — Create docs/ai/wiki-bridge.md

Use `templates/project-wiki-bridge.md` as the base. Fill in all project-specific details.

Write to: `<PROJECT_ROOT>/docs/ai/wiki-bridge.md`

## Step 6 — Update AGENTS.md (if present)

```bash
test -f "$PROJECT_ROOT/AGENTS.md" && echo "UPDATE needed" || echo "SKIP: no AGENTS.md"
```

If `AGENTS.md` exists, append the block from `templates/AGENTS-project-wiki-bridge-block.md`
under a `## RAG / Wiki Bridge` section. Use the `<!-- BEGIN project-wiki-rag-bridge:agents -->`
managed block markers. Fill in project-specific values.

## Step 7 — Update AI_NAVIGATION.md (if present)

```bash
test -f "$PROJECT_ROOT/AI_NAVIGATION.md" && echo "UPDATE needed" || echo "SKIP: no AI_NAVIGATION.md"
```

If present, append the block from `templates/AI_NAVIGATION-project-wiki-bridge-block.md`
under `## RAG and Wiki Access`. Use the `<!-- BEGIN project-wiki-rag-bridge:ai-nav -->` markers.

## Step 8 — Update README.md (if present)

Add a short "RAG / Wiki Bridge" section if `README.md` exists:
- Points to `rag/retrieval-policy.yaml` and `docs/ai/wiki-bridge.md`
- One sentence summary of allowed domains

## Step 9 — Update CHANGELOG.md (if present)

Append entry:
```
YYYY-MM-DD  Added RAG/wiki bridge files (rag/, docs/ai/wiki-bridge.md)
            Allowed wiki domains: <ALLOWED_DOMAINS>
```

## Step 10 — Validate YAML files

```bash
python3 -c "
import yaml, pathlib
for f in ['rag/project-context.yaml', 'rag/retrieval-policy.yaml', 'rag/manifests/project-documents.yaml']:
    path = pathlib.Path('<PROJECT_ROOT>') / f
    try:
        yaml.safe_load(path.read_text())
        print(f'PASS: {f}')
    except Exception as e:
        print(f'FAIL: {f} — {e}')
"
```

---

## Output format

```
Verdict: PROJECT_WIKI_BRIDGE_READY | PROJECT_WIKI_BRIDGE_PARTIAL | PROJECT_WIKI_BRIDGE_NOT_READY

Files created:
  - rag/project-context.yaml
  - rag/retrieval-policy.yaml
  - rag/manifests/project-documents.yaml
  - docs/ai/wiki-bridge.md

Files modified:
  - AGENTS.md             (RAG block appended, or SKIPPED)
  - AI_NAVIGATION.md      (RAG block appended, or SKIPPED)
  - README.md             (RAG section added, or SKIPPED)
  - CHANGELOG.md          (entry appended, or SKIPPED)

Checks passed:  <list>
Checks failed:  <list or "none">

Next prompt: 04-validate-project-policy.md
```
