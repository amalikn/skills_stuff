---
Title: Session record 2026-11-19 (periodic review of every skill pack, 90-day window, rotation fixes)
Category: session-record
Status: closed
Authority: built from the raw transcript (transcript_passes.py: 11 typed messages, 8 mid-turn, 13 answers; 965 side-effect lines; 21 sub-agent runs) and git log
Scope: skills_stuff session 1c2cb9b4, 2026-11-19 15:47 to 17:05 (local), started in skill-coder; touched 16 skill packs, governance and local-knowledge-ansible
Last reviewed: 2026-11-19
Summary: >-
  Whole-chat closeout: skill-coder's 33 overdue review dates grew into a full review of 323 docs in 16 packs on a 90-day window, with rotation, adoption and
  write-back-test bugs fixed, identifiers redacted, versions verified, a playbook retired, a Pad workspace created and three scripts promoted.
---

# Session record 2026-11-19 (17:00)

Slurp close of the whole chat (operator: "once done slurp close the whole chat in detail, write back to skills, add/update scripts, commit and push, slurp close again"). Passes from the raw
transcript, not a summary: 11 typed messages, 8 mid-turn notes, 13 question answers, 965 side-effect lines, 21 sub-agent runs (every report delivered in full in the session). Boundary: none (no
earlier slurp of this conversation), so the whole chat is covered. Summary entries: each pack's CHANGELOG of 2026-11-19.

## Contents

