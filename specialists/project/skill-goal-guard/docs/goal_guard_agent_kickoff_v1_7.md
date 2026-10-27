---
Title: GoalGuard v1.7 Coding Agent Kickoff
Category: agent-kickoff
Status: current
Authority: operator instruction for the pilot; derives from the v1.7 handoff
Scope: First end-to-end GoalGuard enforcement pilot in project_stuff/apn
Last reviewed: 2026-10-27
Summary: Ordered tasks, stop conditions and completion gate for one hub milestone, one spoke, one Vikunja link, one agent adapter and one snapshot/restore proof.
---
# GoalGuard v1.7 — Coding Agent Kickoff

Use [`goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md`](goal_guard_mvp_delivery_policy_agent_handoff_v1_7.md) as the proposed design handoff. Version 1.6 supersedes v1.5 for this assignment.

## Objective
Implement the **smallest verified end-to-end GoalGuard enforcement pilot** in the existing workspace: one Enterprise-Strategy milestone; one APN spoke project; one Vikunja linkage; one actual Codex
*or* Claude Code enforcement adapter; one approved MVP, one allowed action, one blocked out-of-scope action.

## Non-negotiable boundaries
- Root is **`project_stuff/`**, with sibling `APN/` and `me/`. Preserve names and existing directory structure; inspect actual absolute path and repository layout.
- **Enterprise-Strategy** remains hub; UNC and SMC Resiliency are spokes. Do not infer their actual disk folder spellings.
- GoalGuard owns delivery governance and scope approvals; Vikunja owns live tasks/priorities; Archcore owns technical rules; Knowledge Curator owns Markdown knowledge extraction only.
- `.gg/` per-project layout is a **proposal**, not permission to scatter files or create a parallel planning database. First inspect existing conventions and report any conflicts.
- Preserve protected management baseline and issued Excel. Keep separate internal target and forecast; do not silently change committed dates.
- Do not install tools, change all repositories, migrate all milestones, or build dashboards during pilot.

**Existing project maps:** Before designing `.gg/`, inspect the actual `target-map` convention and `code-map.toml` under each pilot project. Treat `target-map` as the existing target catalog (not
automatic authorization) and `code-map.toml` as the scripts index. Do not invent schemas, move files, or auto-write either map. Demonstrate one target → approved MVP criterion → Vikunja task trace, or
report REVIEW if mapping cannot be safely established.

## Ordered tasks
1. Inventory `target-map` and `code-map.toml` locations, formats, ownership and existing generators; then inventory installed GoalGuard skill/prototype, existing skill placement, `.gg/` conflicts,
   `.archcore/`, `AGENTS.md`, Git boundaries, canonical data/cache policy, Vikunja API/version, existing hub plan and management export.
2. Produce a compact **current → proposed** hierarchy and storage table with exact physical paths and owned files. Identify already-supported hooks and whether they actually block on failure.
3. Propose the minimal changes needed for one pilot and request owner authorization for scope-affecting edits. Reuse existing policy package and project files wherever possible.
4. Implement and test one end-to-end flow: read current approved MVP + hub decision + Vikunja task; PROCEED in-scope work; PARK/REVIEW/BLOCK out-of-scope work; record auditable evidence.
5. Trace one approved baseline milestone to Vikunja, its separate internal target, and one management Excel sample, without replacing original evidence.
6. Return PASS/FAIL results for applicable v1.7 acceptance tests, including M01–M08, exact changes, unsupported paths, rollback and follow-up recommendation.

## Completion gate
Do **not** claim enforcement exists because a skill, instruction file or hook configuration was written. Show a real, observed allowed action and real observed blocked action. If technical constraints
prevent strict blocking, declare the pilot PARTIAL and explain the gap instead of simulating a PASS.

## Stop conditions
Pause the affected modification on conflicting ownership, stale hub baseline, inaccessible task authority, unapproved schema migration, cross-portfolio data access, or insufficient protection of
management commitments. Continue independent read-only inspection and report blockers.


## Additional v1.7 scope — portable recovery proof
- Inspect current filesystem and `.gg/` naming conflicts before creation.
- Produce a single pilot project snapshot plus a parent manifest, retaining last-known-good data.
- Validate export completeness/checksums, offline read-only retrieval, and idempotent dry-run/restore to a clean test target.
- Document exact data not captured (such as attachments, user accounts, instance config), and separate project portability from full Vikunja disaster recovery.
- Keep `target-map` and `code-map.toml` read-only until ownership/schema are established.
- Stop after one project and one restore proof; do not expand all project hierarchies automatically.
