#!/usr/bin/env bash
# Read-only probe: will a Pi SMC boot the kernel it is meant to run? Over Teleport.
#
# usage: smc_boot_kernel_probe.sh [--parallel N] --proxy <teleport-proxy> --target <kernel> <node> [<node> ...]
#   e.g. smc_boot_kernel_probe.sh --proxy teleport.apn.au --target 5.15.0-1078-raspi myra-vale-smc01 wungu-qld-smc01
#
# Prints one `BOOTKERNEL|<node>|running=..|next_boot=..|modules=..|state=..` line per box. next_boot is the version inside
# /boot/firmware/vmlinuz, which is what the Pi boots; running can be fine while next_boot has already moved. modules lists /lib/modules.
# state: ok, or DRIFT when next_boot or running differs from the target or modules holds another kernel; smc_enable_overlay skips
# its whole job on that last case, reporting failed=0.
# Why: myra-vale-smc01, 2026-11-01. smc_qos installs linux-modules-extra-raspi, an unpinned meta-package, which pulled a newer kernel;
# the box ran the target until its next reboot (references/13_known-issues.md).
# Writes nothing on the box or locally. Does not run flash-kernel: it has no --help and takes any argument as a kernel version.
# Exit status: 0 all ok, 1 any DRIFT or unreachable node, 2 on bad usage.

set -u

# read_box: print the probe line's fields, run on the SMC.
#   Args: none (sent as the remote command). Returns: 0.
read_box='
fw=$(zcat /boot/firmware/vmlinuz 2>/dev/null | strings | grep -m1 "^Linux version" | cut -d" " -f3)
[ -n "$fw" ] || fw=$(strings /boot/firmware/vmlinuz 2>/dev/null | grep -m1 "^Linux version" | cut -d" " -f3)
echo "running=$(uname -r)|next_boot=${fw:-unknown}|modules=$(ls /lib/modules | tr "\n" ",")"
'

# probe_node: read one box and print its BOOTKERNEL line.
#   Args: $1 node name. Uses proxy and target. Returns: 0 ok, 1 DRIFT or unreachable.
probe_node() {
  local node=$1 out state=ok
  out=$(timeout 60 tsh ssh --proxy="$proxy" "root@$node" "$read_box" 2>/dev/null | grep '^running=' | head -n 1)
  if [ -z "$out" ]; then
    echo "BOOTKERNEL|$node|unreachable"
    return 1
  fi
  case "$out" in
    "running=$target|next_boot=$target|modules=$target,") ;;
    *) state=DRIFT ;;
  esac
  echo "BOOTKERNEL|$node|$out|state=$state"
  [ "$state" = ok ]
}

proxy="" target="" parallel=8
while [ $# -gt 0 ]; do
  case $1 in
    --proxy) proxy=${2:-}; shift 2 ;;
    --target) target=${2:-}; shift 2 ;;
    --parallel) parallel=${2:-8}; shift 2 ;;
    --) shift; break ;;
    -*) echo "unknown option $1" >&2; exit 2 ;;
    *) break ;;
  esac
done
if [ -z "$proxy" ] || [ -z "$target" ] || [ $# -eq 0 ]; then
  echo "usage: smc_boot_kernel_probe.sh [--parallel N] --proxy <teleport-proxy> --target <kernel> <node> [<node> ...]" >&2
  exit 2
fi

rc=0
active=0
for node in "$@"; do
  probe_node "$node" &
  active=$((active + 1))
  if [ "$active" -ge "$parallel" ]; then
    wait -n || rc=1
    active=$((active - 1))
  fi
done
while [ "$active" -gt 0 ]; do
  wait -n || rc=1
  active=$((active - 1))
done
exit "$rc"
