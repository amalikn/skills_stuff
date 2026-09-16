# Checklist: RAG Tools Readiness

**Use before:** any indexing or retrieval operation.
**Blocks:** indexing if NOT_READY.

---

## External venv

- [ ] `/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/` — exists
- [ ] `/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python` — executable
- [ ] `python -c "import rag_tools"` — imports without error
- [ ] All core modules import: `paths`, `config`, `collections`, `policy`, `embeddings`

## UV sync

- [ ] `uv sync` with `UV_PROJECT_ENVIRONMENT` set runs without error
- [ ] Lock file (`uv.lock`) is present and current
- [ ] No conflicting `VIRTUAL_ENV` shell variable causing warnings (warn only — UV still works)

## Doctor

- [ ] `rag_tools.cli doctor` exits 0 or reports `RAG_TOOLS_READY`
- [ ] All 10 health checks pass:
  - Canonical directories
  - Config file (live or example fallback)
  - Python imports
  - LlamaIndex availability
  - Docker daemon
  - Qdrant connectivity
  - Embedding model (384-dim output)
  - Collection policy functions
  - Wiki roots
  - Domain registry

## Qdrant

- [ ] Docker context is set correctly (OrbStack, Colima, or Docker Desktop — whichever is running)
- [ ] `qdrant-status` confirms container running
- [ ] `localhost:6333` HTTP API responds (200 OK)
- [ ] `qdrant-collections` lists existing collections without error

## Embedding smoke test

- [ ] `scripts/embedding-smoke-test` completes without error
- [ ] Output confirms 384-dimensional vectors
- [ ] Model (`all-MiniLM-L6-v2`) loads from HuggingFace cache (no download required)

## Collection audit (no forbidden names)

- [ ] No collection named `default`, `documents`, `knowledge`, `main`
- [ ] No collection named `rag__all`, `rag__wiki_all`, `rag__global_all_docs`
- [ ] All existing collections match `rag__project_*`, `rag__wiki_*`, or `rag__test_*` patterns

## pytest

- [ ] `pytest tests/ -v` passes (all tests green) — WARN if skipped, FAIL if red

---

## Verdict

```
RAG_TOOLS_READY    — all checks pass
RAG_TOOLS_PARTIAL  — some checks failing (Qdrant down, venv issues, but imports work)
RAG_TOOLS_NOT_READY — venv missing, imports fail, or Qdrant unreachable
```
