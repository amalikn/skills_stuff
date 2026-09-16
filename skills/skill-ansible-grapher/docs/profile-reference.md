# Profile reference

Source of truth: `config/profiles.yaml`. This doc explains intent; flags are the
canonical detail.

## Inventory profiles

| Profile | Variables | Orientation | Formats | Use when |
|---|---|---|---|---|
| `inventory-summary` (default) | off | TB | dot, svg | General documentation, quick look |
| `inventory-detailed` | off | TB, extra spacing | dot, svg, png | Larger inventories needing more room |
| `inventory-left-right` | off | LR | dot, svg | Wide infrastructure diagrams |
| `inventory-uml` | off | LR, orthogonal | dot, svg | Inheritance-style topology view |

All inventory profiles suppress variables by default — pass `--show-variables`
explicitly on any of them if you need value display (and read
`docs/security-and-safety.md` first).

All inventory and playbook profiles set `strict_ansible_version_match: false` and
`allow_development_tool_versions: true` — mismatches/dev-version tools are reported
(WARN) but never block interactive/local use. See `SKILL.md` §19.

## Playbook profiles

| Profile | Role tasks | Handlers | Roles only | Renderer | Use when |
|---|---|---|---|---|---|
| `playbook-summary` (default) | no | no | no | graphviz | General documentation |
| `playbook-roles` | n/a | no | yes, grouped by name | graphviz | Role-focused overview |
| `playbook-detailed` | yes | yes | no | graphviz (+ dot) | Deep analysis, collapsible nodes |
| `playbook-mermaid` | n/a | no | grouped by name | mermaid-flowchart (LR) | Markdown embedding |
| `playbook-json` | n/a | n/a | n/a | json | Downstream/automated analysis |

## Combined profiles

| Profile | Contents | Compatibility policy | Use when |
|---|---|---|---|
| `documentation-pack` | inventory SVG+DOT, playbook SVG+Mermaid+JSON, manifest, index, validation report | Inherits sub-profile defaults (warn, permissive) | Full repo documentation |
| `ci-light` | inventory SVG+DOT, playbook JSON only, no viewer, no timestamps | **Strict**: `strict_ansible_version_match: true`, `allow_development_tool_versions: false`, no system-Python fallback, no dynamic inventory, no variable display, bounded artifacts, no network dependency, machine-readable validation report | Deterministic CI artifact generation |

`ci-light`'s strict policy is deliberate hardening, not a bug — see `SKILL.md` §19. **On
this machine it fails by default** (the installed `ansible-playbook-grapher` is a
`2.11.0-dev0` build whose venv pins a different `ansible-core` than the system
validator). Pass `--allow-ansible-version-mismatch --allow-development-tool-versions` (or
use `documentation-pack`) to proceed anyway.

## Choosing a profile

- Unsure → start with `inventory-summary` + `playbook-summary` (both defaults).
- Repo is large → `discover` first; it recommends `playbook-roles` automatically when
  more than 2 playbook candidates are found.
- Need something to paste into a wiki page → `playbook-mermaid`.
- Need machine-readable output for further tooling → `playbook-json`.
- Building a CI artifact → `ci-light` (no browser interaction, deterministic filenames,
  strict toolchain compatibility — expect to need an explicit override on a dev-build
  install; see above).
