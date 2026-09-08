#!/usr/bin/env bash
# collect-smc-evidence-full.sh — broad read-only diagnostic capture from SMC appliances via Teleport.
#
# ORIGIN: written 2026-08-25. Companion to collect-smc-evidence.sh, which is deliberately narrow (WAN routing / topology drift, ~25 captures, feeds
# analyse-routing-drift.py and analyse-topology-interface-match.py). This script is the wide one: it captures the whole box across every subsystem in
# references/02_service-map.md, for incident triage, pre-deploy baselines, and post-deploy verification.
#
# WHICH SCRIPT DO I WANT?
#   collect-smc-evidence.sh       routing/topology question, feeds the two analysers. Small, fast, stable output contract.
#   collect-smc-evidence-full.sh  "what is going on with this box", or "capture everything before/after I deploy". This file.
#
# SAFETY CONTRACT
#   Every remote command below is read-only: reads files, queries systemd/ip/tc, runs config *validators* (dhcpd -t, unbound-checkconf, named-checkconf,
#   nginx -t style) which parse without loading. No file is written, no service restarted, no interface touched, no packet injected. The command set is
#   hardcoded — this script accepts host names and group names only, never arbitrary commands. Do not add a command here that mutates state; run it by
#   hand and record it in the analysis instead. Specifically excluded on purpose: tcpdump (needs a time bound and a human), speedtest (bills data on a
#   metered link), apt update, any systemctl verb other than status/show/list-*/is-*/cat.
#
# SECRETS
#   Unlike the narrow collector, this one reads service configs, and this fleet stores credentials in plaintext (no ansible-vault anywhere — see
#   references/13_known-issues.md). Asterisk SIP secrets, Teleport join tokens, Graylog tokens and API keys WILL appear in raw output. Captures are
#   therefore redacted by default: values following password/secret/token/key-ish keys are replaced with <REDACTED>. Pass --no-redact only when you
#   genuinely need the value, and then treat the whole evidence directory as a credential store. Redaction is pattern-based, so it is a reasonable
#   default, NOT a guarantee — never attach a capture directory to a ticket without reading it first.
#
# Usage
#   ./collect-smc-evidence-full.sh <site> [<site> ...]              # bare name or full -smc01
#   ./collect-smc-evidence-full.sh yakanarra --only network,rise
#   ./collect-smc-evidence-full.sh umoona --skip voip,portal
#   ./collect-smc-evidence-full.sh --list-groups
#   ./collect-smc-evidence-full.sh yakanarra --no-redact
#
# Output (default: next to this script — override with OUTDIR_ROOT)
#   <OUTDIR_ROOT>/evidence-full/<YYYYMMDD_hhmm>/<host>/<group>/<capture>.txt
#   <OUTDIR_ROOT>/evidence-full/<YYYYMMDD_hhmm>/<host>/SUMMARY.txt
#   <OUTDIR_ROOT>/evidence-full/<YYYYMMDD_hhmm>/MANIFEST.txt
#
# Requires: tsh, already logged in (`tsh status`).
#
# PLATFORM
#   The fleet is x86 (BOXER-6404 / BOXER-6641 chassis) and ARM64 Raspberry Pi 4B, and BOTH capture sets are implemented. Platform is detected per host
#   and the capture list is filtered accordingly: the `rpi` group runs only on a Pi, and the x86-only probes (dmidecode, smartctl) are dropped there
#   rather than filling the summary with absences that read like findings. A host whose platform cannot be identified gets the platform-neutral set.

set -uo pipefail

REPO_ROOT="${OUTDIR_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STAMP="$(date '+%Y%m%d_%H%M')"
OUTDIR="${REPO_ROOT}/evidence-full/${STAMP}"
SSH_USER="${SMC_SSH_USER:-root}"
REDACT=1

# --------------------------------------------------------------------------------------------------------------------------------------------------
# CAPTURES — "group|name|command". One SSH session per host runs all of them; see build_remote_script().
#
# Ordering within a group is deliberate: cheap identity/state first, large file dumps last, so a truncated or interrupted capture still yields the
# orienting facts.
# --------------------------------------------------------------------------------------------------------------------------------------------------

