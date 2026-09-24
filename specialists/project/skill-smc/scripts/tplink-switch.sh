#!/usr/bin/env bash
# Reach a TP-Link site switch (JetStream/Omada, e.g. SG2428P) through its site's SMC box, with the
# password pulled from KeePass and never written into any command line or transcript.
#
# Usage:
#   scripts/tplink-switch.sh <site> <switch_ip> ["show ..." ...]   # run commands (default: show system-info)
#   scripts/tplink-switch.sh <site> --discover                      # list TP-Link switches the SMC can see
#   scripts/tplink-switch.sh <site> <switch_ip> --shell             # interactive CLI; password to clipboard
#   scripts/tplink-switch.sh <site> <switch_ip> --backup <dir>      # redacted running-config to <dir>/<site>/
#   scripts/tplink-switch.sh --write <site> <switch_ip> "cmd" ...   # allow non-show commands (config!)
#
# Examples:
#   scripts/tplink-switch.sh kalumburu 10.255.0.2
#   scripts/tplink-switch.sh kalumburu 10.255.0.3 "show interface status" "show vlan"
#
# Read-only by default: only `show`, `ping` and `tracert` commands are sent unless --write is given.
# --write is a config change on a production switch; it needs the operator's explicit go-ahead.
#
# Site -> SMC host and Teleport cluster are resolved from ansible-wifi's inventory, the same way
# teleport-tunnel.sh does it. Requires an active `tsh login` for that cluster.
#
# Credentials: KeePass entry "/Network/tplink switch" (user admin) via the `kp` wrapper; override with
# TPLINK_KP_ENTRY. Verified at kalumburu only (2026-09-24); other sites may carry a different password.
# The login allows one password attempt per run (NumberOfPasswordPrompts=1) so a wrong entry cannot
# pile up failures against the switch's lockout.
#
# Enable: some switches enter `enable` with no password (kalumburu), others ask for one. Set
# TPLINK_KP_ENABLE_ENTRY to a KeePass entry when the enable password differs from the login password;
# otherwise the login password is tried once. The driver reports which case applied on stderr.
#
# --backup runs `show system-info` and `show running-config`, redacts every password/secret/community/key
# value, refuses to write if either known password string survives redaction, and writes
# <dir>/<site>/<system-name>_<ip>_<YYYYMMDD_hhmm>.cfg. Keep <dir> out of git (the configs are site data).
#
# The switch-side quirks (legacy SSH algorithms, no exec channel, CR for Enter, enable) are handled
# by tplink_cli_driver.py, which this script streams to the SMC over stdin; see its docstring.

set -euo pipefail

usage() { sed -n '4,10p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }

WRITE=0
if [ "${1:-}" = "--write" ]; then WRITE=1; shift; fi
SITE="${1:-}"; [ -n "$SITE" ] || usage; shift
TARGET="${1:-}"; [ -n "$TARGET" ] || usage; shift

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRIVER="$SCRIPT_DIR/tplink_cli_driver.py"
ANSIBLE_INVENTORY_ROOT="/Volumes/Data/_ansible/ansible-wifi/inventories"
KP_ENTRY="${TPLINK_KP_ENTRY:-/Network/tplink switch}"
KP_ENABLE_ENTRY="${TPLINK_KP_ENABLE_ENTRY:-}"
SW_USER="${TPLINK_USER:-admin}"

# Same resolver as teleport-tunnel.sh: [<site>_smc_bases] in exactly one inventories/<flavour>/prod.
cluster_for_flavour() {
  case "$1" in
    nbn_accelerate|nbn_wh|cw) echo "teleport.communitywifi.net.au" ;;
    rcp|rct|wh|apn) echo "teleport.apn.au" ;;
    *) echo "" ;;
  esac
}
INVENTORY_FILE="$(grep -rl "^\[${SITE}_smc_bases\]" "$ANSIBLE_INVENTORY_ROOT"/*/prod 2>/dev/null | head -1 || true)"
[ -n "$INVENTORY_FILE" ] || { echo "No '[${SITE}_smc_bases]' group under $ANSIBLE_INVENTORY_ROOT/*/prod." >&2; exit 1; }
FLAVOUR="$(basename "$(dirname "$INVENTORY_FILE")")"
SMC_HOST="$(awk -v grp="[${SITE}_smc_bases]" '$0 == grp {f=1; next} f && /^\[/ {exit} f && NF {print $1; exit}' "$INVENTORY_FILE")"
CLUSTER="$(cluster_for_flavour "$FLAVOUR")"
[ -n "$SMC_HOST" ] && [ -n "$CLUSTER" ] || { echo "Could not resolve SMC host/cluster for '$SITE' (flavour $FLAVOUR)." >&2; exit 1; }
echo "# $SITE -> $SMC_HOST via $CLUSTER" >&2

# Always --proxy=, never --cluster= (see references/01_overview.md, incident 2026-09-18).
TSH=(tsh ssh --proxy="$CLUSTER" "root@$SMC_HOST")

if [ "$TARGET" = "--discover" ]; then
  # Ping-sweep the SMC's management subnet, then probe every live host's SSH banner for TP-Link's
  # TPSSH. Read-only, no login.
  # TPSSH sends its banner only after the client's, so send one first; other devices emit NULs, drop them.
  "${TSH[@]}" 'bash -s' <<'DISCOVER'
