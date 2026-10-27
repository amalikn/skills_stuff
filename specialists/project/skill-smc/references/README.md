---
Title: references folder index
Category: folder-index
Status: current
Authority: pointer
Scope: The numbered reference files, registries and vendor-source folders under references/
Last reviewed: 2026-10-27
Summary: Points to RUNBOOK.md, which routes every reference file; this folder keeps no second list so the four enforced catalogs stay the only ones.
---

# references

<!-- inverse-sweep:describes-only reason="RUNBOOK.md, SKILL.md, AI_NAVIGATION.md and context-map.yaml list every file here; check_catalog_coverage enforces all four" -->

The content source files of this pack. Open [RUNBOOK.md](../RUNBOOK.md) to find the one for a task: its routing table names every numbered reference. `just check` fails when a file here is missing from RUNBOOK.md,
SKILL.md, AI_NAVIGATION.md or context-map.yaml, so no list is kept in this folder.

- `NN_<topic>.md`: numbered reference files, one domain each.
- `*.yaml`, `*.csv`: registries (SNMP OIDs, site switches) named in the reference that owns them.
- `vendor-sources-<vendor>-<stamp>/`: verbatim vendor documents with their own `readme.md`.
- `screenshots/<YYYYMMDD>-<slug>/`: evidence images with their own `readme.md`.
