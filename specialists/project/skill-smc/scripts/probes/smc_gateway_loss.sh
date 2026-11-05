#!/usr/bin/env bash
# Is the site link (satellite, Sky Muster Plus on rct) losing packets, and is it one site or many? Read-only survey of named SMCs over Teleport.
#
# usage: smc_gateway_loss.sh [-c <pings>] [-t <sec>] [-s] <smc> [<smc> ...]
#        smc_gateway_loss.sh [options] - < names.txt          # one SMC per line
#   e.g. smc_gateway_loss.sh goojarr-goonyool gurrbalgun garimba
# Options: -c pings to the gateway (default 20, 0.3 s apart), -t seconds per SMC for the whole probe (default 90; give -s 240),
#          -s also measure download speed: a 5 MB Cloudflare file and bitbucket.org over HTTPS (KB/s, to /dev/null), slow link vs slow destination.
# A name without "-smcNN" or "-rctNN" gets "-smc01". Per SMC, from the box: its default gateway (the first hop: the satellite NTD/router side),
# packet loss and average RTT to it, and the WAN's rx/tx over 5 s. Loss already at the first hop with the WAN nearly idle is the site link,
# not Teleport, the SMC or load (skill-smc references/06_failure-modes.md). The last lines group SMCs by gateway /24, so loss that follows a
# shared upstream shows as one bad group while a single bad site stands alone.
# All SMCs are probed at once (one tsh ssh each); runtime about 15 s plus Teleport setup, bounded by -t. Nothing is changed on any box.
# Exit: 0 all answered; 1 some did not answer (listed NO ANSWER: check the backdoor before calling one down); 2 bad usage.
# Origin: goojarr-goonyool and gurrbalgun clones at 3-4 KB/s, 23-27 % loss at the first hop, 2026-11-05 (references/19_smc-change-role.md).
set -u

pings=20
per_smc=90
speed=""

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
  # Args: $1 the name as typed.
  # Returns: 0; prints the inventory name.
  case "$1" in
    *-smc[0-9][0-9] | *-rct[0-9][0-9]) printf '%s\n' "$1" ;;
    *) printf '%s-smc01\n' "$1" ;;
  esac
}

while getopts 'c:t:sh' opt; do
  case "$opt" in
    c) pings=$OPTARG ;;
    t) per_smc=$OPTARG ;;
    s) speed=speed ;;
    h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
case "$pings$per_smc" in '' | *[!0-9]*) echo "-c and -t take whole numbers" >&2; exit 2 ;; esac

names=()
if [ "${1:-}" = "-" ]; then
  while read -r line; do [ -n "$line" ] && names+=("$(host_name "$line")"); done
else
  for n in "$@"; do names+=("$(host_name "$n")"); done
fi
[ ${#names[@]} -gt 0 ] || { echo "name at least one SMC" >&2; usage >&2; exit 2; }

# The probe that runs on each SMC, sent on stdin so its variables expand there, not here.
remote="$(dirname "$0")/smc_gateway_loss_remote.sh"
[ -r "$remote" ] || { echo "missing $remote" >&2; exit 2; }
tmp=$(mktemp -d) || exit 2
trap 'rm -f "$tmp"/*.out "$tmp"/table.txt; rmdir "$tmp"' EXIT
for smc in "${names[@]}"; do
  ( timeout "$per_smc" tsh ssh "root@$smc" "sh -s $pings $speed" <"$remote" 2>/dev/null | grep '^gw=' | tail -n 1 >"$tmp/$smc.out" ) &
done
wait

rc=0
printf '%-26s %-16s %7s %8s %9s %9s %8s %8s\n' SMC GATEWAY LOSS% RTT_MS WAN_RX_KB WAN_TX_KB DL_KB/s BB_KB/s >"$tmp/table.txt"
for smc in "${names[@]}"; do
  line=$(cat "$tmp/$smc.out" 2>/dev/null)
  if [ -z "$line" ]; then
    printf '%-26s NO ANSWER (check the backdoor: backdoor-watch.sh)\n' "$smc" >>"$tmp/table.txt"
    rc=1
    continue
  fi
  printf '%s\n' "$line" | tr ' ' '\n' \
    | awk -F= -v smc="$smc" '{v[$1]=$2} END {printf "%-26s %-16s %7s %8s %9s %9s %8s %8s\n", smc, v["gw"], v["loss"], v["rtt"], v["rx"], v["tx"], (v["dl"] == "" ? "-" : v["dl"]), (v["bb"] == "" ? "-" : v["bb"])}' >>"$tmp/table.txt"
done
cat "$tmp/table.txt"
echo
echo "by gateway /24 (loss that follows a shared upstream shows as one bad group):"
awk 'NR > 1 && $2 ~ /^[0-9]+\./ {split($2, o, "."); net=o[1] "." o[2] "." o[3] ".0/24"; n[net]++; s[net] += ($3 == "?" ? 0 : $3); l[net] = l[net] " " $1 "(" $3 "%)"}
     END {for (k in n) printf "  %-18s %2d SMC  avg loss %5.1f %%  %s\n", k, n[k], s[k] / n[k], l[k]}' "$tmp/table.txt" | sort -k5 -rn
exit "$rc"
