---
Title: YAML, JSON and TOML override
Category: reference
Status: current
Authority: local-supplement
Scope: Data and configuration files - YAML, JSON and TOML - including catalogs, registers and CI configuration
Last reviewed: 2026-10-19
Summary: >-
  A header in each file's native form, explicit booleans and quoted ambiguous strings in YAML, unique keys everywhere,
  yamllint and a schema check, safe loaders only, stable key order for generated files, and data files as the single home of facts.
---

# YAML, JSON and TOML override

## Authoritative sources

YAML 1.2.2 specification, yamllint rules documentation, RFC 8259 (JSON), TOML 1.0.0. Copies: `../documents/research-sources-20261019/`.

## Tools

| Job | Tool | Note |
| --- | --- | --- |
| YAML lint | yamllint (`truthy`, `key-duplicates` and the project's rule set) | VERIFIED_PRIMARY |
| Schema | A JSON Schema or the program's own loader check, run in the closing check | UNVERIFIED stub for a tool choice |
| Format | The project's formatter, if any | Do not reflow a generated file by hand |

## Core rule mapping

| Core reference | In data files |
| --- | --- |
| documentation-and-headers | YAML and TOML: a leading `#` block stating purpose, owner and whether it is generated. JSON has no comments in its grammar, so use a `_meta` object where the consumer allows, or a `readme.md` row |
| design-principles | Data decides, code executes: a fact lives in one data file, and code reads it; split large files into parts with an include list |
| generated-artifacts | Generated YAML or JSON carries a banner (or `_meta.generated_from`) and stable key order |
| security | Load YAML with a safe loader only; never a loader that builds arbitrary objects |
| configuration-and-literals | No secrets in committed data files; reference the secret store entry by name |
| testing | A check that every record answers every required key, with a negative test |

## Format rules

| Rule | Why |
| --- | --- |
| YAML: write booleans as `true` and `false` only; quote strings such as `yes`, `no`, `on`, `off`, `y`, `n` and country codes like `NO` | yamllint's `truthy` rule exists to prevent parsers turning `[yes, FALSE, Off]` into booleans (VERIFIED_PRIMARY); YAML 1.1 parsers still do this (VERIFIED_SECONDARY via yamllint) |
| YAML: quote version strings and values with leading zeros or colons (`"3.10"`, `"0755"`, `"12:30"`) | Unquoted, they can parse as numbers or other types (UNVERIFIED per parser; quoting is always safe) |
| Keys are unique within a mapping or table | JSON: names "SHOULD be unique" (RFC 8259, VERIFIED_PRIMARY), and parsers differ on duplicates; TOML: defining a key multiple times is invalid (VERIFIED_PRIMARY); yamllint `key-duplicates` |
| TOML keys are case-sensitive | TOML 1.0.0 (VERIFIED_PRIMARY) |
| Indent YAML with spaces, two per level unless the project says otherwise | Tabs are not allowed for YAML indentation (UNVERIFIED in the truncated spec copy) |

## Size and limit tweaks

| Item | Value | Reason |
| --- | --- | --- |
| File an agent loads whole | Core 200 lines and 25 KB | Large maps are read one entry at a time through a show command |
| Module and function budgets | Not applicable | Data, not code |

## Open items

- Schema tooling choice and JSON5 or JSONC policy: UNVERIFIED stubs.

> **Learned 2026-10-23** · taplo 0.9.3, biome 2.5.15, djlint 1.47.0 · VERIFIED_PRIMARY (ansible-wifi checkout; a negative test with one
> bad file per language failed each step) · Source: local-knowledge-ansible `ansible-wifi/ansible-wifi-root-governance/{.taplo.toml,
> biome.jsonc,djlint.toml,lint_new.sh}` (uncommitted at writing); taplo and biome docs via context7 · Falsifier: a tool that lints an
> excluded file, or misses a bad new one
> TOML: taplo, `.taplo.toml` at the root with `exclude` globs and `[formatting] indent_string = "  "` (its default), `column_width`; `taplo
> lint` and `taplo fmt --check`. JSON: biome, `biome.jsonc` with `files.includes` = `["**/*.json", "!folder", "!path/file.json", ...]`
> (negations must follow a `**` pattern; a folder is `!folder`, not `!folder/**`, or biome warns useBiomeIgnoreFolder), `formatter.indentWidth
> 2`; pin a release at least two weeks old (`npx -y @biomejs/biome@<version> check`). Both follow symlinks, so local-only folders
> symlinked into a checkout need excluding by name. Jinja2: djlint reads `djlint.toml` (`profile`, `extension`, `indent`, `ignore`,
> `exclude`, `extend_exclude` as a comma-separated string); on non-HTML templates (netplan, shell, Apache) use `--lint` only and ignore
> the H (HTML) rules, which misfire there; never `--reformat` them. djlint does not descend into a symlinked folder: pass the physical path
> with `--configuration`.
