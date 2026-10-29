---
Title: skill-network-architect scratchpad
Category: working-memory
Status: current
Authority: local-supplement
Scope: Current state and next actions for the skill-network-architect pack
Last reviewed: 2026-10-29
Summary: Where the pack stands and what to do next. Overwrite the state section each session; keep it short.
---

# SCRATCHPAD

## Current state (2026-10-29)

- v2.0.0: adopted into skills_stuff conventions, every reference and template deepened, source-checked and restructured; local source store and
  ledger in place; `just check` passes. Not yet committed or installed (symlink install pending operator go-ahead).
- Behavioural eval rerun 2026-10-29 with and without the skill: see evals/results.md.

## Next actions

1. Operator review, then commit and symlink-install both packs (~/.claude/skills, ~/.agents/skills).
2. Act on the gap list in evals/results.md (Proxmox/product-lookup routing gap, templates without filled worked examples, references over 180 lines).
3. Rerun `just links` and `just fetch-sources --apply` before each release; `just ledger --apply` after any new citation.
4. Gaps from the 2026-10-29 eval and reviews: routing pulls 3-6 whole modules per case (consider split modules or section anchors in the routing
   table); no throughput-from-PHY rule for radio links; no BGP edge-policy checklist per peer or EVPN fabric build sheet template; no fibre
   loss-budget or PoE/UPS budget helper; Wi-Fi survey and PtP link acceptance records; 2025 LIPD upper-6 GHz inclusion still UNVERIFIED.
5. Six references exceed 180 lines (routing-and-switching 233 the largest); trim only by moving tables into templates, not by cutting facts.
