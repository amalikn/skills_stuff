---
Title: Security
Category: reference
Status: current
Authority: local-supplement
Scope: Secure coding for any language - input, injection, secrets, access, cryptography, supply chain
Last reviewed: 2026-10-19
Summary: >-
  OWASP-informed secure coding: validate input by allowlist at trust boundaries, parameterise every query and command,
  keep secrets out of code and logs, least privilege, safe defaults, and supply-chain hygiene (pins, hashes, provenance).
---

# Security

Informed by the OWASP Top 10:2025, the OWASP Cheat Sheet Series and ASVS 5.0 (retrieved 2026-10-19). The Top 10 is an awareness list, not a standard; use ASVS when a project needs verifiable
requirements.

## Contents

- [Rules](#rules)
- [Injection by language](#injection-by-language)
- [Supply chain](#supply-chain)
- [The OWASP Top 10:2025 for reference](#the-owasp-top-102025-for-reference)

## Rules

| Area            | Rule                                                                                                            | Why                                                              |
| --------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Input           | Validate at every trust boundary by allowlist (type, length, range, format), on the server side                 | OWASP: define what is accepted rather than trying to recognise   |
|                 |                                                                                                                 |   every bad string                                               |
| Injection       | Pass data as parameters, never by building a query, command or template string from input                       | Parameterised queries are OWASP's first defence against          |
|                 |                                                                                                                 |   SQL injection                                                  |
| Commands        | Run programs with an argument list, not a shell string; when a shell is unavoidable, quote every expansion      | A shell string lets input become code                            |
| Paths           | Resolve user-supplied paths and refuse those that escape the intended root; refuse symlink escapes              | Path traversal reads or writes anything                          |
| Secrets         | Never in code, tests, logs, error messages, command-line arguments or committed config; read from the secret    | OWASP: secrets should never be hardcoded                         |
|                 |   store at run time                                                                                             |                                                                  |
| Secrets         | Show only a non-secret field (entry name, user); deliver a secret by piping it to the consumer                  | Chat and logs are copied (governance security guide)             |
|   in output     |                                                                                                                 |                                                                  |
| Least privilege | Each writer identity has only the rights its job needs; routine writes refuse an administrator credential       | A leaked or buggy writer does limited damage                     |
| Defaults        | Safe by default: deny, read-only, TLS verification on, debug off                                                | A missed setting fails closed                                    |
| Errors          | Do not leak stack traces, secrets or internal paths to an untrusted caller; log them internally                 | Errors are a reconnaissance tool (A10:2025 is Mishandling of     |
|                 |                                                                                                                 |   Exceptional Conditions)                                        |
| Cryptography    | Use the platform's vetted libraries; never write your own primitives; never disable certificate checks to make  | Home-made crypto is broken crypto                                |
|                 |   a call work                                                                                                   |                                                                  |
| Deserialisation | Never load untrusted data with a format that can construct arbitrary objects (a language's native object        | It is remote code execution                                      |
|                 |   serialiser, YAML full loaders)                                                                                |                                                                  |

## Injection by language

| Language                  | Do                                                                                       | Do not                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Python                    | `subprocess.run([...], timeout=...)`; DB-API placeholders; `yaml.safe_load`              | `shell=True` with input; f-string SQL; a YAML loader that is not the safe one |
| Shell                     | Quote every expansion (`"$var"`); `--` before arguments that may start with `-`          | Unquoted `$var`; evaluating input as code                                     |
| JavaScript and TypeScript | Parameterised driver calls; `execFile` with an argument array; `textContent` over raw    | Template-string SQL; a shell-string child process; evaluating strings as code |
|                           |   HTML insertion                                                                         |                                                                               |
| Go                        | `database/sql` placeholders; `exec.CommandContext(ctx, name, args...)`                   | `fmt.Sprintf` into SQL; `sh -c` with input                                    |
| Rust                      | Bound parameters in the driver; `std::process::Command` with `.arg()`                    | `format!` into SQL                                                            |
| SQL                       | Bind variables; stored procedures without dynamic SQL                                    | Concatenated dynamic SQL                                                      |

The Python subprocess documentation warns about shell injection when `shell=True` is combined with untrusted input (VERIFIED_PRIMARY).

## Supply chain

- Pin dependencies and actions (by version and, for build tooling, by digest or hash). OpenSSF Scorecard's Pinned-Dependencies check scores this (VERIFIED_PRIMARY).
- Give CI tokens the least permission (Scorecard Token-Permissions) and avoid workflow patterns that run untrusted code with secrets (Dangerous-Workflow).
- Prefer releases with provenance; SLSA build levels describe increasing guarantees against tampering, with Build L3 requiring a hardened build platform (VERIFIED_PRIMARY, SLSA 1.0).
- Review lock-file diffs. Why: Software Supply Chain Failures is A03 in the OWASP Top 10:2025.

## The OWASP Top 10:2025 for reference

A01 Broken Access Control; A02 Security Misconfiguration; A03 Software Supply Chain Failures; A04 Cryptographic Failures; A05 Injection; A06 Insecure Design; A07 Authentication Failures; A08 Software
or Data Integrity Failures; A09 Security Logging and Alerting Failures; A10 Mishandling of Exceptional Conditions.

> **Learned 2026-10-20** · gpg 2.5 in a script · VERIFIED_PRIMARY · Source: smc-resiliency scripts/make_release_key.sh (commit 4d6e1b0); gpg exit 2 with a deep GNUPGHOME, success under `$HOME/.k.XXXX` · Falsifier: gpg-agent starting with a GNUPGHOME path over about 100 characters on macOS
> A throwaway keyring for making a key keeps the private key out of `~/.gnupg`, but gpg-agent's socket lives in GNUPGHOME and a Unix socket path
> has a hard limit (about 104 bytes on macOS), so a GNUPGHOME under a deep session scratchpad fails with exit 2 and nothing useful on stderr. Use a
> short `mktemp -d "$HOME/.k.XXXX"`, pass the passphrase with `--passphrase-file` (mode 600 in the work folder) rather than on the command line,
> keep the revocation certificate gpg writes at key creation before removing the folder, and `gpgconf --kill all` for each throwaway keyring.
> `--gen-revoke` refuses `--batch`; answer it through `--command-fd 0` without `--batch` if a certificate must be made later.
>
> ```bash
> # smc-resiliency scripts/make_release_key.sh (excerpt)
> WORK=$(mktemp -d "$HOME/.k.XXXX"); trap cleanup EXIT
> ( umask 077; printf '%s' "$PASS" > "$WORK/pp" )
> export GNUPGHOME="$WORK/g1"; mkdir -m 700 "$GNUPGHOME"
> gpg -q --batch --pinentry-mode loopback --passphrase-file "$WORK/pp" --quick-gen-key "$KEY_UID" ed25519 sign "$EXPIRY"
> cp "$GNUPGHOME/openpgp-revocs.d/$FPR.rev" "$WORK/rev.asc"
> ```
