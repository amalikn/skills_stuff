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

## Current state (2026-10-29, closeout)

- v2.2.0: research-deepened, source-checked references on one backbone; 21 references, 19 templates with filled examples, 11 helpers;
  local source store (519 items) and sources.json ledger; APN operator context in operator/apn/ (index plus four files).
- Evals: skill 22/22 against a baseline, and 22/22 against a fair baseline given the specialist registry (12.71 vs 9.75).
- Committed in skills_stuff up to b6f399f (concurrent session's commit carried this session's files); push pending (operator).

## Next actions

1. Operator: `git -C /Volumes/Data/_ai/_skills/skills_stuff push origin main` (auto mode refused the agent's push).
2. Verify the open items: nbn maximum frame sizes for RFC 4638, whether the POI count changed since 2012, carrier-side STIR, PRI format.
3. Rerun `just links` and `just fetch-sources --apply` before each release; `just ledger --apply` after any new citation.
4. Next eval: run the trigger set live in a fresh session (not only the description proxy).
