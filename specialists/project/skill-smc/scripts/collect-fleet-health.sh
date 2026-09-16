#!/usr/bin/env bash
# collect-fleet-health.sh — read-only hardware + service-health evidence capture from SMC
# appliances via Teleport, at fleet scale (any flavor, any Teleport cluster).
#
# ORIGIN: written 2026-08-03 for the first-ever live NBN Accelerate cluster sweep (all
# nbn_accelerate + nbn_wh sites) — a thorough hardware/security/service-health audit, not the
# WAN-routing focus of collect-smc-evidence.sh. Promoted directly into skill-smc/scripts/ as a
# reusable, flavor-agnostic tool (not investigation-specific) since a full-fleet hardware/health
# sweep is a recurring need, not a one-off.
#
# SAFETY CONTRACT (same as collect-smc-evidence.sh)
#   Every remote command in CAPTURES below is read-only. No file is written, no service is
#   restarted, no interface is touched on the appliance. The remote command set is hardcoded —
#   this script accepts host names only, never arbitrary commands. Do not add a command here
#   that mutates state; if you need one, run it by hand and record it in the analysis instead.
#
# DIFFERENCE FROM collect-smc-evidence.sh: at fleet scale (dozens of hosts), a naive one-ssh-
# round-trip-per-command design is too slow over satellite links (per ../references/01_overview.md
# "Network Link — Satellite": "batch commands into single SSH round-trips wherever possible").
# Each CAPTURES entry below is therefore a small *bundle* of related read-only commands joined
# with `;` and separated by echo markers, run as ONE ssh round-trip — not one command per
# round-trip. This trades some of collect-smc-evidence.sh's per-command output granularity for
# roughly 3-4x fewer round-trips at fleet scale. Keep this bundling if you add captures; don't
# silently drift back to one-command-per-entry as the fleet grows.
#
# Usage
#   ./collect-fleet-health.sh warakurna indulkana bungardi   # named sites (bare or full -smc01)
#   ./collect-fleet-health.sh $(cat sites.txt)                # from a file, one host per line
#
#   There is no default host list — always pass the hosts you actually need explicitly.
#
# Output (by default, next to this script — override with OUTDIR_ROOT)
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/<host>/<capture>.txt
#   <OUTDIR_ROOT>/evidence/<YYYYMMDD_hhmm>/MANIFEST.txt
#
# Requires: tsh, already logged in to the relevant Teleport cluster (`tsh status` to check).
# For the NBN Accelerate cluster this is teleport.communitywifi.net.au — `tsh ssh root@<host>`
# uses the bare node name once logged in, NOT `<host>.teleport.<domain>` (that FQDN form is the
# Ansible-side ansible_host convention, not the tsh CLI target syntax — confirmed live 2026-08-03,
# a plain `tsh ssh root@<host>.teleport.communitywifi.net.au` returns "access denied").

set -uo pipefail

REPO_ROOT="${OUTDIR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STAMP="$(date '+%Y%m%d_%H%M')"
OUTDIR="${REPO_ROOT}/evidence/${STAMP}"
SSH_USER="${SMC_SSH_USER:-root}"

