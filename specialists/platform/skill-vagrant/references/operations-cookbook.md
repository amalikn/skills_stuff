---
Title: Operations cookbook
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Exact vagrant, prlctl and prlsrvctl syntax for lab sessions with a deadline on every call and writes marked; verified against Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0.
---

# Operations cookbook

Verified against: Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0 (Parallels Desktop), macOS on Apple silicon, 2026-11-07

Exact syntax for the commands a lab session uses. Every command that can hang carries a deadline (`timeout N`); every write is marked. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [1. Read-only status](#1-read-only-status)
- [2. Running commands in a guest](#2-running-commands-in-a-guest)
- [3. Lifecycle (writes)](#3-lifecycle-writes)
- [4. Boxes](#4-boxes)
- [5. Snapshots](#5-snapshots)
- [6. Parallels networks and adapters](#6-parallels-networks-and-adapters)
- [7. Machine-readable output](#7-machine-readable-output)
- [8. Summary table](#8-summary-table)

## 1. Read-only status

```bash
cd <vagrant-dir> && timeout 60 vagrant status                  # machines in this Vagrantfile, by name
timeout 60 vagrant global-status                                 # every environment Vagrant knows; a cache, not a live probe
timeout 120 vagrant global-status --prune                        # drop rows whose environment is gone (slower)
timeout 30 prlctl list -a                                        # every registered VM: UUID, status, IP, name
timeout 30 prlctl list -a -i -j                                  # full settings of every VM as JSON (State, Parent VM, GuestTools, Hardware.netN)
timeout 30 prlctl list -a -f                                     # the guests' real IP addresses
timeout 30 prlctl status <vm>
timeout 30 prlsrvctl net list                                    # Shared, Host-Only and Vagrant-created host-only networks
```

`global-status` is "based on a cache" and can list environments that no longer exist; `--prune` removes invalid entries and is "much more time consuming" (VERIFIED_PRIMARY,
[vagrant-cli-global-status.md]). `prlctl list` without `-a` shows only running VMs; `-o` picks fields, `-L` lists them, `-j` gives JSON (VERIFIED_PRIMARY, Parallels Desktop 20 Command-Line Reference,
[parallels-desktop-v20-command-line-reference.pdf] p.14).

## 2. Running commands in a guest

```bash
cd <vagrant-dir> && timeout 120 vagrant ssh <machine> -c 'sudo systemctl is-system-running' \
  -- -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=8
timeout 60 vagrant upload <local-path> <guest-path> <machine>
timeout 30 prlctl exec <vm> "uname -r"                            # no network needed; needs Parallels Tools running in the guest
timeout 30 prlctl capture <vm> --file /tmp/<vm>-console.png       # the console as PNG; works when exec and ssh do not
```

`vagrant ssh [name|id] [-- extra_ssh_args]`: arguments after `--` go to the `ssh` program; `-c COMMAND` runs one command, prints stdout and stderr and exits (VERIFIED_PRIMARY, [vagrant-cli-ssh.md]).
Name the machine in a multi-machine Vagrantfile; without a name `vagrant ssh` uses the primary. `prlctl exec` "Executes a command inside a virtual machine. Parallels Tools must be installed"; Linux
commands run with `bash -c` (VERIFIED_PRIMARY, CLI reference p.19). `prlctl capture` writes a PNG of the screen (VERIFIED_PRIMARY, p.21).

Quote the remote command as one argument. Build it with `printf %q` when it contains quotes or `$`, as the worked example does:

```bash
# smc-resiliency spike/vm/sm/setup_sm.sh @ 2402b961 (2026-11-07): every exec has its own deadline
onvm() { timeout "$1" prlctl exec "$VM" "bash -c $(printf %q "$2")"; }
put() { base64 < "$1" | timeout 60 prlctl exec "$VM" "bash -c 'base64 -d > $2 && chmod $3 $2'"; }
```

## 3. Lifecycle (writes)

```bash
vagrant up [<machine>] [--provider=parallels] [--no-provision]   # creates or starts; provisions on first up only
vagrant provision <machine> [--provision-with <name>]            # re-run provisioners
vagrant reload <machine> [--provision]                           # halt + up (re-applies the Vagrantfile and customize)
vagrant halt <machine>; vagrant destroy -f <machine>
timeout 300 prlctl stop <vm>            # graceful through Parallels Tools, else ACPI; --kill is a hard stop
timeout 120 prlctl restart <vm>         # graceful shutdown then start
timeout 120 prlctl reset <vm>           # 'hard' shutdown then start: the guest gets no chance to flush
```

Restart is graceful, reset is a hard power cycle, `stop --kill` a hard stop; `stop` without `--kill` uses Parallels Tools when installed, otherwise ACPI (VERIFIED_PRIMARY, CLI reference p.20). After a
reset, `prlctl exec` fails until Tools come back (see [parallels-prlctl.md](parallels-prlctl.md#exec-after-a-reset)).

## 4. Boxes

```bash
timeout 60 vagrant box list                       # name (provider, version, (arch))
timeout 120 vagrant box outdated --global         # read-only, calls the registry
vagrant box add bento/ubuntu-24.04 --provider parallels --box-version 202510.26.0     # write: downloads
vagrant box prune --dry-run                        # what prune would remove; a linked clone needs its box (boxes-and-pinning.md)
```

## 5. Snapshots

```bash
vagrant snapshot save <machine> <name>; vagrant snapshot list <machine>; vagrant snapshot restore <machine> <name>
timeout 60 prlctl snapshot <vm> -n <name> -d "<why>"
timeout 30 prlctl snapshot-list <vm> -t           # tree; -j for JSON
timeout 300 prlctl snapshot-switch <vm> -i <snapid> [--skip-resume]
```

Do not mix `vagrant snapshot push/pop` with `save/restore` on one machine (VERIFIED_PRIMARY, [vagrant-cli-snapshot.md]). Detail: [clones-snapshots-and-identity.md](clones-snapshots-and-identity.md).

## 6. Parallels networks and adapters

```bash
timeout 30 prlsrvctl net list
timeout 30 prlsrvctl net info <vnetwork_id>
prlctl set <vm> --device-set net1 --disconnect               # write: unplug an adapter (VM may be running)
prlctl set <vm> --device-set net0 --mac auto                 # write: new MAC (VM stopped)
prlctl set <vm> --device-add net --type host-only --iface <vnet>   # write: add an adapter
```

Adapter types are `shared`, `bridged` and `host-only`; `--mac auto` generates one (VERIFIED_PRIMARY, CLI reference p.34).

## 7. Machine-readable output

`--machine-readable` prints `timestamp,target,type,data...` lines; commas inside data are written as `%!(VAGRANT_COMMA)`, newlines as `\n` (VERIFIED_PRIMARY, [vagrant-cli-machine-readable.md]).
`global-status --machine-readable` gives `machine-id`, `provider-name`, `machine-home` and `state` per environment, but no machine name (observed, Vagrant 2.4.9, 2026-11-07). `box list
--machine-readable` gives `box-name`, `box-provider`, `box-version` and `box-architecture`. `vagrant_lab_inventory.py` parses both.

## 8. Summary table

| Need                     | Command                                                          | Writes           |
| ------------------------ | ---------------------------------------------------------------- | ---------------- |
| What exists              | `vagrant global-status`, `prlctl list -a -i -j`                  | no               |
| Is the guest alive       | `prlctl capture <vm> --file x.png`, then `prlctl exec <vm> true` | no (a local PNG) |
| One command in the guest | `vagrant ssh <m> -c '<cmd>' -- -o ConnectTimeout=15`             | guest            |
| Hard power cycle         | `prlctl reset <vm>`                                              | yes              |
| Pinned box present       | `vagrant box list`                                               | no               |
| Newer box published      | `vagrant box outdated --global`                                  | no               |
| Unplug an adapter        | `prlctl set <vm> --device-set netN --disconnect`                 | yes              |

> **Learned 2026-11-07** · logic over adapters · VERIFIED_PRIMARY · Source: smc-resiliency `lab/adapters/transports.py` (VagrantTransport), `lab/logic/e2e.py`;
> the same cases passed on the Vagrant VM and a Proxmox VM · Falsifier: a Vagrant-only case that cannot run through an ssh transport
> Drive a Vagrant lab from a test package through one transport class (`vagrant ssh <machine> -c "sudo bash -c '<cmd>'"` and
> `vagrant upload <src> <dst> <machine>`, run from the Vagrantfile's folder, each call with a timeout), so the same cases run on a
> Proxmox or bench box through ssh; keep a wrong-VM guard (a marker file the clone carries) in the box-side command, not in the transport.
