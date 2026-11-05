---
Title: Screenshots - an edge through the notes band passes the audit, 2026-11-06
Category: reference
Status: current
Authority: local-supplement
Scope: Evidence for the Learned 2026-11-06 entry in references/layout-audits.md (Limits)
Last reviewed: 2026-11-06
Summary: >-
  smc-resiliency flow page "4. VM: render site config from identity" (a lab VM flow, no site names or addresses), rendered with skill-drawio on
  2026-11-06: once with the defect, once after the map's step order was corrected.
---

# Screenshots: an edge through the notes band passes the audit

| File | Shows | Rendered at |
| --- | --- | --- |
| `audit-clean-edge-through-notes.png` | The decision's red "No" edge to step 10 runs below the lanes and across note cards 2 to 9, through their text; `render_flowmap.py --audit` reported "clean" on this page | Repro of the map before the fix (steps hold and recheck listed last), rendered from a working-cache copy, 2026-11-06 |
| `fixed-by-step-order.png` | The same flow with hold and recheck listed right after the decision: the "No" edge is a short hop inside the lanes | smc-resiliency `docs/flows/drawio/smc-resiliency-flows.drawio` page 15, 2026-11-05 (apn 1dc80235) |
