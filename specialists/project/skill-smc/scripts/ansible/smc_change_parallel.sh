#!/usr/bin/env bash
# Run one ansible-playbook per SMC, all at once, so a slow or stalled SMC never holds the others (each SMC has its own controller run).
#
# usage: smc_change_parallel.sh [options] <smc> [<smc> ...] [-- <extra ansible-playbook args>]
#   e.g. smc_change_parallel.sh gumbarnun gurrbalgun banana-well                     # plan only: which SMCs answer, the commands
#        smc_change_parallel.sh --apply gumbarnun gurrbalgun banana-well             # start them
#        smc_change_parallel.sh --apply -p smc_change.yml map -- -e smc_change=rct-avr-smsc -e smc_change_mode=apply
# Options:
#   --apply      start the runs (without it: print the plan and start nothing)
#   -i <inv>     inventory, relative to the repo (default inventories/rct/prod)
#   -p <book>    playbook, relative to the repo (default smc_change_multiple.yml)
#   -r <repo>    ansible-wifi checkout (default $ANSIBLE_WIFI or /Volumes/Data/_ansible/ansible-wifi)
#   -o <dir>     log folder (default <local-knowledge>/evidence/smc-change-parallel-<YYYYMMDD_HHMM>)
#   -t <sec>     Teleport check per SMC, seconds (default 30); 0 skips the check
# A name without "-smcNN" or "-rctNN" gets "-smc01" (gumbarnun -> gumbarnun-smc01). Each run is `ansible-playbook -f 1 -l <smc>`, its output in
# <dir>/<smc>.log and its PID in <dir>/pids.txt. CHANGES SMCs with --apply: whatever the playbook does (smc_change apply by default in
# smc_change_multiple.yml). Refuses an SMC that another ansible-playbook on this machine is already running against (one controller per SMC: two
# probes at once collided on the AVR serial port, alkngarrija-smc01, 2026-10-26), and an SMC Teleport does not answer for (skipped, listed).
# Each run is started under nohup, so closing the terminal does not stop it (a hang-up would cut an SMC off mid-change). Stop one run with
# `kill <pid>` from pids.txt; Ctrl-C stops all of them. smc_change journals stay resumable either way.
# Exit: 0 every started run exited 0; 1 a run failed or an SMC was skipped; 2 bad usage; 3 nothing to start.
# Origin: rct iridium resumes, 2026-11-05: under strategy linear one stalled clone held a serial batch 35 min (references/19_smc-change-role.md).
set -u

repo=${ANSIBLE_WIFI:-/Volumes/Data/_ansible/ansible-wifi}
inventory=inventories/rct/prod
playbook=smc_change_multiple.yml
logdir=""
check_seconds=30
apply=0
smcs=()
extra=()

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,/^# Origin:/p' "$0" | sed 's/^# \{0,1\}//'
}

host_name() {
  # The inventory name for an SMC given short or in full.
  #
  # Args: $1 the name as typed (gumbarnun, gumbarnun-smc01, warehouse-rct01).
  # Returns: 0; prints the inventory name.
  case "$1" in
    *-smc[0-9][0-9] | *-rct[0-9][0-9]) printf '%s\n' "$1" ;;
    *) printf '%s-smc01\n' "$1" ;;
  esac
}

already_running() {
  # Whether another ansible-playbook on this machine targets the SMC (its name in the command line as a whole word).
  #
  # Args: $1 the inventory name.
  # Returns: 0 when one runs (prints its PID and command), 1 when none does.
  # Anchored: the command line starts with ansible-playbook, or with its interpreter and then ansible-playbook (Homebrew's Python).
  pgrep -lf '^([^ ]+ )?([^ ]+/)?ansible-playbook ' | grep -E "(^|[ ,=])$1([ ,]|$)"
}

answers() {
  # Whether Teleport reaches the SMC within check_seconds.
  #
  # Args: $1 the inventory name.
  # Returns: 0 when `tsh ssh root@<smc> true` succeeds in time (or the check is off), 1 otherwise.
  [ "$check_seconds" -eq 0 ] && return 0
  timeout "$check_seconds" tsh ssh "root@$1" true >/dev/null 2>&1
}

