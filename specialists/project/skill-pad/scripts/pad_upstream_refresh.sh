#!/usr/bin/env bash
# pad_upstream_refresh.sh: mirror one Pad release's upstream texts into references/upstream/v<version>/ so skill-pad can be diffed and updated by hand.
#
# Why: skill-pad is the operator's own text (operator, 2026-11-10: "develop our own skill and not rely on the plugin"), so a Pad release never
# overwrites it; this script fetches what changed for a reader to carry over (references/upgrade.md).
#
# Usage:
#   bash scripts/pad_upstream_refresh.sh 0.19.2            # plan: list what would be written
#   bash scripts/pad_upstream_refresh.sh 0.19.2 --apply    # write references/upstream/v0.19.2/
# Writes: repo files at tag v<version> (flattened names, '/' -> '_'; skills_pad_SKILL.md is the text `pad agent install claude` writes, minus its
#   stamp line), cli/pad-cli-reference.md/.json (generated outside any workspace: cmdhelp is context-aware) and agent-guide-all.md from the installed pad, releases-v<version>.md.
# Needs: curl, gh (authenticated), pad at the same version for the cli help and guide (skipped with a warning otherwise).
# Exit: 0 done or plan printed, 1 a fetch failed, 2 bad arguments.
# Budget: about 20 seconds measured (30 small HTTPS fetches, three local pad runs); the run prints its measured time.
set -euo pipefail

REPO="PerpetualSoftware/pad"
PACK="$(cd "$(dirname "$0")/.." && pwd)"
TIMEOUT_S=30
FILES=(
  README.md CLAUDE.md CONTRIBUTING.md SECURITY.md skills/INSTALL.md skills/pad/SKILL.md
  plugin/skills/pad/SKILL.md plugin/skills/status/SKILL.md plugin/skills/capture/SKILL.md plugin/skills/onboard/SKILL.md
  plugin/skills/connect/SKILL.md plugin/skills/disconnect/SKILL.md plugin/scripts/pad-monitor.sh plugin/hooks/activity-hooks.json
  plugin/monitors/monitors.json plugin/.claude-plugin/plugin.json .claude-plugin/marketplace.json
  internal/mcp/instructions.md internal/mcp/chatgpt_instructions.md internal/cli/agents.go
  docs/api.md docs/apps.md docs/architecture.md docs/backup.md docs/deployment.md docs/mcp.md docs/plugin-releases.md schema/README.md
  integrations/chatgpt/README.md integrations/chatgpt/skills/pad/SKILL.md
  web/src/lib/components/collections/collection-templates.ts
)

# die: print a message to stderr and exit.
#   Args: $1 message; $2 exit code (default 1).
#   Returns: never.
die() { echo "pad_upstream_refresh: $1" >&2; exit "${2:-1}"; }

# flat: turn a repo path into the mirror's flattened file name (leading dot dropped, '/' -> '_').
#   Args: $1 repo path.
#   Returns: prints the name.
flat() { local p="${1#.}"; echo "${p//\//_}"; }

[ $# -ge 1 ] || die "usage: pad_upstream_refresh.sh <version> [--apply]" 2
version="${1#v}"; apply=0
[ "${2:-}" = "--apply" ] && apply=1
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-rc\.[0-9]+)?$ ]] || die "version must look like 0.19.2" 2
dest="$PACK/references/upstream/v$version"
start=$(date +%s)

installed="$(pad --version 2>/dev/null | awk '{print $3}')" || installed=""
if [ $apply -eq 0 ]; then
  echo "plan: write $dest/"
  for f in "${FILES[@]}"; do echo "  $(flat "$f")  <- $REPO@v$version:$f"; done
  echo "  cli/pad-cli-reference.md, cli/pad-cli-reference.json, agent-guide-all.md  <- pad $installed$([ "$installed" = "$version" ] || echo " (version differs: skipped)")"
  echo "  releases-v$version.md  <- gh release view v$version"
  echo "run again with --apply to write"
  exit 0
fi

mkdir -p "$dest"
for f in "${FILES[@]}"; do
  curl -sfL --max-time "$TIMEOUT_S" "https://raw.githubusercontent.com/$REPO/v$version/$f" -o "$dest/$(flat "$f")" || die "fetch failed: $f"
done
gh release view "v$version" -R "$REPO" --json tagName,publishedAt,body --jq '"## \(.tagName) (\(.publishedAt))\n\n\(.body)\n"' > "$dest/releases-v$version.md" \
  || die "gh release view failed for v$version"

if [ "$installed" = "$version" ]; then
  pad agent guide all > "$dest/agent-guide-all.md"
  mkdir -p "$dest/cli"
  (cd "${TMPDIR:-/tmp}" && pad help --all --format md > "$dest/cli/pad-cli-reference.md" && pad help --all --format json > "$dest/cli/pad-cli-reference.json" && pad help --capabilities > "$dest/cli/capabilities.txt")
else
  echo "pad_upstream_refresh: installed pad is '$installed', not $version: cli help and agent guide skipped" >&2
fi
echo "wrote $(find "$dest" -type f | wc -l | tr -d ' ') files to $dest in $(( $(date +%s) - start ))s"
