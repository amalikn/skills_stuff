# Clones, snapshots and identity

A copy of a VM is cheap under Parallels and dangerous when it keeps the original's identity. This file covers the two kinds of linked clone a lab meets, what a copy shares with its source, and
snapshots. Captures named `[file]` are in [documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Two kinds of linked clone](#two-kinds-of-linked-clone)
- [Cloning a lab VM with prlctl](#cloning-a-lab-vm-with-prlctl)
- [Machine-id](#machine-id)
- [What else a copy shares](#what-else-a-copy-shares)
- [Snapshots](#snapshots)
- [Worked example](#worked-example)

## Two kinds of linked clone

1. **Every vagrant-parallels machine.** Since vagrant-parallels 2.0.0 (2018-11-19) `vagrant up` creates a new VM as a linked clone of the box image (a disk under 1 MB bound to the box's snapshot);
   `linked_clone = false` makes a full, independent copy for new machines; deleting the box breaks its linked clones (VERIFIED_PRIMARY, [vp-configuration.md], [vp-changelog-github.md]). The box image
   is registered, cloned and unregistered during `up`, so `prlctl list -i` shows no `Parent VM` for these machines ([vp-issue-522.md] log; observed 2026-11-07).
2. **A lab clone of a lab VM.** `prlctl clone <vm> --name <new> --linked` makes a linked clone of an existing VM (optionally from a snapshot, `-i <snapid>`); `--regenerate-src-uuid` regenerates the
   source ID and the SMBIOS product ID (VERIFIED_PRIMARY, CLI reference p.17). Its `Parent VM` names the source. The source must stay: the clone's disk holds only its changes.

## Cloning a lab VM with prlctl

- Clone a stopped VM: the worked example stops a running source first ("Parallels clones only a stopped VM (not running, not suspended)", `setup_sm.sh` @ 2402b961; USER_STATED, observed on Parallels
  26 to 27).
- Give the clone new MACs (`prlctl set <clone> --device-set net0 --mac auto`) and decide, per adapter, whether it may meet the source's networks.
- A clone is not Vagrant-managed: `vagrant ssh`, `vagrant halt` and `vagrant destroy` in the source's folder still act on the source. Drive the clone with `prlctl exec` and `prlctl` power commands,
  and delete it with `prlctl delete <clone>` (a write; the operator's).
- Watch the host disk: a linked clone grows with every write it makes; the worked example refuses to start with under 8 GiB free on the data disk.

## Machine-id

`/etc/machine-id` identifies the installation. systemd-networkd's default DHCP identity is a DUID hashed from it, so two VMs with one machine-id get one DHCP lease on a shared network
([networking-and-synced-folders.md](networking-and-synced-folders.md#same-dhcp-address-on-two-vms)). A clone copies the file. Images "created once and used on multiple machines" should ship it missing or empty, so an ID is generated at boot; an empty file is not a
first boot, a missing file or the string `uninitialized` is (VERIFIED_PRIMARY, [machine-id-man.md]).

Check before trusting a copy:

```bash
timeout 30 prlctl exec <source> "cat /etc/machine-id"; timeout 30 prlctl exec <clone> "cat /etc/machine-id"   # must differ
timeout 30 prlctl list -a -f | grep -E '<source>|<clone>'                                                          # addresses must differ
```

Choices, safest first:

1. **No shared network for the clone** (the smc-resiliency rule since 2026-11-06): disconnect the adapters it shares with the source; reach it by `prlctl exec`. Nothing to regenerate, nothing to
   forget.
2. **New identity in the clone** before it joins a shared network: empty `/etc/machine-id` (and check `/var/lib/dbus/machine-id` is a link to it, not a copy, because systemd falls back to it when the
   file is empty), then reboot; systemd writes a new ID (semantics VERIFIED_PRIMARY, [machine-id-man.md]; the procedure on a Parallels clone is UNVERIFIED until a lab runs it and records the new
   lease).
3. **Fix the box**: for many machines from one box, use a box version whose image ships without a fixed ID (the bento regressions are listed in [boxes-and-pinning.md](boxes-and-pinning.md#bento-boxes)).

A new MAC alone does not help: the DUID does not use the MAC unless `DUIDType=link-layer` or `ClientIdentifier=mac` is configured (VERIFIED_PRIMARY, [networkd-conf-man.md], [systemd-network-man.md]).

## What else a copy shares

SSH host keys (so `known_hosts` cannot tell the copies apart), the Vagrant insecure-key replacement in `~/.ssh/authorized_keys`, any service identity under `/etc` or `/var/lib` (a device key, a
registration token), and the hostname. A copy used for a different test renames itself and regenerates what the test depends on, or stays off every network the source uses.

## Snapshots

- `vagrant snapshot save|restore|list|delete <machine> <name>`, or `push`/`pop` as a stack; do not mix `push`/`pop` with `save`/`restore`; not every provider supports snapshots (VERIFIED_PRIMARY,
  [vagrant-cli-snapshot.md]). vagrant-parallels has implemented `vagrant snapshot` since its 1.x series (VERIFIED_PRIMARY, [vp-changelog-github.md], GH-228).
- `prlctl snapshot <vm> -n <name> -d <desc>`, `snapshot-list <vm> -t` (tree) or `-j`, `snapshot-switch <vm> -i <id> [--skip-resume]`, `snapshot-delete <vm> -i <id> [-c]` (VERIFIED_PRIMARY, CLI
  reference pp.39-40).
- A snapshot of a vagrant-parallels machine sits on top of a linked clone of the box: removing the box still breaks it.
- Snapshots are a rollback inside a session, not a backup and not a reproducible build; the Vagrantfile and its pins are what rebuild the lab.
- Take a snapshot before a destructive stage (a disk-fill test, an image switch) and name it after the stage; record its ID with the run.

## Worked example

smc-resiliency's SM stage (measuring root writes) runs on a linked clone of the Pi spike VM, so the spike VM's state is untouched (`smc-resiliency/spike/vm/sm/setup_sm.sh` @ 2402b961):

```bash
# Parallels clones only a stopped VM (not running, not suspended): shut the spike VM down for the clone and start it after
WAS=$(prlctl list -o status "$SRC" | tail -1 | tr -d ' ')
[ "$WAS" = running ] && { timeout 300 prlctl stop "$SRC" >/dev/null || exit 1; }
timeout 600 prlctl clone "$SRC" --name "$VM" --linked; RC=$?
[ "$WAS" = running ] && timeout 300 prlctl start "$SRC" >/dev/null
timeout 60 prlctl set "$VM" --device-set net0 --mac auto >/dev/null && timeout 60 prlctl set "$VM" --device-set net1 --disconnect >/dev/null
```

On 2026-11-06 the clone still received the spike VM's address on the shared network, because it kept the machine-id; `vagrant ssh smc-pi-spike01` then reached the clone. The project disconnected the
clone's shared adapter and added a guard to its driver ([lab-safety-and-guards.md](lab-safety-and-guards.md#refuse-the-wrong-vm)).

> **Learned 2026-11-07** · copy-on-write root · VERIFIED_PRIMARY · Source: smc-resiliency docs/pi/pi-spike-sm-root-writes-20261107_1602.md · Falsifier: a runtime install on a dm-snapshot root that survives a reboot
> On a lab clone whose root is a RAM copy-on-write, anything installed at run time (a fixed watcher script) is gone after the reboot; reinstall after each boot or install into the origin. `dmsetup status` of a snapshot counts 512-byte sectors.
