---
name: skill-proxmox
description: >-
  Design, operate, automate and troubleshoot Proxmox VE 9.x: clusters, Corosync, pmxcfs (/etc/pve); storage (dir, LVM-thin, ZFS, Ceph/pveceph, PBS 4.x); bridges, VLAN-aware bridges, SDN zones/VNets,
  DHCP/IPAM; QEMU VMs (q35, OVMF, Secure Boot, cloud-init, guest agent, disk import, templates, migration, PCI/USB mappings, virtiofs), LXC; users, realms, roles, ACLs, API tokens; REST API, pvesh,
  pveum, qm, pct, pvesm; OpenTofu bpg/proxmox; vzdump and PBS backups; HA; upgrades (pve8to9); certificates, firewall, metrics, notifications; arm64 hosts; Datacenter Manager. Not for the guest OS
  inside a VM or device-specific facts.
---

# Proxmox VE

## Contents

- [Role and non-goals](#role-and-non-goals)
- [Read, write, and evidence boundaries](#read-write-and-evidence-boundaries)
- [Orient first](#orient-first)
- [Route the task](#route-the-task)
- [Verify version-sensitive facts](#verify-version-sensitive-facts)
- [Search before building](#search-before-building)
- [Project boundary](#project-boundary)
- [Standing write-back contract](#standing-write-back-contract)

---

## Role and non-goals

Use this skill for the virtualisation platform: how a Proxmox VE node or cluster is built, configured, automated, secured, upgraded and diagnosed, and how OpenTofu drives it through the bpg/proxmox
provider. It does not hold the guest operating system's knowledge (what runs inside a VM belongs to that workload's skill or project), site or customer specifics, or a project's lab inventory.

Sibling skills (hand off, do not duplicate): `skill-vagrant` for local Parallels VMs on the Mac, the arm64 half of a lab whose x86 half runs here
(lab symmetry lives in its [tool-choice-and-lab-symmetry.md](../skill-vagrant/references/tool-choice-and-lab-symmetry.md)); `skill-coder` before writing or changing any script, OpenTofu module or
recipe this skill describes; `skill-drawio` for a project's lab flow pages; the workload's own skill (for example `skill-smc`) for what runs inside a VM.

## Read, write, and evidence boundaries

Reading a node (API GETs, `pvesh get`, `qm config`, `pveversion`) needs no approval when the engaging project allows read-only access. Every write (a `pvesh create|set|delete`, `qm set`, `pveum`,
`apt`, an OpenTofu apply) needs the engaging project's authorization, prints a plan first and runs only with `--apply`. `apt update` is a write; so is a node network change, which can cut off access.
Never print or store a token secret outside a password manager. Keep each observation's node, version, time and identity when a later decision may depend on it. Label load-bearing claims
`VERIFIED_PRIMARY`, `VERIFIED_SECONDARY`, `UNVERIFIED` or `USER_STATED`.

## Orient first

On an unfamiliar node, establish the version, quorum, storage and who can do what before anything else; behaviour and privileges change between releases (9.0 removed `VM.Monitor`, 9.1 and 9.2 changed
QEMU, OVMF and HA).

```bash
pveversion -v | head -5; pvecm status 2>/dev/null | grep -E 'Quorate|Nodes'; pvesm status
pvesh get /nodes/localhost/apt/update --output-format json | head -c 300   # pending updates, cached list (no refresh)
pveum acl list; pveum user list                                             # who can do what
```

`scripts/` holds tested, stdlib-only helpers (`just helpers`): `pve_node_report.py` (a read-only health and inventory report in one SSH round trip; `just node_report --host <node>`),
`pve_token_audit.py` (least-privilege audit of users, tokens and ACLs; `just token_audit --host <node>`) and `pve_ssh.py` (the batched reader both use).

## Route the task

Choose this skill when the object being changed is a Proxmox VE node, cluster, storage, network, guest definition, identity or the OpenTofu configuration that drives them. What runs inside a guest
goes to that workload's skill; the inventory of record goes to the source-of-truth skill (for example skill-nautobot), which reads Proxmox as actual state.

| Task                                                                            | Read first                                   |
| ------------------------------------------------------------------------------- | -------------------------------------------- |
| Exact syntax: pvesh, pveum, qm, pct, pvesm, API paths                           | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Nodes, clusters, Corosync, quorum, pmxcfs, node removal, arm64                  | [references/architecture-and-cluster.md](references/architecture-and-cluster.md) |
| Storage types, content types, import, hyperconverged Ceph                       | [references/storage.md](references/storage.md) |
| Bridges, VLAN-aware bridges, SDN zones, VNets, DHCP and IPAM                    | [references/networking-and-sdn.md](references/networking-and-sdn.md) |
| VMs: q35, OVMF, boot order, cloud-init, agent, serial, clones, migration, mappings | [references/qemu-vms.md](references/qemu-vms.md) |
| LXC containers, privileged and unprivileged, templates                          | [references/lxc-containers.md](references/lxc-containers.md) |
| Users, realms, roles, privileges, ACLs, pools, API tokens, 2FA                  | [references/access-control.md](references/access-control.md) |
| REST API, authentication, tasks, safe readers and writers                       | [references/api-and-cli.md](references/api-and-cli.md) |
| OpenTofu with bpg/proxmox: auth, ssh block, import, state                       | [references/opentofu-bpg-provider.md](references/opentofu-bpg-provider.md) |
| vzdump, PBS 4.x (S3), retention and restore                                     | [references/backup-and-restore.md](references/backup-and-restore.md) |
| HA, placement rules, fencing, storage replication                               | [references/ha-and-replication.md](references/ha-and-replication.md) |
| Repositories, updates, 8-to-9 upgrade, 9.x changes, triage                      | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Certificates, ACME, firewall, hardening                                         | [references/security-certificates-firewall.md](references/security-certificates-firewall.md) |
| Health reads, metrics, notifications, node report                               | [references/monitoring-and-metrics.md](references/monitoring-and-metrics.md) |
| Missing capability: native, Proxmox products, seams, FOSS                       | [references/capability-extension.md](references/capability-extension.md) |
| Reusable learning capture and engagement closeout                               | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Verify version-sensitive facts

Before asserting an API path, privilege, CLI option, provider attribute or release behaviour, check the documentation for the exact installed version (or the installed source on the node,
`/usr/share/perl5/PVE/`) and the provider version in the lock file, and record the source and date in [sources.yaml](sources.yaml). Official pages are kept verbatim in
[documents/research-sources-20261107/](documents/research-sources-20261107/readme.md). Use
[compatibility.yaml](compatibility.yaml) only for its stated environment and evidence rung; a lab observation is not a production guarantee.

## Search before building

```text
desired operator outcome
  ↓ Proxmox VE core (API, CLIs, SDN, HA, firewall, vzdump, metric servers)
  ↓ Proxmox products (PBS, Datacenter Manager) and the bpg/proxmox provider
  ↓ supported seams (hook scripts, cloud-init custom data, API clients)
  ↓ compatible external FOSS through the API
  ↓ from-scratch component only when the acceptance test still cannot be met
```

At every downward step, state why the step above cannot meet the acceptance test. The Telmate provider is not used.

## Project boundary

Keep node names, addresses, VMID ranges, pools, password-manager entries and lab inventories in the engaging project. A worked example cited here (smc-resiliency's x86 lab) is an example, not stock
behaviour. A project may keep its own Proxmox conventions (pools, token identities, VMID ranges, approval rules); check its `AGENTS.md` before any write; project rules outrank this skill.

## Standing write-back contract

Invoking this skill obliges you to write back what the engagement taught, in any project, before the session ends: a dated Learned entry in the focused reference plus one CHANGELOG line under `##
Unreleased`, read back after writing. Classify every engagement in one sentence (no new learning, verified update, candidate, contradiction, project-only, equipment-only). Skill use never authorizes
editing a live system; edit this source only when the task permits it, otherwise leave the entry in the engaging project. Format, classes and release reconciliation:
[references/evolution-and-write-back.md](references/evolution-and-write-back.md).

**Evidence with every entry (operator, 2026-10-20; every calling project owes it).** A write-back that records how something is done carries (1) a **code excerpt** of the logic that does it: the few
lines that matter (about 30 at most), as a fenced block with its source path and commit, secrets and customer identifiers removed; and (2) for anything with a visual surface (the Proxmox web UI, a
device web UI, a draw.io render) a **screenshot** as reference, saved under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each image, what it shows and where it was taken. Node
names, addresses, MACs and serials are redacted or the shot is taken on a lab node; when the surface is not live yet, the entry says "screenshot pending: `<page>`, after `<deploy>`" and the next
engagement adds it.
