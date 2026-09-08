# SMC fleet hardware/security/service-health audit — reusable task runner.
#
# ORIGIN: written 2026-08-03 for the first full NBN Accelerate cluster sweep (all nbn_accelerate
# + nbn_wh sites). Unlike routing-diagnostics.justfile, this one ships with a real, current site
# list below rather than a placeholder — the NBN Accelerate fleet is small and stable enough
# that hardcoding it here is more useful than forcing a copy-and-edit step every time. For a
# DIFFERENT fleet/flavor, either edit `sites` below or override on the command line, e.g.
#   just -f fleet-health.justfile collect-sites "site-one site-two"
#
# Every recipe here is READ-ONLY with respect to the SMC appliances. Nothing in this file changes
# a site. See scripts/README.md for the full safety contract on collect-fleet-health.sh.

set shell := ["bash", "-uc"]

# NBN Accelerate cluster — teleport.communitywifi.net.au. Confirmed live via `tsh ls` 2026-08-03;
# excludes central-infra nodes (cnmaestro01, cw-jenkins01, cw-prometheus01, cw-teleport01) and
# generic/test-only hosts (generic-*, aurukun-test-smc0*). aurukun-smc03 is in the static
# inventory but was not visible in `tsh ls` at capture time — check reachability before assuming
# it's covered by `collect`.
sites := "amata ampilatwatja arawerr arreyonga aurukun-smc01 aurukun-smc02 bungardi burawa darlngunaya doomadgee galiwinku gan-gan hope-vale indulkana junjuwa kaltjiti-fergon koonibba kowanyama kurnangki loanbun mimili mindi-rardi mungkarta pipalyatjara pormparaaw pukatja wandawuy warakurna"

# Show available recipes
default:
    @just --list

# --- Live capture (read-only, requires tsh login) -------------------------------------------

# Confirm Teleport session is live before capturing — NBN Accelerate cluster specifically
check-login:
    @tsh status 2>/dev/null | grep -A6 'communitywifi.net.au' | grep -E 'Cluster:|Valid until:' || { echo "not logged in to teleport.communitywifi.net.au — run: tsh login --proxy=teleport.communitywifi.net.au"; exit 1; }

# PATH NOTE (fixed 2026-08-03, found via dogfooding after the first real fleet run): `just -f
# <path>` runs every recipe with its working directory set to the JUSTFILE'S OWN DIRECTORY
# (scripts/), not the invoker's cwd and not skill-smc root. Since collect-fleet-health.sh writes
# evidence/ into its parent dir by default (REPO_ROOT resolves from the *script's* location, one
# level up from scripts/), every recipe below must say `./collect-fleet-health.sh` (sibling file,
# same dir as this justfile) and `../evidence` (one level up) — NOT `./scripts/...` or bare
# `evidence`, both of which silently resolved to a nonexistent path and failed with a misleading
# "no captures yet" on the very first real run of this file.

# Capture hardware + service-health evidence from the full NBN Accelerate fleet (28 sites, ~6 ssh round-trips each)
collect: check-login
    ./collect-fleet-health.sh {{sites}}

# Capture from named sites only, e.g. just -f fleet-health.justfile collect-sites "warakurna indulkana"
collect-sites sites: check-login
    ./collect-fleet-health.sh {{sites}}

# List captures held locally
list-captures:
    @test -d ../evidence && find ../evidence -maxdepth 1 -mindepth 1 -type d | sort || echo "no captures yet"

# --- Quick cross-host checks on the most recent capture --------------------------------------

# Which hosts have a failed clamav-freshclam (the 2026-08-03 finding, confirmed 26/26 nbn_accelerate on the first full sweep) in the latest capture
freshclam-check:
    #!/usr/bin/env bash
    latest=$(find ../evidence -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort | tail -1)
    [ -z "$latest" ] && { echo "no captures yet — run 'just -f fleet-health.justfile collect' first"; exit 1; }
    echo "checking: $latest"
    for f in "$latest"/*/02-services-security.txt; do
      host=$(basename "$(dirname "$f")")
      section=$(awk '/--freshclam-status--/{f=1;next}/--lynis-present--/{f=0}f' "$f" 2>/dev/null)
      if echo "$section" | grep -q "could not be found"; then
        printf '%-24s not installed\n' "$host"
      elif echo "$section" | grep -q "Active: failed"; then
        since=$(echo "$section" | grep -oE 'since [A-Za-z]+ [0-9-]+' | head -1)
        printf '%-24s FAILED (%s)\n' "$host" "${since:-unknown date}"
      else
        printf '%-24s ok\n' "$host"
      fi
    done

# Which hosts report a non-empty `systemctl --failed` in the latest capture (isc-dhcp-server6 is expected/benign fleet-wide — IPv6 is disabled by policy, see 08_ansible-authoring.md)
failed-units-check:
    #!/usr/bin/env bash
    latest=$(find ../evidence -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort | tail -1)
    [ -z "$latest" ] && { echo "no captures yet"; exit 1; }
    for f in "$latest"/*/02-services-security.txt; do
      host=$(basename "$(dirname "$f")")
      units=$(awk '/--failed-units--/{flag=1;next}/--teleport--/{flag=0}flag' "$f" 2>/dev/null | grep -v 'isc-dhcp-server6' | grep -c . || true)
      [ "${units:-0}" -gt 0 ] && printf '%-24s %s non-benign failed unit(s)\n' "$host" "$units"
    done
    true

# Distinct hardware chassis models seen across the latest capture (dmidecode system-product-name) — RPi flavors (nbn_wh) report empty here, dmidecode doesn't work on ARM/RPi boards; that's expected, check the cpu line instead for those
chassis-models:
    #!/usr/bin/env bash
    latest=$(find ../evidence -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort | tail -1)
    [ -z "$latest" ] && { echo "no captures yet"; exit 1; }
    for f in "$latest"/*/01-identity-hardware.txt; do
      host=$(basename "$(dirname "$f")")
      model=$(awk '/--dmidecode-product--/{getline; print; exit}' "$f" 2>/dev/null)
      # On ARM boards dmidecode-manufacturer prints nothing, which shifts awk's getline onto the
      # next marker line instead of real data — treat any captured "--marker--"-looking string as
      # empty rather than a real model name.
      case "$model" in --*--) model="" ;; esac
      if [ -z "$model" ]; then
        cpu=$(awk '/Model name:/{sub(/.*Model name:[ \t]*/,"");print;exit}' "$f" 2>/dev/null)
        model="(no dmidecode — ARM board, cpu: ${cpu:-unknown})"
      fi
      printf '%-24s %s\n' "$host" "$model"
    done