CAPTURES=(
  # ---- identity: which box is this, what is it, how long has it been up --------------------------------------------------------------------------
  "identity|hostname|hostnamectl 2>/dev/null || hostname -f"
  "identity|uptime|uptime; echo; cat /proc/uptime"
  "identity|dmidecode-model|dmidecode -s system-product-name 2>/dev/null"
  "identity|dmidecode-system|dmidecode -t system 2>/dev/null"
  "identity|dmidecode-baseboard|dmidecode -t baseboard 2>/dev/null"
  "identity|cpuinfo|lscpu 2>/dev/null || cat /proc/cpuinfo"
  "identity|meminfo|free -h; echo; head -5 /proc/meminfo"
  "identity|machine-id|cat /etc/machine-id 2>/dev/null"
  # site_eclipse_siteid drives the Teleport SSH port (50000 + siteid) and the DHCP/subnet maths. Ansible facts are the only on-box trace of it.
  "identity|ansible-local-facts|cat /etc/ansible/facts.d/*.fact 2>/dev/null"

  # ---- os: release, kernel, pending updates ------------------------------------------------------------------------------------------------------
  "os|os-release|cat /etc/os-release"
  "os|kernel|uname -a; echo; cat /proc/cmdline"
  "os|kernel-installed|dpkg -l 'linux-image-*' 2>/dev/null | grep '^ii' || true"
  # The Pi half of the fleet pins linux-image-*-raspi via /etc/apt/preferences.d/pin-kernel at priority 1001; x86 pins nothing. Capture both so a
  # mixed-version fleet stays readable. See the Ubuntu migration plan's kernel-baselines section.
  "os|apt-pins|cat /etc/apt/preferences.d/* 2>/dev/null"
  "os|apt-holds|apt-mark showhold 2>/dev/null"
  "os|apt-sources|cat /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null"
  "os|timedate|timedatectl 2>/dev/null; echo; chronyc tracking 2>/dev/null || ntpq -p 2>/dev/null"

  # ---- overlay: overlayroot state. THE question on any SMC — did my change persist? ----------------------------------------------------------------
  # references/07_hardware-overlay.md: writes land in tmpfs and are lost on reboot unless the lower dir was remounted rw. Every overlay guard in the
  # repo greps mount output for the literal string "overlayroot on / type overlay", so capture the raw mount table, not a parsed summary.
  "overlay|mount|mount"
  "overlay|mount-overlay|mount | grep -i overlay || echo 'NO OVERLAY MOUNTS'"
  "overlay|overlayroot-conf|cat /etc/overlayroot.conf 2>/dev/null"
  "overlay|overlayroot-local|cat /etc/overlayroot.local.conf 2>/dev/null"
  "overlay|overlay-usage|df -h /media/root-rw /media/root-ro / 2>/dev/null"
  "overlay|overlay-inodes|df -i /media/root-rw /media/root-ro / 2>/dev/null"
  "overlay|overlay-upper-top|du -xh --max-depth=3 /media/root-rw/overlay 2>/dev/null | sort -rh | head -40"

  # ---- storage -----------------------------------------------------------------------------------------------------------------------------------
  "storage|df|df -h"
  "storage|df-inodes|df -i"
  "storage|lsblk|lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,MODEL 2>/dev/null"
  "storage|fstab|cat /etc/fstab"
  "storage|largest-files|find /var /opt /home -xdev -type f -size +50M -printf '%s\\t%p\\n' 2>/dev/null | sort -rn | head -40"
  "storage|smart-health|for d in /dev/sd? /dev/nvme?n?; do [ -e \"\$d\" ] && { echo \"== \$d\"; smartctl -H \"\$d\" 2>/dev/null; }; done"

  # ---- services: what is running, what is broken ---------------------------------------------------------------------------------------------------
  "services|failed-units|systemctl list-units --state=failed --no-pager --no-legend"
  "services|units-enabled|systemctl list-unit-files --state=enabled --no-pager --no-legend"
  "services|smc-units|systemctl list-units 'smc*' 'rise*' 'autossh*' 'iperf*' --all --no-pager --no-legend"
  "services|timers|systemctl list-timers --all --no-pager --no-legend"
  "services|boot-time|systemd-analyze 2>/dev/null; echo; systemd-analyze blame 2>/dev/null | head -25"

  # ---- network: addresses, routes, the ECMP picture ------------------------------------------------------------------------------------------------
  "network|ip-addr|ip -br addr show"
  "network|ip-addr-full|ip addr show"
  "network|ip-link|ip -br link show"
  "network|ip-link-stats|ip -s link show"
  "network|ip-route|ip route show"
  "network|ip-route-table-all|ip route show table all"
  "network|ip-rule|ip rule show"
  "network|rt-tables|cat /etc/iproute2/rt_tables /etc/iproute2/rt_tables.d/* 2>/dev/null"
  "network|netplan|cat /etc/netplan/*.yaml"
  "network|netplan-mtime|stat --format='%Y %y %n' /etc/netplan/*.yaml 2>/dev/null"
  "network|networkd-status|networkctl status --no-pager 2>/dev/null"
  "network|bridges|bridge link show 2>/dev/null; echo; bridge vlan show 2>/dev/null"
  "network|arp|ip neigh show"
  "network|sysctl-net|sysctl -a 2>/dev/null | grep -E 'net\\.ipv4\\.(ip_forward|conf\\.(all|default)\\.(rp_filter|arp_))|net\\.ipv4\\.fib_multipath' || true"
  "network|conntrack-count|cat /proc/sys/net/netfilter/nf_conntrack_count /proc/sys/net/netfilter/nf_conntrack_max 2>/dev/null"
  # Deployed by smc_network to the FILESYSTEM ROOT, not /usr/local/bin — corrected 2026-08-25 after the narrow collector was found to have been looking
  # in the wrong place and failing this capture on every site, silently, since it was written. See roles/smc_network/tasks/ubuntu.yml:346.
  "network|interfacecheck-script|cat /interfacecheckv2.sh 2>/dev/null"
  "network|interfacecheck-prom|cat /var/lib/node_exporter/textfile_collector/my_node_interfacecheck_success.prom 2>/dev/null"

  # ---- dhcp: both halves — the client (WAN leases, ECMP) and the server (LAN scopes) ----------------------------------------------------------------
  # The SMC override is the extensionless /etc/dhcp/dhclient-enter-hooks, NOT the .d/ directory — .d/ holds stock Debian fragments. This is the file
  # that decides ECMP membership, and the one that silently keeps an old interface list after a topology change.
  "dhcp|dhclient-enter-hooks|cat /etc/dhcp/dhclient-enter-hooks 2>/dev/null"
  "dhcp|dhclient-enter-hooks-d|cat /etc/dhcp/dhclient-enter-hooks.d/* 2>/dev/null"
  "dhcp|hook-mtime|stat --format='%Y %y %n' /etc/dhcp/dhclient-enter-hooks 2>/dev/null"
  "dhcp|dhclient-units|systemctl list-units 'dhclient@*' --all --no-pager --no-legend"
  "dhcp|dhclient-confs|for f in /etc/dhcp/dhclient.*.conf; do [ -e \"\$f\" ] && { echo \"== \$f\"; cat \"\$f\"; }; done 2>/dev/null"
  "dhcp|dhclient-leases|for f in /var/lib/dhcp/dhclient.*.leases; do [ -e \"\$f\" ] && { echo \"== \$f\"; tail -40 \"\$f\"; }; done 2>/dev/null"
  "dhcp|dhcpd-conf|cat /etc/dhcp/dhcpd.conf 2>/dev/null"
  "dhcp|dhcpd-configtest|dhcpd -t -cf /etc/dhcp/dhcpd.conf 2>&1 || true"
  "dhcp|dhcpd-status|systemctl status isc-dhcp-server --no-pager 2>/dev/null"
  # Fleet-wide known failure, present on every site checked 2026-08-25 — capture it so it is visibly pre-existing rather than a new finding.
  "dhcp|dhcpd6-status|systemctl status isc-dhcp-server6 --no-pager 2>/dev/null"
  "dhcp|dhcpd-leases-count|wc -l /var/lib/dhcp/dhcpd.leases 2>/dev/null"

  # ---- dns: three independent systems on one box — see references/02_service-map.md ------------------------------------------------------------------
  # (1) unbound+stubby serve LAN clients on non-smc_ltp hosts; (2) bind/named replaces them entirely on smc_ltp hosts, with the cambium RPZ; and
  # (3) systemd-resolved handles the HOST's own lookups with DNSStubListener=no, so the box's own getaddrinfo bypasses all of the above.
  "dns|resolved-status|resolvectl status 2>/dev/null"
  "dns|resolved-conf|cat /etc/systemd/resolved.conf /etc/systemd/resolved.conf.d/* 2>/dev/null"
  "dns|resolv-conf|ls -l /etc/resolv.conf; echo; cat /etc/resolv.conf"
  "dns|unbound-conf|cat /etc/unbound/unbound.conf /etc/unbound/unbound.conf.d/* 2>/dev/null"
  "dns|unbound-checkconf|unbound-checkconf 2>&1 || true"
  "dns|unbound-status|systemctl status unbound --no-pager 2>/dev/null"
  "dns|stubby-conf|cat /etc/stubby/stubby.yml 2>/dev/null"
  "dns|stubby-status|systemctl status stubby --no-pager 2>/dev/null"
  "dns|named-checkconf|named-checkconf 2>&1 || true"
  "dns|named-status|systemctl status named bind9 --no-pager 2>/dev/null"
  "dns|named-zones|ls -la /etc/bind/ 2>/dev/null"
  "dns|listeners|ss -lnup 2>/dev/null | grep -E ':53|:5353|:60053|:60853' || echo 'no DNS listeners matched'"

  # ---- firewall ----------------------------------------------------------------------------------------------------------------------------------
  # smc_iptables manages filter, mangle and nat (and references raw) — 'iptables -S' alone shows only filter and would miss NAT and mangle entirely.
  "firewall|iptables-save|iptables-save"
  "firewall|iptables-filter|iptables -S"
  "firewall|iptables-nat|iptables -t nat -S"
  "firewall|iptables-mangle|iptables -t mangle -S"
  "firewall|iptables-raw|iptables -t raw -S"
  "firewall|iptables-counters|iptables -L -n -v --line-numbers 2>/dev/null"
  "firewall|rules-v4|cat /etc/iptables/rules.v4 2>/dev/null"

  # ---- qos ---------------------------------------------------------------------------------------------------------------------------------------
  "qos|tc-qdisc|tc -s qdisc show 2>/dev/null"
  "qos|tc-class|tc -s class show 2>/dev/null | head -100"
  "qos|ip-link-ifb|ip -br link show type ifb 2>/dev/null"
  "qos|qos-script|cat /etc/networkd-dispatcher/routable.d/50-qos.sh 2>/dev/null"
  # Manual out-of-band TBF ingress shaping, operator-identified 2026-07-29 — NOT rendered by any smc_* role, so it is invisible to the repo.
  "qos|ingress-shaping-script|cat /usr/local/sbin/internet-ingress-shaping.sh 2>/dev/null"
  "qos|ingress-shaping-service|cat /etc/systemd/system/internet-shaping.service 2>/dev/null"
  "qos|ingress-shaping-status|systemctl status internet-shaping.service --no-pager 2>/dev/null"

  # ---- wifi --------------------------------------------------------------------------------------------------------------------------------------
  "wifi|hostapd-status|systemctl status 'hostapd*' --no-pager 2>/dev/null"
  "wifi|hostapd-conf|cat /etc/hostapd/*.conf 2>/dev/null"
  "wifi|iw-dev|iw dev 2>/dev/null"
  "wifi|regdomain|iw reg get 2>/dev/null"
  "wifi|cnmaestro-status|systemctl status cnmaestro-provisioning --no-pager 2>/dev/null"
  "wifi|cnmaestro-log-tail|tail -60 /var/log/cnmaestro-provisioning/*.log 2>/dev/null"
  "wifi|redis-ping|redis-cli ping 2>/dev/null; redis-cli dbsize 2>/dev/null"

  # ---- voip --------------------------------------------------------------------------------------------------------------------------------------
  "voip|asterisk-status|systemctl status asterisk --no-pager 2>/dev/null"
  # asterisk.service on this fleet is an LSB init wrapper, so systemd reports "active (exited)" once the script returns 0 — WHETHER OR NOT a
  # daemon is left running. Confirmed on umoona-smc01 2026-08-25: unit active (exited), zero asterisk processes, no control socket, and every
  # `asterisk -rx` query below failing with "Unable to connect to remote asterisk". Never read the unit state alone as "Asterisk is up".
  "voip|asterisk-procs|pgrep -a asterisk || echo 'NO ASTERISK PROCESS RUNNING (unit state alone is not proof — LSB wrapper reports active/exited)'"
  "voip|asterisk-ctl-socket|ls -la /var/run/asterisk/ 2>&1 | head -20"
  "voip|asterisk-version|asterisk -rx 'core show version' 2>/dev/null"
  "voip|asterisk-uptime|asterisk -rx 'core show uptime' 2>/dev/null"
  "voip|pjsip-endpoints|asterisk -rx 'pjsip show endpoints' 2>/dev/null"
  "voip|pjsip-registrations|asterisk -rx 'pjsip show registrations' 2>/dev/null"
  "voip|dialplan|asterisk -rx 'dialplan show' 2>/dev/null | head -200"
  "voip|cdr-status|asterisk -rx 'cdr show status' 2>/dev/null"
  # Master.csv size is the cheapest signal that a site's handsets are actually in use — see the 2026-08-19 umoona investigation, where an
  # unchanged 2,885-byte file meant "nobody has ever called", and unanswered/congestion logging being off makes that indistinguishable from
  # "every call fails". Size plus mtime is the whole tell.
  "voip|cdr-master|ls -la /var/log/asterisk/cdr-csv/ 2>/dev/null"

  # ---- portal: captive portal + its database ------------------------------------------------------------------------------------------------------
  # Portal PHP runs as mod_php under Apache as www-data — NOT PHP-FPM. See references/10_captive-portal.md.
  "portal|apache-status|systemctl status apache2 --no-pager 2>/dev/null"
  "portal|apache-configtest|apache2ctl configtest 2>&1 || true"
  "portal|apache-modules|apache2ctl -M 2>/dev/null"
  "portal|apache-vhosts|apache2ctl -S 2>&1 || true"
  "portal|php-version|php -v 2>/dev/null; echo; php -m 2>/dev/null | head -60"
  "portal|php-ini-key|php -i 2>/dev/null | grep -E 'short_open_tag|memory_limit|error_log|display_errors|Loaded Configuration' || true"
  "portal|db-status|systemctl status mariadb mysql --no-pager 2>/dev/null; echo; dpkg -l 2>/dev/null | grep -E 'mariadb-server|mysql-server' || echo 'NO DATABASE SERVER PACKAGE INSTALLED'"
  "portal|apache-error-tail|tail -80 /var/log/apache2/error.log 2>/dev/null"
  "portal|www-tree|ls -la /var/www/ 2>/dev/null; echo; find /var/www -maxdepth 2 -type d -name config 2>/dev/null"
  # The per-site application/config/site.txt + config.txt are UNTRACKED and per-site, so they are the blocking items on any card swap or
  # reimage (see the Ubuntu migration plan). List them; do not cat them — they carry site credentials.
  "portal|portal-config-list|for d in /var/www/*/application/config /var/www/*/system/config; do [ -d \"\$d\" ] && { echo \"== \$d\"; ls -la \"\$d\"; }; done 2>/dev/null"

  # ---- monitoring: node_exporter, local prometheus, textfile collectors ---------------------------------------------------------------------------
  # A textfile collector that stopped writing does not alert as "broken" — it alerts as no-data, or not at all. mtimes are the real check, which is
  # why the staleness windows in references/02_service-map.md exist. Capture mtimes AND contents.
  "monitoring|node-exporter-status|systemctl status node_exporter prometheus-node-exporter --no-pager 2>/dev/null"
  "monitoring|textfile-listing|ls -la /var/lib/node_exporter/textfile_collector/ 2>/dev/null"
  "monitoring|textfile-mtimes|stat --format='%Y %y %n' /var/lib/node_exporter/textfile_collector/*.prom 2>/dev/null"
  "monitoring|textfile-contents|for f in /var/lib/node_exporter/textfile_collector/*.prom; do [ -e \"\$f\" ] && { echo \"== \$f\"; cat \"\$f\"; }; done 2>/dev/null"
  "monitoring|prometheus-status|systemctl status prometheus --no-pager 2>/dev/null"
  "monitoring|prometheus-conf|cat /etc/prometheus/prometheus.yml 2>/dev/null"
  "monitoring|speedtest-status|systemctl status speedtest-exporter --no-pager 2>/dev/null"
  "monitoring|graylog-sidecar|systemctl status graylog-sidecar collector-sidecar --no-pager 2>/dev/null"
  "monitoring|rsyslog-conf|cat /etc/rsyslog.d/*.conf 2>/dev/null"

  # ---- rise: the RISE observability/resilience stack -----------------------------------------------------------------------------------------------
  "rise|rise-units|systemctl list-units 'rise*' --all --no-pager --no-legend"
  "rise|rise-timers|systemctl list-timers 'rise*' --all --no-pager --no-legend"
  "rise|rise-status-dir|ls -la /opt/rise/status/ 2>/dev/null"
  "rise|rise-logcaps-json|cat /opt/rise/status/logcaps.json 2>/dev/null"
  "rise|rise-healthcheck-journal|journalctl -u rise-healthcheck --since '24 hours ago' --no-pager 2>/dev/null | tail -60"
  "rise|rise-watchdog-journal|journalctl -u rise-watchdog --since '24 hours ago' --no-pager 2>/dev/null | tail -60"
  "rise|rise-logcaps-journal|journalctl -u rise-logcaps --since '24 hours ago' --no-pager 2>/dev/null | tail -60"
  "rise|rise-logrotate|cat /etc/logrotate.d/rise-logcaps 2>/dev/null"

  # ---- access: how we get in, and whether we will keep getting in --------------------------------------------------------------------------------
  "access|teleport-status|systemctl status teleport --no-pager 2>/dev/null"
  "access|teleport-conf|cat /etc/teleport.yaml 2>/dev/null"
  "access|autossh-teleport|systemctl status autossh-teleport-openssh --no-pager 2>/dev/null"
  "access|autossh-federation|systemctl status autossh-prometheus-federation --no-pager 2>/dev/null"
  "access|autossh-units|systemctl cat 'autossh*' --no-pager 2>/dev/null"
  "access|sshd-config|sshd -T 2>/dev/null || cat /etc/ssh/sshd_config"
  "access|listening-ports|ss -lntup 2>/dev/null"

  # ---- rpi: Raspberry Pi 4B only. Gated by platform detection — never runs on x86, and the x86-only probes never run here. ---------------------------
  # Every command below verified present and read-only on marta-marta-smc01 (Pi 4B Rev 1.5, aarch64, Ubuntu 22.04) 2026-08-25.
  # vcgencmd/rpi-eeprom-update are QUERIES here: rpi-eeprom-update is never given -a, which is the flag that would stage a firmware write.
  "rpi|model|tr -d '\\000' < /proc/device-tree/model 2>/dev/null; echo"
  # The revision code decides tryboot eligibility and RAM size. An 8 GB 4B is only ever d03114 (rev 1.4) or d03115 (rev 1.5), and the EEPROM
  # write-protect caveat in the tryboot docs applies solely to rev 1.0/1.1 — so this line settles whether A/B boot is available on the box.
  "rpi|revision|grep -E '^(Revision|Serial|Model|Hardware)' /proc/cpuinfo"
  # 26.04 will not boot on a Pi 4/400/CM4 whose EEPROM predates 2022-11-25 (Pi 5/500/CM5: 2025-02-11). This is the pre-migration audit item.
  "rpi|eeprom-version|rpi-eeprom-update 2>&1"
  "rpi|eeprom-config|rpi-eeprom-config 2>/dev/null"
  # Undervoltage and thermal throttling are real field failures on this fleet. get_throttled is a bitmask: bit 0 undervoltage now, bit 16 undervoltage
  # since boot, bit 2 currently throttled, bit 18 throttled since boot. A non-zero value with only the "since boot" bits set is history, not a live fault.
  "rpi|throttled|vcgencmd get_throttled 2>&1; vcgencmd measure_temp 2>&1; vcgencmd measure_volts core 2>&1; vcgencmd get_mem arm 2>&1; vcgencmd get_mem gpu 2>&1"
  "rpi|boot-firmware-listing|ls -la /boot/firmware/ 2>/dev/null"
  "rpi|config-txt|cat /boot/firmware/config.txt 2>/dev/null"
  "rpi|cmdline-txt|cat /boot/firmware/cmdline.txt 2>/dev/null"
  # autoboot.txt and the current/ new/ old/ folders are the piboot A/B layout Canonical ships from 25.10. Absent on 22.04 — capturing the absence now
  # is what makes the before/after comparison possible when the fleet moves to 26.04.
  "rpi|autoboot-txt|cat /boot/firmware/autoboot.txt 2>/dev/null"
  "rpi|piboot-layout|ls -la /boot/firmware/current /boot/firmware/new /boot/firmware/old 2>/dev/null || echo 'no piboot A/B layout (expected pre-25.10)'"
  "rpi|piboot-units|systemctl list-units 'piboot*' --all --no-pager --no-legend 2>/dev/null"
  # 26.04 keeps up to three boot asset sets; older images allocated only 256 MB to this partition, which is why flash-kernel deletes old/ first.
  "rpi|boot-partition|df -h /boot/firmware 2>/dev/null; echo; df -i /boot/firmware 2>/dev/null"
  # SD health. NOTE: life_time / pre_eol_info are eMMC attributes and are NOT present on an SD-booted Pi 4 — verified 2026-08-25. Capture what the
  # SD card actually exposes instead; cid/csd/ssr carry manufacturer, date and wear-relevant fields.
  "rpi|sd-card|head -n 1 /sys/block/mmcblk0/device/{name,type,date,manfid,oemid,fwrev,hwrev,serial,cid,csd,ssr,erase_size,preferred_erase_size} 2>/dev/null"
  "rpi|mmc-errors|dmesg -T 2>/dev/null | grep -iE 'mmc|sd card|I/O error' | tail -30"
  # copymods on /usr/lib/modules is a FAULT on 22.04 that smc_update_kernel tears down (role tasks/main.yml:93-95), but cloud-initramfs-tools 0.55
  # makes it the DEFAULT under dracut on 26.04 — so the platform default becomes the fault condition. Capture the current state as the before-picture.
  "rpi|copymods|grep -E 'copymods' /proc/self/mounts || echo 'copymods not mounted (expected on 22.04)'"
  "rpi|modules-dirs|uname -r; echo; ls -la /lib/modules/ 2>/dev/null"
  # flash-kernel is NEVER invoked here — it writes to the boot partition. Only its config and state are read.
  "rpi|flash-kernel-config|cat /etc/default/flash-kernel 2>/dev/null; echo; ls -la /etc/flash-kernel/ 2>/dev/null"
  # zram is rct/wh flavours only. The legacy ozai-zram vs rise-zram mismatch has bitten this fleet before, so capture both the device and the units.
  "rpi|zram|zramctl 2>/dev/null; echo; head -n 1 /sys/block/zram0/{disksize,comp_algorithm,mem_used_total,orig_data_size,compr_data_size} 2>/dev/null"
  "rpi|zram-units|systemctl list-units '*zram*' --all --no-pager --no-legend 2>/dev/null"
  "rpi|watchdog|cat /sys/class/watchdog/watchdog0/{identity,state,timeout} 2>/dev/null; echo; systemctl list-units '*watchdog*' --all --no-pager --no-legend 2>/dev/null"

  # ---- logs: bounded tails only. Never a full journal — it is enormous and mostly noise ------------------------------------------------------------
  "logs|journal-errors|journalctl -p err --since '24 hours ago' --no-pager 2>/dev/null | tail -120"
  "logs|journal-boot|journalctl -b -p warning --no-pager 2>/dev/null | tail -80"
  "logs|reboot-history|last -x reboot 2>/dev/null | head -20"
  "logs|log-sizes|du -xh --max-depth=2 /var/log 2>/dev/null | sort -rh | head -30"
  "logs|dmesg-tail|dmesg -T 2>/dev/null | tail -60"
)

