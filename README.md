# skills_stuff

Canonical source-of-truth for reusable specialist packs and client export adapters.

## Layout
- `specialists/`: canonical specialist authoring packs.
- `exports/`: client-facing adapters generated or maintained from the canonical packs.
- `governance/`: repo-local pointer docs linking this repo to the shared governance stack.

## Folder index
- [graphify/](graphify/)
  Local Graphify workspace with upstream clone, governance files, and operator install notes.
  Project entry: [graphify/README.md](graphify/README.md)
- [invoice-finance-analyst/](invoice-finance-analyst/)
  Authoring surface for the internal-invoice-analysis skill — multi-layer CSV invoice reconciliation, rate-card validation, and margin analysis.
  Project entry: [invoice-finance-analyst/README.md](invoice-finance-analyst/README.md)
- [personal/](personal/)
  Personal-use skill packs — career tracking, therapy/counselling support, and other personal productivity tools.
  Index: [personal/README.md](personal/README.md)
- [skills/skill-project-wiki-rag-bridge/](skills/skill-project-wiki-rag-bridge/)
  Reusable skill — controlled bridge from project repos to shared wiki and Qdrant RAG tooling, with strict multi-project collection isolation.
  Project entry: [skills/skill-project-wiki-rag-bridge/README.md](skills/skill-project-wiki-rag-bridge/README.md)
  AI navigation: [skills/skill-project-wiki-rag-bridge/AI_NAVIGATION.md](skills/skill-project-wiki-rag-bridge/AI_NAVIGATION.md)

## Specialist Packs — Project

| Pack | Path | Status |
|---|---|---|
| `skill-ai-it` | `specialists/project/skill-ai-it/` | Stable — just-only task runner; mise fully removed |
| `skill-smc` | `specialists/project/skill-smc/` | Active |
| `skill-mx02-migration` | `specialists/project/skill-mx02-migration/` | Active |

## Current Focus
- Project specialist coverage now includes:
  - `skill-eml-to-md`
  - `skill-generator-and-derived-artifact-tracing`
  - `skill-holistic-impact-assessment`
  - `skill-repo-bootstrap-and-governance`
  - `skill-repo-knowledge-capture`
  - `skill-repo-local-guidance`
  - `skill-safe-change-validation`
  - existing `skill-mx02-migration`
- `skill-commtracker` — generic communication thread tracker (extracts email/.eml/Teams into markdown)
- Codex export adapters are present under `exports/codex/project/` for the new project specialists.
- `specialists/agent-stack/` is the canonical, English-only home for Auto Company-derived personas and skills. It is a reusable on-demand library, not an Auto Company runtime component.
- Graphify is locally installed on macOS via uv tool (`/Users/malik.ahmad/.local/bin/graphify`).

## Reusable Skills — skills/

| Skill | Path | Purpose |
|---|---|---|
| `skill-project-wiki-rag-bridge` | `skills/skill-project-wiki-rag-bridge/` | Controlled project/wiki/rag-tools bridge with multi-project isolation |

`skill-project-wiki-rag-bridge` governs how project repos connect to the shared wiki and rag-tools.
It does not own wiki content, project content, Qdrant data, or embeddings. Depends on external `rag-tools`.

## Governance
- Repo-local guidance: [AGENTS.md](/Volumes/Data/_ai/_skills/skills_stuff/AGENTS.md)
- Local governance index: [governance/README.md](/Volumes/Data/_ai/_skills/skills_stuff/governance/README.md)
- Shared governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Publishing Notes
- Treat `specialists/` as the canonical authoring surface.
- Treat `exports/` as delivery layers that must stay aligned with the corresponding canonical specialist packs.
- Use governed commit messages and update [REVISION_HISTORY.md](/Volumes/Data/_ai/_skills/skills_stuff/REVISION_HISTORY.md) when publishing meaningful repo changes.
