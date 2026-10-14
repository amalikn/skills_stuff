<!-- BEGIN MANAGED: skill-ai-it:navigation --> <!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## AI navigation and context preflight

Before answering, planning or editing, read [AI_NAVIGATION.md](AI_NAVIGATION.md) first: it routes everything else (read order, source priority, task routing, scripts, checks, compaction recovery).
Read [context-map.yaml](context-map.yaml) only when changing routing or companion files.

- Sources disagree: stop and report, never guess. `SCRATCHPAD.md` is not durable truth unless marked `KEEP`; generated output never is.
- Run catalogued tasks only (`just --list`, `scripts/README.md`); an uncatalogued script is unknown safety. A new or changed script updates `scripts/README.md`.
- Before calling work done: `just check` (fix the project, not the check), and a `CHANGELOG.md` entry for any governance or navigation change.
- Preserve user content outside managed blocks.

<!-- END MANAGED: skill-ai-it:navigation -->
