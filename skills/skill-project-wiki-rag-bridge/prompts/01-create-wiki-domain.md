# Prompt 01 — Create Wiki Domain

**Purpose:** Create a new wiki domain directory structure and register it in the domain registry.
This prompt does NOT index the domain into Qdrant. Indexing is a separate step (prompt 05).

**Parameters to set before running:**

```
DOMAIN_SLUG:        <domain_slug>        # e.g. "nbn", "vocus", "mcp"
DOMAIN_NAME:        <Domain Name>        # e.g. "NBN", "Vocus"
DOMAIN_DESCRIPTION: <description>        # e.g. "NBN WBA/DCR rebate and eligibility reference"
```

**Copy this prompt into Codex or Claude Code. Replace parameters before pasting.**

---

## Pre-flight check

Before creating anything, run:

```bash
# Check if domain already exists
ls /Volumes/Data/_ai/_wiki/wiki_stuff/domains/
grep 'domain: "<DOMAIN_SLUG>"' /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml 2>/dev/null \
  && echo "WARN: domain already in registry" || echo "OK: domain not yet registered"
```

If the domain already exists, verify it has content and stop. Do not recreate.

---

## Step 1 — Create domain directory structure

```bash
DOMAIN="<DOMAIN_SLUG>"
WIKI_DOMAINS="/Volumes/Data/_ai/_wiki/wiki_stuff/domains"

mkdir -p "$WIKI_DOMAINS/$DOMAIN/references"
echo "Created: $WIKI_DOMAINS/$DOMAIN/"
echo "Created: $WIKI_DOMAINS/$DOMAIN/references/"
```

## Step 2 — Create domain index page

Create file: `/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<DOMAIN_SLUG>/index.md`

Use `templates/wiki-domain-index.md` as the template. Fill in:
- `title`: `<Domain Name> Domain Index`
- `domain`: `<DOMAIN_SLUG>`
- `updated`: today's date
- Purpose, scope, exclusions appropriate to this domain

Do not invent content. Write only what is known from governance context or explicit instruction.

## Step 3 — Register domain in domain-registry.yaml

Read the current registry:

```bash
cat /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml
```

Append the new domain entry under the `domains:` list. Use `templates/wiki-domain-registry-entry.yaml` as the pattern:

```yaml
  - domain: "<DOMAIN_SLUG>"
    slug: "<DOMAIN_SLUG>"
    description: "<DOMAIN_DESCRIPTION>"
    source_paths:
      - "domains/<DOMAIN_SLUG>"
    qdrant_collection: "rag__wiki_<DOMAIN_SLUG>"
    status: "active"
```

**Do not modify any existing domain entries.**

## Step 4 — Update wiki index.md

Append a line for the new domain to `/Volumes/Data/_ai/_wiki/wiki_stuff/index.md` under the domains section.

## Step 5 — Update wiki log.md

Append an entry to `/Volumes/Data/_ai/_wiki/wiki_stuff/log.md`:

```
YYYY-MM-DD  Created domain: <DOMAIN_SLUG> — <DOMAIN_DESCRIPTION>
```

## Step 6 — Validate

```bash
python3 -c "
import yaml
with open('/Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml') as f:
    reg = yaml.safe_load(f)
found = [d for d in reg['domains'] if d['slug'] == '<DOMAIN_SLUG>']
print('PASS: domain registered' if found else 'FAIL: domain not found in registry')
"

test -f /Volumes/Data/_ai/_wiki/wiki_stuff/domains/<DOMAIN_SLUG>/index.md \
  && echo "PASS: index.md exists" || echo "FAIL: index.md missing"
```

---

## Output format

```
Files created:
  - domains/<DOMAIN_SLUG>/index.md
  - domains/<DOMAIN_SLUG>/references/  (empty dir)

Files modified:
  - wiki-data/domain-registry.yaml  (appended entry)
  - wiki_stuff/index.md             (appended line)
  - wiki_stuff/log.md               (appended entry)

Checks passed:  <list>
Checks failed:  <list or "none">

Verdict: WIKI_DOMAINS_READY | WIKI_DOMAINS_PARTIAL | WIKI_DOMAINS_NOT_READY

Next prompt: 02-verify-rag-tools.md
```
