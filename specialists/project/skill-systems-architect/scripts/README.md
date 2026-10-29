---
Title: Offline script catalogue
Category: script-catalogue
Status: current
Authority: authored-guidance
Scope: skill-systems-architect scripts/
Last reviewed: 2026-10-29
Summary: Every helper in scripts/, its inputs, outputs, safety class, exit codes, recipe and limits.
---

# Offline script catalogue

Standard library only; run through the working-cache venv (`just bootstrap` once, then the recipes). No helper touches a host, hypervisor or network, and none writes a file.

## Helpers

| Script | Recipe | Input -> output | Safety and limits |
| --- | --- | --- | --- |
| [capacity_check.py](capacity_check.py) | `just capacity <plan.json>` | Nodes, demand, failure scenarios, optional restore -> RAM shortfall per scenario and restore time vs RTO | Read-only; 1 MiB, 1,000 nodes, 5,000 scenarios |
| [quorum_check.py](quorum_check.py) | `just quorum <cluster.json>` | Nodes, failure domains, optional QDevice, required scenarios -> votes left and quorum per node, domain and QDevice loss | Read-only; 64 nodes; votes only, not fencing or capacity |
| [ceph_capacity.py](ceph_capacity.py) | `just ceph <pools.json>` | Failure domains with raw TB, pools (replica size or EC k+m, min_size, tolerated domain losses, demand) -> plan TB and layout findings | Read-only; 256 domains, 64 pools; each pool assessed alone |
| [availability.py](availability.py) | `just availability <model.json>` | Series/parallel block model -> composite availability and downtime per year | Read-only; symlink to skill-network-architect (canonical) |
| [check_links.py](check_links.py) | `just links` | Skill folder -> every cited external URL probed (HEAD, GET fallback); failures and redirects with citing files | Read-only but uses the network; 8 workers, 15 s timeout, 2,000 URLs; symlink to skill-network-architect (canonical) |
| [fetch_sources.py](fetch_sources.py) | `just fetch-sources [--apply]` | Both packs' Markdown -> RFC .txt, PDFs and all-scraper Markdown snapshots in `sources/`, indexed in `sources/index.json` | Plan by default; writes only the store with --apply; resumable; 4 workers, timeouts, process-group kill; symlink to skill-network-architect (canonical) |
| [sources_ledger.py](sources_ledger.py) | `just ledger [--add f.json] [--apply]` | Pack Markdown + curated lists + store index -> rebuilt `sources.json` (curated evidence kept, every other cited URL as CITED, local copy paths) | Plan by default; writes only sources.json with --apply; symlink to skill-network-architect (canonical) |
| [check_package.py](check_package.py) | `just check` | Skill folder -> broken links, headers, JSON and Python syntax | Read-only; symlink to skill-network-architect (canonical) |

Exit status for every helper: 0 = no findings, 1 = findings, 2 = invalid input.

## Capacity model

Input keys: schema_version=1, nodes=[{id, domain, memory_gib, reserve_gib}], demand_gib, headroom_fraction and
scenarios=[{id, failed_nodes, failed_domains}], plus optional restore={data_gib, throughput_mbps, efficiency, fixed_seconds, rto_seconds}.
Effective RAM = sum(memory - reserve for surviving nodes) * (1 - headroom).
Restore seconds = fixed_seconds + data_gib * 2^30 * 8 / (throughput_mbps * 10^6 * efficiency).
Scenarios are explicit: include normal, maintenance, each relevant host and correlated domain loss. Unlisted failures are untested.
Pooled RAM and a serialised transfer budget only; no CPU, per-VM placement, quorum, storage, parallel recovery or RPO proof.

## Cluster models

Quorum = floor(total votes / 2) + 1. A QDevice adds 1 vote on an even node count and N-1 on an odd one (Proxmox pvecm; odd counts are discouraged and reported as a warning).
Scenarios evaluated: everything up, each node, each failure domain (a QDevice in that domain goes with it) and the QDevice alone; `must_survive` names the ones that must keep quorum. Join names with `+` for a combined failure, e.g. `domain:rack-a+qdevice`.
Ceph plan = (raw - the largest f domains) / overhead x nearfull (0.85 default), overhead = size, or (k+m)/k for erasure coding. Findings: fewer domains than placements;
too few to re-place after losing f (data stays degraded); min_size below 2 (replica) or k+1 (EC); demand above the plan.

## Runtime budget

Target: under 5 seconds per command on a workstation. Measured: 1,000 nodes and 5,000 scenarios in 0.25 s (evals/results.md). Re-measure when an input grows past its cap.
