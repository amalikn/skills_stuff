# Graph Report - skill-smc  (2026-10-07)

## Corpus Check
- 11 files · ~232,200 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 70 nodes · 111 edges · 6 communities detected
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]

## God Nodes (most connected - your core abstractions)
1. `search()` - 8 edges
2. `check_referenced_paths()` - 8 edges
3. `parse_live()` - 8 edges
4. `check_catalog_coverage()` - 7 edges
5. `check_version_single_source()` - 7 edges
6. `main()` - 6 edges
7. `read()` - 6 edges
8. `_curl()` - 5 edges
9. `fail()` - 5 edges
10. `counted()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `count()` --calls--> `search()`  [INFERRED]
  scripts/undervoltage-profile.py → scripts/smc_graylog.py
- `main()` --calls--> `search()`  [INFERRED]
  scripts/tplink_cli_driver.py → scripts/smc_graylog.py
- `_token()` --calls--> `read()`  [INFERRED]
  scripts/smc_graylog.py → scripts/analyse-routing-drift.py
- `parse_netplan()` --calls--> `search()`  [INFERRED]
  scripts/analyse-topology-interface-match.py → scripts/smc_graylog.py
- `parse_hook()` --calls--> `search()`  [INFERRED]
  scripts/analyse-routing-drift.py → scripts/smc_graylog.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.25
Nodes (15): check_catalog_coverage(), check_referenced_paths(), check_split_path_tokens(), check_version_single_source(), counted(), fail(), _live_surfaces(), members() (+7 more)

### Community 1 - "Community 1"
Cohesion: 0.22
Nodes (15): committed_internet_vlans(), committed_primaries(), main(), newest_capture(), parse_hook(), parse_live(), parse_nat_ifaces(), parse_netplan_vlans() (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.31
Nodes (7): aggregate(), _cert(), _curl(), search(), _token(), _utc(), count()

### Community 3 - "Community 3"
Cohesion: 0.27
Nodes (7): epoch(), _get(), instant(), metric_names(), Range query chunked into <=10k-point windows. Returns {json(labels): [(t, v), .., YYYY-MM-DD HH:MM' in AEDT -> epoch seconds., rng()

### Community 4 - "Community 4"
Cohesion: 0.44
Nodes (8): main(), newest_capture(), parse_active_dhclient(), parse_model(), parse_netplan(), parse_topology(), Parse the committed topology_vars/<site>.yml from the working tree (not a specif, read()

### Community 5 - "Community 5"
Cohesion: 0.67
Nodes (3): clean(), main(), Strip ANSI, then honour carriage returns: the pager erases its prompt with CR +

## Knowledge Gaps
- **14 isolated node(s):** `Strip ANSI, then honour carriage returns: the pager erases its prompt with CR +`, `Parse the committed topology_vars/<site>.yml from the working tree (not a specif`, `Range query chunked into <=10k-point windows. Returns {json(labels): [(t, v), ..`, `YYYY-MM-DD HH:MM' in AEDT -> epoch seconds.`, `No backticked path is split across two table rows by a trailing backslash.` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `search()` connect `Community 2` to `Community 1`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `parse_netplan()` connect `Community 4` to `Community 2`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `parse_live()` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `search()` (e.g. with `count()` and `main()`) actually correct?**
  _`search()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Strip ANSI, then honour carriage returns: the pager erases its prompt with CR +`, `Parse the committed topology_vars/<site>.yml from the working tree (not a specif`, `Range query chunked into <=10k-point windows. Returns {json(labels): [(t, v), ..` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._