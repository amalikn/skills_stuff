---
Title: JavaScript and TypeScript override
Category: reference
Status: current
Authority: local-supplement
Scope: JavaScript and TypeScript code for Node and the browser
Last reviewed: 2026-10-19
Summary: >-
  TypeScript with strict on, typescript-eslint, the project's formatter, TSDoc or JSDoc comments with param and returns,
  strict equality, no any at seams, the Node version pinned by engines, and argument-array child processes.
---

# JavaScript and TypeScript override

## Authoritative sources

The Google TypeScript Style Guide, the TypeScript `tsconfig` reference (`strict`), typescript-eslint Getting Started, TSDoc. Copies: `../documents/research-sources-20261019/`.

## Tools

| Job          | Tool                                                                                           | Note                                                                                 |
| ------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Runtime      | Node at the project's pin (`.nvmrc`, `.mise.toml`, `package.json` `engines`)                   | Run with `mise exec -- node` or the pinned path                                      |
| Types        | `tsc` with `strict: true`                                                                      | `strict` turns on the strict family of checks (VERIFIED_PRIMARY, tsconfig reference) |
| Lint         | ESLint with typescript-eslint; its `recommended` config, `strict` where the project accepts it | VERIFIED_PRIMARY (typescript-eslint docs)                                            |
| Format       | The project's formatter (often Prettier)                                                       | UNVERIFIED: no source fetched                                                        |
| Tests        | The project's runner (Vitest, Jest or `node:test`)                                             | UNVERIFIED stub                                                                      |
| Dependencies | The project's package manager with its lock file committed                                     | Change the lock only with the manager's own command                                  |

## Core rule mapping

| Core reference              | In JavaScript and TypeScript                                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| documentation-and-headers   | A file comment; `/** ... */` on exported functions and classes with `@param` and `@returns` (TSDoc/JSDoc); `@throws` for thrown errors (UNVERIFIED in the fetched      |
|                             |   TSDoc page; JSDoc defines it)                                                                                                                                        |
| design-principles           | Interfaces at seams; types, not `any`, across module boundaries (Google: `any` is a super and subtype of all types and disables checking, VERIFIED_PRIMARY); prefer    |
|                             |   `unknown` and narrow                                                                                                                                                 |
| errors-and-timeouts         | Throw `Error` subclasses with a `cause`; never an empty `catch`; every `fetch` has an `AbortSignal` timeout; await or return every promise                             |
| security                    | `execFile`/`spawn` with an argument array; parameterised DB calls; no evaluating strings as code; set `textContent`, not raw HTML                                      |
| configuration-and-literals  | Read `process.env` in one settings module and validate at start-up                                                                                                     |
| runtime-boundaries          | A JS engine a project imports declares `engines` in `package.json`; a project's tools run with the project's pinned Node                                               |
| documentation-and-headers   | No `// eslint-disable-line` or `// @ts-ignore` to pass a check; fix it, or configure the rule in the ESLint config with a comment                                      |
|   (suppression)             |                                                                                                                                                                        |

## Size and limit tweaks

| Item                | Value                   | Reason                                                           |
| ------------------- | ----------------------- | ---------------------------------------------------------------- |
| Equality            | `===` and `!==` only    | Loose equality coerces types (Google TS guide, VERIFIED_PRIMARY) |
| Module and function | Core defaults           | No change                                                        |
| Line length         | The formatter's setting | Do not hand-format                                               |

## Open items

- Formatter, test runner and module-format (ESM versus CommonJS) guidance: UNVERIFIED stubs.
