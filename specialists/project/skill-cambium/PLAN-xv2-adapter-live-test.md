# Plan: finish the Cambium XV2 adapter live test (resume point)

**Status: DONE, same session, 2026-09-17.** Operator chose to continue rather than pause. Result below.

## Result

Ran `scripts/cambium_xv2_adapter.py` against the real Hope Vale Tower 1 AP (`10.255.3.1`) via `tsh ssh --proxy teleport.communitywifi.net.au -L 10001:10.255.3.1:443 root@hope-vale-smc01`.
`get_facts()` returned exactly the expected values (hostname `HOP_XV2_AP1_IP3_1`, serial `WLYB0501N05R`, firmware `6.6.0.3-r9`, MAC `BC-A9-93-30-23-2A`, live `cnmaestro_status`). Confirms: **no formal
CLI/API schema was needed** — ~170 lines of stdlib Python, zero dependencies, resolved the question definitively.

One real bug found and fixed by normal engineering (not something a schema would have prevented — a vendor API data-semantics issue, not a syntax one): the first `get_interfaces()` draft used
`port_stats[].link`, which read `"DOWN"` for every port including `ETH1` even though `ETH1` was physically up and passing real traffic. `device-summary` carries a *separate* `port_status[]` array with
the authoritative link/speed/duplex (integer 1/0 encoding) — fixed to merge `port_status` (link/speed/duplex) with `port_stats` (counters) by port name. Re-run confirmed `ETH1: is_up=true, 1000M,
FULL` — matches the real port_status data already seen in evidence E101.

Written back to `skill-cambium`'s `CHANGELOG.md` and `SCRATCHPAD.md`; `skill-walk-before-run`'s `ledger.jsonl` given a RESOLVED entry (mirrored to `cambium-swap/.wbr-ledger.jsonl` and its
`SCRATCHPAD.md`).

## Contents