- [Operator messages and their destinations](#operator-messages-and-their-destinations)
- [Coverage table](#coverage-table)
- [Writes outside the repositories](#writes-outside-the-repositories)
- [Read-only reads](#read-only-reads)
- [Incidents](#incidents)
- [Commits](#commits)
- [Follow-ups by owner](#follow-ups-by-owner)

## Operator messages and their destinations

| #   | Message (short)                                                                                   | Destination                                                                                |
| --- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1   | "skill-coder review dates ... 33 ... What's happening here?"                                      | Explained (doc_freshness 30-day window from 2026-10-19); row C1                            |
| 2   | "do all.."                                                                                        | Review of 32 skill-coder docs by 4 agents + coordinator; efb81fa0; CHANGELOG               |
|     |                                                                                                   |   0.2.0 (archived)                                                                         |
| 3   | Side note: all 31 will fall due together on 19 Dec                                                | Asked; operator chose "Leave as is" (row C4); later superseded by the 90-day window        |
| 4   | "run skill-ai-it refresh"                                                                         | govern run; 2439939e; Unreleased-move bug undone and logged in skill-ai-it SCRATCHPAD      |
| 5   | Side note: the review changed rules (production read-only proof)                                  | Asked; clause narrowed to "where the project authorises it" (a3560e57; testing.md)         |
| 6   | "What do you again? ... take care of them now. I don't want to review them again."                | Asked; operator chose stop monthly review + fix leftovers (c0699498)                       |
| 7   | Side note: switching off review removes drift detection                                           | Answered with the 3-month compromise; operator later chose 90 days                         |
| 8   | "Are there any other skill which also need this sort of regular review"                           | Survey of 16 packs (now `just freshness-survey` in skill-ai-it)                            |
| 9   | "what is the cause or the logic for the review?"                                                  | Answered from the UNC OKF assessment 2026-10-10 (option B); 30-day number has no           |
|     |                                                                                                   |   recorded rationale                                                                       |
| 10  | "go through all of them, address the issues, fix them, and make it like a three-month review"     | 9 review agents, 323 docs; `--window-days 90` in 16 justfiles; governance guide 2f8de8f    |
| 11  | Side note: review dates do not mean vendor facts verified                                         | Doubtful facts collected; operator chose verify (row 13 answers)                           |
| 12  | Side note: nautobot hit by the same-minute rotation overwrite                                     | Restored 0.2.0 from git; test reads archives (236a4a62)                                    |
| 13  | "ask questions"                                                                                   | Four questions asked; answers rows 14-17                                                   |
| 14  | Answer: redact all identifiers                                                                    | 93ff6aaf (smc, nautobot, openwisp, skill-ai-it, goal-guard)                                |
| 15  | Answer: diagrams diff first, then decide; later re-render both                                    | cc01e14b after a scratch diff                                                              |
| 16  | Answer: verify and update versions                                                                | c41b8dd6, 38d02d62, 3806c291                                                               |
| 17  | Answer: retire smc_update_php.yml, renumber patterns, pad --op-key, smc CHANGELOG line            | 0c22e11 + e90bc3c6; 4862bb11; 3806c291; 02d96bea                                           |
| 18  | "once done slurp close ... write back ... scripts ... commit and push ... slurp close again"      | This record; write-backs and scripts below; push at the end                                |
| 19  | Side note: redactions remain in git history                                                       | Open decision for the operator (history rewrite is destructive): Follow-ups                |
| 20  | Answers on the first refresh round: commit then refresh; leave dates; fix rotate_records; Pad     | 2439939e; 4484e209; 69877c53                                                               |
|     |   "skills" shared by all skills_stuff                                                             |                                                                                            |

## Coverage table

| #   | Item                                              | Type            | memory-keeper key               | project-context | Governed file                                          | Status      |
| --- | ------------------------------------------------- | --------------- | ------------------------------- | --------------- | ------------------------------------------------------ | ----------- |
| C1  | skill-coder check red on 33 review dates (30-day  | finding         | skills_stuff.review-20261119    | note            | skill-coder CHANGELOG                                  | done        |
|     |   window from 2026-10-19)                         |                 |                                 |                 |   0.2.0 (docs/history/changelog-20261119_1603.md)      |             |
| C2  | Review of 32 skill-coder docs (rules aligned with | repo change     | skills_stuff.review-20261119    | note            | skill-coder CHANGELOG 0.2.0                            | done        |
|     |   Learned entries)                                |                 |                                 |                 |                                                        |   efb81fa0  |
| C3  | Production read-only proof clause narrowed to     | operator        | skills_stuff.decisions-20261119 | decision        | skill-coder references/testing.md; CHANGELOG           | done        |
|     |   project authorisation                           |   decision      |                                 |                 |                                                        |   a3560e57  |
| C4  | Stagger dates: "Leave as is" (superseded by       | operator        | skills_stuff.decisions-20261119 | decision        | this record                                            | superseded  |
|     |   90-day window)                                  |   decision      |                                 |                 |                                                        |             |
| C5  | rotate_records read "this file" as a tracker      | incident + fix  | skills_stuff.incidents-20261119 | note            | skill-ai-it CHANGELOG; 4484e209; acf8d9ac              | fixed       |
|     |   path; files named `this` in skill-coder         |                 |                                 |                 |                                                        |             |
|     |   and skill-drawio                                |                 |                                 |                 |                                                        |             |
| C6  | govern moved CHANGELOG Unreleased out as a        | incident        | skills_stuff.incidents-20261119 | note            | skill-ai-it SCRATCHPAD (open fix); undone in 2439939e  | open (tool) |
|     |   reference file                                  |                 |                                 |                 |                                                        |             |
| C7  | skill-coder 0.2.0 cut and archived to fit         | operator        | skills_stuff.decisions-20261119 | decision        | skill-coder CHANGELOG                                  | done        |
|     |   the budget                                      |   decision      |                                 |                 |                                                        |   2439939e  |
| C8  | Pad workspace "skills" for all of skills_stuff;   | operator        | skills_stuff.pad-workspace      | decision        | skill-pad CHANGELOG; .pad.toml                         | done        |
|     |   conventions baseline                            |   decision +    |                                 |                 |                                                        |   69877c53  |
|     |                                                   |   operational   |                                 |                 |                                                        |             |
|     |                                                   |   event         |                                 |                 |                                                        |             |
| C9  | skill-pad `conventions` recipe split              | finding + fix   | skills_stuff.incidents-20261119 | note            | skill-pad references/cli-reference.md                  | done        |
|     |   spaced arguments                                |                 |                                 |                 |   Learned 2026-11-19                                   |   69877c53  |
| C10 | Stop monthly review of the 32 (Review by          | operator        | skills_stuff.decisions-20261119 | decision        | skill-coder CHANGELOG                                  | superseded  |
|     |   2027-05-19), later replaced by the              |   decision      |                                 |                 |                                                        |             |
|     |   90-day window                                   |                 |                                 |                 |                                                        |             |
| C11 | Write-back contract test: 9 headers repaired, 6   | repo change     | skills_stuff.review-20261119    | note            | skill-coder CHANGELOG                                  | done        |
|     |   logged, sources C-C83..85                       |                 |                                 |                 |                                                        |   c0699498  |
| C12 | Why the review exists: OKF assessment option      | finding         | skills_stuff.review-window      | note            | governance naming-and-file-summary-guide               | answered    |
|     |   B, 2026-10-10                                   |                 |                                 |                 |   (Freshness keys)                                     |             |
| C13 | 90-day review window for skill                    | operator rule   | skills_stuff.review-window      | decision        | governance guide 2f8de8f; 16 justfiles                 | done        |
|     |   packs (`--window-days 90`)                      |                 |                                 |                 |                                                        |             |
| C14 | adopt_governed_files copied --window-days         | finding + fix   | skills_stuff.incidents-20261119 | note            | skill-ai-it CHANGELOG; test                            | done        |
|     |   onto role_check                                 |                 |                                 |                 |                                                        |   9ece8f1a  |
| C15 | Periodic review of 323 docs in 16 packs           | repo change     | skills_stuff.review-20261119    | note            | each pack's CHANGELOG 2026-11-19                       | done        |
|     |   (9 agents)                                      |                 |                                 |                 |                                                        |   (commits  |
|     |                                                   |                 |                                 |                 |                                                        |   below)    |
| C16 | Same-minute rotation overwrote archives; nautobot | incident + fix  | skills_stuff.incidents-20261119 | note            | skill-ai-it CHANGELOG; nautobot 236a4a62;              | fixed       |
|     |   0.2.0 and a drawio line lost, restored          |                 |                                 |                 |   drawio acf8d9ac                                      |             |
| C17 | nautobot contract test read only CHANGELOG.md; my | incident + fix  | skills_stuff.incidents-20261119 | note            | skill-nautobot CHANGELOG                               | fixed       |
|     |   rotation broke it in 94a9bec7                   |                 |                                 |                 |                                                        |   236a4a62  |
| C18 | mikrotik provisioning script edited by 0c11906e   | incident + fix  | skills_stuff.incidents-20261119 | note            | skill-mikrotik commit 712e6364; SCRATCHPAD             | fixed       |
|     |   (docstring, CRLF); restored, finding baselined  |                 |                                 |                 |                                                        |             |
| C19 | Adoption-era Review by dates undercut the window  | repo change     | skills_stuff.review-window      | note            | 033a25cf                                               | done        |
|     |   (10 files); agent-stack report reclassified     |                 |                                 |                 |                                                        |             |
| C20 | Redaction of identifiers in pack text             | operator        | skills_stuff.decisions-20261119 | decision        | 93ff6aaf                                               | done        |
|     |                                                   |   decision      |                                 |                 |                                                        |             |
| C21 | Identifiers remain in git history; company-domain | undecided       | skills_stuff.open-followups     | note            | skill-coder SCRATCHPAD; this record                    | open        |
|     |   packs (smc, cambium) hold site data by design   |   proposal      |                                 |                 |                                                        |             |
| C22 | Versions of record: Nautobot 3.2.9 (+SSoT 4.7.0,  | operator        | skills_stuff.decisions-20261119 | decision        | nautobot, proxmox, pad CHANGELOGs                      | done        |
|     |   DLM 4.2.0), PVE 9.2 / 9.2.26, pad 0.21.0,       |   decision      |                                 |                 |                                                        |             |
|     |   --op-key commands                               |   + finding     |                                 |                 |                                                        |             |
| C23 | smc_update_php.yml retired (no callers)           | operator        | skills_stuff.decisions-20261119 | decision        | local-knowledge-ansible 0c22e11; skill-smc e90bc3c6;   | done        |
|     |                                                   |   decision +    |                                 |                 |   ADR-007 amendment open                               |             |
|     |                                                   |   operational   |                                 |                 |                                                        |             |
|     |                                                   |   event         |                                 |                 |                                                        |             |
| C24 | design-patterns: 9 patterns moved, exact-commit   | operator        | skills_stuff.decisions-20261119 | decision        | skill-coder CHANGELOG                                  | done        |
|     |   gate P-77                                       |   decision      |                                 |                 |                                                        |   4862bb11  |
| C25 | Flow drawings re-rendered after a semantic diff   | operator        | skills_stuff.decisions-20261119 | decision        | cc01e14b; skill-drawio Learned 2026-11-19              | done        |
|     |                                                   |   decision      |                                 |                 |                                                        |             |
| C26 | First diagram diff missed compressed pages        | incident        | skills_stuff.incidents-20261119 | note            | skill-coder generated-artifacts.md Learned 2026-11-19  | corrected   |
|     |   (reported "0 label changes"; truth: generated   |                 |                                 |                 |                                                        |             |
|     |   titles changed)                                 |                 |                                 |                 |                                                        |             |
| C27 | Script: freshness survey (16 packs)               | script          | skills_stuff.scripts-20261119   | note            | skill-ai-it scripts/checks/freshness_survey.py,        | promoted    |
|     |                                                   |                 |                                 |                 |   `just freshness-survey`, tests                       |             |
| C28 | Script: drawing diff                              | script          | skills_stuff.scripts-20261119   | note            | skill-drawio scripts/compare_drawings.py,              | promoted    |
|     |                                                   |                 |                                 |                 |   `just compare-drawings`, tests                       |             |
| C29 | Script: write-back entry scan                     | script          | skills_stuff.scripts-20261119   | note            | skill-coder tests/test_package_contract.py now collects | promoted    |
|     |                                                   |                 |                                 |                 |   all and reads topic files                            |   into      |
|     |                                                   |                 |                                 |                 |                                                        |   the test  |
| C30 | Script: word-loss scan of a pack diff (lost.sh)   | script          | skills_stuff.scripts-20261119   | note            | covered by skill-coder scripts/reflow_lossless.py      | not needed  |
|     |                                                   |                 |                                 |                 |   (per file)                                           |             |
| C31 | Scripts: header fixes, redaction, renumber.py,    | script          | skills_stuff.scripts-20261119   | note            | one-off edits                                          | not needed  |
|     |   routing inserts, CHANGELOG recoveries           |                 |                                 |                 |                                                        |             |
| C32 | Review agents' unfixed findings, per pack         | open task       | skills_stuff.open-followups     | note            | each pack's SCRATCHPAD Open items (agent-stack: its    | routed      |
|     |                                                   |                 |                                 |                 |   tracker; ascii: ROADMAP)                             |             |
| C33 | Doubtful external facts left after verification   | open task       | skills_stuff.open-followups     | note            | packs' SCRATCHPAD Open items                           | routed      |
|     |   (POSIX pipefail, stdbuf, Parallels limits,      |                 |                                 |                 |                                                        |             |
|     |   codex-cli defaults, aafigure licence)           |                 |                                 |                 |                                                        |             |
| C34 | Go/Rust indentation vs the two-space rule         | undecided       | skills_stuff.open-followups     | note            | skill-coder SCRATCHPAD                                 | open        |
|     |                                                   |   proposal      |                                 |                 |                                                        |             |
| C35 | rotate_records vs doc_freshness line count off by | finding         | skills_stuff.incidents-20261119 | note            | skill-ai-it SCRATCHPAD                                 | open        |
|     |   one (trailing blank line)                       |                 |                                 |                 |                                                        |             |
| C36 | skill-ai-it self-check red on nine size           | finding         | skills_stuff.open-followups     | note            | skill-ai-it SCRATCHPAD                                 | open        |
|     |   findings (pre-existing)                         |                 |                                 |                 |                                                        |             |
| C37 | Side agents' notes (5)                            | operator        | skills_stuff.review-20261119    | note            | rows 3, 5, 7, 11, 12, 19 above                         | routed      |
|     |                                                   |   message       |                                 |                 |                                                        |             |

## Writes outside the repositories

1. Pad (local server, workspace "skills"): created by `pad workspace init skills --template startup` from the skills_stuff root (operator: create "skills" shared by all skills_stuff); conventions
   baseline applied, 7 changes, a second plan showed 0. The two `pad/SKILL.md` copies init wrote were deleted.
2. Company repo ansible-wifi (local only, untracked): the symlink `smc_update_php.yml` and its `.git/info/exclude` line 77 removed (backup of exclude in the session scratchpad); nothing tracked or
   pushed there.
3. Web reads for verification only (GitHub releases API, pve.proxmox.com roadmap and package index): no writes.

## Read-only reads

- `pad auth whoami`, `pad workspace list`, `pad help ... --format md`, `pad --version`.
- crontab and `~/Library/LaunchAgents` searched for callers of smc_update_php.yml (none).

## Incidents

1. **Stray `this` trackers (skill-coder, skill-drawio):** rotate_records.py took "this file, Open items" as a path. Fixed in the tool with a test; both files removed or moved.
2. **govern moved Unreleased out of skill-coder's CHANGELOG:** undone by hand; release 0.2.0 cut instead; tool fix open (skill-ai-it SCRATCHPAD).
3. **Same-minute archive overwrite:** two rotations in one minute wrote the same archive name; skill-drawio lost a line (restored before commit), skill-nautobot lost its 0.2.0 section (restored after
   commit 94a9bec7 in 236a4a62). Tool fixed: free_archive_name, deterministic test.
4. **nautobot tests broken by my commit 94a9bec7:** its contract test read CHANGELOG.md only; fixed to read the archives.
5. **A fabricated rationale in the governance guide:** "monthly reviews cost more than they caught" was written without the operator saying it; replaced with the operator's words before commit.
6. **Diagram diff under-reported:** the first ad-hoc diff ignored compressed pages; the operator was told "0 label changes"; the full diff showed 1 label and 4 text changes, all the renderer's own
   generated titles. The re-render decision stands; the correction is in the closeout report.
7. **mikrotik provisioning script changed by 0c11906e (2026-10-10):** a docstring and CRLF->LF in a "never edit" file; restored to sha256 1f346831.
8. **Hook-blocked commands:** two Bash commands (`eval`, `rm -rf`, a combined hash pipeline) blocked by the OPA hook; rerun as plain steps.

## Commits

See the list appended below (35 commits across skills_stuff, governance and local-knowledge-ansible), plus the closeout commit and push.

## Persistence and second close

- First close: skills_stuff `a7ee5fe7` and wiki_stuff `55ecc56` (skill-coder page, its index and log lines only) committed and pushed (`git -C <repo> push origin HEAD`); before the push,
  skill-coder and skill-drawio check and test exited 0, skill-ai-it test 0 and check 1 on its pre-existing size findings only.
- Not pushed, by the operator's push-scope rule (only the active repo and the wiki): governance `2f8de8f` (review window in the Freshness keys) and local-knowledge-ansible `0c22e11`
  (smc_update_php.yml retired). Push them on the operator's word.
- memory-keeper (channel skills_stuff): `skills_stuff.review-20261119`, `.review-window`, `.decisions-20261119`, `.incidents-20261119`, `.scripts-20261119`, `.open-followups`,
  `session.closeout.20261119.skills-review`; project-context skills_stuff: 3 notes and 8 decisions; checkpoints `slurp-20261119-skills-review` in both.
- Second close (operator: "slurp close again"): Step 6b re-run over the whole chat after the push; writeback-status showed every engaged skill clean except skill-coder's untracked
  regenerated `.ai-context/` (committed with this update, as eight other packs track theirs); freshness survey after the last commit (baseline ignored): 0 overdue in 15 packs; skill-smc 1, its `scripts/README.md` (another session's file, no `Last reviewed`, baselined; in its SCRATCHPAD follow-ups).

- After the second close: tracking skill-coder's `.ai-context/` turned its check red (`no-header` on the generated pack, seen only once tracked); fixed in skill-ai-it file_headers SKIP_PARTS
  with a test (`2a5d56c0`); skill-coder check 0, both packs' tests 0; pushed.

## Follow-ups by owner

- **Operator:** history rewrite for the redacted identifiers (or accept: private repos); whether company-domain packs (skill-smc, skill-cambium) keep site data; Go/Rust indentation rule; ADR-007
  amendment in local-knowledge-ansible (Archcore promote).
- **skill-ai-it:** budget_plan must not move Unreleased; rotate/check line-count off by one; adoption `Review by` +30 ignores the project window; embedded template copies drifted; self-check size
  findings; the rest in its SCRATCHPAD.
- **Each pack:** its SCRATCHPAD "Review follow-ups (periodic review 2026-11-19)" line.
- **Next review:** the packs come due together around 2027-02-17 (`just freshness-survey --scan /Volumes/Data/_ai/_skills/skills_stuff --window-days 90 --by 2027-02-17`).

### Commit list

- efb81fa0 skill-coder: periodic review of 32 docs (doc-freshness window from 2026-10-19 expired 2026-11-18)
- a3560e57 skill-coder: production read-only proof needs the project's authorisation; stray `this` removed; Learned 2026-11-19 header values used as pat
- 4484e209 skill-ai-it: rotate_records.py ignores an Open items tracker value that is not a relative markdown path
- 2439939e skill-coder 0.2.0; skill-ai-it refresh (govern): navigation upgrade, Budget keys, adopt_code_map in govern
- 3f97a77a skill-ai-it: ROADMAP item for budget_plan moving a CHANGELOG's Unreleased out; tracker-path item marked fixed; CHANGELOG rotated back under b
- 69877c53 Pad workspace "skills" for all of skills_stuff (.pad.toml at the repo root, conventions baseline applied: 7 changes, re-plan 0); skill-pad: c
- c0699498 skill-coder: write-back contract test green; 32 reviewed docs get Review by 2027-05-19 (operator)
- 94a9bec7 skill-nautobot: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 0887aeab skill-openwisp: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- b4cf2804 skill-pad: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 712e6364 skill-mikrotik: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 58d3857e skill-cambium: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 51e4ef4e skill-coder: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 820a7399 skill-proxmox: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- a3b8d422 skill-vagrant: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 9ece8f1a skill-ai-it: periodic review of 55 docs; rotate_records no longer overwrites a same-minute archive; role_check line drops --window-days; temp
- acf8d9ac skill-drawio: periodic review of 49 docs; 90-day review window; stray `this` tracker moved to docs/trackers; write-back test green
- 236a4a62 skill-nautobot: restore CHANGELOG 0.2.0 lost by a same-minute double rotation (94a9bec7); write-back test reads rotated archives
- 811dd1b5 skill-goal-guard: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 664838b1 skill-ascii-diagrams: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- b1215da8 skill-knowledge-curator: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- ba00a16d skill-eval-manager: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 0217b98c agent-stack: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 9da296e7 skill-smc: periodic review of every due doc (operator, 2026-11-19); 90-day review window
- 033a25cf Skill packs: drop adoption-era Review by dates that undercut the 90-day window; agent-stack 2026-09-01 classification is a report
- 4862bb11 skill-coder: design-patterns misplaced patterns moved into Patterns; exact-commit pre-push gate is P-77 (operator)
- 93ff6aaf Skill packs: redact identifiers in pack text (operator, 2026-11-19)
- e90bc3c6 skill-smc: smc_update_php.yml retired (refs 18 and 19)
- c41b8dd6 skill-nautobot: version of record verified against primary sources (operator, 2026-11-19)
- 38d02d62 skill-proxmox: version of record verified against primary sources (operator, 2026-11-19)
- 3806c291 skill-pad: version of record verified against primary sources (operator, 2026-11-19)
- cc01e14b skill-vagrant, skill-goal-guard: flow drawings re-rendered from their YAML (operator, 2026-11-19)
- 02d96bea skill-smc v0.15.8: CHANGELOG entry for today's review, redaction and smc_update_php.yml retirement
- 2f8de8f governance: naming-and-file-summary-guide: review window per project; skill packs in skills_stuff use 90 days (operator, 2026-11-19)
- 0c22e11 local-knowledge-ansible: ansible-wifi: retire playbooks/smc_update_php.yml (operator approved 2026-11-19)

## Dependency reviews

Every document whose `Last reviewed` this session's commits set to 2026-11-19, from git (323 documents: 132 accurate, date only; 191 edited). Read scope: the whole file, end to end, by a review agent under the shared brief (rules: references resolve, body agrees with its Learned entries, Summary and Scope match, no external fact changed without a stored source) or by the coordinator.

| Document | Full read scope before edits | Review result |
| --- | --- | --- |
| `project/skill-coder/references/version-control-and-review.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (126 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/operations-cookbook.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/upgrade-and-troubleshooting.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-nautobot/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/python/learned-other.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (11 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/references/18_local-knowledge-ansible.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (10 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/references/19_smc-change-role.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (21 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-nautobot/references/operations-cookbook.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (14 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-openwisp/references/deployment-and-recovery.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/docs/history/changelog/changelog-20261119_1648.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (31 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/finishing.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/phases-1-3.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (14 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/references/pilot-plan.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/design-patterns.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (484 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (9 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-knowledge-curator/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (9 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/ARCHITECTURE.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (10 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/docs/audits/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-smc/docs/trackers/open-items-20261010_1821.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-smc/references/17_site-ata-dallas-delta.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (10 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/references/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `agent-stack/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `agent-stack/MEMORY.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (10 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `agent-stack/docs/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `agent-stack/docs/trackers/open-items-20261010_1821.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (16 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `agent-stack/personas/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `skills/skill-eval-manager/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `skills/skill-eval-manager/docs/history/changelog-20261119_1640.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (63 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/docs/catalog.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (21 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/docs/knowledge-curator-foss-implementation-spec-v2.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/docs/project-knowledge-curator-design-v1.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (23 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/docs/research/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/references/archive-safety.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-knowledge-curator/references/authority-and-promotion.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-knowledge-curator/references/claim-model-and-taxonomy.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/references/conflicts-and-review.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/references/evaluation.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (12 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/references/feature-inventory.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (13 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/references/invocation-contract.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/references/workflow.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-knowledge-curator/scripts/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ascii-diagrams/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/ROADMAP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (12 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/references/checking-diagrams.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/references/drawing-diagrams.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/references/evolution-and-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ascii-diagrams/references/extensions.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ascii-diagrams/references/fixing-diagrams.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/references/graph-layout.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ascii-diagrams/references/reading-diagrams.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ascii-diagrams/references/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (1 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/scripts/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ascii-diagrams/tests/eval-procedure.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ascii-diagrams/tests/scenarios.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/docs/catalog.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/docs/goal-guard-research-pack/00-executive-decision.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/docs/goal-guard-research-pack/01-milestones-and-roadmap.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/docs/goal-guard-research-pack/02-ctps-implementation.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/docs/goal-guard-research-pack/03-acceptance-test-matrix.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/docs/goal-guard-research-pack/04-vikunja-integration-design.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/docs/goal-guard-research-pack/05-implementation-backlog.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/docs/goal_guard_agent_kickoff_v1_7.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/references/decision-rules.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/references/enforcement-and-hooks.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/references/evolution-and-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/references/feature-inventory.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/references/hub-management-and-dates.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/references/mvp-contract-and-change-control.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/references/project-layout-and-storage.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/references/snapshot-and-restore.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/references/test-catalog.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/references/vikunja-integration.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (17 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-goal-guard/references/whats-next-and-portfolio.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-goal-guard/roadmap.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-nautobot/docs/history/changelog-20261119_1628.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (45 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/ROADMAP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (23 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/SETUP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/docs/changelog-reference-1-20261026_2147.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/docs/history/changelog-20261119_1635.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (37 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/docs/performance-review-20261028_2317.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/docs/trackers/open-items-20261028_2305.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (27 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/prototypes/business-views/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/charts-and-trace.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (43 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/data-first-diagrams.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (28 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/evolution-and-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/export-and-self-review.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (34 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/file-format.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/layout-and-routing.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (36 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/layout-audits.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/reading-drawings.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/screenshots/20261020-group-columns/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261020-thin-track-order/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-component-shapes/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-flow-page-climb-arrow/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-flow-page-room/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-flow-router/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-option-pages/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-options-page/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261021-shapes-adopted/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261023-decision-branch-labels/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261023-e2e-family-pages/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261023-palette-export/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261023-tips-tags/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-click-toggle/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-e2e-click-isolate/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-drawio/references/screenshots/20261026-e2e-family-colours/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-e2e-loops/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-e2e-step-totals/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-joint-moves/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-loop-heading-clearance/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-own-page/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261026-row-moves/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261027-labels-routing/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261029-unc-overview-real-route/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261102-charts-lanes-bpmn/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261106-fold-lanes/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261106-measured-row-wrap/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261106-notes-band-crossing/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261106-step-box-sizing-and-legend-links/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261107-compact-diamonds-and-store-text/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261118-continuum-first-slice/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/screenshots/20261118-decision-page-after-a-register-decision/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-drawio/references/visual-style.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/ARCHITECTURE.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/ROADMAP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (26 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/docs/central-project-tooling-plan-20261111_1141.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/docs/history/changelog/changelog-20261119_1639.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (23 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/docs/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/docs/reviews/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/docs/trackers/open-items-20261010_1830.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/patterns/archcore-routing.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/drift-audit.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (20 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/memory-bank-structure.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/patterns/navigation-control-automation.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/navigation/change-rules.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/navigation/read-order-and-sources.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/navigation/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/navigation/recovery-and-audit.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/patterns/navigation/task-routing.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (28 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/patterns/script-task-audit-checklist.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (21 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/background.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/compaction-recovery.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/files-ai-navigation.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/files-architecture-conventions-roadmap.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/files-context-map.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/files-history.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/files-readme-agents-claude.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/files-records.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/files-support.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/generation-policy.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/governance-checker.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/governed-file-roles.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/inputs.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/managed-blocks.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/navigation-automation.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/new-skill.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/package-layout.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/pad-workspace.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/references/pitfalls.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (11 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (20 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/script-task-inventory.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (19 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/references/target-map-and-timeline.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/scripts/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (27 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/templates/AGENTS-plan-tracker-block.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/templates/history-readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (1 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/templates/plan-tracker.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/research-brief.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/seed-folder/parts-readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/seed-folder/research-readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/skill-intake.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-ai-it/templates/skill-seed.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (14 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/references/boxes-and-pinning.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/references/clones-snapshots-and-identity.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/references/evolution-and-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/lab-safety-and-guards.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/licensing-and-editions.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/networking-and-synced-folders.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/operations-cookbook.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/parallels-prlctl.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (11 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/references/providers-and-choice.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/qemu-and-libvirt.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/tool-choice-and-lab-symmetry.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/upgrade-and-troubleshooting.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/references/vagrantfile-and-provisioning.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/references/virtualbox.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-vagrant/tests/eval-procedure.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-vagrant/tests/scenarios.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (23 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/access-control.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (10 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/api-and-cli.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/architecture-and-cluster.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/backup-and-restore.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/capability-extension.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/evolution-and-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/ha-and-replication.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/lxc-containers.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/monitoring-and-metrics.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/networking-and-sdn.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/opentofu-bpg-provider.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/qemu-vms.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (14 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-proxmox/references/security-certificates-firewall.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/references/storage.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/tests/eval-procedure.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-proxmox/tests/scenarios.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (29 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/AI_NAVIGATION.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (30 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/ROADMAP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (26 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/SETUP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (10 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/ansible.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (33 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/ansible/before-any-change-trace-every-reference.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/ansible/learned-connections.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/ansible/learned-execution.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (40 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/ansible/learned-lint-and-tests.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/ansible/learned-other.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/ansible/learned-templating.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/ansible/learned-tooling.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (25 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/ansible/open-items.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (67 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/go.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/hcl.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/javascript-typescript.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (69 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/python.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (44 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/python/open-items.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (14 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/rust.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (64 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/shell.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (34 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/shell/learned-format-and-lint.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/shell/learned-other.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/shell/learned-processes-and-timeouts.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (38 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/shell/learned-safety.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/shell/open-items.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (16 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/shell/posix-sh.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/languages/sql.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (8 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/languages/yaml-json-toml.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/configuration-and-literals.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (19 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/dependencies.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/references/design-principles.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (11 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/documentation-and-headers.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/efficiency-and-measurement.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/engine-composition.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/errors-and-timeouts.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (70 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/evolution-and-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (12 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/generated-artifacts.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (13 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/module-and-function-shape.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (9 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/naming-conventions.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/refactoring-and-promotion.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (73 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/runtime-boundaries.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-coder/references/safety-and-writes.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/security.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (34 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/testing.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (81 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/references/tooling-and-runtime.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (61 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/templates/project-agents-write-back.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/tests/scenarios.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-cambium/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (5 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-cambium/docs/history/changelog-20261119_1631.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (33 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-cambium/schemas/DIVERGENCE.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-cambium/schemas/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-cambium/schemas/SWEEP-LOG.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-mikrotik/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-mikrotik/SCRATCHPAD.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/docs/history/changelog-20261119_1631.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (28 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/references/01_overview.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/references/02_device-access.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-mikrotik/references/03_routeros-cli-reference.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-mikrotik/references/04_failure-modes.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/references/05_known-issues.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/references/06_provisioning.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-mikrotik/references/07_equipment-and-snmp.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/references/08_routeros-platform-features.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-mikrotik/scripts/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (3 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (12 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/conventions/collection-schemas/readme.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/docs/history/changelog/changelog-20261119_1631.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (26 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/docs/pad-usage-guidelines-20261110_1628.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/docs/trackers/open-items-20261110_1644.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-pad/references/cli-reference.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (109 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/references/integrations.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-pad/references/items-and-edits.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (7 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/references/modes.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-pad/references/playbooks-and-workflows.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-pad/references/upgrade.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `project/skill-pad/references/workspace-context.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (2 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/scripts/README.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (6 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-openwisp/AGENTS.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (4 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-openwisp/references/configuration-management.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-openwisp/references/connections-and-firmware.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-openwisp/references/operations-cookbook.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (11 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-openwisp/references/radius-and-captive-portal.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
| `platform/skill-nautobot/references/app-development.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (16 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-nautobot/references/data-model.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (16 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-nautobot/references/integrations.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (15 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `platform/skill-nautobot/references/operations-and-recovery.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (11 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/docs/history/changelog/changelog-20261119_1605.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (32 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/docs/history/changelog-20261119_1601.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (22 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/docs/history/changelog-20261119_1603.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (177 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-coder/docs/history/changelog-20261119_1554.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (22 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-smc/docs/history/changelog-20261119_1555.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (23 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/docs/history/changelog/changelog-20261119_1552.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (26 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-ai-it/docs/history/changelog/changelog-20261119_1551.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | edited (33 changed lines; see the pack's 2026-11-19 CHANGELOG entry) |
| `project/skill-pad/SETUP.md` | whole file, end to end (review agent under the shared brief, or coordinator for skill-coder root docs) | accurate, date only |
