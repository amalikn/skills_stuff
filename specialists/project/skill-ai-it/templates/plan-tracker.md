---
Title: Plan tracker
Category: living-tracker
Status: current
Authority: >-
  index of which document governs each topic and where each stage stands; it points, it does not decide: decisions live in SCRATCHPAD Recent
  decisions (and any decision register the project keeps), designs in the governing documents named here
Owner: agents keep it current at every slurp and whenever a stage or a governing document changes
Last reviewed: 2026-10-22
Summary: >-
  One page to answer "which file has the current plan, which stage are we at, what comes next": where the project stands, the dated plan, what
  is next with links to where each item starts, the governing document per topic, decisions not yet folded in, and every stage.
---

# Plan tracker

Read this page first; open a document only when its row says you need it. Every named section, stage, risk, decision and drawing links to the exact place it lives.

## Contents

- [Where we are](#where-we-are)
- [What next](#what-next)
- [Which document to follow](#which-document-to-follow)
- [Decided but not yet in the designs](#decided-but-not-yet-in-the-designs)
- [Stages](#stages)
- [How this page is kept](#how-this-page-is-kept)

## Where we are

As of {today}. TODO: one line on the live state (what runs where, what is built, what is not).

1. **TODO workstream ([TODO stage](stage-tracker.md#TODO)):** where it stands and what comes next, each named section linked.
2. **Waiting on the operator:** TODO, each item with its date and the stage it unblocks.

Horizon: TODO, the plan's next milestone dates (from the [Timeline](#timeline)).

### Timeline

Generated from [plan-timeline.yaml](plan-timeline.yaml) by skill-ai-it's `plan_timeline.py` (`just plan-timeline`). Edit the YAML, never the block.

## What next

In order. The table is the summary; each row links to a block below that says what is needed, why now, what is already in hand and how to
tell it is done. Owner is who acts.

| #   | Next | Owner | By | Done when |
| --- | --- | --- | --- | --- |
| 1   | [TODO: the action](#1-todo-the-action) | TODO | TODO | TODO: one-line summary of the checklist below |

### 1. TODO: the action

- **What is needed:** TODO: the work or choice, with options or steps and links to [the exact section](TODO.md#TODO).
- **Why now:** TODO: the stage or plan date that waits on it.
- **In hand:** TODO: results, proposals or evidence that already exist.
- **Done when:** [ ] TODO: a check a reader can verify, naming the record that changes · [ ] TODO.

## Which document to follow

"Follow" is the governing document for that topic. "Input" is evidence or a proposal it draws on; "history" is kept for the record only.

| Topic | Follow | Its state | Inputs and history (do not follow these) |
| ----- | ------ | --------- | ---------------------------------------- |
| TODO  | [TODO](TODO.md) | TODO      | TODO                                     |

## Decided but not yet in the designs

Decisions made but not yet written into the governing document; each row is cleared when the design carries it.

| Decision | Goes into | Done |
| -------- | --------- | ---- |

## Stages

Generated from target-map.yaml by skill-ai-it's `target_map.py` (`just target-map`, `embed:` this page under this heading). Edit the map, never the table.

## How this page is kept

- Updated in the same pass as the change it reflects: a stage moving, a document becoming governing or historical, a decision made or folded in.
- Where we are carries an "As of" date; it is rewritten (not appended) whenever the state it describes changes.
- The Stages table and the Timeline are generated; edit target-map.yaml and plan-timeline.yaml, never the blocks.
- Every reference links to the exact section, stage or drawing; table rows stay on one line. `just check` runs `anchor_links.py` and `plan_tracker.py --check`.
- Every slurp checks this page against SCRATCHPAD, ROADMAP and the stage tables and fixes this page, not those.
- A new document gets a row in "Which document to follow" when it is created; one that stops governing moves to "Inputs and history".
