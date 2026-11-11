---
title: "Bootstrap and refresh ask whether to link a Pad workspace"
status: accepted
tags: [pad]
---

Added 2026-11-11; [AGENTS.md](../../AGENTS.md) (Working rules) has one line pointing here.

## Rule

`bootstrap` and `refresh` ask once whether the repo should be linked to a Pad workspace (skill-pad) when it has no `.pad.toml`. The question
suggests a workspace name (the repo folder's name) and offers the existing workspaces too, because several repos may share one workspace.
The answer is acted on through skill-pad; "no" is recorded so refresh does not ask again. Detail:
[references/pad-workspace.md](../../references/pad-workspace.md).

## Rationale

Operator, 2026-11-11: "it should ask if pad needs to be initialized for that particular repo ... suggesting the name for the workspace ...
multiple projects might be using the same workspace".
