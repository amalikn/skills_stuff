---
id: bounded-retrieval
type: rule
title: Bounded retrieval is mandatory
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from AGENTS.md, SKILL.md
tags: [performance, contract]
---

# Bounded retrieval is mandatory

Agents must not load the full `graph.yaml` by default. The compact `ANSIBLE_REPO_MAP.md` is the first read; graph slices come from bounded queries (default 25 nodes / 1 hop) and impact (50 nodes / 3 hops). Every traversal reports whether it was truncated and why. This guarantee is the point of the tool.
