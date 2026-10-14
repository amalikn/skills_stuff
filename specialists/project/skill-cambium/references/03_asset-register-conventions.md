# Cambium Device Asset Registers

## Contents

- [What These Are](#what-these-are)
- [Naming Grammar](#naming-grammar)
- [Per-Site Drift — Read the Columns, Not the Name](#per-site-drift--read-the-columns-not-the-name)
- [Site-Name Convention](#site-name-convention)
- [R195P Residential CPE — `rcp`-Only, IP Not in the Register](#r195p-residential-cpe--rcp-only-ip-not-in-the-register)
- [As-Built Sets — Site Drawings Beside the Register (2026-10-13)](#as-built-sets--site-drawings-beside-the-register-2026-10-13)
- [Extraction Gotchas](#extraction-gotchas)

---

## What These Are

Site-maintained Excel workbooks (`inventory/asset-register/<flavour>/<Site Name>.xlsx` in `cambium-swap`, e.g. `nbn_accelerate/Hope Vale Asset Register_V1.2.xlsx`, `rcp/Burringurrah Asset
Register.xlsx`), kept live by field installers through deployment and ongoing maintenance — not authored or templated by any project. No standard template exists across sites; each register grew its
own sheet layout independently. Learned 2026-09-17 extracting device-access data (model, MAC, IP, credential-vault reference) into `cambium-swap`'s `inventory/device-inventory.csv`; see that project's
`inventory/asset-register/readme.md` and CHANGELOG `20260917_1015` for the full extraction detail.

## Naming Grammar

Both registers seen so far bake the device's own IP into its human-readable name: `<SITE>_<MODEL-CODE>_<ROLE-ID>_IP<SUBNET-OCTET>_<HOST-OCTET>`. Example: `HOP_XV2_AP1_IP3_1` = Hope Vale, XV2-series
AP, unit 1, `10.255.3.1`.

## Per-Site Drift — Read the Columns, Not the Name

The naming *idea* is shared but each site applies it with its own drift:

- **Subnet-octet-to-role mapping differs per site — see the table below, not a register or a name.** The register (and the `device-inventory.csv` rows derived from it) can be flat-out wrong about
  which octet a family actually lives on; only a live ARP table + MAC-OUI cross-check is trustworthy. Don't assume an octet means the same thing at a new site without checking.

- **The management address is the one inside `10.255.0.0/18`, whatever the device calls it** (operator, 2026-09-21: "10.255/18 or 19, always"). A device may report it as `device_ip`, as a VLAN500
  interface address, as `ipv4_address`, or among several addresses on a bridge; pick the address in that range, never an address inferred from the device's name. Seen live 2026-09-21 on
  `HOP_XV2_AP1_IP3_1` (hope-vale): `device_ip` 10.255.3.1, mask 255.255.224.0 (a `/19` inside the `/18`), gateway 10.255.0.1, `vlan_id` 500, the VLAN500 interface carrying the same address and every
  other interface `0.0.0.0`. `unified-network-controller` applies this rule in `adapters/estate.py` (`select_management_ip`).

- **For an ePMP unit the register's `mac_address` is the unit's LAN MAC (`cambiumLANMACAddress`) at every site checked, but the SMC's ARP table shows LAN + 1 for its management address**
  (`VERIFIED_PRIMARY` 2026-09-23: hope-vale `HOP_3000L_T1_SecE0_21` LAN `58:C1:7A:79:21:BD`, ARP `…:BE`; `SecW0_22` `…:06:CB` / `…:CC`; every one of 67 ePMP rows at kalumburu matched at ARP MAC =
  register MAC + 1; the kalumburu masters' device-reported `lan_mac_address` equals their register MAC). So a MAC join between register and ARP must try the value and value + 1, and the ARP MAC is the
  management-plane address (bridge side), not the LAN port's. An earlier note here that kalumburu's register held the radio MAC was wrong and is withdrawn. Confirmed on another model 2026-10-14
  (wandawuy, Force 300-25 PtP master and slave): the sweep's ARP MACs `00:04:56:4A:E7:89` and `…:E4:4D` were landed in Nautobot, and OpenWISP registration found the units identify as `…:E7:88` and
  `…:E4:4C` (LAN MAC), so a store of the ARP MAC reads as drift.

### Per-Site IP Addressing Reality

What octet a device family actually answers on, per site — **register/derivation claim** vs **live-confirmed reality** where checked. Consult this before trusting a `management_ip` at a site you
haven't personally verified, and add a row here (with evidence) the first time a new site or family gets checked.

| Site           | Family         | Register/derivation claims      | Live reality (confirmed 2026-09-17)                              | Trust this row?                                               |
| -------------- | -------------- | ------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------- |
| `hope-vale`    | Enterprise     | `10.255.3.x`                    | Confirmed `10.255.3.x` — three physical units live- tested       | Yes — directly verified, not just register-consistent         |
|                |   Wi-Fi (XV2)  |                                 |   (Towers 1, 5, 6) via SSH/REST sessions                         |                                                               |
| `hope-vale`    | ePMP AP        | `10.255.0.x`                    | Confirmed `10.255.0.x` — Tower 1 Omni0 live-tested via an        | Yes                                                           |
|                |                |                                 |   authenticated LuCI-API adapter session                         |                                                               |
| `hope-vale`    | ePMP SM        | `10.255.4.x`                    | Confirmed `10.255.4.x` — Tower 5 live-tested via an              | Yes                                                           |
|                |                |                                 |   authenticated LuCI-API adapter session                         |                                                               |
| `burringurrah` | Enterprise     | Most rows say `10.255.3.x`      | **Resolved (was contradicted).** Real subnet is `10.255.11.x`,   | Yes, since the operator's cnMaestro export reconciliation —   |
|                |   Wi-Fi (XV2)  |                                 |   confirmed via the operator's cnMaestro Cloud export. That      |   `device-inventory.csv` corrected against it. Note:          |
|                |                |                                 |   octet is a **mixed XV2+R195P** cluster (both share the `bc:a9:93` |   `10.255.11.x` is not XV2-exclusive — cross-check hostname   |
|                |                |                                 |   OUI block there)                                               |   or serial, not just OUI, to tell the two families apart     |
| `burringurrah` | ePMP SM        | Most rows say `10.255.21.x`     | **Confirmed.** Live ARP shows the real ePMP fleet (OUI `58:c1:7a`) | Mostly yes — matches live evidence, except the one `.3.11`    |
|                |                |   (one outlier                  |   at `10.255.21.x`, 44 hosts                                     |   outlier row                                                 |
|                |                |   at `10.255.3.11`)             |                                                                  |                                                               |
| `burringurrah` | cnPilot R195P  | `10.255.10.x`                   | **Resolved (was contradicted).** Real subnet is `10.255.11.x`,   | Yes, since the operator's cnMaestro export reconciliation —   |
|                |                |   (`EXT10XX → 10.255.10.XX`     |   confirmed via the operator's cnMaestro Cloud export, shared    |   `device-inventory.csv` corrected against it (also exposed a |
|                |                |   rule — confirmed wrong)       |   with XV2 above                                                 |   row-misalignment bug in the original extraction)            |

**How this table gets built**: from a site's SMC box, `ip neigh show` (ARP table) lists every live host on the management bridge with its MAC; match the MAC's OUI against a family you've already
confirmed elsewhere (XV2 = `bc:a9:93`, ePMP = `58:c1:7a`, per the evidence above) to find where that family *actually* lives, independent of what the register or `device-inventory.csv` claims.

**Machine-readable companion**: [references/site-addressing.yaml](site-addressing.yaml) holds this same data in queryable form (per site, per family: octet pattern, trust state, evidence IDs), plus
the MAC-OUI lookup table, for anything that needs to consult it programmatically rather than read prose. Update both together — this table is the narrative-with-citations version, the YAML is the
lookup version, neither is canonical over the other.
- **The AP-number axis isn't stable**, and some sites layer a second numbering axis for the same physical device. Hope Vale: Tower 25's AP is literally named `AP32` (install-order numbering, not
  tower-order). Burringurrah: the same Force-300 SM is `AP4` in the "Tower + AP" sheet but `EXT1058` (a 4-digit subscriber/extension number) in the per-residence "Internals" sheet — the two numbers
  aren't derivable from each other.
- **The Name field doubles as an informal changelog.** Rename-in-place via `>>` (`BUR_F300-25SM_AP2_IP_3_21 >>BUR_F300-25SM_AP2_IP_21_6` = old name >> new name after a re-IP, sometimes bundled with a
  hardware swap), or free-text notes in an adjacent cell (`'was HOP_F25_AP30_IP4_30 <-- This is wrong'`).
- **Nothing cross-validates name against the actual IP column.** A Hope Vale row had `10.2.55.3.35` (extra dot, a typo) sitting right next to a name that still said `IP3_35`.

**Rule: always read the real `IP`/`MAC`/`Serial Number` columns. Never parse an address back out of the device name** — it's a mnemonic snapshot from whenever it was last (maybe never) kept in sync,
not a live value.

## Site-Name Convention

Use ansible-wifi's `site_name` (from `inventories/<flavour>/group_vars/<site>.yml`) as the canonical site identifier — `hope-vale`, `burringurrah` — not the register's own display name ("Hope Vale",
"Burringurrah Asset Register"). Operator instruction, 2026-09-17: any inventory built from an asset register must use this slug so it joins cleanly against ansible-wifi's own inventory. See
`skill-smc/references/01_overview.md` for how ansible-wifi organizes its own site inventories.

## R195P Residential CPE — `rcp`-Only, IP Not in the Register

Operator-confirmed program-level fact (2026-09-17): **`rcp`-flavour sites carry R195P residential CPE; `nbn_accelerate` sites do not.** Not a coincidence of Hope Vale vs Burringurrah specifically —
treat it as a general rule when a new site's register shows up.

The register's per-residence sheet (Burringurrah: "Internals") never records an IP for the R195P device itself — only a 4-digit extension number (`R195 EXT`) and its MAC. The R195P's management IP is
derived by a rule the operator supplied that is **not written anywhere in either register**: `EXT10XX → 10.255.10.XX` (e.g. `EXT1031` → `10.255.10.31`). Confirmed only against Burringurrah's extension
numbers, all in the 1001–1099 range — re-verify before trusting it at a different `rcp` site or outside that range. The R195P's Force 300 backhaul radio *does* get an IP in the register, under the
same `EXTnnnn`-named entry, in the "Tower + AP" sheet — don't double-count it as a second, IP-less device.

## As-Built Sets — Site Drawings Beside the Register (2026-10-13)

A deployed site may also have an **as-built set** from its build contractor, besides the asset register: first read at old-looma (FNCW - Looma Community, rcp low-touch, version 1.0, drawings
2026-08-03, map 2026-09-01; kept verbatim in unified-network-controller `docs/sites/old-looma/as-built/`).

- **What a set holds:** a central chassis connectivity drawing (SMC, switches, UPS, uplinks with their SMC interfaces, switch ports to the tower radios and APs), one connection drawing per tower
  (radios, mast heights, injectors, power, the tower's XV2 and any wired router), each as draw.io plus PDF; a KMZ (one folder per tower: point, sector and omni coverage shapes, each XV2 and how it is
  fed, the cnWave and PtP links; carries no date); a coverage map (InDesign plus PDF: lot, hardware, power, mast height and AP number per tower, and a hardware glossary). Towers without a drawing
  (old-looma T6-T8) are on the map and KMZ only.
- **Labels:** XV2s are numbered `APn` per tower (the map and KMZ, AP1 at the central tower); 3000L sectors and omnis carry `WifiBridge_n` (with a direction for sectors, e.g. "SouthEast"); `F25` is the
  ePMP Force 300-25 (SM or PtP), `V5000/V3000/V2000` the cnWave units; `CIE`/`CEE` are central internal (SMC plus switches) and external equipment; `SWP n` is a switch port; routers are drawn `R195P
  IAP (Ext XXXX)` with the extension left blank.
- **Read the drawings as text** with unified-network-controller `just wc::asbuilt-read <folder>` (`wc-local/scripts/site_onboarding/asbuilt_read.py`): draw.io pages are deflated base64 XML with HTML
  labels. A drawing's port labels (`SWP n`) are separate boxes beside the line; since 2026-10-14 asbuilt_read also gives each box's position and each line's path, and `just wc::asbuilt-generate --site
  <s>` matches a port to the nearest line (old-looma, wangkatjungka and yakanarra checked against the PDFs: every port right). A line drawn to a picture takes the caption beside it.
- **Known flaws in v1.0:** tower drawings are copied from each other (old-looma T2's drawing carries T3's XV2 and omni labels; the map, KMZ and discovery agree on T2 = AP3); a hardware list can name a
  unit discovery never finds (T4's F25); the KMZ and the map can disagree on mast height and power (T4). Cross-check every drawing against the map and discovery; a corrected set arrives as a new
  version beside the old one, never over it.
- **Seen across seven sets (2026-10-14: beagle-bay, pandanus-park, umoona, wangkatjungka, warburton, yakanarra besides old-looma):** the copied XV2 label recurs (pandanus-park T2 drawn AP2, KMZ AP5;
  wangkatjungka T3 drawn AP3, KMZ AP2); placeholders `AP#` and `EAP` stand for the number; sets often ship drawings as PDF only (beagle-bay towers, umoona and warburton chassis) or no central drawing
  at all; KMZ link text can name the wrong tower ("T1 F25 - T6" drawn T1-T3), a place ("Shop V5000 - Clinic V1000") or a non-tower ("T2B"), and a line can run backwards, so take ends from the line's
  coordinates; towers can be split (warburton 3A/3B, 4A/4B); the map can number routers as APs (warburton AP17-19 are R195s); Force 300-16 SMs feed some towers ("via F16", umoona). The KMZ is the most
  complete source: every set has one, one folder per tower.
- **How it is used:** a deployed site's as-built is the reference for drift against what discovery finds; unified-network-controller holds it per site as `docs/sites/<site>/as-built-reference.yaml`
  (format `unc-as-built/1`) and shows it in Nautobot's As built panel.

## Extraction Gotchas

Two real bugs caught while building `cambium-swap/inventory/device-inventory.csv`, worth checking for at any future site:

1. **Cross-reference placeholders masquerading as devices.** A row's backhaul link can say `"As above"` instead of a real name/IP (Hope Vale "Tower 27 Ext", reusing Tower 27's own radio). Blindly
   copying that literal string into a device record creates a phantom device. Validate the value looks like an IPv4 address before treating a link-derived field as a new device.
2. **Embedded whitespace/newlines inside a cell.** A Burringurrah MAC-address cell had a trailing newline baked into the string, corrupting the CSV row it was written into. Normalize every extracted
   string value (`" ".join(v.split())`) before writing it out.
