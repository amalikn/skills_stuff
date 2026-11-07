# QEMU VMs

VM definition, firmware, disks, cloud-init, guest agent, serial console, templates and clones. Sources: [qm chapter](../documents/research-sources-20261107/pve-admin-chapter-qm.html),
[qm.conf(5)](../documents/research-sources-20261107/pve-qm-conf-man5.md), [Cloud-Init Support](../documents/research-sources-20261107/pve-wiki-cloud-init-support.md), [Qemu guest
agent](../documents/research-sources-20261107/pve-wiki-qemu-guest-agent.md), [Serial Terminal](../documents/research-sources-20261107/pve-wiki-serial-terminal.md), edk2 sources
([QemuBootOrderLib.c](../documents/research-sources-20261107/edk2-QemuBootOrderLib.c.txt), [BdsPlatform.c](../documents/research-sources-20261107/edk2-ovmf-BdsPlatform.c.txt),
[BdsEntry.c](../documents/research-sources-20261107/edk2-BdsEntry.c.txt)).

## Contents

- [Machine and CPU](#machine-and-cpu)
- [UEFI: OVMF and the EFI disk](#uefi-ovmf-and-the-efi-disk)
- [Boot order and what OVMF does with it](#boot-order-and-what-ovmf-does-with-it)
- [Disks and import](#disks-and-import)
- [Cloud-init](#cloud-init)
- [Guest agent and serial console](#guest-agent-and-serial-console)
- [Templates and clones](#templates-and-clones)
- [Worked example config](#worked-example-config)

## Machine and CPU

- `machine: q35` gives a PCIe topology; PCIe passthrough and vIOMMU need it. i440fx remains the default machine type. `VERIFIED_PRIMARY`.
- CPU type: the backend default is `kvm64`; the GUI default for new VMs is `x86-64-v2-AES`. Pick the oldest `x86-64-v*` level every node in the cluster supports so live migration keeps working.
  `VERIFIED_PRIMARY` (qm chapter, CPU Type).
- A virtual watchdog is available: `watchdog: model=i6300esb|ib700,action=reset|...`. `VERIFIED_PRIMARY` (qm.conf).

## UEFI: OVMF and the EFI disk

- `bios: ovmf` boots UEFI. "In order to save things like the boot order, there needs to be an EFI Disk" (`efidisk0`); there can only be one, and it is in backups and snapshots. Without it, EFI
  variables (`BootOrder`, `BootNext`, `Boot####`) are lost at every stop. `VERIFIED_PRIMARY` (qm chapter, BIOS and UEFI).
- `efitype=4m` is the one to use for new VMs (Secure Boot capable, more space); `2m` is the backend default. `VERIFIED_PRIMARY`.
- `pre-enrolled-keys=1` uses a vars template with distribution and Microsoft keys **and turns Secure Boot on** (it can be turned off inside the VM); `0` (default) leaves Secure Boot off, so unsigned
  bootloaders and UKIs boot. `VERIFIED_PRIMARY` (qm.conf `efidisk0`).
- Certificates: with `pve-edk2-firmware` 4.2025.05-1 or later, new EFI disks with keys carry both the 2011 and 2023 Microsoft certificates and the `ms-cert=2023k` marker; older EFI disks need the 2023
  certificates enrolled before booting media signed only with them. `VERIFIED_PRIMARY` (qm chapter).

## Boot order and what OVMF does with it

- `boot: order=scsi0;net0` sets the device order QEMU passes to the firmware. `VERIFIED_PRIMARY` (qm chapter, Device Boot Order).
- **OVMF rewrites `BootOrder` on every boot** from that list (QEMU's `bootorder` fw_cfg): matching boot options first in that order, other active options kept after them, and `HD()` options that match
  no listed device are **dropped and their `Boot####` deleted** (`PruneBootVariables`). So a second EFI boot entry on a disk not in `boot: order=` does not survive a boot. `VERIFIED_PRIMARY` (edk2
  master `QemuBootOrderLib.c`, `BdsPlatform.c` calls `SetBootOrderFromQemu` each boot).
- **OVMF honours `BootNext`** as the UEFI spec says: BDS caches it, deletes the variable before booting the option, then boots it, so a one-shot trial falls back to `BootOrder` at the next reset.
  `VERIFIED_PRIMARY` (edk2 master `BdsEntry.c`). That Proxmox's packaged OVMF matches edk2 master here is `VERIFIED_SECONDARY` (same upstream, not diffed).
- Consequence for A/B or boot-slot tests in a VM: put every slot's disk in `boot: order=`, or the firmware deletes the other slot's entry; and remember this rewrite is OVMF behaviour that real
  hardware firmware does not have.

## Disks and import

- `import-from` copies an image into a new volume at creation: `qm set <vmid> --scsi0 <target>:0,import-from=<path-or-volume>`; the source may be an `import`-content volume such as
  `local:import/<file>.qcow2`. `VERIFIED_PRIMARY` (qm chapter, cloud-init example).
- Ubuntu cloud images need the `virtio-scsi-pci` controller for SCSI disks. `VERIFIED_PRIMARY` (qm chapter).
- `discard=on` passes TRIM to thin storage; `ssd=1` emulates an SSD (not on VirtIO block). `VERIFIED_PRIMARY` (qm.conf drive options).

## Cloud-init

- Cloud-init VMs need a CD-ROM drive for the generated config: `qm set <vmid> --ide2 <storage>:cloudinit`. Values: `ciuser`, `cipassword`, `sshkeys`, `ipconfig0` (`ip=dhcp` or `ip=<cidr>,gw=<addr>`),
  `nameserver`, `searchdomain`. `VERIFIED_PRIMARY` (qm chapter, Cloud-Init Support).
- Custom user, network or meta data come from `snippets` volumes: `--cicustom "user=local:snippets/<file>.yaml"`. `VERIFIED_PRIMARY`.
- `qm cloudinit update <vmid>` regenerates the config drive (`VERIFIED_PRIMARY`, `qm help` on 9.1.5); `qm cloudinit dump <vmid> user` shows
  what the guest will read. Cloud-init inside the guest acts once per instance, on first boot (`VERIFIED_PRIMARY`, Cloud-Init Support wiki).

## Guest agent and serial console

- The guest agent needs two steps: install and run `qemu-guest-agent` inside the guest, **and** enable it on the VM (`agent: 1`). With it, PVE reads addresses (`qm guest cmd <vmid>
  network-get-interfaces`), freezes file systems for backups and shuts down cleanly. Without it, a shutdown is ACPI only and OpenTofu needs `stop_on_destroy = true`. `VERIFIED_PRIMARY` (qm chapter;
  bpg vm page).
- Ubuntu's cloud image does not ship `qemu-guest-agent`; with the agent disabled the VM's address is found another way (DHCP leases, the node's neighbour table by MAC). `UNVERIFIED` for the image
  contents (observed by the worked example, not from Ubuntu's manifest).
- Without the agent, find a guest's address from the network side: on an SDN VNet with PVE IPAM, the dnsmasq `ethers` binding and
  lease file on the node ([networking-and-sdn.md](networking-and-sdn.md#dhcp-for-guests-with-sdn-and-pve-ipam)); on a plain bridge,
  the LAN's DHCP server or the node's neighbour table, which never sees a guest on a VNet.
- Serial console: `qm set <vmid> --serial0 socket` (and `--vga serial0` to make it the only display); `qm terminal <vmid>` attaches. `VERIFIED_PRIMARY` (qm chapter; Serial Terminal wiki).

- The serial socket is `/var/run/qemu-server/<vmid>.serial0` on the node; read it without a terminal session with
  `socat -u UNIX-CONNECT:/var/run/qemu-server/<vmid>.serial0 -`. The socket belongs to the running QEMU process: `qm reboot` (a
  stop and start through PVE) closes it, so reattach after the VM starts again. Observed in the lab on 9.1.5 (2026-11-07, the
  coordinating session); the socket path is `VERIFIED_PRIMARY` by listing `/var/run/qemu-server/` on the node.

## Templates and clones

- `qm template <vmid>` turns a VM into a read-only template. A **linked clone** shares the template's base disk (fast, needs the same storage, the template cannot be deleted while clones exist); a
  **full clone** copies everything. `VERIFIED_PRIMARY` (qm chapter, Copies and Clones).

## Worked example config

The smc-resiliency x86 lab (`spike/x86/tofu/main.tf`, uncommitted on 2026-11-07) creates this VM through OpenTofu; `qm config` on the lab node read back (2026-11-07, keys and IDs trimmed):

```text
bios: ovmf
machine: q35
boot: order=scsi0;net0
cpu: x86-64-v2-AES
efidisk0: local:901/vm-901-disk-0.qcow2,efitype=4m,pre-enrolled-keys=0,size=528K
scsi0: local:901/vm-901-disk-1.qcow2,...,discard=on,...,size=16G
ide2: local:901/vm-901-cloudinit.qcow2,media=cdrom
ipconfig0: ip=dhcp
serial0: socket
agent: enabled=0,...
```

> **Learned 2026-11-07 (d)** · Proxmox VE 9.1.5, pve-edk2-firmware 4.2025.05-2 · VERIFIED_PRIMARY · Source: lab node read-only (`qm config`, `pvesh get /nodes/localhost/apt/update`) and the
> smc-resiliency OVMF research (docs/x86/x86-ab-boot-research-20261107_1504.md, section 8) · Falsifier: a 4m EFI disk created by the provider with `pre_enrolled_keys = false` that shows Secure
> Boot enabled
> The bpg provider's `efi_disk { type = "4m", pre_enrolled_keys = false }` becomes `efidisk0: ...,efitype=4m,pre-enrolled-keys=0`, so Secure Boot is off and unsigned UKIs boot. The installed OVMF was
> 4.2025.05-2 while the no-subscription repository already offered 4.2026.08-1: state the **installed** firmware version when citing OVMF behaviour, not the repository's.

> **Learned 2026-11-07 (b)** · OVMF 4.2026.08-1 (PVE 9.2.26), RAUC efi backend · VERIFIED_PRIMARY · Source: smc-resiliency
> `docs/x86/x86-spike-x2-ab-boot-20261107_1847.md` findings X2-2, X2-5, X2-6 · Falsifier: an entry in BootOrder kept with its file missing
> OVMF deletes a boot entry that is in BootOrder when its file is missing or not a loadable image: recreate a slot's entry before arming a
> trial. The Ubuntu cloud kernel ships no watchdog driver (i6300esb, iTCO_wdt are in linux-modules-extra), and Ubuntu's deny-list also stops
> systemd-modules-load (`Module 'i6300esb' is deny-listed (by kmod)`), so a virtual watchdog never fires without a deliberate load path.
>
> The recreate step, as RAUC's pre-install handler runs it (smc-resiliency `lab/payloads/x2_setup.sh`, commit 61abf479; the new entry is kept out
> of BootOrder, RAUC adds it at the commit):
>
> ```sh
> efibootmgr | grep -qE "^Boot[0-9A-F]{4}\*? $boot([[:space:]]|$)" && continue
> order=$(efibootmgr | sed -nE 's/^BootOrder: //p')
> efibootmgr -q -c -d "$DISK" -p "$ESP_PART" -L "$boot" -l "\\EFI\\smc\\$boot\\vmlinuz.efi" -u "root=PARTUUID=$uuid rw rauc.slot=$boot ..."
> [ -n "$order" ] && efibootmgr -q -o "$order"
> ```

> **Learned 2026-11-08** · q35 VM on PVE 9.2.26, Ubuntu 24.04 guest (kernel 6.8.0-147) · VERIFIED_PRIMARY · Source: smc-resiliency
> `docs/overview/smc-lab-test-record-20261107_1931.md` section 14 · Falsifier: a q35 guest where `modprobe iTCO_wdt` gives no /dev/watchdog0
> A q35 machine emulates the ICH9 chipset, whose TCO timer the guest's `iTCO_wdt` drives (`identity="iTCO_wdt"`), so the guest gets a watchdog
> without the `i6300esb` device. Ubuntu's deny-list stops alias loading and systemd-modules-load, not an explicit `modprobe <name>`; with
> `RuntimeWatchdogSec=30` a crash with `kernel.panic=0` reset the VM by itself in 91.1 s. Excerpt (smc-resiliency `lab/payloads/x1_watchdog.sh`, d1a7d894):
>
> ```sh
> for m in $DRIVERS; do   # iTCO_wdt first, then the Super I/O drivers, then i6300esb
>   modinfo -n "$m" >/dev/null 2>&1 || continue
>   if timeout 30 modprobe "$m" 2>/dev/null && [ -e /sys/class/watchdog/watchdog0 ]; then bound=$m; break; fi
> done
> printf '[Manager]\nRuntimeWatchdogSec=%s\n' "$SEC" >/run/systemd/system.conf.d/90-smc-x1.conf
> timeout 60 systemctl daemon-reexec
> ```
