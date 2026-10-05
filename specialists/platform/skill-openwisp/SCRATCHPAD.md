# SCRATCHPAD

Agent working memory for skill-openwisp.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-10-05 from memory-keeper + mcp-project-context + claude-mem -->

## Current state

**Phase:** released pack, latest release heading in [CHANGELOG.md](CHANGELOG.md); governance scaffold bootstrapped 2026-10-05.

Standalone, cross-project OpenWISP pack (operator decision 2026-10-01: separate evolving skills, not sections of skill-smc or skill-cambium). Built guidance-only at 0.1–0.2,
version-matched cookbook and tested write-back contract at 0.3.0, then 0.4.0 on 2026-10-05 from an independent assessment: new focused references and promoted stdlib helpers with
tests. The skill-ai-it governance layer (navigation, context map, justfile, governance checker) was added on 2026-10-05.

---

## Open items

- [ ] Live, version-pinned behavioural probes on a disposable install — `compatibility.yaml` rows above `observed_install` stay `pending_live_test` until then (handoff 2026-10-02).
- [ ] Full client evaluation matrix (Claude Code with authentication, Codex) per [tests/eval-procedure.md](tests/eval-procedure.md); release claims stay PARTIAL until it runs.
- [ ] skill-ai-it template drift (fix in skill-ai-it, not here): its `context-map.yaml` template lacks `skill_ai_it_version` and `update_rules.governance_navigation`
  (validator warns on a fresh bootstrap); template block markers are one line where the builder writes two; the governance-checks block exceeds 200 columns; the upgrader
  re-dumps `context-map.yaml` (drops comments) and appends a generic CHANGELOG heading.
- [x] 6 `.archcore/` documents accepted by the operator 2026-10-05 — index [.archcore/index.guide.md](.archcore/index.guide.md).

---

## Key anchors

| Item | Detail |
|---|---|
| Install | `~/.claude/skills/skill-openwisp` is a symlink to this folder |
| Observed version | OpenWISP 26.09.0 images with Controller/Monitoring/Notifications 1.3 (observed install; see `compatibility.yaml`) |
| Memory channel | memory-keeper `openwisp` (exact name, USER_STATED) |
| Origin project | unified-network-controller — design reports under its project-reviews reports folder |
| Gate | `just test` then `just check` |

---

## Recent decisions

- 2026-10-01 — Independent pack, guidance-only at first; capability search order provider → supported extension → other FOSS → scratch (USER_STATED).
- 2026-10-05 — `scripts/` admitted for tested, stdlib-only helpers; the contract requires each helper to be tested.
- 2026-10-05 — Governance checker runs inside `tests/test_helpers.py`, so the existing test run is also the governance gate.
- 2026-10-05 — `AGENTS.md` force-added to git (operator); the repo's git info/exclude file keeps ignoring it repo-wide, so every later edit needs `git add -f`.
- 2026-10-05 — `/skill-ai-it promote` for all candidates: 2 ADRs, 3 rules, 1 plan; candidates queue deleted. Operator accepted all 6 the same day.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-10-05 (~19:25–19:36) — collision merge, promote, accept, commit

- A parallel UNC session overwrote the `justfile`; merged its `helpers`/probe recipes into the skill-ai-it justfile; it promoted 5 helpers from UNC and catalogued them.
- Promoted all candidates (2 ADRs, 3 rules, 1 plan) and the operator accepted all; `AGENTS.md` force-added; committed and pushed with skill-cambium.
- Evidence basis: memory-keeper keys `platform-packs.justfile-collision.20261005_1930`, `nautobot.archcore-promote.20261005`, `platform-packs.slurp.20261005`.

### 2026-10-05 — skill-ai-it bootstrap

- Added README, AGENTS, CLAUDE, AI_NAVIGATION, context-map, justfile, .mise.toml, scripts/README, governance checker, Repomix config; `archcore init`.
- Evidence basis: this CHANGELOG `## Unreleased` line.

### 2026-10-05 — 0.4.0 from an independent assessment

- New references and promoted helpers; capture-corpus fleet lessons as Learned entries.
- Evidence basis: claude-mem observations 2026-10-05; CHANGELOG 0.4.0.

### 2026-10-01/02 — 0.1.0 → 0.2.0 operational revision

- Claims, scenarios, package contract; operational depth; no runnable helpers then.
- Evidence basis: memory-keeper key `unc-platform-skills-0-2-0-posthook-handoff-20261002`.

---

## Next actions

- Run the disposable live probes and the client matrix (`.archcore/plans/live-probes-then-client-matrix.plan.md`) before widening release claims.
- Report the skill-ai-it template drift above into skill-ai-it's own SCRATCHPAD/CHANGELOG.

---

## Memory pointers (navigation only — content is above)

- memory-keeper channels: `openwisp`, `unc` / keys: `openwisp.skill-v01-frozen-spec.20261001_1724`, `unc.nautobot-openwisp-skill-operator-contract.20261001_1724`,
  `unc-platform-skills-0-2-0-posthook-handoff-20261002`
- project-context: no dedicated project; nearest are `unified-network-controller` and `skills_stuff`
- memory-keeper (this session): `nautobot.governance-bootstrap.20261005_1602`, `openwisp.governance-bootstrap.20261005_1602`,
  `platform-packs.justfile-collision.20261005_1930`, `nautobot.archcore-promote.20261005`, `platform-packs.archcore-promote.20261005`, `platform-packs.slurp.20261005`
- checkpoints: `slurp-20261005-platform-packs-governance` (memory-keeper and project-context)
- claude-mem: results found (observations 2026-10-01 and 2026-10-05)
