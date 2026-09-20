# Script Inventory

Runnable scripts and task entrypoints for skill-cambium. Prefer `just --list` / `just <task>` — the [justfile](../justfile) routes every recipe through the pinned working-cache venv
(`/Volumes/Data/_ai/_skills/skills-working-cache/skill-cambium/.venv`, built by `just bootstrap` from `.mise.toml` + `requirements.txt`). Raw script inventory below is for reference, not direct
invocation.

`just tunnel` does not run a script from this directory — it calls [skill-smc's `skill-smc/scripts/teleport-tunnel.sh`](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/scripts/teleport-tunnel.sh) directly, since Teleport
tunneling is that pack's concern, not this one's. Consuming projects call the canonical path directly rather than this pack keeping its own copy — same pattern as `cambium-portal.sh` below, in the
other direction.

## Contents

- [Raw Script Inventory](#raw-script-inventory)
- [Safety Labels](#safety-labels)
- [Maintenance Rules](#maintenance-rules)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules-1)

---

## Raw Script Inventory

| Script                      | Purpose                        | Inputs                                | Outputs                        | Safety           | Idempotent   | When to use                |
| --------------------------- | ------------------------------ | ------------------------------------- | ------------------------------ | ---------------- | ------------ | -------------------------- |
| `fleet_schema_sweep.py` | Stage 2 of the schema exercise: picks one representative device per family per site, contracts its responses, and records unreachable or empty as findings rather than skips | `--inventory` (cambium-swap's device-inventory.csv), optional `--sites`/`--families`; credentials read from the `cambium-devices/` vault | Observations under `schemas/_observations/<family>/`, plus a findings log | `safe`, `external-network`, `requires-secrets`, `requires-credentials` | Yes — resumable, skips a site/family that already has an observation | Building or refreshing the fleet-wide contract |
| `schema_divergence_report.py` | Reports where devices of one family disagree about their own response shape — universal fields versus splits by model, firmware or site, plus type conflicts | `--schemas` (the schemas tree) | A generated markdown divergence report | `safe`, `modifies-files` | Yes — regenerated from observations each run | After a sweep, to decide where the adapter needs a branch rather than a default |
| `schema_tool.py` | Derives, merges and enforces the device response contract — `observe` one device, `merge` observations into the family standard, `check` a new observation for divergence | Live device via `--driver falcon` (usually a Teleport port-forward) or an adapter's stdout via `--driver stdin`; `CAMBIUM_USER`/`CAMBIUM_PASS` | JSON Schema files under `schemas/<family>/`, observations under `schemas/_observations/`; no response values recorded | `safe`, `external-network`, `requires-secrets`, `requires-credentials` | Yes — read-only | Before writing adapter field mappings; when a new site, model or firmware appears |
| `check_governance.py` | Governance coherence checks for this pack — | This pack's own files | Console, exit status | `safe` | Yes | Before claiming |
|  |   turns its documented claims |  |  |  |  |   any durable |
|  |   into assertions |  |  |  |  |   change to this |
|  |  |  |  |  |  |   pack |
|  |  |  |  |  |  |   is complete |
| `extract-asset-register.py` | One-off Hope Vale / Burringurrah | cambium-swap's | Per-site extract CSVs, | `modifies-files` | No — appends, | Reference |
|  |   asset-register extraction — worked |   `inventory/asset-register/*.xlsx` |   appended into |  |   no dedup |   implementation |
|  |   example, not general-purpose (see its |  |   cambium-swap's |  |  |   when |
|  |   own docstring) |  |   `device-inventory.csv` |  |  |   extracting a |
|  |  |  |  |  |  |   new site's |
|  |  |  |  |  |  |   register |
|  |  |  |  |  |  |   (re-read its |
|  |  |  |  |  |  |   columns first) |
| `cambium-portal.sh` | Cambium support-portal | `kp` vault entry "/Network/cambium | Downloaded release files | `external-network`, | `login` no (new | Fetching a dated |
|  |   (support.cambiumnetworks.com) automation: |   support" (UserName+Password), a |   + sha256 manifest to |   `requires-credentials` |   session each |   release's |
|  |   `login` and |   live MFA code pasted |   stdout, into a |  |   run); |   firmware/MIB |
|  |   `fetch-release <model> <version> <dest>`. |   interactively (no stored |   caller-chosen dest dir |  |   `fetch-release` |   files, or |
|  |   Read-only against the portal — never |   TOTP seed) |  |  |   yes (re-derives |   confirming |
|  |   uploads or changes anything Cambium-side. |  |  |  |   per-session |   what a release |
|  |   Moved here from |  |  |  |   links and |   actually |
|  |   `cambium-swap` 2026-09-17. |  |  |  |   re-downloads) |   contains, |
|  |  |  |  |  |  |   without a |
|  |  |  |  |  |  |   manual browser |
|  |  |  |  |  |  |   session |
| `cambium_xv2_adapter.py` | Minimal Enterprise Wi-Fi (XV2/Falcon | `CAMBIUM_HOST`/`CAMBIUM_USER`/ | JSON (facts + | `external-network`, | Yes | Reading real |
|  | UI) REST adapter — `login`/`logout`, | `CAMBIUM_PASS` env vars; a live | interfaces) to stdout | `requires-credentials` |  | device state |
|  |   `get_facts()`, `get_interfaces()`. |   tunnel to the device's HTTPS port |  |  |  |   from an XV2 |
|  |   Stdlib-only, no `requests`, no venv. |  |  |  |  |   AP; the first |
|  |   Verified live against Hope Vale Tower |  |  |  |  |   two getters |
|  |   1, 2026-09-17. |  |  |  |  |   for Option 3's |
|  |  |  |  |  |  |   Cambium |
|  |  |  |  |  |  |   vendor adapter |
| `cambium_epmp_adapter.py` | Minimal ePMP AP/SM (LuCI-derived JSON RPC) | `CAMBIUM_HOST`/`CAMBIUM_USER`/ | JSON (facts, interfaces, | `external-network`, | Yes | Reading real |
|  |   adapter — `login`/`logout`, |   `CAMBIUM_PASS` env vars; a live |   wireless_link, |   `requires-credentials` |  |   device state |
|  |   `get_facts()`, `get_interfaces()`, |   tunnel to the device's HTTPS port |   clients) to stdout; |  |  |   from an ePMP |
|  |   `get_wireless_link()` (SM), |  |   `--include-config` |  |  |   AP or SM; |
|  |   `get_clients()` (AP), `get_config()` |  |   prints the redacted |  |  |   `get_config()` |
|  |   (redacted, behind `--include-config`). |  |   config |  |  |   only when |
|  |   Stdlib-only. Verified live against Hope |  |   snapshot instead |  |  |   actually |
|  |   Vale Tower 5 (SM) and Tower 1 Omni0 |  |  |  |  |   needed — |
|  |   (AP), 2026-09-17 |  |  |  |  |   carries real |
|  |  |  |  |  |  |   secrets |
|  |  |  |  |  |  |   pre-redaction, |
|  |  |  |  |  |  |   see |
|  |  |  |  |  |  |   its docstring |
| `cambium_cnwave_adapter.py` | Minimal cnWave 60GHz REST adapter — | `CAMBIUM_HOST`/`CAMBIUM_USER`/ | JSON (facts, e2e_info, | `external-network`, | Yes | Reading real |
|  |   `login()`/`logout()`, `get_facts()`, |   `CAMBIUM_PASS` env vars; a live |   status, capability, |   `requires-credentials` |  |   device state |
|  |   `get_e2e_info()`, `get_status()`, |   tunnel to the device's HTTPS port |   links_count, gps, |  |  |   from a cnWave |
|  |   `get_capability()`, `get_links_count()`, |  |   config, and — only |  |  |   node; |
|  |   `get_gps()`, `get_topology()`, |  |   when e2e_info is |  |  |   topology/ |
|  |   `get_ctrl_status_dump()` (E2E-role only), |  |   enabled — topology, |  |  |   ctrl_status_dump |
|  |   `get_config()` (redacted). Stdlib-only, |  |   ctrl_status_dump) |  |  |   only |
|  |   JWT bearer-token auth, not cookies. |  |   to stdout |  |  |   meaningful |
|  |   Verified live against Hope Vale's V5000 |  |  |  |  |   from an E2E- |
|  |   (E2E/POP role) and V2000 (plain Client |  |  |  |  |   role node |
|  |   Node), 2026-09-17. SSH TUI has no |  |  |  |  |  |
|  |   official docs at all — REST is the real |  |  |  |  |  |
|  |   adapter path, see its docstring |  |  |  |  |  |
| `cambium_r195p_adapter.py` | Minimal cnPilot R195P SSH adapter — | `CAMBIUM_HOST`/`CAMBIUM_USER`/ | JSON (facts, | `external-network`, | Yes | Reading real |
|  | `login()`/`logout()`, `get_facts()`, | `CAMBIUM_PASS` env vars; | interfaces) to stdout | `requires-credentials` |  | device state |
|  |   `get_interfaces()`. No REST API confirmed |   `ssh`/`sshpass` on PATH; network |  |  |  |   from a real |
|  |   for this family — shells out to system |   access to the device (normally a |  |  |  |   R195P; only |
|  |   `ssh`/`sshpass`, not a pure-stdlib |   `tsh` tunnel through the site's |  |  |  |   family whose |
|  |   client. Verified live against two real |   SMC box) |  |  |  |   adapter shells |
|  |   Burringurrah units, 2026-09-17. No |  |  |  |  |   out to `ssh` |
|  |   `get_config()` — deliberately not |  |  |  |  |   instead of |
|  |   implemented, this family's SNMP community |  |  |  |  |   using a |
|  |   is fleet-wide and this project has two |  |  |  |  |   REST/HTTP |
|  |   prior secret-exposure incidents from |  |  |  |  |   client — see |
|  |   unscoped config dumps on other families |  |  |  |  |   its docstring |
| `scan-config-fields.py` | Reports which keys in a JSON file look | A JSON file path, or `-` for stdin | Console report: flagged | `safe` | Yes | Before viewing |
|  |   credential-shaped, without ever printing |  |   key path + |  |  |   any captured |
|  |   their values. Written after two live |  |   empty/non-empty per |  |  |   config/status |
|  |   secret-exposure incidents this session — |  |   key, exit 1 if |  |  |   dump by hand — |
|  |   both caused by printing a value to "check |  |   any found |  |  |   run this |
|  |   if it's real" instead of just |  |  |  |  |   first, never |
|  |   checking `bool(v)` |  |  |  |  |   eyeball-scan |
|  |  |  |  |  |  |   raw JSON |
|  |  |  |  |  |  |   for secrets |
| `generate_site_addressing_families.py` | Derives a site's `families:` block | `--flavour rcp\|nbn_accelerate`, | YAML fragment to | `safe` | Yes | Onboarding a |
|  | (octet_pattern/host_count per device | `--site <slug>` or `--all`, | stdout — never writes |  |  | new site's |
|  | family) | optional `--inventory-root` | `references/site-addressing.yaml` |  |  | export, or |
|  |   for `references/site-addressing.yaml` |  |  |  |  |  |
|  | straight from a site's reconciled | (default: cambium-swap's | directly (hand-authored |  |  | regenerating |
|  | `*_cnmaestro-inventory.csv` — the same | `inventory/asset-register/`) | live-session notes there |  |  | one after its |
|  | computation evidence E124/E125/E126 |  | aren't derivable from a |  |  | export |
|  | (cambium-swap) did by hand for the |  | CSV and would be lost by |  |  | changes |
|  | 2026-09-18 split. Written after that manual |  | a blind overwrite) |  |  |  |
|  |   pass, per operator instruction to make it |  |  |  |  |  |
|  |   a persistent, reusable tool. |  |  |  |  |  |
|  |   `--oui-audit` (added 2026-09-18, evidence |  |  |  |  |  |
|  |   E129) reports OUI blocks in |  |  |  |  |  |
|  |   `device-inventory.csv` missing from |  |  |  |  |  |
|  |   `oui_reference` instead — same |  |  |  |  |  |
|  |   never-writes-the-file design. |  |  |  |  |  |

## Safety Labels

- `safe` — Read-only or low-risk repeatable operation
- `review-required` — Needs human review before execution
- `destructive` — Deletes, overwrites, migrates, deploys, or changes external state
- `external-network` — Calls external services or APIs
- `modifies-files` — Writes to repo/project files
- `requires-secrets` — Requires secret values
- `requires-credentials` — Requires authenticated local/session credentials
- `long-running` — May take significant time
- `unknown` — Not yet classified; do not run without inspection

## Maintenance Rules

- Keep this file aligned with `scripts/`; `check_governance.py` fails on an uncatalogued script.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.
- Run with `python3 scripts/check_governance.py` (no venv in this pack — stdlib only).

<!-- BEGIN MANAGED: skill-ai-it:scripts --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

