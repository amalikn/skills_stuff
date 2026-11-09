---
Title: LXC containers
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/lxc-containers.md
Last reviewed: 2026-11-07
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
