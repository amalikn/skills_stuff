---
Title: Naming conventions by language and element
Category: reference
Status: current
Authority: local-supplement
Scope: skill-coder — which case convention each language and each kind of name uses, with its primary source
Last reviewed: 2026-10-19
Summary: >-
  The mapping of language and element to naming convention, verified against primary sources on 2026-10-19. One rule underneath: code files and
  identifiers follow their language; names people type at a command line follow the CLI convention (kebab-case); a tool's own schema wins for its names.
---

# Naming conventions by language and element

## Contents

- [The rule](#the-rule)
- [Mapping](#mapping)
- [Where the rule bends](#where-the-rule-bends)
- [Applying it](#applying-it)

## The rule

Operator, 2026-10-19 (after asking what is universally used, and for every row to be checked against its source): **code files and identifiers follow their language; names people type at a command
line follow the command-line convention, which is kebab-case; a name a tool parses follows that tool's own rule.** Why: an identifier must be valid where the language reads it (a hyphen is the minus
sign to Python's `import`), while a typed command is read only by a person and a shell, where GNU long options and multi-word commands already use hyphens. A project's own rule outranks this mapping.

## Mapping

The table is generated from the pack's `naming.toml` (`just naming-table`), which `scripts/naming_check.py` also enforces, so what is shown and what is checked
cannot differ. Every row is VERIFIED_PRIMARY unless its source says otherwise; the captures are in `documents/research-sources-20261019/`.

<!-- BEGIN GENERATED: naming table (scripts/naming_table.py from naming.toml; do not edit) -->

| Language              | Element                                | Convention                                                        | Checked by                                                | Source (capture)                                                                                                   |
| --------------------- | -------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| python                | module and file                        | snake_case_identifier                                             | `naming_check.py` (file names)                            | PEP 8 (`pep-0008.txt`)                                                                                             |
| python                | function, method, variable             | snake_case                                                        | ruff (pep8-naming, N8xx)                                  | PEP 8 (`pep-0008.txt`)                                                                                             |
| python                | class                                  | CapWords                                                          | ruff (pep8-naming, N801)                                  | PEP 8 (`pep-0008.txt`)                                                                                             |
| python                | constant                               | UPPER_CASE                                                        | review                                                    | PEP 8 (`pep-0008.txt`)                                                                                             |
| shell                 | script source file                     | snake_case                                                        | `naming_check.py` (file names)                            | Google Shell Style Guide (`google-shell-style.txt`)                                                                |
| shell                 | function and variable                  | snake_case                                                        | review (ShellCheck does not check case)                   | Google Shell Style Guide (`google-shell-style.txt`)                                                                |
| shell                 | constant and exported environment name | UPPER_CASE                                                        | review                                                    | Google Shell Style Guide (`google-shell-style.txt`)                                                                |
| go                    | package                                | lowercase                                                         | golangci-lint (revive var-naming)                         | Effective Go (`effective-go.txt`)                                                                                  |
| go                    | identifier                             | MixedCaps (exported) or mixedCaps                                 | golangci-lint (revive)                                    | Effective Go (`effective-go.txt`)                                                                                  |
| go                    | file                                   | lowercase; `_test.go` marks tests                                 | review (no primary separator rule; not enforced)          | go command (only `_test.go` is defined; the separator is UNVERIFIED as a rule) (`go-cmd-go.txt`)                   |
| rust                  | module, function, variable, crate      | snake_case_identifier                                             | `naming_check.py` (file names)                            | Rust API Guidelines; RFC 430 for crates (`rust-api-guidelines-naming.txt`)                                         |
| rust                  | type and trait                         | CapWords                                                          | rustc (non_camel_case_types)                              | Rust API Guidelines (`rust-api-guidelines-naming.txt`)                                                             |
| rust                  | constant and static                    | UPPER_CASE                                                        | rustc (non_upper_case_globals)                            | Rust API Guidelines (`rust-api-guidelines-naming.txt`)                                                             |
| javascript            | file                                   | project's choice of snake_case or kebab-case                      | review: follow the project                                | Google JS Style Guide (`google-jsguide.txt`)                                                                       |
| typescript            | file                                   | snake_case                                                        | `naming_check.py` (file names)                            | Google TS Style Guide (`google-tsguide.txt`)                                                                       |
| javascript-typescript | variable and function                  | lowerCamelCase                                                    | eslint (camelcase / @typescript-eslint/naming-convention) | Google JS and TS style guides (`google-jsguide.txt`)                                                               |
| javascript-typescript | class and type                         | CapWords                                                          | @typescript-eslint/naming-convention                      | Google JS and TS style guides (`google-tsguide.txt`)                                                               |
| npm                   | package name                           | lowercase, URL-safe (hyphens in practice)                         | npm                                                       | npm package.json docs (`npm-package-json.txt`)                                                                     |
| ansible               | variable                               | snake_case                                                        | ansible-lint (var-naming)                                 | Ansible docs; ansible-lint var-naming (`ansible-lint-rules-var-naming.txt`)                                        |
| ansible               | role                                   | snake_case                                                        | ansible-lint (role-name)                                  | ansible-lint role-name (`ansible-lint-rules-role-name.txt`)                                                        |
| ansible               | collection namespace and name          | snake_case (no hyphen)                                            | ansible-galaxy                                            | Galaxy collection metadata (`ansible-collections-galaxy-meta.txt`)                                                 |
| kubernetes            | API JSON field                         | lowerCamelCase                                                    | the API schema                                            | Kubernetes API conventions (`kubernetes-api-conventions.txt`)                                                      |
| kubernetes            | object name                            | kebab-case (DNS label; `.` allowed in subdomains)                 | the API server                                            | Kubernetes object names (`kubernetes-object-names.txt`)                                                            |
| oci                   | image repository name                  | lowercase with `-`, `_`, `__` or `.` separators                   | the registry                                              | OCI distribution spec (`oci-distribution-spec.txt`)                                                                |
| css                   | class and ID name                      | kebab-case                                                        | stylelint (selector-class-pattern)                        | Google HTML/CSS Style Guide (`google-htmlcss-style.txt`)                                                           |
| web                   | URL path                               | kebab-case                                                        | review                                                    | Google Search Central URL structure (`google-search-url-structure.txt`)                                            |
| command line          | long option                            | kebab-case                                                        | review (argparse, getopt_long)                            | GNU Coding Standards option table (`gnu-standards-option-table.txt`)                                               |
| command line          | multi-word command and subcommand      | kebab-case                                                        | review                                                    | Git (cherry-pick); GNU practice (`git-cherry-pick.txt`)                                                            |
| just                  | recipe                                 | kebab-case                                                        | `naming_check.py` (recipes)                               | just grammar and manual (both separators allowed; the manual uses `-`); GNU standard targets (`just-grammar.txt`)  |
| yaml-json-toml        | key                                    | the consuming tool's schema                                       | the tool's schema                                         | Kubernetes (camelCase) and Ansible (snake_case) show there is no universal rule (`kubernetes-api-conventions.txt`) |
| git                   | branch name                            | no primary convention (character rules only); kebab-case by habit | git check-ref-format                                      | git-check-ref-format (`git-check-ref-format.txt`)                                                                  |
| documents             | time-bound markdown file               | `<slug>-YYYYMMDD_hhmm.md`                                         | governance markdown hooks                                 | Governance naming guide (USER_STATED)                                                                              |
| skills                | skill name                             | kebab-case                                                        | the skill spec                                            | Governance coding guide (USER_STATED)                                                                              |

<!-- END GENERATED: naming table -->

## Where the rule bends

- **POSIX** names utilities with lowercase letters and digits only and has single-character options and no long options; hyphenated commands and `--long-options` rest on GNU and Git practice. Follow
  POSIX only where a project targets strict POSIX portability.
- **Cargo** keeps both conventions at once: a hyphenated package becomes an underscored library name, while the binary keeps the hyphen. This is the rule itself in one tool: the identifier is
  snake_case, the typed command is kebab-case.
- **A script installed as a command** keeps a snake_case file in the repository and gets its kebab-case command name when it is installed (a symlink,
  an install path, a console-script entry point), the same split Cargo makes. Why: the file is code the language reads; the command is what a person types.
- **A tool's parser wins.** An Ansible collection name cannot hold a hyphen; an OCI image name may hold `_` and `.`; Kubernetes object names are DNS names. A name one of these tools reads follows that
  tool, even when a person also types it.
- **JavaScript file names** have no single standard: follow the project, and the framework's guide where it has one.

## Applying it

- New names follow the mapping. An existing name that breaks it is renamed when next touched, with every reference updated in the same change ([safety-and-writes.md](safety-and-writes.md), "Changing
  an identifier"); a typed command's old name stays working through a transition when callers outside the repository may use it.
- skill-ai-it's `check_file_naming` enforces snake_case for code files under `scripts/`; task-runner recipe names are not yet checked.
