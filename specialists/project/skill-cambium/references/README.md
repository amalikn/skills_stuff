# references/ — skill-cambium content source

The 6 numbered files here are this pack's content source (see `AGENTS.md` Working rules). This is a folder index only — task-to-file routing lives in the parent `RUNBOOK.md`'s Reference Routing table,
not duplicated here.

## Contents

- [Canonical governance linkage](#canonical-governance-linkage)
1. `01_overview.md` — device families/models, EoL/EoS snapshot, evidence-state discipline.
2. `02_device-access-and-vault.md` — KeePassXC `cambium-devices/` vault structure, `kp` wrapper gotchas, reference convention.
3. `03_asset-register-conventions.md` — naming grammar, per-site drift, site-name convention, R195P IP-derivation rule.
4. `04_device-inventory-schema.md` — `device-inventory.csv` column contract, `UNKNOWN` discipline, extraction workflow.
5. `05_known-issues.md` — coverage gaps, unverified assumptions, staleness risks.
6. `06_device-api-cli-reference.md` — device REST API / SSH CLI data points per adapter method, config-backup source, write-ops boundary.

Plus machine-readable companions, not counted among the numbered files:

- `site-addressing.yaml` — per-site/family IP addressing trust state and MAC-OUI lookup, companion to `03_asset-register-conventions.md`'s narrative.
- `snmp-oid-registry.yaml` — verified SNMP OIDs per device type (read or write, unit, date, method), companion to `06_device-api-cli-reference.md`.

## Canonical governance linkage

- Navigation and routing: [`../RUNBOOK.md`](../RUNBOOK.md)
- Agent guidance: [`../AGENTS.md`](../AGENTS.md)
