#!/usr/bin/env bash
# Read-only resiliency probe for x86 SMC boxes (rcp, nbn_accelerate, and any future x86 model), over Teleport.
#
# usage: x86_resiliency_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> [<node> ...]
#   e.g. x86_resiliency_probe.sh --proxy teleport.apn.au horn-island-smc01 jigalong-smc01
#
# The proxy is required and never guessed: a node name can exist on both clusters as different boxes (AGENTS.md, "Always name
# the proxy"). Prints one `== <node>` block of key=value lines per box: DMI model and BIOS, memory, each disk (size, model),
# root source and filesystem, LVM volume groups with free space, EFI boot entries and timeout, the UEFI surface the OS can see (UEFI or legacy
# mode, efivars mount mode, Secure Boot and Setup Mode, ESRT capsule entries, the capsule loader, fwupd, DMI BIOS characteristics), the hardware watchdog (device, identity,
# timeouts, which watchdog drivers ship with the kernel), the soft-lockup detector, systemd version, and the size of the
# state directories that must survive a reboot (squidguard, Asterisk, DHCP, url_capture, MySQL, ClamAV, Teleport).
# These are the inputs to smc-resiliency's x86 plan (section 3) and its per-model qualification (stage XQ).
# Only reads; writes nothing on the box or locally. Every tsh call has a deadline (default 90 s, `--deadline`).
# Exit status: 0 when every node answered, 1 when any node was unreachable or returned no probe output, 2 on bad usage.
# Origin: smc-resiliency session 2026-10-14 (x86 plan; references/07_hardware-overlay.md, smc_disk_failover mechanics).
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
deadline=90
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --proxy=*) proxy="${1#--proxy=}"; shift ;;
    --deadline) deadline="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ -n "$proxy" ] && [ $# -ge 1 ] || { usage >&2; exit 2; }
case "$deadline" in ''|*[!0-9]*) echo "--deadline must be whole seconds" >&2; exit 2 ;; esac

# Remote command set is fixed here; the script takes node names only, never commands.
REMOTE='
echo dmi_model=$(cat /sys/class/dmi/id/product_name 2>/dev/null) bios=$(cat /sys/class/dmi/id/bios_version 2>/dev/null) bios_date=$(cat /sys/class/dmi/id/bios_date 2>/dev/null)
echo mem=$(free -g | awk "/Mem/{print \$2}")G
lsblk -dn -o NAME,SIZE,MODEL,TYPE 2>/dev/null | awk "\$NF==\"disk\"{\$NF=\"\"; print \"disk=\" \$0}"
echo root=$(findmnt -n -o SOURCE,FSTYPE / | tr -s " " ,) root_use=$(df -h / | awk "NR==2{print \$5}")
vgs --noheadings -o vg_name,vg_size,vg_free 2>/dev/null | awk "{print \"vg=\" \$1 \",size=\" \$2 \",free=\" \$3}"
efibootmgr 2>/dev/null | grep -E "^(BootCurrent|BootNext|BootOrder|Timeout|Boot[0-9A-F]{4})" | sed "s/^/efi=/"
echo uefi_mode=$([ -d /sys/firmware/efi ] && echo uefi || echo legacy) efivars=$(findmnt -n -o OPTIONS /sys/firmware/efi/efivars 2>/dev/null | cut -d, -f1)
sb=/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c; echo secure_boot=$([ -r $sb ] && od -An -t u1 $sb | awk "{print \$NF}" || echo unreadable) setup_mode=$(f=/sys/firmware/efi/efivars/SetupMode-8be4df61-93ca-11d2-aa0d-00e098032b8c; [ -r $f ] && od -An -t u1 $f | awk "{print \$NF}" || echo unreadable)
echo esrt_entries=$(ls -d /sys/firmware/efi/esrt/entries/entry* 2>/dev/null | wc -l) capsule_loader=$([ -e /dev/efi_capsule_loader ] && echo yes || echo no) fwupd=$(command -v fwupdmgr >/dev/null 2>&1 && echo installed || echo absent)
for e in /sys/firmware/efi/esrt/entries/entry*; do [ -d "$e" ] && echo esrt=type=$(cat $e/fw_type),version=$(cat $e/fw_version),lowest=$(cat $e/lowest_supported_fw_version),flags=$(cat $e/capsule_flags),last=$(cat $e/last_attempt_status),class=$(cat $e/fw_class); done
dmidecode -t bios 2>/dev/null | grep -E "Vendor:|ROM Size:|BIOS is upgradeable|UEFI is supported|BIOS ROM is socketed|Firmware Revision" | sed "s/^[[:space:]]*/bios_char=/"
echo watchdog_dev=$(ls /dev/watchdog* 2>/dev/null | tr "\n" " ")
for w in /sys/class/watchdog/watchdog*; do [ -e "$w" ] && echo watchdog=$(basename $w),$(cat $w/identity 2>/dev/null),timeout=$(cat $w/timeout 2>/dev/null),max=$(cat $w/max_timeout 2>/dev/null); done
echo watchdog_drivers=$(ls /lib/modules/$(uname -r)/kernel/drivers/watchdog/ 2>/dev/null | grep -iE "itco|it87|f71808|nct|w83627|sch56" | tr "\n" " ")
echo runtime_watchdog=$(grep -hE "^RuntimeWatchdogSec" /etc/systemd/system.conf /etc/systemd/system.conf.d/*.conf 2>/dev/null | tail -1) softlockup=$(cat /proc/sys/kernel/watchdog 2>/dev/null)
echo systemd=$(systemctl --version | head -1 | cut -d" " -f2) kernel=$(uname -r)
for d in /var/lib/squidguard /var/lib/asterisk /var/lib/dhcp /url_capture /var/lib/mysql /var/lib/clamav /var/lib/teleport; do [ -d "$d" ] && echo state=$d,$(du -sh "$d" 2>/dev/null | cut -f1); done
echo probe_end=ok
'

probe() {
  # Run the fixed read-only command set on one node and print its block.
  # Args: $1 node name (Teleport node). Returns: 0 when the node completed the probe, 1 when unreachable, cut short or past the deadline.
  local node="$1" out rc
  out=$(perl -e 'alarm shift; exec @ARGV' "$deadline" tsh ssh --proxy="$proxy" "root@$node" "$REMOTE" </dev/null 2>&1)   # stdin closed: a tsh reading stdin hung a background run (2026-10-22)
  rc=$?
  echo "== $node ($proxy)"
  if [ $rc -ne 0 ] || ! printf '%s\n' "$out" | grep -q '^probe_end=ok$'; then
    printf '%s\n' "$out" | tail -3 | sed 's/^/  /'
    echo "unreachable=yes rc=$rc"
    return 1
  fi
  printf '%s\n' "$out" | grep -v '^probe_end=ok$'
}

failed=0
for node in "$@"; do
  probe "$node" || failed=1
  echo
done
exit $failed
