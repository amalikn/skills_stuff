---
Title: Research sources 2026-10-19
Category: reference
Status: current
Authority: local-supplement
Scope: Verbatim copies of the external pages skill-coder relies on
Last reviewed: 2026-10-19
Summary: Index of the pages fetched on 2026-10-19 as Markdown text, with the URL and what each supports.
---

# Research sources 2026-10-19

Each file is the page as fetched on 2026-10-19, converted to Markdown text and kept verbatim. Pages over about 100 KB were cut by the fetcher; the note says so.
The ShellCheck wiki home page was behind a bot challenge; its README on GitHub is used instead.

| File | URL | Supports |
| --- | --- | --- |
| [ansible-become.txt](ansible-become.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_privilege_escalation.html> | Ansible `become` privilege escalation |
| [ansible-check-mode.txt](ansible-check-mode.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html> | Check and diff mode; modules without check-mode support do nothing |
| [ansible-error-handling.txt](ansible-error-handling.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html> | `max_fail_percentage`, `any_errors_fatal`, blocks |
| [ansible-handlers.txt](ansible-handlers.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html> | A handler runs once however many tasks notify it |
| [ansible-lint-profiles.txt](ansible-lint-profiles.txt) | <https://ansible.readthedocs.io/projects/lint/profiles/> | ansible-lint profiles from `min` to `production` |
| [ansible-lint-rules-fqcn.txt](ansible-lint-rules-fqcn.txt) | <https://ansible.readthedocs.io/projects/lint/rules/fqcn/> | Fully qualified collection names |
| [ansible-lint-rules-no-changed-when.txt](ansible-lint-rules-no-changed-when.txt) | <https://ansible.readthedocs.io/projects/lint/rules/no-changed-when/> | `changed_when`, `creates`, `removes` |
| [ansible-logging-no-log.txt](ansible-logging-no-log.txt) | <https://docs.ansible.com/ansible/latest/reference_appendices/logging.html> | `no_log: true` keeps secrets out of logs |
| [ansible-strategies-serial.txt](ansible-strategies-serial.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_strategies.html> | `serial` batches |
| [ansible-tags.txt](ansible-tags.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html> | Tags, `always` and `never`; tags supersede block error handling |
| [ansible-tips-tricks.txt](ansible-tips-tricks.txt) | <https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html> | General Ansible practice |
| [ansible-vault.txt](ansible-vault.txt) | <https://docs.ansible.com/ansible/latest/vault_guide/vault.html> | Vault protects data at rest only |
| [molecule-docs.txt](molecule-docs.txt) | <https://ansible.readthedocs.io/projects/molecule/> | Molecule role and playbook tests |
| [bash-set-builtin.txt](bash-set-builtin.txt) | <https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html> | Shell: `set -e`, `-u`, `-o pipefail` semantics |
| [cargo-test.txt](cargo-test.txt) | <https://doc.rust-lang.org/cargo/commands/cargo-test.html> | Rust: `cargo test` runs unit, integration and doc tests |
| [conventional-commits.txt](conventional-commits.txt) | <https://www.conventionalcommits.org/en/v1.0.0/> | Commit message types, `BREAKING CHANGE` |
| [effective-go.txt](effective-go.txt) | <https://go.dev/doc/effective_go> | Go: gofmt, multiple return values, errors, panic (truncated at 100 KB by the fetcher) |
| [fowler-refactoring-definition.txt](fowler-refactoring-definition.txt) | <https://martinfowler.com/bliki/DefinitionOfRefactoring.html> | Refactoring changes structure without changing observable behaviour |
| [fowler-test-pyramid.txt](fowler-test-pyramid.txt) | <https://martinfowler.com/bliki/TestPyramid.html> | Many fast low-level tests, few broad ones |
| [go-blog-error-handling.txt](go-blog-error-handling.txt) | <https://go.dev/blog/error-handling-and-go> | Go: errors are values |
| [go-blog-go113-errors.txt](go-blog-go113-errors.txt) | <https://go.dev/blog/go1.13-errors> | Go: wrapping with `%w`, `errors.Is`, `errors.As` |
| [go-code-review-comments.txt](go-code-review-comments.txt) | <https://go.dev/wiki/CodeReviewComments> | Go: error strings, do not panic, contexts, handle errors |
| [go-context-pkg.txt](go-context-pkg.txt) | <https://pkg.go.dev/context> | Go: `WithTimeout`, Context as first parameter |
| [go-table-driven-tests.txt](go-table-driven-tests.txt) | <https://go.dev/wiki/TableDrivenTests> | Go: table-driven tests |
| [gofmt.txt](gofmt.txt) | <https://pkg.go.dev/cmd/gofmt> | Go: gofmt is the formatter |
| [golangci-lint-docs.txt](golangci-lint-docs.txt) | <https://golangci-lint.run/docs/linters/> | Go: linter aggregator (govet, errcheck, staticcheck) |
| [google-go-style-decisions.txt](google-go-style-decisions.txt) | <https://google.github.io/styleguide/go/decisions> | Go: naming, errors, doc comments (truncated at 100 KB) |
| [google-python-style.txt](google-python-style.txt) | <https://google.github.io/styleguide/pyguide.html> | Python: Args/Returns/Raises docstrings, 80 columns (truncated at 100 KB) |
| [google-shell-style.txt](google-shell-style.txt) | <https://google.github.io/styleguide/shellguide.html> | Shell: Bash only, 100-line limit, function comments, ShellCheck |
| [google-tsguide.txt](google-tsguide.txt) | <https://google.github.io/styleguide/tsguide.html> | TypeScript: JSDoc, equality, `any` (truncated at 100 KB) |
| [json-rfc8259.txt](json-rfc8259.txt) | <https://www.rfc-editor.org/rfc/rfc8259.txt> | JSON: names SHOULD be unique; no comments in the grammar |
| [keep-a-changelog.txt](keep-a-changelog.txt) | <https://keepachangelog.com/en/1.1.0/> | `Unreleased` section; Added, Changed, Deprecated, Removed, Fixed, Security |
| [mise-python.txt](mise-python.txt) | <https://mise.jdx.dev/lang/python.html> | mise: `.python-version`, `_.python.venv` |
| [mozilla-sql-style.txt](mozilla-sql-style.txt) | <https://docs.telemetry.mozilla.org/concepts/sql_style.html> | SQL: uppercase reserved keywords, be explicit |
| [openssf-scorecard-checks.txt](openssf-scorecard-checks.txt) | <https://github.com/ossf/scorecard/blob/main/docs/checks.md> | Supply chain: Pinned-Dependencies, Token-Permissions, Dangerous-Workflow |
| [owasp-asvs.txt](owasp-asvs.txt) | <https://owasp.org/www-project-application-security-verification-standard/> | ASVS 5.0 requirement identifiers |
| [owasp-cheatsheet-injection-prevention.txt](owasp-cheatsheet-injection-prevention.txt) | <https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html> | Injection: parameterisation, OS command injection |
| [owasp-cheatsheet-input-validation.txt](owasp-cheatsheet-input-validation.txt) | <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html> | Allowlist over denylist |
| [owasp-cheatsheet-secrets.txt](owasp-cheatsheet-secrets.txt) | <https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html> | Secrets never hardcoded; rotation; least privilege |
| [owasp-cheatsheet-sql-injection.txt](owasp-cheatsheet-sql-injection.txt) | <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html> | SQL: prepared statements with parameterised queries |
| [owasp-scp-quick-reference-github.txt](owasp-scp-quick-reference-github.txt) | <https://github.com/OWASP/secure-coding-practices-quick-reference-guide> | Secure Coding Practices checklist (project landing page) |
| [owasp-top10-2025.txt](owasp-top10-2025.txt) | <https://owasp.org/Top10/2025/> | OWASP Top 10:2025 list (A03 supply chain, A05 injection) |
| [pep-0008.txt](pep-0008.txt) | <https://peps.python.org/pep-0008/> | Python style: 79 columns, bare except, consistency |
| [pep-0020.txt](pep-0020.txt) | <https://peps.python.org/pep-0020/> | The Zen of Python |
| [pep-0257.txt](pep-0257.txt) | <https://peps.python.org/pep-0257/> | Docstring conventions: triple double quotes, summary line |
| [pip-hash-checking.txt](pip-hash-checking.txt) | <https://pip.pypa.io/en/stable/topics/secure-installs/> | pip `--require-hashes` |
| [pytest-fixtures.txt](pytest-fixtures.txt) | <https://docs.pytest.org/en/stable/how-to/fixtures.html> | pytest fixtures and `yield` teardown |
| [python-packaging-src-layout.txt](python-packaging-src-layout.txt) | <https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/> | src layout prevents accidental import of the working copy |
| [python-subprocess.txt](python-subprocess.txt) | <https://docs.python.org/3/library/subprocess.html> | `subprocess.run(timeout=...)`, `TimeoutExpired`, shell injection |
| [python-typing-protocol.txt](python-typing-protocol.txt) | <https://typing.python.org/en/latest/spec/protocol.html> | Protocols: structural subtyping for seams and fakes |
| [python-venv.txt](python-venv.txt) | <https://docs.python.org/3/library/venv.html> | A venv is not checked into source control and is not movable |
| [ruff-faq.txt](ruff-faq.txt) | <https://docs.astral.sh/ruff/faq/> | ruff pydocstyle `convention = "google"` |
| [ruff-linter.txt](ruff-linter.txt) | <https://docs.astral.sh/ruff/linter/> | ruff rule selection and suppression |
| [rust-api-guidelines-checklist.txt](rust-api-guidelines-checklist.txt) | <https://rust-lang.github.io/api-guidelines/checklist.html> | Rust: C-FAILURE, C-GOOD-ERR, C-EXAMPLE, C-QUESTION-MARK |
| [rust-api-guidelines-documentation.txt](rust-api-guidelines-documentation.txt) | <https://rust-lang.github.io/api-guidelines/documentation.html> | Rust: doc sections Errors, Panics, Safety |
| [rust-book-error-handling.txt](rust-book-error-handling.txt) | <https://doc.rust-lang.org/book/ch09-00-error-handling.html> | Rust: `Result<T, E>` for recoverable, `panic!` for unrecoverable |
| [rust-clippy-readme.txt](rust-clippy-readme.txt) | <https://doc.rust-lang.org/clippy/> | Rust: Clippy lint groups |
| [rustfmt-readme.txt](rustfmt-readme.txt) | <https://github.com/rust-lang/rustfmt> | Rust: `cargo fmt` |
| [semver-2.txt](semver-2.txt) | <https://semver.org/> | SemVer 2.0.0: MAJOR.MINOR.PATCH; released versions never modified |
| [shellcheck-readme.txt](shellcheck-readme.txt) | <https://github.com/koalaman/shellcheck> | ShellCheck static analysis (the wiki home page was bot-walled) |
| [shellcheck-sc2086.txt](shellcheck-sc2086.txt) | <https://www.shellcheck.net/wiki/SC2086> | Shell: double quote to prevent globbing and word splitting |
| [slsa-levels.txt](slsa-levels.txt) | <https://slsa.dev/spec/v1.0/levels> | SLSA build levels and provenance |
| [sqlfluff-getting-started.txt](sqlfluff-getting-started.txt) | <https://docs.sqlfluff.com/en/stable/gettingstarted.html> | SQL: `sqlfluff lint --dialect` |
| [sqlfluff-rules.txt](sqlfluff-rules.txt) | <https://docs.sqlfluff.com/en/stable/reference/rules.html> | SQL: rule categories |
| [toml-1-0.txt](toml-1-0.txt) | <https://toml.io/en/v1.0.0> | TOML: case-sensitive keys; defining a key twice is invalid |
| [tsdoc.txt](tsdoc.txt) | <https://tsdoc.org/> | TypeScript doc comments (`@param`, `@returns`) |
| [twelve-factor-config.txt](twelve-factor-config.txt) | <https://12factor.net/config> | Strict separation of config from code |
| [twelve-factor-dependencies.txt](twelve-factor-dependencies.txt) | <https://12factor.net/dependencies> | Declare and isolate dependencies |
| [typescript-eslint-getting-started.txt](typescript-eslint-getting-started.txt) | <https://typescript-eslint.io/getting-started/> | typescript-eslint recommended and strict configs |
| [typescript-tsconfig-strict.txt](typescript-tsconfig-strict.txt) | <https://www.typescriptlang.org/tsconfig/#strict> | TypeScript `strict` (truncated at 100 KB) |
| [wikipedia-characterization-test.txt](wikipedia-characterization-test.txt) | <https://en.wikipedia.org/wiki/Characterization_test> | Characterisation tests (Feathers) pin existing behaviour (secondary source) |
| [yaml-1-2-2-spec.txt](yaml-1-2-2-spec.txt) | <https://yaml.org/spec/1.2.2/> | YAML 1.2.2 core schema (truncated at 100 KB) |
| [yamllint-docs.txt](yamllint-docs.txt) | <https://yamllint.readthedocs.io/en/stable/rules.html> | yamllint `truthy` and `key-duplicates` rules |
| [ansible-collections-galaxy-meta.txt](ansible-collections-galaxy-meta.txt) | <https://docs.ansible.com/ansible/latest/dev_guide/collections_galaxy_meta.html> | Naming: collection namespace and name only lowercase alphanumerics and underscores |
| [ansible-lint-rules-role-name.txt](ansible-lint-rules-role-name.txt) | <https://ansible.readthedocs.io/projects/lint/rules/role-name/> | Naming: role names lowercase alphanumerics and `_` |
| [ansible-lint-rules-var-naming.txt](ansible-lint-rules-var-naming.txt) | <https://ansible.readthedocs.io/projects/lint/rules/var-naming/> | Naming: `var-naming`, default pattern `^[a-z_][a-z0-9_]*$` |
| [ansible-variables.txt](ansible-variables.txt) | <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html> | Naming: valid variable names are letters, numbers and underscores |
| [cargo-manifest.txt](cargo-manifest.txt) | <https://doc.rust-lang.org/cargo/reference/manifest.html> | Naming: package name may use alphanumerics, `-` or `_` |
| [cargo-targets.txt](cargo-targets.txt) | <https://doc.rust-lang.org/cargo/reference/cargo-targets.html> | Naming: library name is the package name with dashes replaced by underscores; binary keeps dashes |
| [docker-image-tag.txt](docker-image-tag.txt) | <https://docs.docker.com/reference/cli/docker/image/tag/> | Naming: image reference parts (HOST, NAMESPACE/REPOSITORY, TAG); the character rule is in the OCI spec |
| [git-check-ref-format.txt](git-check-ref-format.txt) | <https://git-scm.com/docs/git-check-ref-format> | Naming: Git ref (branch, tag) character rules; no word-separator convention |
| [git-cherry-pick.txt](git-cherry-pick.txt) | <https://git-scm.com/docs/git-cherry-pick> | Naming: a hyphenated Git subcommand (`git-cherry-pick`) |
| [glibc-getopt-long-options.txt](glibc-getopt-long-options.txt) | <https://sourceware.org/glibc/manual/latest/html_node/Getopt-Long-Options.html> | Naming: `getopt_long` for GNU-style long options |
| [gnu-standards-command-line-interfaces.txt](gnu-standards-command-line-interfaces.txt) | <https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html> | Naming: define long-named options; consistent names across programs |
| [gnu-standards-option-table.txt](gnu-standards-option-table.txt) | <https://www.gnu.org/prep/standards/html_node/Option-Table.html> | Naming: GNU table of long options (`dry-run`, `after-date`) |
| [gnu-standards-standard-targets.txt](gnu-standards-standard-targets.txt) | <https://www.gnu.org/prep/standards/html_node/Standard-Targets.html> | Naming: GNU standard make targets (`install-strip`, `maintainer-clean`, `distclean`) |
| [go-cmd-go.txt](go-cmd-go.txt) | <https://pkg.go.dev/cmd/go> | Naming: `*_test.go` files; names beginning `_` or `.` are ignored |
| [google-htmlcss-style.txt](google-htmlcss-style.txt) | <https://google.github.io/styleguide/htmlcssguide.html> | Naming: separate words in CSS class names by a hyphen |
| [google-jsguide.txt](google-jsguide.txt) | <https://google.github.io/styleguide/jsguide.html> | Naming: JS file names lowercase with `_` or `-`; lowerCamelCase, UpperCamelCase, CONSTANT_CASE |
| [google-search-url-structure.txt](google-search-url-structure.txt) | <https://developers.google.com/search/docs/crawling-indexing/url-structure> | Naming: hyphens rather than underscores in URLs |
| [just-grammar.txt](just-grammar.txt) | <https://github.com/casey/just/blob/master/GRAMMAR.md> | Naming: just `NAME` token allows letters, digits, `_` and `-` |
| [just-manual-readme.txt](just-manual-readme.txt) | <https://github.com/casey/just/blob/master/README.md> | Naming: the just manual's examples use hyphenated recipe names (`recipe-name`) |
| [kubernetes-api-conventions.txt](kubernetes-api-conventions.txt) | <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md> | Naming: JSON field names camelCase, Go field names PascalCase |
| [kubernetes-object-names.txt](kubernetes-object-names.txt) | <https://kubernetes.io/docs/concepts/overview/working-with-objects/names/> | Naming: DNS subdomain and RFC 1123 label names, lowercase alphanumerics and `-` |
| [npm-package-json.txt](npm-package-json.txt) | <https://docs.npmjs.com/cli/v10/configuring-npm/package-json> | Naming: npm package names have no uppercase and are URL-safe |
| [oci-distribution-spec.txt](oci-distribution-spec.txt) | <https://github.com/opencontainers/distribution-spec/blob/main/spec.md> | Naming: repository `<name>` regular expression, lowercase with `.`, `_`, `__` or `-` separators |
| [posix-utility-conventions.txt](posix-utility-conventions.txt) | <https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html> | Naming: POSIX utility names lowercase letters and digits; single-character options |
| [rust-api-guidelines-naming.txt](rust-api-guidelines-naming.txt) | <https://rust-lang.github.io/api-guidelines/naming.html> | Naming: Rust casing table (C-CASE); crate casing "unclear" |
| [rust-rfc-0430-naming.txt](rust-rfc-0430-naming.txt) | <https://rust-lang.github.io/rfcs/0430-finalizing-naming-conventions.html> | Naming: RFC 430, crates `snake_case` (but prefer single word) |
