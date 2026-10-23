#!/usr/bin/env bash
# Read-only identity probe for Raspberry Pi SMC boxes (rct, wh, nbn_wh flavours), over Teleport.
#
# usage: pi_identity_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> [<node> ...]
#   e.g. pi_identity_probe.sh --proxy teleport.apn.au 20-mile-smc01 adjamarragu-smc01
#
# The proxy is required and never guessed: a node name can exist on both clusters as different boxes (AGENTS.md, "Always name
# the proxy"). Prints one `== <node>` block of key=value lines per box: device-tree model and serial-number, cpuinfo
# Serial/Revision/Model, dmidecode (empty on a Pi, which has no DMI), os-release, arch, kernel, each physical NIC with MAC,
# driver and speed, bridges, VLAN interfaces and memory, then the swap-check lines: hostname vs the hostname the box booted with,
# root filesystem and overlayroot setting, boot time, journal boot count and when the previous journalled boot ended. After a site
# visit, boot_hostname=generic-wh01-* or root_fs on ext4 where RISE runs means a spare disk or unit went in (kupungarri, 2026-10-09).
# hosts_name is the 127.0.1.1 name in /etc/hosts: a box renamed from a generic image can keep the image's name there, and sudo then warns
# "unable to resolve host" (php-rct-smc01, 2026-10-23; fix with smc_change spec etc-hosts-hostname).
# Then the EEPROM lines (2026-10-22): bootloader version, the bootloader config it runs (vcgencmd bootloader_config), rpi-eeprom-update's
# report (bare command: reports, never stages), autoboot.txt presence and the hardware watchdog's identity.
# Only reads; writes nothing on the box or locally. Every tsh call has a deadline (default 90 s, `--deadline`).
# Exit status: 0 when every node answered, 1 when any node was unreachable or returned no probe output, 2 on bad usage.
# Origin: unified-network-controller session 2026-10-08 (Pi identity, references/07_hardware-overlay.md).
set -u

usage() {
  # Print the header comment as help.
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
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
echo model=$(tr -d "\0" </proc/device-tree/model 2>/dev/null)
echo dt_serial=$(tr -d "\0" </proc/device-tree/serial-number 2>/dev/null)
grep -E "^(Serial|Revision|Model)" /proc/cpuinfo | sed "s/\t*: /=/"
echo dmi=$(dmidecode -s system-product-name 2>&1 | head -1)
. /etc/os-release; echo os=$ID $VERSION; echo arch=$(uname -m) kernel=$(uname -r)
for i in $(ls /sys/class/net); do [ -e /sys/class/net/$i/device ] && echo nic=$i,$(cat /sys/class/net/$i/address),$(basename $(readlink /sys/class/net/$i/device/driver) 2>/dev/null),$(cat /sys/class/net/$i/speed 2>/dev/null); done
echo bridges=$(ip -br link show type bridge | cut -d" " -f1 | tr "\n" " ")
echo vlans=$(ip -br link show type vlan | cut -d" " -f1 | tr "\n" " ")
echo mem=$(free -g | awk "/Mem/{print \$2}")G
echo hostname=$(hostname) boot_hostname=$(journalctl -b 0 --no-pager -o cat 2>/dev/null | sed -n "s/^Hostname set to <\(.*\)>\.$/\1/p" | head -1) hosts_name=$(awk "/^127\.0\.1\.1/{print \$2}" /etc/hosts)
echo root_fs=$(findmnt -n -o SOURCE,FSTYPE / | tr -s " " ,) overlayroot_conf=$(grep -h "^overlayroot=" /etc/overlayroot.conf /media/root-ro/etc/overlayroot.conf 2>/dev/null | tail -1)
echo boot_now=$(uptime -s) journal_boots=$(journalctl --list-boots --no-pager 2>/dev/null | grep -cE "^ *-?[0-9]+ ") prev_boot_end=$(journalctl --list-boots --no-pager 2>/dev/null | tail -2 | head -1 | sed "s/.*—//")
echo eeprom_version=$(vcgencmd bootloader_version 2>/dev/null | tr "\n" " ")
echo eeprom_config=$(vcgencmd bootloader_config 2>/dev/null | grep -vE "^\[|^$" | tr "\n" ";")
echo eeprom_update=$(rpi-eeprom-update 2>&1 | grep -E "BOOTLOADER|CURRENT|LATEST|RELEASE|VL805" | tr -s " " | tr "\n" ";")
echo autoboot_txt=$([ -e /boot/firmware/autoboot.txt ] && echo present || echo absent) watchdog=$(cat /sys/class/watchdog/watchdog0/identity 2>/dev/null)
echo probe_end=ok
'

probe() {
  # Run the fixed read-only command set on one node.
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
