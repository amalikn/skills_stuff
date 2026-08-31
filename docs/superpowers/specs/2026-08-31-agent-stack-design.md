# Agent Stack Migration Design

## Purpose

Make Auto Company's 14 advisory personas and its complete reusable skill library available as a shared, on-demand capability pack without exporting Auto Company's autonomous loop, consensus model, or
risk posture to other projects.

## Decision

The canonical source will be `specialists/agent-stack/` in `skills_stuff`. The pack is named `agent-stack`, not `venture-studio` or `auto-company`, because it represents reusable agent capabilities
rather than an autonomous company operating model.

## Scope

Included:

- All 14 files currently in Auto Company's `.claude/agents/` directory.
- Every current package or standalone file in `.claude/skills/`, retaining each package's internal layout exactly unless translation is required for the English-only content rule.
- A manifest that classifies all skills as `general` or `tool-specific`; classification is advisory and never prevents selective installation.
- Documentation of the canonical source and symlink-only install procedure.

Excluded:

- `scripts/core/auto-loop.sh`, `memories/consensus.md`, and daemon configuration.
- Auto Company prompts, settings, project guardrails, runtime state, logs, and generated outputs.
- A cross-project daemon, scheduler, consensus file, or automatic invocation mechanism.

## English-Only Content Rule

Every canonical persona, skill, manifest value, and `agent-stack` documentation file must be in English. The migration will audit all Markdown, text, YAML, JSON, shell, and source-comment content
for non-English prose. Any non-English prose will be translated before the canonical pack is installed. Names, commands, code, URLs, identifiers, and source-language samples remain unchanged where
translation would alter behaviour or provenance.

## Canonical Structure

```text
specialists/agent-stack/
├── personas/
│   └── the 14 source persona Markdown files
├── skills/
│   └── every source skill file and package
├── manifest.yaml
└── README.md
```

`manifest.yaml` records the source name, classification, package shape, and any known tool dependency. It is an inventory and selection aid, not a new runtime dispatcher.

## Installation Model

Auto Company continues to consume the same logical paths, but its local folders become directory symlinks:

```text
auto-company/.claude/agents -> skills_stuff/specialists/agent-stack/personas
auto-company/.claude/skills -> skills_stuff/specialists/agent-stack/skills
```

Other projects link only individual personas or skill directories that they choose to use. No project receives the Auto Company loop implicitly.

## Migration Safety

1. Inventory names, file counts, and content hashes before moving anything.
2. Create the canonical pack and verify that its inventory exactly matches the source library, except for documented English translations.
3. Replace Auto Company's two source directories with relative directory symlinks only after the canonical inventory passes.
4. Verify every Auto Company path resolves to the canonical target and each `SKILL.md` remains readable.
5. Confirm no excluded loop or consensus files were moved or changed.

Rollback is simple: remove the two symlinks and restore the original directories from the canonical inventory without modifying the autonomous loop or consensus state.

## Validation

- `git diff --check` in both repositories.
- Compare pre- and post-migration path inventories and SHA-256 content hashes, allowing only documented translation deltas.
- Resolve and inspect both Auto Company directory symlinks.
- Confirm 14 personas and every discovered skill package remain present and readable through Auto Company's existing paths.
- Audit canonical prose for English-only content and review every translation delta.
- Confirm `scripts/core/auto-loop.sh`, `memories/consensus.md`, `.claude/settings.json`, and `PROMPT.md` are unchanged.

## Upstream Refresh

`agent-stack` will include a stdlib-only refresh script and a `justfile`. They fetch the configured Auto Company upstream into the `skills-working-cache` mirror, compare the latest `.claude/agents`
and `.claude/skills` trees with the last recorded import, and classify each change as a safe addition, safe replacement, translation-required update, or canonical divergence requiring a merge
proposal.

Dry-run is the default. Apply mode may add or replace only unchanged, English-only canonical files; it writes proposal artifacts for translated or diverged files and never silently overwrites them.
The source remote defaults to `https://github.com/MaxMiksa/Auto-Company.git`, but remains configurable in the checked-in upstream state file.

## Resolved Execution Constraint

The local `skills_stuff` AGENTS entrypoint was thinned from 166 to 57 lines, with detailed catalog material moved to `.agents/skill-surfaces.md`. The policy guard now passes without bypassing its
hook.
