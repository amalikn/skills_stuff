# Prompt 00 — Verify Wiki Operational State

**Purpose:** Validate the shared wiki infrastructure before any bridge or indexing work.
This prompt is read-only. It must not install, index, or delete anything.

**Copy this prompt into Codex or Claude Code to execute.**

---

## Instructions

You are verifying that the shared Karpathy-style LLM wiki is operationally ready.

Run the following checks in order. Report the result of each check (PASS / FAIL / WARN).
Do not stop on the first failure — run all checks and report the full picture.

### Check 1 — Wiki root directories

```bash
ls /Volumes/Data/_ai/_wiki/
```

Verify these directories exist:
- `wiki_stuff/` — content vault (REQUIRED)
- `wiki-data/` — metadata/policy layer (REQUIRED)
- `wiki-runtime/` — runtime/reports area (WARN if missing)
- `wiki-working-cache/` — generated/cache area (WARN if missing)

### Check 2 — Wiki governance files

```bash
ls /Volumes/Data/_ai/_wiki/wiki_stuff/
```

Verify these files exist:
- `README.md` — REQUIRED
- `AGENTS.md` — REQUIRED
- `AI_NAVIGATION.md` — REQUIRED
- `SCHEMA.md` — REQUIRED
- `context-map.yaml` — REQUIRED
- `index.md` — REQUIRED
- `log.md` — REQUIRED
- `CHANGELOG.md` — WARN if missing

### Check 3 — Wiki metadata layer

```bash
ls /Volumes/Data/_ai/_wiki/wiki-data/
```

Verify:
- `domain-registry.yaml` — REQUIRED
- `qdrant-collection-policy.md` — REQUIRED
- `project-dependency-model.schema.yaml` — WARN if missing

### Check 4 — Domain registry validity

```bash
python3 -c "
import yaml, sys
with open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)
domains = reg.get('domains', [])
print(f'Domains registered: {len(domains)}')
for d in domains:
    print(f'  - {d[\"domain\"]} → {d[\"qdrant_collection\"]} [{d[\"status\"]}]')
rules = reg.get('rules', {})
if not rules.get('disallow_global_collection'):
    print('WARN: disallow_global_collection not set')
"
```

Expected: at least 1 active domain, `disallow_global_collection: true`.

### Check 5 — Wiki domain directories

```bash
ls /Volumes/Data/_ai/_wiki/wiki_stuff/domains/
```

For each domain in the registry, verify:
- `domains/<domain>/` directory exists
- `domains/<domain>/index.md` exists (WARN if missing)

```bash
for domain in nbn vocus mcp; do
  echo -n "$domain/index.md: "
  test -f /Volumes/Data/_ai/_wiki/wiki_stuff/domains/$domain/index.md && echo PASS || echo WARN
done
```

### Check 6 — Frontmatter spot-check

```bash
python3 -c "
import pathlib, yaml
wiki = pathlib.Path('/Volumes/Data/_ai/_wiki/wiki_stuff')
files = list(wiki.glob('domains/**/*.md'))[:5]
for f in files:
    text = f.read_text()
    if text.startswith('---'):
        try:
            fm_end = text.index('---', 3)
            yaml.safe_load(text[3:fm_end])
            print(f'OK: {f.relative_to(wiki)}')
        except Exception as e:
            print(f'FAIL: {f.relative_to(wiki)} — {e}')
    else:
        print(f'WARN: {f.relative_to(wiki)} — no frontmatter')
"
```

### Check 7 — Qdrant collection policy

```bash
cat /Volumes/Data/_ai/_wiki/wiki-data/qdrant-collection-policy.md
```

Verify: forbidden names listed, required metadata fields documented.

---

## Output format

Report each check as:
```
[ PASS / FAIL / WARN ]  Check N — <name>
                         <detail if not PASS>
```

Then emit the verdict:

```
Verdict: WIKI_OPERATIONAL_READY | WIKI_OPERATIONAL_PARTIAL | WIKI_OPERATIONAL_NOT_READY

READY    = all REQUIRED checks pass
PARTIAL  = some REQUIRED checks fail or WARN checks flag issues
NOT_READY = one or more critical components absent
```

**Do not proceed to prompt 01 or beyond if verdict is NOT_READY.**
Fix the identified issues first.
