# Agent Stack Runtime Contract

Agent Stack is primarily prompt/source material, but several skills include executable helpers. The repository therefore defines one reproducible **maintenance/validation runtime** without forcing every consumer project to adopt it.

## Root environment

The root `.mise.toml` pins Python and `uv`, creates/activates `.venv`, and exposes maintenance tasks.

```bash
mise install
mise run bootstrap
mise run check
mise run test
```

Equivalent `just` commands are available for common repository operations.

### Why a root virtual environment

- Skill helper scripts must not depend on whichever Python/packages happen to be globally installed.
- Repository tests and validators should run in an isolated, reproducible environment.
- Agent Stack must not silently install global Python packages.

The `.venv` is maintenance/runtime support only. A consuming project keeps ownership of its own environment.

## Skill runtime rules

Skills fall into two execution classes in `routing.toml`:

- `analysis`: prompt/reasoning procedure; no inherent local executable prerequisite.
- `tool`: requires a CLI, runtime, provider, or script environment that must be checked before use.

For a `tool` skill:

1. Read its declared `requires_any` plus the skill's own compatibility/setup notes.
2. Prefer an already-available project runtime when project-local instructions say so.
3. Otherwise use Agent Stack's root `mise`/`.venv` only for Agent Stack-owned helper scripts.
4. Do not install system/global dependencies without explicit operator authority.
5. Do not silently mutate the consuming project's dependency files.
6. If prerequisites are unavailable, route to a safe alternative or report the blocker.

## Python helper policy

- New Agent Stack-owned Python helpers should support the root pinned Python unless a skill declares a narrower compatibility range.
- External Python dependencies must be declared, not assumed.
- Repository-maintenance/test dependencies belong in `requirements-dev.txt`.
- Skill-specific runtime dependencies remain with the skill when they are genuinely specific.
- Prefer standard library for small validators/installers where doing so materially improves portability.

## Consumer isolation

Global installation is symlink-only. It exposes skills/personas; it does **not** activate this venv inside consumer projects, inject packages, or change their toolchains.