- [Result](#result)
- [Goal](#goal)
- [Why this matters — the decision it resolves](#why-this-matters--the-decision-it-resolves)
- [What is already done](#what-is-already-done)
- [Exact steps to resume](#exact-steps-to-resume)
- [After it runs](#after-it-runs)
- [Multi-vendor context (for when this pattern repeats)](#multi-vendor-context-for-when-this-pattern-repeats)
- [Key facts to preserve](#key-facts-to-preserve)
## Goal

Prove — with real, running code against a real device, not opinion — whether the Cambium vendor adapter (part of `cambium-swap`'s Option 3 custom-controller work) needs a formal CLI/API schema
(command-schema.json, OpenAPI generation, Tree-sitter/ANTLR grammar, an AI-extraction pipeline) before it can be written, or whether plain hand-written code is enough.

## Why this matters — the decision it resolves

Operator proposed building a `device-interface-modeler` skill (formal CLI grammar + OpenAPI + capability-model YAML, AI-extraction from vendor docs, provenance tracking) after seeing how many REST
endpoints/SSH commands a single Cambium family exposes, and confirmed the plan is to go multi-vendor later (Cambium now, MikroTik/Ubiquiti/others eventually).

Ran `skill-walk-before-run` against that proposal. **Verdict: RED** — no adapter code existed for any vendor yet (signal 1: no reality contact), and the proposal was peripheral tooling on top of a
still-stubbed core capability (signal 4). Cheapest test agreed with the operator: hand-write `get_facts()`/`get_interfaces()` in plain Python against the real device, see if a schema was actually
needed.

Disconfirming result agreed up front: if this works in well under an hour with zero schema/dependencies, that kills the case for building the elaborate tooling now — it would mean solving a problem
the project doesn't have yet. (Full reasoning on why multi-vendor doesn't change this: a schema designed from one vendor's shape, before a second vendor exists to design against, is a guess that gets
redone anyway. The actual cross-vendor abstraction already exists — `unified-network-controller`'s `docs/controller-option3/option-3-architecture.md`'s adapter contract, `get_facts`/`get_interfaces`/... —
each vendor just needs its own skill pack implementing those same method names, same pattern as `skill-smc`/`skill-cambium` already being separate packs.)

Operator confirmed: proceed with the code test (not the docs-only alternative), and **all Cambium development work goes into `skill-cambium`, not into `cambium-swap`** — `cambium-swap` is the
live-deployment/evidence project; `skill-cambium` is the cross-project canonical home for reusable Cambium knowledge and code.

## What is already done

- [scripts/cambium_xv2_adapter.py](scripts/cambium_xv2_adapter.py) — written, **not yet executed**. Stdlib-only (`urllib.request`, `http.cookiejar`, `ssl`, `json` — no `requests`, no venv/dependency
  needed, runs with plain `python3`). Implements:
  - `CambiumXV2Adapter.login()` / `.logout()` — `POST /api/login` (JSON `{"username","password"}`), tracks the `XSRF-TOKEN` cookie and echoes it as an `X-XSRF-TOKEN` header on every later call
    (required — confirmed live 2026-09-17, calls 401 without it even with valid session cookies).
  - `.get_facts()` — calls `GET /api/platform-info` + `GET /api/device-summary`, returns vendor/model/hostname/serial/os_version/uptime/mac/cnMaestro-connection-state.
  - `.get_interfaces()` — calls `GET /api/device-summary`, extracts `port_stats` into a NAPALM-shaped per-port dict (is_up/speed/duplex/rx/tx counters/errors).
  - `main()` reads `CAMBIUM_HOST`/`CAMBIUM_USER`/`CAMBIUM_PASS` from env — **never hardcode or print `CAMBIUM_PASS`**.
- Reference/evidence work already committed in `cambium-swap` (read-only prerequisite knowledge, already proven live before this adapter was written):
  - `unified-network-controller/docs/controller-option3/cambium-vendor-adapter-data-points.md` — the curated (not exhaustive) list of which REST endpoints/CLI commands matter for the controller, mapped to adapter
    method names. This adapter file implements two rows of that table.
  - Evidence E99 (SSH CLI `show version`), E100 (web UI tunnel HTTP 200), E101 (authenticated REST API session — `platform-info`/`device-summary` real data), E102 (exact firmware-version-matched CLI
    Reference Guide, Release 6.6.0.3, superseding the 7.2 guide for this specific fleet).
  - `skill-smc`'s `references/01_overview.md` — canonical `tsh ssh --proxy <cluster> -L <local_port>:<device_ip>:<device_port> root@<smc-hostname>` tunnel form (the `--proxy` flag matters — an earlier
    attempt without it was flaky).

## Exact steps to resume

1. **Check Teleport session**: `tsh status` — need a valid (non-expired) profile for `teleport.communitywifi.net.au`. Re-`tsh login --proxy=teleport.communitywifi.net.au` if expired.
2. **Open the tunnel** (background task, ~120s window — re-run this step if it expires mid-work):
   ```bash
   tsh ssh --proxy teleport.communitywifi.net.au -L 10001:10.255.3.1:443 root@hope-vale-smc01 sleep 120
   ```
Verify with `nc -z -w3 localhost 10001`.
3. **Fetch the device credential** (never print the value):
   ```bash
   DEV_USER=$(kp show -s -a UserName cambium-devices/enterprise-wifi)
   DEV_PASS=$(kp show -s -a Password cambium-devices/enterprise-wifi)
   ```
`kp` must resolve on `PATH` (symlinked to `~/.local/bin/kp` — see `references/02_device-access-and-vault.md`). If running this from inside the `cambium-swap` project directory, its
`.claude/settings.local.json` already allow-lists this exact `kp show ... cambium-devices/*` pattern; from elsewhere it may need approval.
4. **Run the adapter**:
   ```bash
   CAMBIUM_HOST=localhost:10001 CAMBIUM_USER="$DEV_USER" CAMBIUM_PASS="$DEV_PASS" \
     python3 /Users/malik.ahmad/.claude/skills/skill-cambium/scripts/cambium_xv2_adapter.py
   ```
5. **Inspect the JSON output.** Expect `facts.hostname == "HOP_XV2_AP1_IP3_1"`, `facts.serial_number == "WLYB0501N05R"`, `facts.os_version == "6.6.0.3-r9"` (matches E99/E101's already-observed
   values), plus an `interfaces` dict keyed by port name (`PORT-CHANNEL1`, `VLAN501`, `VLAN500`, `ETH1`, `ETH2` per the raw data already seen in E101).
6. If it fails: check whether the tunnel window expired mid-run (re-open it, step 2) before assuming a code bug — this bit twice already this session.

## After it runs

- **If it works as expected** (near-certain, since both endpoints were already called manually and returned exactly this data under E101): that's the resolving evidence. Update:
  - This file's Status line to DONE, with the actual JSON output summarized (not the credential).
  - `skill-walk-before-run`'s `ledger.jsonl` — append a RESOLVED entry for the "formal schema needed?" assumption, `result: PASS` meaning the *disconfirming* result did NOT occur (schema was not
    needed) — i.e. the proposal to build `device-interface-modeler` now stays correctly rejected. Mirror to `cambium-swap/.wbr-ledger.jsonl` and its `SCRATCHPAD.md` per the skill's own write-back
    rule.
  - `skill-cambium/CHANGELOG.md` — new entry for the adapter script + the resolved test.
  - `skill-cambium/SCRATCHPAD.md` — this file is stale (still says "Phase: Bootstrap"); fold this session's work in properly once the test is done, not before (avoid two half-updated state files).
- **Then decide** (operator call, not pre-decided): extend this same adapter with `get_radios`/`get_wlans`/`get_clients`/`get_config` (the remaining rows in `unified-network-controller/docs/controller-option3/cambium-vendor-adapter-data-points.md`),
  or move to the "stub files for the other 4 Cambium families" option that was deferred in favor of this test, or pause Cambium adapter work entirely until Option 3's controller bake-off actually
  needs it.

## Multi-vendor context (for when this pattern repeats)

- When a second vendor (MikroTik, Ubiquiti, ...) is actually being onboarded: check for an existing maintained Python library first (`librouteros` for MikroTik, `aiounifi` for UniFi both already
  exist) — Cambium needed hand-rolled code specifically because no maintained OSS client exists for it.
- If hand-rolled code is needed for that vendor too: give it its own specialist skill pack (`skill-<vendor>`), same shape as this one — not a shared generic schema, and not folded into
  `skill-cambium`.
- Only revisit the formal-schema question once **two** real vendor adapters exist to design a genuine cross-vendor abstraction against — one data point can't validate a generic schema.

## Key facts to preserve

| Fact              | Value                                                                                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Test device       | Hope Vale Tower 1, Enterprise Wi-Fi XV2-2T0, `HOP_XV2_AP1_IP3_1`, `10.255.3.1`                                                                                                   |
| Teleport cluster  | `teleport.communitywifi.net.au` (NOT `apn.au` — `hope-vale` is `nbn_accelerate` flavour)                                                                                         |
| Jump host         | `hope-vale-smc01`                                                                                                                                                                |
| Tunnel form       | `tsh ssh --proxy <cluster> -L <local_port>:<device_ip>:<443\|80> root@<smc-hostname>` — `--proxy` required                                                                       |
| Device credential | `<secret:keepassxc:cambium-devices/enterprise-wifi>`, username `admin`                                                                                                           |
| Auth endpoint     | `POST /api/login` JSON body, `api_token`+`XSRF-TOKEN` cookies, `X-XSRF-TOKEN` header on every later call, `POST /api/logout` to end                                              |
| Related project   | `/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap` — evidence E99-E102,                                                                                                 |
|                   |   `unified-network-controller/docs/controller-option3/cambium-vendor-adapter-data-points.md`, `unified-network-controller/docs/controller-option3/option-3-architecture.md`                                                                          |
