#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

"$ROOT/scripts/validate-skill.sh"

[[ "$("$ROOT/scripts/detect-language-profile" --repo "$ROOT/tests/fixtures/python-project" --primary-only)" == "python" ]]
[[ "$("$ROOT/scripts/detect-language-profile" --repo "$ROOT/tests/fixtures/typescript-project" --primary-only)" == "javascript-typescript" ]]
[[ "$("$ROOT/scripts/detect-language-profile" --repo "$ROOT/tests/fixtures/mixed-project" --json)" == *'"recommendedProfile": "mixed-monorepo"'* ]]

if "$ROOT/scripts/repomix-security" --no-security-check >/dev/null 2>&1; then
  printf 'Security wrapper incorrectly accepted --no-security-check\n'
  exit 1
fi

if "$ROOT/scripts/repomix-reference" owner/repo >/dev/null 2>&1; then
  printf 'Reference wrapper incorrectly allowed missing revision\n'
  exit 1
fi

# Behavioural contract requirement checks
check_heading() {
  local file="$1" heading="$2"
  grep -qF "$heading" "$ROOT/$file" || { printf 'Missing heading in %s: %s\n' "$file" "$heading"; exit 1; }
}

check_phrase() {
  local file="$1" phrase="$2"
  grep -qF "$phrase" "$ROOT/$file" || { printf 'Missing phrase in %s: %s\n' "$file" "$phrase"; exit 1; }
}

check_heading SKILL.md '## Audience and Authority'
check_heading SKILL.md '## Token-Budget Thresholds'
check_heading SKILL.md '## Pack-Too-Large Retry Strategy'
check_heading SKILL.md '## Ambiguous Routing'
check_heading SKILL.md '## Required Run Report'

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

check_phrase patterns/context-scoping.md 'split or abort'

check_phrase patterns/static-pack-vs-mcp.md 'escalation authority'

check_phrase AGENTS.md 'synchronised between'

# Idempotency test: generator output must match current files
GENERATOR="$ROOT/create-skill-repomix.sh"
if [[ -x "$GENERATOR" ]]; then
  GEN_OUT="$TMP/skill-repomix-idempotency"
  "$GENERATOR" --target-dir "$GEN_OUT"
  for f in SKILL.md README.md AGENTS.md AI_NAVIGATION.md context-map.yaml \
            patterns/token-budgeting.md patterns/context-scoping.md \
            patterns/static-pack-vs-mcp.md patterns/compression-policy.md \
            scripts/validate-skill.sh tests/test-skill-repomix.sh; do
    if [[ -f "$ROOT/$f" && -f "$GEN_OUT/$f" ]]; then
      diff -q "$ROOT/$f" "$GEN_OUT/$f" >/dev/null || {
        printf 'Idempotency drift detected: %s\n' "$f"
        exit 1
      }
    fi
  done
  printf 'Idempotency check passed\n'
else
  printf 'SKIP idempotency: generator not found or not executable\n'
fi

printf 'All tests passed\n'
