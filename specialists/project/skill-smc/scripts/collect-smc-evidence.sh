#!/usr/bin/env bash
# collect-smc-evidence.sh — read-only evidence capture from SMC appliances via Teleport.
#
# ORIGIN: written 2026-07-29 for the APN routing-issue investigation
# (local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/). Promoted into skill-smc for
# reuse on future WAN-routing/topology-drift investigations at any site, any flavor.
#
# SAFETY CONTRACT
#   Every remote command in CAPTURES below is read-only. No file is written, no service is
#   restarted, no interface is touched on the appliance. The remote command set is hardcoded —
#   this script accepts host names only, never arbitrary commands. Do not add a command here
#   that mutates state; if you need one, run it by hand and record it in the analysis instead.
#
# Usage
#   ./collect-smc-evidence.sh old-looma umoona    # named sites (bare name or full -smc01) — REQUIRED
#
#   There is no default host list — this is a generic tool, not scoped to any one investigation's
#   sites. Always pass the hosts you actually need explicitly.
#
# Output (by default, next to this script — override with OUTDIR_ROOT to write into your own
# investigation folder instead, e.g. OUTDIR_ROOT=/path/to/issues/apn/some-issue/evidence)
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/<host>/<capture>.txt
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/MANIFEST.txt
#
# Requires: tsh, already logged in to the relevant Teleport cluster (`tsh status` to check).

set -uo pipefail

REPO_ROOT="${OUTDIR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STAMP="$(date '+%Y%m%d_%H%M')"
OUTDIR="${REPO_ROOT}/evidence/${STAMP}"
SSH_USER="${SMC_SSH_USER:-root}"

# capture-name : remote command (read-only)
CAPTURES=(
  "ip-route:ip route show"
  "ip-route-table-all:ip route show table all"
  "ip-rule:ip rule show"
  "ip-addr:ip -br addr show"
  "ip-link:ip -br link show"
  # Hardware model matters: this fleet mixes at least two SMC chassis (e.g. BOXER-6404,
  # BOXER-6641) with different physical NIC naming schemes. topology_vars can silently assume the
  # wrong one for a given site's actual hardware — see analyse-topology-interface-match.py and the
  # "Mandatory pre-check" note in ../references/08_ansible-authoring.md, added after a live New
  # Looma bug (2026-07-30 APN routing-issue investigation) where topology_vars named a WAN
  # interface after a NIC that only exists on a different chassis model.
  "dmidecode-model:dmidecode -s system-product-name 2>/dev/null"
  "netplan:cat /etc/netplan/*.yaml"
  # The SMC override is the extensionless /etc/dhcp/dhclient-enter-hooks, NOT the .d/ directory —
  # .d/ holds only stock Debian fragments. This is the file that decides ECMP membership.
  "dhclient-enter-hooks:cat /etc/dhcp/dhclient-enter-hooks 2>/dev/null"
  "dhclient-enter-hooks-d:cat /etc/dhcp/dhclient-enter-hooks.d/* 2>/dev/null"
  "dhclient-script:cat /etc/dhcp/dhclient-script 2>/dev/null"
  "dhclient-units:systemctl list-units 'dhclient@*' --no-pager --no-legend"
  # smc_iptables manages filter, mangle and nat (and references raw) — 'iptables -S' alone shows
  # only filter and would miss the NAT and mangle rules entirely.
  "iptables-save:iptables-save"
  "iptables-filter:iptables -S"
  "iptables-nat:iptables -t nat -S"
  "iptables-mangle:iptables -t mangle -S"
  "iptables-raw:iptables -t raw -S"
  # PATH CORRECTED 2026-08-25. smc_network deploys this to the FILESYSTEM ROOT (roles/smc_network/tasks/ubuntu.yml:346 renders to
  # /interfacecheckv2.sh), not /usr/local/bin. The old path meant this capture failed on EVERY site, silently, for the life of the script —
  # verified absent at /usr/local/bin and present at / on yakanarra, umoona and pandanus-park.
  "interfacecheck:cat /interfacecheckv2.sh 2>/dev/null"
  # Manual out-of-band TBF ingress-shaping script + its systemd unit, operator-identified 2026-07-29.
  # Not rendered by any smc_* role. Captured here to validate the operator-supplied script text and
  # to check whether the unit persists shaping across reboots — see docs/tbf-shaping-20260729_1503.md.
  "internet-ingress-shaping-script:cat /usr/local/sbin/internet-ingress-shaping.sh 2>/dev/null"
  "internet-shaping-service:cat /etc/systemd/system/internet-shaping.service 2>/dev/null"
  "internet-shaping-unit-status:systemctl status internet-shaping.service --no-pager 2>/dev/null"
  "tc-qdisc:tc -s qdisc show 2>/dev/null"
  "ip-link-ifb:ip -br link show type ifb 2>/dev/null"
  # Directly answers analysis §7 step 6: compare mtimes of the two artifacts smc_network and
  # smc_application render, to see how far apart in time the two roles were actually run.
  "netplan-mtime:stat --format='%Y %y %n' /etc/netplan/*.yaml 2>/dev/null"
  "hook-mtime:stat --format='%Y %y %n' /etc/dhcp/dhclient-enter-hooks 2>/dev/null"
)

die() { echo "ERROR: $*" >&2; exit 1; }

command -v tsh >/dev/null || die "tsh not found in PATH"
tsh status >/dev/null 2>&1 || die "not logged in to Teleport — run 'tsh login' first"

[[ $# -gt 0 ]] || die "no hosts given — usage: ./collect-smc-evidence.sh <site> [<site> ...]"

# Resolve bare site names to -smc01 appliance names.
hosts=()
for h in "$@"; do
  [[ "$h" == *-smc01 ]] && hosts+=("$h") || hosts+=("${h}-smc01")
done

mkdir -p "$OUTDIR"
MANIFEST="${OUTDIR}/MANIFEST.txt"
{
  echo "# SMC evidence capture"
  echo "captured_at: ${STAMP}"
  echo "captured_by: $(whoami)"
  echo "cluster:     $(tsh status 2>/dev/null | awk '/Cluster:/ {print $2}')"
  echo "ssh_user:    ${SSH_USER}"
  echo "mode:        read-only (see SAFETY CONTRACT in scripts/collect-smc-evidence.sh)"
  echo "hosts:       ${hosts[*]}"
  echo ""
  echo "## captures"
  for c in "${CAPTURES[@]}"; do echo "  ${c%%:*} = ${c#*:}"; done
  echo ""
  echo "## results"
} > "$MANIFEST"

for host in "${hosts[@]}"; do
  echo "==> ${host}"
  hostdir="${OUTDIR}/${host}"
  mkdir -p "$hostdir"

  for entry in "${CAPTURES[@]}"; do
    name="${entry%%:*}"
    cmd="${entry#*:}"
    out="${hostdir}/${name}.txt"

    if tsh ssh "${SSH_USER}@${host}" "$cmd" > "$out" 2>"${out}.err"; then
      lines=$(wc -l < "$out" | tr -d ' ')
      rm -f "${out}.err"
      printf '  %-24s %s\n' "$name" "ok (${lines} lines)"
      echo "  ${host}/${name}: ok (${lines} lines)" >> "$MANIFEST"
    else
      printf '  %-24s %s\n' "$name" "FAILED"
      echo "  ${host}/${name}: FAILED — see ${name}.txt.err" >> "$MANIFEST"
    fi
  done
done

echo ""
echo "Evidence written to: ${OUTDIR}"
echo "Manifest:            ${MANIFEST}"
