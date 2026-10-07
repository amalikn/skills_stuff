---
name: skill-smc
description: "Ansible-wifi/SMC playbooks, PCAP processing, SMC appliance troubleshooting."
metadata:
  short-description: SMC box operational knowledge and ansible-wifi authoring
---

# SMC: Operations and ansible-wifi Authoring

## Contents

- [Use When](#use-when)
- [Standing Write-Back Contract (applies no matter which project invoked this skill)](#standing-write-back-contract-applies-no-matter-which-project-invoked-this-skill)
- [What This Pack Covers](#what-this-pack-covers)
- [Access in One Paragraph](#access-in-one-paragraph)
- [Diagnosis Decision Tree](#diagnosis-decision-tree)
- [Related Workspaces](#related-workspaces)
- [References](#references)
- [Related Skills](#related-skills)
- [Source](#source)

---

## Use When

Invoke for any of:

- Working on the `ansible-wifi` Ansible repo (roles, templates, inventory, topology vars)
- Working on `/Volumes/Data/_ansible/ansible-malik` SMC operator playbooks, especially URL-capture PCAP fetch/process workflows
- Working on `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` when the change depends on SMC URL-capture PCAP layout, capture cadence, or reporting assumptions
- Writing or reading SMC local knowledge under `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi`
- Troubleshooting a live SMC box (service down, unreachable, wrong config, alert firing)
- Understanding communication flows between SMC boxes and external systems
- Adding a new site, VLAN, service, or feature to the SMC infrastructure
- Interpreting a Prometheus alert for an SMC host
- Determining blast radius of a topology or role change
- Working on a central backend the SMC fleet depends on, even when the task looks like plain AWS/DNS/cert work: Graylog (`gl.aws.apn.au`, its ALB, ACM cert, CAA), Teleport, Prometheus/Grafana. A
  failure there is an SMC fleet incident (example: the 2026-09-12 cert expiry silently stopped all SMC log shipping).

## Standing Write-Back Contract (applies no matter which project invoked this skill)

This skill is the **shared, cross-project source of truth** for SMC/ansible-wifi infrastructure knowledge — not something scoped to whichever project happens to be open. If, while doing SMC-related
work in **any** project, you discover a new fact, fix, access method, root cause, or behavior change relevant to SMC infrastructure or `ansible-wifi` authoring, **write it back to the appropriate
`references/*.md` file in this skill before ending the session** — regardless of whether the calling project's own `AGENTS.md`/`CLAUDE.md` says to. Do not wait for a project-local governance file to
remind you; invoking this skill at all carries that obligation, including the first time a brand-new project ever touches SMC work.

- Pick the right file with `RUNBOOK.md`'s Domain → file routing table (add a row there if a genuinely new domain surfaces — don't force-fit into an existing one).
- Verify the update by **reading the file back** after writing, in the same session. A session-history note, a `SCRATCHPAD.md` claim, or a file timestamp is not proof the content is present — only
  reading the file body counts. (See any consuming project's own `RULE-007`-equivalent for the failure mode this guards against: a project claimed "skill-smc updated" across several sessions while the
  actual content was never added.)
- A project's own `AGENTS.md`/`CLAUDE.md` MAY restate this obligation with project-specific detail (its own routing-table rows, its own verification rule number) — that's reinforcement, not the source
  of the rule. A project that says nothing about skill-smc at all still carries this obligation the moment it invokes this skill.

## What This Pack Covers

SMC boxes and the `ansible-wifi` repo that builds them. An SMC is an x86 PC (`rcp`, `nbn_accelerate`) or an ARM64 Raspberry Pi (`rct`, `wh`, `nbn_wh`) on Ubuntu 22.04, acting as
a site's WiFi hotspot and gateway: DHCP, DNS, captive portal, filtering, monitoring exporters, sometimes VoIP and HA. Seven inventory flavors in two projects (`references/01_overview.md`).

**Overlayroot runs on the Pi and WH boxes only** (operator, 2026-09-22): writes there land in tmpfs and vanish on reboot unless the lower dir is remounted read-write. x86 boxes have a
plain ext4 root. Check before assuming a change persisted (`references/07_hardware-overlay.md`).

It does not own the MikroTik or Cambium devices behind the SMC, or the Nautobot/OpenWISP platforms: see Related Skills.

## Access in One Paragraph

Everything goes through Teleport: `tsh ssh root@<host>` after the operator has logged in, and Ansible's `ansible_host` is `{{inventory_hostname}}.teleport.<project>.au`, split by
project (APN, nbn_accelerate), not flavor. Every box also holds a raw `autossh` reverse tunnel to its project bastion on port `50000 + site_eclipse_siteid`, independent of the Teleport
agent. **Never report a box as unreachable until that backdoor has been checked** (operator, 2026-10-07): `scripts/backdoor-watch.sh <site>`. Details:
`references/03_communication-flows.md` §All Inbound Access and §Backdoor SSH Access.

## Diagnosis Decision Tree

1. **Box unreachable?** Backdoor first (above), then classify the outage with `scripts/fleet-reboot-timeline.py`: reboot, dark-then-boot (power or a power-cycled hang), or WAN-only.
   `references/05_troubleshooting.md` Tier 1; solar-site power loss and Pi undervoltage in `references/06_failure-modes.md`.
2. **Alert firing?** `references/06_failure-modes.md` §Key Prometheus Alerts gives trigger and first check for each. There is no per-device `role="internet"` loss alert
   (`references/13_known-issues.md`).
3. **Service down, or DHCP/DNS/WiFi/VoIP/HA misbehaving?** `references/05_troubleshooting.md` Tiers 2–6. DNS differs by host: Unbound + Stubby on most boxes, BIND on the `smc_ltp`
   low-touch sites, and the box's own resolution bypasses both.
4. **Metrics missing?** Tier 7: textfile collectors have staleness windows (`references/02_service-map.md`), and federation rides its own autossh tunnel.
5. **Changing Ansible?** `references/08_ansible-authoring.md` first: edit `topology_vars/<site>.yml`, never the hidden `.<site>.yml` cache; a `group_vars` or plugin change reaches all
   flavors; one inventory per run (`-i A -i B` loses B's topology vars); validate with yamllint, ansible-lint, ansible-inventory, then `--syntax-check`.

## Related Workspaces

Treat these paths as part of the SMC working surface:

| Path                                                            | Relationship to SMC work                                                                                                           |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `/Volumes/Data/_ansible/ansible-wifi`                           | Production Ansible repo: roles, inventory, topology, SMC service deployment                                                        |
| `/Volumes/Data/_ansible/ansible-malik`                          | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` URL-capture fetch/process                                    |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query`     | DNS reporting pipeline consuming SMC URL-capture PCAP output                                                                       |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi`   | Local-only plans, reports, OPA artifacts, and SMC investigation knowledge for `ansible-wifi`                                       |
| `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller`        | FOSS network controller build (Nautobot + adapter layer) intended to eventually replace/complement `smc_cnmaestro_provisioning`'s  |
|                                             |   role — call `skill-cambium` first for device-layer questions, this pack for SMC/Ansible-layer questions                          |

When behavior, layout, or troubleshooting assumptions change in one of these surfaces, update the corresponding references in the others during the same session where practical.

**project-coherence scope**: When running `project-coherence` on `ansible-wifi`, `RUNBOOK.md` and the focused files under `references/` are external governed artifacts and must be included in the
coherence Tier 3 pass — check that they reflect any new findings, fixes, or architecture decisions from the session.

## References

- `RUNBOOK.md` — navigation index and reference-routing table.
- `references/01_overview.md` — SMC definition, inventory flavors, remote access, satellite constraints, APN vs NBN Accelerate cluster differences.
- `references/02_service-map.md` — service names, units, config paths, monitoring collectors, RCT/x86 differences.
- `references/03_communication-flows.md` — inbound/outbound communication paths.
- `references/04_dependency-tree.md` — dependencies between network, DNS, portal, monitoring, and access systems.
- `references/05_troubleshooting.md` — live incident triage, alerts, DHCP/DNS/WiFi/VoIP/HA issues.
- `references/06_failure-modes.md` — known failure signatures, root causes, and fix patterns.
- `references/07_hardware-overlay.md` — hardware differences, overlayroot, persistence, disk-write risk.
- `references/08_ansible-authoring.md` — topology vars, cache coherence, validation, generator drift.
- `references/09_url-capture-pcap.md` — URL capture v2, PCAP layout, fetch/process workflows, dns_query assumptions.
- `references/10_captive-portal.md` — captive portal, Eclipse config sync, Kohana issues, portal PHP (mod_php as www-data — NOT PHP-FPM).
- `references/11_vagrant-lab.md` — local Vagrant lab bring-up and virtualization issues.
- `references/12_content-filtering.md` — family-friendly VLAN 501 filtering, MAC randomization, CAKE.
- `references/13_known-issues.md` — coverage gaps, live-validation limits, and staleness risks.
- `references/14_pin-activation-diagnosis.md` — pin validity (mangle) vs pin issuance (Apache access log): two independent mechanisms, marks-≠-activations pitfalls, and the 2026-09-11 fleet case
  study.
- `references/snmp-oid-registry.yaml` — verified SNMP OIDs on the SMC box itself (net-snmp agent; canary 2026-09-24), the list `unified-network-controller/wc-local/scripts/collector/smc_collect.py`
  reads.
- `references/snmp-oid-registry-tplink.yaml` — verified SNMP OIDs on the TP-Link site switches (SG2428P, 2026-09-30), kept like skill-cambium's registry: each with the controller's use for it, plus
  the MIBs checked and absent. `references/tplink-site-switches.yaml` holds one record per switch (identity, address, VLANs, port descriptions, SNMP state, evidence) and
  `references/tplink-snmp-enablement-survey-20260930.csv` the SNMP survey, as skill-cambium keeps them.
- `references/15_cambium-asset-registers.md` — pointer only: the ansible-wifi `site_name` join point for a Cambium asset register. Full asset-register naming-convention/extraction knowledge now lives
  in `skill-cambium` — see Related Skills below.
- `references/16_tplink-site-switches.md` — TP-Link site switches behind the SMC: KeePass entry, SSH quirks, enable scenarios, discovery, redacted config capture, the `SNMP-<location>` read-write
  community, and how unified-network-controller seeds them in Nautobot; driven by `scripts/tplink-switch.sh`.
- `scripts/` — read-only diagnostics (backdoor check, outage classification, fleet health, WAN-routing drift, pin activation, Prometheus/Graylog query helpers) and the
  ansible-lint pre-push gate; catalogued with safety labels in `scripts/README.md`. Run them through the pack-root `justfile` (`just --list`).

## Related Skills

- **`skill-mikrotik`** — the MikroTik devices behind the SMC (on `rct`: RB450Gx4 switch at `10.255.0.5`, Metal 52 ac AP at `10.255.0.20`). Call it when a site
  outage might be the switch or the SMC-to-switch cable, or to read switch uptime, voltage, link-downs and logs. The SMC side of the trunk, the TSTIK app
  that power-cycles the switch, and Teleport stay here; write a fact spanning both to both packs.
- **`skill-cambium`** — the Cambium device/hardware layer this fleet's boxes provision and manage: device families/firmware, local-admin credential vault, cnMaestro estate, asset-register conventions,
  device-inventory schema. Call it for anything about the radios/APs themselves rather than the SMC box or Ansible. It calls back here for: SMC service troubleshooting, Ansible topology/role
  questions, `smc_cnmaestro_provisioning` behaviour, Teleport access. Neither pack duplicates the other's content — cross-reference, don't copy.
- **`skill-nautobot`** and **`skill-openwisp`** (canonical under `../../platform/`) — the platform layer this fleet's inventory and monitoring run on. Call them for Nautobot models, APIs, Jobs and
  onboarding mechanics, or OpenWISP registration, metrics, workers and storage. A SMC box or Ansible fact stays here; a fact true of any Nautobot or OpenWISP deployment goes to them as a dated Learned
  entry.

## Source

- specialist_type: project
- slug: skill-smc
- version: see `manifest.json` in the canonical source (not duplicated here — see `manifest-version-discipline.rule.md`)
