---
Title: MikroTik vendor sources (RB450Gx4, Metal 52 ac, RouterOS 7.8 to 7.24.5)
Category: reference
Status: current
Authority: vendor-source
Scope: Verbatim vendor pages, MIB files, datasheets and changelogs backing the skill-mikrotik SNMP OID registry and hardware facts
Last reviewed: 2026-10-07
Summary: >-
  Raw evidence folder. MikroTik MIB for RouterOS 7.8 and 7.24.5, help.mikrotik.com pages (SNMP, Ethernet, Bridging, RouterBOARD, Device-mode, Health, Packages, WiFi), product pages and PDFs,
  concatenated RouterOS changelogs 7.8 to 7.24.5, and three community forum threads (secondary) on the cpu-frequency warning.
---

# MikroTik vendor sources

All files were retrieved on 2026-10-07 without logging in to any device. Text files (`.txt`) carry the page text only; the first line of each is its source URL. Files under `mib-*/` named
`mikrotik.mib` are byte-for-byte downloads. The two `mikrotik-mib-oid-index.tsv` files are derived (object name resolved to numeric OID by a stdlib parser) and are not vendor files; the `.mib` beside
them is the authority. Forum threads are secondary sources: the `forum-staff` / `moderator` flags are Discourse forum roles, not proof of MikroTik employment.

Current RouterOS channels on the retrieval date: stable 7.24.5, long-term 7.23.7 (from the `NEWESTa7.*` files).

All retrieved 2026-10-07.

Firmware binaries (RouterOS 7.8, 7.12.2, 7.23.7, 7.24.5 for arm and mipsbe, added 2026-10-08) are not in this folder: they are in the pack's `firmware-files/<version>/`,
indexed with size, sha256 and source URL in [../firmware-manifest.yaml](../firmware-manifest.yaml).

- `mib-7.8/mikrotik.mib`: MIKROTIK-MIB shipped for RouterOS 7.8 (LAST-UPDATED 202112210000Z), as downloaded Source: https://download.mikrotik.com/routeros/7.8/mikrotik.mib.
- `mib-7.8/mikrotik-mib-oid-index.tsv`: Derived: every object in the 7.8 MIB with resolved numeric OID, syntax, status (not a vendor file) Source: derived from `mib-7.8/mikrotik.mib`.
- `mib-7.24.5/mikrotik.mib`: MIKROTIK-MIB for current stable RouterOS 7.24.5 (LAST-UPDATED 202607070000Z), as downloaded Source: https://download.mikrotik.com/routeros/7.24.5/mikrotik.mib.
- `mib-7.24.5/mikrotik-mib-oid-index.tsv`: Derived: every object in the 7.24.5 MIB with resolved numeric OID, syntax, status (not a vendor file) Source: derived from `mib-7.24.5/mikrotik.mib`.
- `NEWESTa7.stable`: RouterOS upgrade-server pointer: current stable version and build epoch (7.24.5) Source: https://upgrade.mikrotik.com/routeros/NEWESTa7.stable.
- `NEWESTa7.long-term`: RouterOS upgrade-server pointer: current long-term version and build epoch (7.23.7) Source: https://upgrade.mikrotik.com/routeros/NEWESTa7.long-term.
- `ros-snmp.txt`: RouterOS manual: SNMP (enable, communities, v1/v2c/v3, used MIBs list, print oid, traps, SNMP write) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/8978519/SNMP.
- `ros-health.txt`: RouterOS manual: Health (voltage reported as dV and temperature x10 over SNMP) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/25690117/Health.
- `ros-ethernet.txt`: RouterOS manual: Ethernet (mac-address, orig-mac-address, reset-mac-address) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/8323191/Ethernet.
- `ros-bridging-and-switching.txt`: RouterOS manual: Bridging and Switching (auto-mac, admin-mac) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/328068/Bridging+and+Switching.
- `ros-routerboard.txt`: RouterOS manual: RouterBOARD (cpu-frequency setting, routerboard settings) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/40992878/RouterBOARD.
- `ros-device-mode.txt`: RouterOS manual: Device-mode (routerboard feature gates /system routerboard settings) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/93749258/Device-mode.
- `ros-packages.txt`: RouterOS manual: Packages (wireless vs wifi-qcom-ac architectures) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/40992872/Packages.
- `ros-wifi.txt`: RouterOS manual: WiFi (new wifi menu, wifi-qcom-ac driver scope) Source: https://help.mikrotik.com/docs/spaces/ROS/pages/224559120/WiFi.
- `routeros-changelogs-7.8-to-7.24.5.txt`: Concatenated per-version CHANGELOG files, 7.8 through 7.24.5 (77 versions) Source: https://download.mikrotik.com/routeros/<version>/CHANGELOG (index: https://mikrotik.com/download/changelogs).
- `product-rb450gx4.txt`: Product page text: RB450Gx4 description, specifications, test results Source: https://mikrotik.com/product/rb450gx4.
- `product-rbmetalg-52shpacn.txt`: Product page text: Metal 52 ac (RBMetalG-52SHPacn) description, specifications, wireless and test results Source: https://mikrotik.com/product/RBMetalG-52SHPacn.
- `RB450Gx4_180549.pdf`: RB450Gx4 product brochure (1 page) Source: https://cdn.mikrotik.com/web-assets/product_files/RB450Gx4_180549.pdf.
- `RB450-DIM-v1_210803.pdf`: RB450 series mounting dimensions drawing Source: https://cdn.mikrotik.com/web-assets/product_files/RB450-DIM-v1_210803.pdf.
- `metal_52_ac_190120.pdf`: Metal 52 ac product brochure (2 pages) Source: https://cdn.mikrotik.com/web-assets/product_files/metal_52_ac_190120.pdf.
- `metal-52ac_200303.pdf`: Metal 52 ac user manual / quick guide (15 pages) Source: https://cdn.mikrotik.com/web-assets/product_files/metal-52ac_200303.pdf.
- `forum-warning-cpu-not-running-at-default-frequency-144298.txt`: Forum thread (secondary): "Warning: cpu not running at default frequency". Source: https://forum.mikrotik.com/t/warning-cpu-not-running-at-default-frequency/144298.
- `forum-rbcapgi-5acd2nd-cpu-not-running-at-default-frequency-178422.txt`: Forum thread (secondary): cAP ac cpu frequency warning, moderator answer. Source: https://forum.mikrotik.com/t/rbcapgi-5acd2nd-cpu-not-running-at-default-frequency/178422.
- `forum-cannot-change-back-the-cpu-frequency-181656.txt`: Forum thread (secondary): cpu-frequency vs device-mode in 7.17+, warning semantics. Source: https://forum.mikrotik.com/t/cannot-change-back-the-cpu-frequency/181656.
- `readme.md`: This index Source: n/a.

