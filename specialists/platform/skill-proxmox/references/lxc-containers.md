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

> **Learned 2026-11-25 (f)** · Proxmox VE 9.2.2 · VERIFIED_PRIMARY (`pveam available --section system` on the node) · Source: home NAS project
> `scripts/host/pve_image_fetch.sh`, `tests/test_pve_image_fetch.sh` (commit 4e25928) · Falsifier: a 9.2 template index without arm64 entries
> The 9.2 template index lists arm64 builds beside amd64 (`debian-13-standard_13.6-1_amd64.tar.zst` and `..._arm64.tar.zst`), and `sort -V | tail -1`
> picks arm64 because it sorts after amd64. Filter by the node's own architecture before choosing the newest:
> ```bash
> name="$(pveam available --section system | awk '{print $2}' | grep "^debian-13-standard_.*_$(dpkg --print-architecture)\.tar" | sort -V | tail -1)"
> ```

> **Disputed 2026-11-25 (h)** · Conflicts: Learned 2026-11-25 (e) ("feature flags other than nesting need root@pam", implying nesting works through
> the token) · Proxmox VE 9.2.2, bpg/proxmox 0.123.1, privilege-separated token · VERIFIED_PRIMARY (apply output) · Source: home NAS project
> `tofu/containers.tf`, `scripts/host/pve_ct_extras.sh` (commit 0514e66) · Falsifier: a bpg apply adding `features { nesting = true }` to an existing
> container with a privsep token succeeding
> PVE itself allows a non-root user to change nesting, but adding `features { nesting = true }` to existing containers through bpg 0.123.1 failed with
> HTTP 403 "changing feature flags (except nesting) is only allowed for root@pam" on all three (cause UNVERIFIED: likely the provider sends the other
> flags too). Debian 13 (systemd 257) runs `degraded` in an unprivileged CT without nesting, and `pct start` warns "Systemd 257 detected". Set nesting in
> the root host script with the other root-only extras and add `features` to `lifecycle.ignore_changes`:
> ```bash
> pct config "$id" | grep -q '^features:.*nesting=1' || pct set "$id" --features nesting=1   # then restart the CT
> ```

> **Learned 2026-11-25 (i)** · Proxmox VE 9.2.2, bpg/proxmox 0.123.1 · VERIFIED_PRIMARY (apply output; `ip -4 addr` in each CT) · Source: home NAS
> project `tofu/containers.tf` (DL-045) · Falsifier: a running CT that needs a restart before the new address appears
> Changing `initialization.ip_config.ipv4` of running unprivileged containers from `dhcp` to a static `address`/`gateway` through bpg is an in-place
> update (no replace, no restart): the three containers had the new address and default route seconds after the apply.

> **Learned 2026-11-25 (j)** · Proxmox VE 9.2 · VERIFIED_PRIMARY (live run from the Mac to CT 100) · Source: home NAS `scripts/nas_tm_status.sh` ·
> Falsifier: `pct exec <ct> -- sh -s` that ignores piped stdin
> `pct exec <ct> -- sh -s -- <args>` passes the SSH session's stdin into the container, so a script kept in the repo runs inside a CT without being copied
> there first, and its arguments reach it as `$1`, `$2`:
>
> ```sh
> # home NAS scripts/nas_tm_status.sh
> ssh -o BatchMode=yes "root@$NAS_HOST" "pct exec $NAS_SMB_CT -- sh -s -- $NAS_TM_SHARE $ip" <"$NAS_ROOT/scripts/ct/tm_progress.sh"
> ```

> **Learned 2026-11-25 (k)** · Debian 13 LXC on PVE 9.2.2, conserver 8.2.7 · VERIFIED_PRIMARY (`systemctl is-enabled` disabled after install;
> `pct reboot` proof after enabling; sshd forced command tested from a client) · Source: home NAS project, scripts/ct/conserver_setup.sh,
> lab_console_setup.sh, lab-console at 38688f6 · Falsifier: a conserver-server package that enables its unit on install
> A setup script that only `systemctl restart`s a packaged service leaves it down after the next CT reboot when the package ships the unit disabled
> (conserver-server does): `enable` then `restart`, and assert `is-enabled`. To give another project console access without root on the node, a CT
> user whose authorized_keys line is `restrict,pty,command="/usr/local/bin/lab-console" <key>` and a wrapper that allows only `list`, `spy <name>`
> (`console -s`, read-only) and `attach <name>` from `SSH_ORIGINAL_COMMAND`; `console -s` works without a tty, so a recorder can stream it.

> **Learned 2026-11-25 (l)** · PVE 9.2.2, running Debian 13 LXC · VERIFIED_PRIMARY (`pct set 102 -dev1 /dev/serial/by-id/...,gid=20,mode=0660` on
> the running CT; the device appeared inside at once) · Source: home NAS console boxer-lab, 2026-11-25 · Falsifier: a devN change that stays pending
> until a CT restart
> A USB-serial adapter passed as `devN` by its /dev/serial/by-id path is hot-added to a running container (no restart); the consumer (conserver) still
> needs its own reload to use it.
