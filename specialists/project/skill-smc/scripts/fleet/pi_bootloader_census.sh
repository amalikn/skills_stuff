#!/usr/bin/env bash
# Read-only census of Raspberry Pi SMC bootloader (EEPROM) versions over Teleport: one short read per box, several boxes at once.
#
# usage: pi_bootloader_census.sh [--parallel <n>] [--deadline <seconds>] < sample.txt
#   stdin: `<flavour> <proxy> <host>` lines, as skill-smc scripts/fleet/sample_fleet.py prints them (--per-flavour 1000 lists every box)
#   e.g. sample_fleet.py --inventories <inv> --flavours rct,wh,nbn_wh --per-flavour 1000 | pi_bootloader_census.sh --parallel 8
#
# Prints one line per box: `<flavour> <host> bootloader=<YYYY-MM-DD> model=<board> throttled=<flags>`, or `<flavour> <host> unreachable rc=<n>`.
# The proxy is taken from each input line, never guessed. Only reads (vcgencmd, the device tree); writes nothing on the box or locally.
# Each tsh call is cut at the deadline (default 120 s: satellite logins vary): TERM, then KILL (tsh survives SIGALRM, so `alarm; exec` is not enough; 2026-11-10).
# Exit status: 0 when every box answered, 1 when any did not, 2 on bad usage.
# Origin: smc-resiliency fleet survey 2026-11-10 (four of 20 rct Pis on bootloader 2022-04-26; operator: census first).
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
}

parallel=8
deadline=120
while [ $# -gt 0 ]; do
  case "$1" in
    --parallel) parallel="${2:-}"; shift 2 ;;
    --deadline) deadline="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
case "$parallel$deadline" in ''|*[!0-9]*) echo "--parallel and --deadline must be whole numbers" >&2; exit 2 ;; esac

one() {
  # Read one box's bootloader version, board and throttle flags.
  # Args: $1 flavour, $2 proxy, $3 host; $4 deadline in seconds. Returns: 0 answered, 1 not (its line says why).
  local out rc
  out=$(perl -e '$d=shift; defined(my $p=fork) or die "fork: $!"; if(!$p){exec @ARGV; exit 127} $SIG{ALRM}=sub{kill "TERM",$p; for(1..5){exit 124 if waitpid($p,1)>0; sleep 1} kill "KILL",$p; waitpid($p,0); exit 124}; alarm $d; waitpid($p,0); exit($? & 127 ? 128+($? & 127) : $?>>8)' "$4" \
    tsh ssh --proxy="$2" "root@$3" 'echo bootloader=$(vcgencmd bootloader_version 2>/dev/null | head -1 | cut -d" " -f1 | tr / -) model=$(tr -d "\0" < /proc/device-tree/model | tr " " _) throttled=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2)' </dev/null 2>&1)
  rc=$?
  if [ $rc -eq 0 ] && printf '%s' "$out" | grep -q '^bootloader='; then
    echo "$1 $3 $(printf '%s\n' "$out" | grep '^bootloader=')"
    return 0
  fi
  echo "$1 $3 unreachable rc=$rc $(printf '%s\n' "$out" | tr -d '\033' | grep -m1 -iE 'error|offline|denied|refused|timed out' | cut -c1-120)"
  return 1
}
export -f one

grep -vE '^\s*(#|$)' | xargs -P "$parallel" -L 1 bash -c 'one "$0" "$1" "$2" '"$deadline"
