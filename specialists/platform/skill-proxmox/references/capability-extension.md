---
Title: Capability extension
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/capability-extension.md
Last reviewed: 2026-11-07
Summary: Search order before building around Proxmox VE: core, Proxmox products (PBS, Datacenter Manager), the bpg provider, supported seams, then FOSS; common needs and where each is met.
---

# Capability extension

What to reach for before building something around Proxmox VE, in order. Sources: the admin guide chapters and the bpg provider docs in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Search order](#search-order)
- [Common needs and where they are met](#common-needs-and-where-they-are-met)
- [Extension seams](#extension-seams)

## Search order

```text
desired operator outcome
  ↓ Proxmox VE core (API, pvesh/qm/pct/pveum, SDN, HA, firewall, vzdump, metric servers)
  ↓ Proxmox products (Proxmox Backup Server, Proxmox Datacenter Manager) and the bpg/proxmox provider
  ↓ supported seams: hook scripts (snippets), cloud-init custom data, API clients, Ansible Proxmox modules (collection name `UNVERIFIED` here)
  ↓ compatible external FOSS (exporters, IPAM, DNS) through the API
  ↓ from-scratch component only when the acceptance test still cannot be met
```

At every step down, state why the step above cannot meet the acceptance test (USER_STATED policy shared with skill-nautobot,
[.archcore/rules/capability-search-order.rule.md](../.archcore/rules/capability-search-order.rule.md)). Never patch PVE's Perl or
JavaScript on a node: an update overwrites it silently.

## Common needs and where they are met

| Need                         | Native first                                                        | Note                                                                                            |
| ---------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| VMs as code                  | bpg/proxmox with OpenTofu                                           | Telmate provider not used ([opentofu-bpg-provider.md](opentofu-bpg-provider.md))                |
| Guest DHCP and addresses     | SDN simple zone with dnsmasq + PVE IPAM                             | Tech preview in 9.x; external IPAM (NetBox, phpIPAM) is a supported SDN plugin                  |
|                              |                                                                     |   type ([networking-and-sdn.md](networking-and-sdn.md))                                         |
| Backups with dedup           | PBS (sync jobs between PBS instances)                               | [backup-and-restore.md](backup-and-restore.md)                                                  |
|   and offsite                |                                                                     |                                                                                                 |
| Metrics                      | External metric server (InfluxDB, Graphite, OpenTelemetry)          | Prometheus via an exporter                                                                      |
| Run code on guest events     | Hook scripts in `snippets`                                          | Runs as root on the node: review like code                                                      |
| Many clusters in one view    | Proxmox Datacenter Manager (1.0 on 2025-12-04, 1.1 on 2026-05-28) | Remotes for PVE and PBS, cross-cluster guest migration, Ceph status of remotes, automated-install answer files, subscription registry (1.1). `VERIFIED_PRIMARY` ([PDM roadmap](../documents/research-sources-20261109/pdm-docs-roadmap.html)) |
| Inventory of record          | The source-of-truth system (for example Nautobot) reads PVE through | Proxmox is the actual state, not the intent ([skill-nautobot](../../skill-nautobot/SKILL.md))   |
|                              |   the API                                                           |                                                                                                 |

`VERIFIED_PRIMARY` for the native rows from their chapters; IPAM plugin types (pve, NetBox, phpIPAM) from the SDN chapter.

## Extension seams

- **Hook scripts**: `qm set <vmid> --hookscript local:snippets/<script>` is "called during various phases of the guests lifetime" (`VERIFIED_PRIMARY`, qm chapter, Hookscripts); the phase names
  (pre-start,
  post-start, pre-stop, post-stop) are in the example script `/usr/share/pve-docs/examples/guest-example-hookscript.pl` (`UNVERIFIED` here).
- **cloud-init custom data**: `--cicustom user=...,network=...,meta=...` from `snippets` ([qemu-vms.md](qemu-vms.md#cloud-init)).
- **API clients**: any HTTP client with a token header; keep reads and writes separate and writes gated ([api-and-cli.md](api-and-cli.md)).
