# Script / Task Inventory Audit Checklist

## 0. Managed Block Integrity

Before auditing script/task content, verify the governance block layer is intact.

- [ ] No duplicate `<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->` blocks for the same section in the same file.
- [ ] Active managed blocks use the current format: `<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->`.
- [ ] Version stamp exists in managed blocks where expected: `<!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->`.
- [ ] Old-style markers (`<!-- BEGIN skill-ai-it:... -->` without `MANAGED:`) should only exist as **legacy detection targets** in audit patterns, not as active blocks. Flag any found in operational files.
- [ ] Managed blocks are matched: every `BEGIN MANAGED:` has a corresponding `END MANAGED:`.

## 1. Discovery

- [ ] Check whether `justfile` exists.
- [ ] Check whether `scripts/README.md` exists.
- [ ] Check for raw scripts under `scripts/`.
- [ ] Check for other task runners:
  - [ ] `Taskfile.yml`
  - [ ] `Makefile`
  - [ ] `package.json`
  - [ ] `.github/workflows/`
  - [ ] `ansible/`
  - [ ] `playbooks/`
  - [ ] `scripts/*.py`
  - [ ] `scripts/*.sh`

## 2. Catalog Coverage

- [ ] Every recipe in `justfile` is listed or discoverable via `just --list`.
- [ ] Every important script under `scripts/` is listed in `scripts/README.md`.
- [ ] Catalog does not reference deleted scripts.
- [ ] Catalog does not reference deleted tasks.
- [ ] Duplicate task/script entries are removed or explained.
- [ ] Managed block markers in `scripts/README.md` use the current format: `<!-- BEGIN MANAGED: skill-ai-it:scripts -->` with version stamp.

## 3. Safety Classification

- [ ] Each task/script has a safety label.
- [ ] `unknown` tasks are not treated as safe.
- [ ] Destructive tasks are clearly marked.
- [ ] Tasks that modify files are marked `modifies-files`.
- [ ] Tasks that call external services are marked `external-network`.
- [ ] Tasks requiring credentials are marked `requires-credentials`.
- [ ] Tasks requiring secrets are marked `requires-secrets`.
- [ ] Long-running tasks are marked `long-running`.

## 4. Inputs and Outputs

- [ ] Inputs are documented.
- [ ] Outputs are documented.
- [ ] Generated artifact paths are documented.
- [ ] Persistent state paths are documented.
- [ ] Runtime/cache paths are not confused with source files.
- [ ] Secret values are not documented.

## 5. Idempotency

- [ ] Repeat-safe tasks are marked idempotent.
- [ ] Non-idempotent tasks explain why.
- [ ] Cleanup/reset tasks are clearly separated from normal tasks.
- [ ] Deployment/migration/destructive tasks require review.
- [ ] Re-running the skill does not duplicate managed blocks in `scripts/README.md`.
- [ ] Re-running the skill does not rewrite user-authored script notes.
- [ ] Re-running the skill does not remove unknown custom YAML keys from context-map.yaml.
- [ ] Re-running the skill does not promote generated outputs automatically.

## 6. Agent Routing

- [ ] `AI_NAVIGATION.md` tells agents to inspect task catalog first.
- [ ] `context-map.yaml` routes script/task/automation questions correctly.
- [ ] `context-map.yaml` includes `audit_checks`, `promotion_rules`, and `context_recovery` schema sections.
- [ ] `repomix.config.json` includes task catalog files.
- [ ] Generated outputs like `.ai-context/` and `graphify-out/` are treated as generated support only, not canonical truth.
- [ ] Archcore is used only for durable operational procedures, not every script.
- [ ] Task-runner-first execution policy: prefer documented task runners (`justfile`, `Makefile`, `Taskfile.yml`, `package.json`) before raw scripts. Treat uncataloged executable scripts as `unknown` safety until reviewed.

## 7. Companion-File Update Rules

When scripts or tasks change, verify these companion files are updated or proposed for update:

- [ ] `scripts/README.md` — reflect purpose, inputs, outputs, safety label, and idempotency for each new/modified script.
- [ ] `AI_NAVIGATION.md` — update Script and Task Navigation section if routing changes.
- [ ] `context-map.yaml` — update `routing.scripts` or `routing.automation` sections if task-runner discovery order changes.
- [ ] `AGENTS.md` — update navigation block if script safety or execution policy changes.
- [ ] `CHANGELOG.md` — append entry for durable script/task governance changes.

Pull companion expectations from `context-map.yaml update_rules` where available (e.g. `routing_change`, `governance_history`).

## 8. Context-Map Schema Compatibility

When validating script/task governance, verify these fields in `context-map.yaml`:

