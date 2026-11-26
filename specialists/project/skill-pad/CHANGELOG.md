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
Last rotated: 20261126_2042
---

# Changelog — skill-pad

## Contents

- [20261126_2042 — Backup: a failed night no longer leaves an empty pad-*.db](#20261126_2042--backup-a-failed-night-no-longer-leaves-an-empty-pad-db)
- [20261126_1850 — Plans close with completed, not done](#20261126_1850--plans-close-with-completed-not-done)
- [20261126_1444 — Comments: dash-leading text needs --](#20261126_1444--comments-dash-leading-text-needs---)
- [20261126_1235 — decision_log_add: a `Reversible by` column takes the decider again](#20261126_1235--decision_log_add-a-reversible-by-column-takes-the-decider-again)
- [20261125_2130 — decision_log_add follows the log's own header (seven-column logs: stamp and status)](#20261125_2130--decision_log_add-follows-the-logs-own-header-seven-column-logs-stamp-and-status)
- [20261125_1157 — Housekeeping as the work lands: superseded items, split children, parent-plan comments; in-progress before any reading (v1.0.0)](#20261125_1157--housekeeping-as-the-work-lands-superseded-items-split-children-parent-plan-comments-in-progress-before-any-reading-v100)
- [20261125_0232 — item-check: plans left open with every child closed; DONE markers on open items](#20261125_0232--item-check-plans-left-open-with-every-child-closed-done-markers-on-open-items)
- [20261125_0037 — Learned: decisions hidden without --all; rate limit in loops](#20261125_0037--learned-decisions-hidden-without---all-rate-limit-in-loops)
- [20261124_2356 — pad_decisions reads bodies in one listing call (62.8 s to 0.3 s)](#20261124_2356--pad_decisions-reads-bodies-in-one-listing-call-628-s-to-03-s)
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

## 20261126_2042 — Backup: a failed night no longer leaves an empty pad-*.db

- `scripts/pad_backup.sh`: when `pad db backup` fails or is stopped at the timeout, the partial `pad-<stamp>.db` and its `-journal` are removed
  (found from the NAS vault copy, 2026-11-26: 4 of 16 nights in OneDrive pad_backups were 0-byte files with a 512-byte journal; the log shows
  6 runs stopped at 120 s, successful runs take 0-3 s). Tested with a hanging stub `pad`: nothing left behind. Cause still open (SCRATCHPAD).

## 20261126_1850 — Plans close with completed, not done

- references/cli-reference.md Learned 2026-11-26: plan status values are planned, active, completed, paused. Source: me/nas session nas-60.

## 20261126_1444 — Comments: dash-leading text needs --

- references/items-and-edits.md: a dash-leading comment needs `--` before the text (`pad item comment <ref> -- "- ..."`), else the CLI reads it as a flag (home NAS, 2026-11-26).

## 20261126_1235 — decision_log_add: a `Reversible by` column takes the decider again

- scripts/decision_log_add.py: continuum's log (sixth column `Reversible by`, holding "Operator." since the six-column default) was refused as an unknown
  column after 20261125_2130; the column now maps to the decider, as before. One test added (5 pass). Found by continuum 2026-11-26 recording DL-259.

## 20261125_2130 — decision_log_add follows the log's own header (seven-column logs: stamp and status)

- scripts/decision_log_add.py: the row's cells now follow the log's header. A `Stamp and source` column needs `--stamp` (the reason cell then carries
  "reason; who"), a `Status` column takes `--status` (default accepted), and a header with an unknown column is refused. smc-resiliency 2026-11-25: its
  seven-column log took four six-column rows, the governance check found them (no `| <stamp>: ` cell) and they were repaired by hand. Two tests added (4 pass).

## 20261125_1157 — Housekeeping as the work lands: superseded items, split children, parent-plan comments; in-progress before any reading (v1.0.0)

- SKILL.md: the "Housekeeping as the work lands" rule now also covers items the work supersedes, the children it splits into and a parent-plan comment at every
  child change; "in-progress" is the first step, before reading or preparing (operator, 2026-11-25: write the continuum housekeeping policy back so other
  projects follow it).
- SKILL.md front matter: `metadata.version` added, starting at 1.0.0 (operator, 2026-11-25: "add version to skill-pad"); later entries bump it and name
  the new version in their heading, as the other packs do. ARCHITECTURE.md re-read: item-check row now names the stale, plan and marker findings.

## 20261125_0232 — item-check: plans left open with every child closed; DONE markers on open items

- scripts/pad_item_check.py: two findings (operator, 2026-11-25: "why is the housekeeping not done as soon as the task is completed or has an update?"): `plan`, a plan not closed whose children (`pad item list --parent <plan> --all`, one more call per plan) are all done, resolved, fixed, cancelled, answered, shipped, completed or archived; `marker`, a plan, task, bug or tech-debt item whose newest comment carries `DONE` or `Fixed` while its status is not closed. Evidence: continuum PLAN-491, 403, 531, 446, 374 at planned with every child closed; TD-509 at identified a day after a "Fixed 2026-11-23" comment.
- tests/test_pad_item_check.py HousekeepingTests: both rules fail and pass; red against the previous script (TypeError on `children`, marker test FAIL), 23 tests OK after.
- SKILL.md rule "Housekeeping as the work lands"; scripts/README.md catalog row.

## 20261125_0037 — Learned: decisions hidden without --all; rate limit in loops

- references/cli-reference.md: Learned 2026-11-25, `pad item list` hides accepted decisions without `--all`; loops through `just pad` (home NAS).

## 20261124_2356 — pad_decisions reads bodies in one listing call (62.8 s to 0.3 s)

- scripts/pad_decisions.py: existing() lists the decisions collection once with `--full` and returns each item's body; body_of() reads that cache and falls back to `pad item show` only for a ref the listing lacked. Before, plan() ran one `pad item show` per existing decision: 339 calls took 62.8 s on a plan-only run with nothing to change, and about 118 s when the shared server rate-limited (continuum BUG-557: the 'record and mirror' calls of 2026-11-24 ran 46 to 118 s). After: 0.3 s, same plan (339 wanted, 0 to create, 0 to update).
- tests/test_pad_decisions.py ExistingTest: one listing call gives refs and bodies and passes `--full`; fails on the old code (proven), 96 tests OK.
- Learned 2026-11-24 · pad CLI · VERIFIED_PRIMARY (pad item list --full JSON carries `content`, equal to `pad item show`, 339 items in 0.06 s) · Falsifier: a listing whose content differs from show. Read many items' bodies with one `pad item list <collection> --all --full --format json`, never a show per item.

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
