#!/usr/bin/env bash
# Read-only resiliency probe for Raspberry Pi SMC boxes (rct, wh, nbn_wh), over Teleport: the Pi sibling of x86_resiliency_probe.sh.
#
# usage: pi_resiliency_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> [<node> ...]
#   e.g. pi_resiliency_probe.sh --proxy teleport.apn.au 20-mile-smc01 areyonga-smc01
#
# The proxy is required and never guessed: a node name can exist on both clusters as different boxes (AGENTS.md, "Always name the proxy").
# Prints one `== <node>` block of key=value lines per box: board model and RAM, OS release, kernel and RAUC, the card (name, manufacturer and OEM
# IDs, manufacture date, size), partition table and layout, root mount (overlayroot or not), space used per mount, the bootloader version and
# EEPROM config, autoboot.txt, the kernel command line, the card's I/O counters since boot with uptime (a write rate; SD cards report no
# SMART wear), throttling and undervoltage flags, and for the root filesystem's lower ext4 the data held above 8, 16, 25 and 35 GiB (the
# block moves a shrink to that size needs, read from dumpe2fs group free counts).
# These are the inputs to smc-resiliency's Pi design, the remote-conversion study and the wear baseline.
# Only reads; writes nothing on the box or locally. Every tsh call has a deadline (default 120 s, `--deadline`): satellite links are slow.
# Exit status: 0 when every node answered, 1 when any node was unreachable or returned no probe output, 2 on bad usage.
# Origin: smc-resiliency session 2026-11-10 (fleet survey of 20 boxes per flavour; the six-Pi survey of the same day ran these reads by hand).
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
deadline=120
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
echo model=$(tr -d "\0" < /proc/device-tree/model 2>/dev/null) mem_mb=$(free -m | awk "/Mem/{print \$2}")
. /etc/os-release 2>/dev/null; echo os="$PRETTY_NAME" codename=$VERSION_CODENAME kernel=$(uname -r) rauc=$(rauc --version 2>/dev/null | cut -d" " -f2)
c=/sys/block/mmcblk0/device; echo card_name=$(cat $c/name 2>/dev/null) manfid=$(cat $c/manfid 2>/dev/null) oemid=$(cat $c/oemid 2>/dev/null) card_date=$(cat $c/date 2>/dev/null) size_bytes=$(lsblk -bdn -o SIZE /dev/mmcblk0 2>/dev/null)
echo pttype=$(lsblk -dn -o PTTYPE /dev/mmcblk0 2>/dev/null)
lsblk -n -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT /dev/mmcblk0 2>/dev/null | sed "s/^/part=/"
echo root_mount=$(findmnt -n -o SOURCE,FSTYPE / | tr -s " " ,)
df -BM --output=target,size,used,avail / /boot/firmware /media/root-ro 2>/dev/null | awk "NR>1{print \"df=\" \$1 \",size=\" \$2 \",used=\" \$3 \",avail=\" \$4}"
echo bootloader=$(vcgencmd bootloader_version 2>/dev/null | head -1 | cut -d" " -f1 | tr / -)
vcgencmd bootloader_config 2>/dev/null | grep -E "^[A-Z_]+=" | sed "s/^/eeprom=/"
echo autoboot=$([ -e /boot/firmware/autoboot.txt ] && echo present || echo absent)
echo cmdline_root=$(tr " " "\n" < /proc/cmdline | grep -E "^(root|rootfstype|overlayroot|panic|console)=" | tr "\n" " ")
echo throttled=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2)
echo uptime_s=$(cut -d. -f1 /proc/uptime)
echo io=mmcblk0,sectors_written=$(awk "{print \$7}" /sys/block/mmcblk0/stat),sectors_read=$(awk "{print \$3}" /sys/block/mmcblk0/stat)
dev=$(findmnt -n -o SOURCE /media/root-ro 2>/dev/null || findmnt -n -o SOURCE /)
case "$dev" in /dev/*) dumpe2fs "$dev" 2>/dev/null | awk -v dev="$dev" "
  /^Block size:/ {bs=\$3}
  /^Blocks per group:/ {bpg=\$4}
  /^Group [0-9]+:/ {g=\$2; sub(\":\",\"\",g); split(\$4,r,\"-\"); start=r[1]+0; sub(\"\\\\(\",\"\",start); lo[g]=start}
  / free blocks, / {n=split(\$0,a,\" \"); for(i=1;i<=n;i++) if(a[i]==\"free\"&&a[i+1]==\"blocks,\") {f=a[i-1]; sub(\",\",\"\",f); free[g]=f+0}}
  END {gib=1073741824; total=0; for (k in lo) {u=bpg-free[k]; if(u<0)u=0; total+=u}
       printf \"shrink=dev=%s,bs=%d,used_gib=%.2f\", dev, bs, total*bs/gib
       split(\"8 16 25 35\",t,\" \"); for(j=1;j<=4;j++){s=0; for (k in lo) if (lo[k]*bs>=t[j]*gib) {u=bpg-free[k]; if(u<0)u=0; s+=u}; printf \",above_%dG=%.2f\", t[j], s*bs/gib}
       print \"\"}" ;; esac
echo probe_end=ok
'

probe() {
  # Run the fixed read-only command set on one node and print its block.
  # Args: $1 node name (Teleport node). Returns: 0 when the node completed the probe, 1 when unreachable, cut short or past the deadline.
  local node="$1" out rc
  out=$(perl -e '$d=shift; defined(my $p=fork) or die "fork: $!"; if(!$p){exec @ARGV; exit 127} $SIG{ALRM}=sub{kill "TERM",$p; for(1..5){exit 124 if waitpid($p,1)>0; sleep 1} kill "KILL",$p; waitpid($p,0); exit 124}; alarm $d; waitpid($p,0); exit($? & 127 ? 128+($? & 127) : $?>>8)' "$deadline" tsh ssh --proxy="$proxy" "root@$node" "$REMOTE" </dev/null 2>&1)   # stdin closed: a tsh reading stdin hung a background run (2026-10-22)
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
