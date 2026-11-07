# Networking and SDN

Host networking is Debian `ifupdown2` with Linux bridges (`vmbrN`); SDN adds cluster-wide zones and VNets on top. Sources: [Network
Configuration](../documents/research-sources-20261107/pve-wiki-network-configuration.md), [SDN chapter](../documents/research-sources-20261107/pve-admin-chapter-pvesdn.md), [pveum
chapter](../documents/research-sources-20261107/pve-admin-chapter-pveum.md).

## Contents

- [Host network](#host-network)
- [VLANs for guests](#vlans-for-guests)
- [SDN zones and VNets](#sdn-zones-and-vnets)
- [DHCP for guests with SDN and PVE IPAM](#dhcp-for-guests-with-sdn-and-pve-ipam)
- [Permissions on networks](#permissions-on-networks)

## Host network

- Configuration lives in `/etc/network/interfaces`. The GUI and API write to `/etc/network/interfaces.new` and apply it on request; with `ifupdown2` (the default since 7.0) the change applies live.
  After a manual edit of `interfaces`, run `ifreload -a`. `VERIFIED_PRIMARY` (Network Configuration).
- Bridges are named `vmbr0` to `vmbr4094`. A default install has `vmbr0` bridged to the first NIC, carrying the management address. `VERIFIED_PRIMARY`.
- Changing the bridge that carries the management address over SSH or the API can cut you off. Keep console access (IPMI, the physical console) before a host network write.

## VLANs for guests

- **VLAN-aware bridge**: set `bridge-vlan-aware yes` and `bridge-vids 2-4094` on the bridge; each guest NIC then carries `tag=<vid>`, handled transparently by the bridge. The "traditional" alternative
  creates a VLAN device and bridge per VLAN. `VERIFIED_PRIMARY` (Network Configuration, VLAN for Guest Networks and the VLAN-aware example).
- A host management address on a VLAN of a VLAN-aware bridge is an interface like `vmbr0.5` with the address on it.

```text
auto vmbr0
iface vmbr0 inet manual
        bridge-ports eno1
        bridge-stp off
        bridge-fd 0
        bridge-vlan-aware yes
        bridge-vids 2-4094
```

## SDN zones and VNets

- Zone types: **Simple** (an isolated bridge, local to each node, for NAT or routed setups), **VLAN** (tags on an existing bridge, connects nodes), **QinQ**, **VXLAN**, **EVPN**. A VNet is a virtual
  network in a zone; after applying, each node has a local interface with the VNet's name that guests attach to. `VERIFIED_PRIMARY` (SDN chapter, Zones and VNets).
- Changes are pending until applied cluster-wide (the SDN overview's Apply, or `pvesh set /cluster/sdn`). `VERIFIED_PRIMARY` for the pending/apply model; the exact `pvesh set /cluster/sdn` form is
  `UNVERIFIED` here (not run).
- Support status in 9.x: core SDN (VNets) is fully supported; IPAM with DHCP and FRRouting/controller integration are tech preview. `VERIFIED_PRIMARY` (SDN chapter, Current Status).

## DHCP for guests with SDN and PVE IPAM

- A **Simple** zone with `dhcp: dnsmasq` and `ipam: pve`, a VNet in it and a subnet with a gateway and a `dhcp-range` gives guests DHCP
  from the node: PVE IPAM allocates an address for each guest NIC's MAC on that VNet and dnsmasq answers only those. IPAM with DHCP is
  tech preview in 9.x. `VERIFIED_PRIMARY` (SDN chapter: Simple zone, DHCP IPAM, Current Status). A second simple zone with SNAT on its
  subnet gives guests outbound NAT through the node.
- Attach the guest to the **VNet** (`bridge = "<vnet>"` in OpenTofu, `net0: virtio=<mac>,bridge=<vnet>`), not to `vmbr0`: a LAN DHCP
  server that binds MACs answers nothing for an unknown guest on `vmbr0`, and the node's IPAM never sees it.
- Where to look on the node: the MAC binding in `/etc/dnsmasq.d/<zone>/ethers`, the lease in `/var/lib/misc/dnsmasq.<zone>.leases`,
  the per-VNet config beside `ethers`; read the SDN side with `pvesh get /cluster/sdn/zones`, `/cluster/sdn/vnets` and
  `/cluster/sdn/vnets/<vnet>/subnets`. Neighbour tables on `vmbr0` (`ip neigh show dev vmbr0`) never see a guest on a VNet.
- Pin the NIC's MAC (`mac_address` in the provider's `network_device`) so the IPAM binding, and so the address, survives destroy and
  recreate. A small range reuses addresses: clear stale `known_hosts` entries for a reused address before trusting a host-key warning.

## Permissions on networks

- `SDN.Use` grants "access SDN vnets and local network bridges"; `SDN.Audit` views SDN configuration; `SDN.Allocate` manages it. `VERIFIED_PRIMARY` (pveum privilege list).
- Plain host bridges sit in the built-in zone `localnetwork`: an ACL on `/sdn/zones/localnetwork` (or `/sdn/zones/localnetwork/<bridge>`) with `SDN.Use` lets a token attach a NIC to `vmbr0`. Without
  `SDN.Audit` or `SDN.Use` there, `GET /nodes/{node}/network` hides the bridges from the caller. `VERIFIED_SECONDARY` (bpg provider index, two notes) and observed: the lab's least-privilege token
  attaches `vmbr0` with exactly that grant (see [access-control.md](access-control.md)).
- A guest NIC on an SDN VNet needs `SDN.Use` on that zone (`/sdn/zones/<zone>`, or the VNet below it) in addition to
  `localnetwork` for plain bridges; with privilege separation, grant it to the user and the token.

> **Learned 2026-11-07 (c)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /access/acl`, `qm config`, and the task log: `qmcreate`, `resize`, `qmstart` by the
> token) · Falsifier: a 9.x node where a token with SDN.Use only on /sdn/zones/localnetwork is refused a NIC on vmbr0
> A privilege-separated OpenTofu token whose role includes `SDN.Use`, granted on `/sdn/zones/localnetwork` to both the user and the token, created a VM with `net0: virtio=...,bridge=vmbr0`. No grant
> on `/` or `/nodes` beyond `Sys.Audit` was needed for the NIC.

<!-- next write-back entry -->

> **Learned 2026-11-07 (j)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /cluster/sdn/zones`, `/cluster/sdn/vnets`, `/cluster/sdn/vnets/dhcp0/subnets`,
> `/access/acl`, `qm config 901`, `ls /etc/dnsmasq.d/dhcp/`) and the coordinating session's tcpdump on vmbr0 (2026-11-07) · Falsifier: a 9.x simple zone with dhcp dnsmasq and ipam pve that answers
> a guest MAC IPAM never allocated
> On a LAN whose DHCP server binds MACs, a cloud-image VM on `vmbr0` sent DHCPDISCOVER and got no answer. Moving its NIC to a VNet in a
> simple zone (`dhcp: dnsmasq`, `ipam: pve`, a /28 subnet with the gateway on the node and a DHCP range) made PVE IPAM allocate an
> address and write the MAC binding to `/etc/dnsmasq.d/<zone>/ethers`; the lease appeared in `/var/lib/misc/dnsmasq.<zone>.leases`.
> The OpenTofu token also needed `SDN.Use` on `/sdn/zones/<zone>`, granted to user and token like `localnetwork`.

> **Learned 2026-11-07** · SDN DHCP · VERIFIED_PRIMARY · Source: smc-resiliency spike/x86/x86_lab.sh (`ip` action), commit 26ada6fb · Falsifier: a vnet guest that appears in `ip neigh show dev vmbr0`
> A guest on an SDN vnet never shows in the uplink bridge's neighbour table; read its address from the zone's dnsmasq leases on the node instead:
> ```bash
> awk -v m="$mac" 'tolower($2)==m{print $3; exit}' /var/lib/misc/dnsmasq.dhcp.leases
> ```

> **Learned 2026-11-07** · SDN IPAM, isolated bridge · VERIFIED_PRIMARY · Source: `/etc/dnsmasq.d/<zone>/ethers` before and after stopping VMs;
> smc-resiliency `pve_lab_setup.sh` (vmbr9 step) · Falsifier: a stopped VM's MAC still listed in `ethers`
> PVE IPAM binds a VM's MAC when the VM starts and drops the binding when it stops: with ten VMs stopped, `ethers` listed only the two running,
> and a new VM was given an address a stopped VM had held. Count the subnet for the most VMs that run at once. A lab trunk between two VMs
> needs no SDN: an isolated Linux bridge (`bridge-ports none`, no address, added to `/etc/network/interfaces` with a backup, `ifreload -a`)
> carries tagged VLANs between guests and nothing leaves the node; the token's `SDN.Use` on `/sdn/zones/localnetwork` covers it.
