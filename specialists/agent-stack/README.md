# Agent Stack

Agent Stack is the reusable, English-only extraction of Auto Company’s personas and skill library. It intentionally excludes Auto Company’s autonomous loop, consensus mechanism, daemon, and other
no-human-gate operating patterns.

## Contents

- [Use](#use)
- [Contents](#contents-1)
- [Upstream refresh](#upstream-refresh)
- [Safety model](#safety-model)

## Use

Agent Stack is canonical source material under `specialists/`. Its default delivery path is a global, symlink-only install for Claude Code, Codex, and compatible agents that discover
`~/.agents/skills`. Do not copy its contents.

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack
just global-dry-run
just global-install install
```

This links personas into Claude Code and skills into `~/.claude/skills`, `~/.codex/skills`, and `~/.agents/skills`. The last target is for compatible agents that explicitly discover that
standard path; it is not a claim that every agent does. The installer never copies source content or overwrites a pre-existing global entry. Agent Stack’s duplicate `skill-creator` remains
excluded by default; pass `--include skill-creator` only after deliberately reconciling it.

The original per-project directory-symlink arrangement remains available for a project that explicitly needs a fixed shared library. Do not replace existing project-local directories without
operator approval.

### Orchestrator

Use `orchestrator` for a multi-specialist task that needs one human-governed coordination path. It selects the smallest useful roles and skills, separates evidence from inference, highlights
disagreement, and returns one synthesis. `orchestrator-follett` is the companion persona for runtimes that support persona discovery. Neither starts a background process, makes material decisions
for you, or persists cross-project state.

### Other agents and `.agents`-compatible projects

For an agent that documents global discovery at `~/.agents/skills`, the default global install covers it. For an agent that documents project-local discovery from `.agents/skills`, link the
canonical skill directory directly when that project does not already own the directory:

```bash
mkdir -p <project>/.agents
ln -s /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/skills <project>/.agents/skills
```

`.agents` has no universal persona-discovery convention. Use `orchestrator` everywhere; additionally link or reference `personas/orchestrator-follett.md` only when that runtime documents a persona
path. Project-local instructions remain authoritative.

## Contents

- `personas/`: 15 on-demand specialist personas, including `orchestrator-follett`.
- `skills/`: 37 current packages, including `orchestrator`, classified in `manifest.yaml` as `project_agnostic` or `tool_specific`.
- `manifest.yaml`: source paths, install convention, and the classification inventory.
- `scripts/sync_auto_company.py`: conservative upstream comparison and update tool.

## Upstream refresh

The upstream source is the official `MaxMiksa/Auto-Company` repository. The sync tool uses a disposable mirror under `skills-working-cache`, never an always-on daemon.

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack
just upstream-status
just upstream-dry-run
just upstream-fetch-dry-run
```

The default command fetches the latest configured upstream revision and prints a classification report. The state records both the last upstream hash and the canonical English hash for every file. A
source change to a translated file always becomes `translation_required`, even if that new source happens to be English; it is never treated as a byte-for-byte replacement.

For a translated update, the existing canonical English file is the translation memory. The generated `translation-brief.md` tells the reviewer to preserve unchanged wording and translate only the
source material that changed. Its report retains the previous upstream source and the new source under `skills-working-cache`, so the change can be inspected even when both are non-English.
This is more stable than regenerating a complete file with a model; the full rules are in `translation-policy.md`.

`safe_add` and `safe_replace` are English-only changes to unadapted files that can be applied automatically. `translation_required`, `manual_merge`, and `remove_review` are written as review
proposals instead.

`upstream-status` reads only `upstream-state.json`. `upstream-dry-run` compares an existing mirror without network access. `upstream-fetch-dry-run` fetches then compares. `upstream-apply apply`
fetches and applies only eligible changes.

To apply only the safe changes, use an explicit confirmation:

```bash
just upstream-apply apply
```

Every apply creates a timestamped report under `skills-working-cache/agent-stack/update-reports/`. The baseline is stored in `upstream-state.json`; use
`just record-current <reviewed-auto-company-checkout>` only after a deliberate import review. The source must be an original upstream checkout or the working-cache mirror, never an Auto Company
checkout after it has been symlinked to Agent Stack.

## Safety model

The sync tool is report-first. It does not import autonomy infrastructure, delete canonical material, overwrite local editorial changes, or apply non-English upstream content. Review proposals before
manually translating, merging, or accepting removals.
