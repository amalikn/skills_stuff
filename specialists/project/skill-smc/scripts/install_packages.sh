#!/usr/bin/env bash
# Install apt packages across SMC boxes, scoped by Teleport flavour label.
#
# Generic successor to the one-off snmp installer. SMC boxes are Ubuntu 22.04 or newer, so this
# assumes a modern apt and does no OS-version branching.
#
# Why a purpose-built script rather than ad-hoc `tsh ssh ... apt-get install`:
#
#   * **Scope by flavour.** The estate has 362 SMC boxes and most are `rct`. Installing fleet-wide
#     when someone asked for two flavours is not a recoverable mistake.
#   * **Verify the binary, not apt's exit code.** apt can report success while the command you
#     wanted is still absent; the point is a working tool.
#   * **Wait for the dpkg lock instead of failing.** A box running its own apt will refuse yours.
#     Worse, a `tsh` session that drops mid-install leaves an orphaned `apt-get` holding the lock,
#     so every later attempt fails against your own earlier run. Observed on mindi-rardi-smc01,
#     2026-09-20. `DPkg::Lock::Timeout` makes apt wait rather than lose the race.
#   * **Idempotent.** Boxes that already have the target are reported and skipped, so a re-run
#     after a partial sweep costs nothing and changes nothing.
#
# Persistence: overlayroot sends writes to tmpfs, where they are lost on reboot. Surveyed
# 2026-09-20, none of the 45 rcp/nbn_accelerate boxes had it mounted, but this re-checks per box
# and refuses rather than installing into something a reboot discards. Pass --force-overlay to
# override deliberately, having remounted the lower dir read-write first.
#
# Concurrency defaults low: these sites sit on constrained, sometimes satellite, backhaul.
#
# Usage:
#   scripts/install_packages.sh --packages snmp --verify snmpget --dry-run
#   scripts/install_packages.sh --packages snmp --verify snmpget
#   scripts/install_packages.sh --packages "tcpdump mtr" --verify tcpdump --flavours rcp
set -uo pipefail

PACKAGES=""
VERIFY=""
FLAVOURS="rcp,nbn_accelerate"
WORKERS=5
DRY_RUN=0
FORCE_OVERLAY=0
LOCK_WAIT=300      # seconds apt will wait for the dpkg lock before giving up

usage() { sed -n '2,/^set -uo/p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --packages)      PACKAGES="$2"; shift 2 ;;
    --verify)        VERIFY="$2"; shift 2 ;;
    --flavours)      FLAVOURS="$2"; shift 2 ;;
    --workers)       WORKERS="$2"; shift 2 ;;
    --lock-wait)     LOCK_WAIT="$2"; shift 2 ;;
    --dry-run)       DRY_RUN=1; shift ;;
    --force-overlay) FORCE_OVERLAY=1; shift ;;
    -h|--help)       usage 0 ;;
    *) echo "unknown arg: $1" >&2; usage 2 ;;
  esac
done

[[ -n "$PACKAGES" ]] || { echo "--packages is required" >&2; exit 2; }
# Default the verification binary to the first package name. Usually right (snmp is the exception,
# which is why --verify exists), and a wrong guess fails loudly rather than reporting a false pass.
[[ -n "$VERIFY" ]] || VERIFY="${PACKAGES%% *}"
export PACKAGES VERIFY DRY_RUN FORCE_OVERLAY LOCK_WAIT

install_one() {
  local node="$1" proxy="$2" site="${1%-smc*}" out
  out=$(tsh ssh --proxy="$proxy" "root@${node}" bash -s <<REMOTE 2>&1 | tr -d '\r' | tail -1
set -u
if command -v ${VERIFY} >/dev/null 2>&1; then
  echo "ALREADY|${VERIFY} present"
  exit 0
fi
if mount | grep -qi overlayroot && [ "${FORCE_OVERLAY}" != "1" ]; then
  echo "SKIP-OVERLAYROOT|writes land in tmpfs and are lost on reboot; remount the lower dir first"
  exit 0
fi
if [ "${DRY_RUN}" = "1" ]; then
  echo "WOULD-INSTALL|\$(apt-get -s install -y ${PACKAGES} 2>&1 | grep -c '^Inst') new package(s)"
  exit 0
fi
export DEBIAN_FRONTEND=noninteractive
APT="apt-get -o DPkg::Lock::Timeout=${LOCK_WAIT} -y"
if ! \$APT install ${PACKAGES} >/tmp/pkg-install.log 2>&1; then
  \$APT update >>/tmp/pkg-install.log 2>&1
  \$APT install ${PACKAGES} >>/tmp/pkg-install.log 2>&1 || true
fi
if command -v ${VERIFY} >/dev/null 2>&1; then
  echo "INSTALLED|${VERIFY} now present"
else
  echo "FAILED|\$(tail -1 /tmp/pkg-install.log)"
fi
REMOTE
)
  [[ -z "$out" ]] && out="UNREACHABLE|no response over Teleport"
  printf '%-22s %-17s %s\n' "$site" "${out%%|*}" "${out#*|}"
}
export -f install_one

mapfile -t TARGETS < <(
  for proxy in teleport.communitywifi.net.au teleport.apn.au; do
    tsh ls --proxy="$proxy" --format=json 2>/dev/null \
      | FLAVOURS="$FLAVOURS" PROXY="$proxy" python3 -c '
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
  done | sort -u -k1,1
)

[[ ${#TARGETS[@]} -gt 0 ]] || { echo "no boxes matched flavours: $FLAVOURS" >&2; exit 1; }

echo "packages: ${PACKAGES} | verify: ${VERIFY} | flavours: ${FLAVOURS} | targets: ${#TARGETS[@]} | dry-run: ${DRY_RUN}"
printf '%s\n' "${TARGETS[@]}" | xargs -P "$WORKERS" -n 2 bash -c 'install_one "$0" "$1"'
