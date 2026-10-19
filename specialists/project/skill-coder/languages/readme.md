---
Title: Language overrides
Category: reference
Status: current
Authority: local-supplement
Scope: The per-language override layer of skill-coder and the contract each file follows
Last reviewed: 2026-10-19
Summary: >-
  How a language file may tighten, loosen with a stated reason, or add tool commands to a core rule, the precedence of
  project rules over both, and the list of language files.
---

# Language overrides

## The contract

The core rules in `../references/` are language-agnostic. A file here may, for one language:

| Action                                                                                               | Requirement                                                            |
| ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Tighten** a core rule (a smaller budget, a stricter lint set)                                      | Say which core rule and why                                            |
| **Loosen** a core rule (a larger function budget for a verbose language)                             | State the reason in the same row; a loosening without a reason is void |
| **Add** the language's tools and commands (formatter, linter, type checker, test runner, doc convention) | Name the authoritative source, and the version checked or UNVERIFIED   |
| **Map** a core rule to the language's idiom (errors as values, `Result`, exit status)                | Point at the core reference it maps                                    |

A file never contradicts a core rule silently, and never removes a safety rule. Precedence, highest first:

```text
project's own rules (AGENTS.md, code standards, config files)
        >  languages/<lang>.md
        >  references/*.md (core)
```

Before using any command here, read what the project already pins and configures (`.mise.toml`, the language manifest, the tool's config file) and use that; these files say what to look for, not what
to install ([../references/tooling-and-runtime.md](../references/tooling-and-runtime.md), [../references/runtime-boundaries.md](../references/runtime-boundaries.md)).

## Shape of each file

Each language file has the same sections, so it can be edited later without restructuring: Authoritative sources; Tools; Core rule mapping (a table keyed by the core reference); Size and limit tweaks;
Open items. Evidence that is thin is marked UNVERIFIED and left as an editable stub.

## Files

| File                     | Covers                                                      |
| ------------------------ | ----------------------------------------------------------- |
| [python.md](python.md)   | Python 3 scripts, packages and services                     |
| [shell.md](shell.md)     | Bash and POSIX sh scripts                                   |
| [javascript-typescript.md](javascript-typescript.md) | JavaScript and TypeScript, Node and browser                 |
| [go.md](go.md)           | Go modules and commands                                     |
| [rust.md](rust.md)       | Rust crates                                                 |
| [sql.md](sql.md)         | SQL queries, migrations and SQL embedded in other languages |
| [yaml-json-toml.md](yaml-json-toml.md) | Data and configuration files                                |
| [ansible.md](ansible.md) | Ansible playbooks, roles, inventories and Jinja2 templates |

To add a language, copy the shape of an existing file, add a row here, add a scenario to `../tests/scenarios.md`, and add a CHANGELOG line.