# capture-name : bundled read-only remote command (one ssh round-trip per entry).
#
# Grouped into 4 mega-bundles rather than one-command-per-entry (see the note above on satellite
# round-trip cost) — each bundle covers a coherent theme and writes internal `--marker--` lines
# so a single output file can still be grep/awk'd per sub-topic. Add new commands to the most
# relevant existing bundle rather than creating a 5th+ one, unless it's a genuinely new theme.
#
# Every bundle ends with `; true` — bash's exit code for a `;`-joined command list is the exit
# code of the LAST command run, and several last-in-bundle commands legitimately return non-zero
# on a perfectly healthy host (`grep overlay` finds nothing on a non-overlayroot flavor, a
# package-name grep matches nothing if none of the listed packages are installed). Without
# `; true` those would report as "FAILED" in the manifest even though every command before them
# captured real data to the output file — confirmed live 2026-08-03 on the first fleet run, where
# 01-identity-hardware showed FAILED on every host (last command: `mount | grep overlay`) despite
# full hardware data being present in the .txt file. Check the .txt content, not just the
# ok/FAILED label, when reviewing captures from before this fix.
CAPTURES=(
  # Hardware model matters: this fleet mixes multiple SMC chassis models with different physical
  # NIC naming schemes (see the "Mandatory pre-check" note in ../references/08_ansible-authoring.md).
  # Also the first hardware capture ever taken for the NBN Accelerate cluster (2026-08-03) — no
  # prior chassis-model inventory exists for this flavor the way it does for rcp/rct/wh.
  "01-identity-hardware:echo '--hostname--'; hostname; echo '--uptime--'; uptime; echo '--kernel--'; uname -a; echo '--os-release--'; (lsb_release -d 2>/dev/null || head -3 /etc/os-release); echo '--dmidecode-manufacturer--'; dmidecode -s system-manufacturer 2>/dev/null; echo '--dmidecode-product--'; dmidecode -s system-product-name 2>/dev/null; echo '--dmidecode-serial--'; dmidecode -s system-serial-number 2>/dev/null; echo '--cpu--'; lscpu 2>/dev/null | grep -E 'Model name|^CPU\\(s\\)|Architecture|Thread|Core'; echo '--memory--'; free -h; echo '--disk-lsblk--'; lsblk 2>/dev/null; echo '--disk-usage--'; df -h; echo '--smartmon.prom--'; cat /var/lib/node_exporter/textfile_collector/smartmon.prom 2>/dev/null; echo '--sbdm.prom--'; cat /var/lib/node_exporter/textfile_collector/sbdm.prom 2>/dev/null; echo '--overlayroot-mount--'; mount 2>/dev/null | grep overlay; true"

  # ClamAV+Lynis are an nbn_accelerate-only hardening gate (see 08_ansible-authoring.md "Flavor/
  # Cluster Conditional Branching"). freshclam status specifically: a live 2026-08-03 finding on
  # 2 hosts (warakurna, indulkana) found it chronically CDN-blocked (exit 17) — this capture
  # exists to check how widespread that is across the rest of the fleet. "running-services" gives
  # a full service-state inventory, not just failed units, per the operator's "state of installed
  # apps, scripts, services etc" scope request (2026-08-03).
  "02-services-security:echo '--failed-units--'; systemctl --failed --no-legend 2>/dev/null; echo '--teleport--'; systemctl is-active teleport autossh-teleport-openssh autossh-teleport 2>&1; echo '--dns-stack--'; systemctl is-active unbound stubby named 2>&1; echo '--clamav-daemon--'; systemctl is-active clamav-daemon 2>&1; echo '--freshclam-status--'; systemctl status clamav-freshclam --no-pager -l 2>&1 | head -12; echo '--lynis-present--'; command -v lynis 2>&1; echo '--running-services--'; systemctl list-units --type=service --state=running --no-legend --no-pager 2>/dev/null | awk '{print \$1}'; true"

  # Installed applications, custom scripts, and scheduled jobs — the "specs plus state of the
  # installed apps, scripts, services" scope added 2026-08-03. apn-mqtt-client/kohana/
  # cnmaestro-provisioning are documented apps for this flavor (08_ansible-authoring.md); the
  # /usr/local/{bin,sbin,lib} listing surfaces any undocumented custom scripts the way the
  # rcp-fleet audits in smc-file-writing-analysis found several (interfacecheckv2.sh, etc.).
  "03-apps-scripts-cron:echo '--apn-mqtt-client--'; test -d /var/www/apn-mqtt-client && echo present || echo absent; echo '--cnmaestro-provisioning-files--'; ls /usr/local/lib/cnmaestro-provisioning/ 2>/dev/null; echo '--url-capture-dir--'; (test -d /url_capture && echo 'present (v1 path)') || (test -d /var/lib/url_capture && echo 'present (v2 path)') || echo absent; echo '--kohana-portal-reflog--'; git -C /var/www/html/wifi reflog --date=iso -n3 2>/dev/null; echo '--graylog-sidecar--'; systemctl is-active graylog-sidecar 2>&1; echo '--node-exporter-prometheus--'; systemctl is-active node_exporter prometheus 2>&1; echo '--fluent-bit--'; systemctl is-active fluent-bit 2>&1; echo '--cnmaestro-provisioning-service--'; systemctl is-active cnmaestro-provisioning 2>&1; echo '--usr-local-bin--'; ls -la /usr/local/bin/ 2>/dev/null; echo '--usr-local-sbin--'; ls -la /usr/local/sbin/ 2>/dev/null; echo '--usr-local-lib--'; ls /usr/local/lib/ 2>/dev/null; echo '--root-crontab--'; crontab -l 2>&1; echo '--cron.d--'; ls /etc/cron.d/ 2>/dev/null; echo '--systemd-timers--'; systemctl list-timers --all --no-pager --no-legend 2>/dev/null; true"

  "04-portal-packages:echo '--vhost-config--'; cat /etc/apache2/sites-enabled/*.conf 2>/dev/null; echo '--mobile-app-backend--'; test -d /var/www/html/wifi-community-app-backend && echo present || echo absent; echo '--kohana-portal-dir--'; test -d /var/www/html/wifi && echo present || echo absent; echo '--key-packages--'; dpkg -l 2>/dev/null | grep -E '^ii' | grep -iE 'bind9|unbound|stubby|apache2 |php[0-9]|clamav|lynis|prometheus|node-exporter|fluent-bit|teleport|isc-dhcp-server'; true"

  # Added 2026-09-11 during the nbn_accelerate/nbn_wh portal-FQDN regression investigation (see
  # ../references/13_known-issues.md and ../references/14_pin-activation-diagnosis.md). Both
  # inventories independently had periods where smc_bases_portal_fqdn pointed at the Teleport
  # proxy hostname instead of the real portal domain; git being fixed does NOT mean a box is
  # fixed — squid.conf/Apache vhosts/cron only regenerate when the relevant role actually re-runs
  # on that box, so a box can carry the broken config for over a year after the git revert. This
  # bundle is the config-side half of that diagnosis; ../references/14_pin-activation-diagnosis.md
  # + audit-pin-activation.sh is the live-impact half — run both when investigating a suspected
  # portal-issuance problem.
  "05-portal-fqdn-status:echo '--deny-info--'; grep -m1 -i 'deny_info.*captive_portal' /etc/squid/squid.conf 2>/dev/null; echo '--squid-conf-mtime--'; stat -c '%y' /etc/squid/squid.conf 2>/dev/null; echo '--apache-sites-enabled--'; ls /etc/apache2/sites-enabled/ 2>/dev/null; echo '--sslcertcopy-cron--'; grep -h sslcertcopy /var/spool/cron/crontabs/root 2>/dev/null; true"
)

