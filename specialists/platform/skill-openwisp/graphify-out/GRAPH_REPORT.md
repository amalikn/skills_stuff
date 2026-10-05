# Graph Report - skill-openwisp  (2026-10-05)

## Corpus Check
- 8 files · ~177,461 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 203 nodes · 322 edges · 23 communities detected
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 47 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]

## God Nodes (most connected - your core abstractions)
1. `PackageContractTests` - 14 edges
2. `counted()` - 12 edges
3. `fail()` - 11 edges
4. `AlertPolicyTests` - 10 edges
5. `OpenWispProbe` - 10 edges
6. `shell()` - 9 edges
7. `read()` - 9 edges
8. `without_code()` - 8 edges
9. `read_registered()` - 8 edges
10. `Registry` - 7 edges

## Surprising Connections (you probably didn't know these)
- `compare()` --calls--> `normalise_mac()`  [INFERRED]
  scripts/openwisp_registry.py → scripts/openwisp_identity.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (21): AlertPolicy, AlertSettingsConverger, diff_settings(), from_dict(), parse(), parse_device_pks(), plan_differences(), program() (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (29): check_append_only_grain(), check_catalog_coverage(), check_constant_sync(), check_count_claims(), check_derived_freshness(), check_evidence_provenance(), check_index_links(), check_interpreter_pinning() (+21 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (15): Finding, main(), OpenWispProbe, Each check runs read-only commands through `runner`, so tests can feed recorded, Celery nodes answering `inspect ping`. The 26.09.0 image runs five: celery, netw, Age of the newest point of `measurement`. Old data with live workers points at t, Effective Django settings in each container, compared with `expected`. Reports n, run() (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (18): compare(), django_shell(), find_mismatches(), parse_registered(), Read the devices registered in OpenWISP 1.3 by `hardware_id` and compare each wi, `<record name>: <issue>; <issue>` for every device that differs, in the order re, A runner for docker-openwisp: `docker exec -i <container> python manage.py shell, One OpenWISP device as registered; `mac` and `management_ip` are None when OpenW (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (10): _assert_safe_text(), _learned_entries(), _load(), PackageContractTests, Offline contract checks for the skill-openwisp guidance package., Return (kind, date, line) for every write-back entry outside code fences; raise, _scenario_relevant(), _snapshot_index() (+2 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (16): HealthReadError, MirrorPlan, plan_mirror(), Mirror OpenWISP 1.3 device health into a source of truth's fields, writing only, The shell failed and returned no health at all., {record id: health} for every registered device; `key` turns a hardware_id into, What a mirror run would write: `changes` (health changed or new) and `cleared` (, Registered devices per health value, keys sorted. (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.14
Nodes (12): backfill_time(), device_name(), from_hardware_id(), normalise_mac(), Pure identity and time conversions for integrating an inventory with OpenWISP 1., An inventory UUID as an OpenWISP `hardware_id`: the same 128 bits as 32 lowercas, The inverse of `to_hardware_id`: the dashed UUID. Raises ValueError when the val, A MAC in any common notation as `aa:bb:cc:dd:ee:ff`; None when it does not hold (+4 more)

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (1): From a loaded document: `defaults` and `classes_key` (the caller's name for its

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (1): (counts by SAME/WOULD/CHANGE, the non-SAME lines).

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (1): scripts/check_governance.py ("check_governance") is the pack's governance gate;

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): Record one assertion actually evaluated. Never call this per function — only per

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): Strip fenced code blocks. Their contents are examples, not claims about this rep

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Read a CSV as dicts, or an empty list when it does not exist — an absent table c

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Every repo-relative path named in a governance surface resolves on disk.

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Links inside an index file resolve, relative to the index's own folder.

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Prose stating a quantity matches the real count. Lines marked as historical fact

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Both directions: the catalog names nothing missing, and nothing present is uncat

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Recipes named in prose exist in the task runner, and every cataloged script has

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): No task recipe reaches an interpreter implicitly.      Two defects, one root cau

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Generated artifacts are not older than the sources they are generated from.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Facts restated across surfaces stay identical, and no unregistered file restates

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Every row of an append-only table stamps its pass, and no pass records the same

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Every markdown capture states where it came from, when, and whether the fetch su

## Knowledge Gaps
- **71 isolated node(s):** `Offline contract checks for the skill-openwisp guidance package.`, `Return (kind, date, line) for every write-back entry outside code fences; raise`, `Offline tests for the promoted helpers in scripts/: identity and time conversion`, `A recorded Django-shell runner; `calls` collects (program, stdin).`, `scripts/check_governance.py ("check_governance") is the pack's governance gate;` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 7`** (1 nodes): `From a loaded document: `defaults` and `classes_key` (the caller's name for its`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `(counts by SAME/WOULD/CHANGE, the non-SAME lines).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `scripts/check_governance.py ("check_governance") is the pack's governance gate;`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `Record one assertion actually evaluated. Never call this per function — only per`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `Strip fenced code blocks. Their contents are examples, not claims about this rep`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `Read a CSV as dicts, or an empty list when it does not exist — an absent table c`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `Every repo-relative path named in a governance surface resolves on disk.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `Links inside an index file resolve, relative to the index's own folder.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Prose stating a quantity matches the real count. Lines marked as historical fact`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Both directions: the catalog names nothing missing, and nothing present is uncat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Recipes named in prose exist in the task runner, and every cataloged script has`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `No task recipe reaches an interpreter implicitly.      Two defects, one root cau`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Generated artifacts are not older than the sources they are generated from.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Facts restated across surfaces stay identical, and no unregistered file restates`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Every row of an append-only table stamps its pass, and no pass records the same`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Every markdown capture states where it came from, when, and whether the fetch su`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AlertPolicyTests` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `parse()` connect `Community 0` to `Community 4`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `OpenWispProbe` (e.g. with `.test_workers_counts_replying_nodes()` and `.test_freshness_flags_old_point()`) actually correct?**
  _`OpenWispProbe` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Offline contract checks for the skill-openwisp guidance package.`, `Return (kind, date, line) for every write-back entry outside code fences; raise`, `Offline tests for the promoted helpers in scripts/: identity and time conversion` to the rest of the system?**
  _71 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._