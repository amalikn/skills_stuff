---
id: shared-traversal
type: adr
title: Query and impact share one traversal engine
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ARCHITECTURE.md
tags: [design, traversal]
---

# Query and impact share one traversal engine

Decision: query and impact both call one `bounded_bfs` in `traversal.py`. No duplicated reachability or cycle-detection logic. Impact matches roots by exact-path or directory-prefix only — never bare basename (which exploded to 1361 roots for `main.yml` before the fix).
