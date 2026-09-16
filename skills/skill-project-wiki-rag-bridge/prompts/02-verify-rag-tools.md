# Prompt 02 — Verify RAG Tools Readiness

**Purpose:** Confirm that rag-tools, the external venv, Qdrant, and local embeddings are all
operational before any indexing or retrieval work. Read-only — no destructive operations.

**Copy this prompt into Codex or Claude Code to execute.**

---

## Canonical paths

```
RAG_TOOLS_ROOT: /Volumes/Data/_ai/_tool/tools_stuff/rag-tools
RAG_TOOLS_VENV: /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv
RAG_TOOLS_BIN:  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python
```

---

## Check 1 — External venv exists

```bash
test -d /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv \
  && echo "PASS: venv exists" || echo "FAIL: venv missing — run: cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && uv sync"
```

## Check 2 — Python imports

```bash
/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python -c "
import rag_tools
import rag_tools.paths
import rag_tools.config
import rag_tools.collections
import rag_tools.policy
import rag_tools.embeddings
print('PASS: all rag_tools modules import successfully')
"
```

## Check 3 — Doctor (comprehensive health check)

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python -m rag_tools.cli doctor
```

Expected: `RAG_TOOLS_READY` verdict. All 10 checks passing.

If `RAG_TOOLS_PARTIAL`: note which checks failed and continue — some operations still work.
If `RAG_TOOLS_NOT_READY`: stop and fix before proceeding.

## Check 4 — Qdrant status

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
```

Expected: Qdrant container running and HTTP API responding on localhost:6333.

If Qdrant is down:
```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-up
# Wait 5 seconds then re-check:
sleep 5 && /Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-status
```

## Check 5 — List existing collections

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections
```

Note all existing collection names. Verify:
- No forbidden collections present (`default`, `documents`, `knowledge`, `rag__all`, `rag__wiki_all`, `rag__global_all_docs`)
- Collection naming follows `rag__project_*` or `rag__wiki_*` or `rag__test_*` patterns only

## Check 6 — Embedding smoke test

```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/embedding-smoke-test
```

Expected: model loads, generates 384-dimensional vectors, reports success.

## Check 7 — pytest (optional but recommended)

```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools && \
  /Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python -m pytest tests/ -v --tb=short
```

Expected: all tests pass. Note any failures without fixing them here — report them.

---

## Output format

```
Check 1 — venv:            PASS | FAIL
Check 2 — imports:         PASS | FAIL
Check 3 — doctor:          RAG_TOOLS_READY | RAG_TOOLS_PARTIAL | RAG_TOOLS_NOT_READY
Check 4 — Qdrant status:   PASS (running) | FAIL (down)
Check 5 — collections:     <list of existing collections, or "empty">
Check 6 — embeddings:      PASS (384-dim) | FAIL
Check 7 — pytest:          PASS | FAIL | SKIPPED

Forbidden collections found: <list or "none">

Verdict: RAG_TOOLS_READY | RAG_TOOLS_PARTIAL | RAG_TOOLS_NOT_READY

Next prompt: 03-create-project-bridge.md
```
