---
title: The naming mapping is data in naming.toml
type: adr
status: accepted
tags: [checkers, pack-content]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: The naming mapping is data in naming.toml

Status: accepted (operator decision in chat, 2026-10-19: "is it better to have a json or yaml or toml file for the mapping"; promoted 2026-10-19 on the operator's instruction to add the missing
Archcore entries)

## Context

The pack maps each language and kind of name to a case convention (`references/naming-conventions.md`, claims C-C72 to C-C79). A table written by hand in the reference and a separate list in a checker
can drift: what is shown and what is enforced would then disagree.

## Decision

`naming.toml` is the single source. TOML because the helpers read it with the target project's own Python (`tomllib`, stdlib from 3.11), with no parser to install. `scripts/naming_table.py` renders
the table between the generated markers in `references/naming-conventions.md`; `scripts/naming_check.py` checks code file names and `just` recipe names from the same file. A project adds overrides and
reasoned exceptions in its `code-map.toml` `[naming]` section, never by editing the pack's mapping.

## Consequences

- The table is never edited by hand; `just naming-table` regenerates it and `just self-check` fails while it differs from `naming.toml`.
- `tests/test_package_contract.py` (`test_naming_rows_cite_existing_captures`) fails a row whose source capture is missing under `documents/`.
- The convention itself (code files and identifiers follow their language, typed commands are kebab-case, a tool's parser wins) stays pack content in the reference, not in this record.
