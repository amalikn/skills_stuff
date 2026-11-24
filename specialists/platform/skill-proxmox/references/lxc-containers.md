---
Title: LXC containers
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/lxc-containers.md
Last reviewed: 2026-11-19
Summary: pct containers from pveam and OCI templates, privileged versus unprivileged, automation limits, and when to choose a VM instead.
---

# LXC containers

System containers managed by `pct`, from templates fetched with `pveam`. Sources: [Roadmap](../documents/research-sources-20261107/pve-wiki-roadmap.html), [pct
chapter](../documents/research-sources-20261107/pve-admin-chapter-pct.md), [bpg provider index](../documents/research-sources-20261107/bpg-provider-index.md).

## Contents

- [Templates](#templates)
- [Privileged and unprivileged](#privileged-and-unprivileged)
- [Automation limits](#automation-limits)
- [When a VM instead](#when-a-vm-instead)

## Templates

- `pveam update` refreshes the template index, `pveam available [--section system]` lists, `pveam download <storage> <template>` fetches into a `vztmpl` storage, `pveam list <storage>` shows what is
  there; `pct create <ctid> <storage>:vztmpl/<template> ...` creates. `VERIFIED_PRIMARY` (pct chapter, Container Images).
- Since 9.1, OCI images (uploaded or pulled from a registry) can be container templates; application containers from OCI are a
  technology preview. `VERIFIED_PRIMARY` (Roadmap, 9.1 highlights).

## Privileged and unprivileged

- Unprivileged containers map root (UID 0) inside to an unprivileged UID outside through user namespaces, so a break-out lands on an unprivileged host user. Prefer them. `VERIFIED_PRIMARY` (pct
  chapter).
- The choice is made at creation. The `pct create` CLI defaults to **privileged** (`--unprivileged` default 0); pass `--unprivileged 1`. `VERIFIED_PRIMARY` (`pct help create --verbose` on 9.1.5,
  2026-11-07).
- Since 9.0, **creating a privileged container needs `Sys.Modify`** in most cases (restoring in place over an already privileged one
  does not). A least-privilege token therefore creates unprivileged containers only. `VERIFIED_PRIMARY` (Roadmap, 9.0 breaking changes).
- Docker or nested workloads need features such as `nesting=1` and, for unprivileged containers, `keyctl=1`. `VERIFIED_PRIMARY` (pct chapter, feature options).

## Automation limits

- Some container operations are root-only through the API, whatever the token's privileges: bind mounts, feature flags on privileged containers, `idmap` entries, device passthrough without a mapping.
  A token gets HTTP 403 "only allowed for root@pam". The bpg provider needs its `ssh` block for `idmap`. `VERIFIED_SECONDARY` (bpg provider index, root-only operations and SSH table).
- Design consequence: a least-privilege automation token can create plain unprivileged containers; anything needing the above is a root-run step outside the token, as with image downloads
  ([access-control.md](access-control.md)).

## When a VM instead

Use a VM when the workload needs its own kernel, kernel modules, a different OS, UEFI and boot-order behaviour, or strong isolation. A container shares the host kernel.

> **Learned 2026-11-24 (d)** · Proxmox VE 9.2 (pct.conf 9.2.15), kernel 7.0, Intel Alder Lake-N iGPU · VERIFIED_PRIMARY (the option and the driver flags; UNVERIFIED on hardware) ·
> Source: <https://pve.proxmox.com/pve-docs/pct.conf.5.html>; Linux `drivers/gpu/drm/xe/xe_pci.c` `adl_n_desc` at v6.18 and v7.0; home NAS project
> `docs/research/hardware-gpu-research-20261124_2300.md` · Falsifier: an unprivileged container that cannot open `/dev/dri/renderD128` with the `gid=` set to its `render` group
> Sharing an Intel iGPU's media engine with containers: keep the GPU on the host and pass only the render node, `dev0: /dev/dri/renderD128,gid=<render GID inside the CT>`
> (`dev[n]: [[path=]<Path>][,deny-write][,gid][,mode][,uid]`, "Device to pass through to the container"); several containers can share it, unlike full PCI passthrough to one VM.
> SR-IOV on Alder Lake-N is not production-ready on 9.2: upstream `xe` marks it `has_sriov = true` but `require_force_probe` (xe is not the default driver for it), and the
> `i915-sriov-dkms` backport calls itself highly experimental. Screenshot pending: CT > Resources > Add > Device Passthrough, after the home NAS Immich container exists.
> ```text
> # /etc/pve/lxc/<vmid>.conf (proposed, home NAS Immich container)
> dev0: /dev/dri/renderD128,gid=<render gid>
> ```

> **Learned 2026-11-25 (e)** · Proxmox VE 9.2, bpg/proxmox 0.123.1 · VERIFIED_PRIMARY (the root@pam limits, bpg container docs: bind mounts and feature
> flags other than nesting need root@pam; the provider schema, `tofu validate`; the host-script half is not yet run on a node) · Source: home NAS project
> `tofu/containers.tf`, `scripts/host/pve_ct_extras.sh` (2026-11-25) · Falsifier: a privilege-separated token adding a host bind mount through the API
> Containers as code with a scoped token: create the container in OpenTofu, then add what needs root (host bind mounts `pct set <id> -mpN <host>,mp=<ct>`, a device such
> as `/dev/net/tun` for Tailscale `pct set <id> -dev0 /dev/net/tun`) with an idempotent host script, and give OpenTofu
> `lifecycle { ignore_changes = [mount_point, device_passthrough] }` so it does not remove them. In an unprivileged container uid 1000 is host uid 101000 (default
> idmap), so the shared dataset's top directory is chowned to 101000:101000. A container serving an encrypted dataset gets `start_on_boot = false` and starts after
> the unlock. Screenshot pending: CT > Resources after the home NAS CT 100 exists.
