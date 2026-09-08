# SMC WAN-routing diagnostics — reusable task runner template.
#
# ORIGIN: written 2026-07-29 for the APN routing-issue investigation
# (local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/). Promoted into skill-smc for
# reuse on future WAN-routing/topology-drift investigations. Copy this file into a new
# investigation folder alongside collect-smc-evidence.sh and analyse-routing-drift.py (or symlink
# to skill-smc's copies), then edit the `sites` list and `deployed` commit below for that
# investigation before running anything.
#
# Every recipe here is READ-ONLY with respect to the SMC appliances and the ansible-wifi repo.
# Nothing in this file changes a site. See scripts/README.md (in this skill-smc directory) for
# the full safety contract on the two scripts this justfile wraps.

set shell := ["bash", "-uc"]

ansible_repo := "/Volumes/Data/_ansible/ansible-wifi"
deployed     := "REPLACE_WITH_THE_DEPLOYED_COMMIT_FOR_YOUR_INVESTIGATION"
flavor       := "rcp"

# EDIT THIS before use — there is no universal site list, this is investigation-specific.
sites := "site-one site-two site-three"

# Show available recipes
default:
    @just --list

# --- Live capture (read-only, requires tsh login) -------------------------------------------

# Confirm Teleport session is live before capturing
check-login:
    @tsh status 2>/dev/null | grep -E 'Cluster:|Valid until:' || { echo "not logged in — run: tsh login"; exit 1; }

# Capture read-only evidence from every site in `sites` above
collect: check-login
    ./scripts/collect-smc-evidence.sh {{sites}}

# Capture from named sites, e.g. just collect-sites "umoona beagle-bay"
collect-sites sites: check-login
    ./scripts/collect-smc-evidence.sh {{sites}}

# --- Analysis (local only) ------------------------------------------------------------------

# Correlate live routing state against the deployed topology
analyse:
    ./scripts/analyse-routing-drift.py --flavor {{flavor}}

# Same, as a markdown table ready to paste into an analysis document
analyse-md:
    ./scripts/analyse-routing-drift.py --flavor {{flavor}} --markdown

# Compare against a commit other than the deployed one
analyse-commit commit:
    ./scripts/analyse-routing-drift.py --flavor {{flavor}} --commit {{commit}}

# Cross-check topology_vars physical interfaces/VLANs against a site's actual live hardware
# (catches wrong NIC names, wrong VLAN parents, and VLANs missing from either side — run this
# BEFORE editing topology_vars or deploying to a site you haven't touched recently)
match-topology site:
    ./scripts/analyse-topology-interface-match.py {{site}} --flavor {{flavor}}

# List captures held locally
list-captures:
    @test -d evidence && find evidence -maxdepth 1 -mindepth 1 -type d | sort || echo "no captures yet"

# --- Topology forensics (local git, read-only) ----------------------------------------------

# switch01 primary counts per site at the deployed commit — edit the site loop below
topology-counts:
    #!/usr/bin/env bash
    cd {{ansible_repo}}
    for s in {{sites}}; do
      n=$(git show {{deployed}}:inventories/{{flavor}}/topology_vars/$s.yml 2>/dev/null \
          | grep -A1 -E '^\s+internet[0-9]+:' | grep -oE 'vlanid: 52[0-9]' | wc -l | tr -d ' ')
      printf '%-16s %s\n' "$s" "${n:-n/a}"
    done

# Which refs, if any, define a given VLAN for a given site
find-vlan site vlan:
    #!/usr/bin/env bash
    cd {{ansible_repo}}
    echo "searching every ref for vlanid: {{vlan}} in {{site}}.yml"
    found=0
    for ref in $(git for-each-ref --format='%(refname)'); do
      if git show "$ref:inventories/{{flavor}}/topology_vars/{{site}}.yml" 2>/dev/null \
         | grep -q "vlanid: {{vlan}}"; then echo "  FOUND in $ref"; found=1; fi
    done
    [ "$found" -eq 0 ] && echo "  not defined in any ref"

# Last commit touching each site's topology file, across all refs
topology-history:
    #!/usr/bin/env bash
    cd {{ansible_repo}}
    for s in {{sites}}; do
      printf '%-16s %s\n' "$s" "$(git log --all -1 --date=short \
        --format='%ad %h %an' -- inventories/{{flavor}}/topology_vars/$s.yml)"
    done
