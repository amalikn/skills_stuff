---
name: skill-smc
description: Use when working on ansible-wifi, ansible-malik SMC playbooks, dns_query PCAP processing, local SMC knowledge artifacts, or live SMC appliance issues. Covers Ansible authoring, URL capture/PCAP workflows, service architecture, communication flows, and troubleshooting.
metadata:
  short-description: SMC box operational knowledge and ansible-wifi authoring
---

# SMC: Operations and ansible-wifi Authoring

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

## What an SMC Box Is
An SMC box is an **x86 PC** or **ARM64 Raspberry Pi** running **Ubuntu 20.04+ (22.04 in production)**, deployed as a managed WiFi hotspot and network gateway. All remote access routes through **Teleport** via a persistent `autossh` reverse SSH tunnel. SSH port on Teleport server = `50000 + site_eclipse_siteid`. Ansible connects via `ansible_host = {{inventory_hostname}}.teleport.<flavor>.au`.

**Critical — Overlayroot:** All SMC boxes run overlayroot. Writes go to tmpfs (`/media/root-rw/overlay`) and are **lost on reboot**. Ansible changes only persist if the lower dir (`/media/root-ro`) is remounted read-write first. Always check overlayroot status before assuming a change persisted.

## Related Workspaces

Treat these paths as part of the SMC working surface:

| Path | Relationship to SMC work |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Production Ansible repo: roles, inventory, topology, SMC service deployment |
| `/Volumes/Data/_ansible/ansible-malik` | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` URL-capture fetch/process |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS reporting pipeline consuming SMC URL-capture PCAP output |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only plans, reports, OPA artifacts, and SMC investigation knowledge for `ansible-wifi` |

When behavior, layout, or troubleshooting assumptions change in one of these surfaces, update the
corresponding references in the others during the same session where practical.

---

## Troubleshooting Decision Tree

### Tier 1: Box Unreachable
| Check | Command | What to look for |
|---|---|---|
| autossh tunnel | `systemctl status autossh-teleport-openssh` | Active/failed; check last restart time |
| Network route | Prometheus: `NodeNetworkDefaultRouteInstability` | 4+ route changes in 60min |
| Overlayroot | `mount \| grep overlay` | Lower dir must be mounted |
| Teleport node | `systemctl status teleport` | Failed = no new sessions possible |

### Tier 2: Service Down (systemd failed)
1. `journalctl -u <service> --since "1h ago"` — what caused the failure
2. `systemctl list-units --state=failed` — other failed units
3. Check disk: `HostOutOfDiskSpace` (< 10%) / `HostOutOfInodes`
4. Config error? Check last Ansible playbook run output

### Tier 3: DHCP / DNS Not Serving Clients
- DHCP: `dhcpd -t -cf /etc/dhcp/dhcpd.conf` (config test); `grep -i error /var/log/syslog`
- DNS (RCT / rct flavor — Unbound + Stubby): `unbound-checkconf`; `unbound-control status`; `systemctl status stubby`; config at `/etc/unbound/`, DoT upstream config at `/etc/stubby/stubby.yml`
- DNS (other flavors — BIND/named): `named-checkconf`; `rndc status`; verify zones loaded in `/etc/bind/`

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

| Alert | Trigger | First check |
|---|---|---|
| `HostOutOfDiskSpace` | < 10% free | `/var/log`, overlayroot upper dir fills |
| `HostOutOfInodes` | < 10% inodes | small file accumulation in `/tmp`, logs |
| `HostDiskWillFillIn24Hours` | predict_linear | find write rate source |
| `HostSystemdServiceCrashed` | unit state = failed | `journalctl -u <unit>` |
| `HostClockSkew` | offset > ±0.05s | `chronyc tracking` |
| `HostConntrackLimit` | > 80% conntrack | `ss -s`; check for connection leak |
| `NodeNetworkDefaultRouteInstability` | 4+ route changes/60min | VRRP flap, overlay issue |
| `NodeStarlinkInterfacecheckPacketLoss` | 100% loss 60min | starlink interface down |
| `sbdm_device_health_status == 0` | Samsung SSD degraded | SSD replacement needed |
| `smartmon_device_smart_healthy == 0` | SMART failure | drive health critical |

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
- `autossh` → `teleport.<flavor>.au` (persistent reverse tunnel)
- Prometheus federation → central Prometheus (via dedicated federation tunnel)
- `cnmaestro-provisioning` → CNMaestro WiFi Dashboard API
- `rsyslog` → Graylog (UDP syslog)
- `speedtest_exporter` → Ookla servers
- NBN Accelerate API (broadband management)

**Alerts:** Prometheus alertmanager → Teams (NOC webhook + dev webhook)

---

## Runtime Environments
- ansible-wifi tooling venv: `/Volumes/Data/_ai/_skills/skills-runtime/ansible-wifi/.venv`
- skill-smc specialist venv: `/Volumes/Data/_ai/_skills/skills-runtime/skill-smc/.venv`
- Prefer these environments when running SMC validation tooling (`ansible-lint`, `yamllint`, `ansible-inventory`, `ansible-playbook`) to keep versions stable across sessions.

## References
- `references/RUNBOOK.md` — full service map (30+ services), comms flows, dependency tree, failure modes, hardware differences, overlayroot detail, full Ansible workflows
- `references/PROFILE.md` — SMC box definition, inventory flavors, Teleport access pattern, overlayroot structure

## Source
- specialist_type: project
- slug: skill-smc
- version: 0.1.0
