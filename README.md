# skills_stuff

Canonical source-of-truth for reusable specialist packs and client export adapters.

## Layout
- `specialists/`: canonical specialist authoring packs.
- `exports/`: client-facing adapters generated or maintained from the canonical packs.
- `governance/`: repo-local pointer docs linking this repo to the shared governance stack.

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
- Codex export adapters are present under `exports/codex/project/` for the new project specialists.
- `specialists/agent-stack/` is the canonical, English-only home for Auto Company-derived personas and skills. It is a reusable on-demand library, not an Auto Company runtime component.

## Governance
- Repo-local guidance: [AGENTS.md](/Volumes/Data/_ai/_skills/skills_stuff/AGENTS.md)
- Local governance index: [governance/README.md](/Volumes/Data/_ai/_skills/skills_stuff/governance/README.md)
- Shared governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Publishing Notes
- Treat `specialists/` as the canonical authoring surface.
- Treat `exports/` as delivery layers that must stay aligned with the corresponding canonical specialist packs.
- Use governed commit messages and update [REVISION_HISTORY.md](/Volumes/Data/_ai/_skills/skills_stuff/REVISION_HISTORY.md) when publishing meaningful repo changes.
