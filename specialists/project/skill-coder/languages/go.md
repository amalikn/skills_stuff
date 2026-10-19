---
Title: Go override
Category: reference
Status: current
Authority: local-supplement
Scope: Go modules, libraries and commands
Last reviewed: 2026-10-19
Summary: >-
  Effective Go and Go Code Review Comments; gofmt, go vet and golangci-lint; doc comments on every exported name; errors as
  values wrapped with %w and tested with errors.Is or errors.As; a Context first with timeouts; table-driven tests.
---

# Go override

## Authoritative sources

Effective Go, Go Code Review Comments, the Google Go Style Guide (Decisions), the `context` package docs, the Go blog posts on error handling and on Go 1.13 errors, the Go wiki on table-driven tests,
`gofmt` docs, golangci-lint docs. Copies: `../documents/research-sources-20261019/`.

## Tools

| Job          | Tool                                                                                      | Note                                               |
| ------------ | ----------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Toolchain    | The `go` and `toolchain` lines in `go.mod`                                                | The project's pin                                  |
| Format       | `gofmt` (or `goimports`)                                                                  | gofmt is the standard formatter (VERIFIED_PRIMARY) |
| Vet and lint | `go vet`; golangci-lint where configured (its `govet`, `errcheck`, `staticcheck` linters) | VERIFIED_PRIMARY (golangci-lint linters page)      |
| Tests        | `go test ./...`, table-driven                                                             | VERIFIED_PRIMARY (Go wiki)                         |

## Core rule mapping

| Core reference                 | In Go                                                                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| documentation-and-headers      | A package comment; a doc comment on every exported name, starting with the name (Code Review Comments, VERIFIED_PRIMARY); parameters, return values and error cases |
|                                |   in sentences, since Go has no `Args:` syntax                                                                                                                      |
| errors-and-timeouts            | Errors are values returned last; handle every one; wrap with `fmt.Errorf("...: %w", err)` and test with `errors.Is` / `errors.As` (Go 1.13, VERIFIED_PRIMARY);      |
|                                |   error strings are not capitalised and do not end with punctuation (VERIFIED_PRIMARY); do not panic for normal errors (VERIFIED_PRIMARY)                           |
| errors-and-timeouts (timeouts) | `context.Context` is the first parameter (context docs, VERIFIED_PRIMARY); `context.WithTimeout` around every network call; `exec.CommandContext` for subprocesses  |
| design-principles              | Small interfaces defined by the consumer; the `internal/` directory keeps packages private to the module                                                            |
| security                       | `database/sql` placeholders; `exec.Command(name, args...)`, never `sh -c` with input                                                                                |
| testing                        | Table-driven tests with named cases; fakes satisfy the consumer's interface                                                                                         |
| documentation-and-headers      | No `//nolint` to pass a check without a reason; golangci-lint can require an explanation (UNVERIFIED setting name)                                                  |
|   (suppression)                |                                                                                                                                                                     |

## Size and limit tweaks

| Item        | Value                                                                           | Reason                                                                                               |
| ----------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Function    | Core 60 lines, loosened to about 80 where explicit `if err != nil`              | Error handling adds lines without adding ideas (UNVERIFIED judgement; tighten if the                 |
|             |   handling dominates                                                            |   project prefers)                                                                                   |
| Line length | No fixed limit; gofmt decides layout                                            | Go style has no line-length rule (UNVERIFIED for the Google guide's exact wording)                   |

## Open items

- Module layout guidance (`cmd/`, `internal/`) beyond the note above: UNVERIFIED stub.
