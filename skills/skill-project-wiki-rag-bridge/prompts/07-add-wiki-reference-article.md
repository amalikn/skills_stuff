# Prompt 07 — Add Wiki Reference Article

**Purpose:** Create a curated, sourced reference article under a wiki domain.
Must have an explicit source reference. Must not invent missing facts.

**Parameters:**

```
DOMAIN:          <domain_slug>           # e.g. "nbn"
ARTICLE_SLUG:    <article-slug>          # e.g. "dcr-eligibility-rules"
ARTICLE_TITLE:   <Article Title>         # e.g. "DCR Eligibility Rules"
SOURCE_PATH:     <source-path-or-url>    # e.g. "raw/nbn-dcr-annexure-2026.md" or URL
SOURCE_TYPE:     <document|url|extract|derived>
```

**Copy this prompt into Codex or Claude Code. Replace parameters before pasting.**

---

## Pre-flight

```bash
DOMAIN="<domain_slug>"
DOMAIN_DIR="/Volumes/Data/_ai/_wiki/wiki_stuff/domains/$DOMAIN"

# Verify domain exists
test -d "$DOMAIN_DIR" \
  && echo "PASS: domain directory exists" \
  || echo "FAIL: domain missing — run prompt 01 first"

# Verify source reference material exists (if local path)
test -f "$DOMAIN_DIR/../../<SOURCE_PATH>" 2>/dev/null \
  || echo "NOTE: source file not found locally — ensure URL or external source is documented"
```

---

## Step 1 — Determine article placement

Articles go under: `domains/<domain_slug>/references/<article-slug>.md`

```bash
mkdir -p "/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<domain_slug>/references"
```

## Step 2 — Gather source material

Before writing:
- Locate the source material (local raw file, URL, document)
- Read the relevant sections
- Identify key facts, rules, dates, and conditions
- Do NOT paraphrase or invent — extract and structure only what the source says

If source material is unavailable: stop and report. Do not write speculative content.

## Step 3 — Write the article

Use `templates/wiki-reference-article.md` as the structure. Required sections:

1. Frontmatter with: `title`, `type: reference`, `domain`, `status: active`, `authority: shared_reference`, `source`, `tags`, `updated`
2. `## Purpose` — what this article is for and what agents should use it for
3. `## Summary` — dense factual summary (write for retrieval, not for reading)
4. `## Key rules / facts` — bullet list of discrete facts
5. `## Eligibility / scope` — who/what this applies to
6. `## Exclusions / caveats` — what is NOT covered; unresolved edge cases
7. `## Interactions` — how this interacts with other topics/articles
8. `## Source references` — exact citation with path/URL, date extracted, and page/section
9. `## Related pages` — wikilinks to related articles

Write to: `/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<domain_slug>/references/<article-slug>.md`

**Hard rules for content:**
- Every factual claim must trace to the source.
- Dates, thresholds, percentages, and dollar values must be exact — no rounding or approximation unless the source uses approximations.
- If a fact is uncertain or the source is ambiguous, say so explicitly in a caveat.
- Do not blend facts from multiple sources without labelling each source.

## Step 4 — Update domain index

Update `/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<domain_slug>/index.md`:
- Add the article to the Contents table

## Step 5 — Update wiki log.md

```bash
echo "YYYY-MM-DD  Added reference: <domain_slug>/<article-slug> — <ARTICLE_TITLE>" \
  >> /Volumes/Data/_ai/_wiki/wiki_stuff/log.md
```

## Step 6 — Validate frontmatter

```bash
python3 -c "
import yaml, pathlib
path = pathlib.Path('/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<domain_slug>/references/<article-slug>.md')
text = path.read_text()
if not text.startswith('---'):
    print('FAIL: no frontmatter')
else:
    end = text.index('---', 3)
    fm = yaml.safe_load(text[3:end])
    required = ['title', 'type', 'domain', 'status', 'authority', 'source', 'updated']
    missing = [k for k in required if k not in fm]
    print('FAIL: missing frontmatter keys:', missing) if missing else print('PASS: frontmatter valid')
    if fm.get('source', {}).get('path') in (None, '<source-path-or-url>', ''):
        print('FAIL: source.path not filled in')
    else:
        print('PASS: source reference present')
"
```

---

## Output format

```
Verdict: PASS | FAIL

Files created:
  - domains/<domain_slug>/references/<article-slug>.md

Files modified:
  - domains/<domain_slug>/index.md  (Contents table updated)
  - wiki_stuff/log.md               (entry appended)

Checks passed:  <list>
Checks failed:  <list or "none">
Source verified: PASS | NOT_FOUND

Next prompt: 05-index-wiki-domain.md  (to index domain after adding content)
```
