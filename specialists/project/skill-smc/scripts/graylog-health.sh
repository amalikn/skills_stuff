#!/usr/bin/env bash
# graylog-health.sh — read-only health of the APN Graylog (gl.aws.apn.au) at every layer that failed on 2026-10-08/09.
#
# What it checks, top to bottom (references/03_communication-flows.md "Graylog Backend Path"; 13_known-issues.md 2026-10-09):
#   1. AWS target groups apn-graylog-{api,web,gelf}-tg: healthy or not (noc-admin profile).
#   2. apn-graylog01: graylog-server and mongod active AND enabled at boot; listening on 9000 and 12202.
#   3. apn-datanode01: graylog-datanode active AND enabled at boot; listening on 9200; host boot time.
#   4. Graylog API through the apn-graylog Teleport app: indexer cluster health (needs ../.graylog-token).
#   5. AWS scheduled events on both instances (a scheduled reboot restarts only what is enabled).
# Nothing is changed. Run: scripts/graylog-health.sh   (or: just -f scripts/fleet-health.justfile graylog-health)
# Needs: `tsh login --proxy=teleport.apn.au`, the AWS `noc-admin` profile, and for step 4 `tsh apps login apn-graylog`.
# Exit status: 0 when every check passes, 1 when any fails.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
AWS=(aws --profile noc-admin --region ap-southeast-2)
PROXY="teleport.apn.au"
bad=0

# say: print a check's result and count a failure.
#   Args: $1 ok|FAIL, $2 the check's description.
#   Returns: nothing; sets bad=1 on FAIL.
say() { printf '%-5s %s\n' "$1" "$2"; [ "$1" = ok ] || bad=1; }

for tg in apn-graylog-api-tg apn-graylog-web-tg apn-graylog-gelf-tg; do
  arn=$("${AWS[@]}" elbv2 describe-target-groups --names "$tg" --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null)
  st=$("${AWS[@]}" elbv2 describe-target-health --target-group-arn "$arn" --query 'TargetHealthDescriptions[0].TargetHealth.State' --output text 2>/dev/null)
  [ "$st" = healthy ] && say ok "$tg healthy" || say FAIL "$tg ${st:-unreadable}"
done

# host_check: services active and enabled, and ports listening, on one Teleport node.
#   Args: $1 node, $2 space-separated services, $3 space-separated ports.
#   Returns: nothing; prints one line per service and port.
host_check() {
  local out
  out=$(tsh --proxy="$PROXY" ssh "root@$1" "for s in $2; do echo \"svc \$s \$(systemctl is-active \$s) \$(systemctl is-enabled \$s 2>/dev/null)\"; done; for p in $3; do ss -ltn | grep -q \":\$p \" && echo \"port \$p up\" || echo \"port \$p down\"; done; echo \"boot \$(uptime -s)\"" 2>/dev/null) \
    || { say FAIL "$1 unreachable over tsh"; return; }
  while read -r kind a b c; do
    case "$kind" in
      svc)  [ "$b" = active ] && [ "$c" = enabled ] && say ok "$1 $a active, enabled at boot" || say FAIL "$1 $a $b, $c at boot" ;;
      port) [ "$b" = up ] && say ok "$1 port $a listening" || say FAIL "$1 port $a not listening" ;;
      boot) printf 'info  %s booted %s %s\n' "$1" "$a" "$b" ;;
    esac
  done <<< "$out"
}
host_check apn-graylog01 "graylog-server mongod" "9000 12202"
host_check apn-datanode01 "graylog-datanode" "9200"

cert=$(tsh --proxy="$PROXY" apps config apn-graylog --format=cert 2>/dev/null)
key=$(tsh --proxy="$PROXY" apps config apn-graylog --format=key 2>/dev/null)
token=$(cat "$HERE/../.graylog-token" 2>/dev/null)
if [ -f "$cert" ] && [ -n "$token" ]; then
  h=$(curl -s -m 30 --cert "$cert" --key "$key" -u "$token:token" -H 'Accept: application/json' \
      "https://apn-graylog.$PROXY/api/system/indexer/cluster/health" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status","?"))' 2>/dev/null)
  [ "$h" = green ] && say ok "Graylog indexer cluster green" || say FAIL "Graylog indexer cluster ${h:-unreadable (API down?)}"
else
  printf 'skip  Graylog API: run `tsh --proxy=%s apps login apn-graylog` and keep ../.graylog-token\n' "$PROXY"
fi

for name in apn-graylog01 apn-datanode01; do
  id=$("${AWS[@]}" ec2 describe-instances --filters "Name=tag:Name,Values=$name" --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null)
  ev=$("${AWS[@]}" ec2 describe-instance-status --instance-ids "$id" --include-all-instances \
       --query 'InstanceStatuses[0].Events[?!starts_with(Description, `[Completed]`)].[Code,NotBefore]' --output text 2>/dev/null)
  [ "$ev" = None ] && ev=""   # no Events list at all
  [ -z "$ev" ] && say ok "$name no pending AWS scheduled event" || say FAIL "$name pending AWS event: $ev"
done
exit "$bad"
