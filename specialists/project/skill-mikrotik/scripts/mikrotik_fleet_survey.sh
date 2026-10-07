#!/usr/bin/env bash
# Read-only survey of the site MikroTiks behind each SMC: identity, model, RouterOS version, uptime, supply voltage, temperature,
# per-port link-downs and the interface/system log. One CSV row per device plus a raw capture folder per site.
#
# usage: mikrotik_fleet_survey.sh <outdir> [smc-host ...]
#   With no hosts, takes every Teleport node with the label flavor=$FLAVOR (default rct) and name *-smc01.
#   DEVICES  space-separated MikroTik IPs to query per site (default "10.255.0.5 10.255.0.20": RB450Gx4 switch, Metal AP)
#   WORKERS  parallel sites (default 5; every site is a satellite link)
#   TSH_PROXY, MT_ENTRY, MT_PY  passed through to mikrotik_exec.sh (MT_PY: Python, default python3; the justfile sets the pinned venv)
#
# Reading it: a switch uptime much shorter than the SMC's means it was power-cycled (on rct, usually by the SMC's own TSTIK app
# after ~11 min of failed switch/AP pings). Rising link-downs on the SMC-facing port point at the cable or a port. Voltage is the
# DC bus the board is fed from (about 24-27 V on the rct solar systems seen so far).
set -u
out=${1:?usage: mikrotik_fleet_survey.sh <outdir> [smc-host ...]}; shift
here=$(cd "$(dirname "$0")" && pwd)
devices=${DEVICES:-10.255.0.5 10.255.0.20}
workers=${WORKERS:-5}
proxy=${TSH_PROXY:-teleport.apn.au}
py=${MT_PY:-python3}
mkdir -p "$out/raw"

if [ $# -eq 0 ]; then
  hosts=()
  while IFS= read -r h; do [ -n "$h" ] && hosts+=("$h"); done < <(tsh ls --proxy="$proxy" --format=json "flavor=${FLAVOR:-rct}" 2>/dev/null \
    | "$py" -c 'import json,sys; print("\n".join(sorted(n["spec"]["hostname"] for n in json.load(sys.stdin) if n["spec"]["hostname"].endswith("-smc01"))))')
  set -- ${hosts[@]+"${hosts[@]}"}
fi
echo "$(date '+%F %T') surveying $# sites: devices $devices" >&2

# survey_one <smc-host>: read every device in $devices behind one SMC, save each raw capture to $out/raw/<smc>_<ip>.txt, and print one CSV row
# per device (identity, board, version, uptime, voltage, temperature, link-downs by port, log link-down lines). Runs in a child bash under
# `xargs -P`, so everything it uses is exported below. A device that does not answer still gets a row, with reached=no and empty fields.
survey_one() {
  local smc=$1 ip f
  for ip in $devices; do
    f="$out/raw/${smc}_${ip}.txt"
    "$here/mikrotik_exec.sh" "$smc" "$ip" \
      '/system identity print' '/system resource print' '/system routerboard print' '/system health print' \
      '/interface print detail without-paging' '/interface ethernet print stats without-paging' \
      '/log print without-paging where topics~"interface|system|critical|error"' > "$f" 2>&1
    "$py" - "$f" "$smc" "$ip" <<'PY'
import re, sys
f, smc, ip = sys.argv[1:4]
t = open(f, errors="replace").read()
g = lambda pat: (m.group(1).strip() if (m := re.search(pat, t, re.M)) else "")
link_downs = {m.group(1): int(m.group(2)) for m in re.finditer(r'name="([^"]+)"[^\n]*?(?:\n[^\n#]*?)*?link-downs=(\d+)', t)}
ld = ";".join(f"{k}={v}" for k, v in sorted(link_downs.items()) if v)
reached = "yes" if "name:" in t else "no"
log_ld = len(re.findall(r"link down", t))
print(",".join([smc, ip, reached, g(r"^\s*name: (.+)"), g(r"board-name: (.+)"), g(r"version: (\S+)"), g(r"uptime: (\S+)"),
                g(r"voltage\s+([\d.]+)"), g(r"temperature\s+([\d.]+)"), ld, str(log_ld)]))
PY
  done
}
export -f survey_one; export out here devices py

echo "smc,device_ip,reached,identity,board,routeros,uptime,voltage_v,temp_c,link_downs_by_port,log_link_down_lines" > "$out/survey.csv"
printf '%s\n' "$@" | xargs -P "$workers" -I{} bash -c 'survey_one "$@"' _ {} >> "$out/survey.csv"
echo "$(date '+%F %T') done: $out/survey.csv" >&2
