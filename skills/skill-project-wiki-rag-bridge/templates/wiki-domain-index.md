---
title: "<Domain Name> Domain Index"
type: "domain-index"
domain: "<domain_slug>"
status: "active"
updated: "YYYY-MM-DD"
---

# <Domain Name> Domain Index

## Purpose

<One paragraph: what knowledge this domain contains, what projects may use it, and what it is authoritative for.>

## Scope

This domain covers:

- <topic 1>
- <topic 2>
- <topic 3>

Out of scope for this domain:

- <excluded topic 1>
- <excluded topic 2>

## Contents

| File | Description |
|---|---|
| `references/<article>.md` | <Brief description> |

## Qdrant collection

Collection: `rag__wiki_<domain_slug>`

Indexed by: `rag-tools index-domain --domain <domain_slug>`

## Projects with declared access

| Project | Reason |
|---|---|
| `<project-slug>` | <why this project may use this domain> |

## Related domains

- [[<related-domain>]] — <relationship>

## Notes

- All articles in this domain must have `domain: <domain_slug>` frontmatter.
- Do not add project-specific data to this domain — keep it shared reference only.
- Source references are mandatory for all articles.
