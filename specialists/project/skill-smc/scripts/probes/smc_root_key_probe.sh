#!/usr/bin/env bash
# Read-only probe of root's login secrets on SMCs over Teleport: is root's SSH key and password the same on every box (cloned from one warehouse image)?
#
# usage: smc_root_key_probe.sh --proxy <teleport-proxy> [--deadline <seconds>] <node> [<node> ...]
#   e.g. smc_root_key_probe.sh --proxy teleport.apn.au warehouse-rct01 alpurrurulam-smc01
#
# Prints one line per box: `<node> key=<fingerprint of /root/.ssh/id_rsa> pw=<hash type>:<first 12 hex of sha256 of root's shadow field>
# auth_keys=<count> sshd=<permitrootlogin,passwordauthentication> os=<VERSION_ID> arch=<machine> systemd=<version>`. Equal `key` or `pw` values on
# two boxes mean the same key or password; neither the key, the hash nor the password is ever printed (the pw digest only tells equal from different).
# Only reads; writes nothing on the box or locally. The proxy is required and never guessed. Each tsh call is cut at the deadline (default 60 s).
# Exit status: 0 when every node answered, 1 when any did not, 2 on bad usage.
# Origin: smc-resiliency 2026-11-19 (B19-06): the same root key on 11 of 11 boxes read and in the warehouse rct-iridium image; this re-reads it when
# the fix is checked.
set -u

usage() {
  # Print the header comment as help.
  # Args: none. Returns: 0; the help text on stdout.
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
}

proxy=""
deadline=60
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

# Run on the box as one script on stdin of a login shell (no quoting through tsh).
read -r -d '' REMOTE <<'EOS'
k=$(ssh-keygen -lf /root/.ssh/id_rsa 2>/dev/null | cut -d' ' -f2); [ -n "$k" ] || k=none
h=$(awk -F: '$1=="root"{print $2}' /etc/shadow)
t=$(printf '%s' "$h" | cut -d'$' -f2); d=$(printf '%s' "$h" | sha256sum | cut -c1-12)
a=$(grep -cE '^(ssh-|ecdsa-)' /root/.ssh/authorized_keys 2>/dev/null); a=${a:-0}
s=$(sshd -T 2>/dev/null | awk '$1=="permitrootlogin"||$1=="passwordauthentication"{printf "%s,",$2}')
echo "@@ key=$k pw=\$$t:$d auth_keys=$a sshd=${s%,} os=$(. /etc/os-release; echo $VERSION_ID) arch=$(uname -m) systemd=$(dpkg-query -W -f='${Version}' systemd 2>/dev/null)"
EOS

one() {
  # Run the remote read on one node through tsh, cut at the deadline.
  # Args: $1 node. Returns: 0 answered, 1 not (a `<node> unreachable` line says so).
  local out rc
  out=$(printf '%s\n' "$REMOTE" | perl -e '$d=shift; defined(my $p=fork) or die "fork: $!"; if(!$p){exec @ARGV; exit 127} $SIG{ALRM}=sub{kill "TERM",$p; for(1..5){exit 124 if waitpid($p,1)>0; sleep 1} kill "KILL",$p; waitpid($p,0); exit 124}; alarm $d; waitpid($p,0); exit($? & 127 ? 128+($? & 127) : $?>>8)' "$deadline" \
    tsh ssh --proxy="$proxy" "root@$1" 'bash -s' 2>&1)
  rc=$?
  if [ $rc -eq 0 ] && printf '%s' "$out" | grep -q '^@@ '; then
    echo "$1 $(printf '%s\n' "$out" | sed -n 's/^@@ //p' | head -1)"
    return 0
  fi
  echo "$1 unreachable rc=$rc $(printf '%s\n' "$out" | sed 's/\x1b\[[0-9;]*m//g' | grep -m1 -iE 'error|offline|denied|refused|timed out' | cut -c1-120)"
  return 1
}

fail=0
for node in "$@"; do one "$node" || fail=1; done
exit $fail
