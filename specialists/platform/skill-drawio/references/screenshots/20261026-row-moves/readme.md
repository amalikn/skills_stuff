---
Title: Screenshots - End-to-end row moves and right-hand in-column links, 2026-10-26
Category: reference
Status: current
Authority: local-supplement
Scope: Evidence for the Learned 2026-10-26 entries "End-to-end row moves" and "End-to-end in-column links on the right" in references/layout-and-routing.md
Last reviewed: 2026-10-26
Summary: ansible-wifi smc_change E2E pages after row moves and the right-hand in-column rule landed (role internals only, no site names or addresses).
---

# Screenshots: End-to-end row moves and right-hand in-column links

Exported with the draw.io desktop CLI (`-p 3` and `-p 4`, `-s 1.2`) from ansible-wifi `roles/smc_change/drawio/flows.drawio` on 2026-10-26, after `flowmap.crossing_search.row_move` and the right-hand
in-column rule landed. Role internals only: no site names, addresses, MACs or serials.

| Image          | What it shows                                                                                                                                                   |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `flows-p3.png` | `E2E: PHP CVE-2026-109618`: 1.1 (Wi-Fi user) runs along the portal's row into its lower port, 5.1 (role) drops into the upper port; no crossing (page 22 -> 21) |
| `flows-p4.png` | `E2E: etc-hosts-hostname`: SMC-to-SMC links (1.2, 2.2, 2.3, 5.2) and the dashed line to Change spec in the SMC column's new right-hand channel (page 15 -> 8)   |
