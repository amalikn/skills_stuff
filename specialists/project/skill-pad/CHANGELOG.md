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
Last rotated: 20261119_1552
---

# Changelog — skill-pad

## 20261119_1609 — Workspace init from an agent shell; conventions recipe quoting

- `references/cli-reference.md` Learned 2026-11-19 (Pad 0.21.0, skills_stuff): `pad workspace init` works without a terminal when signed in and still writes two skill copies; one root `.pad.toml` serves a whole repo. `justfile` `conventions` passes arguments with `[positional-arguments]` and `"$@"`, so a spaced `--trackers` value is no longer split.

## 20261119_1551 — CLI traps from smc-resiliency: octet-stream attachments refused, dash-led comment text

- `references/cli-reference.md`: Learned 2026-11-19 (Pad 0.21.0, smc-resiliency): `attachment upload` refuses application/octet-stream (strip a console log to text first); a comment whose text starts with `-` needs `--`; body rewrite with `--stdin --replace`.

## 20261119_1550 — CLI traps: no attachment delete, comments not in item show, Tech Debt priority

- `references/cli-reference.md` Traps: Learned 2026-11-19 (Pad 0.21.0, continuum workspace): no attachment delete or replace (correct with a CORRECTION comment); comments only through `pad item comments`; Tech Debt stores `--priority` undeclared; rate limits on back-to-back calls.

## 20261119_1434 — Body layout for every collection: pad_format_spec.py

- New `scripts/pad_format_spec.py` (`just format-spec OUT`): writes a `pad_rewrite.py` spec that bolds known section labels, starts each on its own paragraph and joins hard-wrapped lines; lists, tables, code and words untouched (an item whose words would change is skipped). 7 tests in `tests/test_pad_format_spec.py`; a no-op reformat fails 3.
- Operator 2026-11-19: 'Formatting of all the pad entries for this project are not correct'. In continuum, 19 of 43 items (all Asks, FRs, TDs; TASK-178 hard-wrapped) rewritten, rescan 0; TASK-166 and TASK-171 closing comments rewritten as `DONE:` bullets; item-check 0 findings.
- Learned entry in docs/pad-usage-guidelines-20261110_1628.md 3.3: the standard covers Asks, FRs and TDs; never draft a body in a file the markdown hook reflows; Pad stores `_` as `\\_` in some bodies.

## 20261119_1325 — Comment edits can be refused by the server

- `references/cli-reference.md`: Learned 2026-11-19: `comment-edit` refused (no `item_scoped_comment_writes`); fallback, a new formatted comment.

## 20261119_1136 — Decision-log process rows mirrored to Pad

- `scripts/pad_decisions.py`: `process` rows of a decision log are mirrored as well as `architecture` rows (category `decision-log-process`); the operator wants every decision
  in Pad (Continuum, 2026-11-19). `tests/test_pad_decisions.py` updated; it fails without the change.

## 20261118_2212 — Tickets tell the whole story: bold labels, updates, a closing statement, logs attached; item-check

- Operator, 2026-11-18 (smc-resiliency bench session, on a closed task with a one-line comment): every item carries proper updates, a proper statement when it moves to done, the log
  files of the work, bold section labels with spacing, and bullets in comments; "add this in the skill pad so that when the skill is used it will enforce that rule", for all projects.
- `SKILL.md` Rules: "Tickets tell the whole story". `docs/pad-usage-guidelines-20261110_1628.md` 3.3: bold bodies, the bug body, the three duties with an example, DONE and CLOSED types.
- `conventions/apn-baseline.toml` `writing-standard` rewritten and raised to must; applied to the smc-resiliency and unified-network-controller workspaces (`just conventions`).
- `scripts/pad_item_check.py` (`just item-check`, test `tests/test_pad_item_check.py`): read-only check of labels, closing comment, update on work in progress, log named but not attached.
- The checker retries a rate-limited pad call (up to five times, growing pause): its first run over 16 items was refused by the server's limit; three tests. First real run after
  the fix: 16 items of the smc-resiliency bench run, 0 findings, 3.0 s (before the tickets were rewritten: 7 findings on 3 items).

## 20261118_2200 — A run planned and recorded in Pad with fields set at create

- `references/cli-reference.md`: Learned 2026-11-18 (v0.21.0): plan, tasks and bugs created with `--fields-json`, `--parent` and `--tags` in one call each; `item update --parent` moves a
  task under a plan; `--workspace` reads another workspace; the ticket practice the operator asked for. From the smc-resiliency bench run.

## 20261118_2149 — pad_decisions.py and a Decisions schema

