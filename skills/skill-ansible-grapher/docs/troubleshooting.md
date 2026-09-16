# Troubleshooting

## "Missing dependency" (exit 5)

`ansible-grapher validate` names the missing executable. This skill never installs or
upgrades anything automatically. Fixes:

- `ansible-inventory-grapher` / `ansible-playbook-grapher` not found: export
  `ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN` / `ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN` to the
  installed launcher scripts (see README.md), or add them to `PATH`.
- Graphviz `dot` missing: `brew install graphviz` (macOS) — this is a genuine system
  prerequisite the skill does not manage.

## Inventory parse failures

- `ansible-inventory -i <path> --list` exits non-zero → fix the inventory syntax.
- `ansible-inventory` exits `0` but this skill still reports failure: every inventory
  plugin (yaml/ini/auto) failed to parse the source and Ansible silently fell back to
  "implicit localhost only." This skill treats that fallback as invalid (see
  `SKILL.md` §19) rather than reporting a false pass.

## Missing collections / roles

`discover` flags `requirements.yml`/`requirements.yaml` presence as a risk. If a
playbook references roles/collections not installed locally, `ansible-playbook
--syntax-check` may still pass (syntax check does not resolve role/collection content)
but `ansible-playbook-grapher` may fail when it tries to expand role tasks
(`--include-role-tasks`). Install requirements first (`ansible-galaxy install -r
requirements.yml`) — this skill does not do this for you.

## `couldn't resolve module/action` from the playbook grapher, but `--syntax-check` passes clean

Symptom: `ansible-playbook-grapher` raises `AnsibleParserError: couldn't resolve
module/action 'X'` for a bare (non-FQCN) module name that ships in a standard collection
(e.g. `mount`/`sysctl` → `ansible.posix`), while the system `ansible-playbook
--syntax-check` on the same file passes with only deprecation warnings.

Root cause: `ansible-playbook-grapher`'s own isolated venv
(`tools_stuff/ansible-playbook-grapher/.../tools-working-cache/.venv`) is typically a bare
`pip install ansible-core` with **zero bundled collections** — confirmed by the absence
of an `ansible_collections` directory in its `site-packages`. This differs from a system
`ansible-playbook` install that bundles collections (e.g. Homebrew's `ansible` meta-package
ships `ansible.posix`/`community.general`) or that resolves a project's own
`ansible.cfg` → `COLLECTIONS_PATH`. This is unrelated to the "Missing collections / roles"
case above — no `requirements.yml` install fixes it, because the grapher's venv has no
collection search path at all by default.

