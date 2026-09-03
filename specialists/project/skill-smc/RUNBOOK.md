# SMC Box Operational Runbook

**Version:** 0.1.24
**Validated against:** malik-rct01 (RCT flavor, ARM64, Ubuntu 22.04, overlayroot enabled)
**Scope:** x86 and ARM64 SMC appliances managed by `ansible-wifi`

This file is the navigation index for the `skill-smc` specialist pack. Load only the focused
reference needed for the task instead of reading every SMC detail up front.

## SMC-Related Workspaces

| Path | Relationship |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible source for SMC roles, inventories, topology, and URL-capture deployment |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` fetch/process workflows |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting and workbook pipeline consuming SMC URL-capture PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans, reports, OPA artifacts, and investigation knowledge for `ansible-wifi` |

Reference hygiene: when a URL-capture or PCAP-layout change affects more than one workspace,
update the relevant focused reference plus the relevant repo governance files in the same session
where practical.

## Reference Routing

| Task | Read |
|---|---|
| Basic SMC definition, inventory flavors, remote access, satellite constraints, APN vs NBN Accelerate cluster differences | `references/01_overview.md` |
| Service names, config paths, monitoring collectors, RCT vs x86 service map | `references/02_service-map.md` |
| External communication paths and inbound/outbound flows | `references/03_communication-flows.md` |
| Dependency relationships between network, DNS, portal, monitoring, and access systems | `references/04_dependency-tree.md` |
| Live incident triage, alerts, service failures, DHCP/DNS/WiFi/VoIP/HA issues | `references/05_troubleshooting.md` |
| Known failure signatures and fix patterns | `references/06_failure-modes.md` |
| Hardware differences, overlayroot, disk write behavior, persistence risk | `references/07_hardware-overlay.md` |
| Overlayroot copy_up cost model, `recurse=0` escape hatch, log capping (`smc_rise_logcaps`) | `references/07_hardware-overlay.md` §8 |
| Box reboot-looping every few minutes (overlay RAM exhaustion) | `references/05_troubleshooting.md` Tier 8b |
| Ansible topology vars, cache coherence, validation commands, generator drift, smc_ltp sub-group, "low touch" onboarding history | `references/08_ansible-authoring.md` |
| Code notes: RULE-006 comment/note split, note provenance (context, branch, commit), what survives a branch switch, `check_note_anchors.py` | `references/08_ansible-authoring.md` §Code notes |
| URL capture v2, PCAP layout, fetch/process workflows, dns_query assumptions | `references/09_url-capture-pcap.md` |
| Captive portal, Eclipse config sync, Kohana issues, portal PHP (mod_php, not PHP-FPM) | `references/10_captive-portal.md` |
| Local Vagrant lab bring-up and known virtualization issues | `references/11_vagrant-lab.md` |
| Family-friendly VLAN 501 access, filtering stack, MAC randomization, CAKE | `references/12_content-filtering.md` |
| Coverage gaps, live-validation limits, stale assumptions | `references/13_known-issues.md` |
| Reusable read-only scripts: WAN-routing/topology-drift investigation tooling (evidence capture, drift analyser, topology/hardware cross-check), plus ansible-lint pre-push/CI gate scripts | `scripts/README.md` |

## Runtime Paths

- ansible-wifi venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- ephemeral logs, pid files, and sockets: `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`

Prefer the working-cache venvs when running SMC validation tooling (`ansible-lint`, `yamllint`,
`ansible-inventory`, `ansible-playbook`) to keep versions stable across sessions.
