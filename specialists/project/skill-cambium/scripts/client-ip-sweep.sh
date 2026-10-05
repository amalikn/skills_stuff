#!/usr/bin/env bash
# client-ip-sweep.sh — read-only check of "why does cnMaestro show Wi-Fi clients with IPv4 0.0.0.0?" for one site.
#
# Compares three layers so the fault is placed, not guessed:
#   1. SMC  — isc-dhcp-server health over the last hour (ACK/NAK/DISCOVER, "no free leases").
#   2. AP   — the client IPv4 the AP itself reports, which is what device-agent forwards to cnMaestro:
#             R195P  -> /tmp/stahost (written by /bin/device-agent; column 2 is the IPv4)
#             E/XV   -> `show wireless clients` (last column IPv4)
#             KNOWN LIMIT (2026-10-05): on XV2 (6.6.x) a non-interactive `ssh ... "show wireless clients"` logs in but prints nothing,
#             so XV2 units report "no table" here, which is NOT "no clients". E500 prints the table fine.
#   3. Join — for each AP-reported client MAC, whether the SMC holds a dhcpd lease for it.
# A client with zero_ip on the AP but a lease on the SMC is a reporting gap, not a DHCP failure.
#
# Usage:   scripts/client-ip-sweep.sh <site>-smc01 <apn|nbn> [samples_per_family=3]
# Needs:   tsh logged in to the cluster; `kp` vault wrapper; OpenSSH 8.4+ (SSH_ASKPASS_REQUIRE).
# Vault:   cambium-devices/{apn,nbn}-snmp-ro, cnpilot-r-series(-legacy), enterprise-wifi(-legacy). Passwords never printed;
#          the SNMP community is piped over stdin, device passwords go through a throwaway SSH_ASKPASS helper.
# Writes:  nothing on SMC or devices. Only GETs (snmpget sysDescr) and file reads / show commands.
# First run 2026-10-05 (kalumburu, burringurrah, bidyadanga, ... — see references/05_known-issues.md).
set -uo pipefail

smc=${1:?usage: client-ip-sweep.sh <site>-smc01 <apn|nbn> [samples]}; prog=${2:?apn|nbn}; samples=${3:-3}
if [ "$prog" = nbn ]; then dom=teleport.communitywifi.net.au; snmp=nbn-snmp-ro
else dom=teleport.apn.au; snmp=apn-snmp-ro; fi
proxy=--proxy=$dom

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
printf '#!/bin/sh\nprintf "%%s\\n" "$CAMBIUM_PASS"\n' > "$tmp/askpass"; chmod 700 "$tmp/askpass"

echo "##### $smc ($prog)"
# SMC side: DHCP health, lease MAC list, and a sysDescr map of every Cambium AP on the management bridge.
kp show -s -a Password "cambium-devices/$snmp" 2>/dev/null | tsh ssh $proxy root@"$smc" '
read -r C
j=$(journalctl -u isc-dhcp-server --since "-1h" 2>/dev/null)
echo "DHCP1h ack=$(echo "$j" | grep -c DHCPACK) nak=$(echo "$j" | grep -c DHCPNAK) disc=$(echo "$j" | grep -c DHCPDISCOVER) nofree=$(echo "$j" | grep -c "no free leases")"
awk "/hardware ethernet/{gsub(\";\",\"\",\$3); print \"LEASE \" toupper(\$3)}" /var/lib/dhcp/dhcpd.leases | sort -u
for ip in $(ip neigh show dev bridge_500 2>/dev/null | awk "/lladdr/{print \$1}"); do
  d=$(snmpget -v2c -c "$C" -t1 -r0 -Oqv $ip 1.3.6.1.2.1.1.1.0 2>/dev/null | tr -d "\"" | cut -c1-48)
  case "$d" in *R195P*) echo "AP r195p $ip $d";; *cnPilot\ E*|*XV*|*Enterprise*) echo "AP ent $ip $d";; esac
done' > "$tmp/smc" 2>&1
grep DHCP1h "$tmp/smc" || { echo "  SMC unreachable:"; tail -3 "$tmp/smc"; exit 1; }
grep '^LEASE ' "$tmp/smc" | cut -d' ' -f2 > "$tmp/leases"
echo "  leases_known=$(wc -l < "$tmp/leases" | tr -d ' ') r195p_found=$(grep -c '^AP r195p' "$tmp/smc") ent_found=$(grep -c '^AP ent' "$tmp/smc")"

dev() { # <vault-entry> <ip> <command>
  CAMBIUM_PASS="$(kp show -s -a Password "cambium-devices/$1" 2>/dev/null)" SSH_ASKPASS="$tmp/askpass" SSH_ASKPASS_REQUIRE=force DISPLAY=:0 \
  ssh -n -J root@"$smc.$dom" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 -o LogLevel=ERROR \
    -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -o KexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 admin@"$2" "$3" 2>&1 | grep -vE "post-quantum|store now|pq.html"; }
leased() { tr '-' ':' | while read -r m; do grep -qx "$m" "$tmp/leases" && echo y; done | grep -c y; }

# Keep reading APs until $samples of them have at least one client (idle APs prove nothing), capped at 4x samples.
n=0; tries=0
for ip in $(awk '/^AP r195p/{print $3}' "$tmp/smc"); do
  [ $n -ge "$samples" ] || [ $tries -ge $((samples*4)) ] && break; tries=$((tries+1))
  fw=$(awk -v i="$ip" '$3==i{print $NF}' "$tmp/smc")
  out=$(dev cnpilot-r-series "$ip" 'cat /tmp/stahost'); echo "$out" | grep -q "Permission denied" && out=$(dev cnpilot-r-series-legacy "$ip" 'cat /tmp/stahost')
  rows=$(echo "$out" | grep -E '^([0-9A-F]{2}:){5}'); [ -z "$rows" ] && continue; n=$((n+1))
  echo "  R195P $ip fw=$fw clients=$(echo "$rows" | wc -l | tr -d ' ') zero_ip=$(echo "$rows" | grep -c ',0\.0\.0\.0,') leased_on_smc=$(echo "$rows" | cut -d, -f1 | leased)"
done
[ $n -eq 0 ] && echo "  R195P: no sampled unit had clients ($tries tried)"

n=0; tries=0
for ip in $(awk '/^AP ent/{print $3}' "$tmp/smc"); do
  [ $n -ge "$samples" ] || [ $tries -ge $((samples*4)) ] && break; tries=$((tries+1))
  model=$(awk -v i="$ip" '$3==i{$1=$2=$3=""; print}' "$tmp/smc" | sed 's/^ *//')
  out=$(dev enterprise-wifi "$ip" 'show wireless clients'); echo "$out" | grep -q "Permission denied" && out=$(dev enterprise-wifi-legacy "$ip" 'show wireless clients')
  rows=$(echo "$out" | grep -E '^ *([0-9A-F]{2}-){5}')
  if [ -z "$rows" ]; then echo "$out" | grep -q "MAC" || echo "  ENT $ip [$model] no table returned (XV2 non-interactive CLI limit, or login failed)"; continue; fi
  n=$((n+1))
  echo "  ENT $ip [$model] clients=$(echo "$rows" | wc -l | tr -d ' ') zero_ip=$(echo "$rows" | grep -c '0\.0\.0\.0 *$') leased_on_smc=$(echo "$rows" | awk '{print $1}' | leased) vlans=$(echo "$rows" | awk '{print $9}' | sort | uniq -c | awk '{printf "%s:%s ", $2, $1}')"
done
[ $n -eq 0 ] && echo "  ENT: no sampled unit returned a client row ($tries tried)"