Fix (env-only, do not modify the grapher's own venv): before invoking `graph-playbook`/
`graph-project`, set `ANSIBLE_COLLECTIONS_PATH` to include both the project's own
`./collections` (per its `ansible.cfg`) and a source that actually has the missing
collection, e.g.:
```bash
export ANSIBLE_COLLECTIONS_PATH=/path/to/project/collections:/opt/homebrew/Cellar/ansible/<version>/libexec/lib/python3.14/site-packages
```
(substitute the Homebrew `ansible` Cellar version installed on the machine, or any other
location with a real `ansible_collections/` tree — `ansible-galaxy collection list` shows
where collections are currently resolved from for the system interpreter).

## Graphviz renderer crash on handler-notify links (`TypeError` sorting `NoneType`)

Symptom: `ansible-playbook-grapher` crashes with
`TypeError: '<' not supported between instances of 'NoneType' and 'NoneType'` inside
`get_notified_handlers()` (`graph_model.py`, around the `sorted(notified_handlers, key=lambda
x: x.index)` call), during the graphviz renderer's link-insertion postprocessing step.

This is an upstream bug in the installed `ansible-playbook-grapher`, reproduced on a
development build (`2.11.0-dev0`) — not a repo/playbook syntax problem, and not something
this skill patches (it does not modify the installed tools). It is playbook-specific: some
playbooks with `notify:` handlers hit it, others in the same repo do not.

Workaround: switch renderers for the affected playbook — `--profile playbook-mermaid`
(renderer `mermaid-flowchart`) or `--renderer json` use a different code path in the
postprocessor and do not hit this crash. Structural content is equivalent; only the output
format differs (`.mmd`/`.json` instead of `.svg`).

## Unsupported installed Ansible version / grapher flags

`docs/tool-capabilities.md` records the exact `--help` output this skill was built
against. If a flag referenced in `config/profiles.yaml` is no longer valid after an
upstream upgrade, the underlying tool will error with "unrecognized arguments" — that is
a validation failure (exit `4`), not a silent misconfiguration. Re-run
`scripts/graph-playbook --help` / `scripts/graph-inventory --help` (via their real
binaries) and update `config/profiles.yaml` accordingly.

## Unresolved variables / dynamic includes in playbook graphs

Static parsing cannot resolve `include_tasks`/`import_tasks` paths that depend on
runtime variables, nor loop/conditional outcomes. The graph will show what could be
statically determined; anything variable-dependent is a known gap, not a bug — see
`SKILL.md` §19.

## Vault errors

`--ask-vault-pass`/prompted vault input is not appropriate for this skill's non-
interactive flows. Use `--vault-password-file` pointing at a file the calling shell
already trusts; this skill never reads or logs its contents.

## Excessively large graphs

- `inventory` warns when host count exceeds `thresholds.max_inventory_hosts_before_warning`
  (default 200) — narrow with `--pattern` or use `inventory-summary`.
- `discover` caps recommended playbooks at `thresholds.max_auto_selected_playbooks`
  (default 5) and reports the drop count.
- Prefer SVG over PNG for large graphs (`docs/profile-reference.md`).

## SVG viewer limitations

Generated SVGs use standard Graphviz output; if a viewer doesn't render double-click
navigation (`--open-protocol-handler`), that's a viewer limitation, not a generation
failure — this skill never launches a viewer automatically (`--view` is never passed).

## Mermaid rendering issues

`.mmd` files are raw Mermaid source. If a Markdown renderer doesn't show the diagram,
confirm it supports fenced ```` ```mermaid ```` blocks and check
`--renderer-mermaid-directive` compatibility with your renderer's Mermaid version.

## Unexpected `ansible.cfg` effects

`ansible-inventory`/`ansible-playbook --syntax-check` respect any `ansible.cfg`
discoverable from the current working directory or `ANSIBLE_CONFIG`. `discover` reports
the found `ansible.cfg` path — if validation behaves unexpectedly, check that file first
before assuming a skill bug.

## Python environment / version conflicts

- This skill's own dependency (PyYAML) lives in
  `/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv`
  (Python 3.14, via `mise`). `scripts/*` and the `justfile` **do not silently fall back**
  to system `python3` — if the managed venv is missing they fail clearly (exit `5`) with
  a rebuild command. Rebuild it:
  ```bash
  cd /Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher
  mise install
  mise exec -- python -m venv .venv
  .venv/bin/python -m pip install PyYAML
  ```
  Supported interpreter range: Python 3.10–3.14 (`config/default.yaml` →
  `python_runtime`); 3.14 is this stack's pinned default, not a hard requirement.
- To explicitly opt into a system-Python fallback instead of rebuilding the venv
  (e.g. a throwaway environment), pass `--allow-system-python-fallback` to any
  `scripts/*` entrypoint, or set `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1`. This
  is always logged and recorded as `runtime_isolation: degraded` — it is never silent.
- `ansible-inventory-grapher` and `ansible-playbook-grapher` each run in their **own**
  isolated venvs under `tools_stuff/*/tools-working-cache` with different pinned
  `ansible-core` versions (2.21.1 vs. 2.18.2) — this is expected and does not need to be
  reconciled; they serve different purposes (topology grapher vs. playbook grapher). The
  mismatch is detected and reported by `ansible-grapher validate`/`inventory`/`playbook`
  (see next section), not silently ignored.
- Non-deterministic DOT/SVG byte output between runs of the same input: both grapher
  tools iterate Python sets/dicts whose default ordering depends on `PYTHONHASHSEED`.
  This skill pins `PYTHONHASHSEED=0` for both subprocess invocations
  (`deterministic_env()` in `scripts/ansible-grapher`) specifically to prevent this —
  if you invoke the raw upstream binaries directly (bypassing this skill), you may
  observe run-to-run differences that this skill's own output will not have.

## Ansible-version mismatch between validation and a grapher (WARN or FAIL)

`ansible-grapher validate --format json` (or the console report from `inventory`/
`playbook`/`project`) reports `playbook_ansible_version_match` / `inventory_ansible_version_match`
with a `PASS`/`WARN`/`FAIL`/`UNKNOWN` status. On this machine, the playbook path shows
`WARN` by default (system `ansible-core 2.21.1` vs. the playbook grapher's own venv
`2.18.2`) — this is expected, not a bug (see `docs/tool-capabilities.md`). To make this a
hard failure instead, pass `--strict-ansible-version-match`; to proceed anyway even in
strict/`ci-light` contexts, pass `--allow-ansible-version-mismatch`.

## Development/prerelease grapher version rejected

If a run fails with a message about a "development version" (e.g. under `ci-light`),
the installed grapher's `--version` string was classified `development`/`prerelease`
(contains `dev`/`rc`/`alpha`/`beta`) and `allow_development_tool_versions` is disabled
for the active profile/policy. Pass `--allow-development-tool-versions` to permit it, or
install a stable release if reproducibility is the concern.

## Expected artifact missing or invalid after a "successful" grapher run (exit 7)

If a grapher exits `0` but the run still fails, this skill detected one of:
- no output file was created at the expected path,
- the file is empty, or
- the file's content doesn't match its expected format (no `<svg`, invalid JSON, no
  Mermaid graph declaration, or DOT not starting with `graph`/`digraph`).

This is intentional — an upstream exit code of `0` is not treated as proof of a valid
result. Check the grapher's own stderr (recorded in `logs/commands.log`) for warnings
about the input that might explain the empty/invalid output.
