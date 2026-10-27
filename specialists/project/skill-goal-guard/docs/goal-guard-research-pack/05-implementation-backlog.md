---
Title: GoalGuard Implementation Backlog
Category: backlog
Status: proposed, not decided
Authority: research proposal; item IDs GG-01..GG-19 are backlog items, not GG-0xx tests
Scope: Sprints A-D for Codex/Claude Code with release gates
Last reviewed: 2026-10-27
Summary: Ordered backlog from decision engine to agent observation, visualisation and autonomy, with Thekedar reuse as acceptance subtasks.
---
# Prioritized implementation backlog for Codex / Claude Code

Work **strictly in this order** and stop at each release gate. The skill and CLI are the product; the tool should not reinvent project management software.

## Sprint A: first usable decision engine

- [ ] `GG-01`: write `goal-contract.schema.json` including version, goal, exclusions, finish criteria, deadline types; validate two long projects and one ad-hoc job.
- [ ] `GG-02`: task/milestone schema and globally unique IDs; dependency cycle test.
- [ ] `GG-03`: update classifier interface: record proposed action, criterion, why necessary, smallest viable step, stop condition, evidence refs.
- [ ] `GG-04`: deterministic `validate` and `assess` return stable JSON with `PROCEED/PARK/REVIEW/BLOCK` plus explanation.
- [ ] `GG-05`: `what-next --task`, `--project`, `--portfolio`: return exactly one next action or explicit no-action reason.
- [ ] `GG-06`: golden tests including necessary reliability repair and non-essential future-proofing.
- [ ] **Gate:** execute pilot manually on UNC + SMC. Do not continue until useful.

## Sprint B: agent observation

- [ ] `GG-07`: SQLite authoritative state and immutable decision log; migration and backup.
- [ ] `GG-08`: single trusted writer with task revision check and idempotent event ID.
- [ ] `GG-09`: Claude Code hook adapter; first advisory, blocking only with reviewed test cases.
- [ ] `GG-10`: Codex hook adapter; verify actual locally installed hook support and payload schema.
- [ ] `GG-11`: session interruptions, task handoff and evidence capture.
- [ ] **Gate:** verify crash, parallel write, prompt-injection, and false-positive behavior.

## Sprint C: visualization

- [ ] `GG-12`: deploy isolated Vikunja; capture live OpenAPI schema/version.
- [ ] `GG-13`: define ID mapping, priorities, parent/blocking edges, labels.
- [ ] `GG-14`: one-way projector with dry-run and reconciliation.
- [ ] `GG-15`: saved cross-project views and dashboards.
- [ ] `GG-16`: webhook HMAC receiver + polling reconciliation.
- [ ] **Gate:** duplicate and conflicting sync tests pass.

## Sprint D: autonomy

- [ ] `GG-17`: periodic deterministic overdue/stalled/milestone review.
- [ ] `GG-18`: optional separate semantic scope critic using existing authorized model backend.
- [ ] `GG-19`: concise weekly portfolio report: goals, single focus, each project's next, exception/decision queue.
- [ ] **Gate:** owner approves action before any protected mutation.

## Out of scope until a need is established

- Custom SPA/dashboard, swarm executor, agent model router, advanced planning AI, integration with every MCP, cloud service, probabilistic project forecasting, or full resource-management suite.

## Benchmark question at every sprint review

> Did this change make it easier to finish an accepted deliverable, or did it merely add new capabilities to GoalGuard?

If the answer is the latter, park it.

## GoalGuard v0.2 targeted Thekedar reuse (inside existing tasks)

**No new sprint and no new standalone work items.** The following are *acceptance subtasks* of the IDs above; see [06-Thekedar-Extraction-Matrix.md](06-thekedar-extraction-matrix.md) for upstream exact paths and regression IDs.

- **GG-01/02/03:** Borrow the explicit **objective / in scope / NOT in scope / acceptance criteria** task-writing discipline, without making Git or file lists mandatory for infrastructure/ad-hoc
  tasks.
- **GG-04:** Extend scope assessment beyond allowed file paths. A feature inside an allowed file that does not advance a verified MVP criterion must be `PARK`/`REVIEW`. Task self-edits cannot
  authorize material scope changes.
- **GG-06:** Port canonical-path, symlink/unknown, traversal, unsafe-scope-addition and no-active-task counterexamples from Thekedar's scope tests into GoalGuard regression fixtures. Separate
  observation from approval.
- **GG-07/08:** Extend the single-writer journal with facts-only event provenance, idempotency, task revision and leases. This closes Thekedar's documented multi-session race hazard.
- **GG-09/10:** Add terse SessionStart snapshots, advisory pre-edit checks and safe installation/rollback for Claude and Codex. **Capture live provider payload fixtures; do not assume Codex
  `apply_patch` exposes `file_path`.**
- **GG-11:** Generate task completion records listing changed and deliberately unchanged work; attribute Git changes from task-start baseline (not raw current `git status` alone), or use non-code
  evidence for infrastructure work. Enforce bounded retries.
- **Gate for Sprint A/B:** Run GG-401–425 **as applicable by release gate** in the existing [acceptance matrix](03-acceptance-test-matrix.md). The original 44 scenario specifications remain; new tests are additive specifications,
  not passes.

**Explicit exclusion:** do not install or fork Thekedar's multi-agent orchestrator, duplicate its security scanner, launch additional reviewers on every task, or add a new management dashboard as part
of this reuse.
