---
Title: skill-systems-architect scratchpad
Category: working-memory
Status: current
Authority: local-supplement
Scope: Current state and next actions for the skill-systems-architect pack
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
4. Gaps from the 2026-10-29 eval and reviews: restore-only helper (capacity_check needs nodes) and per-phase restore timing; FOSS MDM options
   (NanoMDM, MicroMDM, Fleet) and osquery licence; LLM inference sizing (KV cache, tokens/s, time to first token); PostgreSQL HA (Patroni,
   streaming replication) reference; EOL register checker script; DR runbook and restore-drill record template; replace eval cases S01/S02,
   which reuse worked-example numbers.
5. References run 190-243 lines; trim only by moving tables into templates, not by cutting facts.
