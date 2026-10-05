# Graph Report - skill-nautobot  (2026-10-05)

## Corpus Check
- 7 files · ~140,186 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 194 nodes · 306 edges · 25 communities detected
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 41 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]

## God Nodes (most connected - your core abstractions)
1. `PackageContractTests` - 14 edges
2. `Linkage` - 12 edges
3. `counted()` - 12 edges
4. `Source` - 11 edges
5. `fail()` - 11 edges
6. `SiteGraph` - 10 edges
7. `read()` - 9 edges
8. `Traverse` - 8 edges
9. `without_code()` - 8 edges
10. `MaskPlan` - 7 edges

## Surprising Connections (you probably didn't know these)
- `site()` --calls--> `SiteGraph`  [INFERRED]
  tests/test_helpers.py → scripts/nautobot_linkage.py
- `plan()` --calls--> `network_mask()`  [INFERRED]
  scripts/nautobot_masks.py → scripts/nautobot_ipam.py
- `pages()` --calls--> `traverse()`  [INFERRED]
  scripts/nautobot_linkage.py → scripts/nautobot_paging.py
- `pages()` --calls--> `listing()`  [INFERRED]
  scripts/nautobot_linkage.py → scripts/nautobot_paging.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (29): check_append_only_grain(), check_catalog_coverage(), check_constant_sync(), check_count_claims(), check_derived_freshness(), check_evidence_provenance(), check_index_links(), check_interpreter_pinning() (+21 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (22): evaluate(), Finding, islands(), label(), Linked, print_estate(), print_site(), Find the breaks in a Location's Nautobot hierarchy: objects that belong to it bu (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (10): _assert_safe_text(), _learned_entries(), _load(), PackageContractTests, Offline contract checks for the skill-nautobot guidance package., Return (kind, date, line) for every write-back entry outside code fences; raise, _scenario_relevant(), _snapshot_index() (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (13): Reads Nautobot through `get(path)` (path relative to /api, returning parsed JSON, Collect `site`'s objects in collector order, then join Relationship associations, (path, count) for every list endpoint that holds objects and is not in `covered`, Objects the API can filter to the site. `query` is formatted with the site name., (field, id) for every foreign key and M2M member in a depth-0 object., The id behind foreign key `key`, or None., ref(), refs() (+5 more)

### Community 4 - "Community 4"
Cohesion: 0.22
Nodes (8): apply(), plan(), Give every /32 address its subnet's mask: plan the changes from address and Pref, (to fix: [(address, "host/len")], to report: [(address, why)]) for one Namespace, Bulk-PATCH each planned `address` through `call(method, path, body)`, `batch` ob, addr(), MaskPlan, nautobot_masks: which /32s get their subnet's mask, which are only reported, and

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (12): pages(), A `next` link is absolute; the caller's GET takes paths relative to /api., Every row of `path` at depth 0 with M2M members, in a total order, failing close, _relative(), listing(), PagingError, Fail-closed traversal of a Nautobot REST listing. Stdlib only; the caller suppli, The listing cannot be trusted as one consistent set of objects. (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.21
Nodes (6): fk(), Governance, Listing, Offline tests for the promoted helpers in scripts/: the fail-closed paging guard, scripts/check_governance.py ("check_governance") is the pack's governance gate;, site()

### Community 7 - "Community 7"
Cohesion: 0.2
Nodes (4): list, pages(), A fake GET over numbered pages: page n holds chunks[n]., Traverse

### Community 8 - "Community 8"
Cohesion: 0.26
Nodes (4): location(), The objects joined to `oid` by Relationship `key`, in either direction., The objects collected for one site, keyed by id, plus Relationship edges (a, b,, SiteGraph

### Community 9 - "Community 9"
Cohesion: 0.27
Nodes (7): network_mask(), _prefix_type(), Pure IPAM rules for Nautobot 3.x data. Stdlib only, no I/O.  The mask an address, The prefix length of the narrowest `network` Prefix in `prefixes` (REST dicts wi, `ip/len` using `network_mask`; None when no network Prefix holds the address (cr, with_mask(), Mask

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): A fake GET over numbered pages: page n holds chunks[n].

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): scripts/check_governance.py ("check_governance") is the pack's governance gate;

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Record one assertion actually evaluated. Never call this per function — only per

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Strip fenced code blocks. Their contents are examples, not claims about this rep

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Read a CSV as dicts, or an empty list when it does not exist — an absent table c

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Every repo-relative path named in a governance surface resolves on disk.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Links inside an index file resolve, relative to the index's own folder.

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Prose stating a quantity matches the real count. Lines marked as historical fact

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Both directions: the catalog names nothing missing, and nothing present is uncat

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Recipes named in prose exist in the task runner, and every cataloged script has

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): No task recipe reaches an interpreter implicitly.      Two defects, one root cau

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Generated artifacts are not older than the sources they are generated from.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Facts restated across surfaces stay identical, and no unregistered file restates

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Every row of an append-only table stamps its pass, and no pass records the same

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Every markdown capture states where it came from, when, and whether the fetch su

## Knowledge Gaps
- **67 isolated node(s):** `Offline contract checks for the skill-nautobot guidance package.`, `Return (kind, date, line) for every write-back entry outside code fences; raise`, `Offline tests for the promoted helpers in scripts/: the fail-closed paging guard`, `A fake GET over numbered pages: page n holds chunks[n].`, `nautobot_masks: which /32s get their subnet's mask, which are only reported, and` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (1 nodes): `A fake GET over numbered pages: page n holds chunks[n].`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `scripts/check_governance.py ("check_governance") is the pack's governance gate;`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `Record one assertion actually evaluated. Never call this per function — only per`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `Strip fenced code blocks. Their contents are examples, not claims about this rep`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `Read a CSV as dicts, or an empty list when it does not exist — an absent table c`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Every repo-relative path named in a governance surface resolves on disk.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Links inside an index file resolve, relative to the index's own folder.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Prose stating a quantity matches the real count. Lines marked as historical fact`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Both directions: the catalog names nothing missing, and nothing present is uncat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Recipes named in prose exist in the task runner, and every cataloged script has`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `No task recipe reaches an interpreter implicitly.      Two defects, one root cau`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Generated artifacts are not older than the sources they are generated from.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Facts restated across surfaces stay identical, and no unregistered file restates`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Every row of an append-only table stamps its pass, and no pass records the same`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Every markdown capture states where it came from, when, and whether the fetch su`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `table_rows()` connect `Community 0` to `Community 7`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `evaluate()` connect `Community 1` to `Community 8`, `Community 7`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `site()` connect `Community 6` to `Community 8`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Source` (e.g. with `.test_collects_in_order_and_joins_relationships()` and `.test_doubtful_listing_fails_closed()`) actually correct?**
  _`Source` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Offline contract checks for the skill-nautobot guidance package.`, `Return (kind, date, line) for every write-back entry outside code fences; raise`, `Offline tests for the promoted helpers in scripts/: the fail-closed paging guard` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._