- `scripts/pad_decisions.py` (`just decisions`, test `tests/test_pad_decisions.py`): mirrors a project's curator ledger and decision log into a `decisions` collection, one item per
  decision with every version; matched on `decision_ref`, changed bodies rewritten. `conventions/collection-schemas/decisions.json`. From continuum (operator, 2026-11-18: decisions out of
  versions.toml into a dedicated Pad section).
- references/cli-reference.md trap: `pad item list` hides closed statuses (accepted is closed in this schema); pass `--all` to see them.

## 20261118_2129 — 0.21.0 string flags need =value; continuum workspace set up

- references/cli-reference.md Traps: Learned entry, `--awaits-human=true --tracks-work=false` form; init still writes skill copies (moved to the Trash). From the continuum workspace setup.
- references/cli-reference.md Traps: Learned entry, `pad item block <source> <target>` means source blocks target.

## 20261118_2106 — item update has no --op-key; code paths in item bodies; a question without an Asks collection

- `references/cli-reference.md`: Learned 2026-11-18 (v0.21.0), `item update` rejects `--op-key`; a backticked code path in an item body is checked by the project that exports it; an operator
  question in a workspace with no Asks collection goes in as a blocking Task. From the unified-network-controller D17 session.

## 20261118_1742 — CLI at 0.21.0

- `references/cli-reference.md`: Learned 2026-11-18, the installed pad is 0.21.0 (map is v0.19.2); create flags unchanged; a new bug section renders as its own
  generated heading. Map refresh per `references/upgrade.md` still to do.

## 20261111_1223 — .pad.toml rewrite behaviour tested

- `references/workspace-context.md`: Learned 2026-11-11, `pad workspace link` refuses a linked folder; `switch` rewrites `.pad.toml`, keeping
  unknown tables but deleting comments; both write skill copies into the project. Project settings belong in a file Pad never writes.

## 20261111_1213 — links step in a commit gate

- `references/items-and-edits.md`: run `pad_tracker.py links` before the export in a project's commit gate.

## 20261111_1135 — workspace sharing noted

- `references/workspace-context.md`: Learned 2026-11-11, `pad workspace link` shares an existing workspace across repos (skill-ai-it asks at bootstrap).

## 20261111_1054 — Pad link opener: repo links in Pad open in VS Code

### Added

- `scripts/pad_link_opener.py`: a localhost service (127.0.0.1:47800, launchd `pad_link_opener.plist`, `just link-opener`) that redirects
  `/open/<absolute path>?f=L<n>` to `vscode://file/<path>:<n>`. Pad v0.19.2 strips vscode:// links (web/src/lib/utils/markdown.ts:224, only
  http(s), mailto, ftp, tel kept), so Pad holds http links and is not patched: upgrades need nothing. Existing paths under `/Volumes/Data`
  only; no file content served. `just link-url PATH --line N` prints a link. Tests `tests/test_pad_link_opener.py`.
- `pad_tracker.py links`: rewrites relative repo links in a collection's Pad bodies into opener links (each write guarded by the item's seq);
  `import` writes opener links (`--no-opener` to skip) and `export` always turns them back into links relative to the tracker file, so the
  repo file is unchanged. Applied to smc-resiliency Bugs (7 items, 8 links); the operator confirmed a click in BUG-41 opens VS Code.
- `references/items-and-edits.md`: Learned 2026-11-11, Pad strips vscode:// and relative links go nowhere; write opener links.

## 20261110_2055 — tracker import spike noted for the trial review

### Changed

- Side agent: imported closed bugs and features count as done on 10 Nov. Checked in UNC: `next`, `stale` and the dashboard are not flooded;
  today's changelog lists 43 imported closures. Operator: keep both collections as work and discount the spike; noted on UNC TASK-20 and in
  guidelines section 6 step 6.

## 20261110_2031 — slurp close: session record, write-backs, collection schemas

### Added

- `docs/session-record-20261110_2029.md`: all 56 operator messages with destinations, side effects outside the repos, open work by owner.
- `conventions/collection-schemas/` (asks, bugs, feature-requests, tech-debt) with a readme; cli-reference Traps: web collection templates.
- Write-backs: skill-coder `references/tooling-and-runtime.md` (dataclass loaded by path, flushed progress lines); skill-ai-it
  `references/pitfalls.md` (generation-policy table rows; markdown hook re-wraps whole files).

### Notes

- Flows: smc-resiliency and UNC rendered and traced; nothing of this session's changes is described there; UNC's 157 unstamped steps are its own.

## 20261110_2020 — UNC moved: bugs, feature requests and tech debt in Pad in both workspaces

### Changed

