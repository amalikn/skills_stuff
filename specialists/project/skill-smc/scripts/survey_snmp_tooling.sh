#!/usr/bin/env bash
# Read-only survey: which SMC boxes have net-snmp client tools, and which run overlayroot.
#
# Both questions turned out to vary per box rather than per inventory flavour, which is why this
# exists: `snmpget` was recorded as an `rcp`-versus-`nbn_accelerate` split on a three-box sample
# and that was wrong (skill-smc references/13_known-issues.md). Overlayroot is the same shape of
# assumption — it is documented as fleet-wide, and at least one box does not have it mounted.
#
# Overlayroot matters here because it decides whether installing a package persists: on a box with
# overlayroot active, writes land in tmpfs and are lost on reboot unless the lower dir is remounted
# read-write first. A survey that reports only the missing binary would lead straight to an install
# that silently evaporates.
#
# Usage:
#   scripts/survey_snmp_tooling.sh [--workers N]
# Output: one TSV line per box — site, node, proxy, snmpget, overlayroot, os
set -uo pipefail

WORKERS=8
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workers) WORKERS="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

probe() {
  local node="$1" proxy="$2" site="${1%-smc*}"
  local out
  out=$(tsh ssh --proxy="$proxy" "root@${node}" \
        'printf "%s|" "$(command -v snmpget >/dev/null && echo yes || echo no)"; \
         printf "%s|" "$(mount | grep -qi overlayroot && echo yes || echo no)"; \
         printf "%s" "$(. /etc/os-release 2>/dev/null; echo "${VERSION_ID:-unknown}")"' \
        2>/dev/null | tr -d '\r' | tail -1)
  if [[ -z "$out" || "$out" != *"|"* ]]; then
    printf '%s\t%s\t%s\tUNREACHABLE\t-\t-\n' "$site" "$node" "${proxy%%.*}"
    return
  fi
  IFS='|' read -r has_snmp has_overlay os <<<"$out"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$site" "$node" "${proxy%%.*}" "$has_snmp" "$has_overlay" "$os"
}
export -f probe

# Scope by flavour. The estate has 362 SMC boxes but most are `rct`; a survey that ignores the
# flavour label spends hours on boxes the caller did not ask about.
FLAVOURS="${FLAVOURS:-rcp,nbn_accelerate}"
export FLAVOURS

for proxy in teleport.communitywifi.net.au teleport.apn.au; do
  tsh ls --proxy="$proxy" --format=json 2>/dev/null | FLAVOURS="$FLAVOURS" PROXY="$proxy" python3 -c '
import json, os, sys
try:
    nodes = json.load(sys.stdin)
except ValueError:
    sys.exit()
wanted = {f.strip() for f in os.environ["FLAVOURS"].split(",") if f.strip()}
for n in nodes:
    name = n.get("spec", {}).get("hostname") or n.get("metadata", {}).get("name", "")
    labels = n.get("metadata", {}).get("labels") or {}
    if labels.get("flavor") in wanted and "-smc" in name:
        print(name, os.environ["PROXY"])
'
done | sort -u -k1,1 | xargs -P "$WORKERS" -n 2 bash -c 'probe "$0" "$1"'
