# Changelog

## Unreleased

## 0.3.0 — 2026-10-05

- Added `references/operations-cookbook.md`: twelve version-matched recipes with a summary table (GraphQL, REST, Dynamic Groups, computed/custom fields, Config
  Contexts, Secrets, webhooks/Job Hooks/events, approvals, data validation, permissions and change log, nautobot-server, Jobs, Circuits), cited to the installed 3.2.3
  source; 27 bundled 3.2.3 doc snapshots in `documents/`.
- Replaced the five-file write-back rule with a standing contract: a dated Learned entry plus one CHANGELOG line, checked by the contract test; release reconciliation
  and a version trigger keep the cookbook current.
- SKILL.md: trigger-rich description, cookbook route, project-conventions pointer. Claims N-C18, N-C19; scenarios N-S19 to N-S23; compatibility row for 3.2.3 docs.
- Contract test: snapshots verified from the index table, Learned entries parsed and tied to CHANGELOG lines, cookbook version tied to `compatibility.yaml`, fixed a
  private-address false positive.
- Evaluation 2026-10-05 (Claude Code, Sonnet, fresh contexts): N-S19 and N-S20 passed with the skill; the no-skill controls were partial.

- 2026-10-05 `operations-cookbook.md`: Learned entry, REST create accepts a client-supplied `id` (installed source); found by the skill evaluation.
- 2026-10-05 `authority-and-modeling.md`: Learned entry, deleted built-in Statuses/Roles are not recreated by migrate or post_upgrade (installed source).

## 0.2.0 — 2026-10-01

- Deepened ownership, paging/writer, onboarding, replacement, Wireless Link, Job, backup and upgrade decisions with synthetic failure cases (N-C01–N-C17).
- Split official, implementation, test, synthesis, policy and install evidence; repaired N-C13 → N-S16 and N-C03 → N-S17 links.
- Added scenario N-S16–N-S18, claim/scenario semantic validation and a mixed-primary routing rule. No runnable helpers or runtime install changes.

## 0.1.0 — 2026-10-01

- Added claims N-C01 through N-C17, scenarios N-S01 through N-S15, and the deterministic package contract.
- Recorded the observed Nautobot 3.2.3/application baseline, the version-bounded 3.2 Job source, and local official-documentation snapshots.
- Hardened authority, pagination, staged onboarding, replacement, topology, worker, backup, extension, and upgrade guidance with Phase 1 worked patterns.
- No migrations or retirements.
