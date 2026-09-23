# Device-Inventory Schema

## Contents

- [Purpose](#purpose)
- [Column Contract](#column-contract)
- [UNKNOWN Discipline](#unknown-discipline)
- [Cross-Site IP Collisions Are Normal](#cross-site-ip-collisions-are-normal)
- [Building or Refreshing an Extract](#building-or-refreshing-an-extract)

---

## Purpose

`cambium-swap/inventory/device-inventory.csv` is the canonical per-device export — one row per physical device, device-access fields only. As of 2026-09-17 it holds 143 rows seeded from the two site
asset registers (see `03_asset-register-conventions.md`); it is **not yet** a real cnMaestro export.

## Column Contract

`serial_msn, mac_address, model, product_family, hardware_revision, current_firmware, previous_known_good_firmware, management_ip, site, smc_flavour, network, tower_site_hierarchy, device_name,
device_role, topology_role, wlan_profile, ap_group, configuration_template, cloud_sync_status, cnmaestro_server, licence_tier, licence_state, licence_expiry, local_credentials_ref, last_seen, status,
spare_mapping, export_date`

Key columns to get right:
- `mac_address` for an **ePMP AP** is the unit's **LAN MAC** (`device_props.cambiumLANMACAddress`, the adapter's `lan_mac_address`), not its wireless MAC. VERIFIED_PRIMARY 2026-09-23:
  the device-reported LAN MAC equalled the register's `mac_address` on six ePMP 3000L APs at hope-vale, mornington and horn-island (unified-network-controller identity canary), and the
  register's `serial_msn` and `current_firmware` matched `cambiumEPMPMSN` and `cambiumCurrentuImageVersion` on all six. Other families' MAC column semantics are not established by this.

- `site` — ansible-wifi `site_name` slug (`hope-vale`, `burringurrah`), not a display name. See `03_asset-register-conventions.md`.
- `smc_flavour` — `nbn_accelerate` or `rcp`, matching the asset-register source directory / ansible-wifi inventory flavour.
- `product_family` — must match `device-family-matrix.csv`'s `family` column exactly (`Enterprise Wi-Fi`, `cnPilot R-series`, `ePMP AP`, `ePMP SM`, `cnWave 60 GHz`) so the two files join cleanly.
- `local_credentials_ref` — `<secret:keepassxc:cambium-devices/<entry>>`, assigned from the family→vault mapping in `02_device-access-and-vault.md`, never from anything the register itself carries
  (registers never record device-access values).

## UNKNOWN Discipline

Fields the source register doesn't carry — most `serial_msn`, `firmware`, `hardware_revision`, `licence_*`, `cnmaestro_server`, `last_seen` — are `UNKNOWN`. **Never guess a value to fill a gap.** This
is inherited from `cambium-swap`'s own `inventory/readme.md` rule and applies to this pack's guidance too.

## Cross-Site IP Collisions Are Normal

Each site runs its own isolated `10.255.x.x` space with no routing between sites — the same IP (e.g. `10.255.3.10`) can legitimately appear at two different sites for two different physical devices.
`site` + `management_ip` together are the key; `management_ip` alone is not unique across the fleet.

## Building or Refreshing an Extract

No general-purpose extraction script exists — `scripts/extract-asset-register.py` in this pack is a worked example for the two sites seen so far (Hope Vale, Burringurrah), not a reusable tool; the two
registers have different enough sheet layouts that its per-site parsing was hand-written, not general. If a register updates or a new site is added, treat that script as a reference for the guardrails
(IPv4 validation, whitespace normalization — see `03_asset-register-conventions.md`), not as something to run unmodified:

1. Read the register's actual sheet/column layout fresh — don't assume it matches a previous site's.
2. Write a per-site extract CSV first (same column contract as `device-inventory.csv`), as a reviewable checkpoint, before touching the canonical file.
3. Validate IPv4-format fields and normalize whitespace in every extracted string (see the extraction gotchas in `03_asset-register-conventions.md`) before folding the extract into
   `device-inventory.csv`.
4. Re-extracting a site that's already in `device-inventory.csv`: remove that site's old rows first (or filter by `site` + latest `export_date`) — folding is a straight append, there's no dedup logic.