- [ ] `audit_checks` — includes script/task audit expectations (task_runner_consistency, companion_update_completeness).
- [ ] `promotion_rules` — confirms script/task procedures are not promoted to `.archcore/` automatically.
- [ ] `context_recovery` — includes steps for regenerating generated outputs (`graphify-out/`, `.ai-context/`) after script changes.
- [ ] `routing.scripts` — defines read-first order and safety rules.
- [ ] `routing.automation` — defines automation entrypoint discovery order.

## 9. Drift Audit Handoff

- **script-task-audit-checklist.md** (this file) = detailed script inventory audit. Validates catalog entries, safety labels, inputs/outputs, idempotency markers, and companion-file updates for scripts and tasks.
- **patterns/drift-audit.md** = broader governance coherence audit. Validates managed block integrity, authority hierarchy, companion-update completeness across all governance files, generated-output policy, and .archcore/ promotion gates.

Both should be run for complete navigation/control-layer validation. Run this checklist first for script-specific issues, then run `patterns/drift-audit.md` for cross-file governance consistency.

## 10. Generated-Output Policy

- [ ] `.ai-context/` and `graphify-out/` are treated as generated support only, never canonical source of truth.
- [ ] Regeneration commands are documented:
  - `graphify update .` for Graphify
  - `repomix --config repomix.config.json` for Repomix
- [ ] Generated outputs are refreshed only when requested or when clearly stale (not auto-promoted).
- [ ] Governance files (AGENTS.md, AI_NAVIGATION.md, context-map.yaml) are not overwritten by generated output.

## 11. Validation Commands

Run from repo root. These are safe, non-destructive checks:

```bash
# Managed block integrity
echo "=== Duplicate managed blocks ==="
for section in navigation scripts; do
  count=$(grep -r "BEGIN MANAGED: skill-ai-it:$section" . --include="*.md" --include="*.yaml" -l 2>/dev/null | wc -l)
  files=$(grep -r "BEGIN MANAGED: skill-ai-it:$section" . --include="*.md" --include="*.yaml" -l 2>/dev/null | tr '\n' ' ')
  echo "section=$section files_found=$count"
done

# Old marker format (legacy detection)
echo "=== Old-style markers (legacy detection) ==="
grep -rn "BEGIN skill-ai-it:" . --include="*.md" 2>/dev/null | grep -v "docs/archive" | grep -v "CHANGELOG.md" | grep -v "patterns/drift-audit.md" || echo "(none outside expected files)"

# Version string presence
echo "=== Version stamp ==="
grep -rn "skill-ai-it-version: 2026-08-11-governance-checks-layer-v1" . --include="*.md" --include="*.yaml" 2>/dev/null || echo "(check expected files)"

# Task runner discovery
echo "=== Task runners ==="
test -f justfile && echo "justfile: present" || echo "justfile: absent"
test -f scripts/README.md && echo "scripts/README.md: present" || echo "scripts/README.md: absent"
test -f Taskfile.yml && echo "Taskfile.yml: present" || echo "Taskfile.yml: absent"
test -f Makefile && echo "Makefile: present" || echo "Makefile: absent"
test -f package.json && echo "package.json: present" || echo "package.json: absent"

# Script inventory vs actual files
echo "=== Script files ==="
find scripts -maxdepth 2 -type f 2>/dev/null | sort || echo "(no scripts directory)"

# just list
just --list 2>/dev/null || echo "just not available"

# YAML syntax
echo "=== YAML syntax ==="
python3 -c "
import yaml, sys
for f in ['context-map.yaml']:
    try:
        yaml.safe_load(open(f))
        print(f'  {f}: OK')
    except Exception as e:
        print(f'  {f}: FAIL - {e}')
" || echo "python3/yaml not available; skip YAML check"

# context-map schema fields
echo "=== context-map schema ==="
python3 -c "
import yaml
try:
    d = yaml.safe_load(open('context-map.yaml'))
    for field in ['audit_checks','promotion_rules','context_recovery']:
        status = 'present' if field in d else 'MISSING'
        print(f'  {field}: {status}')
except Exception as e:
    print(f'  Could not read: {e}')
" || echo "python3/yaml not available; skip schema check"
```

## 12. Audit Verdict

| Area | Status | Notes |
|---|---|---|
| Managed block integrity | PASS / PARTIAL / FAIL |  |
| Runnable task catalog exists | PASS / PARTIAL / FAIL |  |
| Human-readable script inventory exists | PASS / PARTIAL / FAIL |  |
| Safety labels present | PASS / PARTIAL / FAIL |  |
| Companion-file updates verified | PASS / PARTIAL / FAIL |  |
| Generated-output policy enforced | PASS / PARTIAL / FAIL |  |
| Context-map schema compatible | PASS / PARTIAL / FAIL |  |
| Idempotency confirmed | PASS / PARTIAL / FAIL |  |
| Drift audit cross-reference | PASS / PARTIAL / FAIL |  |
| Agent routing updated | PASS / PARTIAL / FAIL |  |
| Ready for agent use | YES / NO |  |