# Group order for display/selection. Keep in sync with CAPTURES.
CAPTURE_GROUPS=(identity os overlay storage services network dhcp dns firewall qos wifi voip portal monitoring rise access rpi logs)

# Captures that only make sense on x86. On a Pi, dmidecode is absent entirely and smartctl reports nothing useful about an SD card — running them
# there would fill the summary with absences that look like findings. The rpi group is the mirror image: it runs ONLY on a Pi.
X86_ONLY=("identity|dmidecode-model" "identity|dmidecode-system" "identity|dmidecode-baseboard" "storage|smart-health")

# --------------------------------------------------------------------------------------------------------------------------------------------------

die() { echo "ERROR: $*" >&2; exit 1; }

list_groups() {
  echo "Capture groups (use --only / --skip):"
  for g in "${CAPTURE_GROUPS[@]}"; do
    n=0
    for e in "${CAPTURES[@]}"; do [[ "${e%%|*}" == "$g" ]] && n=$((n + 1)); done
    printf '  %-12s %2d captures\n' "$g" "$n"
  done
  echo ""
  echo "Total: ${#CAPTURES[@]} captures."
}

# Build one remote bash script for the selected captures. Delimiters let us split the single stream back into per-capture files locally, which keeps
# this to ONE ssh round trip per host instead of one per capture — the narrow collector's per-capture model would mean ~150 sequential Teleport
# sessions here, which is both slow and noisy in the audit log.
build_remote_script() {
  local selected=("$@")
  echo "export LC_ALL=C PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  for entry in "${selected[@]}"; do
    local group="${entry%%|*}"
    local rest="${entry#*|}"
    local name="${rest%%|*}"
    local cmd="${rest#*|}"
    printf 'printf "\\n===SMC-CAPTURE %s %s===\\n"\n' "$group" "$name"
    printf '{ %s ; } 2>&1\n' "$cmd"
    printf 'printf "===SMC-RC %%s===\\n" "$?"\n'
  done
  printf 'printf "\\n===SMC-CAPTURE-END===\\n"\n'
}

