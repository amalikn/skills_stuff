---
title: Wiki Domain Creation Guide
status: accepted
date: 20260524
provenance: prompts/01-create-wiki-domain.md, schemas/wiki-domain-registry.schema.yaml
---

# Wiki Domain Creation Guide

Step-by-step guide for creating a new wiki domain. This guide creates the directory structure and registers the domain. It does **not** index the domain into Qdrant — that is a separate step (see `guides/new-project-onboarding.md` Step 7, or `prompts/05-index-wiki-domain.md`).

## Contents

- [Prerequisites](#prerequisites)
- [Pre-flight check](#pre-flight-check)
- [Step 1 — Create domain directory structure](#step-1--create-domain-directory-structure)
- [Step 2 — Create domain index page](#step-2--create-domain-index-page)
- [Step 3 — Register domain in domain-registry.yaml](#step-3--register-domain-in-domain-registryyaml)
- [Step 4 — Update wiki index.md](#step-4--update-wiki-indexmd)
- [Step 5 — Update wiki log.md](#step-5--update-wiki-logmd)
- [Step 6 — Validate](#step-6--validate)
- [Output and next steps](#output-and-next-steps)

## Prerequisites

- `DOMAIN_SLUG` chosen: lowercase alphanumeric, e.g. `nbn`, `vocus`, `mcp`
- `DOMAIN_NAME` chosen: human-readable, e.g. `NBN`, `Vocus`
- `DOMAIN_DESCRIPTION` written: one sentence describing what knowledge the domain contains
- Wiki operational state confirmed (see `checklists/wiki-operational-readiness.md`)

## Pre-flight check

```bash
# Verify domain does not already exist
ls /Volumes/Data/_ai/_wiki/wiki_stuff/domains/
grep "domain: \"<DOMAIN_SLUG>\"" /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml 2>/dev/null \
  && echo "WARN: domain already in registry — stop" || echo "OK: not yet registered"
```

If domain already exists and has content: stop, do not recreate.

## Step 1 — Create domain directory structure

```bash
DOMAIN="<DOMAIN_SLUG>"
WIKI_DOMAINS="/Volumes/Data/_ai/_wiki/wiki_stuff/domains"

mkdir -p "$WIKI_DOMAINS/$DOMAIN/references"
```

Creates:
- `domains/<DOMAIN_SLUG>/` — domain root
- `domains/<DOMAIN_SLUG>/references/` — curated reference articles directory

## Step 2 — Create domain index page

Create: `/Volumes/Data/_ai/_wiki/wiki_stuff/domains/<DOMAIN_SLUG>/index.md`

Use `templates/wiki-domain-index.md` as the template. Populate:
- `title`: `<Domain Name> Domain Index`
- `domain`: `<DOMAIN_SLUG>`
- `updated`: today's date (YYYYMMDD)
- Purpose, scope, and exclusions appropriate to this domain

Do not invent content. Write only what is known from governance context or explicit instruction.

## Step 3 — Register domain in domain-registry.yaml

Read the current registry first:

```bash
cat /Volumes/Data/_ai/_wiki/wiki-data/domain-registry.yaml
```

Append under the `domains:` list — **do not modify existing entries**:

```yaml
  - domain: "<DOMAIN_SLUG>"
    slug: "<DOMAIN_SLUG>"
    description: "<DOMAIN_DESCRIPTION>"
    source_paths:
      - "domains/<DOMAIN_SLUG>"
    qdrant_collection: "rag__wiki_<DOMAIN_SLUG>"
    status: "active"
```

Confirm `qdrant_collection` exactly matches `rag__wiki_<DOMAIN_SLUG>`. See `specs/wiki-domain-registry-contract.md`.

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

## Output and next steps

After successful creation:

```
Files created:
  - domains/<DOMAIN_SLUG>/index.md
  - domains/<DOMAIN_SLUG>/references/  (empty)

Files modified:
  - wiki-data/domain-registry.yaml  (appended entry)
  - wiki_stuff/index.md             (appended line)
  - wiki_stuff/log.md               (appended entry)
```

Next: add curated reference articles to `domains/<DOMAIN_SLUG>/references/`, then index the domain (Step 7 of `guides/new-project-onboarding.md`, or `prompts/05-index-wiki-domain.md`).

## Related

- [prompts/01-create-wiki-domain.md](../../prompts/01-create-wiki-domain.md)
- [specs/wiki-domain-registry-contract.md](../specs/wiki-domain-registry-contract.md)
- [templates/wiki-domain-index.md](../../templates/wiki-domain-index.md)
- [templates/wiki-domain-registry-entry.yaml](../../templates/wiki-domain-registry-entry.yaml)
- [rules/retrieval-isolation-rules.md](../rules/retrieval-isolation-rules.md)
