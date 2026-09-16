---
id: generic-inventory-scoping
type: adr
title: Generic inventory flavor/environment discovery
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ARCHITECTURE.md
tags: [inventory, portability]
---

# Generic inventory flavor/environment discovery

Decision: inventory scopes (flavors) and sub-scopes (environments) are discovered from the filesystem, never hardcoded. A repo may have 0, 1, or N scopes; names like prod/stage/production are read, not assumed. Handles no-inventory, single flat file, standard production/staging dirs, and multi-flavor layouts alike.