while [ $# -gt 0 ]; do
  case "$1" in
    --apply) apply=1 ;;
    -i) inventory=${2:?-i needs an inventory}; shift ;;
    -p) playbook=${2:?-p needs a playbook}; shift ;;
    -r) repo=${2:?-r needs a folder}; shift ;;
    -o) logdir=${2:?-o needs a folder}; shift ;;
    -t) check_seconds=${2:?-t needs seconds}; shift ;;
    -h | --help) usage; exit 0 ;;
    --) shift; extra=("$@"); break ;;
    -*) echo "unknown option $1" >&2; usage >&2; exit 2 ;;
    *) smcs+=("$(host_name "$1")") ;;
  esac
  shift
done

[ ${#smcs[@]} -gt 0 ] || { echo "name at least one SMC" >&2; usage >&2; exit 2; }
case "$check_seconds" in '' | *[!0-9]*) echo "-t needs whole seconds" >&2; exit 2 ;; esac
[ -f "$repo/$playbook" ] || { echo "no playbook $repo/$playbook" >&2; exit 2; }
[ -e "$repo/$inventory" ] || { echo "no inventory $repo/$inventory" >&2; exit 2; }
dupes=$(printf '%s\n' "${smcs[@]}" | sort | uniq -d)
[ -z "$dupes" ] || { echo "named twice: $dupes" >&2; exit 2; }
[ -n "$logdir" ] || logdir=/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/evidence/smc-change-parallel-$(date '+%Y%m%d_%H%M')

# Decide each SMC before starting any, so the plan and the run see the same list.
start=()
skipped=()
for smc in "${smcs[@]}"; do
  if running=$(already_running "$smc"); then
    skipped+=("$smc: another ansible-playbook targets it ($(printf '%s' "$running" | head -n 1 | cut -c1-80))")
  elif ! answers "$smc"; then
    skipped+=("$smc: no answer over Teleport in ${check_seconds}s (check its backdoor before calling it down)")
  else
    start+=("$smc")
  fi
done

echo "PLAYBOOK $playbook  INVENTORY $inventory  LOGS $logdir"
for smc in "${start[@]+"${start[@]}"}"; do
  echo "RUN      ansible-playbook -i $inventory $playbook -f 1 -l $smc ${extra[*]+"${extra[*]}"}"
done
for line in "${skipped[@]+"${skipped[@]}"}"; do echo "SKIP     $line"; done
[ ${#start[@]} -gt 0 ] || { echo "nothing to start"; exit 3; }
if [ "$apply" -ne 1 ]; then
  echo "plan only: add --apply to start ${#start[@]} run(s)"
  exit 0
fi

mkdir -p "$logdir" || exit 2
cd "$repo" || exit 2
: >"$logdir/pids.txt"
pids=()
for smc in "${start[@]}"; do
  nohup ansible-playbook -i "$inventory" "$playbook" -f 1 -l "$smc" ${extra[@]+"${extra[@]}"} >"$logdir/$smc.log" 2>&1 </dev/null &
  pids+=("$!")
  printf '%s %s\n' "$!" "$smc" >>"$logdir/pids.txt"
  echo "STARTED  $smc pid $! log $logdir/$smc.log"
done
echo "watch:   for f in $logdir/*.log; do echo \"\$(basename \"\$f\"): \$(grep 'TASK \\[' \"\$f\" | tail -1)\"; done"
echo "stop one: kill <pid> (pids.txt); Ctrl-C stops all"

rc=0
for i in "${!pids[@]}"; do
  smc=${start[$i]}
  if wait "${pids[$i]}"; then status=0; else status=$?; rc=1; fi
  recap=$(grep -A20 'PLAY RECAP' "$logdir/$smc.log" | grep -E "^$smc " | tail -n 1 | tr -s ' ')
  echo "DONE     $smc exit $status  ${recap:-no recap (stopped early, see the log)}"
done
[ ${#skipped[@]} -eq 0 ] || rc=1
exit "$rc"
