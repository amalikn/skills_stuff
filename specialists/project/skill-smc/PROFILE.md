# PROFILE

## Subject
- Type: project
- Name: smc
- Slug: skill-smc

## What an SMC Box Is
An SMC (Site Management Controller) box is a managed Linux appliance deployed as a WiFi hotspot and network gateway. Hardware is either an **x86 PC** or an **ARM64 Raspberry Pi** (aarch64), running **Ubuntu 20.04+ (22.04 seen in production)**. All remote management access goes through **Teleport** via a persistent autossh reverse SSH tunnel. The port used on the Teleport server is `50000 + site_eclipse_siteid`.

## Inventory Flavors
The `ansible-wifi` repo manages 7 flavors:

| Flavor | Description |
|---|---|
| apn | APN network hotspots |
| cw | Community WiFi |
| rcp | RCP network |
| rct | RCT (Raspberry Pi-based) |
| wh | WH network |
| nbn_accelerate | NBN Accelerate broadband |
| nbn_wh | NBN WH |

## Related Workspaces

| Path | Role |
|---|---|
| `/Volumes/Data/_ansible/ansible-wifi` | Canonical SMC Ansible source: roles, inventory, topology, service deployment |
| `/Volumes/Data/_ansible/ansible-malik` | Operator SMC playbooks, including URL-capture PCAP fetch/process |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query` | DNS query processing and reporting for SMC URL-capture PCAPs |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans, reports, OPA artifacts, and investigation notes |

## Overlayroot
All SMC boxes run with overlayroot enabled:
- Lower dir (real filesystem, read-only at runtime): `/media/root-ro`
- Upper dir (tmpfs, volatile): `/media/root-rw/overlay`
- Workdir: `/media/root-rw/overlay-workdir/_`
- Mount: `overlay / overlay rw,relatime,lowerdir=/media/root-ro,...`
- **Consequence**: file writes at runtime go to RAM and are lost on reboot. Ansible changes only persist if the lower dir is remounted rw before changes are made.

## Stable Facts
- Root AGENTS.md thin wrapper over .agents/ docs.
- Ansible connects to SMC boxes via `ansible_host = {{inventory_hostname}}.teleport.<flavor>.au`.
- Topology plugin generates `topology_interfaces`, `topology_bridges`, `topology_vrfs` per host.
- 7 inventory flavors; group_vars structure separates: teleport, prometheus, jenkins, aws, per-user, all.
