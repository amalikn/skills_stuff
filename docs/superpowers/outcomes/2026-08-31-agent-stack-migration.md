# Agent Stack Migration Outcome

## Scope

Extracted Auto Company’s 14 personas and 36 skill entries into the English-only canonical Agent Stack. The autonomous loop, consensus mechanism, daemon, prompts, and runtime settings remain Auto Company-local.

## Delivered

- Canonical pack: `specialists/agent-stack/` with 186 source-library files, a 50-capability manifest, English personas, and translated team and GitHub-explorer skills.
- Installation model: Auto Company now exposes canonical personas and skills through directory symlinks.
- Upstream workflow: stdlib-only sync script, Just recipes, official upstream state, translation memory, review proposals in `skills-working-cache`, and 11 regression tests.
- Documentation: canonical and Auto Company README boundaries, design, approved plan, and this outcome record.

## Safety Decisions

- Translated canonical files are never automatically overwritten; an upstream hash change creates a translation review with previous and new source copies outside Agent Stack.
- Local canonical divergence and untracked target files require manual merge review.
- The sync tool rejects post-cutover symlinked Auto Company content as an upstream baseline source.

## Validation

- Canonical inventory matches the rollback source snapshot: 186 files.
- Manifest parses and contains 50 complete capability records.
- English audit passed, allowing only established Greek mathematical notation in formulas.
- `just test` passed: 11 tests.
- `just upstream-status`, `just upstream-dry-run`, and `just upstream-fetch-dry-run` passed against official commit `ebfab9b4bd5f0ab5ad452a1ff85285b3c141acdd` with no library changes.
- Auto Company symlinks resolve to the canonical persona and skill directories; `bash -n scripts/core/auto-loop.sh` passed.

## Recovery

The pre-cutover Auto Company copies are retained at `/private/tmp/agent-stack-migration/rollback/agents-original` and `/private/tmp/agent-stack-migration/rollback/skills-original` for temporary recovery.
