---
Title: Screenshots - joint port-and-track moves, 2026-10-26
Category: reference
Status: current
Authority: local-supplement
Scope: Evidence for the Learned 2026-10-26 entry "joint moves in the End-to-end search" in references/visual-style.md
Last reviewed: 2026-10-26
Summary: ansible-wifi smc_change E2E pages after the joint-move search (role internals only, no site names or addresses).
---

# Screenshots: joint port-and-track moves

Exported with `scripts/drawio_export.py --scale 1` (draw.io desktop 32.5.5) from ansible-wifi `roles/smc_change/drawio/flows.drawio` on
2026-10-26, after `flowmap.crossing_search` landed. Role internals only: no site names, addresses, MACs or serials.

| Image | What it shows |
| ----- | ------------- |
| `flows-p2.png` | `E2E flow`: 72 crossings before, 24 after (`scripts/count_crossings.py --page 2`) |
| `flows-p3.png` | `E2E: PHP CVE-2026-109618`: 1.2 and 1.3 (role to Live root and back) nested, no crossing; 29 crossings before, 20 after |
