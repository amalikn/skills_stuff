# Setup — skill-project-wiki-rag-bridge

Step-by-step install and first-use guide for a new machine or agent environment.

## Contents

- [Prerequisites](#prerequisites)
- [rag-tools verification](#rag-tools-verification)
- [Skill installation](#skill-installation)
- [First-use workflow](#first-use-workflow)
- [Qdrant setup](#qdrant-setup)
- [Validation](#validation)

---

## Prerequisites

| Requirement | Notes |
|---|---|
| `rag-tools` venv | Must exist at `tools-working-cache/rag-tools/.venv/` (see below) |
| Qdrant | Running locally at `http://localhost:6333`; Docker recommended |
| Python 3.11+ | Required by rag-tools; managed inside venv — no global install needed |
| `sentence-transformers/all-MiniLM-L6-v2` | Downloaded on first use; HuggingFace cache |

---

## rag-tools verification

The rag-tools venv lives at the **working-cache** path — not inside `tools_stuff`:

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin

# Confirm binary exists
ls "$VENV/rag-tools"

# Run health check
$VENV/rag-tools doctor

# Confirm Qdrant connection
$VENV/rag-tools qdrant-status

# Confirm embedding model loads
$VENV/rag-tools embedding-smoke-test
```

If the binary is missing, the venv needs to be rebuilt. See `_tool/tools_stuff/rag-tools/README.md` for install steps.

> **Note:** Prompts `02b` and `02c` define a `RAG_TOOLS` variable at the top. Verify this variable points to `tools-working-cache/rag-tools/.venv/bin` before running either prompt.

---

## Skill installation

Install `SKILL.md` to all agent runtime directories. The canonical source is this repo — never edit runtime installs directly.

```bash
SKILL_SRC="/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-project-wiki-rag-bridge/SKILL.md"

# Claude Code
mkdir -p ~/.claude/skills/skill-project-wiki-rag-bridge
cp "$SKILL_SRC" ~/.claude/skills/skill-project-wiki-rag-bridge/SKILL.md

# Codex
mkdir -p ~/.codex/skills/skill-project-wiki-rag-bridge
cp "$SKILL_SRC" ~/.codex/skills/skill-project-wiki-rag-bridge/SKILL.md

# Hermes
mkdir -p ~/.hermes/skills/domain/skill-project-wiki-rag-bridge
cp "$SKILL_SRC" ~/.hermes/skills/domain/skill-project-wiki-rag-bridge/SKILL.md
```

After any SKILL.md update, re-run the copy commands above to sync all three targets.

---

## First-use workflow

Run these prompts in sequence for a new project:

```
prompts/00-verify-wiki-operational-state.md   ← confirm wiki + rag-tools ready
prompts/01-create-wiki-domain.md              ← create domain if needed
prompts/02-verify-rag-tools.md                ← smoke-test rag-tools commands
prompts/02b-profile-and-recommend-strategy.md ← profile project docs (read-only)
prompts/02c-benchmark-retrieval-routes.md     ← benchmark key source files
prompts/03-create-project-bridge.md           ← create bridge files in project repo
prompts/04-validate-project-policy.md         ← validate retrieval-policy.yaml
```

Before indexing:

```
prompts/05-index-wiki-domain.md               ← dry-run first, then confirm
prompts/06-post-index-retrieval-validation.md ← test retrieval; check citations
```

---

## Qdrant setup

```bash
# Start Qdrant via Docker
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools
bash scripts/qdrant-up

# Verify
curl http://localhost:6333/healthz
```

Collection naming rules enforced by this skill:

| Pattern | Use |
|---|---|
| `rag__wiki_<domain>` | Wiki domain collection |
| `rag__project_<slug>` | Project document collection |

Forbidden names: `rag__all`, `rag__wiki_all`, `default`, `documents`, `knowledge`, `main`.

---

## Validation

Run after setup to confirm everything is wired correctly:

```bash
VENV=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin

# 1. rag-tools health
$VENV/rag-tools doctor

# 2. Qdrant status
$VENV/rag-tools qdrant-status

# 3. List indexed collections
$VENV/rag-tools collections

# 4. Validate a project's retrieval policy
$VENV/rag-tools validate-policy <project>/rag/retrieval-policy.yaml

# 5. YAML parse all schemas
python3 -c "
import yaml, pathlib
for f in pathlib.Path('schemas').glob('*.yaml'):
    yaml.safe_load(f.read_text())
    print(f'PASS {f.name}')
"
```

See `checklists/rag-tools-readiness.md` and `checklists/indexing-readiness.md` for the full gate checklists before live indexing.
