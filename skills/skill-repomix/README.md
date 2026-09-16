# skill-repomix

Reusable Repomix skill for Codex, Claude Code, and local LLM workflows.

## Audience

- `SKILL.md` defines how AI agents must behave when using Repomix.
- `README.md` explains installation, scripts, profiles, and human operation.
- `AGENTS.md` defines maintenance rules for the skill package.
- Scripts implement supporting mechanics; they do not replace the behavioural contract.
- The skill can be used behaviourally without copying every wrapper into each project.
- Wrappers are optional execution assets. Repomix MCP and static wrappers are complementary.

## Features

- four production wrapper scripts
- automatic language-profile detection
- per-language include and ignore profiles
- Repomix MCP routing policy
- secure static-pack generation
- project installer
- validation and test scripts

## Generate

```bash
./create-skill-repomix.sh
```

## Validate

```bash
skill-repomix/scripts/validate-skill.sh
skill-repomix/tests/test-skill-repomix.sh
```

## Wrappers

- `repomix-current`: project onboarding and current-state packs
- `repomix-review`: change-review packs with Git diffs
- `repomix-security`: security-focused context packs
- `repomix-reference`: pinned remote FOSS reference packs

## Profiles

See `profiles/README.md`.

## Licence

Apache-2.0
