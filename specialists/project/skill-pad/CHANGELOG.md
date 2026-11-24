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
Last rotated: 20261124_2252
---

# Changelog — skill-pad

## Contents

- [20261124_2252 — Learned: workspace setup traps (icons, boolean flags, conventions arguments)](#20261124_2252--learned-workspace-setup-traps-icons-boolean-flags-conventions-arguments)
- [20261124_2211 — decision-add keeps free-text arguments intact](#20261124_2211--decision-add-keeps-free-text-arguments-intact)
- [20261124_1634 — pad_decisions shows a row's points one per line](#20261124_1634--pad_decisions-shows-a-rows-points-one-per-line)
- [20261124_1452 — pad_spec_words checks comment rewrites](#20261124_1452--pad_spec_words-checks-comment-rewrites)
- [20261124_1451 — Write-back from continuum 2026-11-24: bulk standard pass](#20261124_1451--write-back-from-continuum-2026-11-24-bulk-standard-pass)
- [20261123_1840 — Mirrored decisions carry wiki-links](#20261123_1840--mirrored-decisions-carry-wiki-links)
- [20261123_1422 — Status values per collection](#20261123_1422--status-values-per-collection)
- [20261122_2341 — Decision links looked up, not recalled](#20261122_2341--decision-links-looked-up-not-recalled)
- [20261122_2046 — Bugs close with fixed; no pad search; blocked-by](#20261122_2046--bugs-close-with-fixed-no-pad-search-blocked-by)
- [20261122_1745 — Status values per collection; `--` before dash-led comments; collections used unprompted](#20261122_1745--status-values-per-collection----before-dash-led-comments-collections-used-unprompted)
- [20261122_0031 — Transient comment-edit refusal retried; decision store not a log; CLI traps](#20261122_0031--transient-comment-edit-refusal-retried-decision-store-not-a-log-cli-traps)
- [20261121_1950 — label-fill and done-backfill scripts; fields as a JSON string; a refused comment edit](#20261121_1950--label-fill-and-done-backfill-scripts-fields-as-a-json-string-a-refused-comment-edit)
- [20261121_1908 — Tech Debt closes with resolved, not done](#20261121_1908--tech-debt-closes-with-resolved-not-done)
- [20261120_2335 — Comment edits work again (Disputed); statuses are per collection; list is partial](#20261120_2335--comment-edits-work-again-disputed-statuses-are-per-collection-list-is-partial)
- [20261120_2218 — item-check finds in-progress items left idle (stale); session start handles them (operator)](#20261120_2218--item-check-finds-in-progress-items-left-idle-stale-session-start-handles-them-operator)
- [20261120_2210 — item-check reports comments not in the bullet form and references not written as links (operator)](#20261120_2210--item-check-reports-comments-not-in-the-bullet-form-and-references-not-written-as-links-operator)
- [20261120_1827 — Templates for every collection, enforced; draw.io flow map; links in comments; component tags; trial adopted](#20261120_1827--templates-for-every-collection-enforced-drawio-flow-map-links-in-comments-component-tags-trial-adopted)
- [20261120_1812 — pad_retry.sh and just pad: single calls retry while the shared server rate-limits (operator, option 3)](#20261120_1812--pad_retrysh-and-just-pad-single-calls-retry-while-the-shared-server-rate-limits-operator-option-3)
- [20261120_1811 — Learned: list hides done items, stdin for bulleted bodies, rate limits](#20261120_1811--learned-list-hides-done-items-stdin-for-bulleted-bodies-rate-limits)
- [20261120_1744 — pad_decisions reads an architecture document's Key decisions; pad_links links register ids; workspace rename is name-only](#20261120_1744--pad_decisions-reads-an-architecture-documents-key-decisions-pad_links-links-register-ids-workspace-rename-is-name-only)
- [20261120_1647 — pad_links: item references as links, dependencies as typed relations (operator)](#20261120_1647--pad_links-item-references-as-links-dependencies-as-typed-relations-operator)
- [20261120_1420 — Work visible in Pad; Pad consulted at session start; smc-resiliency decisions](#20261120_1420--work-visible-in-pad-pad-consulted-at-session-start-smc-resiliency-decisions)
- [20261120_1417 — Rule: work in Pad shows as active](#20261120_1417--rule-work-in-pad-shows-as-active)

## 20261124_2252 — Learned: workspace setup traps (icons, boolean flags, conventions arguments)

- references/cli-reference.md: Learned 2026-11-24 (emoji icons, boolean flags with =, conventions needs --project, item comment text is positional or --stdin), from the home NAS workspace setup.

## 20261124_2211 — decision-add keeps free-text arguments intact

- `decision-add` passes its arguments through `"$@"` ([positional-arguments]); with `{{ARGS}}` an argument holding `(`, quotes or spaces broke the recipe (`syntax error near unexpected token`), seen 2026-11-24 in continuum writing DL-227. Tested: plan run with parentheses, quotes and an apostrophe.
- Learned 2026-11-24 · justfile · VERIFIED_PRIMARY · Source: justfile decision-add · Falsifier: a {{ARGS}} recipe passing "a (b)" through intact. A recipe whose arguments are free text needs [positional-arguments] and "$@"; {{ARGS}} is re-split by the shell.

## 20261124_1634 — pad_decisions shows a row's points one per line

- **What:** a decision-log row with several points separates them with `<br>` (a table row stays on one line); the Pad body shows one point per line with a blank line where a list starts
  and ends, the title stops at the first break, and an update now rewrites the title too (it kept the old one before). No space follows `**Decision:**` before a multi-point body: Pad strips it, and the next plan re-updated the item forever (found the same day on DL-219). `--show-updates` prints each planned update with a diff (a trailing space quoted). New `scripts/decision_log_add.py` (`just decision-add`):
  appends one row (next DL id, six columns, points joined by `<br>`, refuses `|`); tests/test_decision_log_add.py round-trips it through pad_decisions; SKILL.md rule
  "Decision rows".
- **Why:** operator, continuum 2026-11-24, on DL-215 (four answers in one run-on row): "each point should be on a separate line at least"; a bold ref inside a point was replaced by the
  linked item's whole title, so points start with the plain ref.
- **Evidence:** tests/test_pad_decisions.py test_points_one_per_line fails on the old script and passes now (7 tests OK); continuum DECIS-560 re-mirrored, the next plan shows 0 to update.

---

## 20261124_1452 — pad_spec_words checks comment rewrites

- scripts/pad_spec_words.py also compares each comment rewrite (spec `comments`) with the comment's current text and lists a bullet newly labelled Decision for review; two offline tests; smoke run on three continuum comments (promoted from a continuum TD-541 one-off check).

## 20261124_1451 — Write-back from continuum 2026-11-24: bulk standard pass

- references/items-and-edits.md, Learned 2026-11-24: the order for a bulk writing-standard pass and three traps (label-fill filler passes the check, a word check does not validate labels, links lengthen comments past the bullet threshold); continuum TD-541, TD-542.

## 20261123_1840 — Mirrored decisions carry wiki-links

- Operator, 2026-11-23 (continuum): "Why links are missing in the decisions?" Cause: `pad_decisions.py` wrote bodies as plain text and every sync replaced the body, so the `[[REF]]` rule
  never held for the `decisions` collection and a link added by `just links` was overwritten on the next sync.
- Fix: `link_bodies` runs each mirrored body through `pad_links.linked` before the compare and write: item refs become `[[FR-275]]`, other decisions `[[<mirror ref>|DL-nnn]]`, never a
  self-link, code spans untouched. `--no-links` keeps the old plain bodies. A decision created in a run becomes a link target on the next run.
- Evidence: new test `LinkBodies` (red with linking stubbed out), `test_pad_decisions` 6/6, `just check` green; continuum plan 167 of 297 bodies to re-mirror (49 s).

## 20261123_1422 — Status values per collection

- references/cli-reference.md, Learned 2026-11-23: status values of each default collection, from the CLI's own refusals (continuum).

## 20261122_2341 — Decision links looked up, not recalled

references/cli-reference.md: two DECIS links written from memory pointed at missing items; look ids up with pad item list decisions --all and fix bodies with pad item update --stdin.

## 20261122_2046 — Bugs close with fixed; no pad search; blocked-by

references/cli-reference.md: Bugs refuse resolved (allowed: open confirmed in-progress fixed wont-fix); each collection's closing word listed; no pad search command (use item list --all | grep); blocked-by in one call. Source: continuum 2026-11-22 night (BUG-435, TASK-383).

## 20261122_1745 — Status values per collection; `--` before dash-led comments; collections used unprompted

- references/cli-reference.md (Traps), Learned 2026-11-22: allowed statuses per collection (asks, feature requests, bugs, tasks, tech debt); `--` lets a comment start with `-`; plans have no priority
  field; operator rule to use every collection unprompted (continuum).

## 20261122_0031 — Transient comment-edit refusal retried; decision store not a log; CLI traps

- scripts/pad_rewrite.py, pad_links.py, pad_retry.sh: the comment-edit capability refusal ("does not advertise item_scoped_comment_writes") is retried with backoff like `rate_limited` (`TRANSIENT`);
  continuum 2026-11-22 saw 11 such refusals, each applied on a rerun.
- scripts/pad_item_check.py: a `*decisions.jsonl` store named in an item is no longer reported as a log to attach (continuum TASK-27 false positive).
- references/cli-reference.md Traps: the refusal recurs under bursts; `--` before a comment body starting with `-`; a long DONE comment needs bullets too; pad_rewrite order (notes first in their own
  spec). Tests: `just test` 88 OK.

## 20261121_1950 — label-fill and done-backfill scripts; fields as a JSON string; a refused comment edit

- scripts/pad_label_fill.py (`just label-fill`): a rewrite spec adding each missing required template label, inventing nothing; tests/test_pad_label_fill.py.
- scripts/pad_done_backfill.py (`just done-backfill`): a DONE closing statement for closed work items without one, quoted from their own comments; tests/test_pad_done_backfill.py.
- references/cli-reference.md: `fields` comes as a JSON string; one comment edit refused while others in the run succeeded. Used on continuum 2026-11-21: 48 bodies filled, 26 closing statements, 39
  link writes.

## 20261121_1908 — Tech Debt closes with resolved, not done

- references/cli-reference.md (statuses and listing): Tech Debt refuses `done` and takes `resolved` (continuum TD-315, 2026-11-21).

## 20261120_2335 — Comment edits work again (Disputed); statuses are per collection; list is partial

- references/cli-reference.md: Disputed 2026-11-20 beside the 2026-11-19 refusal (comment-edit worked four times on 0.21.1); Learned 2026-11-20: Feature Requests use `building`, not `in-progress`;
  `item list --format json` returns part of a collection, so read refs with `item show` and never write placeholder links.

## 20261120_2218 — item-check finds in-progress items left idle (stale); session start handles them (operator)

- scripts/pad_item_check.py: `stale` rule: an in-progress item with no item update, comment or note for `--stale-hours` (default 24); the recent list always includes every in-progress item, however
  old. 2 tests (79 OK). SKILL.md rule "No item left in the wrong state": at session start run item-check and resume each stale item or set it back to open with a comment saying why. First runs:
  smc-resiliency 217 items clean (three idle items had been reset by hand the same evening: TASK-14, TASK-96, TASK-98); ansible-wifi 3 comments with bullets on one line, split. Operator, 2026-11-20.

## 20261120_2210 — item-check reports comments not in the bullet form and references not written as links (operator)

- scripts/pad_item_check.py: two rules. `comments`: a comment from 2026-11-18 on, over 200 characters, with no `- **Label:**` bullet line. `refs`: an item ref of this workspace or a DL id (where the
  workspace has a Decisions collection) written as plain text, in the body or a comment from 2026-11-20 on. Another workspace's ref or a typo is not reported. 5 tests (77 OK). First run on
  smc-resiliency: 14 findings, cleared by `just links` and a word-for-word bullet conversion; TASK-92's non-existent BUG-89 found and corrected to BUG-91. Operator, 2026-11-20: TASK-53 passed
  item-check while its start comment was one paragraph and its body linked nothing.

## 20261120_1827 — Templates for every collection, enforced; draw.io flow map; links in comments; component tags; trial adopted

- docs/pad-usage-guidelines-20261110_1628.md 3.3: Templates by collection (operator 2026-11-20, Extend and enforce): required and optional labels for plans, tasks, bugs, tech debt, ideas, asks,
  feature requests (a one-line request keeps the operator's words), decisions, conventions; the closing-comment check is for work only. 3.4: component tags in a workspace shared by several projects or
  packs (operator 2026-11-20). Section 6 step 6: trial over, Pad adopted for all important projects (unc ASK-237).
- scripts/pad_item_check.py: required labels per collection; closing-comment and log checks only on work collections (a decision naming its .jsonl ledger is not a log: 102 false findings in
  continuum); a one-line feature request is exempt even with a cut title; a collection missing from a workspace is skipped. Tests added.
- scripts/pad_decisions.py: bold labels in both generated bodies (Serves, Question, Decision, Reason, Versions, Source); unc 34, smc-resiliency 100, continuum 191 and enterprise-strategy 128 decisions
  re-synced.
- scripts/pad_links.py: agent-written comments linked as well as bodies (operator: "Unblocked: ASK-237 answered" went out unlinked); a person's comment is never edited. Test with a fake pad.
- scripts/pad_conventions.py: retries a rate-limited call (three of four applies had stopped). Tests.
- conventions/apn-baseline.toml and ansible-wifi.toml: every content as Rule and Source; writing-standard names every template, links in comments and component tags; pad-owned-trackers drops the old
  bug first-line form. Applied to unc, smc-resiliency, enterprise-strategy (without pad-owned-trackers) and ansible-wifi; a second plan shows 0 changes. unc's CONVE-24 tracker list restored (an
  earlier run today had replaced it with docs/trackers/).
- docs/flows/: draw.io flow map (operator 2026-11-20): 11 flows in four families rendered by skill-drawio's engine; just flows, just flows-check in just check (drift, code citations, layout audits
  clean).
- SKILL.md Rules: links in comments and status comments; skill work goes to the skills workspace (operator 2026-11-20). Pad items: skills TASK-12, TASK-13, TASK-14 (tag skill-pad); ansible-wifi items
  tagged by component (ansible-wifi 20, local-knowledge 7, skill-smc 1).

## 20261120_1812 — pad_retry.sh and just pad: single calls retry while the shared server rate-limits (operator, option 3)

- scripts/pad_retry.sh (new), `just pad` recipe, tests/test_pad_retry.py (4 tests: retry then success with stdin replayed, give up at the limit, no retry on success, bad usage); SKILL.md rule;
  references/cli-reference.md Learned entry on the per-user limiter (server log of 20 Nov); scripts/README.md, code-map.toml. 63 tests OK.

## 20261120_1811 — Learned: list hides done items, stdin for bulleted bodies, rate limits

- references/cli-reference.md: Learned 2026-11-20 from the continuum workspace (pad item list hides done-like items without --all; comment bodies starting with '- ' need --stdin; rate_limited bursts).

## 20261120_1744 — pad_decisions reads an architecture document's Key decisions; pad_links links register ids; workspace rename is name-only

- `scripts/pad_decisions.py`: `--architecture PATH` mirrors the decision bullets of that document's `## Key decisions` section (unc keeps its decisions in ARCHITECTURE.md, not a DL log); refs are
  register ids (D17, S20, X2) or `ARCH-<slug>`; a status note without DECIDED, SETTLED, RESOLVED, still open or (operator, date) is skipped and listed; items whose ref left every source are listed as
  orphaned, never changed (a renamed bullet gets a new slug). Tests: `tests/test_pad_decisions.py` Architecture, orphans. unc: 34 decisions mirrored, a re-run plans 0 creates and 0 updates (3.5 s).
- `scripts/pad_links.py`: a mirrored register id (`D17`) becomes `[[DECIS-n|D17]]`; never `D17-03` or `D3.6`. New `tests/test_pad_links.py` (4 tests).
- `references/cli-reference.md` Traps: Learned 2026-11-20, workspace rename is web-UI and name-only (slug read-only); reads are rate-limited too.
- unc workspace brought to the smc-resiliency and continuum layout: Asks and Decisions collections, baseline conventions plus decisions-mirror and progress-record, 52 bodies laid out, links applied.

## 20261120_1647 — pad_links: item references as links, dependencies as typed relations (operator)

- scripts/pad_links.py and `just links`: bare item refs and decision ids in bodies become `[[REF]]` / `[[DECIS-n|DL-058]]` wiki-links; a JSON spec adds typed relations (blocks, implements, split-from,
  supersedes); plan by default, idempotent. Operator, 2026-11-20 (continuum ASK-251): references must be clickable and dependencies recorded in the relationship section.
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
- Duplicate removed: a parallel session committed this rule and its own fuller "Work is visible in Pad" rule together (a0fea8bb); this rule's text is dropped and its "a relay, a write-back or a side
  task counts as work" clause joins the kept rule.
- 20261120_1425: housekeeping exception (operator, 20 Nov 2026): closeout, slurp, skill write-backs, coherence sweeps and staleness audits get no Pad item; "a write-back" dropped from the work clause.
- SKILL.md Rules: "Never add to Pad" lists the housekeeping kinds (closeout and slurps, write-backs, coherence sweeps, staleness audits, record upkeep, sync reports, memory saves, their commits)
  (operator, 20 Nov 2026).
