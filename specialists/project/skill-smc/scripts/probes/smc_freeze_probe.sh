#!/usr/bin/env bash
# Read-only probe of what turns a frozen SMC (Pi or x86) into a reboot: the hardware watchdog, systemd's use of it, and the kernel's panic settings, over Teleport.
#
# usage: smc_freeze_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> [<node> ...]
#   e.g. smc_freeze_probe.sh --proxy teleport.apn.au alpurrurulam-smc01 akwalirrumanja-smc01
#
# Prints one `== <node> <kernel> <board> bios=<version>` block per box: the watchdog devices and each one's driver identity, state and timeout; the
# watchdog modules loaded and any blacklist lines naming them; systemd's RuntimeWatchdogUSec and RebootWatchdogUSec; kernel.panic, softlockup_panic,
# hardlockup_panic, hung_task_panic, panic_on_oops and nmi_watchdog; the watchdog core's open_timeout; the kernel build options behind them; on a Pi
# the model, the panic and watchdog words on the command line, overlayroot and any watchdog or tstik units. Only reads; writes nothing on the box or
# locally. The proxy is required and never guessed. Each tsh call is cut at the deadline (default 120 s): TERM, then KILL.
# Exit status: 0 when every node answered, 1 when any did not, 2 on bad usage.
# Origin: smc-resiliency 2026-11-19 (B19-03, B19-04): two Pis and three x86 SMCs read, none with a watchdog fed and all with kernel.panic=0.
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
deadline=120
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --deadline) deadline="${2:-}"; shift 2 ;;
    -h | --help) usage; exit 0 ;;
    --*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ -n "$proxy" ] && [ $# -gt 0 ] || { usage >&2; exit 2; }
case "$deadline" in '' | *[!0-9]*) echo "--deadline must be a whole number" >&2; exit 2 ;; esac

# The commands run on the box, as one script on stdin of a login shell (no quoting through tsh).
read -r -d '' REMOTE <<'EOS'
echo "== $(hostname) $(uname -r) $(cat /sys/class/dmi/id/board_name 2>/dev/null) bios=$(cat /sys/class/dmi/id/bios_version 2>/dev/null)"
echo "dev: $(ls /dev/watchdog* 2>/dev/null | tr '\n' ' ')"
for w in /sys/class/watchdog/watchdog*; do [ -d "$w" ] && echo "$w id=$(cat $w/identity 2>/dev/null) state=$(cat $w/state 2>/dev/null) timeout=$(cat $w/timeout 2>/dev/null)"; done
echo "modules: $(lsmod | awk '/wdt|tco|watchdog/{print $1}' | tr '\n' ' ')"
echo "blacklist: $(grep -rhiE 'iTCO|it87_wdt|bcm2835_wdt' /etc/modprobe.d/ /lib/modprobe.d/ 2>/dev/null | grep -i black | tr '\n' ';')"
echo "systemd: $(systemctl show -p RuntimeWatchdogUSec -p RebootWatchdogUSec 2>/dev/null | tr '\n' ' ')"
echo "sysctl: $(sysctl -e kernel.panic kernel.softlockup_panic kernel.hardlockup_panic kernel.hung_task_panic kernel.panic_on_oops kernel.nmi_watchdog 2>/dev/null | tr '\n' ' ')"
echo "open_timeout: $(cat /sys/module/watchdog/parameters/open_timeout 2>/dev/null)"
echo "config: $(grep -E 'CONFIG_WATCHDOG_OPEN_TIMEOUT|CONFIG_ITCO_WDT=|CONFIG_IT87_WDT=|CONFIG_BCM2835_WDT=|CONFIG_HARDLOCKUP_DETECTOR=' /boot/config-$(uname -r) 2>/dev/null | tr '\n' ' ')"
if [ -r /proc/device-tree/model ]; then
  echo "model: $(tr -d '\0' </proc/device-tree/model)"
  echo "cmdline: $(tr ' ' '\n' </proc/cmdline | grep -E '^(panic|watchdog|bcm2835_wdt)' | tr '\n' ' ')"
  echo "overlayroot: $(grep -E '^overlayroot=' /etc/overlayroot.conf 2>/dev/null)"
  echo "units: $(systemctl list-units --no-pager --no-legend 2>/dev/null | awk '/tstik|watchdog/{print $1}' | tr '\n' ' ')"
fi
EOS

one() {
  # Run the remote read on one node through tsh, cut at the deadline.
  # Args: $1 node. Returns: 0 answered, 1 not (an `== <node> unreachable` line says so).
  local out rc
  out=$(printf '%s\n' "$REMOTE" | perl -e '$d=shift; defined(my $p=fork) or die "fork: $!"; if(!$p){exec @ARGV; exit 127} $SIG{ALRM}=sub{kill "TERM",$p; for(1..5){exit 124 if waitpid($p,1)>0; sleep 1} kill "KILL",$p; waitpid($p,0); exit 124}; alarm $d; waitpid($p,0); exit($? & 127 ? 128+($? & 127) : $?>>8)' "$deadline" \
    tsh ssh --proxy="$proxy" "root@$1" 'bash -s' 2>&1)
  rc=$?
  if [ $rc -eq 0 ] && printf '%s' "$out" | grep -q '^== '; then
    printf '%s\n' "$out" | sed -n '/^== /,$p'
    return 0
  fi
  echo "== $1 unreachable rc=$rc $(printf '%s\n' "$out" | tr -d '\033' | grep -m1 -iE 'error|offline|denied|refused|timed out' | cut -c1-120)"
  return 1
}

fail=0
for node in "$@"; do one "$node" || fail=1; done
exit $fail
