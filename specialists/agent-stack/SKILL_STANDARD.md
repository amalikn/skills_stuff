# Agent Stack Skill Contract

This is the local quality contract for skills consumed through Agent Stack. Upstream skills may have different style, but Agent Stack adaptations must preserve these semantics.

## Required metadata

Every package skill has `SKILL.md` with valid YAML frontmatter containing at least:

- `name`: stable kebab-case identifier;
- `description`: trigger-oriented description of what the skill does and when it should be used.

Additional metadata already used by imported skills is valid when the target runtime supports or safely ignores it. `skills/skill-creator/scripts/quick_validate.py` validates the current accepted key
set.

## Trigger quality

A skill description should make clear:

1. the concrete task/intents it handles;
2. important scope boundaries when confusion with another skill is likely;
3. tool/runtime requirements only when they affect selection.

The root `routing.toml` provides Agent Stack-specific routing semantics, including overlap resolution, likely persona consumers, tool-vs-analysis execution class, runtime prerequisites, and safety
notes.

## Body quality

A strong skill should contain:

- purpose and trigger conditions;
- a bounded workflow;
- explicit stop/failure behaviour for fragile operations;
- expected outputs;
- references/resources only when they actually exist;
- runtime/setup guidance for executable helpers;
- no implicit authority to override project-local instructions or Agent Stack human-control rules.

Keep SKILL.md procedural. Put detailed reusable knowledge in `references/`, deterministic helpers in `scripts/`, and output templates in `assets/`.

## Environment rules

See `RUNTIME.md`.

- Do not assume globally installed Python packages.
- Agent Stack-owned Python helpers should use the root `mise`/`.venv` environment unless a consuming project explicitly owns the execution environment.
- Declare external packages/tools rather than silently installing them.
- Tool skills are selected only after runtime prerequisites are checked.

## Safety adaptation

Imported upstream instructions that imply unattended background agents, indefinite continuation, implicit persistent state, destructive operations, or material external commitments do not override
Agent Stack policy. Such behaviours require explicit project/operator authority.

## Validation

Run:

```bash
mise run bootstrap
mise run check
mise run test
```

The static validator checks capability inventory, routing coverage, persona contract depth, selected concrete local references, and skill metadata presence. Routing regression cases live in
`evals/routing-cases.toml`.
