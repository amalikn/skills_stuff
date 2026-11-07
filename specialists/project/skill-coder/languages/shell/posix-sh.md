---
Title: shell override - posix sh
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/shell.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The posix sh part of the shell override; the entry file holds the tools and the core rule mapping.
---

# shell: posix sh

Part of [shell.md](../shell.md).

Where a script must run under `/bin/sh` (minimal images, some embedded systems), `pipefail` may be missing on older shells and arrays do not exist; keep such scripts tiny and say in the header why
they are POSIX. UNVERIFIED which target shells support `pipefail`; check the target's shell manual.
