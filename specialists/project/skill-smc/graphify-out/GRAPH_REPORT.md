# Graph Report - skill-smc  (2026-10-07)

## Corpus Check
- 11 files · ~231,207 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 80 nodes · 117 edges · 14 communities detected
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]

## God Nodes (most connected - your core abstractions)
1. `search()` - 9 edges
2. `check_referenced_paths()` - 8 edges
3. `parse_live()` - 8 edges
4. `check_catalog_coverage()` - 7 edges
5. `check_version_single_source()` - 7 edges
6. `main()` - 6 edges
7. `fail()` - 6 edges
8. `counted()` - 6 edges
9. `check_version_format()` - 6 edges
10. `read()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `count()` --calls--> `search()`  [INFERRED]
  scripts/undervoltage-profile.py → scripts/smc_graylog.py
- `main()` --calls--> `search()`  [INFERRED]
  scripts/tplink_cli_driver.py → scripts/smc_graylog.py
- `_token()` --calls--> `read()`  [INFERRED]
  scripts/smc_graylog.py → scripts/analyse-routing-drift.py
- `search()` --calls--> `parse_netplan()`  [INFERRED]
  scripts/smc_graylog.py → scripts/analyse-topology-interface-match.py
- `check_version_format()` --calls--> `search()`  [INFERRED]
  scripts/check_governance.py → scripts/smc_graylog.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.23
Nodes (17): check_catalog_coverage(), check_referenced_paths(), check_split_path_tokens(), check_version_format(), check_version_single_source(), counted(), fail(), _live_surfaces() (+9 more)

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

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): No backticked path is split across two table rows by a trailing backslash.

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): Every repo-relative path named in a governance surface resolves on disk.

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Both directions: the catalog names nothing missing, and nothing present is uncat

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): manifest.json is the sole version-of-record; no other governance surface may har

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): No backticked path is split across two table rows by a trailing backslash.

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Every repo-relative path named in a governance surface resolves on disk.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Both directions: the catalog names nothing missing, and nothing present is uncat

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): manifest.json is the sole version-of-record; no other governance surface may har

## Knowledge Gaps
- **23 isolated node(s):** `Strip ANSI, then honour carriage returns: the pager erases its prompt with CR +`, `Parse the committed topology_vars/<site>.yml from the working tree (not a specif`, `Range query chunked into <=10k-point windows. Returns {json(labels): [(t, v), ..`, `YYYY-MM-DD HH:MM' in AEDT -> epoch seconds.`, `No backticked path is split across two table rows by a trailing backslash.` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (1 nodes): `No backticked path is split across two table rows by a trailing backslash.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `Every repo-relative path named in a governance surface resolves on disk.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `Both directions: the catalog names nothing missing, and nothing present is uncat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `manifest.json is the sole version-of-record; no other governance surface may har`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `No backticked path is split across two table rows by a trailing backslash.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Every repo-relative path named in a governance surface resolves on disk.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Both directions: the catalog names nothing missing, and nothing present is uncat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `manifest.json is the sole version-of-record; no other governance surface may har`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `search()` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.390) - this node is a cross-community bridge._
- **Why does `check_version_format()` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Why does `parse_live()` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `search()` (e.g. with `count()` and `main()`) actually correct?**
  _`search()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Strip ANSI, then honour carriage returns: the pager erases its prompt with CR +`, `Parse the committed topology_vars/<site>.yml from the working tree (not a specif`, `Range query chunked into <=10k-point windows. Returns {json(labels): [(t, v), ..` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._