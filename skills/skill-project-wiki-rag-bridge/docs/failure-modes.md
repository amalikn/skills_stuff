# Failure Modes

## FM-01 — Scaffold-only collection

**What:** Collection exists in Qdrant with 0 vectors. Policy validates. Queries return nothing.

**Cause:** `rag-tools index-domain` was never run, or it exited before indexing any chunks.

**Detection:**
```python
from qdrant_client import QdrantClient
client = QdrantClient(host='localhost', port=6333)
info = client.get_collection('rag__wiki_nbn')
print(info.vectors_count)  # 0
```

**Fix:** Re-run prompt/05. Check domain directory has markdown files before indexing.

---

## FM-02 — Empty collection (indexing failed silently)

**What:** Index command appeared to succeed but collection has 0 or very low vector count.

**Cause:** Domain directory had no eligible files, or embedding failed quietly on all chunks.

**Detection:** Compare dry-run chunk count with actual vectors_count after indexing.

**Fix:** Check domain markdown files for frontmatter errors. Run embedding smoke test.
Re-run with `--dry-run` to confirm chunk count, then live index.

---

## FM-03 — Policy validates but no retrieval

**What:** `rag-tools validate-policy` passes. Qdrant is running. Queries return 0 results.

**Cause:** Collection is empty (FM-01/FM-02), or wiki_domain filter excludes all results,
or embedding model mismatch between index time and query time.

**Detection:** Query without domain filter. Check if any results come back.
```python
results = client.search(collection_name='rag__wiki_nbn', query_vector=vector, limit=3)
# vs
results_filtered = client.search(..., query_filter={"must":[{"key":"wiki_domain","match":{"value":"nbn"}}]}, ...)
```

**Fix:** Re-index with correct metadata. Confirm model is `all-MiniLM-L6-v2` at both index and query.

---

## FM-04 — Global collection pollution

**What:** A collection named `default`, `documents`, `rag__all`, etc. exists in Qdrant.

**Cause:** Tooling defaults, an external experiment, or a policy violation during indexing.

**Detection:**
```bash
/Volumes/Data/_ai/_tool/tools_stuff/rag-tools/scripts/qdrant-collections
# Look for names not matching rag__project_* | rag__wiki_* | rag__test_*
```

**Fix:** Delete the offending collection immediately:
```bash
curl -X DELETE http://localhost:6333/collections/<forbidden_name>
```
Update any project policy that references it. Re-index under the correct name.

---

## FM-05 — Ambiguous wikilinks

**What:** Articles reference `[[some-page]]` but `some-page.md` does not exist or the slug is wrong.

**Cause:** Wikilink slug not matching filename, or referenced article not yet created.

**Detection:**
```bash
grep -r '\[\[' /Volumes/Data/_ai/_wiki/wiki_stuff/domains/ --include='*.md' | \
  grep -v '\.md\]\]' | head -20
```

**Impact:** Broken links don't break retrieval but reduce knowledge graph navigability.

**Fix:** Either create the missing article or correct the wikilink slug.

---

## FM-06 — Missing frontmatter

**What:** A wiki article has no YAML frontmatter or invalid frontmatter.

**Cause:** Article was added without following the template.

**Detection:**
```python
import pathlib, yaml
for f in pathlib.Path('/Volumes/Data/_ai/_wiki/wiki_stuff/domains').rglob('*.md'):
    t = f.read_text()
    if not t.startswith('---'):
        print(f'NO FRONTMATTER: {f}')
    else:
        try: yaml.safe_load(t.split('---')[1])
        except: print(f'INVALID FRONTMATTER: {f}')
```

**Impact:** Indexing may succeed but metadata fields will be missing, breaking citation.

**Fix:** Add or fix frontmatter using `templates/wiki-reference-article.md` as the structure.

---

## FM-07 — Qdrant missing / unreachable

**What:** All Qdrant operations fail with `Connection refused` on localhost:6333.

**Cause:** Qdrant container not running. Docker context pointing to wrong runtime.

**Fix:** See prompt/09 Symptom C. Run `qdrant-up`. Check `docker context ls`.

---

## FM-08 — Missing external venv

**What:** `No module named 'rag_tools'` or `python: command not found` from justfile tasks.

**Cause:** Venv at `tools-working-cache/rag-tools/.venv` was not created or was deleted.

**Fix:** See prompt/09 Symptom A.
```bash
cd /Volumes/Data/_ai/_tool/tools_stuff/rag-tools
UV_PROJECT_ENVIRONMENT=/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv uv sync
```

---

## FM-09 — Wrong UV environment

**What:** UV installs packages to wrong location. Shell `VIRTUAL_ENV` conflicts.

**Cause:** `VIRTUAL_ENV` env var set to a different venv. UV warns but proceeds to `UV_PROJECT_ENVIRONMENT`.

**Detection:** UV warning: `Ignoring existing virtual environment linked to...`

**Fix:** Set `UV_PROJECT_ENVIRONMENT` explicitly. The warning is safe to ignore if the target venv is correct.

---

## FM-10 — Project accidentally indexed raw data

**What:** Sensitive file paths (CSV, raw invoices, communications) appear in project collection payloads.

**Cause:** Project manifest had `index: true` on a raw or sensitive document, or `default_index` was set to `true`.

**Detection:** See prompt/09 Symptom J.

**Fix:**
1. Delete the project collection: `curl -X DELETE http://localhost:6333/collections/rag__project_<slug>`
2. Fix manifest: set `index: false` on all sensitive/raw/communications documents.
3. Confirm `rules.default_index: false`.
4. Re-run prompt/08 with corrected manifest.
5. Verify collection no longer contains sensitive paths.
