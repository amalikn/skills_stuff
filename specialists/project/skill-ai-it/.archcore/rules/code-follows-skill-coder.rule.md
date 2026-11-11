---
title: "Code follows skill-coder: code map, ruff on new files, tests"
status: accepted
tags: [code]
---

Added 2026-11-11; [AGENTS.md](../../AGENTS.md) (Working rules) has one line pointing here.

## Rule

Invoke `skill-coder` before adding or changing a script (purpose header, docstrings with Args/Returns/Raises, `--apply` for writes, timeouts,
tests, measured runtime). Every script has a decided status in [code-map.toml](../../code-map.toml) (this pack's own tooling: `promoted`,
2026-11-11); a new script gets its entry in the same pass. Python is linted and format-checked by ruff ([ruff.toml](../../ruff.toml): two-space
indent, 160 columns) in `just lint`, part of `just check`; files from before 2026-11-11 are excluded until a reformat is decided, and a new file
is never added to the exclusions. Never silence a linter inline.

## Rationale

Operator, 2026-11-11: skill-ai-it gets the lint config, code map and the rest "like we do in our other skills".
