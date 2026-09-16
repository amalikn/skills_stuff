---
id: module-ownership
type: spec
title: Fixed module ownership boundaries
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ARCHITECTURE.md
tags: [architecture, modules]
---

# Fixed module ownership boundaries

Fixed separations that must not be merged: app_config (tool config) vs ansible_config (repo ansible.cfg); variables vs vars_plugins; inventory vs inventory_flavors; query/impact share traversal.py. graph.py is the assembly orchestrator; renderer emits, validator gates. Changing these boundaries requires a new ADR.
