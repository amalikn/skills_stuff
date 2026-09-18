# Cambium Asset Registers — Pointer

## Contents

- [Canonical Home](#canonical-home)
- [What Stays Here](#what-stays-here)

---

## Canonical Home

Full asset-register naming-convention, per-site drift, site-name convention, and R195P IP-derivation knowledge now lives in `skill-cambium`'s `references/03_asset-register-conventions.md` (moved
2026-09-17 — this pack originally held that content before `skill-cambium` existed). Read it there; this pack owns the SMC/Ansible layer, not the device/hardware layer.

## What Stays Here

One fact genuinely belongs to this pack, not `skill-cambium`: any Cambium asset-register work must use ansible-wifi's own `site_name` (`inventories/<flavour>/group_vars/<site>.yml`) as the canonical
site identifier — e.g. `hope-vale`, `burringurrah` — not a register's own display name. That's the ansible-wifi join point, which is this pack's concern. See `01_overview.md` for how ansible-wifi
organizes its site inventories.