- UNC: Bugs (73, nested as children), Feature Requests (84, 49 children) imported, round trip identical; TASK-21 and TASK-22 moved to Tech Debt
  (TD-21, TD-22) and TD-183 points at the refactor tracker (a generated inventory read by check_script_structure, so it stays a file); commit gate
  runs `just pad-trackers`; AGENTS.md rule and task text point at Pad; 34 bug IDs set; tasks linked to their bugs (implements).
- Both workspaces: trackers-truth conventions (CONVE-9, CONVE-24) and the baseline gain the Pad exception; pad-owned-trackers applied to UNC.
- Guidelines: principle 1 exception; 3.1 lists Bugs, Feature Requests, Tech Debt.

## 20261110_2014 — bugs, feature requests and tech debt in Pad (smc-resiliency done)

### Added

- `scripts/pad_tracker.py` (import and export of a Markdown tracker as a file generated from a Pad collection; hand-edited blocks refused; 4 tests).
- Convention `pad-owned-trackers` (always, must; exception to trackers-truth) in the baseline, now seven; applied to smc-resiliency.
- smc-resiliency: collections Bugs (BUG), Feature Requests (FR), Tech Debt (TD) from Pad's web templates plus section, order and declared closed
  states (the Feature Requests and Tech Debt templates declare none); 16 bugs and 1 feature imported, round trip identical; commit gate runs
  `just pad-trackers`; tasks link to their bugs (implements). UNC next.

## 20261110_2004 — closed items on the standard; output order fix

### Changed

- The four closed items (smc TASK-29; UNC TASK-15, TASK-19, IDEA-23) rewritten to guidelines 3.3; their 8 comment originals saved as notes first,
  then reformatted. Sweep: 36 plans, tasks and ideas and 20 comments in both workspaces on the standard.
- `pad_rewrite.py` flushes each progress line, so an error is no longer printed ahead of it (the earlier "silent stop" was an `update_conflict`
  hidden by that order). cli-reference Traps: notes and comments move an item's seq.

## 20261110_1958 — original comment texts kept; rate-limit retries

### Changed

- The 12 smc-resiliency comments' original texts saved verbatim as notes on their items (side agent: Pad may not keep an edited comment's
  earlier text). Guidelines 3.3: keep the original as a note before reformatting a comment. `pad_rewrite.py` retries `rate_limited` answers up to
  5 times (the likely cause of the earlier silent stop). cli-reference Traps: rate limit, comment history.

## 20261110_1956 — smc-resiliency comments rewritten to the comment standard

### Changed

- The 12 smc-resiliency comments rewritten to guidelines 3.3 (operator: comment formatting not updated): stamp and type first (times from each
  comment's creation, AEDT), at most five lines, verified and not verified said, `Next:` last; every fact kept. `pad_rewrite.py` comment entries
  take `body` to replace the text (skipped when equal); test added.

## 20261110_1955 — open Pad items rewritten to the writing standard; pad_rewrite.py; item links

### Added

- `scripts/pad_rewrite.py` (spec-driven, plan by default, seq-guarded bodies, idempotent notes and decisions; 3 tests, `just rewrite`, code-map).
- Guidelines 3.10: Pad link types mapped to Jira's (blocks, implements, supersedes, split-from, parent; fallbacks for relates, duplicates, clones).

### Changed

- All 32 open plans and tasks rewritten to guidelines 3.3 (smc-resiliency 20, UNC 12): bodies, titles, dates from the timelines, tags; smc's 12
  comments gained type words, with 8 notes and 2 decisions extracted. Old text compared token by token; two facts dropped from TASK-30 restored as a
  note (side agent). Open: the first smc apply stopped once without an error message; a rerun completed it; cause not found.

## 20261110_1940 — guard for the live Pad database in tools_stuff

### Changed

- SETUP.md: Git tracks the live pad.db in tools_stuff (operator); no stash, checkout, restore, clean or branch switch there while Pad runs, and
  `pad/` is committed only with the server stopped. Rule kept in tools_stuff `.agents/pad-data.md` (operator chose a rule over untracking).

## 20261110_1936 — Pad usage guidelines in force (Q1 to Q6 answered)

### Changed

- Operator answered Q1 to Q6: Asks collection, current focus only, no roles, answers on the ask or in chat (both), roll out to smc-resiliency and
  UNC together, keep the OneDrive backup. Proposal renamed `docs/pad-usage-guidelines-20261110_1628.md` (Status current); rollout reworked for both
  workspaces (smc-resiliency canary first within each step); SKILL.md, AGENTS, README and SCRATCHPAD now treat it as in force.