probe() {
  local b mac
  b=$(timeout 3 bash -c "exec 3<>/dev/tcp/$1/22; printf 'SSH-2.0-discover\r\n' >&3; head -c 24 <&3" 2>/dev/null | tr -d '\0\r\n')
  case "$b" in *TPSSH*) mac=$(ip -4 neigh show "$1" | awk '{print $5}'); echo "$1 ${mac:-?} $b" ;; esac
}
export -f probe
# Management subnet only (bridge_500 / 10.255.x). Never sweep the client bridges: bridge_501 is a /18 of
# public Wi-Fi clients. ARP alone is not a usable host list: gc_thresh1 is 1 on the SMCs, so idle switches
# are purged after gc_stale_time (60 s). fping -a gives the live hosts.
MGMT=$(ip -4 route show scope link | awk '$3 == "bridge_500" || $1 ~ /^10\.255\./ {print $1}' | sort -u)
if command -v fping >/dev/null; then
  for net in $MGMT; do fping -a -q -r 0 -t 300 -i 2 -g "$net" 2>/dev/null; done
else
  echo "fping missing on this SMC: falling back to the ARP table, quiet switches can be missed" >&2
  ip -4 neigh | awk '$4 == "lladdr" && $1 ~ /^10\.255\./ {print $1}'
fi | sort -u | xargs -P 32 -n 1 bash -c 'probe "$0"' | sort -t. -k3,3n -k4,4n
DISCOVER
  exit $?
fi

command -v kp >/dev/null || { echo "kp wrapper not on PATH (see the KeePass kp wrapper note)." >&2; exit 1; }

if [ "${1:-}" = "--shell" ]; then
  kp show -s -a Password "$KP_ENTRY" | tr -d '\n' | pbcopy
  echo "# Password copied to the clipboard. Paste at the prompt; type 'enable' for show commands." >&2
  exec "${TSH[@]}" -t "ssh -F /dev/null -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -o HostKeyAlgorithms=+ssh-rsa -o MACs=hmac-sha2-256 -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 $SW_USER@$TARGET"
fi

BACKUP_DIR=""
if [ "${1:-}" = "--backup" ]; then
  BACKUP_DIR="${2:?--backup needs a directory}"
  set -- "show system-info" "show running-config"
fi
[ $# -gt 0 ] || set -- "show system-info"
if [ "$WRITE" -eq 0 ]; then
  for c in "$@"; do
    case "$c" in
      show\ *|ping\ *|tracert\ *) ;;
      *) echo "Refusing '$c': read-only mode allows show/ping/tracert. Use --write only with operator approval." >&2; exit 2 ;;
    esac
  done
fi

REMOTE="read -r SSHPASS; read -r ENABLEPASS; export SSHPASS ENABLEPASS; exec python3 - $(printf '%q ' "$TARGET" "$SW_USER" "$@")"
PASS="$(kp show -s -a Password "$KP_ENTRY")"
ENABLE_PASS=""
[ -z "$KP_ENABLE_ENTRY" ] || ENABLE_PASS="$(kp show -s -a Password "$KP_ENABLE_ENTRY")"
run_driver() { { printf '%s\n%s\n' "$PASS" "$ENABLE_PASS"; cat "$DRIVER"; } | "${TSH[@]}" "$REMOTE"; }

if [ -z "$BACKUP_DIR" ]; then
  run_driver
  exit $?
fi

RAW="$(run_driver)" || { echo "Switch session failed; nothing written." >&2; exit 1; }
# Redaction and the leak check run locally; passwords reach python through the environment, never argv.
RAW="$RAW" TP_PASS="$PASS" TP_ENABLE="$ENABLE_PASS" python3 - "$BACKUP_DIR" "$SITE" "$TARGET" "$(date +%Y%m%d_%H%M)" <<'PY'
import os, re, sys
out_dir, site, ip, stamp = sys.argv[1:5]
raw = os.environ["RAW"]
sections = dict(re.findall(r"^### [^:]+: (.+?)\n(.*?)(?=^### |\Z)", raw, re.S | re.M))
info, cfg = sections.get("show system-info", ""), sections.get("show running-config", "")
if not cfg.strip():
    sys.exit("No running-config captured; nothing written.")
secret = re.compile(r"(\b(?:password|secret|community|key|passphrase|psk)\s+(?:[0-9]\s+)?)(\S+)", re.I)
cfg = "\n".join(secret.sub(r"\1<redacted>", line) for line in cfg.splitlines())
for known in (os.environ.get("TP_PASS"), os.environ.get("TP_ENABLE")):
    if known and known in cfg:
        sys.exit("A known password survived redaction; nothing written.")
name = re.search(r"System Name\s+-\s+(.+)", info)
name = re.sub(r"[^A-Za-z0-9._-]+", "-", name.group(1).strip()) if name else "unknown"
path = os.path.join(out_dir, site, f"{name}_{ip}_{stamp}.cfg")
os.makedirs(os.path.dirname(path), exist_ok=True)
header = "\n".join(f"! {line}" for line in info.strip().splitlines())
with open(path, "w") as fh:
    fh.write(f"! site: {site}  ip: {ip}  captured: {stamp}  (redacted)\n{header}\n!\n{cfg}\n")
print(path)
PY
