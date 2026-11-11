#!/usr/bin/env bash
# Read-only probe: does each SMC trust a given apt signing key fingerprint (primary or subkey), over Teleport.
#
# usage: apt_key_subkey_probe.sh [--parallel N] [--source <pattern>] --proxy <teleport-proxy> --fpr <40-hex> <node> [<node> ...]
#   e.g. apt_key_subkey_probe.sh --proxy teleport.communitywifi.net.au --source packages.cisofy.com \
#          --fpr 3E82FB7C68F57341349ED2C17A9A1D9D5B27C6D3 kaltjiti-fergon-smc01
#
# Prints one `APTKEY|<node>|host=...|fpr=present|absent|in=<keyring files>|primary=<primary fpr>|source=<lines>` line per box.
# Every keyring apt reads is checked (/etc/apt/trusted.gpg, trusted.gpg.d, /etc/apt/keyrings, /usr/share/keyrings), subkeys
# included: a vendor that adds a signing subkey to an existing primary key leaves boxes that imported the older key with the
# primary but not the subkey, and apt fails with NO_PUBKEY <last 16 of the subkey>. --source shows the matching apt source
# lines (active, or commented with a leading #). Writes nothing but a gpg home in mktemp, removed on exit.
# Exit status: 0 when every node answered, 1 when any node gave no probe line, 2 on bad usage.
# Origin: ansible-wifi smc_lynis NO_PUBKEY 7A9A1D9D5B27C6D3, 2026-11-11 (references/06_failure-modes.md).
set -u

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
}

# The on-box probe. Quoted heredoc so nothing expands locally; FPR, SOURCE and APT_ROOT (tests only) come from the environment.
read -r -d '' PROBE <<'EOF'
kv() { printf '|%s=%s' "$1" "$(printf '%s' "$2" | tr '\n|' ' /' | sed -E 's/ +/ /g; s/ $//')"; }
r="${APT_ROOT:-}"
GNUPGHOME=$(mktemp -d); export GNUPGHOME; trap 'rm -rf "$GNUPGHOME"' EXIT
found=""; primary=""
for f in "$r"/etc/apt/trusted.gpg "$r"/etc/apt/trusted.gpg.d/* "$r"/etc/apt/keyrings/* "$r"/usr/share/keyrings/*; do
  [ -f "$f" ] || continue
  fprs=$(gpg --show-keys --with-colons --with-subkey-fingerprints "$f" 2>/dev/null | awk -F: '/^pub/{p=1} /^fpr/{if(p){prim=$10;p=0} print prim" "$10}')
  hit=$(printf '%s\n' "$fprs" | awk -v f="$FPR" 'toupper($2)==toupper(f){print $1; exit}')
  [ -n "$hit" ] && { found="$found ${f#$r}"; primary="$hit"; }
done
out="$(kv host "$(hostname)")"
if [ -n "$found" ]; then out="$out$(kv fpr present)$(kv in "${found# }")$(kv primary "$primary")"; else out="$out$(kv fpr absent)"; fi
if [ -n "${SOURCE:-}" ]; then
  out="$out$(kv source "$(grep -h -F "$SOURCE" "$r"/etc/apt/sources.list "$r"/etc/apt/sources.list.d/* 2>/dev/null | sed -E 's/ +/ /g' | sort -u | tr '\n' ';')")"
fi
echo "APTKEY$out"
EOF

proxy=""
fpr=""
source_pat=""
parallel=8
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --fpr) fpr="${2:-}"; shift 2 ;;
    --source) source_pat="${2:-}"; shift 2 ;;
    --parallel) parallel="${2:-8}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
if [ -z "$proxy" ] || [ $# -eq 0 ] || ! printf '%s' "$fpr" | grep -qE '^[0-9A-Fa-f]{40}$'; then
  usage >&2
  exit 2
fi
case "$parallel" in ''|*[!0-9]*|0) echo "--parallel needs a positive number" >&2; exit 2 ;; esac
case "$source_pat" in *\'*) echo "--source must not contain a single quote" >&2; exit 2 ;; esac

probe_one() {
  # Run the probe on one node and print its APTKEY line, or a FAIL line.
  #
  # Args:
  #   $1: node name as Teleport knows it.
  # Returns: 0 when a probe line came back, 1 otherwise; prints one line either way.
  local node="$1" line
  line="$(tsh ssh --proxy="$proxy" "root@$node" "FPR=$fpr SOURCE='$source_pat' bash -s" <<<"$PROBE" 2>&1 | tr -d '\r' | grep '^APTKEY|' | head -1)"
  if [ -n "$line" ]; then
    echo "APTKEY|$node|${line#APTKEY|}"
    return 0
  fi
  echo "FAIL|$node|no probe output (Teleport unreachable? check scripts/access/backdoor-watch.sh)"
  return 1
}

rc=0
running=0
for node in "$@"; do
  probe_one "$node" &
  running=$((running + 1))
  if [ "$running" -ge "$parallel" ]; then
    wait -n || rc=1
    running=$((running - 1))
  fi
done
while [ "$running" -gt 0 ]; do
  wait -n || rc=1
  running=$((running - 1))
done
exit "$rc"
