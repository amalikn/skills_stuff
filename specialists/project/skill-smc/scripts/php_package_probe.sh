#!/usr/bin/env bash
# Read-only PHP exposure probe for SMC boxes and other Ubuntu/RHEL hosts, over Teleport.
#
# usage: php_package_probe.sh [--parallel N] --proxy <teleport-proxy> <node> [<node> ...]
#   e.g. php_package_probe.sh --proxy teleport.apn.au beagle-bay-smc01 fish-river-smc01
#        php_package_probe.sh --proxy teleport.communitywifi.net.au $(cat nodes.txt)
#
# Prints one `PHPPROBE|<node>|host=<hostname>|key=value|...` line per box (host shows a mismatch): os, arch, php (PHP_VERSION), the installed (`ii`) PHP and
# libapache2-mod-php package versions, rpm PHP packages, loaded Apache PHP/FCGI modules, apt candidate for php8.1-common,
# apache2 state, overlay root and lower-dir mode, apt holds on php/apache, unattended-upgrades state, overlayroot-chroot
# presence, free MB on / and /media/root-ro, every long-running PHP process (a `php -S` built-in server or a cron-run CLI
# job keeps the old build until restarted), listening PHP sockets, and running containers. Ubuntu backports fixes into
# its own 8.1.2 build, so `php` alone never shows patch state: compare the package version to the USN's fixed build.
# Only reads; writes nothing on the box or locally. Set DEEP=1 to also search the disk for PHP binaries and modules.
# Exit status: 0 when every node answered, 1 when any node was unreachable or gave no probe line, 2 on bad usage.
# Origin: ansible-wifi PHP CVE-2026-109618/109619 assessment, 2026-10-22 (references/10_captive-portal.md).
set -u

usage() {
  # Print the header comment as help.
  #
  # Args: none.
  # Returns: 0; writes the usage text to stdout.
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
}

# The on-box probe. Kept in one quoted heredoc so nothing expands locally.
read -r -d '' PROBE <<'EOF'
kv() { printf '|%s=%s' "$1" "$(printf '%s' "$2" | tr '\n|' ' /' | sed -E 's/ +/ /g; s/ $//')"; }
os=$( . /etc/os-release 2>/dev/null; echo "${ID:-?}-${VERSION_ID:-?}")
out="$(kv os "$os")$(kv arch "$(uname -m)")"
out="$out$(kv php "$(php -r 'echo PHP_VERSION;' 2>/dev/null || echo none)")"
out="$out$(kv deb "$(dpkg-query -W -f='${db:Status-Abbrev} ${Package}=${Version}\n' 'php*' 'libapache2-mod-php*' 2>/dev/null | awk '$1=="ii"{print $2}')")"
out="$out$(kv rpm "$(rpm -qa 2>/dev/null | grep -E '^php')")"
out="$out$(kv apache_mods "$(apache2ctl -M 2>/dev/null | grep -oE 'php[0-9_]*_module|proxy_fcgi_module')")"
out="$out$(kv apache2 "$(systemctl is-active apache2 2>/dev/null)")"
out="$out$(kv candidate_php81 "$(apt-cache policy php8.1-common 2>/dev/null | awk '/Candidate/{print $2}')")"
out="$out$(kv overlay_root "$(mount | grep -c 'on / type overlay')")"
out="$out$(kv lower_dir "$(mount | grep ' /media/root-ro ' | grep -oE '\((rw|ro)' | tr -d '(')")"
out="$out$(kv holds "$(apt-mark showhold 2>/dev/null | grep -iE 'php|apache')")"
out="$out$(kv unattended "$(systemctl is-enabled unattended-upgrades 2>/dev/null)")"
out="$out$(kv overlayroot_chroot "$(command -v overlayroot-chroot >/dev/null && echo yes || echo no)")"
out="$out$(kv free_root_mb "$(df -m / | awk 'NR==2{print $4}')")"
out="$out$(kv free_lower_mb "$(df -m /media/root-ro 2>/dev/null | awk 'NR==2{print $4}')")"
out="$out$(kv php_procs "$(ps -eo user=,args= | awk '$2 ~ /(^|\/)php[0-9.]*$/ {sub(/^ +/,""); print}' | sort -u | tr '\n' ';')")"
out="$out$(kv php_listen "$(ss -ltnp 2>/dev/null | grep -E '"php[^"]*"' | awk '{print $4}' | sort -u)")"
out="$out$(kv containers "$(for t in docker podman; do command -v $t >/dev/null && $t ps --format '{{.Image}}' 2>/dev/null; done)")"
if [ "${DEEP:-0}" = 1 ]; then
  out="$out$(kv php_files "$(find / -xdev \( -path /proc -o -path /sys \) -prune -o -type f \( -name php -o -name 'php[0-9]*' -o -name 'php-fpm*' -o -name 'libphp*.so' \) -print 2>/dev/null | head -10)")"
fi
echo "PHPPROBE$(kv host "$(hostname)")$out"
EOF

proxy=""
parallel=8
while [ $# -gt 0 ]; do
  case "$1" in
    --proxy) proxy="${2:-}"; shift 2 ;;
    --proxy=*) proxy="${1#--proxy=}"; shift ;;
    --parallel) parallel="${2:-8}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
if [ -z "$proxy" ] || [ $# -eq 0 ]; then
  usage >&2
  exit 2
fi

probe_one() {
  # Run the probe on one node and print its PHPPROBE line, or a FAIL line.
  #
  # Args:
  #   $1: node name as Teleport knows it.
  # Returns: 0 when a probe line came back, 1 otherwise; prints one line either way.
  local node="$1" line
  line="$(tsh ssh --proxy="$proxy" "root@$node" "DEEP=${DEEP:-0} bash -s" <<<"$PROBE" 2>&1 | tr -d '\r' | grep '^PHPPROBE|' | head -1)"
  if [ -n "$line" ]; then
    echo "PHPPROBE|$node|${line#PHPPROBE|}"
    return 0
  fi
  echo "FAIL|$node|no probe output (Teleport unreachable? check scripts/backdoor-watch.sh)"
  return 1
}

rc=0
running=0
for node in "$@"; do
  probe_one "$node" &
  running=$((running + 1))
  if [ "$running" -ge "$parallel" ]; then
    wait -n || rc=1
    running=$((running - 1))
  fi
done
while [ "$running" -gt 0 ]; do
  wait -n || rc=1
  running=$((running - 1))
done
exit "$rc"
