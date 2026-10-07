# Graph Report - skill-cambium  (2026-10-05)

## Corpus Check
- 12 files · ~78,579 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 239 nodes · 444 edges · 13 communities detected
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `CambiumCnWaveAdapter` - 22 edges
2. `_cmd_getters()` - 17 edges
3. `CambiumXV2Adapter` - 15 edges
4. `read()` - 15 edges
5. `CambiumEPMPAdapter` - 15 edges
6. `counted()` - 14 edges
7. `fail()` - 13 edges
8. `CambiumR195PAdapter` - 13 edges
9. `_cmd_getters()` - 11 edges
10. `main()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `known_ouis()` --calls--> `read()`  [INFERRED]
  scripts/generate_site_addressing_families.py → scripts/check_governance.py
- `cmd_observe()` --calls--> `load()`  [INFERRED]
  scripts/schema_tool.py → scripts/schema_divergence_report.py
- `main()` --calls--> `load()`  [INFERRED]
  scripts/scan-config-fields.py → scripts/schema_divergence_report.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (19): CambiumCnWaveAdapter, _cmd_getters(), main(), Public escape hatch for exploring an endpoint not yet wrapped by a getter below., NAPALM-style get_facts: device identity, firmware, uptime. `type` distinguishes, Whether THIS node runs the E2E controller. Check enabled=True before trusting ge, onboardStatus (is the E2E controller running on this box) and, if so, its own in, Confirmed live to 400 with an empty body on at least one real node (no GPS fix, (+11 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (35): check_append_only_grain(), check_catalog_coverage(), check_constant_sync(), check_count_claims(), check_derived_freshness(), check_evidence_provenance(), check_index_links(), check_interpreter_pinning() (+27 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (20): _askpass_helper(), CambiumR195PAdapter, _cmd_getters(), _extract_mac(), main(), _parse_ip_addr(), _parse_uci_text(), Talks to one cnPilot R195P's real BusyBox/Buildroot shell over SSH, via the syst (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (20): check_map(), cmd_check(), cmd_merge(), cmd_observe(), collapse_map(), _enumerable(), FalconDriver, FieldFacts (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (15): CambiumXV2Adapter, _cmd_dump(), _cmd_getters(), main(), Public escape hatch for exploring an endpoint not yet wrapped by a getter below., NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection, NAPALM-style get_interfaces: per-port link state and counters.          device-s, Per-radio operational state, channel/power, and utilization — merges radio-summa (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (14): CambiumEPMPAdapter, _cmd_getters(), main(), Public escape hatch: raw (unredacted) get_param response for a given `act` secti, `act=status` device_props: the snapshot's single read while get_snapshot() runs,, facts, interfaces, wireless_link, clients and counters from ONE `act=status` rea, NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection, LAN (Ethernet) port state. ePMP has one LAN port (two on some AP models, LAN2 fi (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (14): build_node_map(), free_port(), load_inventory(), main(), observe_adapter(), observe_wifi(), site -> (node, proxy). A site listed on both clusters is taken from the first th, The credential is fed to the remote shell on stdin, never as an argument.      A (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (9): find_flagged(), main(), Walk obj, return (path, has_nonempty_value) for every credential-shaped key foun, analyse(), classify(), load(), main(), endpoint -> field -> facts about where it was seen and what type it had. (+1 more)

### Community 8 - "Community 8"
Cohesion: 0.39
Nodes (8): audit_oui(), compute_families(), find_site_files(), ip_field(), known_ouis(), main(), Lowercase colon-form OUI keys already in oui_reference — stdlib-only parse (no P, render_site()

### Community 9 - "Community 9"
Cohesion: 0.4
Nodes (3): is_ip(), Hope Vale (nbn_accelerate) / Burringurrah (rcp) asset-register -> device-invento, sanip()

### Community 10 - "Community 10"
Cohesion: 0.6
Nodes (4): build(), main(), parse_walk(), `{oid: (snmp_type, value)}` from an `snmpwalk -On` capture, skipping absent-obje

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): Parser for this BusyBox's `ip -o addr show`, shared by get_interfaces() and get_

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Best-effort parse of BusyBox/OpenWrt-style UCI config text into a nested dict ke

## Knowledge Gaps
- **80 isolated node(s):** `Walk obj, return (path, has_nonempty_value) for every credential-shaped key foun`, `Recursively replace any dict value whose key looks credential-shaped with a plac`, `Talks to one Enterprise Wi-Fi XV2/XE-family AP's local REST API over HTTPS.`, `Public escape hatch for exploring an endpoint not yet wrapped by a getter below.`, `NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (1 nodes): `Parser for this BusyBox's `ip -o addr show`, shared by get_interfaces() and get_`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `Best-effort parse of BusyBox/OpenWrt-style UCI config text into a nested dict ke`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read()` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`, `Community 5`, `Community 8`?**
  _High betweenness centrality (0.463) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `read()` (e.g. with `._request()` and `._request()`) actually correct?**
  _`read()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Walk obj, return (path, has_nonempty_value) for every credential-shaped key foun`, `Recursively replace any dict value whose key looks credential-shaped with a plac`, `Talks to one Enterprise Wi-Fi XV2/XE-family AP's local REST API over HTTPS.` to the rest of the system?**
  _80 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._