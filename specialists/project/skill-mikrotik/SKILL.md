---
name: skill-mikrotik
description: "MikroTik site switches and APs behind SMC boxes (RB450Gx4, Metal 52 ac): read-only RouterOS access through Teleport, port/VLAN layout, link and power diagnosis, fleet surveys."
metadata:
  short-description: MikroTik site switch and AP operations behind SMCs
---

# MikroTik: Site Switch and AP Operations

## Contents

- [Use When](#use-when)
- [Standing Write-Back Contract (applies no matter which project invoked this skill)](#standing-write-back-contract-applies-no-matter-which-project-invoked-this-skill)
- [What This Pack Covers](#what-this-pack-covers)
- [Access in One Paragraph](#access-in-one-paragraph)
- [Diagnosis Decision Tree](#diagnosis-decision-tree)
- [Related Workspaces](#related-workspaces)
- [Related Skills](#related-skills)
- [References](#references)
- [Source](#source)

## Use When

- Any work touching a MikroTik device at an SMC site: the RB450Gx4 site switch (`10.255.0.5`) or the Metal 52 ac AP (`10.255.0.20`) on `rct` sites, and any other RouterOS device found behind an SMC
- An SMC goes dark and the question is cable, switch, power or WAN: run the decision tree below before blaming the satellite or the SMC
- Reading switch uptime, supply voltage, port link-downs, the RouterOS log, bridge/VLAN layout or config for a site or the fleet
- Interpreting TSTIK "Resetting Switch" events on `rct` (the SMC's TSTIK app power-cycles this switch)
- Planning any RouterOS change: this pack is read-only by default; a change needs the operator's go-ahead and the depth-before-breadth canary rule

## Standing Write-Back Contract (applies no matter which project invoked this skill)

This skill is the **shared, cross-project source of truth** for MikroTik device knowledge in the SMC fleet. If, while doing MikroTik-related work in **any** project, you discover a new fact, fix,
access method, root cause, port layout, firmware detail or behaviour change, **write it back to the matching `references/*.md` file before ending the session**, whether or not the calling project's
own `AGENTS.md`/`CLAUDE.md` says so. Invoking this skill carries that obligation.

- Pick the file with `RUNBOOK.md`'s Reference Routing table; add a row there when a genuinely new domain appears.
- Reusable scripts written during the work go into `scripts/` in the same session, unprompted: generic inputs, a safety row and usage in `scripts/README.md`, a `justfile` recipe, a smoke test from the
  new path, a `CHANGELOG.md` entry.
- Every write-back bumps `manifest.json` `version` and `updated_at` and adds a `CHANGELOG.md` entry; run `just check` (`scripts/check_governance.py`) before reporting.
- Verify by **reading the file back**. A changelog line or a timestamp is not proof the content is there.
- Label load-bearing claims `VERIFIED-OBSERVED` (seen on a device, with date and site), `VERIFIED-DOC` (vendor documentation, with version) or `UNVERIFIED`.
- **Boundaries:** SMC box, Ansible, Teleport and TSTIK-app facts go to `skill-smc`; Cambium radios and APs go to `skill-cambium`. A fact that spans packs (for example the RCT trunk layout, which is
  both the SMC's eth0 and this switch's ether1) is written to every pack it touches, cross-referenced, not copied wholesale.
- **Never write a password or any secret value into this pack.** Reference it as `<secret:keepassxc:Network/mikrotik switch & metal ap>`.

## What This Pack Covers

The MikroTik devices that sit between an SMC and the rest of a site: on `rct` sites an RB450Gx4 used as the site switch and a Metal 52 ac outdoor AP, both on RouterOS 7.8 at the sites surveyed. Their
port and VLAN layout, how to reach them without exposing the password, how to read their health and history, and the failure signatures seen so far. Seeded 2026-10-07 from the arrkapa outage
investigation and a read-only `rct` fleet survey.

It does not own the SMC, Ansible, the TSTIK app, or Cambium devices: see Related Skills.

## Access in One Paragraph

The devices are only reachable from the SMC's management VLAN. `scripts/mikrotik_exec.sh <smc> <ip> '<cmd>'` opens a Teleport port-forward through the SMC (`tsh ssh -N -L`) and runs the SSH client
locally with `sshpass -e`, so the password never appears in a command that runs on the SMC: Teleport audits exec commands and the SMC ships that audit log to Graylog. The script refuses anything but
`print`/`export`/`monitor … once`/`get` unless `MT_ALLOW_WRITE=1`. Details: `references/02_device-access.md`.

## Diagnosis Decision Tree

1. **Is the SMC up but dark?** In skill-smc, `fleet-reboot-timeline.py` (boot time unchanged = box up) and `vlan-traffic-timeline.py --gap` (what crossed each VLAN). Only the WAN VLAN silent =
   WAN/satellite. Every VLAN on the trunk silent = this switch or the SMC-to-switch cable.
2. **Switch uptime vs SMC uptime** (`scripts/mikrotik_fleet_survey.sh` or `/system resource print`): a much younger switch was power-cycled, on `rct` usually by the TSTIK app after ~11 minutes of failed
   switch/AP pings.
3. **Port link-downs and the log** (`/interface print detail` `link-downs=`, `/log print where topics~"interface"`): rising link-downs on ether1 = SMC side (Pi NIC, cable, SMC reboots); on ether2 =
   Sky Muster NTD side.
4. **Supply voltage and temperature** (`/system health print`): the DC bus the board is fed from; compare with the fleet range in `references/01_overview.md`.
5. **Capture before any power-cycle**: the RouterOS log is a 1,000-line buffer; arrkapa's survived crash reboots, but do not count on it across a power-cycle (`references/05_known-issues.md` #4). `scripts/mikrotik_site_capture.sh` (add `WAIT_UP=1` for a box that is offline now).

## Related Workspaces

| Path                                                                       | Relationship                                                                      |
| -------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `/Volumes/Data/_ansible/ansible-wifi`                                      | SMC inventory: site names, the SMC side of the trunk (`topology_vars/<site>.yml`) |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/issues`       | Investigation folders and raw captures (for example `rct-fleet/arrkapa-wan/`)     |
| `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc`     | SMC box, Teleport, Prometheus/Graylog tooling, TSTIK app                          |
| `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-cambium` | Cambium devices at the same sites                                                 |

## Related Skills

- **`skill-smc`** — the SMC box, ansible-wifi, Teleport access, Prometheus/Graylog scripts, and the `rct` TSTIK app that power-cycles this switch. It calls back here for anything about the switch or
  AP itself.
- **`skill-cambium`** — Cambium radios and APs. MikroTik-vs-Cambium boundary: the device vendor decides the pack.

## References

- `RUNBOOK.md` — navigation index and reference-routing table.
- `references/01_overview.md` — models, RouterOS versions, port and VLAN layout, fleet ranges for uptime, voltage and temperature.
- `references/02_device-access.md` — KeePass entry, Teleport port-forward method, why nothing secret runs on the SMC, read-only guard.
- `references/03_routeros-cli-reference.md` — the read-only commands this pack uses, what each field means, RouterOS 7 gotchas.
- `references/04_failure-modes.md` — signatures seen in the fleet and how they were confirmed.
- `references/05_known-issues.md` — gaps, unverified assumptions, staleness risks.
- `references/06_provisioning.md` — the Pi provisioning script: firmware, the two SSH command batches, what they set, and the cloned MACs they cause.
- `references/07_equipment-and-snmp.md` — vendor specs for both models, SNMP state and MIBs, firmware status, vendor sources in `references/vendor-sources-20261007_1640/`.
- `references/snmp-oid-registry.yaml` — per-model OIDs (candidates until SNMP is enabled and verified) and equipment facts, the list tools read.
- `scripts/README.md` — script catalogue with safety classification.

## Source
- specialist_type: project
- slug: skill-mikrotik
- version: see `manifest.json` (not duplicated here)
