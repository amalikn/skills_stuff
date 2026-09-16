#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0

required=(
  SKILL.md README.md AGENTS.md ARCHITECTURE.md AI_NAVIGATION.md
  context-map.yaml CHANGELOG.md
  templates/repomix.config.json templates/.repomixignore
  templates/repomix-instruction.md templates/repomix-mcp-routing-policy.md
  scripts/repomix-current scripts/repomix-review scripts/repomix-security
  scripts/repomix-reference scripts/detect-language-profile
  scripts/install-skill-into-project
)

for f in "${required[@]}"; do
  [[ -e "$ROOT/$f" ]] || { printf 'Missing: %s\n' "$f"; fail=1; }
done

for f in "$ROOT"/scripts/*; do
  [[ -f "$f" ]] || continue
  bash -n "$f" || fail=1
done

if command -v python3 >/dev/null 2>&1; then
  for f in "$ROOT"/profiles/*.json "$ROOT/templates/repomix.config.json"; do
    python3 -m json.tool "$f" >/dev/null || fail=1
  done
fi

grep -q '^name: skill-repomix' "$ROOT/SKILL.md" || { printf 'Missing name frontmatter in SKILL.md\n'; fail=1; }
grep -q '\.ai-context/' "$ROOT/templates/.repomixignore" || { printf 'Missing .ai-context/ in .repomixignore\n'; fail=1; }

if grep -R -- '--no-security-check' "$ROOT/scripts" | grep -v 'prohibited' >/dev/null 2>&1; then
  printf 'Forbidden security-disable support detected\n'
  fail=1
fi

# Behavioural contract section checks
check_phrase() {
  local file="$1" phrase="$2"
  grep -qF "$phrase" "$ROOT/$file" || { printf 'Missing in %s: %s\n' "$file" "$phrase"; fail=1; }
}

check_phrase SKILL.md '## Audience and Authority'
check_phrase SKILL.md '## Token-Budget Thresholds'
check_phrase SKILL.md '## Pack-Too-Large Retry Strategy'
check_phrase SKILL.md '## Ambiguous Routing'
check_phrase SKILL.md '## Required Run Report'
check_phrase SKILL.md 'maximum of three attempts'
check_phrase SKILL.md 'silently truncate'
check_phrase SKILL.md 'Repomix Execution Summary'
check_phrase SKILL.md 'Compression justification'
check_phrase SKILL.md 'Budget utilisation'
check_phrase SKILL.md 'Retry attempts'

check_phrase README.md '## Audience'

check_phrase context-map.yaml 'agent_behavior'
check_phrase context-map.yaml 'human_operations'
check_phrase context-map.yaml 'token_policy'

check_phrase patterns/token-budgeting.md 'maximum of three attempts'
check_phrase patterns/token-budgeting.md 'silently truncate'
check_phrase patterns/token-budgeting.md 'Budget utilisation'

check_phrase patterns/context-scoping.md 'split or abort'

check_phrase patterns/static-pack-vs-mcp.md 'escalation authority'

check_phrase AGENTS.md 'synchronised between'

if command -v shellcheck >/dev/null 2>&1; then
  for f in "$ROOT"/scripts/*; do
    [[ -f "$f" ]] || continue
    shellcheck -x -S warning "$f" || fail=1
  done
else
  printf 'ShellCheck not available — not checked\n'
fi

if [[ "$fail" -ne 0 ]]; then
  printf 'Validation failed\n'
  exit 1
fi

printf 'Validation passed\n'
