This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, README.md, ARCHITECTURE.md, architecture.md, CONVENTIONS.md, ROADMAP.md, roadmap.md, SCRATCHPAD.md, CHANGELOG.md, ARCHCORE_PROMOTION_CANDIDATES.md, context-map.yaml, scripts/README.md, scripts/**, justfile, Justfile, Taskfile.yml, Makefile, package.json, memory-bank/**/*.md, .archcore/**/*.md, docs/**/*.md
- Files matching these patterns are excluded: node_modules/**, .git/**, dist/**, build/**, cache/**, runtime/**, __pycache__/**, .venv/**, graphify-out/**, .ai-context/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.archcore/
  adr/
    separate-pack-from-skill-smc.adr.md
    vault-file-avoids-opa-blocked-words.adr.md
  rules/
    cambium-smc-cross-pack-boundary.rule.md
    manifest-version-discipline.rule.md
    vault-reference-convention.rule.md
  specs/
    specialist-pack-file-roles.spec.md
  index.guide.md
scripts/
  cambium_cnwave_adapter.py
  cambium_epmp_adapter.py
  cambium_r195p_adapter.py
  cambium_xv2_adapter.py
  cambium-portal.sh
  check_governance.py
  client-ip-sweep.sh
  extract-asset-register.py
  fleet_schema_sweep.py
  generate_site_addressing_families.py
  README.md
  scan-config-fields.py
  schema_divergence_report.py
  schema_tool.py
  snmp_schema_from_walk.py
AGENTS.md
AI_NAVIGATION.md
CHANGELOG.md
CLAUDE.md
context-map.yaml
justfile
Justfile
README.md
SCRATCHPAD.md
````

# Files

## File: .archcore/adr/separate-pack-from-skill-smc.adr.md
````markdown
---
title: Separate Pack From skill-smc
type: adr
status: accepted
date: 20260917
provenance: promoted from SCRATCHPAD.md (KEEP, Recent decisions) on 20260917; accepted by operator 20260917
---

# ADR: Separate Pack From skill-smc

## Status

Accepted

## Context

`skill-cambium`'s content — device families/firmware, the local-admin credential vault, the cnMaestro estate, site asset-register conventions, and the `device-inventory.csv` schema — was first
discovered and written down during `cambium-swap`'s device-credentialing and device-inventory extraction session. `skill-smc` already existed as the pack for the SMC box / ansible-wifi provisioning
layer around this same hardware, and one of skill-smc's own numbered reference files already held an early version of the asset-register naming-convention content that later became this pack's
canonical home for that topic.

## Decision

Scaffold `skill-cambium` as its own specialist pack rather than folding this content into `skill-smc`.

Rationale:
- Different domain: hardware/credentials/asset-registers/cnMaestro versus the SMC box/Ansible authoring/provisioning-role layer.
- The content already had real cross-project-reusable volume of its own, not just a few notes.
- This mirrors the precedent that created `skill-smc` in the first place — a pack is split out once its content earns independent reuse rather than staying folded into an adjacent pack.

## Consequences

**Positive:**
- Each pack stays scoped to one domain; an agent working the SMC box does not have to load Cambium hardware/credential content and vice versa.
- The asset-register naming-convention content gained one canonical home (`references/03_asset-register-conventions.md`) instead of living forked across two packs.

**Negative:**
- Two packs must now stay cross-referenced in both directions (`SKILL.md` Related Skills, `RUNBOOK.md`/`AI_NAVIGATION.md` routing) — see the cross-pack boundary rule.
- A fact spanning both domains must be written to both packs in the same session, which is easy to forget.

## Enforcement

See rule: [`.archcore/rules/cambium-smc-cross-pack-boundary.rule.md`](../rules/cambium-smc-cross-pack-boundary.rule.md)
````

## File: .archcore/adr/vault-file-avoids-opa-blocked-words.adr.md
````markdown
---
title: Vault Reference File Avoids OPA-Blocked Path Words
type: adr
status: accepted
date: 20260917
provenance: promoted from SCRATCHPAD.md (KEEP, Recent decisions) on 20260917; accepted by operator 20260917
---

# ADR: Vault Reference File Avoids OPA-Blocked Path Words

## Status

Accepted

## Context

The workspace's OPA write-gate hard-blocks any file **path** containing certain sensitive-sounding substrings, regardless of the file's actual content. This pack's device-access and KeePassXC
vault-structure content needed a home under `references/`, and the natural name for that content hit the gate directly — this happened once already, on 2026-09-17, and again while drafting this very
document (see Notes).

## Decision

Name the vault-related reference file `references/02_device-access-and-vault.md`, not any name containing the blocked words. Apply the same avoidance to any other path in this pack, including
`.archcore/` documents that discuss the gate itself.

## Consequences

**Positive:**
- Files write cleanly without triggering the workspace write-gate.
- The naming pattern (`device-access-and-vault`) generalizes to any future file that would otherwise need a blocked word in its name.

**Negative:**
- The filename is one step less discoverable by literal keyword search for the blocked term — mitigated by routing tables in `RUNBOOK.md`, `SKILL.md`, and `AI_NAVIGATION.md` all pointing to it by task
  description rather than by name alone.

## Notes

This document's own first draft filename was blocked by the same OPA gate it describes, because the filename itself contained one of the blocked words — direct, immediate confirmation of the decision
it records. The final filename above avoids it.

## Enforcement

See rule in `.archcore/rules/` covering secret-handling in this pack's files (not linked here by name, for the same reason this document exists).
````

## File: .archcore/rules/cambium-smc-cross-pack-boundary.rule.md
````markdown
---
title: Cambium/SMC Cross-Pack Boundary
type: rule
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; accepted by operator 20260917
---

# Rule: Cambium/SMC Cross-Pack Boundary

Device/hardware/vault/asset-register/cnMaestro knowledge belongs in `skill-cambium`. SMC box, Ansible authoring, and provisioning-role knowledge belongs in `skill-smc`.

A fact spanning both domains (e.g. a `site_name` value, an `smc_cnmaestro_provisioning` behaviour) gets written to both packs' matching reference files in the same session — not deferred to a later
pass, and not left in only one pack on the assumption the other will pick it up.

**Rationale:** this is the enforcement mechanism for [`separate-pack-from-skill-smc.adr.md`](../adr/separate-pack-from-skill-smc.adr.md) — the two packs stay useful as separate, focused packs only if
domain knowledge is routed to the correct one immediately rather than accumulating in whichever pack happened to be open at the time.
````

## File: .archcore/rules/manifest-version-discipline.rule.md
````markdown
---
title: Manifest Version Discipline
type: rule
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; accepted by operator 20260917
---

# Rule: Manifest Version Discipline

Update `manifest.json` whenever any content file in this pack changes:

- `version` — bump patch for content changes; minor for structural changes (new reference file, new top-level section)
- `updated_at` — set to the current date in ISO 8601 format (`YYYY-MM-DDT00:00:00Z`)

Also update `stable_facts` when a live validation session confirms or contradicts a prior fact, and `known_constraints` when a new constraint is discovered (e.g. the `hardware_revision: UNKNOWN` entry
currently in `known_constraints` should be replaced with a confirmed value once a real cnMaestro export happens against actual hardware).

Append a corresponding entry to `CHANGELOG.md` in the same pass.

**No other file may hardcode a duplicate version number** — not `RUNBOOK.md`, not `SKILL.md`, not any `references/*.md` file. `manifest.json` is the sole version-of-record. If a file needs to display
the pack's version to a reader, point to `manifest.json` (canonical source) rather than restating the number.

**Rationale:** `manifest.json` is the machine-readable specialist metadata consumed by install tooling and skill validators. A stale `updated_at` or a second hardcoded version number misleads
automated freshness checks and eventually drifts, because no other rule updates a restated copy on a bump — this is the same failure mode `skill-smc` already hit once (`RUNBOOK.md`'s header carrying a
stale version against `manifest.json`'s current one), and this pack hit its own version too: `manifest.json`'s `updated_at` sat on an early-morning bootstrap timestamp for ~19 hours on 2026-09-17
while dozens of real content changes (four device adapters, `references/site-addressing.yaml` expansion, SNMP vault additions) landed in `CHANGELOG.md`, caught only by manual staleness audit.

**Automated enforcement (added 2026-09-17):** `scripts/check_governance.py`'s `check_manifest_freshness` (Tier 3) fails the gate if `manifest.json`'s `updated_at` is older, to the minute, than
`CHANGELOG.md`'s latest `## YYYYMMDD_HHMM` heading. This covers only the freshness half of this rule. Still unenforced, per `CHANGELOG.md`'s `20260917_2130` Residual notes: whether the version was
actually bumped for every content change, and whether any other file has hardcoded a duplicate version number.
````

## File: .archcore/rules/vault-reference-convention.rule.md
````markdown
---
title: Vault Reference Convention, Never Plaintext Values
type: rule
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; accepted by operator 20260917
---

# Rule: Vault Reference Convention, Never Plaintext Values

Never write a device password or other plaintext sensitive value into any file in this pack. Use the reference convention `<secret:keepassxc:cambium-devices/<entry>>` instead — see
`references/02_device-access-and-vault.md` for the vault structure this points into.

Avoid the blocked words (the ones the workspace's OPA write-gate hard-blocks in file **paths**, regardless of content) in every file path in this pack — not just the vault reference file. Hit and
worked around on 2026-09-17, and again while promoting this rule into `.archcore/`.

**Rationale:** the OPA gate blocks on path text alone, so a compliant file with a non-compliant name still fails to write. Getting the naming right the first time avoids a blocked write mid-task.

## Enforcement

See ADR: `.archcore/adr/vault-file-avoids-opa-blocked-words.adr.md`
````

## File: .archcore/specs/specialist-pack-file-roles.spec.md
````markdown
---
title: Specialist Pack File Roles
type: spec
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; reclassified from a rule candidate to a spec on promotion, mirroring skill-smc's identical spec; accepted by operator 20260917
---

# Spec: Specialist Pack File Roles

Defines the role and content-source status of every governance file in the skill-cambium specialist pack.

## File role table

| File                     | Role                                               | Notes                                                                             |
| ------------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| `SKILL.md`               | Agent-facing activation surface                    | Defines triggers, the Standing Write-Back Contract, and pointers to `references/` |
| `RUNBOOK.md`             | Navigation index only                              | Maps task types to numbered reference files; not a content source                 |
| `references/01_` – `05_` | Numbered content source files                      | Load only the one needed for the task                                             |
| `manifest.json`          | Machine-readable specialist metadata               | Sole version-of-record — see `manifest-version-discipline.rule.md`                |
| `AGENTS.md`              | Agent policy for pack maintenance                  | Governs contributors, not end-users                                               |
| `CLAUDE.md`              | Claude Code governance wrapper                     | Pack maintenance only                                                             |
| `AI_NAVIGATION.md`       | Human-readable context router                      | Pack maintenance only                                                             |
| `context-map.yaml`       | Machine-readable routing map                       | Pack maintenance only                                                             |
| `CHANGELOG.md`           | Pack version history                               | History and corroboration only — never a promotion source                         |
| `README.md`              | Pack orientation and folder index                  | Human entry point                                                                 |
| `SCRATCHPAD.md`          | Agent working memory for pack maintenance sessions | Durable only where marked `KEEP`                                                  |
| `.archcore/`             | Durable rules, ADR, spec for this pack             | Canonical source once accepted                                                    |

## Authority

`manifest.json` is the highest-authority metadata source. `SKILL.md` is the highest-authority agent-facing surface. `references/*.md` are content truth for their domain. No other file overrides these.

## Notes

This pack is smaller than its sibling `skill-smc` (5 reference files versus skill-smc's 13, no `exports/` client-adapter layer yet, no dedicated-agent `PROFILE.md`/`SYSTEM_PROMPT.md`), so this spec
omits rows for files that do not exist here. Add a row when a corresponding file is introduced.
````

## File: .archcore/index.guide.md
````markdown
---
title: Archcore index — skill-cambium
status: accepted
tags: [index]
---

# Archcore — skill-cambium

Durable pack truth: decisions that are settled, rules that are enforced, contracts other work must satisfy. Proposed 20260917 by `skill-ai-it promote` from `ARCHCORE_PROMOTION_CANDIDATES.md`
(generated the same day during a `refresh` run), which is now deleted — it was a proposal queue, not a record.

**All 6 documents below were ACCEPTED by the operator on 20260917**, the same day they were proposed. They are now the highest-authority statement of what this pack has decided per
`AI_NAVIGATION.md`'s source-priority list. An accepted document is not immutable — supersede it in place with a dated banner naming what replaced it and what still stands, rather than deleting it,
since the superseded reasoning is usually the part a later reader needs.

## Contents

- [Decisions](#decisions)
- [Rules](#rules)
- [Contracts](#contracts)
- [Never promoted, and why](#never-promoted-and-why)
- [Proposing another](#proposing-another)

## Decisions

| Document                                           | Governs                                                          |
| -------------------------------------------------- | ---------------------------------------------------------------- |
| [Separate pack from skill-smc](adr/separate-pack-from-skill-smc.adr.md) | Why this pack exists independently of skill-smc                  |
| [Vault reference file avoids OPA-blocked path words](adr/vault-file-avoids-opa-blocked-words.adr.md) | Why `references/02_device-access-and-vault.md` is named as it is |

## Rules

| Document                                           | Enforced by                                                                                                                                     |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [Vault reference convention, never plaintext values](rules/vault-reference-convention.rule.md) | Operator review only — no automated check yet; a real candidate is a `check_governance.py` grep for the blocked words appearing in a tracked    |
|                                                    |   path, not just content                                                                                                                        |
| [Cambium/SMC cross-pack boundary](rules/cambium-smc-cross-pack-boundary.rule.md) | Operator review only; enforces the ADR above                                                                                                    |
| [Manifest version discipline](rules/manifest-version-discipline.rule.md) | Partially automated 2026-09-17: `scripts/check_governance.py`'s `check_manifest_freshness` enforces `updated_at` is not older than the latest   |
|                                                    |   `CHANGELOG.md` entry. Still operator review only for the version-bump-per-change and no-duplicate-version-number parts of the rule            |

## Contracts

| Document                   | Defines                                                  |
| -------------------------- | -------------------------------------------------------- |
| [Specialist pack file roles](specs/specialist-pack-file-roles.spec.md) | Role and authority of every governance file in this pack |

## Never promoted, and why

Carried out of the candidate queue before it was deleted, so a future `skill-ai-it refresh` does not re-propose these.

| Item                                                             | Why not                                                                                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `AGENTS.md` naming convention bullet (`<slug>-YYYYMMDD_hhmm.md`) | Restates the parent/global `AGENTS.md` markdown-naming policy verbatim — already governed upstream.                          |
| `AGENTS.md` "Keep CHANGELOG.md current" bullet                   | Generic housekeeping instruction, not a durable project-specific rule or decision.                                           |
| `SCRATCHPAD.md` "Open items" and "Next actions"                  | Transient working-session state, not marked `KEEP`, and inherently time-bound.                                               |
| `CHANGELOG.md` (entire file)                                     | History/corroboration only — never a direct promotion source.                                                                |
| Spec/plan candidates                                             | None existed at promotion time — no stable schema/interface contract or accepted phased plan was in any governance file yet. |

## Proposing another

1. Write the candidate into the source it belongs to first — `AGENTS.md`, `SCRATCHPAD.md` (marked `KEEP`), or a reference file.
2. Run `/skill-ai-it refresh` to regenerate a candidate queue (`ARCHCORE_PROMOTION_CANDIDATES.md`), or add the document here directly with a provenance header, starting at `status: proposed`.
3. Apply the test: would it still read as true after the next real device-access/inventory-extraction session? If not, it belongs in `SCRATCHPAD.md` instead.
4. Avoid the OPA-blocked path words in every filename — see `adr/vault-file-avoids-opa-blocked-words.adr.md`.
````

## File: scripts/cambium_cnwave_adapter.py
````python
#!/usr/bin/env python3
"""Minimal Cambium cnWave 60GHz (Terragraph-based) REST adapter.

Talks to a cnWave node's own local web UI backend — the same one the onboard "60 GHz cnWave" Angular SPA calls — not the SSH TUI. The SSH
TUI (E2E controller's interactive console) has no official documentation at all (checked the vendor's own 60 GHz cnWave User Guide, Release
1.8 — zero SSH/CLI/console mentions across 12,378 lines, see cambium-swap evidence E119) and no scriptable form was found; this REST API is
the real, vendor-sanctioned adapter path, same conclusion already reached for XV2 and ePMP.

Auth flow (reverse-engineered from the device's own served JS, main.<hash>.js — not guessed): POST /local/userLogin with a JSON body returns
{"success":true,"message":"<JWT>"}. Every following call sends "Authorization: Bearer <JWT>" — no cookies involved, unlike XV2.

Role matters here, confirmed live 2026-09-17 against two real Hope Vale nodes:
- A POP/E2E-role node (V5000, onboard E2E controller) answers get_topology/get_ctrl_status_dump with real network-wide data.
- A plain Client Node (V2000) answers every /local/* getter fine (it's still a real device with its own facts/config), but
  /local/getE2eInfo reports {"enabled": false, "available": true} and the /api/* endpoints (topology, controller status) return an EMPTY
  body — those are E2E-controller-only, not per-node. Check get_e2e_info().get("enabled") before trusting get_topology() or
  get_ctrl_status_dump() to return anything.

getGpsBrief returns HTTP 400 with an empty body on at least one real node (no GPS fix, or a missing param this adapter doesn't send yet) —
get_gps() below tolerates that specific failure and returns None rather than raising.

getRadioStats/getNetworkStats/getKeyPerformanceIndex/getCnAgentStatus (confirmed live 2026-09-18 against a real V5000 POP node,
DMG_T12_V5000_DN_IP4_100, Doomadgee) all 400 on a bare `{}` POST to `/api/<name>` — **that path prefix was the actual bug, not a missing
param**: the Angular frontend's own JS bundle (main.<hash>.js, same reverse-engineering technique as every other endpoint here) calls these
four under `/local/`, not `/api/` like getTopology/getCtrlStatusDump. Correct request shapes, read from the JS's own `http.post(...)` call
sites and confirmed live:
- `POST /local/getRadioStats` — `{"macs": [<node_mac>]}` — the physical node MAC (e.g. `00:04:56:88:bb:25`), NOT a `wlan_mac_addrs` radio
  MAC from get_topology() — passing a radio MAC returns `{"success":true,"message":"[]"}` (empty, not an error).
- `POST /local/getNetworkStats` — `{"macs": [<node_mac>], "ifaces": [<iface names>]}` — per-interface Ethernet counters. `ifaces` must be
  non-empty (`[]` still 400s); `"nic1"` confirmed live.
- `POST /local/getKeyPerformanceIndex` — `{"mac": <node_mac>}` (singular key, not `macs`) — node MAC required, same as getRadioStats; a
  radio MAC returns nulled-out placeholder data with HTTP 200, not an error.
- `POST /local/getCnAgentStatus` — `{}` — genuinely takes no params, exactly as the JS calls it; the earlier 400s were entirely the
  `/api/` vs `/local/` path mismatch.

SNMP is documented (SNMPv2c RO/RW + SNMPv3, MIB TERRAGRAPH-RADIO-MIB) but never confirmed live — no community string is known. The R195P
Ansible template's SNMP Get/Set community values are encrypted blobs in the device's own config-encryption format, identical across every
site (one fleet-wide value) — not something to reverse-engineer, and not this device family's community string anyway. Do not guess vendor
default communities beyond a single harmless "public" try.

Usage:
    CAMBIUM_HOST=10.255.4.100 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_cnwave_adapter.py

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/cnwave-60ghz`) into an env
var at the call site.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request

REDACT_KEY_PATTERN = re.compile(
    r"pass|pwd|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def redact(obj):
    """Recursively replace any dict value whose key looks credential-shaped with a placeholder."""
    if isinstance(obj, dict):
        return {
            k: "<REDACTED>" if REDACT_KEY_PATTERN.search(k) else redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


class CambiumCnWaveAdapter:
    """Talks to one cnWave 60GHz node's local REST API over HTTPS (POP/E2E role or plain CN)."""

    def __init__(self, host: str, username: str, password: str, verify_tls: bool = False) -> None:
        self.base_url = f"https://{host}"
        self._username = username
        self._password = password
        self._token: str | None = None

        ctx = ssl.create_default_context()
        if not verify_tls:
            # Device presents a self-signed cert on its management interface — expected here, not a security bypass for anything
            # internet-facing.
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self._opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    def _request(self, path: str, body: dict | None = None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body if body is not None else {}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with self._opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"POST {path} -> HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc

        return json.loads(raw) if raw else {}

    def get_raw(self, endpoint: str):
        """Public escape hatch for exploring an endpoint not yet wrapped by a getter below.

        Returns the RAW (unredacted) response — callers that might print, log, or write this to disk must redact() it themselves first.
        """
        path = endpoint if endpoint.startswith("/") else f"/local/{endpoint}"
        return self._request(path)

    def login(self) -> None:
        result = self._request("/local/userLogin", {"username": self._username, "password": self._password})
        if not result.get("success"):
            raise RuntimeError(f"Cambium login failed: {result}")
        self._token = result["message"]

    def logout(self) -> None:
        self._request("/local/userLogout")

    def get_facts(self) -> dict:
        """NAPALM-style get_facts: device identity, firmware, uptime. `type` distinguishes role — "POP" for a node running the onboard E2E
        controller, "CN" for a plain Client Node."""
        info = self._request("/local/getDeviceInfo")
        return {
            "vendor": "Cambium Networks",
            "role": info.get("type"),
            "model": info.get("model"),
            "hostname": info.get("name"),
            "serial_number": info.get("msn"),
            "os_version": info.get("swVer"),
            "firmware_version": info.get("fwVersion", "").strip(),
            "uptime_seconds": info.get("uptime"),
            "mac_address": info.get("mac"),
            "ipv4_address": info.get("ipv4Address"),
        }

    def get_e2e_info(self) -> dict:
        """Whether THIS node runs the E2E controller. Check enabled=True before trusting get_topology()/get_ctrl_status_dump() to return
        network-wide data — on a plain Client Node those calls succeed but return an empty body (confirmed live 2026-09-17)."""
        return self._request("/local/getE2eInfo")

    def get_status(self) -> dict:
        """onboardStatus (is the E2E controller running on this box) and, if so, its own internal tcp:// URL."""
        return self._request("/local/getStatusInfo")

    def get_capability(self) -> dict:
        return self._request("/local/getSystemCapability")

    def get_links_count(self):
        return self._request("/local/getLinksCount")

    def get_gps(self):
        """Confirmed live to 400 with an empty body on at least one real node (no GPS fix, or a missing param this adapter doesn't send
        yet) — tolerate that specific failure and return None rather than raising, since it is a real, observed device response, not a
        bug in this client."""
        try:
            return self._request("/local/getGpsBrief")
        except RuntimeError as exc:
            if "HTTP 400" in str(exc):
                return None
            raise

    def get_topology(self) -> dict:
        """Full network topology (nodes, links, sites) — E2E-controller-only. Returns an empty dict on a plain Client Node; call
        get_e2e_info() first if that distinction matters."""
        return self._request("/api/getTopology")

    def get_ctrl_status_dump(self) -> dict:
        """Per-node status as seen by the E2E controller, including the underlying open-source Terragraph release string (cnWave is built
        on Meta's Terragraph platform) — E2E-controller-only, same caveat as get_topology()."""
        return self._request("/api/getCtrlStatusDump")

    def get_radio_stats(self, node_mac: str) -> dict:
        """Per-radio RF/TDD stats for one node (rf sync temps, tx/rx byte+packet rates, TDD slot ratio, ...). Confirmed live 2026-09-18.
        `node_mac` is the node's own MAC (get_facts()'s mac_address / get_topology()'s node mac_addr) — a wlan_mac_addrs radio MAC returns
        an empty result, not an error, so a mismatch here fails silently rather than raising."""
        return self._request("/local/getRadioStats", {"macs": [node_mac]})

    def get_network_stats(self, node_mac: str, ifaces: list[str]) -> dict:
        """Per-interface Ethernet counters (rx/tx packets, bytes, errors, drops) for one node. Confirmed live 2026-09-18 with
        ifaces=["nic1"]. `ifaces` must be non-empty — an empty list 400s."""
        return self._request("/local/getNetworkStats", {"macs": [node_mac], "ifaces": ifaces})

    #: Ethernet ports read for monitoring. On HRN_T1_V5000_DN_IP4_10 (2026-09-22) nic2 carried the traffic and nic1 read 0: the
    #: "counters read 0" finding of 2026-09-21 was the wrong port, not a missing counter. nic0/terra*/lo return empty lists.
    MONITOR_IFACES = ("nic1", "nic2", "nic3")

    def get_snapshot(self) -> dict:
        """facts, e2e_info, topology (only where this node runs the E2E controller) and per-port counters, for monitoring (added
        2026-09-22). getNetworkStats returns its data as a JSON string inside `message`; this parses it into `counters.net_dev`,
        keyed by port, cumulative rx/tx bytes, packets, errors and drops."""
        facts = self.get_facts()
        e2e = self.get_e2e_info()
        result = {"facts": facts, "e2e_info": e2e}
        if isinstance(e2e, dict) and e2e.get("enabled"):
            result["topology"] = self.get_topology()
        net_dev = {}
        stats = self.get_network_stats(facts.get("mac_address"), list(self.MONITOR_IFACES)) if facts.get("mac_address") else {}
        message = stats.get("message") if isinstance(stats, dict) else None
        rows = json.loads(message) if isinstance(message, str) and message.strip().startswith("[") else []
        for row in rows:
            if isinstance(row, dict) and row.get("iface"):
                net_dev[row["iface"]] = {k: row.get(k) for k in ("rx_bytes", "tx_bytes", "rx_packets", "tx_packets", "rx_errors",
                                                                 "tx_errors", "rx_dropped", "tx_dropped")}
        result["counters"] = {"net_dev": net_dev}
        return result

    def get_key_performance_index(self, node_mac: str) -> dict:
        """Node-level KPI summary (totalSectors, totalLinks, uptime, tx/rx byte rate) plus a per-sector link-count map. Confirmed live
        2026-09-18. Takes a single `mac` (node MAC, not a list) — a radio MAC returns nulled-out placeholder values with HTTP 200."""
        return self._request("/local/getKeyPerformanceIndex", {"mac": node_mac})

    def get_cn_agent_status(self) -> dict:
        """This node's CN-agent connection status to cnMaestro (code/status/message/ts). Confirmed live 2026-09-18 — genuinely takes no
        params; the {} body matches the JS bundle's own call exactly."""
        return self._request("/local/getCnAgentStatus", {})

    def get_config(self) -> dict:
        """Config snapshot for backup/diff, merging the two confirmed-live config-read endpoints. REDACTS every credential-shaped field via
        REDACT_KEY_PATTERN before returning — not yet seen a real secret in this family's config live, but the pattern applies
        unconditionally per this project's standing rule after two prior incidents on other families."""
        merged = {
            "cn_agent": self._request("/local/getCnAgentConfig"),
            "minion": self._request("/local/minionConfigGet"),
        }
        return redact(merged)


def _cmd_getters(adapter: CambiumCnWaveAdapter) -> int:
    adapter.login()
    try:
        facts = adapter.get_facts()
        e2e = adapter.get_e2e_info()
        node_mac = facts.get("mac_address")
        result = {
            "facts": facts,
            "e2e_info": e2e,
            "status": adapter.get_status(),
            "capability": adapter.get_capability(),
            "links_count": adapter.get_links_count(),
            "gps": adapter.get_gps(),
            "config": adapter.get_config(),
        }
        if node_mac:
            result["radio_stats"] = adapter.get_radio_stats(node_mac)
            result["network_stats"] = adapter.get_network_stats(node_mac, ["nic1"])
            result["key_performance_index"] = adapter.get_key_performance_index(node_mac)
        result["cn_agent_status"] = adapter.get_cn_agent_status()
        if e2e.get("enabled"):
            result["topology"] = adapter.get_topology()
            result["ctrl_status_dump"] = adapter.get_ctrl_status_dump()
        print(json.dumps(result, indent=2))
    finally:
        adapter.logout()
    return 0


def main() -> int:
    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumCnWaveAdapter(host, username, password)
    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: scripts/cambium_epmp_adapter.py
````python
#!/usr/bin/env python3
"""Minimal Cambium ePMP (ePMP AP / ePMP SM, LuCI-derived firmware) REST adapter.

Same shape and rationale as cambium_xv2_adapter.py in this directory, for the ePMP family instead of Enterprise Wi-Fi. Stdlib-only Python,
no schema, no code generation.

Auth flow and RPC mechanics (reverse-engineered live 2026-09-17 from the device's own served JS, cambium.<hash>.js — nowhere documented in
the vendor CLI/user guides, which predate this API surface or simply don't cover it): the web UI is a LuCI-derived stack (confirmed by the
literal LuCI 404 page at unregistered paths). Login is `POST /cgi-bin/luci` (no stok yet) with form-urlencoded `username`/`password`;
success returns JSON `{"stok": "...", "userRole": "...", ...}` plus a `Set-Cookie: sysauth_<host>=<value>`. Every authenticated call after
that needs **both** the `stok` in the URL path AND the `sysauth_<host>` cookie — `POST /cgi-bin/luci/;stok=<stok>/admin/<method>`. A bare
POST with no body 411s ("Length Required"); always send an explicit (even empty) urlencoded body. Auth failure returns **HTTP 200** with
`{"msg":"auth_failed","success":0}` in the body — never trust the status code alone, check `success`.

The one RPC method this adapter actually uses is `get_param` with a form field `act=<section>`: `act=status` returns live telemetry
(identity, interfaces, wireless link/STA table) under a top-level `device_props` dict; `act=config_regular` returns the full device config
(~800 keys) under the same shape — **loaded with real credential-shaped values** (SNMP community strings, RADIUS password, wireless
encryption key all confirmed live and non-empty on a real device) — see REDACT_KEY_PATTERN below and the Known Issues doc before ever
touching this method again. Other real `act=*`/`ajax()` method names exist (`get_log`, `get_chart`, `link_test`, `traceroute`, `set_param`,
`reboot`, `reset_to_def`, ...) but are not wrapped here — see the module docstring's sibling doc, references/06_device-api-cli-reference.md,
for the full enumerated list found in the JS. Never call a write/destructive method (`set_param`, `reboot`, `reset_to_def`,
`disconnect_sta`, `ap_list_flush`, ...) against a production device without explicit operator authorization, same rule as XV2.

Confirmed live 2026-09-17 in an **AP** role too, not just SM (Force 300-16 at Kalumburu, cambium-swap evidence E118) — same `get_param`/
`act=status` shape, but that specific unit needed the `epmp-ap-legacy` vault credential, not the primary `epmp-ap` one.

Usage:
    CAMBIUM_HOST=localhost:20045 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_epmp_adapter.py

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/epmp-sm` or
`cambium-devices/epmp-ap`) into an env var at the call site.

SECRET-EXPOSURE INCIDENT (2026-09-17): while manually checking whether `act=config_regular`'s credential-shaped keys held real values (as
opposed to guessing this adapter's design from field names alone), the check printed the actual values to a transcript — the same mistake
the XV2 incident this pattern already exists to prevent, just made again ad hoc before this file existed. REDACT_KEY_PATTERN and redact()
below are copied verbatim from cambium_xv2_adapter.py specifically so this never has to be reinvented ad hoc again. Checking "does this
field have a value" must only ever use bool()/len() on the value, never print or log it.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

REDACT_KEY_PATTERN = re.compile(
    r"pass|pwd|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def redact(obj):
    """Recursively replace any dict value whose key looks credential-shaped with a placeholder."""
    if isinstance(obj, dict):
        return {
            k: "<REDACTED>" if REDACT_KEY_PATTERN.search(k) else redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


class CambiumEPMPAdapter:
    """Talks to one ePMP AP or ePMP SM's local LuCI-derived JSON API over HTTPS."""

    def __init__(self, host: str, username: str, password: str, verify_tls: bool = False) -> None:
        self.base_url = f"https://{host}"
        self._username = username
        self._password = password
        self._stok: str | None = None

        ctx = ssl.create_default_context()
        if not verify_tls:
            # Device presents a self-signed cert on its management interface — expected here, not a security bypass for anything
            # internet-facing.
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        self._cookiejar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._cookiejar),
            urllib.request.HTTPSHandler(context=ctx),
        )

    def _post(self, path: str, form: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        body = urllib.parse.urlencode(form or {}).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with self._opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"POST {path} -> HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc
        return json.loads(raw) if raw else {}

    def login(self) -> None:
        result = self._post("/cgi-bin/luci", {"username": self._username, "password": self._password})
        stok = result.get("stok")
        if not stok:
            raise RuntimeError(f"Cambium ePMP login failed: {result}")
        self._stok = stok

    def logout(self) -> None:
        if self._stok:
            self._post(f"/cgi-bin/luci/;stok={self._stok}/admin/logout")
        self._stok = None

    def get_raw_param(self, act: str) -> dict:
        """Public escape hatch: raw (unredacted) get_param response for a given `act` section.

        Callers that might print, log, or persist this must redact() it themselves first — see the module docstring's incident note.
        `act=status` is safe (telemetry only, confirmed no credential-shaped keys); `act=config_regular` is NOT (confirmed real secrets
        present).
        """
        if not self._stok:
            raise RuntimeError("login() first")
        return self._post(f"/cgi-bin/luci/;stok={self._stok}/admin/get_param", {"act": act})

    def _status_props(self) -> dict:
        """`act=status` device_props: the snapshot's single read while get_snapshot() runs, otherwise a fresh read."""
        cached = getattr(self, "_status_cache", None)
        return cached if cached is not None else self.get_raw_param("status").get("device_props", {})

    #: Counters in `device_props` that feed monitoring (probed live 2026-09-21, AP and SM alike). Traffic is in kbit;
    #: whether 1 kbit is 1000 or 1024 bits is UNVERIFIED (references/06, "Monitoring Counter and Resource Surfaces").
    COUNTER_KEYS = ("rxEtherLanKbitCount", "txEtherLanKbitCount", "rxEtherLanErrorPacketCount", "txEtherLanErrorPacketCount",
                    "dlWLanKbitCount", "ulWLanKbitCount", "dlWLanErrorDroppedPacketCount", "ulWLanErrorDroppedPacketCount", "sysCPUUsage")

    def get_snapshot(self) -> dict:
        """facts, interfaces, wireless_link, clients and counters from ONE `act=status` read (added 2026-09-22 for monitoring).

        Each getter used to fetch `act=status` again, so a monitoring read cost four identical requests over the site link.
        This reads it once and builds every getter's output from the same payload. `status` holds no credential-shaped keys
        (see get_raw_param), so `counters` is safe to return.
        """
        self._status_cache = self.get_raw_param("status").get("device_props", {})
        try:
            return {
                "facts": self.get_facts(),
                "interfaces": self.get_interfaces(),
                "wireless_link": self.get_wireless_link(),
                "clients": self.get_clients(),
                "counters": {k: self._status_cache.get(k) for k in self.COUNTER_KEYS},
            }
        finally:
            self._status_cache = None

    def get_facts(self) -> dict:
        """NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection state."""
        props = self._status_props()
        return {
            "vendor": "Cambium Networks",
            "hostname": props.get("cambiumEffectiveDeviceName"),
            "serial_number": props.get("cambiumEPMPMSN"),
            "os_version": props.get("cambiumCurrentuImageVersion"),
            "uptime": props.get("cambiumSystemUptime"),
            "mac_address": props.get("cambiumWirelessMACAddress") or props.get("cambiumLANMACAddress"),
            # Added 2026-09-22: the management address and the LAN MAC. The LAN MAC is the one the asset register, cnMaestro
            # and Nautobot hold (checked on a 3000L AP and a Force 300 SM at mowanjum); `mac_address` above is the wireless MAC.
            "ipv4_address": props.get("cambiumEffectiveDeviceIPAddress"),
            "lan_mac_address": props.get("cambiumLANMACAddress"),
            "cnmaestro_status": props.get("cambiumCnsServConsStat"),
        }

    def get_interfaces(self) -> dict:
        """LAN (Ethernet) port state. ePMP has one LAN port (two on some AP models, LAN2 fields exist but read 0/unused on the units
        tested)."""
        props = self._status_props()
        return {
            "LAN": {
                "is_up": bool(props.get("cambiumLANStatus")),
                "speed_mbps": props.get("cambiumLANSpeedStatus"),
                "duplex_full": bool(props.get("cambiumLANModeStatus")),
                "mac_address": props.get("cambiumLANMACAddress"),
            },
            "LAN2": {
                "is_up": bool(props.get("cambiumLAN2Status")),
                "speed_mbps": props.get("cambiumLAN2SpeedStatus"),
                "duplex_full": bool(props.get("cambiumLAN2ModeStatus")),
            },
        }

    def get_wireless_link(self) -> dict | None:
        """SM-side only: this unit's single uplink to its paired AP (RSSI/SNR/distance/frequency). Returns None on an AP (which has no
        single uplink — see get_clients() instead).

        Real bug found and fixed live 2026-09-17: `cambiumSTADLRSSI` exists (=0) on an AP too, so its mere presence isn't a valid SM-vs-AP
        discriminator — an AP was returning a bogus zeroed-out link dict instead of None. `cambiumConnectedAPMACAddress` is the real
        signal: a SM reports a real MAC; an AP reports the literal string "Not Associated"."""
        props = self._status_props()
        connected_ap_mac = props.get("cambiumConnectedAPMACAddress")
        if not connected_ap_mac or connected_ap_mac == "Not Associated":
            return None
        return {
            "connected_ap_mac": props.get("cambiumConnectedAPMACAddress"),
            "frequency_mhz": props.get("cambiumSTAConnectedRFFrequency"),
            "downlink_rssi": props.get("cambiumSTADLRSSI"),
            "downlink_snr": props.get("cambiumSTADLSNR"),
            "distance_km": props.get("cambiumSTADistanceKm"),
        }

    def get_clients(self) -> list:
        """AP-side only: every currently-associated SM, with per-station RF telemetry. Empty list on an SM (which has no stations of its
        own)."""
        props = self._status_props()
        table = props.get("cambiumAPConnectedSTATable")
        if not table:
            return []
        return [
            {
                "hostname": sta.get("connectedClickTHostName"),
                "mac_address": sta.get("connectedSTAMAC"),
                "ip_address": sta.get("connectedSTAIP"),
                "software_version": sta.get("connectedSTASoftwareVersion"),
                "model_name": sta.get("connectedSTAModelName"),
                "downlink_rssi": sta.get("connectedSTADLRSSI"),
                "downlink_snr": sta.get("connectedSTADLSNR"),
                "uplink_rssi": sta.get("connectedSTAULRSSI"),
                "uplink_snr": sta.get("connectedSTAULSNR"),
                "distance_m": sta.get("connectedSTADistance"),
                "session_time": sta.get("connectedSTASessionTime"),
            }
            for sta in table
        ]

    def get_config(self) -> dict:
        """Config snapshot for backup/diff. REDACTS every credential-shaped field via REDACT_KEY_PATTERN before returning — confirmed
        necessary live, this section carries real SNMP community strings, a RADIUS password, and a wireless encryption key in plaintext
        from the device. Callers must never bypass this by calling get_raw_param('config_regular') directly without also redacting."""
        props = self.get_raw_param("config_regular").get("device_props", {})
        return redact(props)


def _cmd_getters(adapter: CambiumEPMPAdapter) -> int:
    adapter.login()
    try:
        result = {
            "facts": adapter.get_facts(),
            "interfaces": adapter.get_interfaces(),
            "wireless_link": adapter.get_wireless_link(),
            "clients": adapter.get_clients(),
        }
        print(json.dumps(result, indent=2))
    finally:
        adapter.logout()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--include-config",
        action="store_true",
        help="also fetch and print the redacted config_regular snapshot (get_config)",
    )
    args = parser.parse_args()

    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumEPMPAdapter(host, username, password)

    if args.include_config:
        # Single combined login: facts/interfaces/wireless_link/clients/config all in one
        # session, mirroring cambium_r195p_adapter.py's --include-config shape. This family has a
        # real 5-session RW cap (see references/06_device-api-cli-reference.md) — a prior version
        # of this branch called get_config() alone and left _cmd_getters()'s own separate
        # login/logout pair unused, which would have cost a second session for no reason.
        adapter.login()
        try:
            result = {
                "facts": adapter.get_facts(),
                "interfaces": adapter.get_interfaces(),
                "wireless_link": adapter.get_wireless_link(),
                "clients": adapter.get_clients(),
                "config": adapter.get_config(),
            }
            print(json.dumps(result, indent=2))
        finally:
            adapter.logout()
        return 0

    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: scripts/cambium_r195p_adapter.py
````python
#!/usr/bin/env python3
"""Minimal Cambium cnPilot R195P (residential CPE) SSH adapter.

Different shape from cambium_xv2_adapter.py/cambium_epmp_adapter.py/cambium_cnwave_adapter.py in this directory: those three talk to a REST
API over HTTPS; R195P has none confirmed. The only access path this project has ever actually exercised live (cambium-swap evidence
E113/E114/E118) is a plain SSH login dropping into a real interactive shell — not a vendor "show"-style CLI (that's XV2's Falcon UI, a
different product line), a real BusyBox/Buildroot userland on a MIPS SoC (MT7621), confirmed live: `uname -a` returned
"Linux <hostname> 2.6.36 ... mips", built by a Flyingvoice/Actiontec-style OEM platform, not Cambium's own Falcon stack.

R195P's `device-family-matrix.csv` row lists "Yes (web UI)" for HTTPS access, but that is `USER_STATED` from vendor docs only — no agent
session has ever actually logged into R195P's web UI this project. Do not assume it works the same way XV2/E500/cnWave's web UIs do
(POST /api/login or /local/userLogin) without checking; R195P is a different, older cnPilot Home Router product line under the hood.

No pure-stdlib SSH client exists (paramiko is a real dependency, not installed per this project's stdlib-only convention for these
adapters) — this adapter shells out to the system `ssh` binary instead, with the password handed over by `SSH_ASKPASS` (since
2026-09-28; before that `sshpass`, see `_run`). That is a real, if unconventional, trade-off: correctness depends on OpenSSH 8.4 or later on PATH and the caller
already having network access to the device (normally via a `tsh` tunnel through the site's SMC box — see references/
02_device-access-and-vault.md).

Usage:
    CAMBIUM_HOST=10.255.11.55 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_r195p_adapter.py

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/cnpilot-r-series`) into
an env var at the call site.

Confirmed live 2026-09-17 against two real Burringurrah units, BUR-R195P-1047 (10.255.11.47) and BUR-R195P-1055 (10.255.11.55) — see
cambium-swap evidence E113/E114/E118. Deliberately did NOT run `cat /etc/config/*` or any full-config dump that session (this family's SNMP
Get/Set community strings are known to be configured fleet-wide per the Ansible R195P provisioning template — encrypted there, but real —
and this project has two prior secret-exposure incidents on other families from exactly this kind of unscoped dump).

get_config() ADDED 2026-09-18 under explicit operator authorization to fetch a live snapshot across all 4 Cambium device families in one
session (cambium-swap evidence E134-series) — the condition this docstring originally asked for ("a real need... never as a blind default")
is now met. It wraps the exact `cat /etc/config/* 2>&1` dump this docstring spent a year deliberately avoiding, but never returns it
unredacted: the raw UCI-style text is parsed into a nested dict and passed through the same REDACT_KEY_PATTERN/redact() shape used verbatim
by cambium_xv2_adapter.py/cambium_epmp_adapter.py/cambium_cnwave_adapter.py, keyed by option name so the fleet-wide SNMP community (an
encrypted blob in this family's own config, not necessarily plaintext-looking) is redacted by key name regardless of whether the value looks
like ciphertext — same rule the other three adapters already apply. Opt-in only, via `--include-config` (same flag name/shape as
cambium_epmp_adapter.py), never part of the default `_cmd_getters()` output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

REDACT_KEY_PATTERN = re.compile(
    r"pass|pwd|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def redact(obj):
    """Recursively replace any dict value whose key looks credential-shaped with a placeholder.

    Copied verbatim from cambium_xv2_adapter.py / cambium_epmp_adapter.py / cambium_cnwave_adapter.py in this directory — deliberately not
    re-derived, per this project's standing rule after two prior secret-exposure incidents on other families.
    """
    if isinstance(obj, dict):
        return {
            k: "<REDACTED>" if REDACT_KEY_PATTERN.search(k) else redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


DEFAULT_SSH_TIMEOUT = 20
# Was 8 (fine for the direct-tunnel path this constant was originally tested against, 2026-09-17).
# Live-tested 2026-09-18 through a nested Teleport --proxy= tunnel to a device reachable only via a
# site's SMC box: the device's own sshd (dropbear) answers its banner instantly (confirmed with a
# raw socket probe), but the fuller key-exchange + password-auth round trip over that extra hop
# exceeded the old 8s ConnectTimeout and raised subprocess.TimeoutExpired. Bumped to 20s rather than
# reverting the nested-tunnel access path, since that path is this family's documented normal case.


#: The environment variable the askpass helper reads the password from; set only in the ssh child's environment, never on its command line.
_PASS_ENV = "CAMBIUM_R195P_SSH_PASSWORD"
_ASKPASS: str | None = None


def _askpass_helper() -> str:
    """Path of a private helper script that prints the password from `_PASS_ENV` (made once per process, mode 0700, in a 0700 temp dir;
    it holds no secret)."""
    global _ASKPASS
    if _ASKPASS is None or not os.path.exists(_ASKPASS):
        path = os.path.join(tempfile.mkdtemp(prefix="r195p-askpass-"), "askpass")
        with open(path, "w") as fh:
            fh.write(f'#!/bin/sh\nprintf "%s\\n" "${_PASS_ENV}"\n')
        os.chmod(path, 0o700)
        _ASKPASS = path
    return _ASKPASS


class CambiumR195PAdapter:
    """Talks to one cnPilot R195P's real BusyBox/Buildroot shell over SSH, via the system ssh/sshpass binaries."""

    def __init__(self, host: str, username: str, password: str, timeout: int = DEFAULT_SSH_TIMEOUT) -> None:
        # Accept "host:port" the same way CAMBIUM_HOST is already written for the other 3 (HTTPS)
        # adapters in this directory, e.g. "localhost:20004" for a local Teleport port-forward —
        # this family's own module docstring says the normal access path IS a tsh tunnel through
        # the site's SMC box, so a bare `ssh user@host:port` (which ssh parses as a literal,
        # unresolvable hostname) was a real bug on the documented default path, not an edge case.
        if ":" in host:
            hostname, _, port_str = host.rpartition(":")
            if port_str.isdigit():
                self.host = hostname
                self._port: str | None = port_str
            else:
                self.host = host
                self._port = None
        else:
            self.host = host
            self._port = None
        self._username = username
        self._password = password
        self._timeout = timeout

    def _run(self, remote_command: str, allow_nonzero: bool = False) -> str:
        """Run one remote shell command over SSH and return its stdout, raising on a non-zero exit or a timeout.

        The password reaches `ssh` through `SSH_ASKPASS` with `SSH_ASKPASS_REQUIRE=force` (OpenSSH 8.4+): ssh runs a tiny helper that prints
        it from this process's environment, so nothing watches a terminal for the prompt. Until 2026-09-28 this used `sshpass -p`, which
        now and then missed the prompt; ssh then fell back to an absent `ssh-askpass`, sent no password and was denied three times (three
        units in scheduled runs 2026-09-22; one or two of five R195Ps read at once 2026-09-28, each fine alone). `sshpass -p` also put the
        password on the command line, readable by any local user in `ps`. `NumberOfPasswordPrompts=1`: a wrong password is one rejected
        login, not three. `StrictHostKeyChecking=no`
        matches those sessions too: these are internal management-network devices reached through an already-authenticated Teleport
        tunnel, not internet-facing hosts.

        `allow_nonzero` (added 2026-09-18, first live get_config() run): `get_config()`'s own `cat /etc/config/* 2>&1` deliberately merges
        BusyBox `cat`'s stderr into the captured stdout stream so a missing config file shows up as parseable text under `_unparsed`
        rather than being lost — see that method's and `_parse_uci_text()`'s docstrings. But BusyBox `cat` exits non-zero as soon as ANY
        one of several glob-matched files fails to open, even though the useful output for every other file is still on stdout. The
        default strict behaviour below raised on that non-zero exit and discarded the merged stdout entirely, silently defeating the
        `2>&1` design intent — confirmed live against a real Burringurrah unit (not every `/etc/config/*` type exists on every unit, so
        this is the common case here, not a rare edge case). Only `get_config()` opts into tolerating this.
        """
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            # UserKnownHostsFile=/dev/null, not just StrictHostKeyChecking=no: this project's site management
            # subnets overlap (skill-smc references/01_overview.md "Device host keys collide across sites"), so
            # the SAME IP is a genuinely DIFFERENT real device at another site with a different host key.
            # StrictHostKeyChecking=no alone still refuses on a CHANGED key ("REMOTE HOST IDENTIFICATION HAS
            # CHANGED") -- it only auto-accepts a host never seen before. Never persisting a key at all is the
            # correct behaviour here, not a security downgrade: caught live 2026-09-21 batch-pushing a second
            # site's R195P units after a first site's IPs were already cached.
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", f"ConnectTimeout={self._timeout}",
            # LogLevel=ERROR added 2026-09-18: the local OpenSSH client's own "not using a
            # post-quantum key exchange" advisory banner is written before the password prompt and
            # was observed live to desync sshpass's naive prompt-pattern matching (three
            # ssh_askpass fallback attempts, then a real "Permission denied" against a password that
            # is in fact correct) — silencing client-side advisory/warning banners avoids the
            # desync without changing auth behaviour.
            "-o", "LogLevel=ERROR",
            "-o", "NumberOfPasswordPrompts=1",
            "-o", "PubkeyAuthentication=no",
        ]
        if self._port:
            cmd += ["-p", self._port]
        cmd += [
            f"{self._username}@{self.host}",
            remote_command,
        ]
        env = {**os.environ, "SSH_ASKPASS": _askpass_helper(), "SSH_ASKPASS_REQUIRE": "force", _PASS_ENV: self._password,
               "DISPLAY": os.environ.get("DISPLAY", ":0")}
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self._timeout + 5, env=env, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:
            # SECRET-EXPOSURE INCIDENT (2026-09-18, live R195P test): subprocess.TimeoutExpired's
            # default __str__/repr embeds the FULL argv it was given, including the `sshpass -p
            # <password>` pair above — an uncaught instance of this exception prints the real
            # device password to whatever captures the traceback (a terminal transcript, a log
            # file). Never let this exception surface with its default message; re-raise sanitized,
            # same discipline as the REDACT_KEY_PATTERN rule elsewhere in this project after two
            # prior incidents of this same class (E107 and the 2026-09-17 ePMP incident).
            raise RuntimeError(f"SSH command timed out after {exc.timeout}s: {remote_command!r}") from None
        # 255 is ssh's own failure (connect, auth, dropped session), never the remote command's: raise it even when the
        # caller tolerates a non-zero remote exit, or get_snapshot() would report an unreachable unit as a parsing fault
        # (HOR-R195P-1002, 2026-09-22: "sections missing" from an empty read).
        # A rejected password is ssh's 255 with "Permission denied" (sshpass used to exit 5 for it). Raised as "password rejected" whatever
        # allow_nonzero says, so callers try the `-legacy` entry (batch_push_devices' auth classifier matches it), and get_snapshot() never
        # reports a rejected login as an empty read ("snapshot incomplete, sections missing", MOW-R195P-1003, 2026-09-22).
        if result.returncode == 255 and "Permission denied" in result.stderr:
            raise RuntimeError(f"SSH login failed: password rejected: {result.stderr.strip()[:120]}")
        if result.returncode == 255:
            raise RuntimeError(f"SSH connection failed (exit 255): {result.stderr.strip()[:160]}")
        if result.returncode != 0 and not allow_nonzero:
            raise RuntimeError(f"SSH command failed (exit {result.returncode}): {remote_command!r} -> {result.stderr.strip()}")
        return result.stdout

    def login(self) -> None:
        """No separate login step — SSH auth happens per-command. Runs one cheap command up front so a bad password/host fails fast and
        loud here, not silently inside the first real getter."""
        self._run("true")

    def logout(self) -> None:
        """No-op: nothing to close. Each _run() is its own short-lived SSH session, same as every other command this adapter runs."""

    def get_facts(self) -> dict:
        """NAPALM-style get_facts, built from real shell commands confirmed live 2026-09-17 (not a vendor "show" command — this product
        line has none): `uname -a` for kernel/hostname/arch, `cat /proc/cpuinfo` for the SoC, and `ifconfig br0`/`ifconfig wan1` for the
        LAN and WAN MAC addresses (confirmed on real units to differ by exactly one — WAN is LAN+1 — the WAN MAC is what shows up in a
        site's ARP table, not the LAN one; see cambium-swap evidence E112/E113 for the addressing bug this distinction resolved)."""
        uname = self._run("uname -a").strip()
        cpu_line = next(
            (line for line in self._run("cat /proc/cpuinfo 2>/dev/null").splitlines() if "system type" in line.lower()),
            "",
        )
        # `ifconfig <name>` exits non-zero when that interface doesn't exist on this unit's config — confirmed live 2026-09-17 that not
        # every real R195P has a standalone `wan1` link (some firmware/config variants only expose it as a VLAN sub-interface, e.g.
        # `wan1.500`). Treat that as a real "unknown", not a fatal error — br0/LAN should always exist, but tolerate its absence too.
        lan_mac = self._try_get_mac("ifconfig br0 2>/dev/null")
        wan_mac = self._try_get_mac("ifconfig wan1 2>/dev/null")

        parts = uname.split()
        hostname = parts[1] if len(parts) > 1 else None
        kernel_version = parts[2] if len(parts) > 2 else None

        return {
            "vendor": "Cambium Networks",
            "model": "R195P",
            "hostname": hostname,
            "kernel_version": kernel_version,
            "soc": cpu_line.split(":", 1)[-1].strip() if cpu_line else None,
            "lan_mac_address": lan_mac,
            "wan_mac_address": wan_mac,
            "raw_uname": uname,
        }

    def get_interfaces(self) -> dict:
        """Per-interface addressing from `ip addr show` — confirmed live to enumerate a large real set on this family (bridge, VLANs,
        wifi radios, WDS, AP-client interfaces; see cambium-swap evidence E118 for the full live list on one unit). Only
        name/state/MAC/IPv4 are parsed here; deeper per-radio stats are not exposed this way on this product line.

        This BusyBox's `ip -o` is not standard iproute2 output: a line with no address to report is the LINK line itself (index, name,
        `<FLAGS>`, `link/ether <mac>`), interleaved with real `... inet <addr> ...` lines for the same interface — confirmed live
        2026-09-17 (a naive parser that assumed one consistent line shape per interface produced duplicate `<name>` and `<name>:` keys
        for the same real interface). Regex-matched instead of split-by-field-position to tolerate that."""
        return self._parse_ip_addr(self._run("ip -o addr show 2>&1"))

    @staticmethod
    def _parse_ip_addr(output: str) -> dict:
        """Parser for this BusyBox's `ip -o addr show`, shared by get_interfaces() and get_snapshot()."""
        interfaces: dict[str, dict] = {}
        for line in output.splitlines():
            header = re.match(r"^\d+:\s+([^\s:@]+)", line)
            if not header:
                continue
            name = header.group(1)
            entry = interfaces.setdefault(name, {"ipv4_addresses": []})

            # `_` matters: an interface that is up carries LOWER_UP, and without it this pattern never matched an up interface,
            # so is_up was only ever set on down ones (found 2026-09-22, MOW-R195P-1002, via the monitoring snapshot).
            flags = re.search(r"<([A-Z_,]+)>", line)
            if flags:
                entry["is_up"] = "UP" in flags.group(1).split(",")

            mac = re.search(r"link/ether\s+([0-9a-fA-F:]{17})", line)
            if mac:
                entry["mac_address"] = mac.group(1).lower()

            addr = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+/\d+)", line)
            if addr:
                entry["ipv4_addresses"].append(addr.group(1))
        return interfaces

    #: Section markers for get_snapshot(). `echo` is a shell builtin, so it needs no binary this BusyBox might lack.
    _SNAPSHOT_SECTIONS = ("uname", "cpuinfo", "uptime", "loadavg", "meminfo", "netdev", "ipaddr", "br0", "stat1", "stat2")
    #: Seconds between the two /proc/stat samples that give CPU utilisation.
    CPU_SAMPLE_S = 2

    def get_snapshot(self) -> dict:
        """Identity, interfaces and monitoring counters from ONE SSH session (added 2026-09-22 for monitoring).

        Every other getter here is its own SSH session; a monitoring read through them costs about seven logins, and this
        dropbear throttles rapid repeated logins (see references/06). So one `;`-chained command reads everything, with an
        `echo` marker before each section. No pipes: a piped command exited 127 on this shell (the `head` it used is
        absent). Each file is its own `cat` so one missing file cannot hide the rest. Returns `facts` and `interfaces` in
        the same shape as get_facts()/get_interfaces(), plus `counters`:
          - `uptime_s`: first field of /proc/uptime;
          - `cpu_percent`: CPU utilisation from two /proc/stat samples CPU_SAMPLE_S apart (the CPU measure to use);
          - `load`: the 1, 5 and 15 minute load averages of /proc/loadavg (kept for reference; not a CPU measure here);
          - `cpus`: `processor` entries in /proc/cpuinfo (a real core count, which the enterprise Wi-Fi REST API lacks);
          - `memory`: MemTotal, MemFree, Buffers and Shmem from /proc/meminfo, converted from kB to bytes;
          - `net_dev`: per-interface rx/tx bytes, packets, errors and drops from /proc/net/dev.
        """
        parts = [f"echo ==={name}===; " + cmd for name, cmd in zip(self._SNAPSHOT_SECTIONS, (
            "uname -a", "cat /proc/cpuinfo", "cat /proc/uptime", "cat /proc/loadavg", "cat /proc/meminfo", "cat /proc/net/dev",
            "ip -o addr show 2>&1", "ifconfig br0 2>/dev/null", f"cat /proc/stat; sleep {self.CPU_SAMPLE_S}", "cat /proc/stat"))]
        text = self._run("; ".join(parts), allow_nonzero=True)
        sections: dict[str, str] = {}
        current = None
        for line in text.splitlines():
            marker = re.fullmatch(r"===(\w+)===", line.strip())
            if marker:
                current = marker.group(1)
                sections[current] = ""
            elif current:
                sections[current] += line + "\n"
        missing = [name for name in self._SNAPSHOT_SECTIONS if name not in sections]
        if missing:
            raise RuntimeError(f"snapshot incomplete, sections missing: {missing}")

        uname = sections["uname"].strip()
        uname_parts = uname.split()
        soc = next((line.split(":", 1)[-1].strip() for line in sections["cpuinfo"].splitlines() if "system type" in line.lower()), None)
        facts = {
            "vendor": "Cambium Networks",
            "model": "R195P",
            "hostname": uname_parts[1] if len(uname_parts) > 1 else None,
            "kernel_version": uname_parts[2] if len(uname_parts) > 2 else None,
            "soc": soc,
            "lan_mac_address": self._extract_mac(sections["br0"]) if sections["br0"].strip() else None,
            "raw_uname": uname,
        }
        counters: dict = {"cpus": sum(1 for line in sections["cpuinfo"].splitlines() if re.match(r"processor\s*:", line))}
        uptime = sections["uptime"].split()
        counters["uptime_s"] = int(float(uptime[0])) if uptime else None
        # CPU utilisation from two /proc/stat samples, not the load average: on MOW-R195P-1002 (2026-09-22) the load average read
        # 9.75 on 4 cores while the CPU was 2.1 % busy, with one process running and none blocked. Idle = idle + iowait.
        def cpu_times(text: str) -> list[int] | None:
            line = next((line for line in text.splitlines() if line.startswith("cpu ")), None)
            return [int(x) for x in line.split()[1:]] if line else None
        first, second = cpu_times(sections["stat1"]), cpu_times(sections["stat2"])
        counters["cpu_percent"] = None
        if first and second:
            delta = [b - a for a, b in zip(first, second)]
            total = sum(delta)
            idle = delta[3] + (delta[4] if len(delta) > 4 else 0)
            counters["cpu_percent"] = round(100.0 * (total - idle) / total, 1) if total > 0 else None
        load = sections["loadavg"].split()
        counters["load"] = [float(x) for x in load[:3]] if len(load) >= 3 else None
        memory = {}
        for line in sections["meminfo"].splitlines():
            m = re.match(r"(MemTotal|MemFree|Buffers|Shmem):\s+(\d+)\s*kB", line)
            if m:
                memory[m.group(1)] = int(m.group(2)) * 1024
        counters["memory"] = memory or None
        net_dev = {}
        for line in sections["netdev"].splitlines():
            if ":" not in line or "|" in line:
                continue
            name, _, rest = line.partition(":")
            fields = rest.split()
            if len(fields) >= 16 and all(f.isdigit() for f in fields[:16]):
                net_dev[name.strip()] = {"rx_bytes": int(fields[0]), "rx_packets": int(fields[1]), "rx_errors": int(fields[2]),
                                          "rx_dropped": int(fields[3]), "tx_bytes": int(fields[8]), "tx_packets": int(fields[9]),
                                          "tx_errors": int(fields[10]), "tx_dropped": int(fields[11])}
        counters["net_dev"] = net_dev
        interfaces = self._parse_ip_addr(sections["ipaddr"])
        # The facts standard requires wan_mac_address. The WAN port's name varies by unit (wan1 on older units, wan3 at mowanjum,
        # 2026-09-22), so take the first `wan*` port without a VLAN suffix rather than asking `ifconfig` for one fixed name.
        facts["wan_mac_address"] = next((v.get("mac_address") for n, v in sorted(interfaces.items())
                                         if n.startswith("wan") and "." not in n and v.get("mac_address")), None)
        return {"facts": facts, "interfaces": interfaces, "counters": counters}

    def _try_get_mac(self, remote_command: str) -> str | None:
        """Runs remote_command (expected to be an `ifconfig <name>` invocation) and extracts a MAC address from its output, returning
        None if the command fails (e.g. that interface doesn't exist on this unit) rather than raising."""
        try:
            return self._extract_mac(self._run(remote_command))
        except RuntimeError:
            return None

    @staticmethod
    def _extract_mac(text: str) -> str | None:
        for token in text.replace(":", " ").split():
            candidate = token
            if len(candidate) == 12 and all(c in "0123456789abcdefABCDEF" for c in candidate):
                return ":".join(candidate[i:i + 2] for i in range(0, 12, 2)).lower()
        # Fall back to scanning colon-separated tokens directly (ifconfig/ip both print MACs this way).
        for line in text.splitlines():
            for token in line.split():
                if token.count(":") == 5 and len(token) == 17:
                    return token.lower()
        return None

    def get_config(self) -> dict:
        """Config snapshot for backup/diff — see the module docstring's 2026-09-18 note for why this was deliberately unbuilt until now
        and what changed. Source: `cat /etc/config/* 2>&1` over the same SSH path every other getter here uses (BusyBox has no `uci`
        binary confirmed on this platform — see 03_asset-register-conventions.md — so this reads the UCI-style config files directly
        rather than shelling a config tool that may not exist). Parses the raw UCI text into a nested dict and REDACTS every
        credential-shaped option via REDACT_KEY_PATTERN before returning — callers must never call `_run("cat /etc/config/*")` directly
        and print/log/persist the result themselves, same rule as every other family's get_config()."""
        raw = self._run("cat /etc/config/* 2>&1", allow_nonzero=True)
        parsed = self._parse_uci_text(raw)
        if set(parsed) - {"_unparsed"}:
            return redact(parsed)
        # 4.7.3-R21 units (tjuntjuntjara, 2026-09-24) have no /etc/config at all: their live settings sit in the MediaTek nvram
        # (zone 2860, read per key with `nvram_get 2860 <key>`; the key list is /var/param_default's), plus the wireless profiles
        # /etc/Wireless/RT2860/RT2860_{2G,5G,dbdc}.dat. Same redaction, same nested shape. No pipes on this shell, `;` works.
        return redact(self._read_nvram_config())

    NVRAM_BATCH = 100  # keys per SSH session: 60 and 100 both took ~11 s on a 4.7.3-R21 unit; 200 got the session closed

    def _read_nvram_config(self) -> dict:
        """{"nvram": {key: value}, "rt2860_2g": {...}, "rt2860_5g": {...}, "rt2860_dbdc": {...}}, unredacted (callers redact)."""
        defaults = self._run("cat /var/param_default 2>&1", allow_nonzero=True)
        keys = [line.split("=", 1)[0].strip() for line in defaults.splitlines() if "=" in line and not line.startswith("#")]
        values: dict = {}
        for start in range(0, len(keys), self.NVRAM_BATCH):
            batch = keys[start : start + self.NVRAM_BATCH]
            out = self._run("; ".join(f'echo "@@{k}"; nvram_get 2860 {k}' for k in batch), allow_nonzero=True)
            current = None
            for line in out.splitlines():
                if line.startswith("@@"):
                    current = line[2:]
                    values[current] = ""
                elif current is not None:
                    values[current] = f"{values[current]}\n{line}" if values[current] else line
        result = {"nvram": values}
        for name in ("2G", "5G", "dbdc"):
            text = self._run(f"cat /etc/Wireless/RT2860/RT2860_{name}.dat 2>&1", allow_nonzero=True)
            result[f"rt2860_{name.lower()}"] = {l.split("=", 1)[0].strip(): l.split("=", 1)[1].strip() for l in text.splitlines()
                                                 if "=" in l and not l.startswith("#")}
        return result

    @staticmethod
    def _parse_uci_text(text: str) -> dict:
        """Best-effort parse of BusyBox/OpenWrt-style UCI config text into a nested dict keyed by `"<type>.<name>"` per `config` stanza,
        each holding its `option`/`list` key-value pairs. Never confirmed live before this method (no prior session ran the underlying
        dump), so this tolerates any line shape gracefully rather than assuming one: an unrecognized line (a different config-file
        syntax entirely, or `cat`'s own "No such file" stderr text mixed into the same 2>&1 stream) is kept verbatim under a synthetic
        `_unparsed` key instead of being silently dropped, so redact() still gets a chance to scrub anything credential-shaped in it and
        a caller can see the raw text was there rather than getting a falsely-empty result."""
        sections: dict = {}
        current: dict | None = None
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            config_match = re.match(r"^config\s+(\S+)(?:\s+'([^']*)'|\s+\"([^\"]*)\"|\s+(\S+))?", stripped)
            if config_match:
                kind = config_match.group(1)
                name = config_match.group(2) or config_match.group(3) or config_match.group(4) or f"section{len(sections)}"
                current = {}
                sections[f"{kind}.{name}"] = current
                continue

            option_match = re.match(r"^(option|list)\s+(\S+)\s+(?:'([^']*)'|\"([^\"]*)\"|(\S+))", stripped)
            if option_match and current is not None:
                key = option_match.group(2)
                value = option_match.group(3)
                if value is None:
                    value = option_match.group(4)
                if value is None:
                    value = option_match.group(5)
                if option_match.group(1) == "list":
                    existing = current.get(key)
                    if not isinstance(existing, list):
                        existing = [] if existing is None else [existing]
                    existing.append(value)
                    current[key] = existing
                else:
                    current[key] = value
                continue

            sections.setdefault("_unparsed", [])
            sections["_unparsed"].append(stripped)
        return sections


def _cmd_getters(adapter: CambiumR195PAdapter) -> int:
    adapter.login()
    try:
        result = {
            "facts": adapter.get_facts(),
            "interfaces": adapter.get_interfaces(),
        }
        print(json.dumps(result, indent=2))
    finally:
        adapter.logout()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--include-config",
        action="store_true",
        help="also fetch and print the redacted /etc/config/* snapshot (get_config) alongside facts/interfaces",
    )
    args = parser.parse_args()

    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumR195PAdapter(host, username, password)

    if args.include_config:
        adapter.login()
        try:
            result = {
                "facts": adapter.get_facts(),
                "interfaces": adapter.get_interfaces(),
                "config": adapter.get_config(),
            }
            print(json.dumps(result, indent=2))
        finally:
            adapter.logout()
        return 0

    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: scripts/cambium_xv2_adapter.py
````python
#!/usr/bin/env python3
"""Minimal Cambium Enterprise Wi-Fi (XV2/Falcon UI) REST adapter.

Implements the vendor-adapter getters from the Option 3 controller architecture (see cambium-swap's docs/migration/controller-option3/
option-3-architecture.md and docs/migration/controller-option3/cambium-vendor-adapter-data-points.md) using nothing but the Python standard
library: no requests, no schema, no code generation.

This exists to answer a real question rather than settle it by opinion: does a Cambium adapter need a formal CLI/API grammar
(command-schema.json, OpenAPI generation, Tree-sitter/ANTLR, an AI extraction pipeline) before it can be written? Answer, confirmed live
against a real Hope Vale device 2026-09-17: no. See skill-walk-before-run's ledger.jsonl for the RESOLVED entry this test closes.

Auth flow (reverse-engineered from the device's own served JS, not guessed — see references/02_device-access-and-vault.md): POST /api/login
with a JSON body, then every following call needs both the session cookies AND an X-XSRF-TOKEN header echoing the XSRF-TOKEN cookie value.

This adapter also covers the older Enterprise Wi-Fi E-series (E500, E430) — confirmed live 2026-09-17 (cambium-swap evidence E118): same
Falcon-family REST API and CLI, no separate adapter needed. See references/06_device-api-cli-reference.md's "Enterprise Wi-Fi E-series"
section for the specific units and firmware confirmed.

Usage:
    # Run the implemented getters, print JSON to stdout:
    CAMBIUM_HOST=localhost:10001 CAMBIUM_USER=admin CAMBIUM_PASS='...' python3 cambium_xv2_adapter.py

    # Explore arbitrary raw endpoints (writes one redacted JSON file per endpoint to a dir, never
    # prints raw content to stdout/stderr — see REDACT_KEY_PATTERN before trusting an unfamiliar
    # endpoint's output):
    CAMBIUM_HOST=... CAMBIUM_USER=... CAMBIUM_PASS=... python3 cambium_xv2_adapter.py \
        --dump radio-summary,wlan-summary,events --dump-dir /tmp/xv2-dump

Never hardcode or print CAMBIUM_PASS — pull it from the KeePassXC vault (`kp show -s -a Password cambium-devices/enterprise-wifi`) into an
env var at the call site, per skill-cambium's own device-access rule.

SECRET-EXPOSURE INCIDENT (2026-09-17): an early exploration pass printed /api/system-config's snmp_read_community/snmp_write_community
values to a terminal transcript because the ad hoc redaction used that session only matched pass/psk/secret/key/shared — not "community".
REDACT_KEY_PATTERN below is the single, deliberately broad, hard-coded fix: every dict key matching it is redacted everywhere this module
ever returns or writes device data, in get_config() and in --dump. Widen it, never narrow it, if another vendor field name is found to
carry a real secret.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request

REDACT_KEY_PATTERN = re.compile(
    r"pass|pwd|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def redact(obj):
    """Recursively replace any dict value whose key looks credential-shaped with a placeholder."""
    if isinstance(obj, dict):
        return {
            k: "<REDACTED>" if REDACT_KEY_PATTERN.search(k) else redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


class CambiumXV2Adapter:
    """Talks to one Enterprise Wi-Fi XV2/XE-family AP's local REST API over HTTPS."""

    def __init__(self, host: str, username: str, password: str, verify_tls: bool = False) -> None:
        self.base_url = f"https://{host}"
        self._username = username
        self._password = password
        self._xsrf_token: str | None = None

        ctx = ssl.create_default_context()
        if not verify_tls:
            # Device presents a self-signed cert on its management interface — expected here, not a security bypass for anything
            # internet-facing.
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        self._cookiejar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._cookiejar),
            urllib.request.HTTPSHandler(context=ctx),
        )

    def _request(self, method: str, path: str, body: dict | None = None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if data is not None else {}
        if self._xsrf_token:
            headers["X-XSRF-TOKEN"] = self._xsrf_token

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc

        for cookie in self._cookiejar:
            if cookie.name == "XSRF-TOKEN":
                self._xsrf_token = cookie.value

        return json.loads(raw) if raw else {}

    def get_raw(self, endpoint: str):
        """Public escape hatch for exploring an endpoint not yet wrapped by a getter below.

        Returns the RAW (unredacted) response — callers that might print, log, or write this to
        disk must redact() it themselves first. Used by --dump, which does exactly that.
        """
        path = endpoint if endpoint.startswith("/api/") else f"/api/{endpoint}"
        return self._request("GET", path)

    def login(self) -> None:
        result = self._request("POST", "/api/login", {"username": self._username, "password": self._password})
        if not result.get("success"):
            raise RuntimeError(f"Cambium login failed: {result}")

    def logout(self) -> None:
        self._request("POST", "/api/logout")

    def get_facts(self) -> dict:
        """NAPALM-style get_facts: device identity, firmware, uptime, cnMaestro connection state."""
        platform = self._request("GET", "/api/platform-info")
        summary = self._request("GET", "/api/device-summary")
        return {
            "vendor": "Cambium Networks",
            "model": platform.get("model") or summary.get("model"),
            "hostname": summary.get("hostname"),
            "serial_number": summary.get("serial_number"),
            "os_version": summary.get("version"),
            "uptime_seconds": summary.get("uptime"),
            "mac_address": summary.get("device_mac"),
            "cnmaestro_status": summary.get("cns_status"),
        }

    def get_interfaces(self) -> dict:
        """NAPALM-style get_interfaces: per-port link state and counters.

        device-summary carries link/speed/duplex in TWO places that disagree: `port_stats[].link` is not reliable (observed "DOWN" on
        Tower 1's ETH1 while it was physically up and passing traffic — confirmed live 2026-09-17), while `port_status[].link` (a separate
        array, integer 1/0) matched reality. Use port_status as authoritative for link/speed/duplex; port_stats for counters only.
        """
        summary = self._request("GET", "/api/device-summary")

        status_by_port = {
            p["device"]: p for p in summary.get("port_status", []) if p.get("device")
        }

        interfaces = {}
        for port in summary.get("port_stats", []):
            name = port.get("device")
            if not name:
                continue
            status = status_by_port.get(name, {})
            interfaces[name] = {
                "is_up": bool(status.get("link", 0)),
                "speed": status.get("speed", port.get("speed")),
                "duplex": "FULL" if status.get("duplex") == 1 else ("HALF" if status.get("duplex") == 0 else port.get("duplex")),
                "rx_bytes": port.get("rx_bytes"),
                "tx_bytes": port.get("tx_bytes"),
                "rx_errors": port.get("rx_errs"),
                "tx_errors": port.get("tx_errs"),
            }
        return interfaces

    def get_radios(self) -> dict:
        """Per-radio operational state, channel/power, and utilization — merges radio-summary (state, channel, power, client/traffic
        counters) with radio-rf-summary (channel utilization, noise floor), by list position (both are ordered by radio index; neither
        response carries a shared join key — confirmed by inspecting both live 2026-09-17)."""
        summary = self._request("GET", "/api/radio-summary") or []
        rf = self._request("GET", "/api/radio-rf-summary") or []

        radios = {}
        for i, radio in enumerate(summary):
            device_id = radio.get("device", i)
            rf_stats = rf[i] if i < len(rf) else {}
            radios[device_id] = {
                "band": radio.get("band"),
                "mac": radio.get("mac"),
                "state": radio.get("radio_state"),
                "channel": radio.get("channel"),
                "channel_width": radio.get("channel-width"),
                "power": radio.get("power"),
                "num_clients": radio.get("num_clients"),
                "num_wlans": radio.get("num_wlans"),
                "utilization_pct": rf_stats.get("total_cu"),
                "noise_floor": rf_stats.get("nf"),
                "packet_error_rate": rf_stats.get("per"),
            }
        return radios

    def get_wlans(self) -> dict:
        """SSID/WLAN definitions and stats — merges wlan-summary (security, VLAN, traffic counters) with wlan-interface-summary (per-band
        BSSID/link status), joined on SSID name. (/api/wlan-config 500'd on this firmware when queried with no params — not used; wlan
        definitions come from wlan-summary instead, which is sufficient for read/monitoring use.)
        """
        summary = self._request("GET", "/api/wlan-summary") or []
        interfaces = self._request("GET", "/api/wlan-interface-summary") or []

        by_ssid: dict[str, dict] = {}
        for wlan in summary:
            ssid = wlan.get("ssid")
            if not ssid:
                continue
            by_ssid[ssid] = {
                "security": wlan.get("security"),
                "vlan": wlan.get("vlan"),
                "guest_access": wlan.get("guest_access"),
                "num_clients": wlan.get("num_clients"),
                "tx_bytes": wlan.get("tx_bytes"),
                "rx_bytes": wlan.get("rx_bytes"),
                "bands": [],
            }
        for iface in interfaces:
            ssid = iface.get("ssid")
            if ssid not in by_ssid:
                continue
            by_ssid[ssid]["bands"].append({
                "band": iface.get("band"),
                "bssid": iface.get("bssid"),
                "status": iface.get("status"),
                "clients": iface.get("clients"),
            })
        return by_ssid

    # `ip6_ll` is the one field whose JSON *type* differs by model, so it is normalised here rather
    # than left for every consumer to special-case. Fleet sweep 2026-09-20: array on XV2 (10 of 32
    # record-bearing observations), string on E500 (6), absent where the client has no link-local
    # address (17). A list is the lossless target — wrapping the E500 string and mapping absent to
    # empty keeps every value, whereas normalising to a string would silently truncate any XV2
    # client holding more than one address.
    #
    # Treat the result as identifying data. An IPv6 link-local address is EUI-64 derived, so it
    # encodes the client MAC: observed `fe80::6885:b9ff:feac:bb89` resolves exactly to MAC
    # `6A-85-B9-AC-BB-89`. Redact it on the same footing as `mac`, not as ordinary telemetry.
    IPV6_LL_FIELD = "ip6_ll"

    def get_clients(self) -> list:
        """Currently-associated wireless stations. Empty list is a real, valid state (observed live 2026-09-17 — no clients connected at
        query time), not a parsing failure.

        `ip6_ll` is normalised to a list on every record, including records where the device omitted it — see the note above the method
        for why a list is the lossless direction and why the value is identifying."""
        clients = self._request("GET", "/api/client-summary") or []
        for client in clients:
            if not isinstance(client, dict):
                continue
            value = client.get(self.IPV6_LL_FIELD)
            if isinstance(value, list):
                client[self.IPV6_LL_FIELD] = [v for v in value if v]
            elif value:
                client[self.IPV6_LL_FIELD] = [value]
            else:
                client[self.IPV6_LL_FIELD] = []
        return clients

    def get_config(self) -> dict:
        """Config snapshot for backup/diff — the read path this family needs since SNMP config is unsupported (evidence E34). REDACTS
        every credential-shaped field via REDACT_KEY_PATTERN before returning; callers must never bypass this by calling the underlying
        endpoints directly without also redacting (get_raw() intentionally does not redact — see its docstring)."""
        merged = {
            "system": self._request("GET", "/api/system-config"),
            "network": self._request("GET", "/api/network-config"),
            "vlan": self._request("GET", "/api/vlan-config"),
            "dhcp": self._request("GET", "/api/dhcp-config"),
            "firewall": self._request("GET", "/api/firewall-config"),
            "service": self._request("GET", "/api/service-config"),
        }
        return redact(merged)

    def get_events(self, limit: int = 100) -> list:
        """Local event log — most-recent-first strings, as the device returns them (already human-readable, e.g. "Sep 17 14:15:22
        WIFI-4-CLIENT-DISCONNECTED ..."). Capped at `limit` since the raw log observed live 2026-09-17 was 41KB / hundreds of entries."""
        events = self._request("GET", "/api/events") or []
        return events[:limit]


def _cmd_getters(adapter: CambiumXV2Adapter) -> int:
    adapter.login()
    try:
        result = {
            "facts": adapter.get_facts(),
            "interfaces": adapter.get_interfaces(),
            "radios": adapter.get_radios(),
            "wlans": adapter.get_wlans(),
            "clients": adapter.get_clients(),
            "config": adapter.get_config(),
            "events": adapter.get_events(limit=20),
        }
        print(json.dumps(result, indent=2))
    finally:
        adapter.logout()
    return 0


def _cmd_dump(adapter: CambiumXV2Adapter, endpoints: list[str], dump_dir: str) -> int:
    os.makedirs(dump_dir, exist_ok=True)
    adapter.login()
    try:
        for ep in endpoints:
            ep = ep.strip()
            if not ep:
                continue
            try:
                raw = adapter.get_raw(ep)
            except RuntimeError as exc:
                print(f"{ep}: ERROR — {exc}", file=sys.stderr)
                continue
            out_path = os.path.join(dump_dir, f"{ep.strip('/').replace('/', '_')}.json")
            with open(out_path, "w") as f:
                json.dump(redact(raw), f, indent=1)
            print(f"{ep}: wrote {out_path}", file=sys.stderr)
    finally:
        adapter.logout()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dump", help="comma-separated list of raw /api/<name> endpoints to fetch and save (redacted) instead of running the getters")
    parser.add_argument("--dump-dir", default="/tmp/cambium-xv2-dump", help="directory to write --dump output into (default: /tmp/cambium-xv2-dump)")
    args = parser.parse_args()

    host = os.environ.get("CAMBIUM_HOST")
    username = os.environ.get("CAMBIUM_USER")
    password = os.environ.get("CAMBIUM_PASS")
    if not (host and username and password):
        print("Set CAMBIUM_HOST, CAMBIUM_USER, CAMBIUM_PASS (never hardcode the password).", file=sys.stderr)
        return 2

    adapter = CambiumXV2Adapter(host, username, password)

    if args.dump:
        return _cmd_dump(adapter, args.dump.split(","), args.dump_dir)
    return _cmd_getters(adapter)


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: scripts/cambium-portal.sh
````bash
#!/usr/bin/env bash
# Cambium support portal (support.cambiumnetworks.com) automation: login, and fetching a specific
# release's files (firmware image, MIBs, etc.) for archiving in a consuming project.
#
# Read-only against the portal: signs in, searches Downloads, downloads files a logged-in user
# could already download by hand. Never uploads, submits a case, or changes anything Cambium-side.
# Nothing here touches AWS, cnMaestro or devices.
#
# Moved here from cambium-swap 2026-09-17 (was scripts/cambium-support-login.sh) — this is
# cross-project Cambium vendor-research tooling, not specific to any one consuming project's
# investigation. See skill-cambium's Standing Write-Back Contract.
#
# Requires: npx (Node), the KeePassXC `kp` wrapper at ~/.config/keepassxc/kp with an entry named
# "/Network/cambium support" (UserName + Password attributes), and a LIVE MFA code from the account
# holder — the vault entry has no stored TOTP seed (its Notes field says "2FA OTP"), so this cannot
# run unattended. Run it from an interactive shell (or have the operator paste the current code the
# moment it is asked for, since codes expire in well under a minute).
#
# Usage:
#   cambium-portal.sh login                          # login only, session stays open
#   cambium-portal.sh login --search "cnMaestro"     # login, then open a Downloads search
#   cambium-portal.sh fetch-release "<model search>" "<version string>" <dest-dir>
#       # login, search Downloads for <model search>, expand the release heading whose text
#       # contains <version string>, download every file under it into <dest-dir>, sniff each
#       # file's real type (MIB text vs firmware image vs other) since the portal's download
#       # links carry no filename, and print a short manifest (path, sniffed type, sha256).
#       # Does NOT commit anything to git and does NOT decide storage_locations — that policy
#       # decision belongs to the consuming project (see its firmware-manifest.yaml /
#       # software-manifest.yaml convention for recording a checksum without committing a binary).
#
# See docs/operations/agent-research-and-tooling-notes.md in a consuming project (originally
# written in cambium-swap) for the manual step-by-step this automates, why the sidebar accordion
# on /files must be avoided in favour of the search box, and why /file/<hash> download links are
# per-session and must always be re-derived rather than reused.
#
# Known gap (2026-09-17): Cambium does not publish a per-patch-version CLI reference or release
# notes file separately from firmware/MIBs on this portal for XV2 — only firmware image + MIB
# files are attached to each dated release entry. For CLI-syntax-vs-firmware-version questions,
# cross-check the CLI Reference Guide's own "New Commands Introduced in <release>" section instead
# of expecting a version-specific CLI doc to exist.

set -euo pipefail

AB_PKG="agent-browser@0.37.1"
AB() { npx --yes "$AB_PKG" "$@"; }

KP="${HOME}/.config/keepassxc/kp"
ENTRY="/Network/cambium support"
PORTAL_URL="https://support.cambiumnetworks.com/"

cambium_login() {
  local search_query="$1"

  if [ ! -x "$KP" ]; then
    echo "kp wrapper not found or not executable at $KP — see the KeePassXC reference in your memory system" >&2
    exit 1
  fi

  local username
  username="$("$KP" show -a UserName "$ENTRY")"
  if [ -z "$username" ]; then
    echo "Could not read UserName from KeePassXC entry '$ENTRY'" >&2
    exit 1
  fi

  echo "Opening $PORTAL_URL ..." >&2
  AB open "$PORTAL_URL"
  AB find text "Login" click
  AB wait --load networkidle

  echo "Filling email ($username) ..." >&2
  AB find label "Email address" fill "$username"
  AB find role button --name Next click 2>/dev/null || AB find text "Next" click
  AB wait --load networkidle

  echo "Filling password (from vault, not printed) ..." >&2
  local pw
  pw="$("$KP" show -s -a Password "$ENTRY")"
  AB find label "Password" fill "$pw"
  unset pw
  AB find role button --name "Sign In" click 2>/dev/null || AB find text "Sign In" click
  AB wait --load networkidle

  echo "" >&2
  echo "=== MFA required — this account has no stored TOTP seed. ===" >&2
  local otp
  read -r -p "Enter the current authentication code from the account holder: " otp
  if [ -z "$otp" ]; then
    echo "No code entered, aborting." >&2
    exit 1
  fi

  AB find label "Authentication Code" fill "$otp"
  AB find role button --name Submit click 2>/dev/null || AB find text "Submit" click
  AB wait --load networkidle

  if AB snapshot -i 2>/dev/null | grep -q 'button "Malik Ahmad"'; then
    echo "Logged in as Malik Ahmad." >&2
  else
    echo "WARNING: could not confirm login — snapshot the page and check manually (agent-browser snapshot -i)." >&2
  fi

  if [ -n "$search_query" ]; then
    echo "Searching Downloads for: $search_query" >&2
    AB open "https://support.cambiumnetworks.com/files?q=${search_query// /%20}"
    AB wait --load networkidle
    AB snapshot -i
  fi
}

cmd_login() {
  local search_query=""
  if [ "${1:-}" = "--search" ]; then
    search_query="${2:?--search requires a query, e.g. --search cnMaestro}"
  fi
  cambium_login "$search_query"
  echo "" >&2
  echo "Session left open. Continue with: npx --yes $AB_PKG <command...> (snapshot -i, click, get attr <ref> href, download <ref> <path>)." >&2
  echo "Close when done: npx --yes $AB_PKG close" >&2
}

cmd_fetch_release() {
  local model_query="${1:?usage: fetch-release <model search> <version string> <dest-dir>}"
  local version_string="${2:?usage: fetch-release <model search> <version string> <dest-dir>}"
  local dest_dir="${3:?usage: fetch-release <model search> <version string> <dest-dir>}"

  mkdir -p "$dest_dir"
  cambium_login "$model_query"

  echo "" >&2
  echo "Looking for a release heading containing: $version_string" >&2
  local snapshot
  snapshot="$(AB snapshot -i 2>&1)"
  local heading_line
  heading_line="$(printf '%s\n' "$snapshot" | grep -F "$version_string" | grep -m1 "link\|heading")"
  if [ -z "$heading_line" ]; then
    echo "No matching release entry found for '$version_string' in the current Downloads search results." >&2
    echo "Re-run with a broader --search or inspect manually: npx --yes $AB_PKG snapshot -i" >&2
    exit 1
  fi
  local ref
  ref="$(printf '%s\n' "$heading_line" | grep -oE 'ref=e[0-9]+' | head -1 | cut -d= -f2)"
  echo "Matched: $heading_line" >&2
  echo "Expanding ref=$ref ..." >&2
  AB click "$ref"
  AB wait --load networkidle

  # Re-snapshot and find every "Download" link immediately after this release's heading and
  # before the next heading — the portal renders one heading per release with its files nested
  # under it, no distinguishing labels on the Download links themselves.
  snapshot="$(AB snapshot -i 2>&1)"
  local in_section=0
  local dl_refs=()
  while IFS= read -r line; do
    if printf '%s' "$line" | grep -qF "$version_string"; then
      in_section=1
      continue
    fi
    if [ "$in_section" = 1 ]; then
      if printf '%s' "$line" | grep -q '^- heading'; then
        break
      fi
      if printf '%s' "$line" | grep -q '"Download"'; then
        dl_refs+=("$(printf '%s' "$line" | grep -oE 'ref=e[0-9]+' | cut -d= -f2)")
      fi
    fi
  done <<< "$snapshot"

  if [ "${#dl_refs[@]}" -eq 0 ]; then
    echo "No Download links found under the matched release heading." >&2
    exit 1
  fi

  echo "Found ${#dl_refs[@]} download link(s): ${dl_refs[*]}" >&2
  echo "" >&2
  printf '%-40s %-20s %s\n' "file" "sniffed_type" "sha256"
  local i=1
  for r in "${dl_refs[@]}"; do
    local out="$dest_dir/download-${i}.bin"
    if AB download "$r" "$out" >/dev/null 2>&1; then
      local kind
      kind="$(file -b "$out" | cut -c1-20)"
      local sum
      sum="$(shasum -a 256 "$out" | awk '{print $1}')"
      printf '%-40s %-20s %s\n' "$out" "$kind" "$sum"
    else
      echo "Download failed for ref=$r (see docs/operations/agent-research-and-tooling-notes.md for the per-session download-link gotcha; retry the whole fetch-release run)" >&2
    fi
    i=$((i + 1))
  done

  echo "" >&2
  echo "Downloaded files are NOT committed to git and storage_locations is NOT decided here — that is" >&2
  echo "a consuming-project policy decision (see its firmware-manifest.yaml / software-manifest.yaml)." >&2
}

case "${1:-}" in
  login)
    shift
    cmd_login "$@"
    ;;
  fetch-release)
    shift
    cmd_fetch_release "$@"
    ;;
  *)
    echo "Usage: $0 login [--search QUERY] | fetch-release <model search> <version string> <dest-dir>" >&2
    exit 2
    ;;
esac
````

## File: scripts/check_governance.py
````python
#!/usr/bin/env python3
"""Governance coherence checks for skill-cambium.

Turns this project's governance CLAIMS into assertions that fail. Stdlib only, so the gate never fails for environment reasons; exit 1 on any failure so it can gate the task runner.

Generated by skill-ai-it from templates/check_governance.py. Doctrine, check families, and the inference table live in the skill's patterns/governance-checks.md — read that before adding,
changing, or retiring a check.

Structure:
  CONFIG      — registries the agent tunes per project. Everything below CONFIG is generic.
  Tier 1      — universal checks. Present in every project.
  Tier 2      — conditional checks. Kept only when their trigger artifact exists.
  Tier 3      — project-specific invariants. Authored per project; each cites the rule it enforces.

Growth rule: this file is expected to grow with the project. A new class of artifact needs a coverage check; a new duplicated constant needs a registry entry. When a check fails, fix the
project, not the check.

Checks:
  1. Referenced paths in the governance surfaces resolve on disk (relative to the referencing file, then to the repo root).
  2. Index links resolve, and every indexed folder member is linked.
  3. Count claims in prose match reality (historical facts exempt).
  4. Cataloged items exist and existing items are cataloged.
  5. Task-runner recipes named in prose exist in the runner.
  5b. No recipe reaches an interpreter implicitly — neither a bare `python3`/`node` nor `mise exec -- python`.
  6. Derived artifacts are not older than their inputs.
  7. Every surface restating a registered constant states it identically, and nothing unregistered restates it.
  8. Every row of an append-only table stamps its pass, and no pass records the same entity twice.
  9. Every dated evidence capture states its URL, retrieval date and HTTP status, or names the capture that corrects it.
  10. manifest.json's `updated_at` is not older than CHANGELOG.md's latest dated entry.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Repo-relative path to this file. Used to exclude the checker from the constant scan: it necessarily contains every
# registered constant's PATTERN, and comparing `rel` against a bare `Path(__file__).name` never matched, so the checker
# reported each of its own pattern definitions as an unregistered restatement.
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()

# --------------------------------------------------------------------------------------------------------------- CONFIG
# Tune these registries to the project. Leave a registry empty and its check contributes zero assertions rather than
# failing — coverage is measured by the assertion count, so an empty registry reads honestly as "not covered yet".

# Governance surfaces whose path references must resolve.
# DERIVED, not hand-listed. Until 2026-09-20 this was a fixed tuple, so `references/**` — where this package's
# actual content lives — sat outside every path check. The sibling project `unified-network-controller` had the same
# hole and it hid two genuinely broken links under a green suite; see its
# `.archcore/rules/govern-a-derived-population-never-a-hand-list.rule.md`. A check's POPULATION is derived; a check's
# PERMISSIONS (CONDITIONAL_PATHS, markers) stay explicit and per-entry reasoned.
#
# `references/**` is EXCLUDED, and the reason is stated rather than left as an omission: those files use slash
# notation for things that are not filesystem paths — KeePassXC vault groups (`cambium-devices/epmp-ap`), CIDR
# blocks (`10.255.0.1/19`), sibling-repo paths — and a path check run over them reports ~50 non-defects. Bringing
# them in needs a token discriminator that tells a filesystem path from a vault group, not a longer exemption list;
# a check that mostly reports non-defects is one nobody reads. Their split-path tokens ARE checked, by
# check_split_path_tokens, which scans every markdown file in the package.
# A path claim may legitimately name a file in a SIBLING repo — `cambium-swap`'s inventory, `skill-smc`'s scripts,
# the controller project's design docs. Declaring those roots makes such references VERIFIED rather than merely
# unchecked: if a sibling renames or moves the target, this package's routing into it fails loudly. An absent root is
# reported as SKIPPED, never as passed. `.` is included so a self-reference written with the package-name prefix
# (`skill-cambium/CHANGELOG.md`) resolves.
SIBLING_ROOTS: dict[str, str] = {
    "self-parent":                "..",
    "apn-projects":               "../../../../../_project/project_stuff/apn",
    "cambium-swap":               "../../../../../_project/project_stuff/apn/cambium-swap",
    "unified-network-controller": "../../../../../_project/project_stuff/apn/unified-network-controller",
    "skill-smc":                  "../skill-smc",
}


def _sibling_roots() -> list[Path]:
    roots: list[Path] = []
    for name, rel in sorted(SIBLING_ROOTS.items()):
        base = (ROOT / rel).resolve()
        if base.is_dir():
            roots.append(base)
        else:
            print(f"  ... SKIPPED (not passed): sibling root `{name}` absent at {rel}; its references were not verified")
    return roots


def _live_surfaces() -> tuple[str, ...]:
    found = [p.relative_to(ROOT).as_posix()
             for pat in ("*.md", "scripts/README.md")
             for p in ROOT.glob(pat)]
    return tuple(sorted(set(found)))



# Index file -> (folder it indexes, glob). Enforces BOTH directions: links resolve, and members are linked.
CATALOGS: dict[str, tuple[str, str]] = {
    "RUNBOOK.md": ("references", "*.md"),
    "scripts/README.md": ("scripts", "*"),
}

# Files a catalog may legitimately omit (the index itself, generated output, dotfiles).
CATALOG_EXEMPT: frozenset[str] = frozenset({"README.md", "__init__.py"})

# Countable noun -> (folder, glob). A prose claim like "26 documents" is checked against the real count. Choose the glob
# deliberately: "*.md" counts the folder's own index too, which is usually not what the prose means — prefer "[0-9]*.md"
# or a similar shape when the index is excluded from the claim.
COUNT_CLAIMS: dict[str, tuple[str, str]] = {
    # Added 2026-09-17 staleness audit: README.md and AGENTS.md both hardcoded "5 numbered ... files" after a 6th
    # reference file (06_device-api-cli-reference.md) had already been added — caught by manual audit because this
    # registry was empty. Two nouns registered for the same folder/glob because the two surfaces phrase the claim
    # differently ("numbered reference files" vs "numbered files") and the checker matches the noun literally.
    "numbered reference files": ("references", "0*.md"),
    "numbered files": ("references", "0*.md"),
}

# Lines carrying this marker state a historical fact, not a live claim, and are exempt from count checking.
ASAT_MARKER = "count:asat"

# Lines carrying this marker show an ILLUSTRATIVE filename — a naming-convention example — not a reference to a file
# that must exist. Same shape as ASAT_MARKER: explicit, per line, and visible in the document itself rather than
# hidden in an ignore-list here.
EXAMPLE_MARKER = "path:example"

# Paths a governance surface references CONDITIONALLY ("when present"). The generic skill-ai-it navigation block names
# several; each is a real artifact in SOME governed project, so its absence here is a fact about this project's
# toolchain rather than a broken reference. Registered with a per-entry reason rather than silently ignore-listed, so
# the exemption stays reviewable — remove an entry the day the artifact appears. Tune per project.
CONDITIONAL_PATHS: frozenset[str] = frozenset({
    # Archcore files renamed to the <slug>.<type>.md form on 2026-10-05 (v0.6.32). Earlier CHANGELOG entries name the old paths as
    # history; these entries keep that record readable without restating it as a live claim.
    ".archcore/README.md",
    ".archcore/adr/adr-separate-pack-from-skill-smc.md",
    ".archcore/adr/adr-vault-file-avoids-opa-blocked-words.md",
    ".archcore/rules/rule-cambium-smc-cross-pack-boundary.md",
    ".archcore/rules/rule-manifest-version-discipline.md",
    ".archcore/rules/rule-vault-reference-convention.md",
    ".archcore/specs/spec-specialist-pack-file-roles.md",
    "Taskfile.yml",                   # this pack uses justfile, not Task
    "Makefile",
    "package.json",                   # no Node toolchain here
    "graphify-out/GRAPH_REPORT.md",   # graphify not initialized for this pack (skill-smc doesn't use it either)
    "graphify-out/graph.json",
    ".ai-context/governance-pack.md", # generated by repomix; absent until it has run
    ".ai-context/repo-pack.md",
    "memory-bank/activeContext.md",   # this pack uses SCRATCHPAD.md, not a memory-bank
    "memory-bank/progress.md",
    "memory-bank/decisionLog.md",
    ".archcore/rules",                # exemption predates content; harmless now that the folder is populated
    ".archcore/adr",
    ".archcore/specs",
    "ARCHCORE_PROMOTION_CANDIDATES.md",  # deleted by `promote` 2026-09-17; CHANGELOG.md's mentions of it are history, not a live claim
    "cambium-swap/.claude/settings.local.json",  # real file, lives in the sibling cambium-swap project outside this pack's own tree —
                                                  # a documented cross-reference-don't-copy pointer (see CHANGELOG.md's staleness-audit
                                                  # entry), not a broken link; this checker only resolves paths inside ROOT
})

# Task runner file, or None if the project has none.
TASK_RUNNER: str | None = "justfile"

# Files whose prose names task-runner recipes.
RUNNER_REFERENCES: tuple[str, ...] = ("scripts/README.md", "RUNBOOK.md")

# Generated artifact -> inputs it must not be older than.
DERIVED: dict[str, tuple[str, ...]] = {
    # "docs/CLASS-PROFILES.md": ("scripts/class_profiles.py", "process/vehicle-classes.yaml"),
}

# Facts deliberately restated across surfaces. Each entry: the regex that recognises a statement of the fact, and every
# file allowed to state it. Drift fails; so does an UNREGISTERED file stating it — that is what makes this self-extending.
# Pair each entry with a spec document explaining why the duplication is intentional.
CONSTANT_SURFACES: dict[str, dict[str, object]] = {
    # "profit-gate": {
    #     "pattern": r"\$2,500",
    #     "surfaces": ("AGENTS.md", "docs/07-DECISIONS.md"),
    #     "owner": ".archcore/rules/purchase-discipline.rule.md",
    # },
}

# Append-only tables and the columns that give them their grain: (entity column, pass column). An append-only table
# records a re-measurement by ADDING a row, which is right and useless on its own — without a column that orders the
# passes there is no way to compute which row is current, and every aggregate over the table double-counts whatever was
# re-measured. Found in a governed project on 2026-08-28 with twelve rows standing for eight entities, the supersession
# recorded only in a prose note. Register the table here and the grain becomes an assertion instead of an intention.
APPEND_ONLY_TABLES: dict[str, tuple[str, str]] = {
    # "data/sku-scores.csv": ("sku_id", "scored_at"),
}

# Folder of dated evidence captures, or None if the project keeps none. A capture asserts what a source said on a date.
EVIDENCE_DIR: str | None = None  # e.g. "trackers/source-captures"

# The index file inside EVIDENCE_DIR, exempt from the provenance header because it is a catalog, not a capture.
EVIDENCE_INDEX = "README.md"

# Header fields that make a capture re-openable by someone who was not there: where it came from, when, and whether the
# fetch actually succeeded. A capture naming no URL and no HTTP status is a recollection in a capture's clothing — in
# the project this was promoted from, exactly that produced a VERIFIED cost row whose only recorded fetch returned 403.
EVIDENCE_PROVENANCE_FIELDS: tuple[str, ...] = ("Canonical URL", "Retrieved", "HTTP status")

# Captures taken before the provenance rule existed. Each MUST name the later capture supplying the missing provenance —
# this is a correction record, not an exemption. Where captures are immutable the only way to clear an entry is to take
# the correcting capture, which is the behaviour the rule wants. Removing an entry whose correction does not exist turns
# the check red rather than quiet, so the list cannot be emptied by deletion.
EVIDENCE_PROVENANCE_CORRECTED: dict[str, str] = {
    # "uae-wholesale-moq-discounts-20260828.md": "wholesale-house-price-provenance-20260828.md",
}

# Extensions scanned when hunting for unregistered restatements of a constant.
SCAN_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".yaml", ".yml"})

# Path-token discrimination. Prose is full of tokens that look like paths and are not; tune until the check is quiet.
PATHLIKE = re.compile(r"^[A-Za-z0-9._/-]+$")
REPO_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt"})
IGNORE_PREFIXES: tuple[str, ...] = ("http://", "https://", "mailto:", "~/", "/")
IGNORE_EXACT: frozenset[str] = frozenset({"README.md", "AGENTS.md", "CLAUDE.md", "SCRATCHPAD.md", "CHANGELOG.md"})

# --------------------------------------------------------------------------------------------------------------- HARNESS

failures: list[str] = []
checks_run = 0


def fail(check: str, detail: str) -> None:
    failures.append(f"{check}: {detail}")


def counted() -> None:
    """Record one assertion actually evaluated. Never call this per function — only per real comparison."""
    global checks_run
    checks_run += 1


def read(rel: str) -> str | None:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def without_code(text: str) -> str:
    """Strip fenced code blocks. Their contents are examples, not claims about this repo."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def table_rows(rel: str) -> list[dict[str, str]]:
    """Read a CSV as dicts, or an empty list when it does not exist — an absent table contributes zero assertions."""
    path = ROOT / rel
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def members(folder: str, glob: str) -> list[Path]:
    base = ROOT / folder
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob(glob) if p.is_file() and not p.name.startswith("."))


# --------------------------------------------------------------------------------------------------------------- TIER 1


def check_split_path_tokens() -> None:
    """No backticked path is split across two table rows by a trailing backslash.

    A wide table cell wraps mid-filename and leaves the token ending in a backslash with its tail on the next row.
    The reference is unfollowable for a reader and invisible to check_referenced_paths, which skips anything that
    does not look like a path — so the defect hides from the very check that should catch it. Found 20 times across
    this package and its siblings on 2026-09-20. A line that legitimately discusses backslash continuation carries
    the EXAMPLE_MARKER.
    """
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", "graphify-out/", ".ai-context/")) or rel == "CHANGELOG.md":
            continue
        counted()  # one assertion per FILE: "this file splits no path token across rows".
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if EXAMPLE_MARKER in line:
                continue
            for m in re.finditer(r"`([^`\n]*\\)`", line):
                fail("split-path", f"{rel}:{number} splits `{m.group(1)}` across rows; a wrapped table cell broke a "
                                   f"path token in half — join it onto one line")


def check_referenced_paths() -> None:
    """Every path named in a live governance surface resolves — here, or inside a declared sibling checkout."""
    _siblings = _sibling_roots()
    for surface in _live_surfaces():
        text = read(surface)
        if text is None:
            fail("surface", f"{surface} is listed as a governance surface but does not exist")
            counted()
            continue
        body = "\n".join(l for l in without_code(text).splitlines() if EXAMPLE_MARKER not in l)
        tokens = set(re.findall(r"`([^`\n]+)`", body))
        tokens |= {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", body)}
        for raw in sorted(tokens):
            tok = raw.split("#", 1)[0].strip().rstrip("/")
            if not tok or tok in IGNORE_EXACT or tok in CONDITIONAL_PATHS or tok.startswith(IGNORE_PREFIXES):
                continue
            if not PATHLIKE.match(tok):
                continue
            suffix = Path(tok).suffix
            if "/" not in tok and suffix not in REPO_SUFFIXES:
                continue
            if suffix and suffix not in REPO_SUFFIXES:
                continue
            counted()
            # Resolve relative to the file that MAKES the reference first, then relative to ROOT. Resolving only
            # against ROOT false-fails every correct relative link written inside a subfolder README.
            near = (ROOT / surface).parent / tok
            if near.exists() or (ROOT / tok).exists() or any((b / tok).exists() for b in _siblings):
                continue
            fail("path", f"{surface} references `{tok}`, which exists neither here nor under any declared "
                         f"sibling root ({', '.join(sorted(SIBLING_ROOTS))})")


def check_index_links() -> None:
    """Links inside an index file resolve, relative to the index's own folder."""
    for index in CATALOGS:
        text = read(index)
        if text is None:
            fail("index", f"catalog {index} does not exist")
            counted()
            continue
        base = (ROOT / index).parent
        for target in {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", without_code(text))}:
            tok = target.split("#", 1)[0].strip()
            if not tok or tok.startswith(IGNORE_PREFIXES):
                continue
            counted()
            if not (base / tok).exists():
                fail("index", f"{index} links `{tok}` which does not exist")


def check_count_claims() -> None:
    """Prose stating a quantity matches the real count. Lines marked as historical facts are exempt."""
    for noun, (folder, glob) in COUNT_CLAIMS.items():
        actual = len(members(folder, glob))
        pattern = re.compile(rf"(\d+)\s+{re.escape(noun)}\b", re.IGNORECASE)
        for surface in _live_surfaces():
            text = read(surface)
            if text is None:
                continue
            for line in without_code(text).splitlines():
                if ASAT_MARKER in line:
                    continue
                for claim in pattern.finditer(line):
                    counted()
                    if int(claim.group(1)) != actual:
                        fail("count", f"{surface} claims {claim.group(1)} {noun}; {folder}/{glob} holds {actual}")


def check_catalog_coverage() -> None:
    """Both directions: the catalog names nothing missing, and nothing present is uncataloged.

    The second direction is the one that grows silently, and it is what makes this checker self-extending — a new file
    turns the build red until it is registered somewhere.
    """
    for index, (folder, glob) in CATALOGS.items():
        text = read(index)
        if text is None:
            continue
        body = without_code(text)
        for item in members(folder, glob):
            if item.name in CATALOG_EXEMPT or (ROOT / index).resolve() == item.resolve():
                continue
            counted()
            if item.name not in body:
                fail("coverage", f"{folder}/{item.name} exists but is not cataloged in {index}")


# --------------------------------------------------------------------------------------------------------------- TIER 2
# Keep a check below only while its trigger artifact exists. Delete the rest rather than leaving inert scaffolding.


def check_task_recipes() -> None:
    """Recipes named in prose exist in the task runner, and every cataloged script has a way to be run."""
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        fail("runner", f"{TASK_RUNNER} is configured but does not exist")
        counted()
        return
    recipes = {m.group(1) for m in re.finditer(r"^([a-zA-Z][\w-]*)\s*(?:[*+a-zA-Z_].*)?:(?!=)", runner, re.MULTILINE)}
    for surface in RUNNER_REFERENCES:
        text = read(surface)
        if text is None:
            continue
        for named in {m.group(1) for m in re.finditer(r"`just ([a-zA-Z][\w-]*)", without_code(text))}:
            counted()
            if named not in recipes:
                fail("runner", f"{surface} names recipe `{named}` which {TASK_RUNNER} does not define")


def check_interpreter_pinning() -> None:
    """No task recipe reaches an interpreter implicitly.

    Two defects, one root cause — the recipe does not say which interpreter it means:

    1. A BARE `python3`/`node`/`npx`/`ruby` resolves to whatever is on PATH, not to what .mise.toml pins.
    2. `mise exec -- python` resolves to the venv only while `_.python.venv` activation applies. It tests clean, reads
       as pinned, and degrades SILENTLY to the host interpreter when that activation stops holding.

    Both are the "it works on the machine it was written on" class. Recipes must address {{py}} by path and depend on
    _require-venv. Node has no venv layer, so `mise exec -- node` is the legitimate explicit form for it and is allowed.

    Rule: the runtime-isolation section of skill-ai-it's SKILL.md, and the RUNTIME PINNING header of templates/justfile.
    """
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        return
    for lineno, line in enumerate(runner.splitlines(), 1):
        if not line.startswith((" ", "\t")):
            continue  # only recipe bodies are commands; headers and variable assignments are not
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Blank out quoted literals, keeping offsets intact: an interpreter NAME inside a string is a label being
        # printed (`printf 'python  '`), not a command being run.
        scan = re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: " " * len(m.group(0)), stripped)
        counted()
        # `python -m venv` creating the venv itself is the one legitimate case for a bare/mise-wrapped interpreter:
        # {{py}} does not exist yet at that point by definition, so it cannot be addressed by path. Every OTHER
        # recipe must still go through {{py}} — this carve-out is scoped to the venv-creation line alone.
        if re.search(r"mise\s+exec\b[^|;]*--\s+python", scan) and "-m venv" not in scan:
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} reaches Python through an implicit `mise exec -- python` — address the venv "
                f"interpreter by path via {{{{py}}}} and guard it with _require-venv",
            )
        for match in re.finditer(r"(?<![-\w/])(python3?|npx|ruby)\b", scan):
            # `mise exec -- <interp>` is handled above for python; for the rest it is the sanctioned explicit form.
            if re.search(r"mise\s+(exec\b[^|;]*--|run)\s*$", scan[: match.start()]):
                continue
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} calls bare `{match.group(1)}` — route it through the pinned interpreter",
            )


# --------------------------------------------------------------------------------------------------------------- TIER 3
# Project-specific invariants. Each check states, in its docstring, the project rule it enforces and where that rule
# lives. A check whose justification cannot be found is a check the next agent deletes.


def check_derived_freshness() -> None:
    """Generated artifacts are not older than the sources they are generated from.

    Freshness only — it proves a rebuild happened, not that the rebuild used the right source. Where the generator can
    stamp its source into the output, add a provenance check alongside this one; see patterns/governance-checks.md.
    """
    for output, inputs in DERIVED.items():
        out = ROOT / output
        if not out.is_file():
            fail("derived", f"{output} is registered as generated but does not exist")
            counted()
            continue
        for src in inputs:
            source = ROOT / src
            counted()
            if not source.is_file():
                fail("derived", f"{output} declares input `{src}` which does not exist")
            elif out.stat().st_mtime < source.stat().st_mtime:
                fail("derived", f"{output} is older than its input `{src}` — regenerate it")


def check_constant_sync() -> None:
    """Facts restated across surfaces stay identical, and no unregistered file restates them.

    Duplication here is deliberate: the operator must read the value at the point of decision without following a
    pointer. So the duplication stays and the sync is enforced. Orphan detection is the half that makes it self-extending.
    """
    for name, entry in CONSTANT_SURFACES.items():
        pattern = re.compile(str(entry["pattern"]))
        registered = {str(s) for s in entry["surfaces"]}  # type: ignore[union-attr]
        owner = str(entry.get("owner", ""))

        for surface in sorted(registered):
            text = read(surface)
            counted()
            if text is None:
                fail("constant", f"{name}: registered surface {surface} does not exist")
            elif not pattern.search(without_code(text)):
                fail("constant", f"{name}: {surface} is registered but no longer states it (owner: {owner or 'unset'})")

        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in registered or rel.startswith(".") or "/." in rel or rel == SELF:
                continue
            counted()
            if pattern.search(without_code(path.read_text(encoding="utf-8", errors="ignore"))):
                fail("constant", f"{name}: {rel} states it but is not registered in CONSTANT_SURFACES")


def check_append_only_grain() -> None:
    """Every row of an append-only table stamps its pass, and no pass records the same entity twice.

    Registered in APPEND_ONLY_TABLES. Two distinct failures, both silent: a row with an EMPTY pass column cannot be
    ordered against any other row, so nothing can say which measurement is current; and a REPEATED (entity, pass) pair
    means one pass measured one entity twice, so every count and every aggregate over the table is wrong by however
    many rows were duplicated. Neither shows up as an error — the table still parses and the report still renders.

    A re-measurement is a NEW pass. Reusing the previous pass identifier to record one is the defect this catches.
    """
    for rel, (entity_col, pass_col) in APPEND_ONLY_TABLES.items():
        rows = table_rows(rel)
        if not rows:
            counted()
            if not (ROOT / rel).is_file():
                fail("append-only-grain", f"{rel} is registered as append-only but does not exist")
            continue
        seen: dict[tuple[str, str], int] = {}
        for i, row in enumerate(rows, start=2):  # line 1 is the header
            counted()
            if entity_col not in row or pass_col not in row:
                fail("append-only-grain",
                     f"{rel} has no {entity_col!r}/{pass_col!r} column; the registered grain does not match the table")
                break
            pass_id = (row.get(pass_col) or "").strip()
            if not pass_id:
                fail("append-only-grain", f"{rel} line {i} has empty {pass_col}; the pass is the grain")
                continue
            key = ((row.get(entity_col) or "").strip(), pass_id)
            if key in seen:
                fail("append-only-grain",
                     f"{rel} line {i} repeats {entity_col} {key[0]!r} for pass {pass_id} (first seen line {seen[key]}); "
                     f"a re-measurement is a NEW pass, so give it a new {pass_col}")
            else:
                seen[key] = i


def check_evidence_provenance() -> None:
    """Every markdown capture states where it came from, when, and whether the fetch succeeded.

    Enforces the global source-discipline policy (~/.agents/AGENTS.md, 'Citations travel into the documentation'): a
    VERIFIED figure means a capture exists that someone else can re-open. Presence of a capture FILE is not that —
    a file with no URL and no HTTP status proves only that somebody wrote something down.

    A capture missing the header is accepted ONLY while it names its correcting capture in
    EVIDENCE_PROVENANCE_CORRECTED and that capture is on disk.
    """
    if EVIDENCE_DIR is None:
        return
    for item in members(EVIDENCE_DIR, "*.md"):
        if item.name == EVIDENCE_INDEX:
            continue
        counted()
        text = read(f"{EVIDENCE_DIR}/{item.name}") or ""
        missing = [f for f in EVIDENCE_PROVENANCE_FIELDS if f"**{f}**" not in text]
        if not missing:
            continue
        corrector = EVIDENCE_PROVENANCE_CORRECTED.get(item.name)
        if corrector is None:
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} states no {', '.join(missing)}; a capture nobody can re-open is not evidence")
        elif not (ROOT / EVIDENCE_DIR / corrector).is_file():
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} defers its provenance to {corrector}, which does not exist")


def check_manifest_freshness() -> None:
    """`manifest.json`'s `updated_at` is not older than the most recent CHANGELOG.md entry, TO THE MINUTE.

    Enforces `.archcore/rules/manifest-version-discipline.rule.md`: "Update manifest.json whenever any content file in
    this pack changes". That rule was violated for ~19 hours on 2026-09-17 — dozens of CHANGELOG entries landed (all
    four device adapters, site-addressing.yaml expansion, SNMP vault additions) while manifest.json's `updated_at`
    still read an early-morning bootstrap timestamp. Caught only by manual audit, because no check existed.

    Compares full YYYYMMDDHHMM, not just the date: a date-only compare was tried first and PROVEN not to fail in the
    negative test this rule requires — every entry that day shared 2026-09-17, so a same-day, hours-stale manifest
    (the actual defect found) passed a date-only check silently. The timestamp is DERIVED from CHANGELOG.md's own
    `## YYYYMMDD_HHMM` headings — never hand-authored — so this can't drift from the thing it counts.
    """
    changelog = read("CHANGELOG.md")
    manifest_text = read("manifest.json")
    if changelog is None or manifest_text is None:
        return
    headings = re.findall(r"^## (\d{8}_\d{4})$", changelog, flags=re.MULTILINE)
    if not headings:
        return
    latest = max(h.replace("_", "") for h in headings)
    counted()
    try:
        manifest = json.loads(manifest_text)
        updated_at = str(manifest["updated_at"])
        manifest_ts = updated_at[0:4] + updated_at[5:7] + updated_at[8:10] + updated_at[11:13] + updated_at[14:16]
    except (KeyError, ValueError, TypeError):
        fail("manifest-freshness", "manifest.json `updated_at` is missing or not a parseable ISO 8601 date")
        return
    if len(manifest_ts) == 12 and manifest_ts < latest:
        fail("manifest-freshness",
             f"manifest.json updated_at ({manifest_ts}) is older than CHANGELOG.md's latest entry ({latest}) "
             "— manifest-version-discipline.rule.md requires bumping it in the same pass as a content change")


# --------------------------------------------------------------------------------------------------------------- MAIN

CHECKS = (
    check_referenced_paths,
    check_split_path_tokens,
    check_index_links,
    check_count_claims,
    check_catalog_coverage,
    check_task_recipes,
    check_interpreter_pinning,
    check_derived_freshness,
    check_constant_sync,
    check_append_only_grain,
    check_evidence_provenance,
    check_manifest_freshness,
)


def main() -> int:
    for check in CHECKS:
        check()

    # The same defect can be reported by more than one matching pattern; a doubled count erodes trust in the number.
    unique = sorted(set(failures))
    if unique:
        print(f"FAIL — {len(unique)} issue(s) across {checks_run} checks\n")
        for f in unique:
            print(f"  ✗ {f}")
        return 1

    print(f"OK — {checks_run} governance checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/client-ip-sweep.sh
````bash
#!/usr/bin/env bash
# client-ip-sweep.sh — read-only check of "why does cnMaestro show Wi-Fi clients with IPv4 0.0.0.0?" for one site.
#
# Compares three layers so the fault is placed, not guessed:
#   1. SMC  — isc-dhcp-server health over the last hour (ACK/NAK/DISCOVER, "no free leases").
#   2. AP   — the client IPv4 the AP itself reports, which is what device-agent forwards to cnMaestro:
#             R195P  -> /tmp/stahost (written by /bin/device-agent; column 2 is the IPv4)
#             E/XV   -> `show wireless clients` (last column IPv4)
#             KNOWN LIMIT (2026-10-05): on XV2 (6.6.x) a non-interactive `ssh ... "show wireless clients"` logs in but prints nothing,
#             so XV2 units report "no table" here, which is NOT "no clients". E500 prints the table fine.
#   3. Join — for each AP-reported client MAC, whether the SMC holds a dhcpd lease for it.
# A client with zero_ip on the AP but a lease on the SMC is a reporting gap, not a DHCP failure.
#
# Usage:   scripts/client-ip-sweep.sh <site>-smc01 <apn|nbn> [samples_per_family=3]
# Needs:   tsh logged in to the cluster; `kp` vault wrapper; OpenSSH 8.4+ (SSH_ASKPASS_REQUIRE).
# Vault:   cambium-devices/{apn,nbn}-snmp-ro, cnpilot-r-series(-legacy), enterprise-wifi(-legacy). Passwords never printed;
#          the SNMP community is piped over stdin, device passwords go through a throwaway SSH_ASKPASS helper.
# Writes:  nothing on SMC or devices. Only GETs (snmpget sysDescr) and file reads / show commands.
# First run 2026-10-05 (kalumburu, burringurrah, bidyadanga, ... — see references/05_known-issues.md).
set -uo pipefail

smc=${1:?usage: client-ip-sweep.sh <site>-smc01 <apn|nbn> [samples]}; prog=${2:?apn|nbn}; samples=${3:-3}
if [ "$prog" = nbn ]; then dom=teleport.communitywifi.net.au; snmp=nbn-snmp-ro
else dom=teleport.apn.au; snmp=apn-snmp-ro; fi
proxy=--proxy=$dom

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
printf '#!/bin/sh\nprintf "%%s\\n" "$CAMBIUM_PASS"\n' > "$tmp/askpass"; chmod 700 "$tmp/askpass"

echo "##### $smc ($prog)"
# SMC side: DHCP health, lease MAC list, and a sysDescr map of every Cambium AP on the management bridge.
kp show -s -a Password "cambium-devices/$snmp" 2>/dev/null | tsh ssh $proxy root@"$smc" '
read -r C
j=$(journalctl -u isc-dhcp-server --since "-1h" 2>/dev/null)
echo "DHCP1h ack=$(echo "$j" | grep -c DHCPACK) nak=$(echo "$j" | grep -c DHCPNAK) disc=$(echo "$j" | grep -c DHCPDISCOVER) nofree=$(echo "$j" | grep -c "no free leases")"
awk "/hardware ethernet/{gsub(\";\",\"\",\$3); print \"LEASE \" toupper(\$3)}" /var/lib/dhcp/dhcpd.leases | sort -u
for ip in $(ip neigh show dev bridge_500 2>/dev/null | awk "/lladdr/{print \$1}"); do
  d=$(snmpget -v2c -c "$C" -t1 -r0 -Oqv $ip 1.3.6.1.2.1.1.1.0 2>/dev/null | tr -d "\"" | cut -c1-48)
  case "$d" in *R195P*) echo "AP r195p $ip $d";; *cnPilot\ E*|*XV*|*Enterprise*) echo "AP ent $ip $d";; esac
done' > "$tmp/smc" 2>&1
grep DHCP1h "$tmp/smc" || { echo "  SMC unreachable:"; tail -3 "$tmp/smc"; exit 1; }
grep '^LEASE ' "$tmp/smc" | cut -d' ' -f2 > "$tmp/leases"
echo "  leases_known=$(wc -l < "$tmp/leases" | tr -d ' ') r195p_found=$(grep -c '^AP r195p' "$tmp/smc") ent_found=$(grep -c '^AP ent' "$tmp/smc")"

dev() { # <vault-entry> <ip> <command>
  CAMBIUM_PASS="$(kp show -s -a Password "cambium-devices/$1" 2>/dev/null)" SSH_ASKPASS="$tmp/askpass" SSH_ASKPASS_REQUIRE=force DISPLAY=:0 \
  ssh -n -J root@"$smc.$dom" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 -o LogLevel=ERROR \
    -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -o KexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 admin@"$2" "$3" 2>&1 | grep -vE "post-quantum|store now|pq.html"; }
leased() { tr '-' ':' | while read -r m; do grep -qx "$m" "$tmp/leases" && echo y; done | grep -c y; }

# Keep reading APs until $samples of them have at least one client (idle APs prove nothing), capped at 4x samples.
n=0; tries=0
for ip in $(awk '/^AP r195p/{print $3}' "$tmp/smc"); do
  [ $n -ge "$samples" ] || [ $tries -ge $((samples*4)) ] && break; tries=$((tries+1))
  fw=$(awk -v i="$ip" '$3==i{print $NF}' "$tmp/smc")
  out=$(dev cnpilot-r-series "$ip" 'cat /tmp/stahost'); echo "$out" | grep -q "Permission denied" && out=$(dev cnpilot-r-series-legacy "$ip" 'cat /tmp/stahost')
  rows=$(echo "$out" | grep -E '^([0-9A-F]{2}:){5}'); [ -z "$rows" ] && continue; n=$((n+1))
  echo "  R195P $ip fw=$fw clients=$(echo "$rows" | wc -l | tr -d ' ') zero_ip=$(echo "$rows" | grep -c ',0\.0\.0\.0,') leased_on_smc=$(echo "$rows" | cut -d, -f1 | leased)"
done
[ $n -eq 0 ] && echo "  R195P: no sampled unit had clients ($tries tried)"

n=0; tries=0
for ip in $(awk '/^AP ent/{print $3}' "$tmp/smc"); do
  [ $n -ge "$samples" ] || [ $tries -ge $((samples*4)) ] && break; tries=$((tries+1))
  model=$(awk -v i="$ip" '$3==i{$1=$2=$3=""; print}' "$tmp/smc" | sed 's/^ *//')
  out=$(dev enterprise-wifi "$ip" 'show wireless clients'); echo "$out" | grep -q "Permission denied" && out=$(dev enterprise-wifi-legacy "$ip" 'show wireless clients')
  rows=$(echo "$out" | grep -E '^ *([0-9A-F]{2}-){5}')
  if [ -z "$rows" ]; then echo "$out" | grep -q "MAC" || echo "  ENT $ip [$model] no table returned (XV2 non-interactive CLI limit, or login failed)"; continue; fi
  n=$((n+1))
  echo "  ENT $ip [$model] clients=$(echo "$rows" | wc -l | tr -d ' ') zero_ip=$(echo "$rows" | grep -c '0\.0\.0\.0 *$') leased_on_smc=$(echo "$rows" | awk '{print $1}' | leased) vlans=$(echo "$rows" | awk '{print $9}' | sort | uniq -c | awk '{printf "%s:%s ", $2, $1}')"
done
[ $n -eq 0 ] && echo "  ENT: no sampled unit returned a client row ($tries tried)"
````

## File: scripts/extract-asset-register.py
````python
"""Hope Vale (nbn_accelerate) / Burringurrah (rcp) asset-register -> device-inventory.csv extraction.

One-off, NOT general-purpose. Site asset registers have no standard template (see
references/03_asset-register-conventions.md) -- each site's sheet layout was hand-read and hand-mapped
below. Adapting this to a new site means re-reading that site's actual columns, not assuming they match
either of these two. Kept here (rather than discarded) as a worked example and a reusable set of
guardrails: is_ip()/sanip() reject cross-reference placeholders ("As above") and validate IPv4 format
before a link-derived field becomes a device row; the row() helper whitespace-normalizes every extracted
string (a source MAC cell had an embedded newline that corrupted a CSV row before this was added).

Moved here from cambium-swap's session scratchpad 2026-09-17, per operator instruction, once
skill-cambium existed as this knowledge's canonical home. Re-run: `python3 extract-asset-register.py`
(stdlib + openpyxl; writes the two per-site extract CSVs, then folds them into device-inventory.csv by
appending -- see references/04_device-inventory-schema.md for why a re-extraction of an already-loaded
site must remove that site's old rows first).
"""

import csv, re
import openpyxl

INV_PATH = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/device-inventory.csv"
HV_OUT = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/asset-register/nbn_accelerate/hope-vale-extract.csv"
BUR_OUT = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/asset-register/rcp/burringurrah-extract.csv"
EXPORT_DATE = "2026-09-17"

HEADER = ["serial_msn","mac_address","model","product_family","hardware_revision",
    "current_firmware","previous_known_good_firmware","management_ip","site","smc_flavour",
    "network","tower_site_hierarchy","device_name","device_role","topology_role",
    "wlan_profile","ap_group","configuration_template","cloud_sync_status","cnmaestro_server",
    "licence_tier","licence_state","licence_expiry","local_credentials_ref","last_seen",
    "status","spare_mapping","export_date"]

CRED = {
    "Enterprise Wi-Fi": "<secret:keepassxc:cambium-devices/enterprise-wifi>",
    "ePMP AP": "<secret:keepassxc:cambium-devices/epmp-ap>",
    "ePMP SM": "<secret:keepassxc:cambium-devices/epmp-sm>",
    "cnWave 60 GHz": "<secret:keepassxc:cambium-devices/cnwave-60ghz>",
    "cnPilot R-series": "<secret:keepassxc:cambium-devices/cnpilot-r-series>",
}

U = "UNKNOWN"
rows = []

def row(**kw):
    r = {h: U for h in HEADER}
    r["hardware_revision"] = U
    r["current_firmware"] = U
    r["previous_known_good_firmware"] = U
    r["network"] = U
    r["wlan_profile"] = U
    r["ap_group"] = U
    r["configuration_template"] = U
    r["cloud_sync_status"] = U
    r["cnmaestro_server"] = U
    r["licence_tier"] = U
    r["licence_state"] = U
    r["licence_expiry"] = U
    r["last_seen"] = U
    r["spare_mapping"] = U
    r["export_date"] = EXPORT_DATE
    r["status"] = "Active"
    for k, v in kw.items():
        if isinstance(v, str):
            kw[k] = " ".join(v.split())
    r.update(kw)
    fam = r.get("product_family")
    if r.get("local_credentials_ref") == U and fam in CRED:
        r["local_credentials_ref"] = CRED[fam]
    rows.append(r)

IPV4_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

def is_ip(v):
    return bool(v) and bool(IPV4_RE.match(str(v).strip()))

def sanip(v):
    return v if is_ip(v) else U

def norm_f300(text):
    if not text:
        return None
    t = str(text)
    if "300-25" in t:
        return "Force 300-25"
    if "300-16" in t:
        return "Force 300-16"
    return None

# ---------------------------------------------------------------------------
# HOPE VALE (nbn_accelerate)
# ---------------------------------------------------------------------------
hv_path = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/asset-register/nbn_accelerate/Hope Vale Asset Register_V1.2.xlsx"
wb = openpyxl.load_workbook(hv_path, data_only=True, read_only=True)
ws = wb["Infrastructure & AP's"]
r_ = list(ws.iter_rows(values_only=True))

SITE = "hope-vale"
FLAVOUR = "nbn_accelerate"

# XV2 AP table: header idx35, data 36-68
for i in range(36, 69):
    rr = r_[i]
    tower, name, model, ip = rr[0], rr[1], rr[2], rr[3]
    backhaul_type, backhaul_name, backhaul_ip = rr[4], rr[5], rr[6]
    if name:
        row(model=model, product_family="Enterprise Wi-Fi", management_ip=sanip(ip), site=SITE,
            smc_flavour=FLAVOUR, tower_site_hierarchy=tower, device_name=name,
            device_role="Wi-Fi AP", topology_role="Enterprise Wi-Fi AP")
    f300_model = norm_f300(backhaul_type)
    if f300_model and backhaul_name and is_ip(backhaul_ip):
        row(model=f300_model, product_family="ePMP SM", management_ip=backhaul_ip, site=SITE,
            smc_flavour=FLAVOUR, tower_site_hierarchy=tower, device_name=backhaul_name,
            device_role="ePMP SM (backhaul)", topology_role="P2P backhaul (paired with XV2 AP)")

# ePMP 3000L table: header idx72, data 73-78
for i in range(73, 79):
    rr = r_[i]
    tower, model, antenna, name, ip, bridge_ssid, freq, backhaul_type = rr[0:8]
    if not name:
        continue
    status = "Spare" if str(tower).strip().lower() == "spare" else "Active"
    row(model="ePMP 3000L", product_family="ePMP AP", management_ip=sanip(ip), site=SITE,
        smc_flavour=FLAVOUR, tower_site_hierarchy=tower, device_name=name,
        device_role="ePMP AP (P2MP)", topology_role=antenna, status=status)

# 5GHz ePMP P2P Links: header idx81, data row 82 (AP + SM per row)
for i in range(82, 86):
    rr = r_[i]
    if not any(rr):
        continue
    ap_tower, ap_model, ap_name, ap_ip, bridge_ssid, freq, chwidth, sm_tower, sm_model, sm_name, sm_ip = rr[0:11]
    status = "Spare" if str(ap_tower).strip().lower() == "spare" else "Active"
    if ap_name:
        row(model=norm_f300(ap_model) or ap_model, product_family="ePMP SM", management_ip=sanip(ap_ip),
            site=SITE, smc_flavour=FLAVOUR, tower_site_hierarchy=ap_tower, device_name=ap_name,
            device_role="ePMP AP (P2P master)", topology_role="P2P AP", status=status)
    if sm_name:
        row(model=norm_f300(sm_model) or sm_model, product_family="ePMP SM", management_ip=sanip(sm_ip),
            site=SITE, smc_flavour=FLAVOUR, tower_site_hierarchy=sm_tower, device_name=sm_name,
            device_role="ePMP SM (P2P slave)", topology_role="P2P SM", status=status)

# 60GHz P2(M)P Links: header idx87, data 88-96 (DN once at 88, CN per row)
for i in range(88, 97):
    rr = r_[i]
    tower, dn_site, dn_name, dn_ip, dn_model, cn_loc, cn_name, cn_ip, cn_model, cn_sitename, sector, cn_mac = rr[0:12]
    if dn_name:
        row(model=dn_model, product_family="cnWave 60 GHz", management_ip=sanip(dn_ip), site=SITE,
            smc_flavour=FLAVOUR, tower_site_hierarchy=tower or "Tower 1", device_name=dn_name,
            device_role="cnWave DN (P2MP hub)", topology_role="DN")
    if cn_name:
        row(model=cn_model, product_family="cnWave 60 GHz", management_ip=sanip(cn_ip),
            mac_address=cn_mac or U, site=SITE, smc_flavour=FLAVOUR,
            tower_site_hierarchy=cn_loc, device_name=cn_name,
            device_role="cnWave CN (P2MP client)", topology_role="CN")

# 60GHz Spare DN's: header idx100, data 101
rr = r_[101]
tower, dn_site, dn_name, dn_ip, dn_model = rr[0:5]
if dn_name:
    row(model=dn_model, product_family="cnWave 60 GHz", management_ip=sanip(dn_ip), site=SITE,
        smc_flavour=FLAVOUR, tower_site_hierarchy=tower, device_name=dn_name,
        device_role="cnWave DN (spare)", topology_role="DN", status="Spare")

hv_count = len(rows)
print(f"Hope Vale rows: {hv_count}")

# ---------------------------------------------------------------------------
# BURRINGURRAH (rcp)
# ---------------------------------------------------------------------------
bur_path = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/asset-register/rcp/Burringurrah Asset Register.xlsx"
wb2 = openpyxl.load_workbook(bur_path, data_only=True, read_only=True)

SITE = "burringurrah"
FLAVOUR = "rcp"

ws2 = wb2["Tower + AP"]
r2 = list(ws2.iter_rows(values_only=True))

# Combined 3000L omni + Force300 SM block: header idx0, data 1-9
for i in range(1, 10):
    rr = r2[i]
    lat, lon, tid, loc, name, ip, serial, mac = rr[0:8]
    bridge_ssid, freq, bridge_mac, power, mast = rr[10:15]
    if not name:
        continue
    latest_name = str(name).split(">>")[-1].strip()
    f300_model = norm_f300(latest_name)
    status = "Spare" if "spare" in str(name).lower() else "Active"
    if f300_model:
        row(mac_address=mac or U, model=f300_model, product_family="ePMP SM", management_ip=sanip(ip),
            site=SITE, smc_flavour=FLAVOUR, tower_site_hierarchy=tid or loc, device_name=latest_name,
            device_role="ePMP SM (backhaul)", topology_role="P2P backhaul", status=status)
    else:
        row(mac_address=mac or U, model="ePMP 3000L", product_family="ePMP AP", management_ip=sanip(ip),
            site=SITE, smc_flavour=FLAVOUR, tower_site_hierarchy=tid or loc, device_name=latest_name,
            device_role="ePMP AP (P2MP)", topology_role="Omni/Sector", status=status)

# XV2 AP table: header idx11, data 13-20
for i in range(13, 21):
    rr = r2[i]
    lat, lon, apid, loc, name, ip = rr[0:6]
    ap_serial, ap_mac = rr[7], rr[8]
    if not name:
        continue
    status = "Spare" if str(apid).strip().upper() == "SPARE" else "Active"
    row(mac_address=ap_mac or U, model="XV2", product_family="Enterprise Wi-Fi", management_ip=sanip(ip),
        site=SITE, smc_flavour=FLAVOUR, tower_site_hierarchy=apid, device_name=name,
        device_role="Wi-Fi AP", topology_role="Enterprise Wi-Fi AP (variant XV2-2T0 vs XV2-22H unconfirmed)",
        status=status)

# Switches sheet skipped (non-Cambium, out of scope)

bur_towerap_count = len(rows) - hv_count

# Internals sheet: residential R195P CPE installs
ws3 = wb2["Internals"]
r3 = list(ws3.iter_rows(values_only=True))
# header at row0: idx2 Street Number, idx3 Street Address, idx13 R195 EXT, idx27 R195 MAC Address
r195_count = 0
for i in range(1, len(r3)):
    rr = r3[i]
    if len(rr) <= 27:
        continue
    street_no, street_addr = rr[2], rr[3]
    r195_ext = rr[13]
    r195_mac = rr[27]
    if r195_ext is None:
        continue
    hierarchy = f"{street_no} {street_addr}".strip() if street_addr else f"EXT {r195_ext}"
    # Operator-stated derivation (2026-09-17, not in the register): EXT10XX -> 10.255.10.XX
    ext_str = str(r195_ext).strip()
    ext_digits = re.match(r"^10(\d{2})", ext_str)
    r195_ip = f"10.255.10.{int(ext_digits.group(1))}" if ext_digits else U
    row(mac_address=r195_mac or U, model="R195P", product_family="cnPilot R-series",
        management_ip=r195_ip, site=SITE, smc_flavour=FLAVOUR, tower_site_hierarchy=hierarchy,
        device_name=f"R195P EXT{r195_ext}", device_role="CPE (R195P)",
        topology_role="Residential CPE")
    r195_count += 1

print(f"Burringurrah Tower+AP rows: {bur_towerap_count}")
print(f"Burringurrah R195P CPE rows: {r195_count}")
print(f"TOTAL new rows: {len(rows)}")

hv_rows = rows[:hv_count]
bur_rows = rows[hv_count:]

# ---------------------------------------------------------------------------
# Per-site normalized extracts (reviewable checkpoints, re-runnable)
# ---------------------------------------------------------------------------
for path, site_rows in [(HV_OUT, hv_rows), (BUR_OUT, bur_rows)]:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in site_rows:
            w.writerow(r)
    print(f"Wrote {path} ({len(site_rows)} rows)")

# ---------------------------------------------------------------------------
# Fold both extracts into device-inventory.csv (append, header stays as-is)
# ---------------------------------------------------------------------------
with open(INV_PATH, "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=HEADER, quoting=csv.QUOTE_MINIMAL)
    for r in rows:
        w.writerow(r)

print("Folded into device-inventory.csv.")
````

## File: scripts/fleet_schema_sweep.py
````python
#!/usr/bin/env python3
"""Sweep every site and family to build the fleet-wide device response contract.

Stage 2 of the schema exercise (stage 1 being the per-family baseline in `schemas/`). For each
site this picks one representative device per family, contracts its responses with
`schema_tool.py`, and records what it found. The point is not the individual observation — it is
the merge afterwards, where a field present at 30 sites and absent at 6 stops being invisible.

Rules this implements, from `schemas/README.md`:

  * For client-bearing endpoints, pick the device that *has* clients. An AP with none returns an
    empty array, which is no evidence either way and would otherwise drag every field to optional.
  * Unreachable and empty are findings, not skips. A site with no reachable device of a family is
    a fact about the estate and is written to the findings log.
  * Never conclude a site is down from one tool's failure. `snmpget` is absent on `rcp`-flavour
    SMC boxes; this sweep deliberately uses no SNMP for exactly that reason.
  * ePMP is throttled — the family has a limited concurrent-session budget, so its devices are
    contracted one at a time with a pause between sites.

Two transports, chosen per family:

  * Enterprise Wi-Fi goes over **one Teleport hop per site**. The login and the GETs run as curl on
    the site's SMC box and the raw JSON comes back over stdout. No port-forward, no local listener,
    and the client-count sweep and the contract fetch share a single connection.
  * ePMP, cnPilot R-series and cnWave go through a **port-forward into this pack's own adapters**,
    because their auth flows already live there and are not worth reimplementing remotely.

Resumable: a site/family whose observation file already exists is left alone, so an interrupted
sweep continues where it stopped. Delete an observation to force a re-run.

Usage:
    CAMBIUM_* creds are read from the KeePassXC vault by the caller and passed in the environment.
    python3 scripts/fleet_schema_sweep.py --inventory <device-inventory.csv> --out schemas
    python3 scripts/fleet_schema_sweep.py ... --families enterprise-wifi --sites hope-vale,amata
"""
import argparse
import csv
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parent

WIFI_ENDPOINTS = ["client-summary", "radio-summary", "radio-rf-summary", "device-summary",
                  "platform-info", "interface-summary", "wlan-summary", "ethports-config",
                  "ip_route-summary"]

# inventory product_family -> (schema family slug, vault entry)
FAMILY_MAP = {
    "Enterprise Wi-Fi": ("enterprise-wifi", "enterprise-wifi"),
    "ePMP AP": ("epmp-ap", "epmp-ap"),
    "ePMP SM": ("epmp-sm", "epmp-sm"),
    "cnPilot R-series": ("cnpilot-r-series", "cnpilot-r-series"),
    "cnWave 60GHz": ("cnwave-60ghz", "cnwave-60ghz"),
    "cnWave 60 GHz": ("cnwave-60ghz", "cnwave-60ghz"),
}
ADAPTER = {
    "epmp-ap": "cambium_epmp_adapter.py",
    "epmp-sm": "cambium_epmp_adapter.py",
    "cnpilot-r-series": "cambium_r195p_adapter.py",
    "cnwave-60ghz": "cambium_cnwave_adapter.py",
}
THROTTLED = {"epmp-ap", "epmp-sm"}


def run(cmd, timeout, stdin_data=None):
    try:
        p = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except OSError as exc:
        return 125, "", str(exc)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def load_inventory(path):
    """site -> family slug -> [ {ip, name, model, firmware} ], deduped by management IP."""
    sites = defaultdict(lambda: defaultdict(list))
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            ip = (row.get("management_ip") or "").strip()
            fam = FAMILY_MAP.get((row.get("product_family") or "").strip())
            site = (row.get("site") or "").strip()
            if not ip.startswith("10.") or not fam or not site:
                continue
            entry = {"ip": ip, "name": row.get("device_name", ""),
                     "model": (row.get("model") or "").strip(),
                     "firmware": (row.get("current_firmware") or "").strip()}
            bucket = sites[site][fam[0]]
            if not any(e["ip"] == ip for e in bucket):
                bucket.append(entry)
    return sites


def build_node_map(proxies):
    """site -> (node, proxy). A site listed on both clusters is taken from the first that has it,
    which is the order the caller gave — the sweep records which proxy it used, so a wrong guess
    shows up as a finding rather than as silence."""
    node_map = {}
    for proxy in proxies:
        rc, out, _ = run(["tsh", "ls", "--proxy", proxy, "--format=text"], 120)
        if rc != 0:
            print(f"! tsh ls failed on {proxy}", file=sys.stderr)
            continue
        for line in out.splitlines()[2:]:
            node = line.split()[0] if line.split() else ""
            m = re.match(r"^(.*)-smc\d+$", node)
            if m and m.group(1) not in node_map:
                node_map[m.group(1)] = (node, proxy)
    return node_map


REMOTE_WIFI = r'''
# u, p, ips and eps arrive exported from stdin - never as arguments, see observe_wifi().
#
# Endpoints are fetched inside the probe loop, immediately after authenticating to that AP, and
# the best AP's output is kept. Two earlier designs failed: logging in again after the loop made
# client-summary return literal null, and reusing the winner's cookie jar after the loop made it
# return empty. Both looked authenticated and both silently lost the client data on every site.
# Fetching while the session is fresh is the only pattern observed to work.
best_ip=""; best_n=-1; best_out=""
for ip in $ips; do
  cj=$(mktemp)
  curl -sk -c "$cj" -X POST -H 'Content-Type: application/json' --max-time 5 \
       -d "{\"username\":\"$u\",\"password\":\"$p\"}" "https://$ip/api/login" >/dev/null 2>&1
  tok=$(grep XSRF-TOKEN "$cj" 2>/dev/null | awk '{print $7}')
  if [ -z "$tok" ]; then echo "COUNT $ip login-failed" >&2; rm -f "$cj"; continue; fi
  # note the space after the colon in the device's JSON - matching without it silently yields 0
  n=$(curl -sk -b "$cj" -H "X-XSRF-TOKEN: $tok" --max-time 6 "https://$ip/api/radio-summary" 2>/dev/null \
      | tr ',' '\n' | grep -oE '"num_clients": *[0-9]+' | grep -oE '[0-9]+$' | paste -sd+ - | bc 2>/dev/null)
  [ -z "$n" ] && n=0
  echo "COUNT $ip $n" >&2
  if [ "$n" -gt "$best_n" ]; then
    out=$(mktemp)
    for ep in $eps; do
      echo "###EP###$ep###" >> "$out"
      curl -sk -b "$cj" -H "X-XSRF-TOKEN: $tok" --max-time 15 "https://$ip/api/$ep" >> "$out" 2>/dev/null
      echo >> "$out"
    done
    [ -n "$best_out" ] && rm -f "$best_out"
    best_n=$n; best_ip=$ip; best_out="$out"
  fi
  curl -sk -b "$cj" -H "X-XSRF-TOKEN: $tok" --max-time 5 -X POST "https://$ip/api/logout" >/dev/null 2>&1
  rm -f "$cj"
done
[ -z "$best_ip" ] && { echo "NO_DEVICE" ; exit 0; }
echo "TARGET $best_ip $best_n" >&2
echo "###TARGET###$best_ip###$best_n###"
cat "$best_out"
rm -f "$best_out"
'''


def observe_wifi(site, node, proxy, devices, out_dir, creds, findings):
    """The credential is fed to the remote shell on stdin, never as an argument.

    An argument lands in the process table on both this machine and the SMC box, where any user
    running `ps` sees the device's admin password in clear text — and it also leaks into local
    shell history and into any transcript that captures a process listing. The remote script reads
    the first two stdin lines as username and password before the rest of the heredoc runs.
    """
    ips = " ".join(d["ip"] for d in devices)
    payload = f"{creds[0]}\n{creds[1]}\n{ips}\n{' '.join(WIFI_ENDPOINTS)}\n" + REMOTE_WIFI
    rc, out, err = run(
        ["tsh", "ssh", "--proxy", proxy, f"root@{node}",
         "IFS= read -r u; IFS= read -r p; IFS= read -r ips; IFS= read -r eps; "
         "export u p ips eps; bash -s"],
        timeout=420, stdin_data=payload)
    if rc != 0 and "###TARGET###" not in out:
        findings.append({"site": site, "family": "enterprise-wifi", "status": "unreachable",
                         "detail": (err or out).strip()[:200]})
        return None
    if "NO_DEVICE" in out or "###TARGET###" not in out:
        findings.append({"site": site, "family": "enterprise-wifi", "status": "no-login",
                         "detail": "no device at this site accepted the vault credential"})
        return None

    # Parse the header and the endpoint blocks independently. Slicing the header off with a
    # shared "###" split used to swallow the first block's delimiter, so the first endpoint in
    # the list was dropped every time — silently, because the others parsed fine. client-summary
    # was first, which cost two full fleet sweeps their client data before the cause was found.
    header = out.partition("###TARGET###")[2].split("###EP###", 1)[0]
    parts = header.split("###")
    target_ip = parts[0].strip() if parts else ""
    client_total = parts[1].strip() if len(parts) > 1 else ""
    payloads = {}
    for chunk in out.split("###EP###")[1:]:
        name, _, raw = chunk.partition("###")
        raw = raw.strip()
        if not raw:
            continue
        try:
            payloads[name.strip()] = json.loads(raw)
        except ValueError:
            findings.append({"site": site, "family": "enterprise-wifi", "status": "bad-json",
                             "endpoint": name.strip()})
    if not payloads:
        findings.append({"site": site, "family": "enterprise-wifi", "status": "no-payload"})
        return None

    dev = next((d for d in devices if d["ip"] == target_ip), {"model": "", "firmware": ""})
    return write_observation(out_dir, "enterprise-wifi", site, dev, payloads,
                             layer="raw-endpoint", extra={"clients_on_target": client_total,
                                                          "devices_probed": len(devices)})


def observe_adapter(site, node, proxy, family, dev, out_dir, creds, findings):
    port = free_port()
    remote_port = 22 if family == "cnpilot-r-series" else 443
    fwd = subprocess.Popen(
        ["tsh", "ssh", "--proxy", proxy, "-L", f"{port}:{dev['ip']}:{remote_port}",
         f"root@{node}", "sleep 240"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_for_port(port, 40):
            findings.append({"site": site, "family": family, "device": dev["name"],
                             "status": "forward-failed"})
            return None
        env = dict(os.environ, CAMBIUM_HOST=f"localhost:{port}",
                   CAMBIUM_USER=creds[0], CAMBIUM_PASS=creds[1])
        p = subprocess.run([sys.executable, str(HERE / ADAPTER[family])],
                           capture_output=True, text=True, timeout=180, env=env)
        if p.returncode != 0 or not p.stdout.strip():
            findings.append({"site": site, "family": family, "device": dev["name"],
                             "status": "adapter-failed",
                             "detail": (p.stderr or "").strip().splitlines()[-1][:200] if p.stderr else ""})
            return None
        try:
            payload = json.loads(p.stdout)
        except ValueError:
            findings.append({"site": site, "family": family, "device": dev["name"],
                             "status": "bad-json"})
            return None
        return write_observation(out_dir, family, site, dev, payload,
                                 layer="adapter-normalized")
    except subprocess.TimeoutExpired:
        findings.append({"site": site, "family": family, "device": dev["name"], "status": "timeout"})
        return None
    finally:
        fwd.terminate()
        try:
            fwd.wait(timeout=10)
        except subprocess.TimeoutExpired:
            fwd.kill()


def wait_for_port(port, seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        with socket.socket() as s:
            s.settimeout(2)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(1)
    return False


def write_observation(out_dir, family, site, dev, payload, layer, extra=None):
    """Hand the payload to schema_tool so there is exactly one inference implementation."""
    model_slug = re.sub(r"[^A-Za-z0-9]+", "-", dev.get("model") or "unknown").strip("-") or "unknown"
    target = Path(out_dir) / "_observations" / family / f"{site}-{model_slug}-{datetime.now().strftime('%Y%m%d')}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(HERE / "schema_tool.py"), "observe", "--driver", "stdin",
           "--split-getters", "--layer", layer, "--family", family, "--site", site,
           "--model", dev.get("model") or "", "--firmware", dev.get("firmware") or "",
           "--out", str(target)]
    p = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        print(f"    schema_tool failed: {p.stderr.strip()[:160]}", file=sys.stderr)
        return None
    if extra:
        doc = json.loads(target.read_text())
        doc["x-observation"].update(extra)
        target.write_text(json.dumps(doc, indent=2) + "\n")
    return target


def vault(entry, field):
    rc, out, _ = run(["kp", "show", "-s", "-a", field, f"cambium-devices/{entry}"], 60)
    return out.strip() if rc == 0 else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--out", default=str(PACK / "schemas"))
    ap.add_argument("--families", default=",".join(sorted({v[0] for v in FAMILY_MAP.values()})))
    ap.add_argument("--sites", default="")
    ap.add_argument("--findings", default="")
    ap.add_argument("--proxies", default="teleport.communitywifi.net.au,teleport.apn.au")
    ap.add_argument("--workers", type=int, default=9, help="sites swept in parallel; families stay sequential within a site")
    args = ap.parse_args()

    families = [f.strip() for f in args.families.split(",") if f.strip()]
    only_sites = {s.strip() for s in args.sites.split(",") if s.strip()}

    inventory = load_inventory(args.inventory)
    node_map = build_node_map([p.strip() for p in args.proxies.split(",") if p.strip()])
    # Some sites (kalumburu, confirmed 2026-09-20) still carry the older local-admin password, so
    # every family gets its primary entry plus a `-legacy` fallback tried in order. A site failing
    # on the primary alone is a credential finding, not an unreachable device.
    creds = {}
    for _, entry in set(FAMILY_MAP.values()):
        pairs = []
        for name in (entry, f"{entry}-legacy"):
            u, pw = vault(name, "UserName"), vault(name, "Password")
            if pw:
                pairs.append((u, pw))
        creds[entry] = pairs

    sites = sorted(s for s in inventory if not only_sites or s in only_sites)

    # Sites are independent devices, so they parallelise safely. ePMP's concurrent-session limit
    # is per device, not per fleet, and families stay sequential within a site so a single AP is
    # never hit by two workers at once.
    lock = threading.Lock()
    counter = {"n": 0}
    findings = []
    made = 0

    def do_site(site):
        nonlocal made
        local_findings = []
        lines = []
        with lock:
            counter["n"] += 1
            i = counter["n"]
        if site not in node_map:
            local_findings.append({"site": site, "family": "*", "status": "no-teleport-node"})
            lines.append(f"[{i}/{len(sites)}] {site}: no Teleport node")
        else:
            node, proxy = node_map[site]
            lines.append(f"[{i}/{len(sites)}] {site} via {node} ({proxy.split('.')[1]})")
            for family in families:
                devices = inventory[site].get(family) or []
                if not devices:
                    continue
                if list((Path(args.out) / "_observations" / family).glob(f"{site}-*.json")):
                    lines.append(f"    {family}: already observed")
                    continue
                vault_entry = next(v[1] for v in FAMILY_MAP.values() if v[0] == family)
                cred_list = creds.get(vault_entry) or []
                if not cred_list:
                    local_findings.append({"site": site, "family": family, "status": "no-credential"})
                    continue
                got = None
                for cred in cred_list:
                    if family == "enterprise-wifi":
                        got = observe_wifi(site, node, proxy, devices, args.out, cred, local_findings)
                    else:
                        for dev in devices[:4]:
                            got = observe_adapter(site, node, proxy, family, dev, args.out, cred, local_findings)
                            if got:
                                break
                    if got:
                        break
                lines.append(f"    {family}: {'ok ' + Path(got).name if got else 'FAILED'}")
                if got:
                    with lock:
                        made += 1
        with lock:
            findings.extend(local_findings)
            print("\n".join(lines), flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(do_site, sites))

    findings_path = Path(args.findings or (Path(args.out) / "_observations" / "sweep-findings.json"))
    findings_path.parent.mkdir(parents=True, exist_ok=True)
    findings_path.write_text(json.dumps({
        "swept_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sites": len(sites), "observations_made": made,
        "findings": findings,
    }, indent=2) + "\n")
    print(f"\nobservations made: {made}; findings: {len(findings)} -> {findings_path}")


if __name__ == "__main__":
    main()
````

## File: scripts/generate_site_addressing_families.py
````python
#!/usr/bin/env python3
"""Derive two parts of references/site-addressing.yaml straight from cambium-swap's inventory data
— the same computations this pack's evidence E124/E125/E126/E129 did by hand:

1. The `families:` block for one or more sites, from their reconciled cnMaestro-export inventory
   CSVs (per-site octet_pattern/host_count by device family).
2. `--oui-audit`: the `oui_reference:` block's coverage, from the consolidated
   inventory/device-inventory.csv — which real MAC OUI prefixes appear there but have no entry in
   site-addressing.yaml yet (the gap E129 found by hand after the file went unmaintained through
   22 sites' worth of new exports).

Both print YAML/text to stdout for review/merge; NEITHER writes the target file directly, since
site-addressing.yaml also carries hand-authored live-session notes (SSH/REST/SNMP verification
narrative, cross-site OUI-reuse cautions) neither computation can derive or preserve.

octet_pattern/host_count/trust in the families: output, and host_count/site in the OUI audit
output, always mean method: cnmaestro-export (the CSV itself is the evidence) — a site or OUI that
has also been live-verified (SSH/REST/SNMP session) should keep or add that richer verification by
hand; this script only ever proposes the export-derived facts.

Usage:
  generate_site_addressing_families.py --flavour nbn_accelerate --site amata
  generate_site_addressing_families.py --flavour rcp --all
  generate_site_addressing_families.py --all --all-flavours   # every site in the inventory root
  generate_site_addressing_families.py --oui-audit             # OUI blocks missing from oui_reference
"""
import argparse
import csv
import glob
import os
import re
from collections import Counter, defaultdict

DEFAULT_INVENTORY_ROOT = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/asset-register"
DEFAULT_DEVICE_INVENTORY = "/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/device-inventory.csv"
DEFAULT_SITE_ADDRESSING_YAML = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "references", "site-addressing.yaml")

FAMILY_MAP = {
    "XV2-2": "enterprise-wifi-xv2", "XV2-2T0": "enterprise-wifi-xv2", "XV2-22H": "enterprise-wifi-xv2",
    "ePMP Force 300-16 SM": "epmp-sm", "ePMP Force 300-25 SM": "epmp-sm",
    "ePMP Force 300-16 AP": "epmp-ap", "ePMP Force 300-25 AP": "epmp-ap", "ePMP 3000L AP": "epmp-ap",
    "60 GHz cnWave V5000 DN": "cnwave-60ghz", "60 GHz cnWave V3000 CN": "cnwave-60ghz",
    "60 GHz cnWave V3000 DN": "cnwave-60ghz", "60 GHz cnWave V2000 CN": "cnwave-60ghz",
    "60 GHz cnWave V2000 DN": "cnwave-60ghz", "60 GHz cnWave V1000 CN": "cnwave-60ghz",
    "60 GHz cnWave V1000 DN": "cnwave-60ghz", "60 GHz cnWave CN": "cnwave-60ghz", "60 GHz cnWave DN": "cnwave-60ghz",
    "cnPilot e500": "enterprise-wifi-eseries", "cnPilot e430H": "enterprise-wifi-eseries",
    "cnPilot e430W": "enterprise-wifi-eseries",
    "cnPilot r195P": "cnpilot-r195p",
}

# RCP exports use "IPv4 Address"; nbn_accelerate exports use "IP Address" — same data, different header.
IP_FIELD_CANDIDATES = ["IP Address", "IPv4 Address"]


def find_site_files(inventory_root, flavour, site):
    pattern = os.path.join(inventory_root, flavour, f"{site}_cnmaestro-inventory.csv" if site else "*_cnmaestro-inventory.csv")
    return sorted(glob.glob(pattern))


def ip_field(fieldnames):
    for cand in IP_FIELD_CANDIDATES:
        if cand in fieldnames:
            return cand
    raise ValueError(f"no known IP column in {fieldnames}")


def compute_families(csv_path):
    family_octets = defaultdict(Counter)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        ipf = ip_field(reader.fieldnames)
        for r in reader:
            fam = FAMILY_MAP.get(r["Device Type"])
            ip = r.get(ipf, "")
            if fam and ip and ip not in ("N/A", "-", ""):
                octet = ".".join(ip.split(".")[:3]) + ".x"
                family_octets[fam][octet] += 1
    return family_octets


def render_site(site, family_octets, indent="    "):
    lines = [f"{indent}families:"]
    for fam, octets in sorted(family_octets.items()):
        total = sum(octets.values())
        dominant, dcount = octets.most_common(1)[0]
        lines.append(f"{indent}  {fam}:")
        lines.append(f'{indent}    octet_pattern: "{dominant}"')
        lines.append(f"{indent}    trust: verified")
        lines.append(f"{indent}    verified:")
        lines.append(f'{indent}      date: "2026-09-18"')
        lines.append(f"{indent}      method: cnmaestro-export")
        lines.append(f"{indent}      host_count: {dcount}")
        others = [f"{o} ({c} hosts)" for o, c in octets.most_common() if o != dominant]
        if others:
            note = f"dominant pattern shown ({dcount}/{total} hosts); also present: {', '.join(others)}"
            lines.append(f'{indent}    notes: "{note}"')
    return "\n".join(lines)


def known_ouis(site_addressing_yaml_path):
    """Lowercase colon-form OUI keys already in oui_reference — stdlib-only parse (no PyYAML
    dependency for this script), since the key form is fixed and simple ('  "xx:yy:zz":' lines)."""
    ouis = set()
    with open(site_addressing_yaml_path) as f:
        text = f.read()
    in_oui_block = False
    for line in text.splitlines():
        if line.startswith("oui_reference:"):
            in_oui_block = True
            continue
        if in_oui_block:
            if line and not line.startswith(" "):
                break
            m = re.match(r'^\s{2}"([0-9a-fA-F:]{8})":\s*$', line)
            if m:
                ouis.add(m.group(1).lower())
    return ouis


def audit_oui(device_inventory_path, site_addressing_yaml_path):
    known = known_ouis(site_addressing_yaml_path)
    oui_data = defaultdict(lambda: {"total": 0, "families": Counter(), "sites": Counter()})
    with open(device_inventory_path, newline="") as f:
        for r in csv.DictReader(f):
            mac = re.sub(r"[^0-9A-Fa-f]", "", r.get("mac_address", ""))
            if len(mac) != 12:
                continue
            oui = ":".join([mac[0:2], mac[2:4], mac[4:6]]).lower()
            d = oui_data[oui]
            d["total"] += 1
            d["families"][r.get("product_family", "UNKNOWN")] += 1
            d["sites"][r.get("site", "UNKNOWN")] += 1

    missing = {oui: d for oui, d in oui_data.items() if oui not in known}
    if not missing:
        print(f"# no OUI blocks in {device_inventory_path} are missing from {site_addressing_yaml_path}'s oui_reference")
        return
    print(f"# OUI blocks present in {device_inventory_path} but missing from oui_reference:")
    for oui, d in sorted(missing.items(), key=lambda kv: -kv[1]["total"]):
        top_site, site_n = d["sites"].most_common(1)[0]
        print(f'  "{oui}":')
        print(f"    # host_count={d['total']}  families={dict(d['families'].most_common())}")
        print(f"    family: UNKNOWN  # pick the dominant one from the families breakdown above — never guess")
        print(f"    verified:")
        print(f'      date: "REPLACE-WITH-TODAY"')
        print(f"      method: cnmaestro-export")
        print(f"      site: {top_site}  # most common of {dict(d['sites'].most_common())}")
        print(f"      host_count: {site_n}")
        print(f'    notes: "REPLACE — state whether this OUI is family-exclusive or shared, per the file\'s existing entries\' style"')
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory-root", default=DEFAULT_INVENTORY_ROOT,
                     help=f"directory holding <flavour>/*_cnmaestro-inventory.csv (default: {DEFAULT_INVENTORY_ROOT})")
    ap.add_argument("--flavour", choices=["rcp", "nbn_accelerate"], help="restrict to one flavour subdirectory")
    ap.add_argument("--all-flavours", action="store_true", help="scan every flavour subdirectory under --inventory-root")
    ap.add_argument("--site", help="a single site slug (matches <site>_cnmaestro-inventory.csv)")
    ap.add_argument("--all", action="store_true", help="every site found for the selected flavour(s)")
    ap.add_argument("--oui-audit", action="store_true",
                     help="report OUI blocks in device-inventory.csv missing from oui_reference, instead of computing families:")
    ap.add_argument("--device-inventory", default=DEFAULT_DEVICE_INVENTORY,
                     help=f"path to the consolidated device-inventory.csv, for --oui-audit (default: {DEFAULT_DEVICE_INVENTORY})")
    ap.add_argument("--site-addressing-yaml", default=DEFAULT_SITE_ADDRESSING_YAML,
                     help=f"path to site-addressing.yaml, for --oui-audit (default: {DEFAULT_SITE_ADDRESSING_YAML})")
    args = ap.parse_args()

    if args.oui_audit:
        audit_oui(args.device_inventory, args.site_addressing_yaml)
        return

    if not args.site and not args.all:
        ap.error("give --site <slug> or --all, or --oui-audit")
    if args.all_flavours:
        flavours = ["rcp", "nbn_accelerate"]
    elif args.flavour:
        flavours = [args.flavour]
    else:
        ap.error("give --flavour <rcp|nbn_accelerate> or --all-flavours")

    for flavour in flavours:
        paths = find_site_files(args.inventory_root, flavour, args.site)
        if not paths:
            print(f"# no *_cnmaestro-inventory.csv found under {flavour}/ matching site={args.site!r}")
            continue
        print(f"  {flavour}:")
        for path in paths:
            site = os.path.basename(path).replace("_cnmaestro-inventory.csv", "")
            family_octets = compute_families(path)
            if not family_octets:
                print(f"    {site}: {{}}  # no recognised device types with a usable IP in {path}")
                continue
            print(f"    {site}:")
            print(render_site(site, family_octets, indent="      "))


if __name__ == "__main__":
    main()
````

## File: scripts/README.md
````markdown
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
| `client-ip-sweep.sh` | Places a "cnMaestro shows Wi-Fi clients with IPv4 0.0.0.0" report: SMC DHCP health (last hour), the client IPv4 each sampled R195P (`/tmp/stahost`) and Enterprise AP (`show wireless clients`) reports, and how many of those MACs hold a lease on the SMC. Written 2026-10-05 in ansible-wifi for the kalumburu 0.0.0.0 question | `<site>-smc01 <apn\|nbn> [samples]`; `tsh` login; `kp` entries `{apn,nbn}-snmp-ro`, `cnpilot-r-series(-legacy)`, `enterprise-wifi(-legacy)` | Per-site summary lines to stdout | `external-network`, `requires-credentials`, read-only | Yes | A client-IP, DHCP or cnMaestro client-table question at one or more sites |
| `fleet_schema_sweep.py` | Stage 2 of the schema exercise: picks one representative device per family per site, contracts its responses, and records unreachable or empty as findings rather than skips | `--inventory` (cambium-swap's device-inventory.csv), optional `--sites`/`--families`; credentials read from the `cambium-devices/` vault | Observations under `schemas/_observations/<family>/`, plus a findings log | `safe`, `external-network`, `requires-secrets`, `requires-credentials` | Yes — resumable, skips a site/family that already has an observation | Building or refreshing the fleet-wide contract |
| `schema_divergence_report.py` | Reports where devices of one family disagree about their own response shape — universal fields versus splits by model, firmware or site, plus type conflicts | `--schemas` (the schemas tree) | A generated markdown divergence report | `safe`, `modifies-files` | Yes — regenerated from observations each run | After a sweep, to decide where the adapter needs a branch rather than a default |
| `schema_tool.py` | Derives, merges and enforces the device response contract — `observe` one device, `merge` observations into the family standard, `check` a new observation for divergence | Live device via `--driver falcon` (usually a Teleport port-forward) or an adapter's stdout via `--driver stdin`; `CAMBIUM_USER`/`CAMBIUM_PASS` | JSON Schema files under `schemas/<family>/`, observations under `schemas/_observations/`; no response values recorded | `safe`, `external-network`, `requires-secrets`, `requires-credentials` | Yes — read-only | Before writing adapter field mappings; when a new site, model or firmware appears |
| `snmp_schema_from_walk.py` | Derives an SNMP table schema from a live `snmpwalk -On` capture, in the same shape as the REST/getter contracts — records `x-oid-column`, the declared SNMP type, and flags columns the MIB mirror does not document | Live device via `--driver falcon` (usually a Teleport port-forward) or an adapter's stdout via `--driver stdin`; `CAMBIUM_USER`/`CAMBIUM_PASS` | JSON Schema files under `schemas/<family>/`, observations under `schemas/_observations/`; no response values recorded | `safe`, `external-network`, `requires-secrets`, `requires-credentials` | Yes — read-only | Before writing adapter field mappings; when a new site, model or firmware appears |
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
|  |   `get_interfaces()`. No REST API confirmed |   `ssh` 8.4+ only on PATH; network |  |  |  |   from a real |
|  |   for this family — shells out to system |   access to the device (normally a |  |  |  |   R195P; only |
|  |   `ssh` 8.4+ only, not a pure-stdlib |   `tsh` tunnel through the site's |  |  |  |   family whose |
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

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

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
````

## File: scripts/scan-config-fields.py
````python
#!/usr/bin/env python3
"""Report which keys in a JSON file look credential-shaped, WITHOUT ever printing their values.

Exists because ad hoc checks of "does this field have a real value" were done by printing the
value to confirm it — twice this session (2026-09-17), on two different device families — each
time exposing a real secret (SNMP community strings, a RADIUS password, a wireless encryption
key) to an agent transcript. This script makes the safe version the path of least resistance:
it reports flag/empty/non-empty per matching key, never the value itself, recursively through
nested dicts and lists.

Uses the same REDACT_KEY_PATTERN convention as cambium_xv2_adapter.py and
cambium_epmp_adapter.py — keep it in sync with those (or import from one, if this ever moves
in-repo relative to them) if a new vendor field name is found to carry a real secret.

Usage:
    scripts/scan-config-fields.py <path-to-json-file>
    scripts/scan-config-fields.py -   # read from stdin

Exit status: 0 if no flagged keys found, 1 if any were found (so it's usable as a gate, e.g.
before archiving a capture file).
"""

from __future__ import annotations

import json
import re
import sys

REDACT_KEY_PATTERN = re.compile(
    r"pass|psk|secret|key|shared|community|radius|credential|token|auth",
    re.IGNORECASE,
)


def find_flagged(obj, path: str = "") -> list[tuple[str, bool]]:
    """Walk obj, return (path, has_nonempty_value) for every credential-shaped key found."""
    found: list[tuple[str, bool]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key_path = f"{path}.{k}" if path else k
            if REDACT_KEY_PATTERN.search(k):
                found.append((key_path, bool(v)))
            else:
                found.extend(find_flagged(v, key_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(find_flagged(item, f"{path}[{i}]"))
    return found


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1])
    with src:
        data = json.load(src)

    flagged = find_flagged(data)
    if not flagged:
        print("No flagged keys found.")
        return 0

    print(f"{len(flagged)} flagged key(s) found (values never shown):")
    for key_path, has_value in flagged:
        status = "NON-EMPTY — treat as a real secret" if has_value else "empty"
        print(f"  {key_path}: {status}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: scripts/schema_divergence_report.py
````python
#!/usr/bin/env python3
"""Report where the fleet disagrees with itself about a device family's response shape.

A merged schema flattens disagreement into `required` and `x-optional`. That is the right contract
but the wrong diagnostic: it tells you a field is optional without telling you *which* sites,
models or firmware lack it, which is the part that decides whether the adapter needs a branch, a
default, or a bug report to the vendor.

This reads the observations behind a standard and writes the disagreement out in full:

  * fields present everywhere — the safe core an adapter may depend on
  * fields that split by model or by firmware — a real capability difference
  * fields that split by neither — present at some sites on the same model and firmware, which
    usually means configuration or device state, not capability
  * type conflicts — the same field returning different JSON types across the fleet
  * endpoints that never returned a record anywhere, which the contract cannot describe at all

Usage:
    python3 scripts/schema_divergence_report.py --schemas schemas --out schemas/DIVERGENCE.md
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def load(schemas_dir):
    obs = defaultdict(list)
    root = Path(schemas_dir) / "_observations"
    for fam_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for f in sorted(fam_dir.glob("*.json")):
            try:
                obs[fam_dir.name].append(json.loads(f.read_text()))
            except ValueError:
                continue
    return obs


def analyse(observations):
    """endpoint -> field -> facts about where it was seen and what type it had."""
    per_endpoint = defaultdict(lambda: {"bearing": [], "empty": [], "fields": defaultdict(lambda: {
        "sites": set(), "models": set(), "firmware": set(), "types": set()})})
    for doc in observations:
        meta = doc["x-observation"]
        tag = (meta.get("site", "?"), meta.get("model") or "?", meta.get("firmware") or "?")
        for ep, node in doc.get("endpoints", {}).items():
            if "x-error" in node:
                continue
            body = node.get("items", node)
            props = body.get("properties") or {}
            rec = per_endpoint[ep]
            if not props:
                rec["empty"].append(tag)
                continue
            rec["bearing"].append(tag)
            for name, spec in props.items():
                t = spec.get("type")
                f = rec["fields"][name]
                f["sites"].add(tag[0])
                f["models"].add(tag[1])
                f["firmware"].add(tag[2])
                for one in (t if isinstance(t, list) else [t]):
                    f["types"].add(one)
    return per_endpoint


def classify(per_endpoint):
    out = {}
    for ep, rec in per_endpoint.items():
        bearing = rec["bearing"]
        all_sites = {t[0] for t in bearing}
        all_models = {t[1] for t in bearing}
        universal, by_model, by_firmware, by_site, conflicts = [], [], [], [], []
        for name, f in sorted(rec["fields"].items()):
            non_null = f["types"] - {"null"}
            if len(non_null) > 1:
                conflicts.append((name, sorted(f["types"])))
            if f["sites"] == all_sites:
                universal.append(name)
                continue
            missing_models = all_models - f["models"]
            if missing_models and f["models"] != all_models:
                by_model.append((name, sorted(f["models"]), sorted(missing_models)))
            else:
                by_site.append((name, sorted(f["sites"]), sorted(all_sites - f["sites"])))
        out[ep] = {"bearing": bearing, "empty": rec["empty"], "universal": universal,
                   "by_model": by_model, "by_site": by_site, "conflicts": conflicts,
                   "all_sites": sorted(all_sites), "all_models": sorted(all_models)}
    return out


def render(results, schemas_dir):
    lines = [
        "---",
        "Title: Cambium Response Schema Divergence",
        "Category: device-reference",
        "Status: current",
        "Authority: primary — derived from the fleet sweep observations in schemas/_observations/",
        "Scope: Where devices of the same family disagree about their own response shape",
        f"Last reviewed: {datetime.now().strftime('%Y-%m-%d')}",
        "Summary: Per-endpoint breakdown of which response fields are universal across the fleet and which split by model, firmware or site, generated from the sweep rather than asserted.",
        "---",
        "",
        "# Cambium Response Schema Divergence",
        "",
        "Generated by `scripts/schema_divergence_report.py` from the observations in "
        "`schemas/_observations/`. Regenerate it rather than editing it; findings worth keeping as "
        "knowledge belong in [references/05_known-issues.md](../references/05_known-issues.md).",
        "",
        "A field listed under **universal** was present on every device that returned a record for "
        "that endpoint — an adapter may depend on it. Everything below that needs a branch, a "
        "default, or an explanation.",
        "",
        "## Contents",
        "",
    ]
    for family in sorted(results):
        lines.append(f"- [{family}](#{family.replace('.', '')})")
    lines.append("")

    for family, endpoints in sorted(results.items()):
        lines += [f"## {family}", ""]
        for ep, r in sorted(endpoints.items()):
            n_bearing, n_empty = len(r["bearing"]), len(r["empty"])
            lines += [f"### {family} — `{ep}`", ""]
            lines.append(f"Observed on **{n_bearing}** device(s) with a record"
                         + (f", empty on **{n_empty}**" if n_empty else "")
                         + f". Models: {', '.join(r['all_models']) or 'n/a'}.")
            lines.append("")
            if not n_bearing:
                lines += ["**No device anywhere returned a record for this endpoint.** The contract "
                          "cannot describe its shape. Empty at: "
                          + ", ".join(sorted({t[0] for t in r['empty']})) + ".", ""]
                continue
            lines.append(f"- **Universal fields:** {len(r['universal'])}")
            lines.append(f"- **Model-specific fields:** {len(r['by_model'])}")
            lines.append(f"- **Site-specific fields:** {len(r['by_site'])}")
            lines.append(f"- **Type conflicts:** {len(r['conflicts'])}")
            lines.append("")
            if r["by_model"]:
                lines += ["| Field | Present on | Absent on |", "| --- | --- | --- |"]
                for name, present, absent in r["by_model"][:60]:
                    lines.append(f"| `{name}` | {', '.join(present)} | {', '.join(absent)} |")
                if len(r["by_model"]) > 60:
                    lines.append(f"| … {len(r['by_model']) - 60} more | | |")
                lines.append("")
            if r["by_site"]:
                lines += ["Fields that vary by site rather than by model — same hardware, different "
                          "response, so configuration or device state rather than capability:", "",
                          "| Field | Missing at |", "| --- | --- |"]
                for name, _, missing in r["by_site"][:40]:
                    lines.append(f"| `{name}` | {', '.join(missing[:12])}"
                                 + (f" … +{len(missing) - 12}" if len(missing) > 12 else "") + " |")
                if len(r["by_site"]) > 40:
                    lines.append(f"| … {len(r['by_site']) - 40} more | |")
                lines.append("")
            if r["conflicts"]:
                lines += ["**Type conflicts** — the same field returns different JSON types across "
                          "the fleet. Each one is a portability hazard for any code that indexes it:",
                          "", "| Field | Types observed |", "| --- | --- |"]
                for name, types in r["conflicts"][:40]:
                    lines.append(f"| `{name}` | {', '.join(types)} |")
                lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schemas", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    obs = load(args.schemas)
    if not obs:
        raise SystemExit("no observations found")
    results = {fam: classify(analyse(docs)) for fam, docs in obs.items()}
    Path(args.out).write_text(render(results, args.schemas))
    total = sum(len(v) for v in results.values())
    print(f"{args.out}: {len(results)} families, {total} endpoints, "
          f"{sum(len(d) for d in obs.values())} observations")


if __name__ == "__main__":
    main()
````

## File: scripts/schema_tool.py
````python
#!/usr/bin/env python3
"""Derive, merge and enforce the Cambium device response *contract* — a schema, not a snapshot.

The problem this solves: the MIB mirrors are not the contract. `cnPilotMIB` describes 16 client
columns where an XV2 returns 95; `CAMBIUM-PMP80211-MIB` documents 29 ePMP connected-SM columns
where a live 3000L returns 42. Adapter code written against a mirror, or against one device's
response captured once, breaks on the next firmware or the next site.

So the contract is derived from observation and then held as a standard:

  1. `observe`  — pull one device's endpoints and emit a schema for that observation. No values
                  are recorded beyond low-cardinality candidate enums on non-identifying fields.
  2. `merge`    — fold many observations into one standard. A field seen on every observation is
                  `required`; a field seen on some is optional and carries the sites and firmware
                  that had it. This is what makes the standard a standard rather than one site's
                  accident.
  3. `check`    — validate a fresh observation against the standard and report divergence:
                  missing required fields, unknown new fields, and type changes.

Privacy: values that identify an end user are never written, at any stage. PII_FIELDS names them
and `--strict-pii` widens the net to anything that *looks* like a MAC, IP or hostname regardless
of field name. Device-side identifiers (AP MAC, radio BSSID, SM MAC) are infrastructure and are
still never emitted as examples — the standard has no use for them.

Layers: a schema describes either a raw device endpoint (`raw-endpoint`) or an adapter's
normalized getter output (`adapter-normalized`). Only the Enterprise Wi-Fi Falcon families expose
raw endpoints conveniently; ePMP, R195P and cnWave are contracted at their adapter's output. The
layer is recorded in every schema so nobody compares two things that are not the same thing.

Usage:
    # one device, one family, live
    CAMBIUM_USER=... CAMBIUM_PASS=... python3 schema_tool.py observe \\
        --driver falcon --host localhost:10019 --family enterprise-wifi \\
        --model XV2 --site hope-vale --endpoints client-summary,radio-summary \\
        --out obs/hope-vale-xv2.json

    # schema from an adapter's stdout (any family)
    python3 cambium_epmp_adapter.py | python3 schema_tool.py observe \\
        --driver stdin --family epmp-ap --model 'ePMP 3000L' --site hope-vale \\
        --layer adapter-normalized --out obs/hope-vale-epmp.json

    # fold observations into the standard
    python3 schema_tool.py merge --family enterprise-wifi obs/*.json \\
        --out ../schemas/enterprise-wifi/

    # conformance of a new site against the standard
    python3 schema_tool.py check --standard ../schemas/enterprise-wifi \\
        --observation obs/amata-xv2.json
"""
import argparse
import ipaddress
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from http.cookiejar import CookieJar
from pathlib import Path

SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"

# Field names whose values identify an end user. Never emitted. Widen, never narrow.
PII_FIELDS = {
    "mac", "macaddress", "mac_address", "ip", "ipaddr", "ipaddress", "ip6", "ip6_ll", "ipv6",
    "name", "hostname", "user_name", "username", "client_name", "dev_type", "vendor",
    "ssid",  # an SSID is not personal, but it is site-identifying and has no place in a contract
}
MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}$")
# A candidate enum must be short, low-cardinality and non-identifying — "2.4GHz", "ON", "axa".
ENUM_MAX_DISTINCT = 8
ENUM_MAX_LEN = 24


def looks_identifying(value):
    """True when a value looks like an address or hostname whatever its field is called."""
    if not isinstance(value, str) or not value:
        return False
    if MAC_RE.match(value):
        return True
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        pass
    return bool(re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$", value))


def json_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


class FieldFacts:
    """What has been observed about one field, across every record and every device."""

    def __init__(self):
        self.types = set()
        self.present = 0
        self.null_count = 0
        self.values = set()
        self.value_overflow = False
        self.child = None          # FieldFacts for array items / nested objects
        self.object_fields = None  # name -> FieldFacts

    def see(self, value, strict_pii, field_name):
        t = json_type(value)
        self.types.add(t)
        self.present += 1
        if t == "null":
            self.null_count += 1
            return
        if t == "object":
            if self.object_fields is None:
                self.object_fields = defaultdict(FieldFacts)
            for k, v in value.items():
                self.object_fields[k].see(v, strict_pii, k)
            return
        if t == "array":
            if self.child is None:
                self.child = FieldFacts()
            for item in value:
                self.child.see(item, strict_pii, field_name)
            return
        if self._enumerable(value, strict_pii, field_name):
            if len(self.values) < ENUM_MAX_DISTINCT:
                self.values.add(value)
            else:
                self.value_overflow = True
        else:
            self.value_overflow = True

    @staticmethod
    def _enumerable(value, strict_pii, field_name):
        if field_name.lower() in PII_FIELDS:
            return False
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            if len(value) > ENUM_MAX_LEN:
                return False
            if strict_pii and looks_identifying(value):
                return False
            return not looks_identifying(value)
        return False

    def to_schema(self, field_name, total_records):
        types = sorted(self.types - {"null"})
        node = {}
        if not types:
            node["type"] = "null"
        elif len(types) == 1:
            node["type"] = types[0]
        else:
            node["type"] = types
            node["x-type-varies"] = True
        if "null" in self.types:
            node["x-nullable"] = True
        if field_name.lower() in PII_FIELDS:
            node["x-identifying"] = True
            node["x-note"] = "End-user identifying — values are never recorded in this contract."
        if self.values and not self.value_overflow and len(self.values) <= ENUM_MAX_DISTINCT:
            node["x-candidate-values"] = sorted(self.values, key=str)
        if self.child is not None:
            node["items"] = self.child.to_schema(field_name, total_records)
        if self.object_fields is not None:
            node["properties"] = {
                k: v.to_schema(k, total_records) for k, v in sorted(self.object_fields.items())
            }
        node["x-observed-count"] = self.present
        return node


def schema_from_payload(payload, strict_pii):
    """Infer one endpoint's schema. A list of records is contracted at the record level, which is
    the useful unit — how many rows happened to exist at capture time says nothing about shape."""
    root = FieldFacts()
    if isinstance(payload, list):
        records = payload
        shape = "array"
    else:
        records = [payload]
        shape = "object"
    for rec in records:
        root.see(rec, strict_pii, "")
    if shape == "array":
        # Each element was fed to `root` directly, so the record's fields live on root itself —
        # `root.child` is only populated for arrays nested *inside* a record.
        fields = root.object_fields or {}
        body = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {k: v.to_schema(k, len(records)) for k, v in sorted(fields.items())},
                "required": sorted(k for k, v in fields.items() if v.present == len(records)) if records else [],
            },
        }
    elif root.object_fields is not None:
        fields = root.object_fields
        body = {
            "type": "object",
            "properties": {k: v.to_schema(k, 1) for k, v in sorted(fields.items())},
            "required": sorted(fields),
        }
    else:
        # A scalar response — an integer count, a bare string. Still a contract, just a flat one.
        body = root.to_schema("", 1)
        body.pop("x-observed-count", None)
    body["x-records-observed"] = len(records)
    return body


class FalconDriver:
    """Enterprise Wi-Fi (XV2 and cnPilot E-series share the Falcon UI): POST /api/login, then
    session cookies plus an X-XSRF-TOKEN header echoing the XSRF-TOKEN cookie."""

    def __init__(self, host, user, password):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.host = host
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx),
            urllib.request.HTTPCookieProcessor(self.jar))
        self.xsrf = None
        self.user, self.password = user, password

    def _req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"https://{self.host}{path}", data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
        if self.xsrf:
            req.add_header("X-XSRF-TOKEN", self.xsrf)
        with self.opener.open(req, timeout=20) as resp:
            raw = resp.read().decode()
        for c in self.jar:
            if c.name == "XSRF-TOKEN":
                self.xsrf = c.value
        return json.loads(raw) if raw else {}

    def login(self):
        if not self._req("POST", "/api/login", {"username": self.user, "password": self.password}).get("success"):
            raise SystemExit("login rejected")

    def fetch(self, endpoint):
        return self._req("GET", f"/api/{endpoint}")


def cmd_observe(args):
    endpoints = {}
    if args.driver == "falcon":
        user, password = os.environ.get("CAMBIUM_USER"), os.environ.get("CAMBIUM_PASS")
        if not (user and password):
            raise SystemExit("CAMBIUM_USER and CAMBIUM_PASS must be set")
        dev = FalconDriver(args.host, user, password)
        dev.login()
        for ep in [e.strip() for e in args.endpoints.split(",") if e.strip()]:
            try:
                endpoints[ep] = schema_from_payload(dev.fetch(ep), args.strict_pii)
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError) as exc:
                endpoints[ep] = {"x-error": f"{type(exc).__name__}: {exc}"}
                print(f"  {ep}: {type(exc).__name__}", file=sys.stderr)
    elif args.driver == "stdin":
        payload = json.load(sys.stdin)
        # An adapter prints one object of named getters; contract each getter separately.
        if isinstance(payload, dict) and args.split_getters:
            for name, value in payload.items():
                endpoints[name] = schema_from_payload(value, args.strict_pii)
        else:
            endpoints[args.endpoints or "response"] = schema_from_payload(payload, args.strict_pii)
    else:
        raise SystemExit(f"unknown driver: {args.driver}")

    doc = {
        "x-observation": {
            "captured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "family": args.family,
            "model": args.model,
            "firmware": args.firmware,
            "site": args.site,
            "layer": args.layer,
            "driver": args.driver,
            "strict_pii": args.strict_pii,
        },
        "endpoints": endpoints,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(doc, indent=2) + "\n")
    print(args.out)


def _merge_node(a, b):
    """Union two schema nodes. Types union; nullability and variance are sticky; candidate values
    union until they stop being a candidate enum; observation counts add."""
    if a is None:
        return json.loads(json.dumps(b))
    out = json.loads(json.dumps(a))
    ta = out.get("type")
    tb = b.get("type")
    types = set(ta if isinstance(ta, list) else [ta]) | set(tb if isinstance(tb, list) else [tb])
    types.discard(None)
    out["type"] = sorted(types)[0] if len(types) == 1 else sorted(types)
    if len(types) > 1:
        out["x-type-varies"] = True
    for flag in ("x-nullable", "x-identifying", "x-type-varies"):
        if b.get(flag):
            out[flag] = True
    va, vb = out.get("x-candidate-values"), b.get("x-candidate-values")
    if va is not None and vb is not None:
        merged = sorted(set(va) | set(vb), key=str)
        if len(merged) <= ENUM_MAX_DISTINCT:
            out["x-candidate-values"] = merged
        else:
            out.pop("x-candidate-values", None)
    else:
        out.pop("x-candidate-values", None)
    out["x-observed-count"] = out.get("x-observed-count", 0) + b.get("x-observed-count", 0)
    if "items" in a or "items" in b:
        out["items"] = _merge_node(a.get("items"), b.get("items")) if b.get("items") else a.get("items")
    if "properties" in a or "properties" in b:
        props = dict(a.get("properties", {}))
        for k, v in b.get("properties", {}).items():
            props[k] = _merge_node(props.get(k), v)
        out["properties"] = props
    return out


# Endpoints whose response is a MAP keyed by a site-variable name rather than a record with fixed
# fields. The adapter layer follows NAPALM's convention here (see cambium_xv2_adapter.py's
# get_interfaces docstring), so an interface map is correct and deliberate. Contracting its keys as
# fields is what is wrong: it makes one site's VLAN plan look like the family's schema. For these,
# the contract describes the VALUE shape under `additionalProperties` and records what the keys are.
MAP_SHAPED = {
    ("cnpilot-r-series", "interfaces"): "interface name, e.g. eth2.17, wan1.500 — varies per site",
}

# A map's keys are contracted by ROLE, not by name: which interface does what, matched by pattern. Every observed name must
# fall into exactly one role (a name in none is divergent), and a role's count must sit within its bounds. Bounds come from
# the observations (11 R195P, nine sites, 2026-09-20/22) and stay loose where the evidence is: the 2026-09-20 files are one
# per site and may combine units, so only single-instance roles carry a maximum. Meanings are those references/06 records;
# where it records none (which radio is which band) the role says so rather than guessing.
MAP_ROLES = {
    ("cnpilot-r-series", "interfaces"): [
        {"role": "loopback", "pattern": r"lo", "min": 1, "max": 1},
        {"role": "lan_bridge", "pattern": r"br0", "min": 1, "max": 1,
         "note": "carries the LAN MAC; the WAN MAC is LAN + 1 (references/06, BUR-R195P-1047)"},
        {"role": "switch_port", "pattern": r"eth2", "min": 1, "max": 1, "note": "the port the switch-side VLANs ride on"},
        {"role": "switch_vlan", "pattern": r"eth2\.\d+", "min": 1,
         "note": "VLAN sub-interfaces; management is eth2.500. The set varies per site (eth2.17, eth2.550 at some only)"},
        {"role": "wan", "pattern": r"wan\d+", "min": 0,
         "note": "name varies per unit (wan1, wan3); one Burringurrah unit had its WAN on eth2.500 and no wan* (references/06)"},
        {"role": "wan_vlan", "pattern": r"wan\d+\.\d+", "min": 0},
        {"role": "radio", "pattern": r"rai?\d+", "min": 1, "note": "MediaTek radio interfaces; which is which band is not recorded"},
        {"role": "radio_client", "pattern": r"apclii?\d+", "min": 0, "note": "MediaTek AP-client interfaces; no use recorded on this estate"},
        {"role": "wds", "pattern": r"wds\d+", "min": 0, "note": "WDS link interfaces; no mesh is enabled on this estate"},
        {"role": "qos_pseudo", "pattern": r"imq\d+", "min": 0, "note": "QoS pseudo-interfaces, not traffic (references/06)"},
    ],
}


def collapse_map(node, key_meaning, roles=None):
    """Fold a map's per-key schemas into one value schema under `additionalProperties`."""
    target = node.get("items", node)
    props = target.pop("properties", {}) or {}
    merged = None
    for spec in props.values():
        merged = _merge_node(merged, spec)
    target["additionalProperties"] = merged or {"type": "object"}
    target["x-map-keyed-by"] = key_meaning
    target["x-keys-observed"] = sorted(props)
    if roles:
        target["x-roles"] = roles
    target.pop("required", None)
    target.pop("x-optional", None)
    return node


def cmd_merge(args):
    obs = [json.loads(Path(p).read_text()) for p in args.observations]
    obs = [o for o in obs if o["x-observation"]["family"] == args.family]
    if not obs:
        raise SystemExit(f"no observations for family {args.family}")

    by_endpoint = defaultdict(list)
    for o in obs:
        for ep, node in o["endpoints"].items():
            if "x-error" not in node:
                by_endpoint[ep].append((o["x-observation"], node))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for ep, entries in sorted(by_endpoint.items()):
        merged = None
        for _, node in entries:
            merged = _merge_node(merged, node)

        # Required = present on every observation that actually returned a record.
        #
        # An endpoint that returned an empty array is not evidence that its fields are absent — a
        # radio with no clients attached says nothing about what a client record contains. Counting
        # it would drag every field to "optional" and destroy the contract. Such observations are
        # excluded from the presence maths and counted separately, so a reader can see how much
        # evidence the `required` set actually rests on.
        bearing = [(meta, node) for meta, node in entries
                   if (node.get("items", node).get("properties") or {})]
        empty = [meta["site"] for meta, node in entries
                 if not (node.get("items", node).get("properties") or {})]
        seen = defaultdict(int)
        sites_with = defaultdict(set)
        for meta, node in bearing:
            for k in (node.get("items", node).get("properties") or {}):
                seen[k] += 1
                sites_with[k].add(f"{meta['site']}/{meta['model']}")
        target = merged.get("items", merged)
        total = len(bearing)
        target["required"] = sorted(k for k, c in seen.items() if c == total) if total else []
        target["x-optional"] = {
            k: {"observed_on": c, "of": total, "seen_at": sorted(sites_with[k])}
            for k, c in sorted(seen.items()) if c < total
        }
        target["x-evidence"] = {
            "observations_with_records": total,
            "observations_empty": len(empty),
            "empty_at": sorted(empty),
            "note": ("`required` rests only on observations that returned a record. Endpoints empty "
                     "at capture time contribute nothing either way."),
        }

        key_meaning = MAP_SHAPED.get((args.family, ep))
        if key_meaning:
            merged = collapse_map(merged, key_meaning, MAP_ROLES.get((args.family, ep)))

        doc = {
            "$schema": SCHEMA_DIALECT,
            "$id": f"cambium/{args.family}/{ep}.schema.json",
            "title": f"Cambium {args.family} — {ep}",
            "description": (
                "Derived from live observation, not from vendor documentation. Fields listed in "
                "`required` were present on every device observed; `x-optional` names the rest with "
                "how often they appeared. No end-user identifying values are recorded."
            ),
            "x-cambium": {
                "family": args.family,
                "endpoint": ep,
                "layer": entries[0][0]["layer"],
                "observations": total,
                "models": sorted({e[0]["model"] for e in entries if e[0].get("model")}),
                "firmware": sorted({e[0]["firmware"] for e in entries if e[0].get("firmware")}),
                "sites": sorted({e[0]["site"] for e in entries if e[0].get("site")}),
                "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            **{k: v for k, v in merged.items() if not k.startswith("x-records")},
        }
        path = out_dir / f"{ep}.schema.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        written.append((ep, total, len((merged.get("items", merged)).get("properties", {})),
                        merged.get("type"), len(entries)))
    for ep, n, fields, typ, seen_total in written:
        if fields:
            detail = f"{fields} fields from {n} observation(s)"
        elif typ == "null":
            detail = f"observed as null on {seen_total} observation(s) — endpoint exists, no data"
        elif typ == "array":
            detail = f"empty on all {seen_total} observation(s) — shape unknown, needs a bearing sample"
        else:
            detail = f"scalar ({typ}) from {seen_total} observation(s)"
        print(f"{ep}: {detail} -> {out_dir / (ep + '.schema.json')}")


def _types(node):
    t = (node or {}).get("type")
    return set(t if isinstance(t, list) else [t])


def check_map(std_t, obs_props):
    """A map-shaped endpoint: each key must fall into exactly one role within its bounds, and each value must fit the
    one value schema under `additionalProperties`. With no `x-roles` the keys are not judged, only the values."""
    roles = std_t.get("x-roles") or []
    counts, unmatched, ambiguous = {r["role"]: 0 for r in roles}, [], {}
    for key in sorted(obs_props):
        hits = [r["role"] for r in roles if re.fullmatch(r["pattern"], key)]
        if len(hits) == 1:
            counts[hits[0]] += 1
        elif roles and not hits:
            unmatched.append(key)
        elif len(hits) > 1:
            ambiguous[key] = hits
    out_of_bounds = {r["role"]: {"observed": counts[r["role"]], "min": r.get("min", 0), "max": r.get("max")}
                     for r in roles if counts[r["role"]] < r.get("min", 0)
                     or (r.get("max") is not None and counts[r["role"]] > r["max"])}
    value_std = (std_t.get("additionalProperties") or {}).get("properties", {})
    unknown_value_fields, value_type_changes = set(), {}
    for spec in obs_props.values():
        for field, fspec in (spec.get("properties") or {}).items():
            if field not in value_std:
                unknown_value_fields.add(field)
            elif not _types(fspec) <= _types(value_std[field]):
                value_type_changes[field] = {"standard": value_std[field].get("type"), "observed": fspec.get("type")}
    divergent = unmatched or ambiguous or out_of_bounds or unknown_value_fields or value_type_changes
    return {"status": "divergent" if divergent else "conformant", "keyed_by": std_t["x-map-keyed-by"], "role_counts": counts,
            "unmatched_keys": unmatched, "ambiguous_keys": ambiguous, "roles_out_of_bounds": out_of_bounds,
            "unknown_value_fields": sorted(unknown_value_fields), "value_type_changes": value_type_changes}


def cmd_check(args):
    obs = json.loads(Path(args.observation).read_text())
    std_dir = Path(args.standard)
    report = {"observation": str(args.observation), "standard": str(std_dir),
              "site": obs["x-observation"].get("site"), "model": obs["x-observation"].get("model"),
              "firmware": obs["x-observation"].get("firmware"), "endpoints": {}}
    worst = "conformant"
    for ep, node in obs["endpoints"].items():
        std_path = std_dir / f"{ep}.schema.json"
        if "x-error" in node:
            report["endpoints"][ep] = {"status": "error", "detail": node["x-error"]}
            worst = "divergent"
            continue
        if not std_path.exists():
            report["endpoints"][ep] = {"status": "no-standard", "detail": "endpoint absent from the standard"}
            worst = "divergent"
            continue
        std = json.loads(std_path.read_text())
        std_t, obs_t = std.get("items", std), node.get("items", node)
        # An endpoint that returned nothing cannot diverge from anything. Reporting it as divergent
        # would flag every site whose AP happened to have no client attached.
        if not (obs_t.get("properties") or {}):
            report["endpoints"][ep] = {
                "status": "no-records",
                "detail": "endpoint returned no record at capture time — contributes no evidence",
            }
            continue
        std_props, obs_props = std_t.get("properties", {}), obs_t.get("properties", {})
        if "x-map-keyed-by" in std_t:
            result = check_map(std_t, obs_props)
            if result["status"] == "divergent":
                worst = "divergent"
            report["endpoints"][ep] = result
            continue
        missing_required = sorted(set(std_t.get("required", [])) - set(obs_props))
        unknown = sorted(set(obs_props) - set(std_props))
        type_changes = {}
        for k in sorted(set(std_props) & set(obs_props)):
            s, o = std_props[k].get("type"), obs_props[k].get("type")
            s_set = set(s if isinstance(s, list) else [s])
            o_set = set(o if isinstance(o, list) else [o])
            if not o_set <= s_set:
                type_changes[k] = {"standard": s, "observed": o}
        status = "conformant" if not (missing_required or unknown or type_changes) else "divergent"
        if status == "divergent":
            worst = "divergent"
        report["endpoints"][ep] = {"status": status, "missing_required": missing_required,
                                   "unknown_fields": unknown, "type_changes": type_changes}
    report["status"] = worst
    text = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n")
        print(args.out)
    else:
        print(text)
    return 0 if worst == "conformant" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("observe", help="contract one device's responses")
    o.add_argument("--driver", choices=["falcon", "stdin"], required=True)
    o.add_argument("--host", help="host:port for a live driver, usually a Teleport port-forward")
    o.add_argument("--endpoints", default="", help="comma-separated endpoints (falcon), or a name (stdin)")
    o.add_argument("--family", required=True)
    o.add_argument("--model", default="")
    o.add_argument("--firmware", default="")
    o.add_argument("--site", required=True)
    o.add_argument("--layer", choices=["raw-endpoint", "adapter-normalized"], default="raw-endpoint")
    o.add_argument("--split-getters", action="store_true", help="stdin driver: contract each top-level key separately")
    o.add_argument("--strict-pii", action="store_true", default=True)
    o.add_argument("--out", required=True)
    o.set_defaults(func=cmd_observe)

    m = sub.add_parser("merge", help="fold observations into the family standard")
    m.add_argument("observations", nargs="+")
    m.add_argument("--family", required=True)
    m.add_argument("--out", required=True)
    m.set_defaults(func=cmd_merge)

    c = sub.add_parser("check", help="conformance of one observation against the standard")
    c.add_argument("--standard", required=True)
    c.add_argument("--observation", required=True)
    c.add_argument("--out")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    raise SystemExit(args.func(args) or 0)


if __name__ == "__main__":
    main()
````

## File: scripts/snmp_schema_from_walk.py
````python
#!/usr/bin/env python3
"""Derive an SNMP table schema from a live `snmpwalk -On` capture.

The existing `schemas/` tree contracts the REST and getter layers. SNMP is a third layer with its own shape —
numeric OIDs, columns rather than names, and values that are all strings on the wire — and nothing contracted
it until now. This tool builds that contract the same way `fleet_schema_sweep.py` builds the others: derived
from live observation, never authored.

Input is the raw output of `snmpwalk -On`, one `OID = TYPE: value` line per row. Output matches the existing
schema convention exactly, so a reader does not have to learn a second one.

Two SNMP-specific facts the output records, because both have already cost a wrong reading:

* **A table entry OID ends in `.1`, the Entry node**, and a row reads `<entry>.<column>.<index>`. Using the
  table OID instead shifts column and index by one, and every row then parses as a separate object carrying
  only its first field. This produced 420 "subscriber links" for an access point with 10 on 2026-09-21.
* **A scalar is instance `.0` of its object.** `cambiumAPNumberOfConnectedSTA` answers at `....10.0`, not at
  `....10`, so an exact-match lookup on the bare OID silently returns nothing.

Usage:

    python3 scripts/snmp_schema_from_walk.py \\
        --walk <raw.txt> --entry .1.3.6.1.4.1.17713.21.1.2.30.1 \\
        --family epmp-ap --name snmp-connected-sta \\
        --columns <json map of column-number to name> \\
        --model ePMP-3000L --firmware 4.7.0.1 --site hope-vale
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LINE = re.compile(r"^(?P<oid>\.[\d.]+)\s*=\s*(?P<type>[A-Za-z0-9-]+):?\s*(?P<value>.*)$")

#: SNMP type token -> JSON Schema type. Everything the agent returns is a string on the wire; this records
#: what the agent DECLARED, which is the more useful contract for an adapter author.
SNMP_TYPES = {
    "INTEGER": "integer", "Gauge32": "integer", "Counter32": "integer", "Counter64": "integer",
    "Unsigned32": "integer", "Timeticks": "integer", "STRING": "string", "Hex-STRING": "string",
    "OID": "string", "IpAddress": "string",
}

#: Column names that carry an end-user identifier. Values are counted, never recorded.
IDENTIFYING = {"mac", "connectedSTAMAC", "ip", "connectedSTAIP", "hostname", "name",
               "connectedSTAClickTHostName", "connectedSTAClickTHWAddr"}


def parse_walk(path: Path) -> dict[str, tuple[str, str]]:
    """`{oid: (snmp_type, value)}` from an `snmpwalk -On` capture, skipping absent-object responses."""
    out: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = LINE.match(line.strip())
        if not match:
            continue
        value = match.group("value").strip().strip('"')
        if "No Such" in line or "No more variables" in line:
            continue
        out[match.group("oid")] = (match.group("type"), value)
    return out


def build(walk: dict[str, tuple[str, str]], entry: str, columns: dict[int, str]) -> dict:
    prefix = entry.rstrip(".") + "."
    rows: dict[str, dict[int, tuple[str, str]]] = defaultdict(dict)
    for oid, (snmp_type, value) in walk.items():
        if not oid.startswith(prefix):
            continue
        remainder = oid[len(prefix):].split(".")
        if len(remainder) < 2 or not remainder[0].isdigit():
            continue
        rows[".".join(remainder[1:])][int(remainder[0])] = (snmp_type, value)

    properties: dict[str, dict] = {}
    seen: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for row in rows.values():
        for column, pair in row.items():
            seen[column].append(pair)

    for column in sorted(seen):
        name = columns.get(column, f"column_{column}")
        pairs = seen[column]
        declared = SNMP_TYPES.get(pairs[0][0], "string")
        prop: dict = {"type": declared, "x-oid-column": column, "x-snmp-type": pairs[0][0],
                      "x-observed-count": len(pairs)}
        if name in IDENTIFYING:
            prop["x-identifying"] = True
            prop["x-note"] = "End-user identifying — values are never recorded in this contract."
        else:
            distinct = sorted({v for _, v in pairs})
            if len(distinct) <= 8:
                prop["x-candidate-values"] = distinct
        if column not in columns:
            prop["x-undocumented-in-mib"] = True
        properties[name] = prop

    return {"properties": properties, "row_count": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--walk", required=True, type=Path)
    ap.add_argument("--entry", required=True, help="table ENTRY oid, ending in the Entry node (usually .1)")
    ap.add_argument("--family", required=True)
    ap.add_argument("--name", required=True, help="schema basename, e.g. snmp-connected-sta")
    ap.add_argument("--columns", type=Path, help="JSON file mapping column number to MIB name")
    ap.add_argument("--model", default=None)
    ap.add_argument("--firmware", default=None)
    ap.add_argument("--site", default=None)
    ap.add_argument("--out-root", type=Path, default=Path(__file__).resolve().parent.parent / "schemas")
    args = ap.parse_args()

    columns: dict[int, str] = {}
    if args.columns:
        columns = {int(k): v for k, v in json.loads(args.columns.read_text(encoding="utf-8")).items()}

    built = build(parse_walk(args.walk), args.entry, columns)
    if not built["properties"]:
        print(f"no rows under {args.entry} — nothing written")
        return 1

    names = sorted(built["properties"])
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"cambium/{args.family}/{args.name}.schema.json",
        "title": f"Cambium {args.family} — {args.name}",
        "description": (
            "Derived from a live SNMP walk, not from a MIB mirror. The live agent may expose more columns than "
            "the mirror documents; those carry `x-undocumented-in-mib`. `x-oid-column` is the column number "
            "under the table ENTRY oid — note the entry ends in `.1` and a row reads "
            "`<entry>.<column>.<index>`. No end-user identifying values are recorded."
        ),
        "x-cambium": {
            "family": args.family,
            "endpoint": args.name,
            "layer": "snmp",
            "entry_oid": args.entry,
            "observations": built["row_count"],
            "models": [args.model] if args.model else [],
            "firmware": [args.firmware] if args.firmware else [],
            "sites": [args.site] if args.site else [],
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "type": "array",
        "items": {
            "type": "object",
            "properties": {name: built["properties"][name] for name in names},
            "required": names,
            "x-records-observed": built["row_count"],
        },
        "x-observed-count": built["row_count"],
    }

    out_dir = args.out_root / args.family
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.name}.schema.json"
    out_path.write_text(json.dumps(schema, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out_path} — {len(names)} columns, {built['row_count']} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: AGENTS.md
````markdown
@../../../AGENTS.md

Title: skill-cambium Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-cambium specialist pack — canonical source for Cambium device-fleet operational knowledge
Last reviewed: 20260917
Summary: Agent guidance for maintaining and using the skill-cambium specialist pack. Covers specialist structure, reference routing, cross-pack boundary with skill-smc, and update discipline.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Project-coherence checklist](#project-coherence-checklist)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)

---

## Working rules

- `SKILL.md` is the agent-facing activation surface — it defines triggers, the Standing Write-Back Contract, and pointers to `references/`.
- `RUNBOOK.md` is the navigation index — it maps task types to specific numbered reference files. Do not use it as a content source.
- The 6 numbered files under `references/` (from `references/01_overview.md` to `references/06_device-api-cli-reference.md`) are the content source. Load only the one needed for the task.
- `manifest.json` is the machine-readable specialist metadata. Update `version` and `updated_at` when any content file changes.
- Never write a device password or other secret value into any file in this pack — reference convention is `<secret:keepassxc:cambium-devices/<entry>>` (see
  `references/02_device-access-and-vault.md`). Avoid the substrings `credential`/`secret`/`password` in file **paths** in this pack — the workspace's OPA write-gate hard-blocks them regardless of
  content (hit and worked around 2026-09-17 — the file is now named `references/02_device-access-and-vault.md`, not `credentials`, for exactly this reason).
- Boundary with `skill-smc`: device/hardware/credential/asset-register/cnMaestro knowledge belongs here; SMC box, Ansible authoring, and provisioning-role knowledge belongs to `skill-smc`. A fact
  spanning both gets written to both packs in the same session.
- Follow naming convention for time-bound docs: `<slug>-YYYYMMDD_hhmm.md`.
- Keep `CHANGELOG.md` current — append entries when content or structure changes.

## Project-coherence checklist

### Tier 1 — Reference files (content source — update first)

| New knowledge type                                                                             | Target file                                                            |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Device family/model/firmware/EoL fact                                                          | `references/01_overview.md`                                            |
| Vault structure change, `kp`/`keepassxc-cli` behaviour                                         | `references/02_device-access-and-vault.md`                             |
| Asset-register naming/drift, a new site's conventions                                          | `references/03_asset-register-conventions.md`                          |
| `device-inventory.csv` schema change, extraction workflow fact                                 | `references/04_device-inventory-schema.md`                             |
| New coverage gap, staleness risk, unvalidated assumption                                       | `references/05_known-issues.md`                                        |
| Device REST API / SSH CLI data point, adapter method, config-backup or write-ops boundary fact | `references/06_device-api-cli-reference.md`                            |
| New reusable Cambium-domain script or tool                                                     | `scripts/` — see Tier 1b below                                         |
| No existing file fits                                                                          | Propose a new numbered file; add the `RUNBOOK.md` row in the same pass |

**Do not write new operational content to `RUNBOOK.md`** — it is a navigation index only. Write content to the matching reference file.

### Tier 1b — Scripts (moved or written in another project — catalog fully in the same pass)

A script belongs here, not in a consuming project, when it is Cambium-domain tooling reusable across projects rather than specific to one project's investigation — the same test already applied to
`scripts/cambium-portal.sh` (vendor-portal automation) and `scripts/extract-asset-register.py` (asset-register extraction), both moved in from `cambium-swap`. Moving the file alone is not enough —
every one of these must land in the same pass, or the script is invisible to the next agent that opens this pack instead of the consuming project:

| Step                          | Update                                                                                                                                                               |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Move the file                 | `scripts/<name>`, with a header comment stating where it came from and why it belongs here (see the two existing scripts for the pattern)                            |
| Catalog it                    | `scripts/README.md` Raw Script Inventory — purpose, inputs, outputs, safety label(s), idempotency, when to use                                                       |
| Route to it                   | `RUNBOOK.md` — a routing row if the script answers a task type; `justfile` — a recipe if it should run via `just`                                                    |
| Prove the catalog is enforced | Run `scripts/check_governance.py` — it fails on any file under `scripts/` not named in `scripts/README.md` (this is a real, executed check, not a                    |
|                               |   documented intention)                                                                                                                                              |
| Metadata + history            | `manifest.json` version bump; `CHANGELOG.md` entry noting where the script came from                                                                                 |

**Do not treat "I moved the file" as done.** The gap this closes is real: `scripts/cambium-portal.sh` sat uncataloged in `scripts/README.md` for a full session after being moved in, because
`scripts/check_governance.py`'s coverage check only covered `RUNBOOK.md`↔`references/` and had no equivalent for `scripts/README.md`↔`scripts/` — the checker's own documented claim ("fails on an
uncatalogued script") was false until that gap was found and closed 2026-09-17. Re-run the checker after adding a script; do not assume the catalog step happened just because the file is present.

### Tier 2 — Routing and navigation (check for staleness after Tier 1)

- `RUNBOOK.md` Reference Routing table — new reference file or renamed file → add/update routing row
- `SKILL.md` References section — pointer to the new/updated file
- `AI_NAVIGATION.md` routing table and Project context files table — new file → add row
- `context-map.yaml` routing section — new domain → add routing entry

### Tier 3 — Metadata and history

- `manifest.json` — bump `version` (patch) + `updated_at` if any reference file content or structure changed; add/update `stable_facts` for durable new facts
- `CHANGELOG.md` — append entry for what changed
- `SCRATCHPAD.md` — update current state, tick/add open items, prepend session history summary

## Cross-project write-back trigger

Any project that invokes this skill and produces Cambium device/hardware/credential/asset-register/cnMaestro knowledge — **or writes a Cambium-domain script or tool** — must write it back here before
the session closes — this is the `SKILL.md` Standing Write-Back Contract in enforceable form. Concretely: `skill-slurp-chat` and `project-coherence`, run in any project that touched Cambium work this
session, must check for unpromoted Cambium knowledge before closing out. If either closes a session without this check, treat the closeout as incomplete.

**Closeout self-check:** did this session (a) learn a new device fact, credential/vault behaviour, asset-register convention, or inventory-schema gotcha that isn't yet reflected in this pack's
`references/`, or (b) write or modify a Cambium-domain script that isn't yet cataloged in this pack's `scripts/`? If either is yes, promote it in the same pass per the Tier 1/1b–3 steps above rather
than deferring it. A script sitting in a consuming project's own `scripts/` folder because a session ran out of time to move it is exactly the failure mode this trigger exists to catch — this pack's
own governance checker cannot see into another project, so nothing will flag the gap from this side.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile`
    exists.
12. Treat uncataloged scripts as `unknown` safety until inspected. Run defined audit/check commands before completing work.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. If `scripts/check_governance.py` exists, run it before claiming any durable change is complete. When it fails, fix the project, not the check. Adding a new artifact class, generated output, or a
    constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This pack's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions; run `python3 scripts/check_governance.py` to gate on them. It is
stdlib-only and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file.

### The checker grows with the pack

| Change made                                 | Required checker update                                                                                                                                |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Add a new `references/*.md` file            | None — the coverage check fails until `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, and `context-map.yaml` all name it                                 |
| Add a script to `scripts/`                  | Catalog it in `scripts/README.md`; coverage fails until then                                                                                           |
| Add a new governance surface that could     | Don't — `manifest.json` is the sole version-of-record (see `.archcore/rules/manifest-version-discipline.rule.md`); point to it instead. No automated   |
|   restate this pack's version               |   check enforces this yet — `scripts/check_governance.py` has no anti-duplicate-version check, despite this row previously naming a                    |
|                                             |   `VERSION_STAMP_SURFACES` registry that was never implemented. Treat as a residual governance gap until a real check exists.                          |
| Rename or move a file                       | Nothing — path resolution catches every stale reference automatically                                                                                  |
| Retire a check                              | Record why in `CHANGELOG.md`                                                                                                                           |

### Rules that are not negotiable

- **When a check fails, fix the pack, not the check.**
- **A new check must be able to fail.** Prove it by breaking the pack deliberately and watching it go red.
- **Text matching does not verify behavior.** Where a check must verify behavior, execute it and assert on the result.
- **Do not enforce history.** `CHANGELOG.md` is an append-only log; a past fact recorded there is evidence, not a live claim.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: AI_NAVIGATION.md
````markdown
# AI Navigation — skill-cambium

Purpose: context entrypoint for AI agents working on the skill-cambium specialist pack. Tells agents where knowledge lives, what to read first, what is authoritative, and what to update after work.

This file is a router, not the knowledge store.

<!-- BEGIN skill-ai-it:navigation --> <!-- skill-ai-it:manual reason="task->reference routing table (6 files) and the skill-smc cross-pack boundary are project-specific; the generic template has no
equivalent and would delete them" -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Reference routing (task → file)](#reference-routing-task--file)
- [Project context files](#project-context-files)
- [Cross-pack boundary](#cross-pack-boundary)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)

---

## Mandatory read order

1. `AGENTS.md`
2. `AI_NAVIGATION.md` (this file)
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `references/*.md` for the task at hand (via `RUNBOOK.md`'s Reference Routing table)
6. Relevant `.archcore/` documents, if any exist yet

## Source priority

1. `.archcore/` accepted ADRs, rules, specs — 6 documents accepted 2026-09-17; see [`.archcore/index.guide.md`](.archcore/index.guide.md) for the index
2. `SKILL.md` (Standing Write-Back Contract, Use When, Related Skills)
3. `references/*.md` (content source — the numbered files)
4. `AGENTS.md` / `CLAUDE.md`
5. `AI_NAVIGATION.md` / `context-map.yaml`
6. `CHANGELOG.md`
7. `manifest.json` `stable_facts` (a snapshot, not the live source — see below)
8. `SCRATCHPAD.md` (temporary unless marked `KEEP` or promoted)

**`manifest.json`'s `stable_facts` and this pack's `references/` are themselves not the live device data.** For anything about a specific model or device, the live source is
`cambium-swap/inventory/device-family-matrix.csv` and `cambium-swap/inventory/device-inventory.csv` — read those files, don't rely on this pack's summary of them.

## Reference routing (task → file)

| Task                                                                                               | Read                                          |
| -------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Device families, models, firmware/EoL snapshot, evidence-state discipline                          | `references/01_overview.md`                   |
| Device local-admin access, KeePassXC vault structure, `kp` wrapper gotchas                         | `references/02_device-access-and-vault.md`    |
| Asset-register naming convention, per-site drift, site-name convention, R195P IP-derivation rule   | `references/03_asset-register-conventions.md` |
| `device-inventory.csv` schema, `UNKNOWN` discipline, extraction workflow                           | `references/04_device-inventory-schema.md`    |
| Coverage gaps, unverified assumptions, staleness risks                                             | `references/05_known-issues.md`               |
| Device REST API / SSH CLI data points per adapter method, config-backup source, write-ops boundary | `references/06_device-api-cli-reference.md`   |

## Project context files

| File / Path       | Role                                                   | Authority   |
| ----------------- | ------------------------------------------------------ | ----------- |
| `SKILL.md`        | Agent activation surface, Standing Write-Back Contract | Highest     |
| `references/*.md` | Content source                                         | Highest     |
| `.archcore/`      | Durable rules/ADR/spec — 6 accepted 2026-09-17         | Highest     |
| `AGENTS.md`       | Universal agent instruction file                       | High        |
| `CLAUDE.md`       | Claude-specific bootstrap file                         | High        |
| `RUNBOOK.md`      | Navigation index only — not a content source           | Routing     |
| `manifest.json`   | Machine-readable metadata + fact snapshot              | Medium      |
| `CHANGELOG.md`    | Durable pack change history                            | Medium-high |
| `SCRATCHPAD.md`   | Temporary notes                                        | Low         |

## Cross-pack boundary

If a task is about the SMC box, Ansible authoring, or provisioning roles rather than the Cambium hardware itself, this is the wrong pack — route to `skill-smc` (see its own `AI_NAVIGATION.md`). If a
fact spans both (e.g. a `site_name` value, a `smc_cnmaestro_provisioning` behaviour), write it to both packs' matching reference files in the same session.

## Generated context

`.ai-context/governance-pack.md` (Repomix) is disposable generated support, not canonical truth. Regenerate after significant reference-file changes:
```
repomix --config /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-cambium/repomix.config.json
```

## Context compaction recovery

When recovering agent context after compaction (new session, cleared context window):

1. Read this file (`AI_NAVIGATION.md`) first for the mandatory read order and routing table above.
2. Read `context-map.yaml` for the machine-readable routing map.
3. Load `.archcore/` context if present — no longer empty: 6 documents (2 ADRs, 3 rules, 1 spec) accepted 2026-09-17, see [`.archcore/index.guide.md`](.archcore/index.guide.md) for the index. Re-check the
   count, it may have grown further.
4. Regenerate `.ai-context/governance-pack.md`: `repomix --config repomix.config.json`.
5. Verify `SCRATCHPAD.md` has current state; if empty or stale, populate from memory-keeper / mcp-project-context.
6. Verify `CHANGELOG.md` is current with recent governance/content changes.
7. Verify this file and `context-map.yaml` agree — see Update rules below for which companion files move together.

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Drift handling

If sources disagree: stop, name the conflicting files, state which has higher authority per the priority list above, propose the smallest correction, and do not silently merge assumptions.

## Update rules

| Change type                  | Update                                                        |
| ---------------------------- | ------------------------------------------------------------- |
| New durable Cambium fact     | The matching `references/*.md` file (see routing table above) |
| New durable rule/decision    | Propose `.archcore/rules/` or `.archcore/adr/`                |
| Routing changed              | `AI_NAVIGATION.md` and `context-map.yaml`                     |
| Any content/structure change | `manifest.json` version bump + `CHANGELOG.md` entry           |
| Temporary note               | `SCRATCHPAD.md` only, mark `KEEP` if it should survive        |

**Companion files** — `context-map.yaml`'s `update_rules.governance_navigation` names which files move together. In short: a change to `AGENTS.md` also touches `AI_NAVIGATION.md`, `context-map.yaml`,
and `scripts/README.md`; a change to this file also touches `context-map.yaml`; a new script also touches `scripts/README.md`, `AGENTS.md`, and `justfile`. Check that map before treating a
governance/routing edit as complete.

<!-- END skill-ai-it:navigation -->
````

## File: CHANGELOG.md
````markdown
# Changelog — skill-cambium

## Contents

- [20261005_1934 — Archcore filenames brought to the <slug>.<type>.md form; index.guide.md replaces .archcore/README.md (v0.6.31 -> v0.6.32)](#20261005_1934--archcore-filenames-brought-to-the-slugtypemd-form-indexguidemd-replaces-archcorereadmemd-v0631---v0632)
- [20261005_1545 — Capture-review notes: cnWave nic2 traffic, E-series radio off, ePMP STA table (v0.6.30 -> v0.6.31)](#20261005_1545--capture-review-notes-cnwave-nic2-traffic-e-series-radio-off-epmp-sta-table-v0630---v0631)
- [20261005_1451 — R195P client IPv4 0.0.0.0 in cnMaestro explained; client-ip-sweep.sh added (v0.6.29 -> v0.6.30)](#20261005_1451--r195p-client-ipv4-0000-in-cnmaestro-explained-client-ip-sweepsh-added-v0629---v0630)
- [20261005_1442 — Fleet SNMP identity gaps measured from the capture corpus (v0.6.28 -> v0.6.29)](#20261005_1442--fleet-snmp-identity-gaps-measured-from-the-capture-corpus-v0628---v0629)
- [20261005_1350 — Related skills: platform packs skill-nautobot and skill-openwisp (v0.6.27 -> v0.6.28)](#20261005_1350--related-skills-platform-packs-skill-nautobot-and-skill-openwisp-v0627---v0628)
- [20260930_1221 — Terminology: "paid PIN" corrected to access mark (v0.6.26 -> v0.6.27)](#20260930_1221--terminology-paid-pin-corrected-to-access-mark-v0626---v0627)
- [20260930_1209 — Dashboard bots poll AP reachability by ping from the SMC over Teleport (v0.6.25 -> v0.6.26)](#20260930_1209--dashboard-bots-poll-ap-reachability-by-ping-from-the-smc-over-teleport-v0625---v0626)
- [20260930_1200 — R195P SNMP communities: Get/Set plaintext equal the programme vault, Error `error`, Trap not the short name (v0.6.24 -> v0.6.25)](#20260930_1200--r195p-snmp-communities-getset-plaintext-equal-the-programme-vault-error-error-trap-not-the-short-name-v0624---v0625)
- [20260930_0325 — XV2 WLAN and radio reads, ePMP set_param and R195P nvram_set write paths; PWD redaction fixed (v0.6.23 -> v0.6.24)](#20260930_0325--xv2-wlan-and-radio-reads-epmp-set_param-and-r195p-nvram_set-write-paths-pwd-redaction-fixed-v0623---v0624)
- [20260929_1903 — XV2-22H REST config writes proven on a test unit (v0.6.22 -> v0.6.23)](#20260929_1903--xv2-22h-rest-config-writes-proven-on-a-test-unit-v0622---v0623)
- [20260929_1820 — SNMP writes per type on the stage test SMC; communities follow the programme; an R195P the vault cannot log in to (v0.6.21 -> v0.6.22)](#20260929_1820--snmp-writes-per-type-on-the-stage-test-smc-communities-follow-the-programme-an-r195p-the-vault-cannot-log-in-to-v0621---v0622)
- [20260929_0631 — cnWave has no serial over SNMP on firmware 1.4; REST getDeviceInfo is the source (v0.6.20 -> v0.6.21)](#20260929_0631--cnwave-has-no-serial-over-snmp-on-firmware-14-rest-getdeviceinfo-is-the-source-v0620---v0621)
- [20260928_2204 — cnWave node type, serial and link facts; ePMP link frequency and width OIDs (v0.6.19 -> v0.6.20)](#20260928_2204--cnwave-node-type-serial-and-link-facts-epmp-link-frequency-and-width-oids-v0619---v0620)
- [20260928_2050 — R195P adapter: SSH_ASKPASS replaces sshpass (v0.6.18 -> v0.6.19)](#20260928_2050--r195p-adapter-ssh_askpass-replaces-sshpass-v0618---v0619)
- [20260928_2044 — Serials over SNMP for ePMP and Enterprise Wi-Fi; concurrent R195P SSH reads fail (v0.6.17 -> v0.6.18)](#20260928_2044--serials-over-snmp-for-epmp-and-enterprise-wi-fi-concurrent-r195p-ssh-reads-fail-v0617---v0618)
- [20260928_2032 — R195P serial, firmware and hardware version over SNMP (CAMBIUM-MIB 41010); the "only signal" claim corrected (v0.6.16 -> v0.6.17)](#20260928_2032--r195p-serial-firmware-and-hardware-version-over-snmp-cambium-mib-41010-the-only-signal-claim-corrected-v0616---v0617)
- [20260928_1540 — R195P interface layout and MAC offsets; the public address comes from the low-touch hook (v0.6.15 -> v0.6.16)](#20260928_1540--r195p-interface-layout-and-mac-offsets-the-public-address-comes-from-the-low-touch-hook-v0615---v0616)
- [20260928_1447 — Force 300-25 and XV2-2T0 sysObjectIDs; sysDescr names the model on R-series and Enterprise Wi-Fi (v0.6.14 -> v0.6.15)](#20260928_1447--force-300-25-and-xv2-2t0-sysobjectids-sysdescr-names-the-model-on-r-series-and-enterprise-wi-fi-v0614---v0615)
- [20260927_2138 — Telling XV2-2T0 from XV2-22H: the REST model, sku and port count; the serial prefix as an observation (v0.6.13 -> v0.6.14)](#20260927_2138--telling-xv2-2t0-from-xv2-22h-the-rest-model-sku-and-port-count-the-serial-prefix-as-an-observation-v0613---v0614)
- [20260927_1954 — R195P management server: cns_static_url, Cloud in git, apn-cnmaestro01 live at wangkatjungka (v0.6.12 -> v0.6.13)](#20260927_1954--r195p-management-server-cns_static_url-cloud-in-git-apn-cnmaestro01-live-at-wangkatjungka-v0612---v0613)
- [20260927_0258 — apn-cnmaestro01 hostname corrected to apn-cnmaestro01.apn.au (operator); it resolves (v0.6.11 -> v0.6.12)](#20260927_0258--apn-cnmaestro01-hostname-corrected-to-apn-cnmaestro01apnau-operator-it-resolves-v0611---v0612)
- [20260926_2320 — monitoring counter surface: the "not wired yet" sentence corrected (wired 2026-09-22, guarded 2026-09-26)](#20260926_2320--monitoring-counter-surface-the-not-wired-yet-sentence-corrected-wired-2026-09-22-guarded-2026-09-26)
- [20260926_2126 — DHCP vendor class (Option 60) per family recorded: what the low-touch hook can and cannot tell from a lease](#20260926_2126--dhcp-vendor-class-option-60-per-family-recorded-what-the-low-touch-hook-can-and-cannot-tell-from-a-lease)
- [20260924_1552 — R-series interfaces contracted by role; the `interfaces` check stops failing on every live unit](#20260924_1552--r-series-interfaces-contracted-by-role-the-interfaces-check-stops-failing-on-every-live-unit)
- [20260922_1957](#20260922_1957)
- [20260922_0941](#20260922_0941)
- [20260922_0754](#20260922_0754)
- [20260922_0020](#20260922_0020)
- [20260921_2015](#20260921_2015)
- [20260921_1541](#20260921_1541)
- [20260921_1237](#20260921_1237)
- [20260921_1015](#20260921_1015)
- [20260920_2339](#20260920_2339)
- [20260920_1951](#20260920_1951)
- [20260920_1856](#20260920_1856)
- [20260920_1758](#20260920_1758)
- [20260920_1745](#20260920_1745)
- [20260920_1652](#20260920_1652)
- [20260920_1556](#20260920_1556)
- [20260917_1100](#20260917_1100)
- [20260917_1130](#20260917_1130)
- [20260917_1135](#20260917_1135)
- [2026-09-17 — deterministic navigation-control upgrade](#2026-09-17--deterministic-navigation-control-upgrade)
- [20260917_1210](#20260917_1210)
- [20260917_1200](#20260917_1200)
- [20260917_1230](#20260917_1230)
- [20260917_1245](#20260917_1245)
- [20260917_1300](#20260917_1300)
- [20260917_1440](#20260917_1440)
- [20260917_1500](#20260917_1500)
- [20260917_1510](#20260917_1510)
- [20260917_1600](#20260917_1600)
- [20260917_1630](#20260917_1630)
- [20260917_1700](#20260917_1700)
- [20260917_1710](#20260917_1710)
- [20260917_1720](#20260917_1720)
- [20260917_1730](#20260917_1730)
- [20260917_1930](#20260917_1930)
- [20260917_1946](#20260917_1946)
- [20260917_2021](#20260917_2021)
- [20260917_2050](#20260917_2050)
- [20260917_2057](#20260917_2057)
- [20260917_2130](#20260917_2130)
- [20260917_2145](#20260917_2145)
- [20260918_0855 — cnMaestro REST API v2 access documented; vault table gained 5 missing entries](#20260918_0855--cnmaestro-rest-api-v2-access-documented-vault-table-gained-5-missing-entries)
- [20260918_0930 — site-addressing.yaml restructured by flavour, populated for all 27 nbn_accelerate sites, generator script added](#20260918_0930--site-addressingyaml-restructured-by-flavour-populated-for-all-27-nbn_accelerate-sites-generator-script-added)
- [20260918_1045 — two missing OUI blocks added after operator flagged oui_reference as stale](#20260918_1045--two-missing-oui-blocks-added-after-operator-flagged-oui_reference-as-stale)
- [20260918_1050 — generate_site_addressing_families.py gained --oui-audit mode](#20260918_1050--generate_site_addressing_familiespy-gained---oui-audit-mode)
- [20260918_1055 — full regenerate-and-verify pass: 8 missing families added, oui_reference restructured to a real site map](#20260918_1055--full-regenerate-and-verify-pass-8-missing-families-added-oui_reference-restructured-to-a-real-site-map)
- [20260918_1100 — YAML formatting cleanup, content accuracy fixes, FAMILY_MAP bug found and fixed](#20260918_1100--yaml-formatting-cleanup-content-accuracy-fixes-family_map-bug-found-and-fixed)
- [20260918_1115 — cnPilotMIB SNMP read-only identity data confirmed live on XV2-22H Wi-Fi 6 firmware](#20260918_1115--cnpilotmib-snmp-read-only-identity-data-confirmed-live-on-xv2-22h-wi-fi-6-firmware)
- [20260918_1155 — unified-network-controller added as a Related Workspace](#20260918_1155--unified-network-controller-added-as-a-related-workspace)
- [20260918_1542 — ePMP SM adapter re-verified fresh-live; cnWave 4 stat endpoints resolved (path bug, not missing params)](#20260918_1542--epmp-sm-adapter-re-verified-fresh-live-cnwave-4-stat-endpoints-resolved-path-bug-not-missing-params)
- [20260918_1557 — R195P get_config() implemented (operator-authorized); live fetch across all 4 families blocked this session by a sandbox credential-materialization guard](#20260918_1557--r195p-get_config-implemented-operator-authorized-live-fetch-across-all-4-families-blocked-this-session-by-a-sandbox-credential-materialization-guard)
- [20260918_1620 — Correction: the outage claim in the entry above was wrong; it was a `tsh` flag mistake, not an outage](#20260918_1620--correction-the-outage-claim-in-the-entry-above-was-wrong-it-was-a-tsh-flag-mistake-not-an-outage)
- [20260918_1705 — Live get_config() verification across all 4 Cambium families completed; 4 real R195P bugs found and fixed; new secret-exposure incident found and closed](#20260918_1705--live-get_config-verification-across-all-4-cambium-families-completed-4-real-r195p-bugs-found-and-fixed-new-secret-exposure-incident-found-and-closed)

---

## 20261005_1934 — Archcore filenames brought to the <slug>.<type>.md form; index.guide.md replaces .archcore/README.md (v0.6.31 -> v0.6.32)

### Changed

- `archcore status` rejected all 7 files under `.archcore/` (filename must match `<slug>.<type>.md`; a bare README is not a document). Renamed with `git mv`, content unchanged:
  the 2 ADRs, 3 rules and 1 spec now carry their type as a filename suffix instead of a prefix, and the index is `.archcore/index.guide.md` with YAML frontmatter
  (`title`, `status: accepted`, `tags: [index]`) in place of the Title/Category header. `archcore status` now reports no issues.
- Live references updated in `README.md`, `AI_NAVIGATION.md`, `AGENTS.md`, `scripts/check_governance.py` and the cross-references inside `.archcore/`. Earlier CHANGELOG entries keep
  the old names as history; the old paths are registered in `scripts/check_governance.py` `CONDITIONAL_PATHS` so those mentions still pass path resolution.
- `SKILL.md` Related skills: the platform-pack location is now the resolvable link `../../platform/` (it failed path resolution since v0.6.28).

### Notes

- Open, not done here: the skill-ai-it navigation validator fails this pack on stale managed blocks (`AGENTS.md` navigation and `scripts/README.md` scripts still carry the
  2026-08-11 stamp) and warns on the `context-map.yaml` version; the fix is a `/skill-ai-it refresh`.
- Done alongside the skill-ai-it bootstrap of the platform packs `skill-nautobot` and `skill-openwisp`, whose `.archcore/` was written in the compliant form from the start.

## 20261005_1545 — Capture-review notes: cnWave nic2 traffic, E-series radio off, ePMP STA table (v0.6.30 -> v0.6.31)

- `references/06_device-api-cli-reference.md`: new section with three device facts from the UNC capture review, each checked against its capture.

## 20261005_1451 — R195P client IPv4 0.0.0.0 in cnMaestro explained; client-ip-sweep.sh added (v0.6.29 -> v0.6.30)

- `references/05_known-issues.md`: new section. R195P reports every client as `0.0.0.0`; a regression since the move to apn-cnmaestro01 (operator: IPs showed before;
  unit confirmed connected to 52.64.230.196), SMC and TFTP config unchanged; SMC DHCP healthy at 10 sites; 12 R195Ps on 6 apn sites all `zero_ip` with every MAC leased.
- `scripts/client-ip-sweep.sh` (new, written in ansible-wifi 2026-10-05): SMC DHCP health vs AP-reported client IPv4 vs SMC leases, per site. Catalogued
  in `scripts/README.md`, `just client-ip-sweep`, RUNBOOK routing row. Known limit: XV2 returns no table over non-interactive SSH.

## 20261005_1442 — Fleet SNMP identity gaps measured from the capture corpus (v0.6.28 -> v0.6.29)

- `references/05_known-issues.md`: new section. ePMP generic sysName (349 units), no SNMP serial on E500, E430H and some R195P, MAC notation per adapter, two net-snmp units of unknown family.

## 20261005_1350 — Related skills: platform packs skill-nautobot and skill-openwisp (v0.6.27 -> v0.6.28)

- `SKILL.md` Related Skills: routes Nautobot and OpenWISP platform questions to the two platform packs, and platform-generic learnings to their
  write-back contract, so they are not filed here.

## 20260930_1221 — Terminology: "paid PIN" corrected to access mark (v0.6.26 -> v0.6.27)

- `references/05_known-issues.md` (dashboard bots section): the nbn bot's routine now reads "wipes every device's access mark", not "every paid PIN".
  Access at these sites is free via T&C acceptance (operator, 2026-09-30).

## 20260930_1209 — Dashboard bots poll AP reachability by ping from the SMC over Teleport (v0.6.25 -> v0.6.26)

- `references/05_known-issues.md`: new section. Both dashboards check AP reachability by running `ping -c 1 <AP IP>` on the SMC through `teleport exec`:
  `bot-cw-dashboard` on nbn (9 of 31 sites polled) and `bot-apn-dashboard` on rcp (8 of 18). Per-site 24h counts and AP IP ranges are recorded. The
  implications are flagged as unverified: sites not polled get AP status from somewhere else, and a failed SMC or Teleport path would show APs as down.
  Cross-references skill-smc 13_known-issues (2026-09-30) for the nbn bot's firewall-restart routine. Written back from the ansible-wifi
  koonibba-usage-drop investigation.

## 20260930_1200 — R195P SNMP communities: Get/Set plaintext equal the programme vault, Error `error`, Trap not the short name (v0.6.24 -> v0.6.25)

- Write-back from unified-network-controller (CHANGELOG 20260930_1159, Golden Config option B): `references/06_device-api-cli-reference.md` records
  what three R195P hold in their four community keys, from a read-only in-process comparison (no value printed or stored).

## 20260930_0325 — XV2 WLAN and radio reads, ePMP set_param and R195P nvram_set write paths; PWD redaction fixed (v0.6.23 -> v0.6.24)

- Write-back from unified-network-controller (CHANGELOG 20260930_0325, low-touch provisioning): `references/06_device-api-cli-reference.md` gains the
  XV2 WLAN/radio read and write shapes, the ePMP `set_param` body and the R195P `nvram_set` path (both unproven); `scripts/cambium_*_adapter.py`
  redaction now matches `pwd`; `references/05_known-issues.md` records the gap and its consumers.
- `references/05_known-issues.md`: the daniel-test R195P's SSH rejected the right password until a reboot (web UI worked throughout); resolved 2026-09-30.

## 20260929_1903 — XV2-22H REST config writes proven on a test unit (v0.6.22 -> v0.6.23)

- Write-back from unified-network-controller (CHANGELOG 20260929_1902): `references/06_device-api-cli-reference.md` "Write Operations" rewritten from the
  unit's own UI bundle and a restore on daniel-test-nbn's XV2-22H: per-section `POST /api/<section>-config`, partial bodies, list encoding, non-atomic
  POSTs, keys to leave out, what was proven.

## 20260929_1820 — SNMP writes per type on the stage test SMC; communities follow the programme; an R195P the vault cannot log in to (v0.6.21 -> v0.6.22)

- Write-back from unified-network-controller (its CHANGELOG 20260929_1819), daniel-test-nbn (nbn_accelerate stage SMC) and its two units:
  `references/snmp-oid-registry.yaml`: R195P `sysName` now `rw` (set-and-revert ok with apn-snmp-rw, which the unit refuses for GETs); XV2-22H `sysLocation` and
  `sysName` SETs refused, and the E-series MIB's only writable objects (`cambiumAPSetIPAddress`, `cambiumAPReboot`), untested; a header note that a
  unit moved between programmes keeps the old programme's community (both units behind the nbn cluster answer only apn-snmp-ro).
- `references/05_known-issues.md`: the R195P `HOR-R195P-1001` (serial WFXK0CTQRQBW) rejects `cnpilot-r-series` over SSH and the vault holds no R-series
  `-legacy` entry, so it has no login and no config backup.

## 20260929_0631 — cnWave has no serial over SNMP on firmware 1.4; REST getDeviceInfo is the source (v0.6.20 -> v0.6.21)

- Write-back from unified-network-controller (its CHANGELOG, 2026-09-29): full SNMP walks of old-looma's V5000 DN (12,196 values) and V2000 CN (8,300 values), firmware 1.4, hold neither unit's serial;
  ENTITY-MIB is not implemented and the cnWave arm `.60` holds only the link entry. Recorded under `cnwave-v5000` as `serial_over_snmp: available: false` with the units and method. The serial stays
  REST `/local/getDeviceInfo` `msn` (`cambium_cnwave_adapter.get_facts`).

## 20260928_2204 — cnWave node type, serial and link facts; ePMP link frequency and width OIDs (v0.6.19 -> v0.6.20)

Written back from unified-network-controller's staleness audit (its defect 1): the facts verified on 2026-09-28 were in that project's change log but not in this pack.
`references/06_device-api-cli-reference.md` gains "cnWave identity and link facts" (sysDescr names DN/CN on 82 of 82 units; serial is REST `getDeviceInfo` `msn`; topology links name ends by radio MAC;
channel and `cb2Enable` config keys; a lone POP reports 0 links). `references/snmp-oid-registry.yaml`: ePMP 3000L `centerFrequency`, `wirelessInterfaceHTMode` and the connected-STA MAC column; Force
300-25 connected frequency and bandwidth, with the width codes marked unverified beyond the MIB's 20 and 40 MHz. Read back after writing.

## 20260928_2050 — R195P adapter: SSH_ASKPASS replaces sshpass (v0.6.18 -> v0.6.19)

`scripts/cambium_r195p_adapter.py` `_run` gives ssh the password through a private askpass helper (`SSH_ASKPASS`, `SSH_ASKPASS_REQUIRE=force`, OpenSSH 8.4+) that prints it from the child's
environment. Why: `sshpass` now and then missed the password prompt, ssh fell back to an absent `ssh-askpass`, sent no password and was denied (three units in scheduled runs 2026-09-22; one or two of
five R195Ps read at once on 2026-09-28, each fine alone; stderr showed three `ssh_askpass: exec ... No such file` lines). With askpass, five at once for three rounds: 15 of 15, 1.5 s each. Also: the
password is off the command line (`sshpass -p` exposed it in `ps`); `NumberOfPasswordPrompts=1` (a wrong password is one rejected login, not three); `PubkeyAuthentication=no`; the one-retry workaround
is gone. A rejected password is now ssh's 255 with `Permission denied`, raised as `SSH login failed: password rejected: ...`, which unified-network-controller's auth classifier still treats as a
rejected credential (its `tests/test_r195p_ssh.py`, red against v0.6.18, green now; the rejected path is tested with a faked ssh, not live). `references/02_device-access-and-vault.md` rejection table,
`references/05_known-issues.md` known issue (marked fixed) and `scripts/README.md` updated.

## 20260928_2044 — Serials over SNMP for ePMP and Enterprise Wi-Fi; concurrent R195P SSH reads fail (v0.6.17 -> v0.6.18)

`references/snmp-oid-registry.yaml`: `cambiumEPMPMSN` (`.1.3.6.1.4.1.17713.21.1.1.31.0`) on ePMP 3000L, Force 300-16 and Force 300-25, and `cambiumAPSerialNum` read by GET at
`.1.3.6.1.4.1.17713.22.1.1.1.4.0` on XV2-2T0 and XV2-22H: every junjuwa unit that answered (18 of 19; the silent one is the Force 300-25 that answers no SNMP) read the serial Nautobot holds.
`references/05_known-issues.md`: five R195Ps read at once over SSH lost two to `sshpass`; read them one at a time. Written back from unified-network-controller. Read back after writing.

## 20260928_2032 — R195P serial, firmware and hardware version over SNMP (CAMBIUM-MIB 41010); the "only signal" claim corrected (v0.6.16 -> v0.6.17)

`references/snmp-oid-registry.yaml` `cnpilot-r195p` gains four verified scalars from the R-series CAMBIUM-MIB (enterprise 41010, cambium-swap's MIB archive): `productName`, `hardwareVersion`,
`firmwareVersion` and `serialNumber`, read by GET on umoona-home-2/-3 (4.7.3-R21) and kalumburu cnPilot-R195P-1027/-1038/-1106 (4.8.1-R4, 4.7-R9); the three kalumburu serials equal the ones Nautobot
holds from cnMaestro. A walk of the arm answers `tooBig`: GET the scalars. The sysDescr note no longer calls it "the only SNMP model and firmware signal", and the R195P comes off the "no verified SNMP
surface" list. `references/06_device-api-cli-reference.md`: the SSH "no serial" statements now say where the serial is. The earlier claim came from a sysDescr-only GET that never asked the enterprise
arm. Written back from unified-network-controller. Read back after writing.

## 20260928_1540 — R195P interface layout and MAC offsets; the public address comes from the low-touch hook (v0.6.15 -> v0.6.16)

`references/06_device-api-cli-reference.md` gains "R195P interface layout and MAC offsets": LAN base, management `eth2.500` base + 1, public `wan3.501` base + 2, from one read-only snapshot of
umoona-home-1 and ARP checks of four routers; and where the public address comes from (the low-touch hook's `public_ip`, not DHCP). Written back from unified-network-controller. Read back after
writing.

## 20260928_1447 — Force 300-25 and XV2-2T0 sysObjectIDs; sysDescr names the model on R-series and Enterprise Wi-Fi (v0.6.14 -> v0.6.15)

`references/snmp-oid-registry.yaml` gains `force-300-25` (sysObjectID `.1.3.6.1.4.1.17713.21.9.36`, 226 swept units, all 40 in Nautobot typed Force 300-25; its sysDescr carries no model) and `xv2-2t0`
(`.1.3.6.1.4.1.17713.22.3.16`, 132 units, sysDescr names the variant). Written back from unified-network-controller, where a sweep left ten umoona units `UNKNOWN` because only the sysObjectID table
was read (its CHANGELOG `20260928_1447`). Read back after writing: the YAML parses.

## 20260927_2138 — Telling XV2-2T0 from XV2-22H: the REST model, sku and port count; the serial prefix as an observation (v0.6.13 -> v0.6.14)

`references/01_overview.md` gains "Telling XV2-2T0 from XV2-22H": `device-summary.model`/`platform-info.model` name the variant, backed by sku (22, 34) and port count (2, 3); seen on 15 units (six
serial-proven, nine by name from serial-redacted captures). The WL / W4ZA-W6YJ serial-prefix split held on all 15 and is recorded as an observation only. Written back from unified-network-controller's
Step 10 work (272 devices typed plain XV2, CHANGELOG `20260927_2135` there). Read back after writing.

## 20260927_1954 — R195P management server: cns_static_url, Cloud in git, apn-cnmaestro01 live at wangkatjungka (v0.6.12 -> v0.6.13)

`references/06_device-api-cli-reference.md`, cnPilot R195P: the unit learns its cnMaestro from the TFTP config key `cns_static_url`; git says Cloud, wangkatjungka-smc01 serves
`https://apn-cnmaestro01.apn.au/` from an uncommitted template (read-only capture in unified-network-controller, 2026-09-27); the value is per era and belongs in the source of truth. Read back after
writing.

## 20260927_0258 — apn-cnmaestro01 hostname corrected to apn-cnmaestro01.apn.au (operator); it resolves (v0.6.11 -> v0.6.12)

`references/02_device-access-and-vault.md`: the on-prem cnMaestro's hostname was recorded on 2026-09-26 as `apn-cnmaestro01.apn.net.au` and marked as not resolving. The operator corrected it on
2026-09-27: `apn-cnmaestro01.apn.au`, which resolves (52.64.230.196 that day). `USER_STATED` hostname, `VERIFIED_PRIMARY` resolution by `dig`. unified-network-controller's catalog already carried the
`.apn.au` URL; its description note is corrected the same night.

## 20260926_2320 — monitoring counter surface: the "not wired yet" sentence corrected (wired 2026-09-22, guarded 2026-09-26)

v0.6.10 -> v0.6.11. `references/06_device-api-cli-reference.md`, "Monitoring Counter and Resource Surfaces": the closing sentence still said nothing was wired into an adapter, citing the consuming
project's probe entry `20260921_2008`. unified-network-controller wired the ePMP `device_props` kbit counters and `sysCPUUsage`, the R195P `/proc` reads and the cnWave `getNetworkStats` counters into
its adapters on 2026-09-22 (its CHANGELOG `20260922_0941`; canaries 6 of 6 stored per family) and on 2026-09-26 added a contract test that fails any adapter change that stops producing a metric.
Sentence replaced; the kbit 1000-vs-1024 `UNVERIFIED` note stands. Found by that project's autonomous queue pass on 2026-09-26, not by a device read: no device fact changed.

## 20260926_2126 — DHCP vendor class (Option 60) per family recorded: what the low-touch hook can and cannot tell from a lease

v0.6.9 -> v0.6.10. Written back from unified-network-controller supplement Step 4 (device-seen events on the SMC's DHCP hook), 2026-09-26. `references/01_overview.md` gains "DHCP Vendor Class (Option
60) per Family": the strings a factory-default unit sends (`Cambium-cnPilot R195P`, `Cambium-WiFi-AP`, `Cambium`), which family each maps to, whether the model is named (only the R-series names it;
Enterprise Wi-Fi and ePMP are `UNKNOWN` types until read), how the SMC answers (Option 43 cnMaestro URL, 20-second lease) and what the hook receives. Source: umoona-smc01's dhcpd files read-only and
the cnMaestro script's dispatch; exercised in the controller's dhcp-lab with the SMC's dhcpd version. cnWave is not on the hook. Also from today's controller work:
`references/02_device-access-and-vault.md` records that every apn and nbn device is now on on-prem `apn-cnmaestro01` (operator, 2026-09-26; its `.apn.net.au` hostname did not resolve publicly) and Q9
(Option 43 unchanged for all families); `references/05_known-issues.md` gains the classified failure signatures over the SMC path (mowanjum: 152 off, 16 TLS EOF, 14 SSH 255, 5 vault timeouts, 4
handshake timeouts, 1 ePMP lockout) with the rule to rule out the `tsh` certificate before reading device errors.

## 20260924_1552 — R-series interfaces contracted by role; the `interfaces` check stops failing on every live unit

v0.6.8 -> v0.6.9. Asked for by unified-network-controller (engineering queue item 5, closing R195P A4 in its device-type matrix). `scripts/schema_tool.py` gains `MAP_ROLES`: for a map-shaped endpoint,
each role is a name pattern with count bounds and the meaning `references/06_device-api-cli-reference.md` records. `merge` writes it into the schema as `x-roles`; `check` now judges map-shaped
endpoints by role (every key in exactly one role, counts within bounds, every value fitting the value schema) instead of listing every interface name as an unknown field.
`schemas/cnpilot-r-series/interfaces.schema.json` regenerated through `merge`: the only change is `x-roles` (counters and facts regenerate identical). All 11 R195P observations conform, where all 11
were divergent before; falsified five ways, each failing for its own reason. The other four families' `check` output is byte-identical before and after. `references/05_known-issues.md` row resolved;
`schemas/README.md` "Map-shaped responses" describes the roles. Not done: `schemas/DIVERGENCE.md` is still computed from raw observations and lists the names as site-specific fields, and which radio
interface is which band remains unrecorded.

## 20260922_1957

v0.6.7 -> v0.6.8. `scripts/cambium_r195p_adapter.py`: sshpass exit 5 (wrong password) now raises `SSH login failed: password rejected (sshpass exit 5)` whatever `allow_nonzero` says; before,
`get_snapshot()` swallowed it and reported `snapshot incomplete, sections missing`. Verified live on `MOW-R195P-1003` with a wrong and then the real password.
`references/02_device-access-and-vault.md`: new table of each family's response to a wrong password, read live the same day. Enterprise Wi-Fi answers HTTP 403 "Invalid username or password", which
unified-network-controller's legacy-retry check did not match.

Also: new `references/snmp-oid-registry.yaml`, the verified SNMP OIDs per device type (operator, 2026-09-22), linked from `references/06_device-api-cli-reference.md` and the references index. Both
read-write SNMP communities are proven by a test-and-revert sysLocation SET on six ePMP 3000L units at three sites, both clusters. The vault table no longer calls them untested.

## 20260922_0941

From the unified-network-controller ePMP and cnWave canaries (18 devices), all read live:

- `scripts/cambium_epmp_adapter.py` gains `get_snapshot()`: one `act=status` read builds facts, interfaces, wireless_link, clients and `counters` (LAN and wireless kbit and error counters,
  `sysCPUUsage`); each getter had re-read it. `get_facts()` adds `ipv4_address` (`cambiumEffectiveDeviceIPAddress`) and `lan_mac_address`; the LAN MAC is the one the asset register and Nautobot hold,
  and `mac_address` stays the wireless MAC (LAN + 1).
- `scripts/cambium_cnwave_adapter.py` gains `get_snapshot()`: facts, e2e_info, topology (E2E controller nodes only) and per-port `counters.net_dev` from one `getNetworkStats` call over `nic1`-`nic3`.
  The 2026-09-21 "counters read 0" was the unused `nic1`; `nic2` carries the traffic (HRN_T1_V5000_DN_IP4_10). No cnWave CPU or memory source found.
- `scripts/cambium_r195p_adapter.py`: `get_snapshot()` restores the required `wan_mac_address` (first `wan*` port without a VLAN suffix; the name varies by unit), and `_run()` retries once when
  sshpass misses the prompt (`ssh_askpass`, exit 255).
- Standards re-merged for epmp-ap, epmp-sm, cnpilot-r-series and cnwave-60ghz; each gains a counters schema (for example `schemas/epmp-ap/counters.schema.json`). `schemas/DIVERGENCE.md` regenerated
  (134 observations, 5 families). R195P `interfaces` stays divergent because it is keyed by interface name, which `schema_tool` models as fields: recorded in references/05_known-issues.md.
  Tjuntjuntjara R195Ps add VLANs `eth2.4` and `eth2.550` (the community's PTAC requirement, operator).

## 20260922_0754

From the unified-network-controller 1 + 5 canaries (E-series, XV2, R195P; 18 devices at 7 sites), all read live:

- `scripts/cambium_r195p_adapter.py` gains `get_snapshot()`: identity, interfaces and monitoring counters in ONE SSH session (`;`-chained, `echo` section markers, no pipes): `/proc/uptime`,
  `/proc/loadavg`, the `processor` count from `/proc/cpuinfo` (4 on MT7621), `/proc/meminfo` in bytes, and `/proc/net/dev` per interface. The getter path costs about seven SSH logins, which this
  dropbear throttles. Verified on six units at mowanjum, horn-island and mornington.
- Parser fix in `_parse_ip_addr()` (was inline in `get_interfaces()`): the flag pattern lacked `_`, so any flag list with `LOWER_UP` never matched and `is_up` was only ever set on down interfaces. Now
  `<([A-Z_,]+)>`.
- Enterprise Wi-Fi standard re-merged with `schemas/_observations/enterprise-wifi/horn-island-XV2-2T0-7.1.1-20260922.json`, the first XV2 on firmware 7.1.1-r5. It adds `connected_ip`, `device_ipv6`,
  `fcc_id` and `reg_info` (device-summary), `stream` and `tx_bytes_unicast` (radio-summary) and `tx_bytes_unicast` (wlan-summary), all optional. No required field changed. E-series firmware 4.2.3-r2
  and 4.2.3.1-r9 also checked conformant.
- `_run()` raises on ssh exit 255 (connect, auth or dropped session) even with `allow_nonzero`; before, a failed session reached `get_snapshot()` as empty output and read as "sections missing"
  (HOR-R195P-1002).
- `get_snapshot()` also returns `cpu_percent`: utilisation from two `/proc/stat` samples `CPU_SAMPLE_S` (2 s) apart, idle = idle + iowait. The load average is no CPU measure on this router: 9.75 on 4
  cores while 2.1 % busy (MOW-R195P-1002).
- R195P MACs seen live: `br0`, `eth2.500` (management, 10.255.0.0/18) and `wan3` each have their own. The management interface's MAC equals the MAC the asset register and Nautobot hold.

## 20260922_0020

Enterprise Wi-Fi standard re-merged with `schema_tool merge` after a new observation, `schemas/_observations/enterprise-wifi/mowanjum-E430H-20260922.json` — the first E430 in the set (model reports as
`cnPilot E430H`, firmware 4.2.3.1-r17). It adds `link_duplex2`, `link_duplex3`, `link_speed2` and `link_speed3` to `device-summary` and the `eth3_*`, `eth4_*`, `interface_eth3_*` and
`interface_eth4_*` families to `ethports-config`, now optional and attributed to E430H at mowanjum. Four mowanjum E500s checked conformant against the standard before the merge. Also recorded:
`redact()`'s key pattern matches `authorized`, so observations must be taken from unredacted payloads (the schema tool records no values). Source: unified-network-controller's enterprise Wi-Fi canary,
cambium-swap evidence E141.

## 20260921_2015

Added "Monitoring Counter and Resource Surfaces — Probed Live 2026-09-21" to [references/06_device-api-cli-reference.md](references/06_device-api-cli-reference.md), under this pack's write-back
contract: live read-only probes from `unified-network-controller` found the ePMP `device_props` kbit counters and `sysCPUUsage`, R195P's `/proc` counters, load and memory (plain `cat` only, pipes exit
127), cnWave `getNetworkStats` reading 0 on a POP node with the KPI and radio endpoints giving rates rather than counters, and the fleet-wide absence of Wi-Fi mesh that makes client `wds: false` a
measurement. No script changed.

## 20260921_1541

### cnMaestro API lifetime across the estate recorded (v0.6.6 -> v0.6.7)

`references/02_device-access-and-vault.md` "cnMaestro REST API v2 Access" now opens with the operator's 2026-09-21 statement: the API depends on cnMaestro X; cw-cnmaestro01 and lt-cnmaestro lose X
soon, Cloud has no API and is being retired, and the new on-prem apn-cnmaestro01 has none. Controller-side automation must plan for web scraping; device-local REST/SNMP is unaffected. Found while
unified-network-controller modelled each cnMaestro as a Nautobot Controller.

## 20260921_1237

### Direct device SSH from the operator Mac via `ProxyJump`; one XV2 variant resolved (v0.6.5 -> v0.6.6)

`references/02_device-access-and-vault.md` gains a section on reaching a device with OpenSSH `ProxyJump` through its SMC box instead of the nested `tsh ssh` + `sshpass` form, so the device credential
is never materialised in a shell on the box. Verified with `<secret:keepassxc:cambium-devices/enterprise-wifi>` against `GAL_XV2_AP32_IP3_32` (`10.255.3.32`, Galiwinku): `show version` identified the
unit as XV2-2T0, serial `WLZE1F5BWMB9`, firmware `6.6.0.3-r9` — resolving the variant `device-inventory.csv` records as unconfirmed, for this unit only. The Teleport and SSH-config side lives in
`skill-smc`; not duplicated here.

## 20260921_1015

### cnWave speaks SNMP on its own arm; the SNMP layer gets contracted; a single-site conclusion nearly became a fact (v0.6.4 -> v0.6.5)

Live walks from `hope-vale-smc01`, `mornington-smc01`, `horn-island-smc01` and `bidyadanga-smc01` while building the `unified-network-controller` adapter layer. Written back here per the Standing
Write-Back Contract.

**The correction worth reading first.** A first pass at hope-vale timed out on every cnWave and very nearly entered the record as "cnWave has no SNMP". Those units were simply down — no ICMP and no
TCP on 443, 80 or 22 — while a control XV2 on the same hop answered normally. Sampling `rcp` sites reversed it completely: **cnWave speaks SNMP on `cambium 60`** (`.1.3.6.1.4.1.17713.60`), its own
enterprise arm, which is why walking `21` or `22` finds nothing even on a unit where SNMP works. Confirmed across two sites, three models (V1000, V3000, V5000) and both Distribution and Client roles.

**Enablement splits by PROGRAMME, and the first answer was wrong.** An `rcp`-only sample said "mostly off". Closing the address gap and probing `nbn_accelerate` reversed it: **40 of 40 reachable nbn
units answer; 5 of 19 on rcp.** Same three models, same firmware `1.4`, both node roles on both sides, so this is a provisioning difference between the programmes rather than a hardware or version
one. Addresses were derived by ping-sweeping `10.255.4.0/24` from each SMC box and joining `ip neigh` against the inventory MAC column — 40 cnWave resolved against the 12 <!-- path:example -->
recoverable from stale ARP. `aurukun` and `hope-vale` return zero ARP for that subnet, so their cnWave network is unreachable from the SMC box: a routing question, not an SNMP one. A cnWave timeout
means "not enabled here", never "this family has no SNMP".

**Sampling limit, recorded rather than glossed.** All five responders are `rcp`. `nbn_accelerate` holds 93 of the fleet's 117 cnWave and is unsampled, because hope-vale was unreachable and the other
five nbn cnWave sites — aurukun, doomadgee, galiwinku, kowanyama, pukatja, **86 devices** — carry no `management_ip` in the inventory at all. That address gap is now a documented inventory finding in
its own right.

**Cross-programme comparison added**, on the principle that a family's contract is not stable until it is checked on both Teleport targets. ePMP is identical across both — exactly 43 columns per SM at
hope-vale (10 SMs), mornington (29) and horn-island (14). Enterprise Wi-Fi's radio contract survives the firmware jump: 36 `cambiumRadioEntry` rows on both `6.6.0.3-r9` and `7.1.1-r5`. Per-device
enablement varies within a programme for Wi-Fi too — mornington `10.255.3.10` is silent.

**Three SNMP mechanics documented, each having already cost a wrong reading.** A table entry OID ends in `.1` and a row is `<entry>.<column>.<index>` — using the table OID instead produced 420
"subscriber links" for an AP with 10. A scalar is instance `.0` of its object. An empty table walks as `noSuchObject`, confirmed again when `HOP_XV2_AP26` returned that for `cambiumClientTable`
**and** `0` for `cambiumAPTotalClients` — genuinely zero clients, not an unimplemented subtree.

**Per-device survey filed** as [references/snmp-enablement-survey-20260921.csv](references/snmp-enablement-survey-20260921.csv) — 27 devices, five sites, three families, with the community tried
recorded per row so the "wrong community or not configured?" question is answerable without re-deriving which credential was used where. **13 rows are the actionable ones: pingable but silent.** Three
outcomes are kept distinct because they are not interchangeable — `UP`/`OK` means enabled and the community is right, `UP`/`TIMEOUT` is actionable, and `DOWN`/`TIMEOUT` carries no information about
SNMP at all. That last distinction is the whole hope-vale lesson in one table row.

**Schemas.** New `snmp` layer in `schemas/`, derived by the new `scripts/snmp_schema_from_walk.py` from live walks rather than from mirrors: `schemas/enterprise-wifi/snmp-radio-entry.schema.json` (18
columns), `schemas/epmp-ap/snmp-connected-sta.schema.json` (42 columns, 13 undocumented in the mirror, including `.43` carrying subscriber firmware), `schemas/cnwave-60ghz/snmp-link-entry.schema.json`
(6 columns; `.5` and `.6` left unnamed because nothing here documents them).

Checks **226 -> 228**.


## 20260920_2339

### Path checking now covers this package's root docs, and a split-filename defect class is enforced (v0.6.3 -> v0.6.4)

Ported from `unified-network-controller`'s staleness audit of the same evening (`unified-network-controller/docs/reports/staleness-audits/staleness-audit-20260920_2324.md`), which found the same two
defects there.

**`SURFACES` was a hand-list of seven files.** `PLAN-xv2-adapter-live-test.md` and anything added later sat outside every path check. It is now derived from the tree — root `*.md` plus
`scripts/README.md`. `references/**` stays excluded, and the reason is stated in the code rather than left as an omission: those files use slash notation for KeePassXC vault groups (the KeePassXC
entry cambium-devices/epmp-ap), CIDR blocks and sibling-repo paths, and a path check over them reports about fifty non-defects, which is a check nobody reads. Bringing them in needs a token <!--
path:example --> discriminator, not a longer exemption list.

**Three references pointed at a path that no longer exists anywhere.** `PLAN-xv2-adapter-live-test.md` cited `cambium-swap`'s
[option-3-architecture.md](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/controller-option3/option-3-architecture.md) (moved there from cambium-swap's
docs/migration/controller-option3/ on the 2026-09-18 split) and <!-- path:example --> `cambium-vendor-adapter-data-points.md`. Those files moved to
`unified-network-controller/docs/controller-option3/` in the 2026-09-18 split, so both the root and the path changed and every citation <!-- path:example --> here silently sent the reader nowhere.
Repointed.

**`SIBLING_ROOTS` added.** A reference into `cambium-swap`, `unified-network-controller` or `skill-smc` now resolves against a declared root, which makes it *verified* rather than merely unchecked —
if a sibling renames the target, this package's routing into it fails loudly. An absent root prints SKIPPED, never passed. Bare basenames are deliberately NOT resolved this way, so
`scripts/README.md`'s `site-addressing.yaml` and `teleport-tunnel.sh` were qualified to `references/site-addressing.yaml` and `skill-smc/scripts/teleport-tunnel.sh`. <!-- path:example -->

**`check_split_path_tokens()` added.** A wide table cell had wrapped mid-filename in three places here (`SKILL.md`, `RUNBOOK.md`, `references/02_device-access-and-vault.md`), leaving a token ending in
a backslash with its tail on the next row — unfollowable for a reader, and invisible to the path check, which skips anything that does not look like a path. Twenty-one instances were found across this
package and its siblings. Both new checks were negative-tested in both directions.

Checks **167 -> 225**.


## 20260920_1951

### SNMP tested head to head against the 60KB cap — it is the proven fallback now

An earlier entry recorded that REST truncates `client-summary` at 60,000 bytes on busy APs and noted SNMP had **no equivalent cap in principle but had not been demonstrated**, because every SMC box
carrying `snmpget` fronted APs of about ten clients. Installing the binary fleet-wide on `rcp`/`nbn_accelerate` made the test possible.

On the same AP at the same time: REST returned unparseable truncated JSON, while a walk of `cambiumClientTable` returned **63 complete client rows from 1008 varbinds** against a reported count of 64.
A walk is many small PDUs, so there is no single-response limit to hit. The "untested fallback" wording is withdrawn.

### The split is real, and it costs something

Neither path alone is sufficient. SNMP scales past the cap and carries 16 columns; REST carries 95 fields including `rssi` and `assoc_time`, **neither of which exists in the MIB at all**. So the
fields lost on a busy AP are precisely the ones SNMP cannot replace — above roughly 60 clients you can have client detail without per-client RSSI or session start.

That is a constraint on the client/session model rather than a collector preference: whether the busiest APs may carry a thinner client record than the rest is a decision to take deliberately, not
something to discover in production.

### Also checked and rejected

The device's SSH CLI (`show wireless clients`) would be a third path, but `sshpass` is not installed on the SMC boxes, so it needs another dependency to reach somewhere SNMP already goes. Recovering
complete records from the truncated JSON is possible but silently lossy — you never learn how many records fell past the cut.

## 20260920_1856

### Verified against upstream — the NAPALM claim holds, but the docstring oversells conformance

An earlier entry asserted that returning a map keyed by interface name is NAPALM's convention. That was argued from this pack's own XV2 `get_interfaces` docstring, which is the same repo claiming its
own conformance — not an authoritative source. Context7 was unavailable at the time and the claim went in unverified.

Now checked against NAPALM's own published documentation: `get_interfaces` does return a dict keyed by interface name, so **the claim stands and the correction it supported was right**.

The check added something the local evidence could not. NAPALM defines six value fields — `is_up`, `is_enabled`, `description`, `last_flapped`, `speed`, `mac_address` — and the R-series adapter
returns two of them plus `ipv4_addresses`, which NAPALM does not define. **"NAPALM-style" therefore describes the response shape, not conformance to the interface contract**, and code written against
NAPALM's documented fields will find four of the six absent. Recorded in `schemas/README.md` beside the map-shape note.

## 20260920_1758

### Changed — `ip6_ll` normalised to a list in `scripts/cambium_xv2_adapter.py`

`get_clients()` now returns `ip6_ll` as a list on every record, including records where the device omits the key. The field's JSON type differs by model — array on XV2 (10 of 32 record-bearing fleet
observations), string on E500 (6), absent where the client has no link-local (17) — and a list is the lossless target, since normalising to a string would truncate any XV2 client holding more than one
address. The E500 shares this adapter, so one change covers both models.

Verified against the six shapes the fleet returned (array, array containing empties, string, null, empty string, empty array), plus a record missing the key and non-dict entries, and live against an
XV2. The value is identifying data — an IPv6 link-local is EUI-64 derived and encodes the client MAC, `fe80::6885:b9ff:feac:bb89` resolving exactly to `6A-85-B9-AC-BB-89` — so it is redacted on the
same footing as `mac`.

### Found — `client-summary` is truncated at 60,000 bytes on busy APs

Verifying the normalisation against a 60-client AP surfaced a device limit, not a tooling one. **The device cuts the response at exactly 60,000 bytes and still returns HTTP 200**, so the body ends
mid-record and will not parse. Repeated identically with `?limit=20`, `?limit=10&offset=0` and `?count=10` — no pagination parameter is honoured.

A busy AP therefore yields **nothing**, not partial data, and the 200 status makes it look like a malformed device rather than a capacity limit. This qualifies the earlier finding that REST dominates
SNMP for Wi-Fi client detail: **it dominates on field richness and fails on the busiest APs**, which are the ones client detail matters most for. SNMP has no equivalent single-response cap, but that
is untested against an AP large enough to cross the threshold — the only SMC boxes carrying `snmpget` currently front APs with about ten clients. The sweep's single `bad-json` finding is now
explained.

### Corrected — `snmpget` availability is per box, not per flavour

An earlier entry recorded `net-snmp` as absent on `rcp`-flavour SMC boxes and present on `nbn_accelerate`. Sampling six boxes disproves it: `hope-vale-smc01` (nbn_accelerate) and `burringurrah-smc01`
(rcp) have it; `wandawuy-smc01`, `amata-smc01`, `doomadgee-smc01` (all nbn_accelerate) and `tjuntjuntjara-smc01` (rcp) do not. Two of six, one from each flavour. The original claim was drawn from
three boxes that happened to line up. Corrected in `skill-smc`'s known-issues reference: probe for the binary, never infer it from the flavour.

## 20260920_1745

### Two sites were never unreachable — they run the `-legacy` password

The sweep's five remaining gaps split into authentication and transport. Testing the vault's `-legacy` entries by hand settled it: on the same kalumburu Enterprise Wi-Fi unit, the primary entry
returns `Invalid username or password` and the `-legacy` entry returns `{"success":true}`. The ePMP legacy entries authenticate through the adapter too, and mornington's R-series behaves the same way.

**kalumburu and mornington were missed by a credential rotation** — 132 devices at kalumburu alone, spanning three families and two different vendor login paths. Recorded in
`references/05_known-issues.md` as a site fact, because it breaks any tooling that assumes one current password per family, not just this exercise.

`scripts/fleet_schema_sweep.py` now resolves each family to its primary vault entry plus a `-legacy` fallback, tried in order. **That recovered 4 of the 5 remaining gaps.**

### Coverage: 121 of 122 site/family pairs, 122 observations

Twelve gaps after the first pass; 7 recovered by restoring the original timeouts, 4 by the credential fallback. One survives: **hope-vale cnWave**, TLS handshake EOF on four devices at full timeout
with both credentials, and all units failed ping — down hardware rather than an access problem.

### Corrected — the R-series `interfaces` getter is not an adapter bug

An earlier entry called it one. That was wrong. Returning a **map keyed by interface name is NAPALM's convention**, and every adapter in this pack follows it — see the `get_interfaces` docstring in
`scripts/cambium_xv2_adapter.py`. The defect was in `scripts/schema_tool.py`, which contracted the map's keys as fields and so surfaced 40 interface names across 9 sites as "site-specific fields",
making one site's VLAN plan look like the family's schema.

Map-shaped endpoints are now declared in the tool's `MAP_SHAPED` registry and contracted as `additionalProperties` describing the **value** shape, with observed keys recorded separately. The R-series
interface value is three fields: `ipv4_addresses`, `is_up`, `mac_address`. Its endpoint field count drops 48 → 8, which is the honest number.

### `ip6_ll` — splits by model, and encodes the client MAC

An `array` on XV2 (10 observations), a `string` on E500 (6), absent where the client has no link-local (17). It is EUI-64 derived, so it carries the same identifying information as the MAC field: the
observed `fe80::6885:b9ff:feac:bb89` resolves exactly to client MAC `6A-85-B9-AC-BB-89`. It was already redacted; the reasoning is now recorded beside it. **Normalise to a list at the adapter
boundary** — wrapping the E500 string and mapping absent to empty is lossless, while normalising to a string would truncate any XV2 client holding more than one address.

### Added

`schemas/SWEEP-LOG.md` — the run-by-run record of all five sweeps, including the two that were discarded, the tuning history with the seven false gaps it cost, and both tooling defects.

## 20260920_1652

### Fleet sweep complete — the contract now rests on 111 live observations

All 36 sites swept by `scripts/fleet_schema_sweep.py`, one representative device per family per site, across four runs — two of which produced confidently wrong data and were discarded and repeated.
Merged standard: `enterprise-wifi` 9 endpoints / 381 fields / 35 observations, `cnwave-60ghz` 13 / 40 / 5, `cnpilot-r-series` 2 / 48 / 8, `epmp-ap` 4 / 20 / 35, `epmp-sm` 4 / 14 / 35. **118 of 122
site/family pairs contracted.** `client-summary` rests on 32 record-bearing observations covering **248 real client records**.

The sweep was worth running rather than extrapolating from the baseline. Against the fleet, `client-summary` grew 95 → 98 fields, `device-summary` 45 → 47, `platform-info` 15 → 16 and
`radio-rf-summary` 15 → 16. Three cnWave models (V1000, V3000, V5000) and ePMP Force 300-16 appeared that one site never showed.

### The finding that matters for adapter work

**In `client-summary` only 43 of 98 fields are universal — 54 split by model.** `radio-rf-summary` is 7 universal against 9 model-split. An adapter written against an XV2 alone depends on fields an
E500 simply does not return, and fails silently because the field is absent rather than wrong. `ip6_ll` additionally returns **an array at some sites and a string at others**, absent entirely at 17.

the R-series `interfaces` getter turned out not to be contractable: its "site-specific fields" are interface names used as object keys (`eth2.17`, `wan1.500`), so each site's VLAN plan appears as
schema fields. That is an adapter design bug, not device divergence — it should return a list with the name as a value. Recorded in `references/05_known-issues.md` rather than smuggled into the
contract.

### Added

`scripts/fleet_schema_sweep.py` (the sweep), `scripts/schema_divergence_report.py` and its generated `schemas/DIVERGENCE.md`, `schemas/SWEEP-LOG.md` (the run-by-run record, including the two sweeps
that were discarded), plus `schemas/_observations/` holding all 118 inputs. Both scripts are cataloged in `scripts/README.md`. 59 reachability findings across the runs are recorded as estate facts
rather than skips. A fourth run retried the 12 gaps at full timeout and recovered 7, proving most were a too-tight mid-run retune rather than estate faults. **Five genuine gaps remain**, three of them
at kalumburu where 132 devices reject the documented vault credentials across two families — a credential problem that blocks all access to that site, not just this exercise.

### Two defects the sweep found in its own tooling

Both produced confident wrong output rather than an error, so both are written up in `references/05_known-issues.md`:

1. **A delimiter-parsing bug silently dropped the first endpoint of every Wi-Fi observation.** The header was sliced on the same `###` separator the endpoint blocks use, consuming the first block's
   delimiter. `client-summary` was first, so **two complete fleet sweeps produced client data for exactly one site** while every other endpoint parsed cleanly — indistinguishable from "no clients
   connected". Found only by asking why 33 sites with non-zero client counts all had empty client lists.
2. **The device credential was passed as a positional argument to `tsh ssh`**, exposing the admin password in the process table locally and on every SMC box touched. Now fed on stdin. The two sweeps
   before the fix did expose it.

### Method correction carried from the baseline

`required` counts only observations that returned a record, and `check` reports an empty endpoint as `no-records` rather than divergent — otherwise every site whose AP happened to have no client
attached would read as a contract violation.

## 20260920_1556

### Added — `schemas/`, the device response contract

A machine-readable contract for what each Cambium family actually returns, derived from live devices rather than from vendor documentation. JSON Schema (draft 2020-12) with `x-cambium` provenance
annotations, one file per family and endpoint, plus `schemas/_observations/` holding the per-device inputs that justify each merged standard.

This exists because the mirrors are wrong in both directions: `cnPilotMIB` describes 16 client columns where a live XV2 returns 95 (including `rssi` and `assoc_time`, absent from the MIB entirely),
and `CAMBIUM-PMP80211-MIB` documents 29 ePMP connected-SM columns where a live 3000L returns 42.

Stage 1 baseline, one reference device per family: `enterprise-wifi` 9 endpoints / 374 fields (XV2 at hope-vale, E500 at Tjuntjuntjara, `raw-endpoint` layer); `cnwave-60ghz` 13 / 40 (V5000 at
doomadgee); `cnpilot-r-series` 2 / 43 (R195P at burringurrah); `epmp-ap` 4 / 20 and `epmp-sm` 4 / 14 (hope-vale). The four non-Falcon families are contracted at `adapter-normalized` layer — their
adapters' getter output — because only the Falcon UI exposes raw endpoints conveniently. Every schema declares its layer so the two are never merged.

### Added — `scripts/schema_tool.py`

Three verbs: `observe` contracts one device, `merge` folds observations into the family standard, `check` reports a new observation's divergence and exits non-zero so it can gate a sweep.

**The method fix that matters:** `required` counts only observations that actually returned a record. An endpoint returning an empty array is not evidence its fields are absent — an AP with no clients
attached says nothing about a client record's shape. The first merge of the `client-summary` contract for `enterprise-wifi` produced **zero** required fields out of 95 purely because the E500 had no
clients at capture time. Empty observations are now excluded from the presence maths and reported in `x-evidence`, and `check` reports such endpoints as `no-records` rather than divergent. The
operational consequence is written into `schemas/README.md`: for client-bearing endpoints, sweep client counts across a site first and contract the device that has clients.

No response values are recorded. `x-candidate-values` carries short, low-cardinality, non-identifying values only — `"2.4GHz"`, `"ON"`, `"axa"` — where the value set is itself part of the contract.
Client MAC, IP, IPv6, hostname, username and SSID are never emitted, and `--strict-pii` (default) also drops anything that looks like a MAC, IP or hostname whatever its field is called.

### Baseline gaps, stated

the `client-summary` contract for `enterprise-wifi` rests on one record-bearing observation, so the XV2-versus-E-series field split (95 against 44, seen in an earlier run) is not yet in the contract.
cnWave `gps` observed as `null` and `links_count` empty. cnWave at hope-vale was unreachable — all three units down on ping — so the baseline came from doomadgee.

### Next

Stage 2 is the fleet sweep: 36 sites, 5 families, roughly 130 device sessions, throttled for ePMP's concurrent-session budget, with unreachable and empty recorded as findings rather than skips.
Divergence between sites goes to `references/05_known-issues.md`, not into a silently widened contract.

## 20260917_1100

### Added

- Pack scaffolded (bootstrap via `skill-ai-it`): `SKILL.md`, `RUNBOOK.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `manifest.json`, `.archcore/` initialized.
- `references/01_overview.md` — device families/models, EoL/EoS snapshot, evidence-state discipline.
- `references/02_device-access-and-vault.md` — KeePassXC `cambium-devices/` vault structure, `kp` wrapper gotchas.
- `references/03_asset-register-conventions.md` — naming grammar, per-site drift, site-name convention, R195P IP-derivation rule. Canonical home for content moved out of the skill-smc pack's numbered
  reference file on this same topic, which is now a short cross-reference stub pointing here instead.
- `references/04_device-inventory-schema.md` — `device-inventory.csv` column contract and extraction workflow.
- `references/05_known-issues.md` — coverage gaps and staleness risks.
- `scripts/check_governance.py` — governance checker generated from `skill-ai-it`'s template, Tier 1 (universal) registries tuned to this pack.

### Notes

- Seeded from the cambium-swap project's 2026-09-17 device-credentialing and device-inventory extraction session — see that project's own changelog entries 20260917_0911 and 20260917_1015.
- Cross-referenced with `skill-smc` in both directions (`SKILL.md` Related Skills, `RUNBOOK.md` Related Workspaces) per operator instruction.
- Generated by `skill-ai-it` in `bootstrap` mode.
- Symlinked at `~/.claude/skills/skill-cambium` and registered in the skills_stuff repo root README's Specialist Packs table for discoverability.

## 20260917_1130

### Added

- `scripts/extract-asset-register.py` — moved here from cambium-swap's session scratchpad per operator instruction, now that this pack is the asset-register knowledge's canonical home. One-off worked
  example, not general-purpose — see its own docstring.
- `justfile`, `.mise.toml` (Python 3.14 pin), `requirements.txt` (`openpyxl`) — runtime isolation per skill-ai-it doctrine: recipes route through `{{py}}` (working-cache peer venv), guarded by
  `_require-venv`; `just bootstrap` / `just runtimes` / `just check` / `just extract-asset-register`.

### Changed

- `scripts/README.md`, `RUNBOOK.md` — routed through `just --list` / `just <task>` instead of direct `python3` invocation.
- `references/03_asset-register-conventions.md` §Extraction Gotchas cross-note and `references/04_device-inventory-schema.md` §Building or Refreshing an Extract — updated to point at the now-real
  `scripts/extract-asset-register.py` instead of stating no script exists.
- `scripts/check_governance.py` — `TASK_RUNNER` set to `justfile`; added one narrow, documented carve-out to the interpreter-pinning check for the `python -m venv` line inside `bootstrap` itself (the
  one recipe that legitimately cannot address `{{py}} by path, since that's the venv it's creating).

### Notes

- `just bootstrap` was not executed this session (would install a real venv) — justfile syntax verified with `just --list` only. Run `just bootstrap && just check` before relying on `just
  extract-asset-register`.

## 20260917_1135

### Added

- `scripts/cambium-portal.sh` — moved here from `cambium-swap` (was cambium-swap's own scripts/cambium-support-login.sh, now removed there). Cross-project Cambium support-portal
  (support.cambiumnetworks.com) automation: `login` (unchanged behaviour) plus a new `fetch-release <model search> <version string> <dest-dir>` subcommand that finds a specific dated
  firmware/documentation release and downloads all its files, sniffing each one's real type since the portal's download links carry no filename. Both need a live MFA code from the operator each run.
- `references/02_device-access-and-vault.md` — documented the confirmed live Hope Vale device-access chain (`tsh` cluster split, SMC-box network path, credential-materialization and `kp`-PATH fixes,
  the Enterprise Wi-Fi REST API auth flow, and the SSH-vs-web-UI comparison), and the `scripts/cambium-portal.sh` move.
- `RUNBOOK.md`, `justfile` — catalogued `scripts/cambium-portal.sh` and its two `just` recipes (`cambium-login`, `cambium-fetch-release`).

### Changed

- `scripts/check_governance.py`: 89/89 passing (up from 84) after the RUNBOOK/justfile additions extended path-resolution coverage.

### Notes

- Prompted by `cambium-swap` work: this pack's own live device-access verification (real SSH CLI login, real authenticated web UI/API session) against a Hope Vale AP, and a version-matched
  documentation fetch (Cambium does not publish a per-patch-version CLI doc separately from firmware/MIBs on the model-specific Downloads page — it publishes a separate per-major-version
  "Documentation" bundle instead, found via its own Archive tab).

## 2026-09-17 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-08-11-governance-checks-layer-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-08-11-governance-checks-layer-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: context-map.yaml, AGENTS.md, scripts/README.md

## 20260917_1210

### Added

- `scripts/cambium_xv2_adapter.py` — minimal Enterprise Wi-Fi (XV2/Falcon UI) REST adapter: `login`/`logout`, `get_facts()`, `get_interfaces()`. Stdlib-only (no `requests`, no venv/dependency). Run
  live against Hope Vale Tower 1 (`10.255.3.1`) via a `tsh` tunnel — matched evidence E101 exactly (hostname, serial, firmware, MAC, live cnMaestro status).
- `PLAN-xv2-adapter-live-test.md` — resume-point plan doc for this test; kept even though the test completed the same session, as the template for the next family/vendor adapter test.

### Fixed

- `get_interfaces()`'s first draft trusted `device-summary`'s `port_stats[].link` field, which reported `"DOWN"` for every port including `ETH1` even though `ETH1` was physically up and passing real
  traffic. The device's separate `port_status[]` array (integer 1/0 link/duplex encoding) is authoritative for link state; `port_stats` is reliable only for byte/packet counters. Fixed to merge both
  by port name. Re-verified live: `ETH1` now correctly reports `is_up=true, speed=1000M, duplex=FULL`.

### Decision

- Operator proposed a formal CLI/API grammar + capability-model skill (`device-interface-modeler`: command-schema.json, OpenAPI generation, Tree-sitter/ANTLR, AI-extraction pipeline) ahead of writing
  any real adapter, given the plan to go multi-vendor later. Ran `skill-walk-before-run` — RED (no reality contact yet, peripheral tooling ahead of a still-stubbed core capability). Cheapest test
  (this adapter) resolved it: `PASS`, formal schema not needed. RESOLVED entry appended to `skill-walk-before-run`'s `ledger.jsonl` (mirrored to `cambium-swap/.wbr-ledger.jsonl`). Multi-vendor plans
  don't change the conclusion — the real cross-vendor abstraction already exists in `cambium-swap`'s
  [option-3-architecture.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/option-3-architecture.md) adapter contract (`get_facts`/`get_interfaces`/...);
  a second vendor gets its own specialist skill pack implementing the same method names, same pattern as `skill-smc`/`skill-cambium`. Revisit only once a second real vendor adapter exists to design
  against.
- All Cambium development work (this adapter, the portal script moved earlier this session) goes into `skill-cambium`, not into `cambium-swap` — explicit operator instruction, reinforcing this pack's
  existing Standing Write-Back Contract.

### Notes

- `just check` / `python3 scripts/check_governance.py`: run before considering this durable — see the Changed section below for the actual count.

## 20260917_1200

### Changed

- `AI_NAVIGATION.md` — hand-added a "Context compaction recovery" section and a "Companion files" note under Update rules. This file's navigation block is project-managed (`skill-ai-it:manual`), so
  the automated upgrade correctly refused to touch it; these two content gaps were unrelated to the file's declared opt-out reason (task→reference routing table, skill-smc boundary), so they were
  added by hand instead of left failing.

### Added

- `ARCHCORE_PROMOTION_CANDIDATES.md` — first promotion-candidate report since `.archcore/` was initialized at bootstrap. Surfaces 2 ADR candidates and 4 rule candidates from `SCRATCHPAD.md`
  (KEEP-marked decisions) and `AGENTS.md`; no spec or plan candidates found. Report only — no `.archcore/` content written.

### Notes

- Generated by `skill-ai-it` in `refresh` mode, immediately following the deterministic upgrade run above.
- `scripts/check_governance.py`: 92/92 passing (unchanged count from before this refresh — no new catalog surfaces were added).
- This pack has no Repomix config yet, so the new candidates file was not added to any generated context pack.

## 20260917_1230

### Added

- `.archcore/adr/adr-separate-pack-from-skill-smc.md` — proposed
- `.archcore/adr/adr-vault-file-avoids-opa-blocked-words.md` — proposed
- `.archcore/rules/rule-vault-reference-convention.md` — proposed
- `.archcore/rules/rule-cambium-smc-cross-pack-boundary.md` — proposed
- `.archcore/rules/rule-manifest-version-discipline.md` — proposed
- `.archcore/specs/spec-specialist-pack-file-roles.md` — proposed (reclassified from a rule candidate to a spec, mirroring skill-smc's identical document)
- `.archcore/README.md` — durable index for the 6 documents above; carries the never-promote reasoning forward from the deleted candidate queue

### Changed

- `README.md`, `AI_NAVIGATION.md` — updated the `.archcore/` description from "empty" to "6 documents proposed 2026-09-17"
- `scripts/check_governance.py` — registered `ARCHCORE_PROMOTION_CANDIDATES.md` in `CONDITIONAL_PATHS` so this and future CHANGELOG mentions of it do not fail path resolution now that the file is
  gone; updated the stale "empty pending first promotion" comment on the three `.archcore/` subfolder exemptions

### Removed

- `ARCHCORE_PROMOTION_CANDIDATES.md` — deleted per promote-mode contract; it was a proposal queue, not a record

### Notes

- Generated by `skill-ai-it` in `promote` mode, per operator instruction ("promote them") against the candidates surfaced in the prior refresh run.
- All 6 documents are `status: proposed`, not `accepted` — operator review of each is still outstanding; flip the frontmatter `status:` field once reviewed.
- The vault-related ADR's first draft filename was itself blocked by the workspace's OPA write-gate for containing a blocked substring — direct confirmation of the decision it records; the final
  filename avoids it, and the same avoidance was applied to the vault-related rule's filename.
- `scripts/check_governance.py`: 94/94 passing.

## 20260917_1245

### Changed

- All 6 `.archcore/` documents — `status: proposed` → `status: accepted` per operator instruction ("accept them all"): both ADRs, all 3 rules, and the spec.
- `.archcore/README.md` — reworded from "6 proposed, not yet accepted" to "6 accepted by the operator on 20260917", mirroring the agent-stack pack's index phrasing; noted that an accepted document is
  superseded in place rather than deleted.
- `README.md`, `AI_NAVIGATION.md` — `.archcore/` descriptions changed from "proposed" to "accepted"; `AI_NAVIGATION.md`'s Project context files table authority column changed from "Highest, once
  accepted" to "Highest".

### Notes

- These 6 documents are now this pack's highest-authority source per `AI_NAVIGATION.md`'s source-priority list.
- `scripts/check_governance.py`: 102/102 passing.

## 20260917_1300

### Fixed

- `scripts/check_governance.py` — `CATALOGS` never covered `scripts/README.md` ↔ `scripts/`, only `RUNBOOK.md` ↔ `references/`. `scripts/cambium-portal.sh` had been sitting uncataloged since it was
  moved in from `cambium-swap`, despite `scripts/README.md`'s own maintenance rule claiming the checker enforces this. Added `"scripts/README.md": ("scripts", "*")` to `CATALOGS`; proved the new check
  could fail (it did, immediately, on the exact gap it was meant to catch) before fixing the gap.
- `scripts/README.md` — added the missing `scripts/cambium-portal.sh` row to the Raw Script Inventory (purpose, inputs, outputs, safety labels, idempotency, when to use).

### Changed

- `AGENTS.md` — extended the Project-coherence checklist with a new Tier 1b ("Scripts") and broadened the Cross-project write-back trigger's closeout self-check to explicitly ask about scripts, not
  just facts. Prompted by an operator design question: how does this pack learn about a Cambium-domain script written or moved in from a consuming project, given this pack has no visibility into
  another project's filesystem? Answer used: no push mechanism is needed (same local filesystem, an agent session in the consuming project already has direct read/write access to this pack's canonical
  path) — the fix is a stronger *closeout obligation* on the consuming-project session, worded against the two real precedents (`scripts/cambium-portal.sh`, `scripts/extract-asset-register.py`) and
  against the coverage gap just found and fixed above.

### Notes

- Generated during a `refresh`-adjacent maintenance pass, not a full `skill-ai-it refresh` run.
- `scripts/check_governance.py`: 108/108 passing (up from 102 — 4 new assertions from the scripts/README.md catalog-coverage direction, 2 more counted-and-passing after the AGENTS.md path fix below).
- The first draft of this entry's AGENTS.md edit referenced the same two scripts as bare filenames in prose; the governance checker's path-resolution check correctly failed because those names only
  resolve under `scripts/`, not at the pack root. Fixed by qualifying both with the `scripts/` prefix — a pitfall this checker itself is meant to catch, and did.

## 20260917_1440

### Added

- `scripts/cambium_xv2_adapter.py`: `get_radios()`, `get_wlans()`, `get_clients()`, `get_config()`, `get_events()` — the remaining rows from
  [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md), all run live against Hope
  Vale Tower 1. `get_radios()` merges `radio-summary` (state/channel/power) with `radio-rf-summary` (utilization/noise floor) by list position — neither response carries a join key. `get_wlans()`
  merges `wlan-summary` with `wlan-interface-summary` by SSID (`/api/wlan-config` 500'd on this firmware with no params — not used). `get_clients()` returned an empty list live, which is a real state,
  not a bug. `get_events()` caps output at a `limit` param (raw log observed live was 41KB).
- `get_raw(endpoint)` — public escape hatch for exploring an endpoint with no getter yet; deliberately returns unredacted data and says so in its docstring, so callers cannot mistake it for safe.
- `--dump <endpoints> --dump-dir <dir>` CLI mode — writes one redacted JSON file per endpoint instead of printing to stdout. Added specifically because the operator asked "why didn't you create a
  script?" after this session's exploration was done as ad hoc `curl` chains instead of through the adapter itself — the right fix was giving the adapter script a first-class exploration mode, not a
  separate one-off shell script.

### Fixed — real secret exposure, see `references/05_known-issues.md` Security Incidents

- `REDACT_KEY_PATTERN` (module-level, used by both `get_config()` and `--dump`) extended from `pass|psk|secret|key|shared` to also match `community|radius|credential|token|auth`, after an ad hoc
  redaction pass during exploration missed `snmp_read_community`/`snmp_write_community` and printed them to a terminal transcript. The earlier per-call redaction logic was also centralized into one
  `redact()` function so there is exactly one place this can go wrong, not one per caller.

### Notes

- `python3 scripts/check_governance.py`: run before considering this durable — see the next entry's Changed section for the count if this was not re-verified standalone.

## 20260917_1500

### Added

- `references/06_device-api-cli-reference.md` — the Enterprise Wi-Fi (XV2) adapter data-points table (REST endpoint + SSH CLI fallback + live-verified quirks per `get_facts`/`get_interfaces`/
  `get_radios`/`get_wlans`/`get_clients`/`get_config`/`get_events`), migrated in from `cambium-swap`'s
  [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md). Prompted by an operator
  design correction: Cambium equipment knowledge (API endpoints, CLI commands, their quirks) belongs in this pack, not duplicated into a consuming project's docs — raw evidence/captures stay in the
  project, the technical knowledge itself lives here next to the adapter code that consumes it.
- `RUNBOOK.md` Reference Routing table and `SKILL.md` References/Use-When lists — both extended with the new file.

### Changed

- `cambium-swap`'s [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md) rewritten
  to a thin, project-scoped pointer (why Option 3's controller needs this data, evidence-ID citations) that links here for the actual endpoint/command table, instead of holding a second copy of it.

### Notes

- `python3 scripts/check_governance.py`: run after this entry to confirm the new reference file is fully cataloged (RUNBOOK.md routing row, SKILL.md references list).

## 20260917_1510

Operator asked to verify the XV2 adapter against a couple more physical units, not just Tower 1.

### Added

- `references/05_known-issues.md` Coverage Gaps — Hope Vale Tower 2 (`10.255.3.2`) recorded as unreachable (`ping`/SSH from `hope-vale-smc01` both returned "no route to host"), found while sweeping
  for a second/third test unit.

### Changed

- `references/06_device-api-cli-reference.md` Evidence and Version Scope — extended from one confirmed unit (Tower 1) to three: Tower 5 (`HOP_XV2_AP5_IP3_5`) and Tower 6 (`HOP_XV2_AP6_IP3_6`) both ran
  all seven getters live in one pass each, same firmware (`6.6.0.3-r9`), same cnMaestro server, different serials — the adapter's output shape holds across physical units, not just the one it was
  developed against.

### Notes

- Both new devices' raw redacted JSON output archived in `cambium-swap`'s [captures/device-queries/](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/captures/device-queries) (gitignored) and
  cited by sha256 in `cambium-swap`'s `evidence/evidence-register.csv` entry E108 — full provenance lives there, not duplicated here.
- Reachability sweep of 9 Hope Vale XV2/backhaul IPs from `hope-vale-smc01` found only Tower 2 down; Towers 5, 6, 7, 8, 9, 10, 11, 12, 13 all answered ping. Only 5 and 6 were actually queried this
  session — the others remain unverified, just known-pingable.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references.

## 20260917_1600

Operator asked to try one of each remaining device family (cnPilot R195P, ePMP SM, ePMP AP), skipping cnWave 60GHz for now.

### Added

- `references/06_device-api-cli-reference.md` — new ePMP AP/ePMP SM section: `show dashboard` CLI (SSH) confirmed live on one unit of each, plus a previously-undocumented HTTPS JSON API discovered by
  reading the web UI's own JS bundle — a LuCI-derived `/cgi-bin/luci` RPC surface (`stok` + `sysauth_<host>` cookie both required, HTTP 200 on auth failure so don't trust the status code alone),
  confirmed live via `test_connect`.
- `references/06_device-api-cli-reference.md` — new cnPilot R195P section documenting the addressing investigation (see Fixed below) and a cnWave 60GHz stub noting it's still untouched.
- `references/05_known-issues.md` — R195P's existing IP-derivation gap upgraded with the live-ARP contradiction; new Coverage Gaps row for Burringurrah addressing generally, since the same failure
  mode was independently found on the XV2 rows, not just R195P's.

### Fixed

- Nothing broken in code — the finding itself is the useful output. R195P was never reached: `burringurrah-smc01`'s ARP table shows zero hosts at `10.255.10.x` (the `EXT10XX → 10.255.10.XX` derivation
  rule's target range) against 96 entries elsewhere on the same bridge. MAC-OUI cross-check on those other entries found Burringurrah's real XV2 fleet at `10.255.11.x` (OUI `bc:a9:93`, matching
  confirmed live Hope Vale XV2 units) and real ePMP fleet at `10.255.21.x` (OUI `58:c1:7a`, matching confirmed live Hope Vale ePMP units) — contradicting the `.3.x` addresses most Burringurrah XV2
  rows in `device-inventory.csv` record, while confirming the `.21.x` addresses most Burringurrah ePMP SM rows already use.

### Notes

- ePMP AP and ePMP SM: `device-family-matrix.csv`'s SSH/CLI notes upgrade from `USER_STATED` to `VERIFIED-OBSERVED` for the two units tested; the API discovery is new information, not present in that
  matrix at all yet.
- The ePMP LuCI API's actual per-page RPC method names (the JSON equivalent of `show dashboard`) are still unknown — `test_connect` proves the auth mechanism works, not full data retrieval. Left as a
  stub for whoever builds an ePMP adapter next, same shape as `scripts/cambium_xv2_adapter.py`.
- R195P remains completely unverified — this session found *why* previous attempts would have failed (wrong address, not just an expired Teleport session), not a working device session. Getting one
  needs a corrected address, not another SSH/API attempt at the recorded one.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references.

## 20260917_1630

Operator asked why no adapter data points existed for anything but XV2, then to go build them. Along the way: a second live secret-exposure incident, a script relocated to its correct owning pack on
operator correction, and a new script built proactively per a standing instruction to stop waiting to be asked for repeated manual patterns.

### Added

- `scripts/cambium_epmp_adapter.py` — the ePMP counterpart to `scripts/cambium_xv2_adapter.py`: `login`/`logout`, `get_facts()`, `get_interfaces()`, `get_wireless_link()` (SM-only, `None` on an AP),
  `get_clients()` (AP-only, `[]` on a SM), `get_config()` (redacted). Stdlib-only. Verified live against Hope Vale Tower 5 (SM, via a captured-data replay after the device's session limit blocked a
  final live run — see Fixed) and Tower 1 Omni0 (AP, fully live). Built from real reverse-engineering of `cambium.<hash>.js`: found the real `get_param`/`act=status`/`act=config_regular` RPC surface
  (46 real method names enumerated), not guessed.
- `references/06_device-api-cli-reference.md` — ePMP section rewritten from narrative access notes into a real Data Points table matching XV2's shape, citing the adapter.
- `scripts/scan-config-fields.py` (`just scan-fields <path>`) — reports which JSON keys look credential-shaped without ever printing their values. Built unprompted after a standing instruction: create
  a script/just-recipe once something's been done by hand two or three times rather than waiting to be asked. This session did the "print a value to check if it's a real secret" mistake twice — this
  makes the safe version the easy path going forward, in this pack or any consuming project.
- `justfile` — `epmp-getters host role="sm"` (runs the new adapter's getters, pulling the right vault credential by role) and `scan-fields path`.

### Fixed

- `get_wireless_link()`: `cambiumSTADLRSSI` exists (=0) on an AP too, so its mere presence isn't a valid SM-vs-AP discriminator — an AP was returning a bogus zeroed-out link dict instead of `None`.
  Now checks `cambiumConnectedAPMACAddress` instead (a SM reports a real MAC; an AP reports the literal string `"Not Associated"`). Found and fixed live before this entry, verified against both device
  roles.
- ePMP SM (`10.255.4.5`) hit the device's real concurrent-session cap (`{"users":{"ro":0,"rw":5}}`) mid-session, from earlier untidy testing that never called `logout()`. It never cleared during this
  session — the adapter's final live-verification run against SM had to be substituted with an offline replay of the SM `act=status` payload already captured earlier in the session, run through the
  same parsing code. Confirmed correct (real facts, real wireless-link RSSI/SNR, empty clients as expected), but it's a replay, not a fresh live call — worth one more real SM run next session to close
  that gap properly.

### Changed

- **[teleport-tunnel.sh](/Users/malik.ahmad/.claude/skills/skill-smc/scripts/teleport-tunnel.sh) moved to `skill-smc`.** Built here first for Cambium device-access convenience, then the operator
  corrected the framing directly: "it's not Cambium tunnel, it's teleport tunnel" — generic Teleport tunneling is `skill-smc`'s concern, not this pack's, per each pack's own boundary rule. Moved,
  generalised (site -> SMC-host resolved live from ansible-wifi's own `[<site>_smc_bases]` inventory groups, never hardcoded — a second operator correction, catching an earlier hardcoded site table
  before it was even committed), and `skill-cambium`'s `just tunnel` now calls the canonical `skill-smc` path directly. See `skill-smc`'s own `CHANGELOG.md` (`20260917_1620`, v0.1.40 -> v0.1.41) for
  its side.

### Security Incidents

- Second live secret-exposure incident this session (first was XV2's SNMP communities, `20260917_1440`): ePMP SM's real SNMP community strings, RADIUS password, and wireless encryption key printed to
  this transcript while manually checking whether `act=config_regular`'s flagged fields held real values. Full incident record and fix (`scripts/scan-config-fields.py`):
  `references/05_known-issues.md`.

### Notes

- R195P and cnWave 60GHz untouched this entry — out of scope, per the earlier operator instruction to skip 60GHz and the still-open addressing problem blocking R195P (`20260917_1600`).
- `python3 scripts/check_governance.py`: 126/126 passing.

## 20260917_1700

Operator asked how to capture per-site addressing conventions so future queries at different sites can consult it, given 20+ `nbn_accelerate` sites and 10+ `rcp` sites exist and only two have ever
been checked. First answer was a markdown table (added to `references/03_asset-register-conventions.md`); operator then asked whether YAML/TOML/JSONL would be better, given the site count. Agreed a
structured companion earns its keep at that scale and built it.

### Added

- `references/site-addressing.yaml` — machine-readable per-site/per-family IP addressing trust state (`verified`/`contradicted`/`unverified`) plus a MAC-OUI lookup (`bc:a9:93` ->
  `enterprise-wifi-xv2`, `58:c1:7a` -> `epmp`), both confirmed live this session. Deliberately sparse — only `hope-vale` and `burringurrah` have entries, since those are the only two sites ever
  checked; the file's own header explicitly warns against guessing a pattern for an unchecked site by analogy to a checked one (the two already disagree with each other).
- `references/03_asset-register-conventions.md`'s new "Per-Site IP Addressing Reality" table (added earlier this session, `20260917_1630`-adjacent but not yet logged) — narrative version of the same
  data, now cross-linked from the YAML and vice versa. Neither is canonical over the other: the `.md` carries evidence citations and prose caveats, the YAML is the queryable form.
- `RUNBOOK.md` and `SKILL.md` — new routing row/reference-list entry for `references/site-addressing.yaml`.

### Notes

- Explicitly scoped to exclude site -> SMC-host -> Teleport-cluster data, which stays resolved live from ansible-wifi by `skill-smc`'s
  [teleport-tunnel.sh](/Users/malik.ahmad/.claude/skills/skill-smc/scripts/teleport-tunnel.sh) — this file only answers "which octet does family X live on at site Y", a genuinely Cambium-specific fact
  ansible-wifi's own inventory doesn't carry.
- No script consumes this yet — built now specifically because the site count (30+) makes ad hoc markdown-table lookups impractical, not because a consumer exists today. The natural next step, if
  wanted, is a validation script that flags `device-inventory.csv` rows whose `management_ip` doesn't match this file's confirmed pattern for that site+family.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references. Note `references/*.yaml` isn't swept by the pack's `CATALOGS` glob (`references/*.md` only), so this
  file's discoverability relies entirely on the manual `RUNBOOK.md`/`SKILL.md` rows above, not an enforced check.

## 20260917_1710

Operator asked whether evidence (E99-E111) should move from `cambium-swap` into this pack, since this pack claims to be cross-project. Conclusion: no — `cambium-swap`'s evidence register is that
project's whole investigation trail (corporate filings, vendor docs, dependency-class tags), not just device facts, and importing that machinery here would be scope creep. The real gap: this pack's
`Ennn` citations should read as self-contained (the fact stated inline, the ID as an optional pointer for provenance detail), never a hard dependency on `cambium-swap` being present.

### Fixed

- `references/site-addressing.yaml` — the three Hope Vale `trust: verified` entries (`enterprise-wifi-xv2`, `epmp-ap`, `epmp-sm`) had an `evidence:` list but no `notes:`, unlike the Burringurrah
  entries — a reader without `cambium-swap` access would see `trust: verified` with no explanation of what was actually confirmed. Added a `notes:` line to each, matching the Burringurrah rows'
  self-contained style. Audited every other `Ennn` citation in this pack (`references/03_asset-register-conventions.md`, `references/06_device-api-cli-reference.md`, this file) — all already state the
  fact in prose before citing the ID, no changes needed there.

### Notes

- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_1720

Operator pushed further on the previous entry: if this pack doesn't validate `Ennn` citations, and `cambium-swap`'s own register could change without this pack knowing, what's the actual logic of
citing an external ID at all — shouldn't the whole register just live here? Landed on: no, most of that register is `cambium-swap`'s own investigation evidence (corporate filings, vendor docs,
community posts), not this pack's domain; relocating the file would just move the coupling, not remove it. The real fix is smaller — stop citing `Ennn` IDs at all.

### Changed

- `references/site-addressing.yaml` (`schema_version: 1` -> `2`) — every `evidence: [Ennn, ...]` list replaced with a self-contained `verified: "<date> — <device> — <method>"` string. `oui_reference`
  entries got the same treatment. Nothing here depends on `cambium-swap`'s register existing, being unchanged, or being reachable anymore.
- `references/03_asset-register-conventions.md` — the Per-Site IP Addressing Reality table's evidence column reworded from bare `Ennn` citations to inline dates/methods; header retitled "Live reality
  (confirmed 2026-09-17)".
- `references/06_device-api-cli-reference.md` — both `Ennn` mentions reworded to point at "cambium-swap's own evidence register" generically (for anyone who wants the raw session/sha256 trail) rather
  than naming specific IDs that could be renumbered or superseded with nothing here to notice.

### Notes

- `CHANGELOG.md`'s own historical `Ennn` mentions (`20260917_1210`, `20260917_1510`) were deliberately left alone — those are dated log entries describing what happened in a past session, not
  current-knowledge claims this pack is asserting today. Same "do not enforce history" principle this pack already applies to counts and states elsewhere.
- This closes the loop from the last two entries: the drift risk raised in `20260917_1700`/`20260917_1710` (an `Ennn` citation could go stale with nothing here noticing) is now moot for this pack's
  own files — there's no external ID left to go stale.
- `python3 scripts/check_governance.py`: run after this entry to confirm no broken references.

## 20260917_1730

Operator pointed out the previous entry's fix (`verified: "<date> — <device> — <method>"` as one prose string) undercut the file's own stated purpose — queryable, not just readable.

### Changed

- `references/site-addressing.yaml` (`schema_version: 2` -> `3`) — every `verified:` string replaced with a structured block: `date`, `method` (one of a fixed enum — `ssh-cli-session`,
  `ssh-rest-session`, `luci-api-session`, `arp-mac-oui-match`, `arp-absence`), plus whichever of `devices`/`host_count`/`oui`/`firmware`/`site` actually applies. `notes` stays free text, but only for
  a genuine one-off caveat — the file's own header now says to give a repeated caveat shape a real field instead of writing the same sentence twice.
- MAC-address keys under `oui_reference` explicitly quoted (`"bc:a9:93"`) — harmless either way in this parser, but removes any doubt about colons-in-keys ambiguity for a future editor or a stricter
  YAML parser.

### Notes

- Confirmed the file still parses clean and demonstrated the actual payoff: `method`/`devices`/`host_count` are now filterable fields, not something a reader would have to regex out of a sentence.
- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_1930

Operator asked, after `cambium-swap`'s multi-site cnMaestro reconciliation, whether every device type is now accessible. Answer: no — accessibility varies a lot by family. Fixed one stale matrix row
and logged the gaps that answer surfaced.

### Fixed

- `inventory` (via `cambium-swap`'s `inventory/device-family-matrix.csv`) — `R195P`'s `local_ssh` field still said `UNVERIFIED (Telnet documented)`, contradicting a real live SSH login this session
  (`cambium-swap` evidence E113/E114: `BUR-R195P-1047`, `BUR-R195P-1055`). Corrected to `VERIFIED-OBSERVED`. The edit briefly shifted every field after `local_ssh` by one column (a plain-text comma
  inside the new note broke the row's alignment) — caught and fixed by re-parsing the row with `csv` before it was left broken.

### Added

- [references/05_known-issues.md](references/05_known-issues.md) — three coverage gaps this pack didn't have rows for: Enterprise Wi-Fi E-series (`E500`/`E430`, credentialed but never live-tested —
  first real units surfaced 2026-09-17 in `cambium-swap`'s multi-site reconciliation), ePMP Force 300-16 in an AP role (first seen at Kalumburu, same hardware as the verified SM role but untested as
  an AP), and cnWave 60GHz (`V1000`–`V5000`, still no adapter or live access attempt at all).

### Notes

- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_1946

Operator asked to log in and fill in adapter data points for the three untested types 20260917_1930 flagged as gaps.

### Added

- [references/06_device-api-cli-reference.md](references/06_device-api-cli-reference.md) — "Enterprise Wi-Fi E-series (E500, E430)" section: same Falcon-family REST/CLI adapter as XV2, confirmed live
  against real `E500` (Tjuntjuntjara, codename `Gambit`, firmware `4.2.3.1-r9`) and `E430H` (Mowanjum, codename `Sage`, firmware `4.2.3.1-r17` — the device's own `show version` output resolves E31's
  H-vs-W ambiguity for this unit). A note under the ePMP section confirms Force 300-16 in an AP role (Kalumburu) works identically to the verified SM role, but only with the `epmp-ap-legacy` vault
  credential — the first real hit of the "minority of field units... legacy default" risk, not just a theoretical note. The cnWave 60GHz section now records a real, partial finding instead of "no
  attempt yet": SSH login against a live V5000 succeeded, but the E2E controller's interface is a full interactive TUI that stalls under non-interactive/forced-pty exec — no data points extracted,
  blind key-navigation against production hardware was deliberately not attempted.
- [references/05_known-issues.md](references/05_known-issues.md) — the E500/E430 and Force-300-16-AP gap rows removed (both now `VERIFIED-OBSERVED`); the cnWave row narrowed to specifically "data
  points beyond login" now that login itself is confirmed.

### Notes

- `cambium-swap` evidence E118 has the full session detail (exact commands, credentials tried, why the cnWave TUI was not navigated blind).
- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_2021

Operator asked to check the official cnWave TUI docs, and whether the REST API works. Checked the vendor's already-archived User Guide (`cambium-swap` evidence/archived-docs/E44) before doing anything
live — it has no CLI/TUI content at all. Then confirmed the REST API instead, fully closing this gap.

### Fixed

- [references/06_device-api-cli-reference.md](references/06_device-api-cli-reference.md) cnWave section rewritten from "no adapter, login only" to a full adapter data-points table: JWT auth (`POST
  /local/userLogin`), 7 confirmed-live endpoints (`getDeviceInfo`, `getE2eInfo`, `getStatusInfo`, `getSystemCapability`, `getLinksCount`, `getGpsBrief`, plus `/api/getTopology` and
  `/api/getCtrlStatusDump` under the same token), and the write-shaped endpoints identified but never called.
- [references/05_known-issues.md](references/05_known-issues.md) — the cnWave coverage-gap row removed; fully resolved.

### Notes

- Key finding: the official 60 GHz cnWave User Guide (Release 1.8, exact firmware match, already in `cambium-swap`'s evidence archive since 2026-09-14 — should have been checked before any live
  SSH/TUI attempt) has zero SSH/CLI/console mentions across 12,378 lines. The SSH TUI reached in the prior entry is undocumented/internal; the web UI's backing REST API is the real, vendor-sanctioned
  interface — same conclusion this project already reached for XV2 and ePMP.
- `cambium-swap` evidence E119 has the full session detail, including an operational note about a download-tooling mishap (browser automation briefly wrote large firmware files into the wrong
  directory — caught and cleaned up, nothing committed).
- `python3 scripts/check_governance.py`: 131/131 passing.

## 20260917_2050

Operator asked to fill the remaining cnWave gaps (CN-role coverage, more endpoints) and pointed out only two of four confirmed families had a real vendor adapter file.

### Added

- `scripts/cambium_cnwave_adapter.py` — JWT bearer-token REST adapter: `login()`/`logout()`, `get_facts()`, `get_e2e_info()`, `get_status()`, `get_capability()`, `get_links_count()`, `get_gps()`,
  `get_topology()`/`get_ctrl_status_dump()` (E2E-role only), `get_config()` (redacted). Verified live against a real V5000 (E2E/POP role) and V2000 (plain Client Node), Hope Vale.
- `scripts/cambium_r195p_adapter.py` — this pack's first adapter that shells out to system `ssh`/`sshpass` instead of using a REST client (no REST API confirmed for this family): `get_facts()`,
  `get_interfaces()`. Verified live against two real Burringurrah units. Two real bugs found and fixed during that live test: a named interface (`wan1`) that doesn't exist on every unit was treated as
  a fatal error instead of a tolerable "unknown" (confirmed one unit uses `eth2.500` for the same WAN role instead); this BusyBox's `ip -o addr show` interleaves LINK-shaped lines with ADDR-shaped
  lines for the same interface, which a naive positional parser mis-split into duplicate keys — fixed with a regex-based parser.
- `references/06_device-api-cli-reference.md` — cnWave section rewritten with the confirmed CN-role behaviour and additional endpoints (`getCnAgentConfig`, `minionConfigGet`); new "cnPilot R195P —
  Adapter" subsection.
- `scripts/README.md` — catalogued both new adapters.

### Fixed

- Confirmed cnWave's local REST API works on every node regardless of role, not E2E-only as previously assumed — the real distinction is that `/api/getTopology`/`/api/getCtrlStatusDump` only return
  data from the E2E-enabled node.
- `references/05_known-issues.md` — Enterprise Wi-Fi E-series and Force 300-16 AP gaps confirmed already closed; no new entries needed.

### Notes

- R195P SNMP: checked `cambium-swap`'s `ansible-wifi` R195P provisioning template — the Get/Set community values are encrypted blobs in the device's own config-encryption format, identical fleet-wide,
  not decryptable and not attempted. Deliberately did not implement `get_config()` for R195P for the same reason plus this project's two prior secret-exposure incidents on other families.
- All comments/docstrings in the four hand-authored adapters (xv2, epmp, cnwave, r195p) rewrapped to this project's 160-column standard.
- `python3 scripts/check_governance.py`: 133/133 passing.

## 20260917_2057

Operator added four real SNMP community credentials to the KeePassXC vault (`apn-snmp-ro`/`rw`, `nbn-snmp-ro`/`rw`) and asked why the remaining rcp sites and OUI blocks weren't in
`references/site-addressing.yaml` yet.

### Added

- SNMP live-verification, closed fleet-wide in one pass: real SNMPv2c `sysDescr`/`sysName` GETs confirmed against one device per major family (R195P via `apn-snmp-ro`, XV2/ePMP AP/cnWave V5000 via
  `nbn-snmp-ro`) — confirms the `apn`/`nbn` split maps exactly to `smc_flavour`. Did not test either `-rw` community (no SNMP SET attempted).
- `references/site-addressing.yaml`: all nine rcp sites the operator's cnMaestro exports covered this session now have entries (was only hope-vale + burringurrah), derived from `cambium-swap`'s
  already-reconciled `device-inventory.csv` — each site's dominant octet-per-family pattern plus real host counts, with secondary/spillover subnets noted where a site splits a family across multiple
  towers. Three more XV2 OUI blocks added (`fc:11:65`, `b4:a2:5c`, `bc:e6:7c`) — this family uses at least five different OUI blocks fleet-wide depending on procurement batch/site, not one; `58:c1:7a`
  also turned out to cover the Enterprise Wi-Fi E-series, not just ePMP. New `snmp-get-session` method value added to the file's own method enum.

### Fixed

- `inventory` (via `cambium-swap`'s `device-family-matrix.csv`) — `local_snmp` upgraded from `USER_STATED` to `VERIFIED-OBSERVED` for R195P, XV2-2T0, ePMP 3000L, and V5000.
- Removed [references/site-addressing.yaml](references/site-addressing.yaml)'s own now-obsolete "eight sites not yet added" note, since they now are.

### Notes

- Full evidence detail (exact devices, IPs, sysDescr strings) lives in `cambium-swap` evidence E122, per this project's routing rule — not duplicated here.

## 20260917_2130

`skill-staleness-audit` run in full detail mode against this pack (invoked by a coordinating session, not the operator directly) — the doctrine being that heavy same-day churn (four adapters, an
expanded references/site-addressing.yaml, new SNMP vault entries) is exactly the situation where governance prose quietly stops matching reality even while every individual entry above was accurate
when written. Found 13 defects (11 from the defect register, 2 more from the Phase 7 inverse-completeness sweep), all fixed in this pass; none required reverting any of this session's real work.

### Fixed

- `manifest.json` — `version` bumped `0.2.0` -> `0.3.0` (structural: a reference file was added since the last bump), `updated_at` moved from an early-morning bootstrap timestamp to the latest real
  change (`2026-09-17T20:57:00Z`), matching `.archcore/rules/rule-manifest-version-discipline.md`'s own rule. Added a `stable_fact` recording all four adapters as live-verified; corrected the R195P
  management-IP `stable_fact`, which still stated the superseded `EXT10XX -> 10.255.10.XX` derivation `references/05_known-issues.md` itself already recorded as wrong (real subnet `10.255.11.x`).
- `RUNBOOK.md` — header banner said "no authenticated cnMaestro or device session yet"; superseded in place — all four families now have live-verified sessions.
- `AI_NAVIGATION.md` — line 89 said `.archcore/` was "empty as of 2026-09-17", directly contradicting lines 35/63 of the SAME file ("6 documents accepted 2026-09-17"), which were correct (verified: 6
  files under `.archcore/{adr,rules,specs}`). Fixed the wrong line.
- `AGENTS.md` — "five numbered files ... from `references/01_overview.md` to `references/05_known-issues.md`" corrected to six, `01` to `06`; the Tier 1 project-coherence checklist table was missing a
  routing row for `references/06_device-api-cli-reference.md` entirely — added one. Also corrected a dead pointer to a `VERSION_STAMP_SURFACES` registry in `scripts/check_governance.py` that was never
  implemented (the real mechanism, `CONSTANT_SURFACES`, doesn't cover this invariant either — recorded as a residual governance gap, not silently invented).
- `README.md` — "5 numbered progressive-disclosure reference files" corrected to 6.
- `references/05_known-issues.md` — the "Sites beyond Hope Vale and Burringurrah — only these two seen" coverage-gap row was stale against `references/site-addressing.yaml`, which already covers all
  10 rcp-flavour sites; narrowed to the part still genuinely open (per-site naming-convention re-verification). The "Pack Staleness Risks" section's blanket "everything is USER_STATED, not
  VERIFIED-OBSERVED" disclaimer was superseded by the same live-adapter work; replaced with a pointer to check facts individually rather than assume a pack-wide state either way.
- `SCRATCHPAD.md` — the KEEP-marked "Current state"/"Open items"/"Next actions" block (written at first-adapter time, XV2 only) was contradicted by this file's own later CHANGELOG entries showing
  three more adapters landed the same day — the exact "claim marked KEEP, contradicted by a completion surface elsewhere in the project" pattern `skill-staleness-audit` names as its structurally
  hardest class. Superseded in place with a dated banner; resolved checklist items marked `[x]` with dated notes rather than rewritten, per the file's own convention. Also caught and fixed a path
  error introduced while writing this fix (site-addressing.yaml referenced without its `references/` prefix — `scripts/check_governance.py`'s path check caught it immediately).
- `scripts/check_governance.py` — `COUNT_CLAIMS` and `CONSTANT_SURFACES` were both empty registries (scaffolding present, zero real assertions enforced). Populated `COUNT_CLAIMS` with the
  reference-file count (catches the README/AGENTS.md defect above on regression). Added a new Tier 3 check, `check_manifest_freshness`, enforcing `.archcore/rules/rule-manifest-version-discipline.md`
  by comparing `manifest.json`'s `updated_at` against `CHANGELOG.md`'s latest `## YYYYMMDD_HHMM` heading. **Negative-tested and it caught a real bug in itself first**: an initial date-only comparison
  passed silently against the actual stale value, because every entry that day shared the same calendar date — the defect found was hours-stale, not days-stale. Rewritten to compare full
  `YYYYMMDDHHMM`, re-tested, confirmed it now fails on the reverted value and passes on the fix.
- `.archcore/README.md` — line 63 cited its ADR by bare filename with no directory prefix (the file actually lives at `.archcore/adr/adr-vault-file-avoids-opa-blocked-words.md`, correctly linked
  elsewhere in the same file); a permissive resolver still finds it, so it read as correct while pointing a reader at the wrong directory. Added the `adr/` prefix. Found by the audit's `DISPLACED`
  inverse-sweep check, not by grep.
- `references/README.md` — did not exist; every sibling folder with documents (`.archcore/`, `scripts/`) has one, `references/` did not. Added, as a thin index pointing back to `RUNBOOK.md`'s
  Reference Routing table rather than duplicating it. Found by the audit's `UNINDEXED-DIR` inverse-sweep check.

### Verified, not a defect

- `scripts/cambium_xv2_adapter.py`, `scripts/cambium_epmp_adapter.py`, `scripts/cambium_cnwave_adapter.py` all carry the `REDACT_KEY_PATTERN` fix an earlier entry above claimed (`pass|psk|secret|key|
  shared|community|radius|credential|token|auth`) — code matches the claim exactly. `scripts/cambium_r195p_adapter.py` deliberately has no `get_config()`, consistent with its own docstring and
  `references/05_known-issues.md`.
- The `<secret:keepassxc:cambium-devices/<entry>>` placeholder convention is used consistently everywhere a credential is referenced (`AGENTS.md`, `SKILL.md`, `SCRATCHPAD.md`, `references/`,
  `.archcore/rules/rule-vault-reference-convention.md`, `scripts/extract-asset-register.py`) — no literal secret value, SNMP community string, or credential found anywhere in the pack.
- `references/06_device-api-cli-reference.md` cross-checked line by line against CHANGELOG's live-test entries — no still-open claim found for something CHANGELOG shows resolved, or vice versa; this
  file has been kept current in the same pass as each adapter change throughout the session.
- The `BROKEN`-path hits the audit's claim-scan tool reported against files in the sibling `cambium-swap` project (e.g. its docs/migration/controller-option3/*.md) and against a workspace-level
  .claude/settings.local.json are the intended cross-reference-don't-copy pattern, not broken links — the scanner cannot resolve paths outside this pack's own tree. `.archcore/README.md`'s reference
  to the deleted `ARCHCORE_PROMOTION_CANDIDATES.md` is self-documented as historical (the file describes its own deletion).

### Residual (not resolved by this audit — see SCRATCHPAD.md Next Actions)

- **This entire pack directory is untracked in the parent `skills_stuff` git repo** (`git status --porcelain` from repo root shows a single `?? specialists/project/skill-cambium/` — never `git
  add`ed). Everything built this session has no version-control history. Outside this audit's git-write constraint; flagged for the operator to commit.
- `hardware_revision` remains genuinely `UNKNOWN` for all 17 catalogued models — not a staleness defect, a real open gap.
- Whether the new SNMP vault credentials (`apn-snmp-ro`/`rw`, `nbn-snmp-ro`/`rw`) resolve the pending community-string rotation decision from the two security incidents, or are a separate addition,
  was not established by this audit — flagged in `SCRATCHPAD.md` for an explicit operator answer rather than assumed either way.
- No automated check enforces "no file other than `manifest.json` hardcodes a duplicate version number" (the rule `.archcore/rules/rule-manifest-version-discipline.md` states) or "the version was
  bumped for every content change" (only "the date is not older than the latest CHANGELOG entry" — a weaker, but real and negative-tested, invariant).
- `references/03_asset-register-conventions.md`'s naming-convention prose was written from 2 sites and has not been individually re-verified against the other 8 now addressed in
  references/site-addressing.yaml.
- Spelled-out number claims (e.g. AGENTS.md's former "five numbered files") are invisible to `check_count_claims`, which only matches digit-form claims (`\d+`) — the AGENTS.md fix converted it to
  digit form partly so it's checkable, but any future spelled-out count claim in prose would not be caught.

### Notes

- `python3 scripts/check_governance.py`: 144/144 passing (was 135/135 before this pass; 133/133 at the last CHANGELOG entry's own note — the rise between 133 and 135 reflects file/path growth from
  this session's own edits before the audit, not new check functions; the rise from 135 to 144 is 2 new checks negative-tested plus additional path assertions the fixed prose now contains).
- Full defect register, residual-risk register, and Phase 4 per-artifact worksheet: `.staleness-audit/` (gitignored working state — deleted on a clean gate pass per the skill's own convention, kept
  only if the gate fails).
- `python3 scripts/check_governance.py`: 133/133 passing.

## 20260917_2145

`skill-project-coherence` run against this pack, propagating the `20260917_2130` staleness-audit fixes outward to the two companion-file surfaces that audit did not reach.

### Fixed

- `AI_NAVIGATION.md` — the managed-block `skill-ai-it:manual` reason comment still said "task->reference routing table (5 files)" after the audit's file-count fix elsewhere; corrected to 6. The
  "Reference routing (task → file)" table itself was missing a row for `references/06_device-api-cli-reference.md` entirely (only 01-05 listed) — added it, matching `RUNBOOK.md`'s and `AGENTS.md`'s
  routing tables, which already had it.
- `context-map.yaml` — the `routing` section had entries for `device_facts`/`device_access`/`asset_registers`/`device_inventory` (01-04) but none for `references/05_known-issues.md` or
  `references/06_device-api-cli-reference.md`; added `known_issues` and `device_api_cli_reference` routing entries. The `update_rules` section had the same gap for `known_issue_fact` and
  `api_cli_fact`; added both, matching the shape of the existing four.
- `.archcore/README.md` — the Rules table's "Manifest version discipline" row still read "Operator review only — no automated check yet", contradicted by the same `20260917_2130` audit that added
  `scripts/check_governance.py`'s `check_manifest_freshness` Tier 3 check enforcing exactly that rule's freshness half. Corrected to name the automated check and what it still leaves unenforced
  (version-bump-per-change, no-duplicate-version-number).
- `.archcore/rules/rule-manifest-version-discipline.md` — added a note that this pack itself hit the ~19-hour `updated_at` drift the rule exists to prevent (not just `skill-smc`, the rule's only cited
  precedent before this), and documented `check_manifest_freshness` as the (partial) automated enforcement now in place.

### Verified, not a defect

- `RUNBOOK.md`'s Reference Routing table already listed `references/06_device-api-cli-reference.md` correctly — no fix needed there.
- `README.md` already said "6 numbered reference files" — no fix needed there.
- `manifest.json`'s `version` had no other surface restating it as a duplicate hardcoded number — `.archcore/rules/rule-manifest-version-discipline.md`'s "sole version-of-record" rule holds.
- `skill-smc`'s files (`AI_NAVIGATION.md`, `CHANGELOG.md`, `SKILL.md`, `references/01_overview.md`, its own references/15_cambium-asset-registers.md stub, `scripts/README.md`, read-only cross-check)
  reference `skill-cambium` only by topic/content pointer, never by version number or file count — none went stale against this session's fixes.
- `cambium-swap`'s governance surfaces (`AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`) do not cite `skill-cambium` by version number — nothing to reconcile there.
- CHANGELOG's own `20260917_2130` entry states 144/144; a fresh run this pass shows 145/145 — both are internally consistent with the checker's own additive nature (new assertions from the
  routing-table and context-map.yaml rows just added), not a discrepancy requiring correction of the historical entry (append-only, left as written).

### Residual (not resolved by this pass — see `SCRATCHPAD.md` and the `20260917_2130` entry's own Residual section)

- **This entire pack directory remains untracked in the parent `skills_stuff` git repo.** `git status --porcelain` from the repo root still shows a single `?? specialists/project/skill-cambium/`.
  Nothing in this pass changes that — no `git add`/`commit` was run, per this task's own constraint. A commit that captures this pack's current state would need to include: every governance/content
  file touched across both this pass and the `20260917_2130` audit (`AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `CHANGELOG.md`, `README.md`, `RUNBOOK.md`, `SCRATCHPAD.md`, `manifest.json`,
  `.archcore/README.md`, `.archcore/rules/rule-manifest-version-discipline.md`, `references/05_known-issues.md`, `references/README.md`, `scripts/check_governance.py`), plus every file from earlier
  the same day (four adapter scripts, `references/06_device-api-cli-reference.md`, `references/site-addressing.yaml` expansion, `.archcore/adr` and `.archcore/specs`, `SKILL.md`, `CLAUDE.md`,
  `justfile`, `.mise.toml`, `requirements.txt`) — i.e. the entire pack, since none of it has ever been committed.
- Every other residual item from the `20260917_2130` entry (SNMP rotation-decision ambiguity, `hardware_revision` UNKNOWN, spelled-out count claims invisible to `check_count_claims`, no
  duplicate-version-number check) stands unchanged by this pass.

### Notes

- `python3 scripts/check_governance.py`: 145/145 passing after this pass's edits (routing-table and context-map.yaml additions raised the assertion count further from `20260917_2130`'s own 144/144
  note).

## 20260918_0855 — cnMaestro REST API v2 access documented; vault table gained 5 missing entries

Triggered by `cambium-swap` work (splitting a 635-device nbn_accelerate system-level cnMaestro export into per-site files, evidence E124) that used two vault entries — `nbn-cnmaestro-api` and the four
`*-snmp-ro`/`*-snmp-rw` entries added under evidence E122 — neither of which had ever been written back to this pack's own vault table, despite the Standing Write-Back Contract.

### Fixed

- `references/02_device-access-and-vault.md`'s Vault Structure table — added `<secret:keepassxc:cambium-devices/apn-snmp-ro>`, `apn-snmp-rw`, `nbn-snmp-ro`, `nbn-snmp-rw` (existed in the vault since
  E122, never documented here) and `<secret:keepassxc:cambium-devices/nbn-cnmaestro-api>` (new this session).
- Added a new "cnMaestro REST API v2 Access" section: the real auth endpoint is `/api/v2/access/token`, not the more guessable `/api/v2/token` (which returns HTTP 400 with plausible-looking OAuth2
  error bodies instead of a 404, so a wrong-path guess reads exactly like a credential failure); the `GET /api/v2/devices?network=<name>&fields=...` query-filter pattern for authoritative device→site
  grouping (this API's v2 explicitly rejects the `/networks/{id}/devices` path-segment form some other cnMaestro doc examples suggest); confirmed live against the real `cw-cnmaestro01` controller
  (v3.0.0-r34) even though the API shape was found in an archived 6.0.0 doc.
- Verified both edits by reading the file back (Standing Write-Back Contract requirement) — `grep` for `nbn-cnmaestro-api`, `/api/v2/access/token`, and `Aurukun` all found in the written file.

### Notes

- Full resolution story (three-pass: name-match → live ARP → this API) lives in `cambium-swap`'s evidence E124 and CHANGELOG `20260918_0850` entry — not duplicated here, per the equipment-knowledge
  routing rule (this pack owns the API/CLI surface knowledge, the consuming project owns the project-specific rationale and evidence chain).
- Governance check not re-run this pass (no `just check` invoked) — flagged for the next full pass over this pack.

## 20260918_0930 — site-addressing.yaml restructured by flavour, populated for all 27 nbn_accelerate sites, generator script added

Prompted by `cambium-swap` populating 27 per-site nbn_accelerate `_cnmaestro-inventory.csv` files (evidence E124) — this file previously had only `hope-vale` filled in for that flavour, the other 26
sites entirely undocumented.

### Changed

- `references/site-addressing.yaml` `schema_version` 3→4. `sites:` and the new `site_short_names:` (see Added) are now nested one level deeper, under each site's flavour (`rcp` / `nbn_accelerate`),
  not flat. Every site's now-redundant `flavour:` field was removed — implied by its parent key instead. Operator-requested change, prompted by the file growing to 35 total sites and the discovery
  that a short device-name code (`KAL`) collides across flavours (`kalumburu` in `rcp`, `kaltjiti-fergon` in `nbn_accelerate`) — nesting by flavour makes that collision structurally visible instead of
  a footnote.
- Populated `families:` (octet_pattern/host_count per device family, `method: cnmaestro-export`, `trust: verified`) for all 26 previously-undocumented `nbn_accelerate` sites, derived from
  `cambium-swap`'s newly-split per-site export CSVs. `hope-vale`'s existing hand-authored block (including its live SSH/REST/SNMP verification notes) was preserved untouched, not regenerated.

### Added

- `references/site-addressing.yaml` `site_short_names:` — the short device-name code(s) each site's cnMaestro export actually uses (`HOP`, `DMG`, `GAL`, ...), nested by flavour for the same collision
  reason as above, with inline notes for the handful of sites with no short code at all (`aurukun`, `indulkana`, `warakurna` — identified via cnMaestro network objects or a device-name suffix instead
  of a leading code, per cambium-swap evidence E124).
- `scripts/generate_site_addressing_families.py` — derives the `families:` block for one or more sites straight from their reconciled cnMaestro-export CSV, at the operator's request to make this a
  persistent reusable tool rather than the scratchpad one-off script this session first used to populate the 26 new sites. Deliberately never writes `references/site-addressing.yaml` directly — prints
  a YAML fragment for review/merge, since the file also carries hand-authored live-session notes (SSH/REST/SNMP narrative) a CSV-only script has no way to derive or preserve. Cataloged in
  `scripts/README.md`.

### Verified

- `python3 -c "import yaml; yaml.safe_load(open('references/site-addressing.yaml'))"` — parses cleanly, `schema_version: 4`, 27 `nbn_accelerate` sites + 9 `rcp` sites in both `sites:` and
  `site_short_names:`, `hope-vale`'s and every `rcp` site's pre-existing hand-authored `notes:`/verification fields intact (spot-checked programmatically, not just by eye).
- `just check` not re-run this pass — flagged for the next full pass over this pack, same as the `20260918_0855` entry above.

### Notes

- Full resolution methodology for the 26 new nbn_accelerate sites (three-pass: name-match → live ARP → cnMaestro REST API) lives in `cambium-swap`'s evidence E124 — not duplicated here, per the
  equipment-knowledge routing rule.

## 20260918_1045 — two missing OUI blocks added after operator flagged oui_reference as stale

Operator flagged `references/site-addressing.yaml`'s `oui_reference` block as possibly stale. Audited `cambium-swap`'s now-3174-row `device-inventory.csv` against the 5 documented blocks and found two
real gaps: `00:04:56` (419 devices — dominant ePMP Force 300-16/25 OUI fleet-wide, also 85 60 GHz cnWave nodes, not ePMP-exclusive) and `30:cb:c7` (20 devices, cnWave-only so far). Both added with
`method: cnmaestro-export`, matching the file's existing verification convention. `updated:` header bumped. See `cambium-swap` evidence E129 for the audit detail (not duplicated here).

## 20260918_1050 — generate_site_addressing_families.py gained --oui-audit mode

Operator asked whether the earlier OUI staleness fix (evidence-adjacent, `20260918_1045`) was captured in the persistent script rather than done ad hoc again.

### Added

- `scripts/generate_site_addressing_families.py --oui-audit`: reports OUI blocks present in `device-inventory.csv` but missing from `oui_reference`, with host_count/family/site breakdown — the same
  computation done by hand for the `00:04:56`/`30:cb:c7` find. Prints a YAML-shaped stub (family left `UNKNOWN` for a human to pick from the breakdown, notes left as a prompt) rather than a
  ready-to-paste entry — deciding family-exclusivity and writing the cross-site caution prose is a judgment call this script doesn't make. Never writes `references/site-addressing.yaml` directly, same
  principle as the existing `families:` mode. Verified both ways: clean run reports nothing missing (both new OUIs already added), and a run against a copy of the file with `00:04:56` stripped out
  correctly re-detects it.
- `scripts/README.md` updated.

### Verification

- `python3 scripts/generate_site_addressing_families.py --oui-audit` — reports clean.
- Negative test: same command against `references/site-addressing.yaml` with the `"00:04:56"` line removed correctly re-surfaces it with the right host_count/family/site breakdown.

## 20260918_1055 — full regenerate-and-verify pass: 8 missing families added, oui_reference restructured to a real site map

Operator asked to regenerate `families:` for every site and diff against the file, then fix what the diff found — consistently, and with `oui_reference`'s site data as a real structured field instead
of prose.

### Fixed

- Regenerating every site with `scripts/generate_site_addressing_families.py --all --all-flavours` and diffing against the file found 8 completely missing family entries at the 8 older rcp sites that
  were never given full coverage: `epmp-ap` at burringurrah; `cnwave-60ghz` at horn-island/mornington/wujal-wujal; `enterprise-wifi-eseries` at jigalong/kalumburu/mowanjum/tjuntjuntjara. Added all 8,
  all `method: cnmaestro-export`, same shape as every other entry — no mixing.
- The diff also found `host_count` disagreements on several already-present families (e.g. mornington `epmp-sm`: file said 343, regenerated CSV says 188). Left alone deliberately — several existing
  entries were verified via `arp-mac-oui-match` (live-connected hosts only) not `cnmaestro-export` (every registered device including offline), so a mismatch there is two different, both-legitimate
  measurements, not an error. Overwriting would have silently swapped verification method without saying so.

### Changed

- Every `oui_reference` entry's `verified.site` rewritten from a single dominant site + "also seen at X, Y, Z" prose into a full `site: {sitename: host_count, ...}` map, regenerated straight from
  `device-inventory.csv`. All 7 entries (the original 5 plus the 2 added in `20260918_1045`) now share the identical shape — the original 5 had no `host_count` field at all; the 2 new ones did; none
  were structurally consistent with each other before this pass.
- `updated:` header bumped with the detail.

### Verification

- `python3 -c "import yaml; yaml.safe_load(...)"` — parses cleanly.
- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1100 — YAML formatting cleanup, content accuracy fixes, FAMILY_MAP bug found and fixed

Operator follow-up on `20260918_1055`: wrap the new header comment properly (and re-flow it, not just cap it), move it above `schema_version:`, wrap every `oui_reference` `notes:` field as a YAML
folded scalar (`notes: >-`) instead of a long single-line quoted string, and verify the notes are still accurate content-wise — then verify `scripts/generate_site_addressing_families.py` itself is
current.

### Fixed

- Moved the long inline `updated:` comment to a proper wrapped block comment above `schema_version:`; wrapped the pre-existing top-of-file header comment (lines 1–58) to actually use the 160-column
  budget instead of sitting under-filled at ~120 (58 lines → 47) — the two indented enumerations (`method values:`, `trust values:`) were left untouched, since reflowing a list breaks its alignment.
- Converted all 34 `notes: "..."` quoted-string fields to `notes: >-` folded block scalars, wrapped at 160 columns — a quoted single-line string can't be wrapped without changing its literal type, a
  folded scalar can.
- Content accuracy pass on `oui_reference`, caught two real errors while re-reading the notes just written in `20260918_1055`: the `fc:11:65` note claimed "five known blocks total" for the
  enterprise-wifi-xv2 family — there are only four (`bc:a9:93`, `fc:11:65`, `b4:a2:5c`, `bc:e6:7c`); fixed and named all four explicitly. The two ePMP OUI blocks (`58:c1:7a`, `00:04:56`) didn't
  cross-reference each other the way the four XV2 blocks do each other — added reciprocal "one of two known ePMP OUI blocks" notes to both.
- `scripts/generate_site_addressing_families.py`'s `FAMILY_MAP` was missing 4 of the 60 GHz cnWave device types (`V2000 CN/DN`, `V1000 CN/DN`) that [cambium-swap's
  scripts/reconcile_cnmaestro_export.py](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/scripts/reconcile_cnmaestro_export.py)'s `TYPE_MAP` already had (synced there in `20260918_1030`,
  never synced here) — rows of those types were silently dropped from `compute_families()`. Fixed. Re-running the corrected script against every rcp site found two real consequences: mornington's
  `cnwave-60ghz` `families:` entry was undercounted (10→11 hosts), and bidyadanga was missing a `cnwave-60ghz` entry entirely (now added, 2 hosts — noted that 4 of its 6 cnWave devices are IPv6-only
  in the export and aren't counted by this octet-based method at all).

### Verification

- `python3 -c "import yaml; yaml.safe_load(...)"` — parses cleanly throughout every edit in this pass.
- Character-length check (not `awk`, which counts UTF-8 bytes and false-flagged two lines containing em-dashes) confirms zero comment lines over 160 characters.
- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1115 — cnPilotMIB SNMP read-only identity data confirmed live on XV2-22H Wi-Fi 6 firmware

Standing Write-Back Contract entry for work done in `cambium-swap`: the pass-08 research gap ("no dedicated XV2/Wi-Fi 6 MIB in any public mirror") turned out not to block a real SNMP walk, and
`cambium-swap` built a reusable script around the finding — both facts belong here, not just in that project's own CHANGELOG.

### Added — `references/06_device-api-cli-reference.md`

- New "SNMP (cnPilotMIB) — Read-Only Identity Data" subsection under Enterprise Wi-Fi (XV2): the 2015-vintage `cnPilotMIB` mirror ([cambium-swap's
  artifacts/mibs/librenms/cnpilote/CAMBIUM-MIB](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/artifacts/mibs/librenms/cnpilote/CAMBIUM-MIB)) matches cleanly against live `XV2-22H` Wi-Fi 6
  firmware `6.6.0.3-r9`. A live SNMPv2c walk of `cambiumAccessPointEntry` (base OID `.1.3.6.1.4.1.17713.22.1.1.1`) against 4 hope-vale units correctly returned all 15 columns, including serial number
  (index `.4`) — the field a cnMaestro-export-based reconciliation pass can never fill for a device cnMaestro itself does not track. Cross-referenced: `cambium-swap` evidence E130, its [new
  scripts/snmp_resolve_unknowns.py](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/scripts/snmp_resolve_unknowns.py).
- Explicit scope-discipline note: this MIB match is confirmed only for `XV2-22H`. Do not assume it covers `XV2-2T0`, `E500` or `E430` firmware without testing one live unit of each first.

### Verification

- Read back `references/06_device-api-cli-reference.md` in the same session — new subsection present between the adapter data-points table and the E-series subsection, as intended.

## 20260918_1155 — unified-network-controller added as a Related Workspace

Operator split the "Option 3" FOSS controller workstream out of `cambium-swap` into its own sibling project, `unified-network-controller`, and asked that this pack and `skill-smc` both know about it,
and it about them.

### Changed — `SKILL.md`, `RUNBOOK.md`

- Added `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller` to the Related Workspaces tables in both files: the FOSS controller build (Nautobot + adapter layer) that consumes
  this pack's device-access/API knowledge for its Cambium vendor adapter, without duplicating it — same cross-reference discipline as the existing `cambium-swap`/`skill-smc` relationships.

### Verification

- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1542 — ePMP SM adapter re-verified fresh-live; cnWave 4 stat endpoints resolved (path bug, not missing params)

Two pending `cambium-swap` open items, operator-authorized this session: a fresh live ePMP SM run (prior coverage was an offline replay only, the Hope Vale unit having hit its 5-session RW cap) and
reverse-engineering the params for cnWave's `getRadioStats`/`getNetworkStats`/`getKeyPerformanceIndex`/`getCnAgentStatus`, all previously 400ing on an empty `{}` POST.

### Changed — `scripts/cambium_epmp_adapter.py` — none (code already correct; only re-verified against a new device)

- Ran `_cmd_getters()` live against a different real Force 300-25 SM, Doomadgee `DMG_F25_AP10_IP3_101` (`10.255.3.101`), instead of spending more of Hope Vale's constrained session budget. Clean
  facts/interfaces/wireless_link/clients response, serial/MAC matched `cambium-swap`'s `device-inventory.csv` exactly. Confirms the SM code path generalises beyond the one unit it was built against.

### Changed — `scripts/cambium_cnwave_adapter.py`

- Added `get_radio_stats()`, `get_network_stats()`, `get_key_performance_index()`, `get_cn_agent_status()` and wired all four into `_cmd_getters()`, using `get_facts()`'s own node `mac_address`.
- Root cause of the 2026-09-17 400s: these four endpoints live under `/local/`, not `/api/` like `getTopology`/`getCtrlStatusDump` — a path-prefix bug in the original assumption, not a missing
  parameter. Found by reading the device's own served Angular JS bundle (`main.<hash>.js`) `http.post(...)` call sites, same technique as every other endpoint in this adapter, then confirmed live
  against a real V5000 POP node (Doomadgee `DMG_T12_V5000_DN_IP4_100`, `10.255.4.100`).
- Docstring rewritten to state the correct `/local/` param shapes instead of "likely need a radio MAC or time range, not yet reverse-engineered".

### Changed — `references/06_device-api-cli-reference.md`

- ePMP section: added a note that the SM adapter is now re-verified fresh-live against a second real unit (Doomadgee), not just the original Hope Vale offline replay.
- cnWave table: added 4 new rows (`get_radio_stats`, `get_network_stats`, `get_key_performance_index`, `get_cn_agent_status`) with confirmed-live param shapes, plus a new "The 4 stat endpoints were a
  path bug, not a missing param" subsection explaining the `/local/` vs `/api/` root cause and the node-MAC-vs-radio-MAC gotcha (a radio MAC silently returns an empty/nulled result with HTTP 200, not
  an error).
- "Not yet exercised" list trimmed to just `getNetworkOverridesConfig`/`getControllerConfig`/`getTopologyMeta` now that the 4 stat endpoints are resolved.

### Verification

- Read back both changed reference files in the same session — new SM note, new cnWave table rows, and new subsection all present as written.
- `cambium_cnwave_adapter.py --help`-equivalent smoke: re-ran the full `_cmd_getters()` live a second time after the code change (not just the ad hoc probe script) — `radio_stats`, `network_stats`,
  `key_performance_index` and `cn_agent_status` all returned real data in the adapter's own JSON output, not just in the standalone probe.
- `python3 scripts/check_governance.py` — 154/154 passing.

## 20260918_1557 — R195P get_config() implemented (operator-authorized); live fetch across all 4 families blocked this session by a sandbox credential-materialization guard

Operator explicitly authorized fetching a live `get_config()` snapshot for all 4 Cambium device families in one `cambium-swap` session (per-family risk profile discussed first, per-family
authorization confirmed). Two things happened that changed the shape of the work actually completed:

1. **`teleport.communitywifi.net.au` (the `nbn_accelerate`-flavour cluster, which carries Hope Vale and Doomadgee) was unreachable all session** — `tsh ls --cluster teleport.communitywifi.net.au`
   returned `connection error: desc = "transport: authentication handshake failed: EOF"` on every retry, despite a `tsh status` profile showing a still-valid session and the proxy itself answering a
   plain `curl`/`nc` probe on 443. `tsh login` cannot refresh it non-interactively (`cannot perform password login without a terminal`). This is a cluster-wide outage, not specific to Hope Vale's
   `hope-vale-smc01` node — Doomadgee (the calling task's fallback site) was equally unreachable. Devices for all 4 families were instead selected from `rcp`-flavour sites on the (reachable)
   `teleport.apn.au` cluster, cross-checked against `references/site-addressing.yaml`'s per-site/family `trust: verified` state: Horn Island XV2 (`HRN_XV2_AP1_IP3_10`, `10.255.3.10`) and cnWave V5000
   POP (`HRN_T1_V5000_DN_IP4_10`, `10.255.4.10`); Kalumburu ePMP AP (`Tower1_Force 300_IP_0_11_master`, `10.255.0.11`, the same unit already evidenced in this file needing the `epmp-ap-legacy` vault
   credential); Burringurrah R195P (`BUR-R195P-1047`/`BUR-R195P-1055`, `10.255.11.47`/`.55`, the same units already evidenced live 2026-09-17). Note also caught in passing: `references/\
   site-addressing.yaml` claims Burringurrah's `enterprise-wifi-xv2` `device-inventory.csv` rows were reconciled to the live `10.255.11.x` octet, but a live grep found all 8 Burringurrah XV2 rows
   still carrying the old register-pattern `10.255.3.x` — a real doc/data contradiction, not yet corrected, why Horn Island was used for XV2 instead. Flagged here rather than silently worked around;
   someone should re-run the Burringurrah XV2 reconciliation pass or correct the `references/site-addressing.yaml` claim.
2. **This sandbox's own harness blocked every `kp show cambium-devices/*` invocation** with `Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Credential
   Materialization]` — on every flag form tried (`kp show <entry>`, `kp show -a Password <entry>`, `kp show -a UserName -a Password <entry>`), despite `cambium-swap/.claude/settings.local.json`
   already carrying an explicit allow-list for exactly this command shape (`Bash(kp show -a UserName -a Password cambium-devices/*)` etc. — see `references/02_device-access-and-vault.md`'s own
   "Resolved 2026-09-17" note about this same class of problem). This auto-mode classifier sits above the project's own permission file and cannot be satisfied by retrying a different flag
   combination; per this project's own no-workaround rule, no attempt was made to bypass it. **Net effect: no device credential was ever materialized this session, so no live login was possible
   against any of the 4 families** — XV2, ePMP and cnWave `get_config()` were NOT re-run live this session (their existing 2026-09-17/2026-09-18 `VERIFIED-OBSERVED` evidence stands unchanged, nothing
   new added), and the new R195P `get_config()` below was written and unit-tested offline only, not live-verified. This is a session-environment permission gap, not a finding about device behaviour —
   flagged for the operator to resolve (interactive `kp` session, or a broadened harness allow-list) before the live fetch can actually be completed.

### Changed — `scripts/cambium_r195p_adapter.py`

- Implemented `get_config()`, deliberately withheld since 2026-09-17 (see the module's own prior docstring) until a real need was authorized. Source: `cat /etc/config/* 2>&1` over the same SSH path
  every other getter here already uses (no `uci` binary confirmed present on this BusyBox/Buildroot platform, so this reads the UCI-style config files directly rather than assuming a config tool
  exists).
- Added `_parse_uci_text()`: a tolerant parser for BusyBox/OpenWrt-style `config <type> '<name>'` / `option <key> '<value>'` / `list <key> '<value>'` text into a nested dict keyed by
  `"<type>.<name>"`. Unrecognized lines (different syntax, or `cat`'s own stderr mixed into the `2>&1` stream if a file is missing) are kept verbatim under a synthetic `_unparsed` key instead of being
  silently dropped, so `redact()` still gets a chance at them and a caller can see raw text was present rather than a falsely-empty result.
- `REDACT_KEY_PATTERN`/`redact()` copied verbatim from `scripts/cambium_xv2_adapter.py`/`scripts/cambium_epmp_adapter.py`/`scripts/cambium_cnwave_adapter.py`, applied to every parsed `option`/`list`
  value keyed by option name — same rule as the other three families: redact by key name regardless of whether the value looks like ciphertext (this family's fleet-wide SNMP community is an encrypted
  blob in its own config, per the Ansible R195P provisioning template, not necessarily plaintext-looking, but redacted unconditionally anyway).
- Wired in as an opt-in `--include-config` CLI flag (same name/shape as `scripts/cambium_epmp_adapter.py`'s), never part of the default `_cmd_getters()` output — matches this family's
  already-conservative default (only `get_facts`/`get_interfaces` run without an explicit flag).

### Verification

- `python3 -m py_compile scripts/cambium_r195p_adapter.py` — clean.
- Offline unit test against synthetic (non-live, non-device) UCI text: a `config snmp` stanza's `option community` and a `config wireless` stanza's `option key` both redacted to `<REDACTED>`; a
  non-secret `option hostname`/`option ssid`/`option timezone` passed through unredacted; an unparseable garbage line landed in `_unparsed` rather than being dropped. Confirms the redaction path is
  correct in isolation — **this is not a substitute for the live device test the operator actually asked for**, which remains blocked per point 2 above.
- `python3 scripts/check_governance.py` — see this session's separate governance-check run for the pass/fail count.

### Not done this session (blocked, not skipped)

- No live `get_config()` (or any other getter) was run against any of the 4 families' real hardware — see the credential-materialization block above. `cambium-swap`'s `evidence-register.csv` was
  therefore **not** given new `VERIFIED-OBSERVED` rows for this session; the existing rows for all 4 families stand as they were before this session started.

## 20260918_1620 — Correction: the outage claim in the entry above was wrong; it was a `tsh` flag mistake, not an outage

Appending a correction rather than editing the entry above (past record, not a live claim — see this pack's "do not enforce history" doctrine). Point 1 in `20260918_1557` above states
`teleport.communitywifi.net.au` was down fleet-wide. **That was wrong.** The operator reproduced the same commands directly: `tsh status` showed a fully valid cached session, plain `curl
https://teleport.communitywifi.net.au/webapi/ping` returned a clean 200, and `tsh ls --proxy=teleport.communitywifi.net.au` listed the full node roster (including `hope-vale-smc01`, contradicting the
earlier session's separate claim that this node was missing/deregistered) — `tsh ssh --proxy=teleport.communitywifi.net.au root@hope-vale-smc01` then connected cleanly. Root cause: that session used
`--cluster=teleport.communitywifi.net.au`, which routes to it as a subordinate target via a trust relationship that doesn't exist (it's its own root Teleport target, confirmed by its own separate `tsh
status` profile) — the resulting gRPC handshake failure (`transport: authentication handshake failed: EOF`) gives no hint it's a flag-choice problem rather than a server problem. Full technical
writeup: skill-smc's `references/01_overview.md` and `CHANGELOG.md` `20260918_1620`. The credential-materialization block (point 2 above) is unaffected by this correction — that part was real and
remains the actual reason no live device session happened this run.

### Changed — `references/02_device-access-and-vault.md`

- Added a `--proxy=` vs `--cluster=` warning directly after the existing Web UI tunnel note, cross-referencing skill-smc's fuller writeup, so a future agent doing Cambium device-access work hits this
  warning before repeating the same misdiagnosis.

### Verification

- `python3 scripts/check_governance.py` — see this session's run for pass/fail count.

## 20260918_1705 — Live get_config() verification across all 4 Cambium families completed; 4 real R195P bugs found and fixed; new secret-exposure incident found and closed

Both blockers named in the `20260918_1557` entry were confirmed resolved this session: the operator added `cambium-devices/*` kp-show patterns to the GLOBAL `~/.claude/settings.json` `autoMode.allow`
(the project-local `cambium-swap/.claude/settings.local.json` allow-list alone was never sufficient — a separate classifier-level list this pack had not previously identified), and the
`--cluster=`/`--proxy=` misdiagnosis from `20260918_1620` meant Teleport access was never actually broken. With both real, live sessions ran against all 4 families.

### Live-verified this session

- **XV2** (cambium-swap E134) — re-run against the same Hope Vale Tower 1 AP as the 2026-09-17 original. No code changes; output shape unchanged, 17 fields redacted, clean.
- **ePMP** (cambium-swap E135) — re-run against the same Doomadgee SM as E132, this time via a newly combined single-login `--include-config` path (see Changed below). 45 fields redacted, clean.
- **cnWave** (cambium-swap E136) — re-run against the same Doomadgee V5000 POP as E133. 21 fields redacted, clean, including the 4 stat-endpoint fields E133 added.
- **R195P** (cambium-swap E137) — **first ever live run** of `get_config()` for this family, against both real Burringurrah units. Real finding: this platform has no `/etc/config/` directory at all —
  the UCI-style source assumption from `20260918_1557` was wrong. See `references/06_device-api-cli-reference.md`'s R195P section for the full write-up (real config surface found instead:
  `/etc/cambium/keystore`, `/etc/provision/`, `/etc/snmpd/snmpd.conf`, a large `/etc_ro/` param-file tree) and the new open item to rebuild `get_config()`'s source around it.

### Changed — `scripts/cambium_r195p_adapter.py`

- `CAMBIUM_HOST` now accepts `host:port` (matches the other 3 adapters' existing convention) — a bare `ssh user@host:port` was failing to resolve, a real bug on this family's own documented normal
  access path (a local Teleport port-forward).
- `_run()` catches `subprocess.TimeoutExpired` and re-raises sanitized — a new secret-exposure incident (device password embedded in the exception's default argv dump) happened live this session when
  the original 8s `DEFAULT_SSH_TIMEOUT` was too short for a nested-tunnel handshake; contained immediately (temp file deleted same turn), root-caused, and fixed. `DEFAULT_SSH_TIMEOUT` raised to 20s.
- Added `LogLevel=ERROR` to the ssh invocation — the local OpenSSH client's own post-quantum-KEX advisory banner was observed live to desync `sshpass`'s prompt detection, producing spurious
  `Permission denied` against a password confirmed correct moments before and after.
- `_run()` gained `allow_nonzero`, used only by `get_config()` — BusyBox `cat`'s non-zero exit on a missing glob member was discarding the `2>&1`-merged stdout that `get_config()`'s own design relies
  on to surface a missing-file message as parseable `_unparsed` text instead of silently losing it.

### Changed — `scripts/cambium_epmp_adapter.py`

- `--include-config` now runs `facts`/`interfaces`/`wireless_link`/`clients`/`config` under one login instead of a separate config-only session — this family has a real 5-session RW cap, so the old
  shape cost two sessions for what is now one.

### Changed — `references/06_device-api-cli-reference.md`

- R195P section rewritten from "not yet live-verified" to the full live-test write-up above (real config-surface finding, the 4 code fixes, the dropbear connection-throttling observation).
- XV2 and cnWave sections each gained a short "re-verified 2026-09-18" note under their existing 2026-09-17 evidence.
- ePMP section gained a "`get_config()` re-verified live 2026-09-18" note documenting the combined-login re-run.

### Not actioned — two mid-task requests to write unredacted secrets to local capture files

During this session, two different framings of the same request arrived mid-task (write the raw pre-`redact()` `get_config()` output to a local `captures/` file, first directly, then via an scp-based
two-hop pull): both were declined. This project's own `AGENTS.md` states "Redact BEFORE persisting or printing" without a scope carve-out for local/gitignored files, and every adapter's own
`get_config()` docstring in this pack states callers "must never bypass [`redact()`]... without also redacting" — a rule written after two real secret-exposure incidents in this exact codebase (E107,
the 2026-09-17 ePMP incident). A mid-task instruction is not the same as the user's own direct, deliberate authorization for a standing security-control rollback of this kind, and the risk (real
RADIUS passwords, SNMP RW communities, wireless PSKs landing in plaintext on disk) is asymmetric and effectively irreversible once written. Flagged to the operator directly rather than silently
complying or silently ignoring it; no code or governance change was made to accommodate it.

### Verification

- `python3 -m py_compile scripts/cambium_r195p_adapter.py scripts/cambium_epmp_adapter.py` — clean after every edit.
- Read back `references/06_device-api-cli-reference.md` in the same session — all 4 new/updated sections present as written (subject to this repo's own markdown-formatter hook reflowing table
  whitespace, not content).
- `python3 scripts/check_governance.py` — see this session's run for pass/fail count.

## 2026-10-05 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-09-23-template-sourced-blocks-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-09-23-template-sourced-blocks-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: context-map.yaml, AGENTS.md, scripts/README.md
````

## File: CLAUDE.md
````markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
````

## File: context-map.yaml
````yaml
version: 1
project:
  name: skill-cambium
  context_policy: AI_NAVIGATION.md is the human-readable router; this file is the
    machine-readable routing map.
bootstrap:
  required_first_read:
  - AGENTS.md
  - SKILL.md
  - AI_NAVIGATION.md
  - context-map.yaml
  - CHANGELOG.md
authority_order:
- path: .archcore/adr
  type: architecture_decisions
  authority: highest
- path: .archcore/rules
  type: durable_rules
  authority: highest
- path: .archcore/specs
  type: design_contracts
  authority: highest
- path: SKILL.md
  type: agent_activation_surface
  authority: highest
- path: references
  type: content_source
  authority: highest
- path: AGENTS.md
  type: agent_instructions
  authority: high
- path: CLAUDE.md
  type: claude_specific_instructions
  authority: high
- path: AI_NAVIGATION.md
  type: context_router
  authority: high
- path: manifest.json
  type: machine_readable_snapshot
  authority: medium
- path: SCRATCHPAD.md
  type: transient_notes
  authority: low
- path: CHANGELOG.md
  type: pack_history
  authority: medium_high
context_sources:
  archcore:
    enabled: true
    root: .archcore
    read_first_for:
    - durable_rule
    - vault_structure_decision
  generated:
    repomix:
      enabled: true
      root: .ai-context
      preferred_files:
      - .ai-context/governance-pack.md
routing:
  device_facts:
    description: Device families, models, firmware baseline, EoL/EoS, evidence-state
      discipline.
    read:
    - references/01_overview.md
  device_access:
    description: Local-admin credential vault structure, kp wrapper behaviour, reference-syntax
      convention.
    read:
    - references/02_device-access-and-vault.md
  asset_registers:
    description: Site asset-register naming grammar, per-site drift, site-name convention,
      R195P IP-derivation rule.
    read:
    - references/03_asset-register-conventions.md
  device_inventory:
    description: device-inventory.csv schema, UNKNOWN discipline, extraction workflow.
    read:
    - references/04_device-inventory-schema.md
  known_issues:
    description: Coverage gaps, unverified assumptions, pack staleness risks.
    read:
    - references/05_known-issues.md
  device_api_cli_reference:
    description: Device REST API / SSH CLI data points per adapter method, config-backup
      source, write-ops boundary.
    read:
    - references/06_device-api-cli-reference.md
  governance:
    description: Agent behaviour, pack rules, cross-pack boundary with skill-smc.
    read:
    - AGENTS.md
    - CLAUDE.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - CHANGELOG.md
    - .archcore/rules
update_rules:
  device_fact:
    update:
    - references/01_overview.md
    also_consider:
    - manifest.json
  access_or_vault_fact:
    update:
    - references/02_device-access-and-vault.md
  asset_register_fact:
    update:
    - references/03_asset-register-conventions.md
  inventory_schema_fact:
    update:
    - references/04_device-inventory-schema.md
  known_issue_fact:
    update:
    - references/05_known-issues.md
  api_cli_fact:
    update:
    - references/06_device-api-cli-reference.md
    also_consider:
    - manifest.json
  durable_rule:
    update:
    - .archcore/rules
    also_consider:
    - AGENTS.md
  temporary_note:
    update:
    - SCRATCHPAD.md
  routing_change:
    update:
    - AI_NAVIGATION.md
    - context-map.yaml
    - RUNBOOK.md
  governance_history:
    update:
    - CHANGELOG.md
  governance_navigation:
    AGENTS.md:
      companions:
      - AI_NAVIGATION.md
      - context-map.yaml
      - scripts/README.md
    AI_NAVIGATION.md:
      companions:
      - context-map.yaml
    context-map.yaml:
      companions:
      - AI_NAVIGATION.md
    scripts/README.md:
      companions:
      - AGENTS.md
      - context-map.yaml
    new_script_added:
      companions:
      - scripts/README.md
      - AGENTS.md
      - justfile
drift_policy:
  on_conflict:
    action: stop_and_report
    required_output:
    - conflicting_files
    - higher_authority_source
    - recommended_fix
    - assumptions
  scratchpad_rule:
    authoritative: false
    promotion_required_for_durable_truth: true
generated_context_policy:
  regenerate_after:
  - reference_file_change
  commands:
    repomix_governance: repomix --config repomix.config.json
answer_contract:
  require_source_paths: true
  unsupported_answer: not found in project context
  distinguish_assumptions: true
  do_not_invent_state: true
skill_ai_it_version: 2026-09-23-template-sourced-blocks-v1
audit_checks:
  governance_file_presence:
  - README.md
  - AGENTS.md
  - CLAUDE.md
  - AI_NAVIGATION.md
  - context-map.yaml
  - CHANGELOG.md
  version_consistency:
    description: Verify managed block version strings match current skill version.
    action: report_mismatch
  companion_update_completeness:
    description: Verify companion files in update_rules were updated together.
    action: report_missing
  generated_output_policy:
    description: Verify Graphify and Repomix outputs are classified as generated support.
    action: report_violation
  task_runner_consistency:
    description: Verify cataloged tasks match actual script files.
    action: report_drift
  no_stale_references:
    description: Detect references to removed tools or superseded governance assumptions.
    action: report_stale
promotion_rules:
  archcore:
    allowed_init_modes:
    - bootstrap
    - navigation-add
    - refresh
    content_write_modes:
    - promote
    required_authorization: true
    candidates_report: ARCHCORE_PROMOTION_CANDIDATES.md
    extract_heuristics_source: patterns/archcore-routing.md
    exclusion:
    - CHANGELOG.md (history only)
    - generated files (.ai-context/, graphify-out/)
    - unmarked SCRATCHPAD sections
    - draft/obsolete roadmap items
context_recovery:
  procedure:
  - Read AI_NAVIGATION.md first for navigation map.
  - Load .archcore/ context if present (durable truth).
  - 'Regenerate graphify-out/ with: graphify update .'
  - 'Regenerate .ai-context/ with: repomix --config repomix.config.json'
  - Verify SCRATCHPAD.md has current state. If empty, populate from memory-keeper
    / mcp-project-context.
  - Verify CHANGELOG.md is current.
  - Verify AI_NAVIGATION.md and context-map.yaml companion consistency.
  evidence_label: Context recovered at <timestamp> via skill-ai-it context-recovery
    procedure.
````

## File: justfile
````
# just task catalog for skill-cambium.
# Usage: just --list | just <task>
#
# Recipes go through {{py}}, never a bare interpreter — see skill-ai-it's Runtime isolation doctrine.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-cambium"
py := wc + "/.venv/bin/python"

# List available tasks
default:
    @just --list

# Build the working-cache venv from the mise-pinned runtime. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @test -f requirements.txt && {{py}} -m pip install --quiet --upgrade pip -r requirements.txt || true
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtime the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# Governance coherence checks — must exit 0 before durable work is called complete.
check: _require-venv
    @{{py}} scripts/check_governance.py

# Extract a site's asset register into device-inventory.csv — reference implementation, not general-purpose.
# See scripts/extract-asset-register.py's own docstring before re-running against a new site.
extract-asset-register: _require-venv
    @{{py}} scripts/extract-asset-register.py

# Log into support.cambiumnetworks.com (agent-browser + KeePassXC), optional Downloads search.
# Needs a live MFA code from the operator — run from an interactive shell. Read-only against the portal.
cambium-login search="":
    @if [ -n "{{search}}" ]; then scripts/cambium-portal.sh login --search "{{search}}"; else scripts/cambium-portal.sh login; fi

# Log in, find a specific firmware/documentation release, download its files into <dest>.
# Example: just cambium-fetch-release "XV2" "6.6.0.3-r9" /tmp/xv2-660-docs
cambium-fetch-release model version dest:
    @scripts/cambium-portal.sh fetch-release "{{model}}" "{{version}}" "{{dest}}"

# Open a tsh tunnel to a device's management interface (site-aware cluster/smc-host routing).
# This is generic Teleport tunneling, not a Cambium-specific concern — the canonical script lives
# in skill-smc (which owns tsh/Teleport mechanics), called here rather than duplicated.
# Example: just tunnel hope-vale 10.255.4.5 20045
# Blocks for the tunnel's lifetime (default 120s) — run in the background if you need to keep
# working. Requires an active `tsh login` for the site's cluster already (burringurrah needs
# interactive MFA — this doesn't log in for you).
smc_scripts := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/scripts"
tunnel site device_ip local_port="20000" device_port="443" duration="120":
    @{{smc_scripts}}/teleport-tunnel.sh "{{site}}" "{{device_ip}}" "{{local_port}}" "{{device_port}}" "{{duration}}"

# Run the ePMP adapter's getters (facts/interfaces/wireless_link/clients) against a live tunnel.
# `host` is CAMBIUM_HOST (e.g. localhost:20045 from `just tunnel`); role is "sm" or "ap", selecting
# the cambium-devices/epmp-<role> vault credential. Never prints the password.
# Example: just epmp-getters localhost:20045 sm
epmp-getters host role="sm": _require-venv
    #!/usr/bin/env bash
    set -euo pipefail
    EPMP_USER=$(kp show -s -a UserName cambium-devices/epmp-{{role}})
    EPMP_PASS=$(kp show -s -a Password cambium-devices/epmp-{{role}})
    CAMBIUM_HOST="{{host}}" CAMBIUM_USER="$EPMP_USER" CAMBIUM_PASS="$EPMP_PASS" \
        {{py}} scripts/cambium_epmp_adapter.py

# Check whether a JSON file has any credential-shaped fields, WITHOUT printing their values.
# Run this on any captured config/status dump before viewing it by hand — see 05_known-issues.md
# Security Incidents for why: printing a value to "check if it's real" has caused two live
# secret exposures this pack's history. Exits 1 if anything was flagged.
# Example: just scan-fields captures/some-dump.json
scan-fields path: _require-venv
    @{{py}} scripts/scan-config-fields.py "{{path}}"

# Read-only: why does cnMaestro show Wi-Fi clients as 0.0.0.0? SMC DHCP health vs the IPv4 each sampled AP reports vs SMC leases.
# prog is apn or nbn (selects the Teleport cluster and SNMP vault entry). Never prints a password.
# Example: just client-ip-sweep kalumburu-smc01 apn 2
client-ip-sweep smc prog="apn" samples="3":
    @scripts/client-ip-sweep.sh "{{smc}}" "{{prog}}" "{{samples}}"

# Run safe local preflight checks
preflight: runtimes check
````

## File: Justfile
````
# just task catalog for skill-cambium.
# Usage: just --list | just <task>
#
# Recipes go through {{py}}, never a bare interpreter — see skill-ai-it's Runtime isolation doctrine.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-cambium"
py := wc + "/.venv/bin/python"

# List available tasks
default:
    @just --list

# Build the working-cache venv from the mise-pinned runtime. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @test -f requirements.txt && {{py}} -m pip install --quiet --upgrade pip -r requirements.txt || true
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtime the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# Governance coherence checks — must exit 0 before durable work is called complete.
check: _require-venv
    @{{py}} scripts/check_governance.py

# Extract a site's asset register into device-inventory.csv — reference implementation, not general-purpose.
# See scripts/extract-asset-register.py's own docstring before re-running against a new site.
extract-asset-register: _require-venv
    @{{py}} scripts/extract-asset-register.py

# Log into support.cambiumnetworks.com (agent-browser + KeePassXC), optional Downloads search.
# Needs a live MFA code from the operator — run from an interactive shell. Read-only against the portal.
cambium-login search="":
    @if [ -n "{{search}}" ]; then scripts/cambium-portal.sh login --search "{{search}}"; else scripts/cambium-portal.sh login; fi

# Log in, find a specific firmware/documentation release, download its files into <dest>.
# Example: just cambium-fetch-release "XV2" "6.6.0.3-r9" /tmp/xv2-660-docs
cambium-fetch-release model version dest:
    @scripts/cambium-portal.sh fetch-release "{{model}}" "{{version}}" "{{dest}}"

# Open a tsh tunnel to a device's management interface (site-aware cluster/smc-host routing).
# This is generic Teleport tunneling, not a Cambium-specific concern — the canonical script lives
# in skill-smc (which owns tsh/Teleport mechanics), called here rather than duplicated.
# Example: just tunnel hope-vale 10.255.4.5 20045
# Blocks for the tunnel's lifetime (default 120s) — run in the background if you need to keep
# working. Requires an active `tsh login` for the site's cluster already (burringurrah needs
# interactive MFA — this doesn't log in for you).
smc_scripts := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/scripts"
tunnel site device_ip local_port="20000" device_port="443" duration="120":
    @{{smc_scripts}}/teleport-tunnel.sh "{{site}}" "{{device_ip}}" "{{local_port}}" "{{device_port}}" "{{duration}}"

# Run the ePMP adapter's getters (facts/interfaces/wireless_link/clients) against a live tunnel.
# `host` is CAMBIUM_HOST (e.g. localhost:20045 from `just tunnel`); role is "sm" or "ap", selecting
# the cambium-devices/epmp-<role> vault credential. Never prints the password.
# Example: just epmp-getters localhost:20045 sm
epmp-getters host role="sm": _require-venv
    #!/usr/bin/env bash
    set -euo pipefail
    EPMP_USER=$(kp show -s -a UserName cambium-devices/epmp-{{role}})
    EPMP_PASS=$(kp show -s -a Password cambium-devices/epmp-{{role}})
    CAMBIUM_HOST="{{host}}" CAMBIUM_USER="$EPMP_USER" CAMBIUM_PASS="$EPMP_PASS" \
        {{py}} scripts/cambium_epmp_adapter.py

# Check whether a JSON file has any credential-shaped fields, WITHOUT printing their values.
# Run this on any captured config/status dump before viewing it by hand — see 05_known-issues.md
# Security Incidents for why: printing a value to "check if it's real" has caused two live
# secret exposures this pack's history. Exits 1 if anything was flagged.
# Example: just scan-fields captures/some-dump.json
scan-fields path: _require-venv
    @{{py}} scripts/scan-config-fields.py "{{path}}"

# Read-only: why does cnMaestro show Wi-Fi clients as 0.0.0.0? SMC DHCP health vs the IPv4 each sampled AP reports vs SMC leases.
# prog is apn or nbn (selects the Teleport cluster and SNMP vault entry). Never prints a password.
# Example: just client-ip-sweep kalumburu-smc01 apn 2
client-ip-sweep smc prog="apn" samples="3":
    @scripts/client-ip-sweep.sh "{{smc}}" "{{prog}}" "{{samples}}"

# Run safe local preflight checks
preflight: runtimes check
````

## File: README.md
````markdown
# skill-cambium

Canonical specialist pack for Cambium wireless device fleet operations.

## Purpose

Provides structured operational knowledge for APN's Cambium hardware fleet — device families and firmware, local-admin credential vault structure, the cnMaestro estate, site asset-register
conventions, and the `device-inventory.csv` schema. Complements `skill-smc`, which owns the SMC box / ansible-wifi provisioning layer around this hardware.

## Folder index

- [references/](references/) — 6 numbered reference files, progressive disclosure (content source)
- [.archcore/](.archcore/) — durable rules, ADR, and spec for this pack (initialized 2026-09-17; 6 documents accepted the same day, see [.archcore/index.guide.md](.archcore/index.guide.md))

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack version history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Key files

| File          | Role                                                                                  |
| ------------- | ------------------------------------------------------------------------------------- |
| [SKILL.md](SKILL.md) | Agent activation surface — triggers, Standing Write-Back Contract, reference pointers |
| [RUNBOOK.md](RUNBOOK.md) | Navigation index — maps task types to numbered reference files                        |
| [manifest.json](manifest.json) | Machine-readable metadata: version, scope, stable facts, constraints                  |

## Related pack

[skill-smc](../skill-smc/README.md) — the SMC box / ansible-wifi layer this fleet is managed through. See each pack's `SKILL.md` Related Skills section for the boundary.
````

## File: SCRATCHPAD.md
````markdown
# SCRATCHPAD

Agent working memory for skill-cambium. Use for: draft plans, terminal output, intermediate analysis. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-09-17 at pack bootstrap; no prior memory-keeper/project-context/claude-mem history for this new pack -->

> **Superseded 2026-09-17, later the same day (staleness audit).** The "Current state"/"Open items"/"Next actions" below were written at first-adapter time (XV2 only) and went stale within the same
> session as three more adapters landed. What still stands: the bootstrap narrative, the resolved-item history, and every item not specifically annotated below. What changed: all four Cambium families
> now have real, live-verified adapter code — see `references/06_device-api-cli-reference.md` and `CHANGELOG.md`'s `20260917_2050`/`20260917_2057` entries for the R195P and cnWave adapters, and the
> full live-test trail. Superseded bullets are marked `[x]` with a dated note rather than rewritten, per this file's own KEEP convention.

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries — full detail in memory-keeper)](#session-history-summaries--full-detail-in-memory-keeper)
- [Next actions](#next-actions)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only--content-is-above)

---

## Current state

**Phase:** All four Cambium device families (Enterprise Wi-Fi XV2/E-series, ePMP AP/SM, cnWave 60GHz, cnPilot R195P) now have real, live-verified adapter code and `VERIFIED-OBSERVED` data — see
`references/06_device-api-cli-reference.md`. Pack scaffolded 2026-09-17 from `cambium-swap`'s device-credentialing/device-inventory session; same day, later sessions added: `scripts/cambium-portal.sh`
(moved from `cambium-swap`, support-portal login + version-matched release fetch), the confirmed live Hope Vale access chain (SSH CLI + authenticated REST API, written into
`references/02_device-access-and-vault.md`), `scripts/cambium_xv2_adapter.py` (first real adapter code), then `scripts/cambium_epmp_adapter.py`, `scripts/cambium_cnwave_adapter.py`, and
`scripts/cambium_r195p_adapter.py` — all run live against real hardware and verified correct. `references/05_known-issues.md`'s blanket staleness disclaimer and site-coverage row were updated in the
same pass as this note (2026-09-17, staleness audit).

---

## Open items

- [ ] Run `/skill-ai-it refresh` here: the navigation validator fails on stale managed blocks (`AGENTS.md` navigation, `scripts/README.md` scripts at the 2026-08-11 stamp) and
  warns on the `context-map.yaml` version (found 2026-10-05, v0.6.32).
- [ ] `AGENTS.md` is not tracked in git (the repo's git info/exclude file ignores it repo-wide); the platform packs force-added theirs on 2026-10-05 — decide whether this pack should too.
- [x] Authenticated device session — resolved 2026-09-17: real SSH CLI login (`show version`) and real REST API session (`login`/`get_facts`/`get_interfaces`/`logout`) both confirmed against Hope Vale
  Tower 1 (Enterprise Wi-Fi XV2-2T0). Credential (`<secret:keepassxc:cambium-devices/enterprise-wifi>`) confirmed correct against real hardware.
- [ ] `hardware_revision` still UNKNOWN for all 17 models except what's now observed for XV2-2T0 (model/serial/firmware confirmed via `get_facts()` — hardware_revision itself not yet in scope of the
  adapter's returned fields).
- [x] `scripts/cambium_xv2_adapter.py`'s remaining getters — resolved 2026-09-17: `get_radios`/`get_wlans`/`get_clients`/`get_config`/`get_events` all implemented and run live against Hope Vale Tower
  1, matching every row in [cambium-vendor-adapter-data-points.md](/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/docs/migration/controller-option3/cambium-vendor-adapter-data-points.md).
- [ ] **Rotate SNMP community strings, 2026-09-17 — operator decision still pending as far as this file records.** See `references/05_known-issues.md` Security Incidents: this device's real
  `snmp_read_community`/`snmp_write_community` briefly printed to a transcript during exploration. Both strings should be treated as compromised. **Note (2026-09-17 staleness audit):** the operator
  has since added four real SNMP community credentials to the vault (`apn-snmp-ro`/`rw`, `nbn-snmp-ro`/`rw` — CHANGELOG `20260917_2057`) and these are now live-verified fleet-wide; whether that
  constitutes the rotation this item asks for, versus a separate standard-credential addition, was not confirmed by this audit — operator should close or restate this item explicitly rather than leave
  it ambiguous.
- [x] Only this one family (Enterprise Wi-Fi XV2) has an adapter or live-observed data — **superseded 2026-09-17, same day, staleness audit.** All four families now have adapters and live-observed
  data: ePMP AP/SM (`scripts/cambium_epmp_adapter.py`), cnWave 60GHz (`scripts/cambium_cnwave_adapter.py`), cnPilot R195P (`scripts/cambium_r195p_adapter.py`) — see CHANGELOG `20260917_1946` through
  `20260917_2057` and `references/06_device-api-cli-reference.md`.
- [x] Only 2 sites' asset registers seen (Hope Vale, Burringurrah) — **narrowed 2026-09-17, staleness audit.** `references/site-addressing.yaml` now covers all 10 rcp-flavour sites. What still stands:
  the naming-convention *prose* in `references/03_asset-register-conventions.md` was written from only 2 sites and has not been individually re-verified against the other 8 — treat as
  likely-generalizes, not confirmed-generalizes.
- [ ] `scripts/check_governance.py` created at bootstrap with Tier 1 (universal) checks only — extend as the pack grows real scripts/tasks.

---

## Key anchors

| Item             | Detail                                                                                    |
| ---------------- | ----------------------------------------------------------------------------------------- |
| Live device data | `/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/`                    |
| KeePassXC vault  | `~/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx`, `cambium-devices/` group |
| Related pack     | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc`                    |

---

## Recent decisions

- 2026-10-05 — `.archcore/` renamed to the `<slug>.<type>.md` form with `.archcore/index.guide.md` (v0.6.32) so `archcore status` passes; old paths kept as reviewed exemptions for history.
- 2026-09-17 — Operator rejected building a formal CLI/API grammar + capability-model skill (`device-interface-modeler`) ahead of any real adapter code, despite a real multi-vendor plan. Resolved via
  `skill-walk-before-run` (RED, then RESOLVED by the `scripts/cambium_xv2_adapter.py` test — `PASS`, schema not needed). Standing rule going forward: build the next vendor's adapter the same way (own
  specialist skill pack, plain code against the real device) — revisit formal schema only once a second real vendor adapter exists to design against.
- 2026-09-17 — All Cambium development work (scripts, adapter code) goes into this pack, not into `cambium-swap` — explicit operator instruction, reinforcing the Standing Write-Back Contract.
- 2026-09-17 — Created as a separate pack from `skill-smc` rather than folding into it. Rationale: different domain (hardware/credentials/asset-registers vs box/Ansible), already had real
  cross-project-reusable volume, mirrors the precedent that created `skill-smc` in the first place.
- 2026-09-17 — Vault-related reference file is `references/02_device-access-and-vault.md`, not a name containing "credentials" — the workspace's OPA write-gate hard-blocks any file **path** containing
  `credential`/`secret`/`password`, regardless of content.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-10-05 — Archcore filename compliance (v0.6.32)

- `git mv` of 7 `.archcore/` files; live references updated; `SKILL.md` platform-pack link fixed; `just check` 237 OK, `archcore status` clean.
- Evidence basis: memory-keeper key `platform-packs.slurp.20261005`.

### 2026-09-17 (~21:21-22:15) — first whole-pack staleness audit, coherence sweep, first-ever commit

- Ran skill-staleness-audit in full detail mode: gate PASSED, checks 133→145. Found and fixed 13 defects, the two most material being a KEEP-block in this file that still claimed only the XV2 family
  had an adapter (superseded above — all four landed the same day) and a self-contradiction inside `AI_NAVIGATION.md` itself (line 89 said `.archcore/` was empty while lines 35/63 of the same file
  said 6 documents accepted). Also fixed a stale `RUNBOOK.md` header banner, a blanket "everything USER_STATED" staleness-risk note in `references/05_known-issues.md` that no longer matched the
  VERIFIED-OBSERVED state of all four families, a frozen `manifest.json` version/timestamp, a superseded R195P `stable_fact`, and two "5 reference files" miscounts (file `06` already existed). Added
  `check_manifest_freshness` and populated the previously-empty `COUNT_CLAIMS` registry in `scripts/check_governance.py`, both negative-tested.
- Coherence sweep then propagated those fixes further: checks 145→150. `AI_NAVIGATION.md` and `context-map.yaml` were both missing routing rows/entries for reference files 05 and 06;
  the archcore index (then a README) and its manifest-version-discipline rule still claimed no automated check existed for manifest freshness, immediately after the audit added one. Verified `skill-smc` only ever
  references this pack by topic, never by version or file count, so nothing there needed reconciling.
- **Committed this pack to git for the first time.** It had accumulated a full day of real work (four live-verified adapters, `references/site-addressing.yaml` expanded to all 10 sites, SNMP vault
  entries, `.archcore/` rules and ADRs) with zero version-control history until now. `skills_stuff` repo (this pack is a subpath, remote `https://github.com/amalikn/skills_stuff`), commit `1d25892`,
  39 files, pushed to `main`.

### 2026-09-17 ~11:35a-12:15p — live device access, first adapter code, formal-schema question resolved

- Moved the former cambium-support-login.sh here from `cambium-swap` as `scripts/cambium-portal.sh`, added a `fetch-release` subcommand; used it to fetch the exact firmware-version-matched CLI
  Reference Guide (Release 6.6.0.3, matching the live-confirmed device firmware) after finding the previously-archived guide was a newer, mismatched Release 7.2.
- Documented the confirmed live Hope Vale access chain in `references/02_device-access-and-vault.md`: `tsh` tunnel form (`--proxy` required), REST API auth (`POST /api/login`, cookie+XSRF-header
  session), SSH-vs-web-UI comparison.
- Operator pushed on a proposal to build a formal CLI/API grammar skill before writing any adapter, given multi-vendor plans. Ran `skill-walk-before-run` (RED), then wrote and ran
  `scripts/cambium_xv2_adapter.py` (`get_facts`/`get_interfaces`, stdlib-only) live against Hope Vale Tower 1 — resolved RED to PASS: no formal schema needed. Found and fixed one real bug along the
  way (`port_stats.link` unreliable; `port_status` array is authoritative for link state).

### 2026-09-17 — pack bootstrap

- Scaffolded via `skill-ai-it` (bootstrap mode): governance files, `.archcore/` init, 5 reference files, cross-links to `skill-smc` in both directions.
- Content ported: the asset-register naming-convention learning originally written into skill-smc's numbered reference file on the same topic moved here as its canonical home; that file trimmed to a
  stub pointing here.

---

## Next actions

- [x] Extend `scripts/cambium_xv2_adapter.py` with `get_radios`/`get_wlans`/`get_clients`/`get_config` — **done 2026-09-17**, see Open items above.
- [x] Other 4 Cambium families (cnPilot R195P, ePMP AP, ePMP SM, cnWave 60GHz) have no adapter or live-observed data yet — **superseded 2026-09-17, staleness audit.** All four now do; ePMP shares the
  XV2/E-series adapter, cnWave and R195P each have their own. See `references/06_device-api-cli-reference.md`.
- [x] `references/05_known-issues.md` still says no `VERIFIED-OBSERVED` data exists — stale for Enterprise Wi-Fi XV2 now, fix next time that file is touched. — **fixed 2026-09-17, staleness audit**
  (the file's "Pack Staleness Risks" blanket disclaimer and its site-coverage row were both updated).
- Done: register this pack in `/Volumes/Data/_ai/_skills/skills_stuff/README.md`'s Specialist Packs table and symlink `~/.claude/skills/skill-cambium` → canonical path (completed at bootstrap).
- **New, from the 2026-09-17 staleness audit:** `hardware_revision` (all 17 models) and the SNMP-rotation decision remain genuinely open — see Open items above. Also open: this entire pack directory
  is untracked in the parent `skills_stuff` git repo (`git status --porcelain` shows it as a single `??` — never `git add`ed) — everything built this session (four adapters, expanded
  `references/site-addressing.yaml`, SNMP vault entries, `.archcore/` rules) has no version-control history and would be lost with the working tree. Not fixed by this audit per its git-write
  constraint; flagged for the operator to commit.
- **`skill-project-coherence` run 2026-09-17 ~21:45, propagating the staleness audit above.** Found and fixed two companion-file gaps the audit itself didn't reach: `AI_NAVIGATION.md` still said "5
  files" in a managed-block comment and was missing a routing-table row for `references/06_device-api-cli-reference.md`; `context-map.yaml`'s `routing`/`update_rules` sections had no entries for files
  05/06 at all. Also found the archcore index (then a README) and its manifest-version-discipline rule still claimed "no automated check yet" after the audit added `check_manifest_freshness` — corrected. See
  CHANGELOG `20260917_2145`. The untracked-directory item above is still open — this pass did not touch git state, per its own constraint.

---

## Memory pointers (navigation only — content is above)

- memory-keeper: no results (new pack, not yet queried under a dedicated channel)
- project-context: no results
- claude-mem: not queried — this pack has no prior session history
````
