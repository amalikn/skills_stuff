# Checklist: Wiki Operational Readiness

**Use before:** any bridge creation, domain indexing, or retrieval work.
**Blocks:** all downstream prompts if NOT_READY.

---

## Directory structure

- [ ] `/Volumes/Data/_ai/_wiki/wiki_stuff/` — content vault exists
- [ ] `/Volumes/Data/_ai/_wiki/wiki-data/` — metadata layer exists
- [ ] `/Volumes/Data/_ai/_wiki/wiki-runtime/` — runtime area exists (WARN if absent)
- [ ] `/Volumes/Data/_ai/_wiki/wiki-working-cache/` — cache area exists (WARN if absent)

## Governance files

- [ ] `wiki_stuff/README.md` — exists
- [ ] `wiki_stuff/AGENTS.md` — exists
- [ ] `wiki_stuff/AI_NAVIGATION.md` — exists
- [ ] `wiki_stuff/SCHEMA.md` — exists
- [ ] `wiki_stuff/context-map.yaml` — exists and parses
- [ ] `wiki_stuff/index.md` — exists
- [ ] `wiki_stuff/log.md` — exists
- [ ] `wiki_stuff/CHANGELOG.md` — exists (WARN if absent)

## Metadata layer

- [ ] `wiki-data/domain-registry.yaml` — exists and parses as valid YAML
- [ ] `wiki-data/domain-registry.yaml` — has at least 1 active domain
- [ ] `wiki-data/domain-registry.yaml` — `disallow_global_collection: true` is set
- [ ] `wiki-data/qdrant-collection-policy.md` — exists
- [ ] `wiki-data/project-dependency-model.schema.yaml` — exists (WARN if absent)

## Domain directories

For each domain in the registry:
- [ ] `wiki_stuff/domains/<domain>/` — directory exists
- [ ] `wiki_stuff/domains/<domain>/index.md` — exists (WARN if absent)
- [ ] `wiki_stuff/domains/<domain>/` — contains at least 1 markdown file other than index

## Frontmatter hygiene

- [ ] Spot-check: at least 5 random wiki domain files parse frontmatter without error
- [ ] No domain file has `domain:` field set to a different domain

## Wikilinks

- [ ] Wikilinks (`[[...]]`) use valid slugs that correspond to existing files (spot-check)
- [ ] No broken `[[...]]` references in domain index files

## Obsidian compatibility

- [ ] Files use `.md` extension throughout
- [ ] No absolute paths in wikilinks (use relative or bare slugs)

## Raw memory immutability

- [ ] `wiki_stuff/memories/raw/` — not modified since last ingestion
- [ ] No project-specific data mixed into domain directories

---

## Verdict

```
WIKI_OPERATIONAL_READY    — all required checks pass
WIKI_OPERATIONAL_PARTIAL  — some required checks fail or WARN checks flagged
WIKI_OPERATIONAL_NOT_READY — critical components absent
```
