---
Title: Changelog
Category: change-log
Status: current
Authority: record
Scope: Dated changes to skill-pad
Last reviewed: 2026-11-10
Summary: Newest entries only; older ones rotate to docs/history (just history <term>).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261120_1813
---

# Changelog — skill-pad

## Contents

- [20261120_1812 — pad_retry.sh and just pad: single calls retry while the shared server rate-limits (operator, option 3)](#20261120_1812--pad_retrysh-and-just-pad-single-calls-retry-while-the-shared-server-rate-limits-operator-option-3)
- [20261120_1811 — Learned: list hides done items, stdin for bulleted bodies, rate limits](#20261120_1811--learned-list-hides-done-items-stdin-for-bulleted-bodies-rate-limits)
- [20261120_1744 — pad_decisions reads an architecture document's Key decisions; pad_links links register ids; workspace rename is name-only](#20261120_1744--pad_decisions-reads-an-architecture-documents-key-decisions-pad_links-links-register-ids-workspace-rename-is-name-only)
- [20261120_1647 — pad_links: item references as links, dependencies as typed relations (operator)](#20261120_1647--pad_links-item-references-as-links-dependencies-as-typed-relations-operator)
- [20261120_1420 — Work visible in Pad; Pad consulted at session start; smc-resiliency decisions](#20261120_1420--work-visible-in-pad-pad-consulted-at-session-start-smc-resiliency-decisions)
- [20261120_1417 — Rule: work in Pad shows as active](#20261120_1417--rule-work-in-pad-shows-as-active)
- [20261120_1408 — pad_decisions joins wrapped rows and reads status; decisions are a standard setup step](#20261120_1408--pad_decisions-joins-wrapped-rows-and-reads-status-decisions-are-a-standard-setup-step)
- [20261120_1355 — Hub workspace set up: baseline without pad-owned-trackers, asks first](#20261120_1355--hub-workspace-set-up-baseline-without-pad-owned-trackers-asks-first)
- [20261120_1347 — Asks collection created in smc-resiliency; 0.21.1 flag form and workspace-wide refs](#20261120_1347--asks-collection-created-in-smc-resiliency-0211-flag-form-and-workspace-wide-refs)
- [20261120_1334 — Pad CLI 0.21.1 installed; no behaviour change seen](#20261120_1334--pad-cli-0211-installed-no-behaviour-change-seen)
- [20261120_0300 — Tracker export: an item made in Pad renders its title](#20261120_0300--tracker-export-an-item-made-in-pad-renders-its-title)
- [20261119_1849 — Markdown and Pad sync plan; peer sessions consulted](#20261119_1849--markdown-and-pad-sync-plan-peer-sessions-consulted)
- [20261119_1820 — ansible-wifi workspace: adapted conventions file, one workspace for three folders](#20261119_1820--ansible-wifi-workspace-adapted-conventions-file-one-workspace-for-three-folders)
- [20261119_1648 — SKILL.md names installed CLI 0.21.0; --op-key rule names the commands that take it](#20261119_1648--skillmd-names-installed-cli-0210---op-key-rule-names-the-commands-that-take-it)
- [20261119_1631 — Periodic review; 90-day review window](#20261119_1631--periodic-review-90-day-review-window)
- [20261119_1609 — Workspace init from an agent shell; conventions recipe quoting](#20261119_1609--workspace-init-from-an-agent-shell-conventions-recipe-quoting)
- [20261119_1551 — CLI traps from smc-resiliency: octet-stream attachments refused, dash-led comment text](#20261119_1551--cli-traps-from-smc-resiliency-octet-stream-attachments-refused-dash-led-comment-text)
- [20261119_1550 — CLI traps: no attachment delete, comments not in item show, Tech Debt priority](#20261119_1550--cli-traps-no-attachment-delete-comments-not-in-item-show-tech-debt-priority)
- [20261119_1434 — Body layout for every collection: pad_format_spec.py](#20261119_1434--body-layout-for-every-collection-pad_format_specpy)
- [20261119_1325 — Comment edits can be refused by the server](#20261119_1325--comment-edits-can-be-refused-by-the-server)
- [20261119_1136 — Decision-log process rows mirrored to Pad](#20261119_1136--decision-log-process-rows-mirrored-to-pad)
- [20261118_2212 — Tickets tell the whole story: bold labels, updates, a closing statement, logs attached; item-check](#20261118_2212--tickets-tell-the-whole-story-bold-labels-updates-a-closing-statement-logs-attached-item-check)
- [20261118_2200 — A run planned and recorded in Pad with fields set at create](#20261118_2200--a-run-planned-and-recorded-in-pad-with-fields-set-at-create)
- [20261118_2149 — pad_decisions.py and a Decisions schema](#20261118_2149--pad_decisionspy-and-a-decisions-schema)

---

## 20261120_1812 — pad_retry.sh and just pad: single calls retry while the shared server rate-limits (operator, option 3)

- scripts/pad_retry.sh (new), `just pad` recipe, tests/test_pad_retry.py (4 tests: retry then success with stdin replayed, give up at the limit, no retry on success, bad usage); SKILL.md rule; references/cli-reference.md Learned entry on the per-user limiter (server log of 20 Nov); scripts/README.md, code-map.toml. 63 tests OK.

## 20261120_1811 — Learned: list hides done items, stdin for bulleted bodies, rate limits

- references/cli-reference.md: Learned 2026-11-20 from the continuum workspace (pad item list hides done-like items without --all; comment bodies starting with '- ' need --stdin; rate_limited bursts).

## 20261120_1744 — pad_decisions reads an architecture document's Key decisions; pad_links links register ids; workspace rename is name-only

- `scripts/pad_decisions.py`: `--architecture PATH` mirrors the decision bullets of that document's `## Key decisions` section (unc keeps its decisions in ARCHITECTURE.md, not a DL log); refs are register ids (D17, S20, X2) or `ARCH-<slug>`; a status note without DECIDED, SETTLED, RESOLVED, still open or (operator, date) is skipped and listed; items whose ref left every source are listed as orphaned, never changed (a renamed bullet gets a new slug). Tests: `tests/test_pad_decisions.py` Architecture, orphans. unc: 34 decisions mirrored, a re-run plans 0 creates and 0 updates (3.5 s).
- `scripts/pad_links.py`: a mirrored register id (`D17`) becomes `[[DECIS-n|D17]]`; never `D17-03` or `D3.6`. New `tests/test_pad_links.py` (4 tests).
- `references/cli-reference.md` Traps: Learned 2026-11-20, workspace rename is web-UI and name-only (slug read-only); reads are rate-limited too.
- unc workspace brought to the smc-resiliency and continuum layout: Asks and Decisions collections, baseline conventions plus decisions-mirror and progress-record, 52 bodies laid out, links applied.

## 20261120_1647 — pad_links: item references as links, dependencies as typed relations (operator)

- scripts/pad_links.py and `just links`: bare item refs and decision ids in bodies become `[[REF]]` / `[[DECIS-n|DL-058]]` wiki-links; a JSON spec adds typed relations (blocks, implements, split-from, supersedes); plan by default, idempotent. Operator, 2026-11-20 (continuum ASK-251): references must be clickable and dependencies recorded in the relationship section.
- references/items-and-edits.md rule 6 rewritten to require both. First run in continuum: 13 bodies and 13 relations.
- SKILL.md "Tickets tell the whole story" gains the links-and-relations bullet, so every project loads the rule, not only items-and-edits readers.

## 20261120_1420 — Work visible in Pad; Pad consulted at session start; smc-resiliency decisions

SKILL.md Rules: two operator rules (20 Nov 2026). (1) Work is visible in Pad. In a project with a `.pad.toml`, work runs on an item the operator can see: it is found, or created before the work starts
(the operator's request is the confirmation), then claimed, kept `in-progress` with comments, and closed with its `DONE:` comment. The confirm-before-create rule names this exception. (2) Pad is
consulted at session start (`status` mode) in every such project. project_stuff/AGENTS.md now names skill-pad as required there. README step 6: smc-resiliency keeps its decision log at
docs/trackers/decision-log.md (91 decisions on 20 Nov, 1 superseded, built from SCRATCHPAD's Recent decisions, live and rotated). Its commit gate runs `just pad-decisions --apply` non-fatally. Its
check fails on a KEEP decision with no log row (negative test: rc 1 with a row removed). Mirror run time: 29.6 s for 89 creates. SETUP.md re-read against the justfile (ruff lint added in dda2a020),
.mise.toml and `pad --version`: pad 0.21.1 and a ruff row (run through mise, not pinned); Last reviewed 2026-11-20.

## 20261120_1417 — Rule: work in Pad shows as active

- SKILL.md Rules: new rule after "Claim before working an item": work found in Pad is claimed and set `in-progress` before it starts; work not in Pad gets an item created first, then kept current and
  closed with the closing statement (operator, 20 Nov 2026, from the enterprise-strategy hub session; hub items TASK-19, TASK-144, TASK-145 were run this way).
- references/cli-reference.md Traps: a comment message starting with `-` is read as a flag and refused (v0.21.1); use `--stdin`.
- Duplicate removed: a parallel session committed this rule and its own fuller "Work is visible in Pad" rule together (a0fea8bb); this rule's text is dropped and its "a relay, a write-back or a side task counts as work" clause joins the kept rule.
- 20261120_1425: housekeeping exception (operator, 20 Nov 2026): closeout, slurp, skill write-backs, coherence sweeps and staleness audits get no Pad item; "a write-back" dropped from the work clause.
- SKILL.md Rules: "Never add to Pad" lists the housekeeping kinds (closeout and slurps, write-backs, coherence sweeps, staleness audits, record upkeep, sync reports, memory saves, their commits) (operator, 20 Nov 2026).

## 20261120_1408 — pad_decisions joins wrapped rows and reads status; decisions are a standard setup step

scripts/pad_decisions.py: decision-log rows wrapped by the Markdown hook were read as their first line only, so long decisions and reasons reached Pad cut short (continuum DL-001's reason ended at
'a'); table_rows() now joins continuation rows; an optional Status column sets the Pad status (accepted, deferred, rejected, superseded by DL-nnn, named in the body). Test added (3 pass). continuum:
its next pad_decisions run updates 5 items to full text. README setup step 6: a decision log and Decisions collection in every Pad project (operator, 20 Nov 2026: 'this will be standard'); first done
for enterprise-strategy (123 decisions, 7 superseded).

## 20261120_1355 — Hub workspace set up: baseline without pad-owned-trackers, asks first

README.md, Setting Pad up in a project, step 3: a project without bug, feature or tech-debt trackers applies the baseline with --only (pad-owned-trackers left out) and starts with the Asks collection;
learned setting up the enterprise-strategy hub workspace (20 Nov 2026: six conventions, Asks with ASK-11 to ASK-15).

## 20261120_1347 — Asks collection created in smc-resiliency; 0.21.1 flag form and workspace-wide refs

references/cli-reference.md (Traps), Learned 2026-11-20: on 0.21.1 --awaits-human and --tracks-work need the = form (the space form fails with "accepts 1 arg(s), received 2"); refs number across the
workspace (ASK-105 after TASK-104); no collection get. docs/pad-usage-guidelines: the Asks create command corrected. The smc-resiliency workspace now has its Asks collection (operator decision Q1 A,
10 Nov), with ASK-105 and ASK-106.

## 20261120_1334 — Pad CLI 0.21.1 installed; no behaviour change seen

SKILL.md: the installed Pad CLI is 0.21.1 (pad --version, 2026-11-20, build 0d76fda of 2026-11-18). Used from smc-resiliency with no change in behaviour seen: bootstrap, item create with --op-key, and
the pack's item-check (TASK-103 and TASK-104, 0 findings) all worked as on 0.21.0. Learned from the enterprise-strategy slurp close of 20 Nov 2026.

## 20261120_0300 — Tracker export: an item made in Pad renders its title

- scripts/pad_tracker.py `from_pad`: an item created in Pad (its title differs from its body's first line) is rendered with the title as the line and the whole body under it; before, the body's first
  line (`**Serves:** ...`) stood in for the item (smc-resiliency features-to-add, FR-95). Imported items are unchanged. Two tests in tests/test_pad_tracker.py (9 pass; the first fails on the old
  code).

## 20261119_1849 — Markdown and Pad sync plan; peer sessions consulted

Operator asked whether skill-pad has the scripts projects need to work with Pad, whether markdown needs a mapping to Pad items, and for a plan with a reversible script (markdown edited, Pad updated,
markdown regenerated). Three live sessions consulted (smc-resiliency-44, ansible-wifi-47, continuum-32) on sync, revert and script gaps.

- New `docs/pad-markdown-sync-plan-20261119_1845.md` (proposed): one owner per record type, keys in the markdown, sync cycle, journal and revert, conflicts, link checks, script constraints,
  collections review (keep, leave empty, add Asks, Decisions, Risks, Handoffs, Runs), gaps G1-G18, stages S0-S6, decisions D1-D9. Indexed in README and SKILL.md.
- `references/cli-reference.md`: Learned 2026-11-19 (format names per command, `item list` has no body, no `collection show`, what Pad can undo).
- No script added: the probes run were one-off; their reusable logic is planned as padlib (G1) and pad_links.py (G7).
- Pad read only (collections, playbooks, items, history); nothing written to Pad.

## 20261119_1820 — ansible-wifi workspace: adapted conventions file, one workspace for three folders

New `conventions/ansible-wifi.toml`: the apn baseline adapted for a repo without `just commit-project` or `just check` (commit style `<flavor or role>: <summary>`, pathspec commits on rise with
cherry-picks to iridium and master, lint/syntax-check/pre-push ansible-lint gate as the done check, pad-owned-trackers without generated tracker files), applied with `--baseline` to the new
`ansible-wifi` workspace (operator, 2026-11-19). The workspace is linked from three folders, each with its own `.pad.toml`: local-knowledge-ansible/ansible-wifi (tracked), the ansible-wifi company
clone (a symlink to its own real file in ansible-wifi-root-governance, excluded in .git/info/exclude, so a rewrite through the clone never touches the local-knowledge file), and skill-smc inside
skills_stuff, whose nearer `.pad.toml` overrides the skills_stuff root link for that folder only (bootstrap resolves each to the right slug, checked 2026-11-19). The startup template does not create
Bugs, Feature Requests or Tech Debt: they were created from `conventions/collection-schemas/`.

## 20261119_1648 — SKILL.md names installed CLI 0.21.0; --op-key rule names the commands that take it

SKILL.md states pad 0.21.0 installed (pad --version, 2026-11-19) while the references and the upstream mirror stay mapped from v0.19.2. The --op-key rule now lists the 0.21.0 commands that accept it
(item create, patch, comment, note, decide, copy, chat send, push) and says item update has none, read from pad help --format md on 2026-11-19 (references/cli-reference.md Learned 2026-11-18).

## 20261119_1631 — Periodic review; 90-day review window

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19; references, Summaries and Scopes fixed, body rules aligned with their Learned entries. Review window now
  90 days (`--window-days 90` in the justfile).

## 20261119_1609 — Workspace init from an agent shell; conventions recipe quoting

- `references/cli-reference.md` Learned 2026-11-19 (Pad 0.21.0, skills_stuff): `pad workspace init` works without a terminal when signed in and still writes two skill copies; one root `.pad.toml`
  serves a whole repo. `justfile` `conventions` passes arguments with `[positional-arguments]` and `"$@"`, so a spaced `--trackers` value is no longer split.

## 20261119_1551 — CLI traps from smc-resiliency: octet-stream attachments refused, dash-led comment text

- `references/cli-reference.md`: Learned 2026-11-19 (Pad 0.21.0, smc-resiliency): `attachment upload` refuses application/octet-stream (strip a console log to text first); a comment whose text starts
  with `-` needs `--`; body rewrite with `--stdin --replace`.

## 20261119_1550 — CLI traps: no attachment delete, comments not in item show, Tech Debt priority

- `references/cli-reference.md` Traps: Learned 2026-11-19 (Pad 0.21.0, continuum workspace): no attachment delete or replace (correct with a CORRECTION comment); comments only through `pad item
  comments`; Tech Debt stores `--priority` undeclared; rate limits on back-to-back calls.

## 20261119_1434 — Body layout for every collection: pad_format_spec.py

- New `scripts/pad_format_spec.py` (`just format-spec OUT`): writes a `pad_rewrite.py` spec that bolds known section labels, starts each on its own paragraph and joins hard-wrapped lines; lists,
  tables, code and words untouched (an item whose words would change is skipped). 7 tests in `tests/test_pad_format_spec.py`; a no-op reformat fails 3.
- Operator 2026-11-19: 'Formatting of all the pad entries for this project are not correct'. In continuum, 19 of 43 items (all Asks, FRs, TDs; TASK-178 hard-wrapped) rewritten, rescan 0; TASK-166 and
  TASK-171 closing comments rewritten as `DONE:` bullets; item-check 0 findings.
- Learned entry in docs/pad-usage-guidelines-20261110_1628.md 3.3: the standard covers Asks, FRs and TDs; never draft a body in a file the markdown hook reflows; Pad stores `_` as `\\_` in some
  bodies.

## 20261119_1325 — Comment edits can be refused by the server

- `references/cli-reference.md`: Learned 2026-11-19: `comment-edit` refused (no `item_scoped_comment_writes`); fallback, a new formatted comment.

## 20261119_1136 — Decision-log process rows mirrored to Pad

- `scripts/pad_decisions.py`: `process` rows of a decision log are mirrored as well as `architecture` rows (category `decision-log-process`); the operator wants every decision in Pad (Continuum,
  2026-11-19). `tests/test_pad_decisions.py` updated; it fails without the change.

## 20261118_2212 — Tickets tell the whole story: bold labels, updates, a closing statement, logs attached; item-check

- Operator, 2026-11-18 (smc-resiliency bench session, on a closed task with a one-line comment): every item carries proper updates, a proper statement when it moves to done, the log files of the work,
  bold section labels with spacing, and bullets in comments; "add this in the skill pad so that when the skill is used it will enforce that rule", for all projects.
- `SKILL.md` Rules: "Tickets tell the whole story". `docs/pad-usage-guidelines-20261110_1628.md` 3.3: bold bodies, the bug body, the three duties with an example, DONE and CLOSED types.
- `conventions/apn-baseline.toml` `writing-standard` rewritten and raised to must; applied to the smc-resiliency and unified-network-controller workspaces (`just conventions`).
- `scripts/pad_item_check.py` (`just item-check`, test `tests/test_pad_item_check.py`): read-only check of labels, closing comment, update on work in progress, log named but not attached.
- The checker retries a rate-limited pad call (up to five times, growing pause): its first run over 16 items was refused by the server's limit; three tests. First real run after the fix: 16 items of
  the smc-resiliency bench run, 0 findings, 3.0 s (before the tickets were rewritten: 7 findings on 3 items).

## 20261118_2200 — A run planned and recorded in Pad with fields set at create

- `references/cli-reference.md`: Learned 2026-11-18 (v0.21.0): plan, tasks and bugs created with `--fields-json`, `--parent` and `--tags` in one call each; `item update --parent` moves a task under a
  plan; `--workspace` reads another workspace; the ticket practice the operator asked for. From the smc-resiliency bench run.

## 20261118_2149 — pad_decisions.py and a Decisions schema

- `scripts/pad_decisions.py` (`just decisions`, test `tests/test_pad_decisions.py`): mirrors a project's curator ledger and decision log into a `decisions` collection, one item per decision with every
  version; matched on `decision_ref`, changed bodies rewritten. `conventions/collection-schemas/decisions.json`. From continuum (operator, 2026-11-18: decisions out of versions.toml into a dedicated
  Pad section).
- references/cli-reference.md trap: `pad item list` hides closed statuses (accepted is closed in this schema); pass `--all` to see them.