die() { echo "ERROR: $*" >&2; exit 1; }

command -v tsh >/dev/null || die "tsh not found in PATH"
tsh status >/dev/null 2>&1 || die "not logged in to Teleport — run 'tsh login' first"

[[ $# -gt 0 ]] || die "no hosts given — usage: ./collect-fleet-health.sh <site> [<site> ...]"

# Resolve bare site names to appliance names. Sites with multiple numbered hosts (e.g.
# aurukun-smc01/aurukun-smc02) must be passed with their full -smcNN suffix already — only bare
# names with NO -smcNN suffix at all get -smc01 appended. (A naive *-smc01-only check would
# mangle aurukun-smc02 into aurukun-smc02-smc01 — fixed 2026-08-03 before the first fleet-wide run.)
hosts=()
for h in "$@"; do
  [[ "$h" =~ -smc[0-9]+$ ]] && hosts+=("$h") || hosts+=("${h}-smc01")
done

mkdir -p "$OUTDIR"
MANIFEST="${OUTDIR}/MANIFEST.txt"
{
  echo "# SMC fleet-health evidence capture"
  echo "captured_at: ${STAMP}"
  echo "captured_by: $(whoami)"
  echo "cluster:     $(tsh status 2>/dev/null | awk '/Cluster:/ {print $2}' | head -1)"
  echo "ssh_user:    ${SSH_USER}"
  echo "mode:        read-only (see SAFETY CONTRACT in scripts/collect-fleet-health.sh)"
  echo "hosts:       ${hosts[*]}"
  echo ""
  echo "## captures"
  for c in "${CAPTURES[@]}"; do echo "  ${c%%:*}"; done
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
