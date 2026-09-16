#!/usr/bin/env bash
# audit-pin-activation.sh — read-only pin validity + issuance audit for SMC captive-portal boxes.
#
# ORIGIN: written 2026-09-11 during the nbn_accelerate/nbn_wh portal-FQDN regression investigation
# (see ../references/14_pin-activation-diagnosis.md and ../references/13_known-issues.md), to
# settle "is anyone actually getting a working pin at this site" with live ground truth instead of
# a Prometheus traffic proxy. Promoted into skill-smc/scripts/ as reusable — any future captive-
# portal outage investigation on this fleet needs the same two checks.
#
# TWO INDEPENDENT MECHANISMS (full explanation: ../references/14_pin-activation-diagnosis.md):
#   1. iptables -t mangle -L ECLIPSE_MARK  — is a pin valid RIGHT NOW (a snapshot; a mark can exist
#      with no local activation ever having happened — Eclipse-side generation + periodic push).
#   2. Apache access log, `wifi/access` endpoint — was a pin ACTUALLY ISSUED through this box's
#      portal (an audit trail over time; 302 = success, 200 = failure). Checks BOTH access.log and
#      other_vhosts_access.log (with all .gz rotations) — on some boxes (confirmed: bungardi-smc01)
#      access.log is absent entirely and portal hits only land in the vhosts log.
# Use both. Read the reference doc before interpreting results, especially the "marks ≠
# activations" and "chain-level pkts/bytes are cumulative since last NAT reload, not current
# traffic" pitfalls — a raw table from this script read without that context will mislead.
#
# SAFETY CONTRACT (same as collect-fleet-health.sh / collect-smc-evidence.sh)
#   Every remote command is read-only: iptables -L (list, not -F/-D/-I), and log reads. No file is
#   written, no service is restarted, no rule is touched on the appliance. The remote command set
#   is hardcoded — this script accepts host names only, never arbitrary commands. Do not add a
#   mutating command here; if you need one, run it by hand under change control.
#
# Usage
#   ./audit-pin-activation.sh hope-vale kowanyama galiwinku          # named sites (bare or -smcNN)
#   ./audit-pin-activation.sh $(cat sites.txt)                       # from a file, one host per line
#
#   There is no default host list — always pass the hosts you actually need explicitly.
#
# Output (by default, next to this script — override with OUTDIR_ROOT)
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/<host>/pin-activation.txt   — raw capture per host
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/SUMMARY.txt                 — the comparison table
#   Same table is also printed to stdout.
#
# Requires: tsh, already logged in to the relevant Teleport cluster (`tsh status` to check). For
# the NBN Accelerate cluster this is teleport.communitywifi.net.au — `tsh ssh root@<host>` uses
# the bare node name, not the ansible_host FQDN form (see collect-fleet-health.sh header).

set -uo pipefail

REPO_ROOT="${OUTDIR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STAMP="$(date '+%Y%m%d_%H%M')"
OUTDIR="${REPO_ROOT}/evidence/${STAMP}"
SSH_USER="${SMC_SSH_USER:-root}"

die() { echo "ERROR: $*" >&2; exit 1; }

command -v tsh >/dev/null || die "tsh not found in PATH"
tsh status >/dev/null 2>&1 || die "not logged in to Teleport — run 'tsh login' first"

[[ $# -gt 0 ]] || die "no hosts given — usage: ./audit-pin-activation.sh <site> [<site> ...]"

# Same bare-name resolution as collect-fleet-health.sh: only names with NO -smcNN suffix get
# -smc01 appended, so aurukun-smc02 etc. must already be passed in full.
hosts=()
for h in "$@"; do
  [[ "$h" =~ -smc[0-9]+$ ]] && hosts+=("$h") || hosts+=("${h}-smc01")
done

mkdir -p "$OUTDIR"

# One SSH round-trip per host. Markers let the local parser pull each section back out.
read -r -d '' REMOTE_CMD <<'EOF'
echo '--MARKS--'
iptables -t mangle -L ECLIPSE_MARK -v -x -n 2>&1 | tail -n +3
echo '--REDIRECT--'
iptables -t nat -L SQUID_REDIRECT -v -x -n 2>&1 | tail -n +3
echo '--WIFI_ACCESS_LOG--'
zcat -f /var/log/apache2/access.log* /var/log/apache2/other_vhosts_access.log* 2>/dev/null | grep 'wifi/access'
echo '--END--'
EOF

printf '%-24s %8s | %12s %12s | %6s %6s %6s\n' "site" "marks" "3128(nopin)" "3131(pin)" "302" "200" "404" > "${OUTDIR}/SUMMARY.txt"
printf '%s\n' "----------------------------------------------------------------------------------------------" >> "${OUTDIR}/SUMMARY.txt"

echo "Auditing ${#hosts[@]} site(s) — pin validity (mangle) + activation log (both mechanisms)."
echo

for host in "${hosts[@]}"; do
  hostdir="${OUTDIR}/${host}"
  mkdir -p "$hostdir"
  out="${hostdir}/pin-activation.txt"

  if ! tsh ssh "${SSH_USER}@${host}" "$REMOTE_CMD" > "$out" 2>"${out}.err"; then
    printf '%-24s %s\n' "$host" "CONNECT FAILED — see ${host}/pin-activation.txt.err"
    printf '%-24s %8s\n' "$host" "unreachable" >> "${OUTDIR}/SUMMARY.txt"
    continue
  fi
  rm -f "${out}.err"

  marks=$(awk '/^--MARKS--$/{f=1;next}/^--REDIRECT--$/{f=0}f' "$out" | grep -c 'CONNMARK set' || true)
  r3128=$(awk '/^--REDIRECT--$/{f=1;next}/^--WIFI_ACCESS_LOG--$/{f=0}f' "$out" | awk '/redir ports 3128/{print $1}')
  r3131=$(awk '/^--REDIRECT--$/{f=1;next}/^--WIFI_ACCESS_LOG--$/{f=0}f' "$out" | awk '/redir ports 3131/{print $1}')
  c302=$(awk '/^--WIFI_ACCESS_LOG--$/{f=1;next}/^--END--$/{f=0}f' "$out" | grep -c '" 302 ' || true)
  c200=$(awk '/^--WIFI_ACCESS_LOG--$/{f=1;next}/^--END--$/{f=0}f' "$out" | grep -c '" 200 ' || true)
  c404=$(awk '/^--WIFI_ACCESS_LOG--$/{f=1;next}/^--END--$/{f=0}f' "$out" | grep -c '" 404 ' || true)

  printf '%-24s %8s | %12s %12s | %6s %6s %6s\n' \
    "$host" "${marks:-0}" "${r3128:-0}" "${r3131:-0}" "${c302:-0}" "${c200:-0}" "${c404:-0}" \
    | tee -a "${OUTDIR}/SUMMARY.txt"
done

echo
echo "Raw captures: ${OUTDIR}/<host>/pin-activation.txt"
echo "Summary:      ${OUTDIR}/SUMMARY.txt"
echo
echo "Read ../references/14_pin-activation-diagnosis.md before interpreting — 'marks' is a"
echo "current-state snapshot, '302' is the activation count over whatever this box's Apache log"
echo "retention covers (~14 days typical on this fleet), and 3128/3131 pkt totals are cumulative"
echo "since the NAT rules were last reloaded, not 'now'."
