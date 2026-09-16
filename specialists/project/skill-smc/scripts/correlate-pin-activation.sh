#!/usr/bin/env bash
# correlate-pin-activation.sh — read-only per-pin activation timeline for SMC captive-portal boxes.
#
# ORIGIN: written 2026-09-11, same investigation as audit-pin-activation.sh (see
# ../references/14_pin-activation-diagnosis.md). That script answers "is this site's pin pipeline
# healthy, fleet-wide" with per-site totals. This one answers a different, narrower question an
# operator asked directly: "for THIS site, give me every real pin activation with WHO (MAC), WHAT
# IP it had, WHEN it activated, and WHEN that IP's DHCP lease started/ended" — a per-pin timeline,
# not a per-site count.
#
# THREE SOURCES, JOINED ON TWO DIFFERENT KEYS (full explanation: ../references/14_pin-activation-diagnosis.md §14.4):
#   1. Apache `wifi/access` log   — WHEN (timestamp) + WHICH IP, keyed on client IP.
#   2. `/var/lib/dhcp/dhcpd.leases` — WHICH MAC held that IP, keyed on IP, valid over a [starts,ends] epoch window.
#   3. `iptables -t mangle -L ECLIPSE_MARK` — is that MAC's pin valid RIGHT NOW, keyed on MAC.
#
# THE BUG THIS SCRIPT EXISTS TO AVOID: naively taking "the last lease block in the file for this
# IP" is WRONG — dhcpd.leases is append-only, and a later renewal can start AFTER an activation
# that happened under an earlier lease for the same IP (confirmed live 2026-09-11, hope-vale,
# 10.0.36.28: last-in-file lease started 15:53:29, but the real activation was logged 15:52:41 —
# 48s "in the future" relative to that lease). This script instead scans ALL lease blocks for the
# IP and picks the one whose `starts` epoch is the LATEST one that is still <= the activation
# epoch (falls back to the earliest known lease if none qualify, and says so).
#
# WHAT IT CANNOT TELL YOU (be honest about this when reading the output):
#   - Pin GENERATION time (Eclipse-side) — not visible from the SMC at all. This shows ACTIVATION
#     (the local wifi/access POST), not issuance-server timestamps. See 14_pin-activation-diagnosis.md §14.6.
#   - Anything outside the Apache log retention window (~14 days typical) or the dhcpd.leases
#     history still on disk (also rotates/compacts over time, unbounded but not infinite).
#   - A mark that predates this box's current NAT rule load, or was pushed by Eclipse's periodic
#     sync with NO local activation ever happening — that pin will just never appear here, because
#     this script starts from the activation log, not from the mark table.
#
# SAFETY CONTRACT (same as audit-pin-activation.sh / collect-fleet-health.sh)
#   Every remote command is read-only: iptables -L (list, not -F/-D/-I), and log/lease-file reads.
#   No file is written, no service is restarted, no rule is touched. The remote command set is
#   hardcoded — this script accepts host names only, never arbitrary commands.
#
# Usage
#   ./correlate-pin-activation.sh hope-vale                 # one site (bare or -smcNN)
#   ./correlate-pin-activation.sh hope-vale kowanyama        # multiple sites, one table each
#   LOOKBACK=50 ./correlate-pin-activation.sh bungardi       # last 50 activations instead of default 30
#
# Output (by default, next to this script — override with OUTDIR_ROOT)
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/<host>/pin-correlation.txt   — the table, also printed to stdout
#
# Requires: tsh, already logged in to the relevant Teleport cluster (`tsh status` to check).
# Requires locally: bash, awk, and either GNU `date -d` or BSD/macOS `date -r` (auto-detected).

set -uo pipefail

REPO_ROOT="${OUTDIR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STAMP="$(date '+%Y%m%d_%H%M')"
OUTDIR="${REPO_ROOT}/evidence/${STAMP}"
SSH_USER="${SMC_SSH_USER:-root}"
LOOKBACK="${LOOKBACK:-30}"

die() { echo "ERROR: $*" >&2; exit 1; }

command -v tsh >/dev/null || die "tsh not found in PATH"
tsh status >/dev/null 2>&1 || die "not logged in to Teleport — run 'tsh login' first"

[[ $# -gt 0 ]] || die "no hosts given — usage: ./correlate-pin-activation.sh <site> [<site> ...]"

# Same bare-name resolution as the sibling scripts: only names with NO -smcNN suffix get -smc01
# appended, so aurukun-smc02 etc. must already be passed in full.
hosts=()
for h in "$@"; do
  [[ "$h" =~ -smc[0-9]+$ ]] && hosts+=("$h") || hosts+=("${h}-smc01")
done

mkdir -p "$OUTDIR"

# Locally-portable epoch -> human converter: try GNU date first, fall back to BSD/macOS date.
# (The REMOTE side is always Ubuntu/GNU date — no portability concern there.)
epoch2human() {
  local e="$1"
  [[ -z "$e" || "$e" == "-" ]] && { echo "-"; return; }
  TZ=Australia/Brisbane date -d "@${e}" '+%d/%b/%Y %H:%M:%S %z' 2>/dev/null \
    || TZ=Australia/Brisbane date -r "${e}" '+%d/%b/%Y %H:%M:%S %z' 2>/dev/null \
    || echo "epoch:${e}"
}

# One SSH round-trip per host. Remote side does the field extraction and the one GNU-date-dependent
# conversion (Apache timestamp -> epoch); everything after that (the actual join, and lease-epoch ->
# human) happens locally so this script works from a non-Linux operator machine too.
read -r -d '' REMOTE_CMD <<'EOF'
echo '--ACTIVATIONS--'
zcat -f /var/log/apache2/access.log* /var/log/apache2/other_vhosts_access.log* 2>/dev/null \
  | grep 'wifi/access' | grep '" 302 ' | tail -n __LOOKBACK__ \
  | awk '{
      ip=$1;
      raw=$4" "$5; gsub(/\[|\]/,"",raw);
      split(raw,a,"/"); day=a[1]; mon=a[2];
      split(a[3],b,":"); year=b[1]; time=b[2]":"b[3]":"b[4]; tz=b[5];
      print ip, day, mon, year, time, tz;
    }' \
  | while read -r ip day mon year time tz; do
      epoch=$(date -d "$day $mon $year $time $tz" +%s 2>/dev/null)
      echo "${ip}|${epoch:-0}|${day}/${mon}/${year} ${time} ${tz}"
    done
echo '--LEASES--'
awk '
  $1=="lease"{ip=$2; starts=""; ends=""; hw=""}
  $1=="starts"{starts=$3; sub(";","",starts)}
  $1=="ends"{ends=$3; sub(";","",ends)}
  /hardware ethernet/{hw=$3; sub(";","",hw)}
  /^}/{ if(ip!=""){ print ip"|"starts"|"ends"|"hw }; ip="" }
