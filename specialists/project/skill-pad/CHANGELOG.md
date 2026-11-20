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
Last rotated: 20261120_1334
---

# Changelog — skill-pad

## Contents

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
- [20261118_2129 — 0.21.0 string flags need =value; continuum workspace set up](#20261118_2129--0210-string-flags-need-value-continuum-workspace-set-up)
- [20261118_2106 — item update has no --op-key; code paths in item bodies; a question without an Asks collection](#20261118_2106--item-update-has-no---op-key-code-paths-in-item-bodies-a-question-without-an-asks-collection)
- [20261118_1742 — CLI at 0.21.0](#20261118_1742--cli-at-0210)
- [20261111_1223 — .pad.toml rewrite behaviour tested](#20261111_1223--padtoml-rewrite-behaviour-tested)
- [20261111_1213 — links step in a commit gate](#20261111_1213--links-step-in-a-commit-gate)
- [20261111_1135 — workspace sharing noted](#20261111_1135--workspace-sharing-noted)
- [20261111_1054 — Pad link opener: repo links in Pad open in VS Code](#20261111_1054--pad-link-opener-repo-links-in-pad-open-in-vs-code)
- [20261110_2055 — tracker import spike noted for the trial review](#20261110_2055--tracker-import-spike-noted-for-the-trial-review)

---

## 20261120_1334 — Pad CLI 0.21.1 installed; no behaviour change seen

SKILL.md: the installed Pad CLI is 0.21.1 (pad --version, 2026-11-20, build 0d76fda of 2026-11-18). Used from smc-resiliency with no change in behaviour
seen: bootstrap, item create with --op-key, and the pack's item-check (TASK-103 and TASK-104, 0 findings) all worked as on 0.21.0. Learned from the
enterprise-strategy slurp close of 20 Nov 2026.

## 20261120_0300 — Tracker export: an item made in Pad renders its title

- scripts/pad_tracker.py `from_pad`: an item created in Pad (its title differs from its body's first line) is rendered with the title as the line and the
  whole body under it; before, the body's first line (`**Serves:** ...`) stood in for the item (smc-resiliency features-to-add, FR-95). Imported items
  are unchanged. Two tests in tests/test_pad_tracker.py (9 pass; the first fails on the old code).

## 20261119_1849 — Markdown and Pad sync plan; peer sessions consulted

Operator asked whether skill-pad has the scripts projects need to work with Pad, whether markdown needs a mapping to Pad items, and for a plan
with a reversible script (markdown edited, Pad updated, markdown regenerated). Three live sessions consulted (smc-resiliency-44, ansible-wifi-47,
continuum-32) on sync, revert and script gaps.

- New `docs/pad-markdown-sync-plan-20261119_1845.md` (proposed): one owner per record type, keys in the markdown, sync cycle, journal and
  revert, conflicts, link checks, script constraints, collections review (keep, leave empty, add Asks, Decisions, Risks, Handoffs, Runs), gaps
  G1-G18, stages S0-S6, decisions D1-D9. Indexed in README and SKILL.md.
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

## 20261118_2129 — 0.21.0 string flags need =value; continuum workspace set up

- references/cli-reference.md Traps: Learned entry, `--awaits-human=true --tracks-work=false` form; init still writes skill copies (moved to the Trash). From the continuum workspace setup.
- references/cli-reference.md Traps: Learned entry, `pad item block <source> <target>` means source blocks target.

## 20261118_2106 — item update has no --op-key; code paths in item bodies; a question without an Asks collection

- `references/cli-reference.md`: Learned 2026-11-18 (v0.21.0), `item update` rejects `--op-key`; a backticked code path in an item body is checked by the project that exports it; an operator question
  in a workspace with no Asks collection goes in as a blocking Task. From the unified-network-controller D17 session.

## 20261118_1742 — CLI at 0.21.0

- `references/cli-reference.md`: Learned 2026-11-18, the installed pad is 0.21.0 (map is v0.19.2); create flags unchanged; a new bug section renders as its own generated heading. Map refresh per
  `references/upgrade.md` still to do.

## 20261111_1223 — .pad.toml rewrite behaviour tested

- `references/workspace-context.md`: Learned 2026-11-11, `pad workspace link` refuses a linked folder; `switch` rewrites `.pad.toml`, keeping unknown tables but deleting comments; both write skill
  copies into the project. Project settings belong in a file Pad never writes.

## 20261111_1213 — links step in a commit gate

- `references/items-and-edits.md`: run `pad_tracker.py links` before the export in a project's commit gate.

## 20261111_1135 — workspace sharing noted

- `references/workspace-context.md`: Learned 2026-11-11, `pad workspace link` shares an existing workspace across repos (skill-ai-it asks at bootstrap).

## 20261111_1054 — Pad link opener: repo links in Pad open in VS Code

### Added

- `scripts/pad_link_opener.py`: a localhost service (127.0.0.1:47800, launchd `pad_link_opener.plist`, `just link-opener`) that redirects `/open/<absolute path>?f=L<n>` to `vscode://file/<path>:<n>`.
  Pad v0.19.2 strips vscode:// links (web/src/lib/utils/markdown.ts:224, only http(s), mailto, ftp, tel kept), so Pad holds http links and is not patched: upgrades need nothing. Existing paths under
  `/Volumes/Data` only; no file content served. `just link-url PATH --line N` prints a link. Tests `tests/test_pad_link_opener.py`.
- `pad_tracker.py links`: rewrites relative repo links in a collection's Pad bodies into opener links (each write guarded by the item's seq); `import` writes opener links (`--no-opener` to skip) and
  `export` always turns them back into links relative to the tracker file, so the repo file is unchanged. Applied to smc-resiliency Bugs (7 items, 8 links); the operator confirmed a click in BUG-41
  opens VS Code.
- `references/items-and-edits.md`: Learned 2026-11-11, Pad strips vscode:// and relative links go nowhere; write opener links.

## 20261110_2055 — tracker import spike noted for the trial review

### Changed

- Side agent: imported closed bugs and features count as done on 10 Nov. Checked in UNC: `next`, `stale` and the dashboard are not flooded; today's changelog lists 43 imported closures. Operator: keep
  both collections as work and discount the spike; noted on UNC TASK-20 and in guidelines section 6 step 6.