# Detect platform before capturing so we never run x86-only probes against a Pi and report the failures as findings.
detect_platform() {
  local host="$1" model
  model="$(tsh ssh "${SSH_USER}@${host}" \
    'if [ -r /proc/device-tree/model ]; then tr -d "\000" < /proc/device-tree/model; echo; else dmidecode -s system-product-name 2>/dev/null || echo unknown; fi' \
    2>/dev/null | grep -v '^$' | tail -1)"
  case "$model" in
    *"Raspberry Pi"*) echo "rpi|${model}" ;;
    ""|unknown)       echo "unknown|unknown" ;;
    *)                echo "x86|${model}" ;;
  esac
}

# Pattern-based redaction. Deliberately conservative about what it keeps: it blanks the VALUE and preserves the KEY, so "there is a secret configured
# here" stays visible (which is itself diagnostic) while the secret does not land on disk.
redact_file() {
  local f="$1"
  sed -E -i.bak \
    -e 's/((password|passwd|secret|token|api[_-]?key|apikey|auth[_-]?key|private[_-]?key|client[_-]?secret|master[_-]?key)[[:space:]]*[:=][[:space:]]*)[^[:space:],;]+/\1<REDACTED>/Ig' \
    -e 's/(Authorization:[[:space:]]*(Bearer|Basic)[[:space:]]+)[A-Za-z0-9._~+\/-]+=*/\1<REDACTED>/Ig' \
    "$f" 2>/dev/null && rm -f "${f}.bak"
}