' /var/lib/dhcp/dhcpd.leases 2>/dev/null
echo '--MARKS--'
iptables -t mangle -L ECLIPSE_MARK -n 2>/dev/null | grep -oE 'MAC[0-9a-fA-F:]{17}' | sed 's/^MAC//' | tr 'A-F' 'a-f' | sort -u
echo '--END--'
EOF
REMOTE_CMD="${REMOTE_CMD//__LOOKBACK__/$LOOKBACK}"

for host in "${hosts[@]}"; do
  hostdir="${OUTDIR}/${host}"
  mkdir -p "$hostdir"
  raw="${hostdir}/pin-correlation.raw"
  out="${hostdir}/pin-correlation.txt"

  echo "=== ${host} ==="
  if ! tsh ssh "${SSH_USER}@${host}" "$REMOTE_CMD" > "$raw" 2>"${raw}.err"; then
    echo "CONNECT FAILED — see ${raw}.err"
    continue
  fi
  rm -f "${raw}.err"

  # Join, done locally in awk (numeric matching only — no date conversion in here).
  joined=$(awk -F'|' '
    /^--ACTIVATIONS--$/ { section="act"; next }
    /^--LEASES--$/      { section="lease"; next }
    /^--MARKS--$/       { section="mark"; next }
    /^--END--$/         { section=""; next }
    section=="act" && NF>=3   { n=++nact; actIP[n]=$1; actEP[n]=$2+0; actHU[n]=$3 }
    section=="lease" && NF>=4 { k=++leaseCount[$1]; leaseSt[$1,k]=$2+0; leaseEn[$1,k]=$3+0; leaseHw[$1,k]=$4 }
    section=="mark" && $0!="" { marks[tolower($0)]=1 }
    END {
      for (i=1;i<=nact;i++) {
        ip=actIP[i]; ep=actEP[i]; hu=actHU[i]
        cnt=leaseCount[ip]+0
        bestK=0; bestSt=-1; earliestK=0; earliestSt=9999999999
        for (k=1;k<=cnt;k++) {
          st=leaseSt[ip,k]
          if (st<=ep && st>bestSt) { bestSt=st; bestK=k }
          if (st<earliestSt) { earliestSt=st; earliestK=k }
        }
        note=""
        if (cnt==0) {
          mac="no-lease-found"; lst="-"; len="-"
        } else if (bestK==0) {
          # every known lease for this IP started AFTER the activation — use the earliest one
          # and flag it, rather than silently picking a lease that could not have been active yet.
          bestK=earliestK; mac=leaseHw[ip,bestK]; lst=leaseSt[ip,bestK]; len=leaseEn[ip,bestK]
          note="(WARNING: earliest known lease for this IP starts AFTER the activation time — MAC below is a best guess, not confirmed)"
        } else {
          mac=leaseHw[ip,bestK]; lst=leaseSt[ip,bestK]; len=leaseEn[ip,bestK]
        }
        if (mac=="") { mac="no-mac-in-lease-record"; if(note=="") note="(lease block matched by IP/time but had no 'hardware ethernet' line — data gap in dhcpd.leases itself, not a script bug)" }
        live = (mac in marks) ? "yes" : "no"
        printf "%s|%s|%s|%s|%s|%s|%s|%s\n", ip, ep, hu, mac, lst, len, live, note
      }
    }
  ' "$raw")

  {
    printf '%-15s %-24s %-17s %-24s %-24s %-6s\n' "IP" "Activated" "MAC" "Lease start" "Lease end" "Live?"
    printf '%s\n' "--------------------------------------------------------------------------------------------------------------------"
    if [[ -z "$joined" ]]; then
      echo "(no successful 302 activations found in the retained log window)"
    else
      while IFS='|' read -r ip ep hu mac lst len live note; do
        lst_h=$(epoch2human "$lst")
        len_h=$(epoch2human "$len")
        printf '%-15s %-24s %-17s %-24s %-24s %-6s %s\n' "$ip" "$hu" "$mac" "$lst_h" "$len_h" "$live" "$note"
      done <<< "$joined"
    fi
  } | tee "$out"
  echo
done

echo "Raw captures: ${OUTDIR}/<host>/pin-correlation.raw + pin-correlation.txt"
echo
echo "Read ../references/14_pin-activation-diagnosis.md §14.4 before trusting this blindly:"
echo "'Live?' reflects the mark table at CHECK time, not at activation time — a since-expired pin"
echo "will correctly show 'no' even though the activation itself was genuine. A WARNING note means"
echo "the lease match is a best-effort fallback, not a confirmed IP-to-MAC binding at that instant."
