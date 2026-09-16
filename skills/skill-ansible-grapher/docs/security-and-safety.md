# Security and safety

## This is a visualization/documentation skill, not an execution skill

- Never runs a playbook against managed hosts.
- Never invokes `ansible-playbook` without `--syntax-check`.
- Never runs ad hoc `ansible` commands.
- Never modifies inventories, playbooks, roles, variables, vaults, or `ansible.cfg`.
- Never decrypts, prints, copies, embeds, or exposes vault secrets.
- A successful graph is evidence of parsed structure, **not** proof of runtime
  correctness, execution order, or successful deployment. Static analysis cannot
  resolve runtime facts, dynamic variables, loop/conditional outcomes, or
  variable-dependent includes.

## Dynamic inventory policy — deny by default

An inventory source that is an executable file without a `.yml`/`.yaml`/`.ini` extension
is treated as dynamic/plugin inventory. Such sources may run arbitrary local code or
contact external systems (AWS, Azure, GCP, VMware, NetBox, etc.). This skill:

- Refuses to invoke it (exit `6`) unless `--allow-dynamic-inventory` /
  `ANSIBLE_GRAPHER_ALLOW_DYNAMIC_INVENTORY=1` is set.
- `discover` may *identify* a dynamic source in its report; it never executes one.
- Enabling the override should only happen after explicit user approval in the current
  conversation — do not set it proactively "to save a step."

## Variable display — off by default

- `--show-variables` is required to render inventory variable values into the graph.
  Off by default because variables frequently contain IP addresses, hostnames,
  usernames, connection parameters, tokens, or other sensitive operational data.
- When enabled, the run prints an explicit warning, and the manifest records
  `"show_variables": true`.
- Never paste graph content into chat output when variables were shown — report only
  the artifact path; the user inspects the file locally.

## Vault and secret policy

- Vault password files/IDs may be passed through to the underlying tools by reference
  only; this skill never reads their contents.
- `--ask-vault-pass` / interactive vault prompts are not used by this skill's own flows
  (unattended/CI-appropriate only).
- `--extra-vars` values, and any flag listed in `config/default.yaml` →
  `redaction.redact_flags` (currently `-e`/`--extra-vars`, `--vault-password-file`,
  `--vault-pass-file`, `--vault-id`, `--ask-vault-pass`/`--ask-vault-password`), are
  replaced with `***REDACTED***` in `logs/commands.log` and never echoed to chat output.

## Custom Jinja templates (`ansible-inventory-grapher -t`)

Custom templates are trusted, code-like inputs (Jinja2 can execute arbitrary logic
against inventory data). This skill:

- Never auto-discovers or auto-executes a template.
- Requires an explicit, local file path if a custom template is ever used (not currently
  exposed as a first-class flag in `scripts/ansible-grapher`; use the underlying
  `ansible-inventory-grapher -t` directly if you need this, with the same caution).
- Rejects remote URLs as template sources.

## Output path safety

- Output roots resolving to `/`, `$HOME`, or a symlink (for `clean`) are refused.
- Writes are atomic (temp file + rename) — no partially-written artifact is ever left at
  the final path.
- `clean` requires a well-formed ownership marker and never follows symlinks while
  walking a tree for deletion.

## Injection and subprocess safety

- All subprocess invocations use `subprocess.run(argv, shell=False, ...)` with argument
  arrays — never shell string concatenation, never `eval`.
- User-supplied paths are resolved to absolute paths before being placed in an argv list;
  no path is ever interpolated into a shell string.

## Runtime provenance and toolchain trust

- Each grapher's actual `ansible-core` version is discovered by introspecting its own
  venv interpreter (not assumed from its name or from the system `ansible` version).
- A version mismatch between the validation `ansible-core` and a grapher's `ansible-core`
  is always reported (never silently ignored) and is a hard failure in
  `--strict-ansible-version-match` mode. See `SKILL.md` §19.
- Development/prerelease tool builds are detected and reported; `ci-light` rejects them
  by default (`allow_development_tool_versions: false`), requiring an explicit override.
- Git provenance (commit SHA, dirty/clean) is read only from a launcher's directly
  associated `*-github` checkout, and only commit/dirty state is reported — no other
  repository content, history, or remote data is read or exposed.

## Managed Python runtime — no silent fallback

- `scripts/*` and the `justfile` use the managed working-cache venv Python by default.
- If that venv is missing, they **fail clearly** (exit `5`, explicit remediation message)
  rather than silently running under system Python — see `scripts/_resolve_python.sh`.
- Falling back to system Python requires explicit opt-in
  (`--allow-system-python-fallback` / `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1`),
  is always logged as a warning, and is recorded as `runtime_isolation: degraded` in the
  manifest/validate output (compatibility status floors at `WARN`, never silently `PASS`).

## Structural artifact validation

- Every generated SVG/JSON/Mermaid/DOT artifact is checked for non-empty, well-formed
  content before being promoted — an upstream grapher exiting `0` is not treated as
  proof it produced valid output. Invalid or empty artifacts are deleted, not left on
  disk, and the run reports failure (exit `7`). See
  `tests/test-partial-generation-failure.sh`.

## Threat model summary

| Risk | Mitigation |
|---|---|
| Playbook execution against real hosts | Never invoked without `--syntax-check`; no execution code path exists |
| Vault secret leakage | Never decrypted/read; redacted in logs/manifests |
| Dynamic inventory / cloud plugin side effects | Deny-by-default, explicit opt-in required |
| Sensitive variable exposure in graphs | Suppressed by default, explicit opt-in required, never echoed to chat |
| Path traversal / unsafe output location | Root/`$HOME`/symlink rejection, path containment checks |
| Unsafe cleanup | Ownership-marker gate, symlink-escape prevention, dry-run without `--force` |
| Shell injection | `shell=False` + argv arrays throughout |
| Arbitrary template execution | Custom templates never auto-discovered/executed |
| Silent Ansible-version mismatch between validation and graphing | Discovered, reported, strict-mode enforceable (§ above) |
| Silent system-Python fallback | Opt-in only, always logged, recorded as degraded (§ above) |
| Upstream tool "succeeding" while producing no/invalid output | Structural artifact validation, exit `7` on failure (§ above) |
| Untrusted development/prerelease tool builds | Detected, reported, rejected by default in `ci-light` (§ above) |
