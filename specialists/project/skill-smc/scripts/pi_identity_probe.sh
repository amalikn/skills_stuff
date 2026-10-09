#!/usr/bin/env bash
# Read-only identity probe for Raspberry Pi SMC boxes (rct, wh, nbn_wh flavours), over Teleport.
#
# usage: pi_identity_probe.sh --proxy <teleport-proxy> <node> [<node> ...]
#   e.g. pi_identity_probe.sh --proxy teleport.apn.au 20-mile-smc01 adjamarragu-smc01
#
# The proxy is required and never guessed: a node name can exist on both clusters as different boxes (AGENTS.md, "Always name
# the proxy"). Prints one `== <node>` block of key=value lines per box: device-tree model and serial-number, cpuinfo
# Serial/Revision/Model, dmidecode (empty on a Pi, which has no DMI), os-release, arch, kernel, each physical NIC with MAC,
# driver and speed, bridges, VLAN interfaces and memory, then the swap-check lines: hostname vs the hostname the box booted with,
# root filesystem and overlayroot setting, boot time, journal boot count and when the previous journalled boot ended. After a site
# visit, boot_hostname=generic-wh01-* or root_fs on ext4 where RISE runs means a spare disk or unit went in (kupungarri, 2026-10-09).
# Only reads; writes nothing on the box or locally.
# Exit status: 0 when every node answered, 1 when any node was unreachable or returned no probe output, 2 on bad usage.
# Origin: unified-network-controller session 2026-10-08 (Pi identity, references/07_hardware-overlay.md).
set -u

usage() {
  # Print the header comment as help.
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --proxy=*) proxy="${1#--proxy=}"; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ -n "$proxy" ] && [ $# -ge 1 ] || { usage >&2; exit 2; }

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
echo hostname=$(hostname) boot_hostname=$(journalctl -b 0 --no-pager -o cat 2>/dev/null | sed -n "s/^Hostname set to <\(.*\)>\.$/\1/p" | head -1)
echo root_fs=$(findmnt -n -o SOURCE,FSTYPE / | tr -s " " ,) overlayroot_conf=$(grep -h "^overlayroot=" /etc/overlayroot.conf /media/root-ro/etc/overlayroot.conf 2>/dev/null | tail -1)
echo boot_now=$(uptime -s) journal_boots=$(journalctl --list-boots --no-pager 2>/dev/null | grep -cE "^ *-?[0-9]+ ") prev_boot_end=$(journalctl --list-boots --no-pager 2>/dev/null | tail -2 | head -1 | sed "s/.*—//")
echo probe_end=ok
'

probe() {
  # Run the fixed read-only command set on one node; return non-zero when the node did not complete it.
  local node="$1" out rc
  out=$(tsh ssh --proxy="$proxy" "root@$node" "$REMOTE" 2>&1)
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
