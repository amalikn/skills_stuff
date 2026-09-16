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
- [What an SMC Box Is](#what-an-smc-box-is)
- [Related Workspaces](#related-workspaces)
- [Troubleshooting Decision Tree](#troubleshooting-decision-tree)
- [Key Prometheus Alerts Reference](#key-prometheus-alerts-reference)
- [Ansible Authoring: Key Rules](#ansible-authoring-key-rules)
- [Communication Flows (Quick Reference)](#communication-flows-quick-reference)
- [Runtime Environments](#runtime-environments)
- [References](#references)
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

## What an SMC Box Is
An SMC box is an **x86 PC** or **ARM64 Raspberry Pi** running **Ubuntu 20.04+ (22.04 in production)**, deployed as a managed WiFi hotspot and network gateway. All remote access routes through
**Teleport** via a persistent `autossh` reverse SSH tunnel. SSH port on Teleport server = `50000 + site_eclipse_siteid`. Ansible connects via `ansible_host =
{{inventory_hostname}}.teleport.<project>.au` — the domain splits by **project** (APN, nbn_accelerate), not by flavor; each project has multiple flavors nested under it (see `01_overview.md` "Remote
Access").

**Critical — Overlayroot:** All SMC boxes run overlayroot. Writes go to tmpfs (`/media/root-rw/overlay`) and are **lost on reboot**. Ansible changes only persist if the lower dir (`/media/root-ro`) is
remounted read-write first. Always check overlayroot status before assuming a change persisted.

## Related Workspaces

Treat these paths as part of the SMC working surface:

| Path                                                          | Relationship to SMC work                                                                        |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `/Volumes/Data/_ansible/ansible-wifi`                         | Production Ansible repo: roles, inventory, topology, SMC service deployment                     |
| `/Volumes/Data/_ansible/ansible-malik`                        | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` URL-capture fetch/process |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query`   | DNS reporting pipeline consuming SMC URL-capture PCAP output                                    |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only plans, reports, OPA artifacts, and SMC investigation knowledge for `ansible-wifi`    |

When behavior, layout, or troubleshooting assumptions change in one of these surfaces, update the corresponding references in the others during the same session where practical.

**project-coherence scope**: When running `project-coherence` on `ansible-wifi`, `RUNBOOK.md` and the focused files under `references/` are external governed artifacts and must be included in the
coherence Tier 3 pass — check that they reflect any new findings, fixes, or architecture decisions from the session.

---

## Troubleshooting Decision Tree

### Tier 1: Box Unreachable
| Check          | Command                                          | What to look for                       |
| -------------- | ------------------------------------------------ | -------------------------------------- |
| autossh tunnel | `systemctl status autossh-teleport-openssh`      | Active/failed; check last restart time |
| Network route  | Prometheus: `NodeNetworkDefaultRouteInstability` | 4+ route changes in 60min              |
| Overlayroot    | `mount \| grep overlay`                          | Lower dir must be mounted              |
| Teleport node  | `systemctl status teleport`                      | Failed = no new sessions possible      |

### Tier 2: Service Down (systemd failed)
1. `journalctl -u <service> --since "1h ago"` — what caused the failure
2. `systemctl list-units --state=failed` — other failed units
3. Check disk: `HostOutOfDiskSpace` (< 10%) / `HostOutOfInodes`
4. Config error? Check last Ansible playbook run output

### Tier 3: DHCP / DNS Not Serving Clients
- DHCP: `dhcpd -t -cf /etc/dhcp/dhcpd.conf` (config test); `grep -i error /var/log/syslog`
- DNS, non-`smc_ltp` hosts (all flavors — Unbound + Stubby, client path only): `unbound-checkconf`; `unbound-control status`; `systemctl status stubby`; config at `/etc/unbound/`, DoT upstream config
  at `/etc/stubby/stubby.yml` (Stubby listens on `127.0.0.1@60053`, single upstream `127.0.0.1@60853` via autossh local forward, no failover)
- DNS, `smc_ltp` hosts only (static `rcp` group, 7 sites — `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona` — all "low touch"-onboarded sites; also runs
  CNMaestro Cambium backhaul provisioning, see `references/08_ansible-authoring.md`): `named-checkconf`; `rndc status`; verify zones loaded in `/etc/bind/`
- DNS, host's own resolution (separate from the two rows above — see `references/02_service-map.md`): `resolvectl status`; `systemctl status systemd-resolved`; `DNSStubListener=no` by default means
  the box's own `getaddrinfo()` bypasses Unbound/Stubby/BIND entirely

### Tier 4: WiFi AP Issues
- hostapd: `journalctl -u hostapd --since "1h ago"`
- CNMaestro provisioning: `systemctl status cnmaestro-provisioning`; check Redis: `redis-cli ping`; daemon log at `/var/log/cnmaestro-provisioning/`

### Tier 5: VoIP / Asterisk Issues
- `asterisk -rvvv` — Asterisk CLI
- Check generated extension config: `/etc/asterisk/extensions.conf`
- `asterisk -rx "dialplan show"` — verify dialplan loaded

### Tier 6: HA / Failover Issues
- VIP assignment: `ip addr show` — VIP should be on active node
- VRRP state: `journalctl -u keepalived --since "1h ago"`
- Conntrack limit: `cat /proc/sys/net/netfilter/nf_conntrack_count` vs `nf_conntrack_max`

### Tier 7: Monitoring Gaps
- Textfile collectors must update within their staleness window:
  - `sbdm.py` → `/var/lib/node_exporter/textfile_collector/sbdm.prom` — max 5400s (90min)
  - `smartmon.py` → `smartmon.prom` — max 5400s
  - `interfacecheckv2.sh` → `my_node_interfacecheck_success.prom` — max 450s
  - `apt_info.py` → `apt_info.prom` — max 450s
- Prometheus federation: check `autossh-prometheus-federation` tunnel service

---

## Key Prometheus Alerts Reference

| Alert                                  | Trigger                | First check                             |
| -------------------------------------- | ---------------------- | --------------------------------------- |
| `HostOutOfDiskSpace`                   | < 10% free             | `/var/log`, overlayroot upper dir fills |
| `HostOutOfInodes`                      | < 10% inodes           | small file accumulation in `/tmp`, logs |
| `HostDiskWillFillIn24Hours`            | predict_linear         | find write rate source                  |
| `HostSystemdServiceCrashed`            | unit state = failed    | `journalctl -u <unit>`                  |
| `HostClockSkew`                        | offset > ±0.05s        | `chronyc tracking`                      |
| `HostConntrackLimit`                   | > 80% conntrack        | `ss -s`; check for connection leak      |
| `NodeNetworkDefaultRouteInstability`   | 4+ route changes/60min | VRRP flap, overlay issue                |
| `NodeStarlinkInterfacecheckPacketLoss` | 100% loss 60min        | starlink interface down                 |
| `sbdm_device_health_status == 0`       | Samsung SSD degraded   | SSD replacement needed                  |
| `smartmon_device_smart_healthy == 0`   | SMART failure          | drive health critical                   |

**This table is not complete coverage — known gap:** there is no per-device `role="internet"` equivalent of `NodeStarlinkInterfacecheckPacketLoss`. A single dead internet-role link can run undetected
indefinitely even though `interfacecheckv2.sh` is faithfully reporting it. See `references/13_known-issues.md` "No per-device `role: internet` Prometheus alert exists".

---

## Ansible Authoring: Key Rules

1. **Canonical source** = `inventories/*/topology_vars/<site>.yml`. Hidden `.*.yml` files are generated cache — never edit them directly.
2. **Cross-flavor impact**: group_vars or plugin change → all 7 flavors affected. Single topology_vars file → one flavor only.
3. **Validation order**: `yamllint` → `ansible-lint` → `ansible-inventory --list` → `ansible-inventory --host <site>` → `ansible-playbook --syntax-check`.
4. **Cache coherence**: delete `inventories/*/topology_vars/.<site>.yml` to force plugin regeneration (git checkout changes mtimes, making stale cache appear current).
5. **Generator drift**: when changing a topology pattern, check `roles/smc_generate_smc_files` templates — future site generation must stay consistent with current site changes.
6. **Overlayroot impact on Ansible**: changes deployed via `smc_bases.yml` only persist if the playbook remounts the lower dir rw. Verify with `mount | grep overlay` on the target.

---

## Communication Flows (Quick Reference)

**All inbound access** → Teleport proxy → autossh reverse tunnel → port 22 (SSH)

**Outbound from SMC:**
- `autossh` → `teleport.<project>.au` (persistent reverse tunnel)
- Prometheus federation → central Prometheus (via dedicated federation tunnel)
- `cnmaestro-provisioning` → CNMaestro WiFi Dashboard API
- `rsyslog` → Graylog (UDP syslog)
- `speedtest_exporter` → Ookla servers
- NBN Accelerate API (broadband management)

**Alerts:** Prometheus alertmanager → Teams (NOC webhook + dev webhook)

---

## Runtime Environments
- ansible-wifi tooling venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc specialist venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- Ephemeral logs, pid files, and sockets belong under `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`.
- Prefer the working-cache venvs when running SMC validation tooling (`ansible-lint`, `yamllint`, `ansible-inventory`, `ansible-playbook`) to keep versions stable across sessions.

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
- `scripts/` — reusable read-only diagnostic tooling for WAN-routing/topology-drift investigations (evidence capture, the "hook covers netplan" drift analyser, and a topology_vars-vs-live-hardware
  cross-check), fleet hardware/service-health + portal-FQDN-status audit, captive-portal pin-activation diagnosis, plus generic ansible-lint pre-push/CI gate scripts (baseline refresh + delta gate);
  see `scripts/README.md`.

## Source
- specialist_type: project
- slug: skill-smc
- version: see `manifest.json` in the canonical source (not duplicated here — see `rule-manifest-version-discipline.md`)