# ---- argument parsing ----------------------------------------------------------------------------------------------------------------------------

hosts=()
only=""
skip=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --list-groups) list_groups; exit 0 ;;
    --only)        only="$2";  shift 2 ;;
    --only=*)      only="${1#*=}"; shift ;;
    --skip)        skip="$2";  shift 2 ;;
    --skip=*)      skip="${1#*=}"; shift ;;
    --no-redact)   REDACT=0;   shift ;;
    -h|--help)     sed -n '2,45p' "${BASH_SOURCE[0]}"; exit 0 ;;
    -*)            die "unknown option: $1" ;;
    *)             [[ "$1" == *-smc01 ]] && hosts+=("$1") || hosts+=("${1}-smc01"); shift ;;
  esac
done

command -v tsh >/dev/null || die "tsh not found in PATH"
tsh status >/dev/null 2>&1 || die "not logged in to Teleport — run 'tsh login' first"
[[ ${#hosts[@]} -gt 0 ]] || die "no hosts given — usage: ./collect-smc-evidence-full.sh <site> [<site> ...] (see --help, --list-groups)"

# Validate group names up front rather than silently capturing nothing.
for g in ${only//,/ } ${skip//,/ }; do
  [[ " ${CAPTURE_GROUPS[*]} " == *" $g "* ]] || die "unknown group: $g (see --list-groups)"
done

selected=()
for entry in "${CAPTURES[@]}"; do
  g="${entry%%|*}"
  [[ -n "$only" && " ${only//,/ } " != *" $g "* ]] && continue
  [[ -n "$skip" && " ${skip//,/ } " == *" $g "* ]] && continue
  selected+=("$entry")
done
[[ ${#selected[@]} -gt 0 ]] || die "no captures selected"

# ---- run -----------------------------------------------------------------------------------------------------------------------------------------

mkdir -p "$OUTDIR"
MANIFEST="${OUTDIR}/MANIFEST.txt"
{
  echo "# SMC full diagnostic capture"
  echo "captured_at: ${STAMP}"
  echo "captured_by: $(whoami)"
  echo "cluster:     $(tsh status 2>/dev/null | awk '/Cluster:/ {print $2}')"
  echo "ssh_user:    ${SSH_USER}"
  echo "mode:        read-only (see SAFETY CONTRACT in scripts/collect-smc-evidence-full.sh)"
  echo "redaction:   $([[ $REDACT -eq 1 ]] && echo 'on (default)' || echo 'OFF — treat this directory as a credential store')"
  echo "groups:      ${only:-all}${skip:+ (minus ${skip})}"
  echo "captures:    ${#selected[@]} of ${#CAPTURES[@]}"
  echo "hosts:       ${hosts[*]}"
  echo ""
  echo "## capture definitions"
  for c in "${selected[@]}"; do printf '  %-12s %-28s %s\n' "${c%%|*}" "$(t="${c#*|}"; echo "${t%%|*}")" "${c##*|}"; done
  echo ""
  echo "## results"
} > "$MANIFEST"

# Filter the selected captures for one host's platform: drop the rpi group on x86, drop the x86-only probes on a Pi. Anything else runs everywhere.
filter_for_platform() {
  local platform="$1" entry key
  for entry in "${selected[@]}"; do
    key="${entry%|*}"
    if [[ "${entry%%|*}" == "rpi" ]]; then
      [[ "$platform" == "rpi" ]] && printf '%s\n' "$entry"
      continue
    fi
    if [[ "$platform" == "rpi" && " ${X86_ONLY[*]} " == *" $key "* ]]; then
      continue
    fi
    printf '%s\n' "$entry"
  done
}

for host in "${hosts[@]}"; do
  echo "==> ${host}"
  hostdir="${OUTDIR}/${host}"
  mkdir -p "$hostdir"

  platform_info="$(detect_platform "$host")"
  platform="${platform_info%%|*}"
  model="${platform_info#*|}"
  printf '  platform: %s (%s)\n' "$platform" "$model"
  echo "  ${host}: platform=${platform} model=${model}" >> "$MANIFEST"

  host_selected=()
  while IFS= read -r line; do [[ -n "$line" ]] && host_selected+=("$line"); done < <(filter_for_platform "$platform")
  if [[ ${#host_selected[@]} -eq 0 ]]; then
    echo "  no captures apply to this platform — skipping"
    echo "  ${host}: SKIPPED — no captures apply to platform ${platform}" >> "$MANIFEST"
    continue
  fi
  printf '  captures: %d selected for this platform\n' "${#host_selected[@]}"
  echo "  ${host}: ${#host_selected[@]} captures selected for platform ${platform}" >> "$MANIFEST"
  if [[ "$platform" == "unknown" ]]; then
    echo "  NOTE: platform not identified — rpi captures skipped, x86 probes attempted anyway."
    echo "  ${host}: NOTE platform unknown — rpi captures skipped" >> "$MANIFEST"
  fi
  remote_script="$(build_remote_script "${host_selected[@]}")"

  raw="${hostdir}/_raw-stream.txt"
  if ! printf '%s\n' "$remote_script" | tsh ssh "${SSH_USER}@${host}" 'bash -s' > "$raw" 2>"${raw}.err"; then
    # A non-zero overall rc is expected — individual captures fail routinely (a service that is not installed on this flavour). Only treat a
    # completely empty stream as a real failure, since that means the session itself did not run.
    if [[ ! -s "$raw" ]]; then
      echo "  SESSION FAILED — see $(basename "$raw").err"
      echo "  ${host}: SESSION FAILED — see ${host}/_raw-stream.txt.err" >> "$MANIFEST"
      continue
    fi
  fi
  [[ -s "${raw}.err" ]] || rm -f "${raw}.err"

  # Split the single stream into per-group/per-capture files.
  ok=0; empty=0; failed=0
  summary="${hostdir}/SUMMARY.txt"
  : > "$summary"

  current_group=""; current_name=""; outfile=""
  while IFS= read -r line; do
    if [[ "$line" =~ ^===SMC-CAPTURE\ ([a-z]+)\ ([a-z0-9-]+)===$ ]]; then
      current_group="${BASH_REMATCH[1]}"
      current_name="${BASH_REMATCH[2]}"
      mkdir -p "${hostdir}/${current_group}"
      outfile="${hostdir}/${current_group}/${current_name}.txt"
      : > "$outfile"
      continue
    fi
    if [[ "$line" =~ ^===SMC-RC\ ([0-9]+)===$ ]]; then
      rc="${BASH_REMATCH[1]}"
      if [[ -n "$outfile" ]]; then
        # Strip the single trailing blank line the delimiter printf introduces.
        sed -i.bak -e '${/^$/d;}' "$outfile" 2>/dev/null && rm -f "${outfile}.bak"
        lines=$(wc -l < "$outfile" | tr -d ' ')
        if [[ "$rc" != "0" && "$lines" -eq 0 ]]; then
          # Classify the absence rather than calling it all "failed". On a healthy box most non-zero rcs mean a subsystem is simply not deployed on
          # this flavour, which is itself a finding worth reading at a glance — not noise to scroll past.
          case "$rc" in
            127) status="absent (command not installed)" ;;
            4)   status="absent (no such systemd unit)" ;;
            1|2) status="absent (no such file or directory)" ;;
            *)   status="FAILED (rc=${rc})" ;;
          esac
          failed=$((failed + 1))
        elif [[ "$lines" -eq 0 ]]; then
          status="empty"; empty=$((empty + 1))
        else
          status="ok (${lines} lines)"; ok=$((ok + 1))
          [[ $REDACT -eq 1 ]] && redact_file "$outfile"
        fi
        printf '  %-12s %-28s %s\n' "$current_group" "$current_name" "$status" >> "$summary"
        echo "  ${host}/${current_group}/${current_name}: ${status}" >> "$MANIFEST"
      fi
      outfile=""
      continue
    fi
    [[ "$line" == "===SMC-CAPTURE-END===" ]] && continue
    [[ -n "$outfile" ]] && printf '%s\n' "$line" >> "$outfile"
  done < "$raw"

  rm -f "$raw"
  printf '  captured: %d ok, %d empty, %d absent-or-failed\n' "$ok" "$empty" "$failed"
  echo "  ${host}: TOTAL ${ok} ok, ${empty} empty, ${failed} absent-or-failed" >> "$MANIFEST"
done

echo ""
echo "Evidence written to: ${OUTDIR}"
echo "Manifest:            ${MANIFEST}"
[[ $REDACT -eq 1 ]] || echo "WARNING: --no-redact was used. This directory contains plaintext credentials."

# --------------------------------------------------------------------------------------------------------------------------------------------------
# RPI NOTES — what the pi captures are for, and what is deliberately NOT here
#
# Implemented and verified against marta-marta-smc01 (Pi 4B Rev 1.5, aarch64, Ubuntu 22.04) on 2026-08-25.
#
#   life_time / pre_eol_info are NOT captured. They are eMMC attributes; an SD-booted Pi 4 does not expose them (checked: /sys/block/mmcblk0/device/
#   holds cid, csd, ssr, fwrev, manfid, oemid, serial, date and friends, and no wear-level pair). Anything claiming to read SD wear-levelling from those
#   two files on this hardware is wrong. cid/csd/ssr are captured instead.
#
#   flash-kernel is never invoked, only its config read — it writes to the boot partition. Same reasoning excludes rpi-eeprom-update -a, which stages a
#   firmware write; the bare command used here only reports.
#
#   piboot captures return "no piboot A/B layout" on 22.04, which is correct and worth recording: Canonical ships piboot from 25.10, so this is the
#   before-picture for the 26.04 migration rather than a fault.
#
#   copymods is captured because its meaning INVERTS across the migration — a fault condition on 22.04 that smc_update_kernel tears down, and the
#   platform default under dracut on 26.04.
# --------------------------------------------------------------------------------------------------------------------------------------------------
