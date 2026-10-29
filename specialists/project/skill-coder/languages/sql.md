---
Title: SQL override
Category: reference
Status: current
Authority: local-supplement
Scope: SQL queries, views, migrations and SQL embedded in other languages
Last reviewed: 2026-10-19
Summary: >-
  Bind parameters always; SQLFluff with the project's dialect; uppercase reserved keywords and explicit column lists and
  joins; migrations forward-only with a tested rollback; a header comment on every SQL file.
---

# SQL override

## Authoritative sources

The OWASP SQL Injection Prevention Cheat Sheet, the SQLFluff documentation (getting started, rules), the Mozilla Data Documentation SQL style guide. Copies: `../documents/research-sources-20261019/`.

## Tools

| Job             | Tool                                                                     | Note                                 |
| --------------- | ------------------------------------------------------------------------ | ------------------------------------ |
| Lint and format | SQLFluff, run with the project's dialect (`sqlfluff lint --dialect <d>`) | VERIFIED_PRIMARY                     |
| Migrations      | The project's migration tool                                             | Never hand-edit an applied migration |
| Tests           | Queries tested against a disposable database seeded from fixtures        | UNVERIFIED stub                      |

## Core rule mapping

| Core reference             | In SQL                                                                                                                                                                  |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| security                   | Prepared statements with bound parameters are the first defence (OWASP, VERIFIED_PRIMARY); never concatenate input into SQL; allowlist identifiers (table or column     |
|                            |   names) that cannot be bound                                                                                                                                           |
| documentation-and-headers  | A leading `--` block: purpose, inputs (parameters), output columns, and who runs it                                                                                     |
| design-principles          | One home per query: a named query file or a repository module, not the same SQL copied into callers                                                                     |
| safety-and-writes          | A data change script selects and counts the rows it will touch first; wraps the change in a transaction; is idempotent where possible                                   |
| refactoring-and-promotion  | Compare the result set before and after a rewrite on the same data                                                                                                      |
| efficiency-and-measurement | Read the plan (`EXPLAIN`) for queries that run often or over many rows; batch writes                                                                                    |
| configuration-and-literals | Connection details from settings; no credentials in SQL files                                                                                                           |

## Size and limit tweaks

| Item         | Value                                                                             | Reason                                                                                            |
| ------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Keyword case | Uppercase reserved keywords                                                       | Mozilla: "Always use uppercase for reserved keywords" (VERIFIED_PRIMARY); a project's SQLFluff    |
|              |                                                                                   |   config wins                                                                                     |
| Explicitness | Explicit column lists (no `SELECT *` in saved queries), explicit join types,      | Mozilla "Be Explicit" (VERIFIED_PRIMARY)                                                          |
|              |   explicit aliases                                                                |                                                                                                   |
| Query length | A query over about 60 lines is split into named CTEs or views                     | Maps the core function budget (UNVERIFIED judgement)                                              |

## Ingestion typing

> **Learned 2026-10-29** · SQL over imported CSV (DuckDB, SQLite, PostgreSQL) · VERIFIED_SECONDARY (harvest 2026-10-29 of voip-analysis) · Source: voip-analysis `.archcore/rules/rule-001-price-filter.md` · Falsifier: a text money column compared with a number that keeps
> every row it should
> Money that arrives as text (`$20`, `1,250.00`) breaks filters silently: a bare `price > 0` on the text column dropped every row. Cast
> money to a numeric type at ingestion (strip the currency sign and thousands separator first), and assert the row count after every
> filter, so a filter that removes everything or nothing fails loudly.
>
> ```sql
> CAST(REPLACE(REPLACE(price, '$', ''), ',', '') AS DECIMAL(12, 2)) AS price
> ```

## Open items

- Dialect-specific notes (PostgreSQL, SQLite, MySQL): UNVERIFIED stubs.
