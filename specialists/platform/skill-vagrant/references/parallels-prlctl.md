# Parallels prlctl

`prlctl` manages VMs and `prlsrvctl` manages Parallels Desktop itself. Vagrant's provider drives both; a lab uses them directly to reach a guest without the network, to see its console, and to
power-cycle it. Source of record: Parallels Desktop 20 Command-Line Reference ([parallels-desktop-v20-command-line-reference.pdf], PDF page numbers below) and the Parallels Developer's Guide
([parallels-cli-utility.md], [parallels-cli-manage-vms.md]); observed behaviour is on prlctl 27.1.0.

## Contents

- [Who can run it](#who-can-run-it)
- [Inventory](#inventory)
- [exec: a command without the network](#exec-a-command-without-the-network)
- [exec after a reset](#exec-after-a-reset)
- [capture: the console when nothing else answers](#capture-the-console-when-nothing-else-answers)
- [Power: restart, reset, stop](#power-restart-reset-stop)
- [Parallels Tools](#parallels-tools)
- [prlsrvctl](#prlsrvctl)

## Who can run it

"In Pro and Business/Enterprise Editions, you can control Parallels Desktop and virtual machines from the command-line interface" (VERIFIED_PRIMARY, [parallels-cli-utility.md]). The Standard edition
has no CLI, so neither `prlctl` nor vagrant-parallels works with it; see [licensing-and-editions.md](licensing-and-editions.md). Check with `prlsrvctl info --license --json` and read only `edition` and `status` (the output also
carries a masked licence key; do not paste it into notes).

## Inventory

```bash
timeout 30 prlctl list -a -i -j     # one JSON array: Name, ID, State, Parent VM, GuestTools {state, version}, Hardware {netN: {type, iface, mac, state}}
```

`prlctl list -a -i -j` returned all 22 VMs with full settings in 0.4 s on the lab Mac (observed 2026-11-07), so one call replaces a loop of `prlctl list -i <vm>`. Fields a lab reads: `State`
(`running`, `stopped`, `suspended`, `invalid` for a registered VM whose bundle is gone), `Parent VM` (set on a `prlctl clone --linked` copy; empty on a Vagrant machine, because vagrant-parallels
unregisters the box image after cloning: "Registering VM image from the base box ... Creating new virtual machine as a linked clone of the box image... Unregistering the box VM image",
[vp-issue-522.md] log), `GuestTools.state` (`installed`, `outdated`, `not_installed`), and each adapter's `type` and `state` (`disconnected` when unplugged). `vagrant_lab_inventory.py` reads exactly
this.

## exec: a command without the network

`prlctl exec <vm> <command>` runs a command inside the VM through Parallels Tools; Linux commands run with `bash -c`; `--current-user` or `--user` picks the account (VERIFIED_PRIMARY, CLI reference
p.19). It needs no guest network, so it reaches a VM whose `eth0` a test has cut, and it runs as root by default on a Linux guest (observed: the worked example's `onvm` runs `systemd-run`, `findmnt`,
writes under `/usr/local` without sudo). Pass the whole command line as one argument and quote it once:

```bash
# smc-resiliency spike/vm/sm/setup_sm.sh @ 2402b961
onvm() { timeout "$1" prlctl exec "$VM" "bash -c $(printf %q "$2")"; }
put() { base64 < "$1" | timeout 60 prlctl exec "$VM" "bash -c 'base64 -d > $2 && chmod $3 $2'"; }   # stdin is passed through
```

Every exec gets its own deadline: an exec into a wedged guest does not return by itself (USER_STATED, lab 2026-11-07: "`prlctl exec` hangs or errors when a guest is wedged").

## exec after a reset

After `prlctl reset` (or a guest-side watchdog reboot) `prlctl exec` fails until Parallels Tools are running again in the new boot, with errors such as `Unable to open new session` and
`PrlJob_GetResult: Invalid argument` (USER_STATED, lab observation 2026-11-07; the messages are not in the CLI reference). Treat them as "not ready yet", not as a failed command: poll with a short
deadline and a bounded number of tries, as the worked example does after every restart:

```bash
timeout 120 prlctl restart "$VM" >/dev/null; for _ in $(seq 1 60); do onvm 20 true 2>/dev/null && break; sleep 5; done
```

If the loop runs out, the guest may not have booted at all: take a console capture before anything else.

## capture: the console when nothing else answers

`prlctl capture <vm> --file <name>` "Captures a screen area of a virtual machine to a file in PNG format" (VERIFIED_PRIMARY, CLI reference p.21). It needs neither the guest network nor Parallels
Tools, so it is the first look at a wedged guest: a kernel panic, an initramfs or emergency shell, a GRUB prompt, a full disk message, or a login prompt that says the guest is up and only Tools are
not. It writes a local file and changes nothing in the VM. Save the PNG with the evidence of the run (redact addresses before it leaves the lab).

## Power: restart, reset, stop

| Command                         | What it does (CLI reference p.20)                            | Use when                       |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------ |
| `prlctl restart <vm>`           | graceful shutdown, then start                                | the guest answers              |
| `prlctl reset <vm>`             | "a 'hard' virtual machine shutdown and then starts it again" | the guest is wedged (captured) |
| `prlctl stop <vm>`              | graceful through Tools, else ACPI                            | normal stop                    |
| `prlctl stop <vm> --kill`       | hard stop                                                    | stop did not finish            |
| `prlctl stop <vm> --drop-state` | discard a suspended state, so the next start is a full boot  | a suspended VM must cold-boot  |

All are writes. A reset loses whatever the guest had not flushed; a lab that measures write behaviour reads its counters before a reset, not after.

## Parallels Tools

Parallels Tools provide exec, graceful shutdown, shared folders and time sync. vagrant-parallels checks the Tools version after boot and warns on a mismatch; `update_guest_tools = true` reinstalls
them on a mismatch (2 to 6 minutes, restarts the VM); `check_guest_tools = false` skips the check (VERIFIED_PRIMARY, [vp-configuration.md]). `outdated` Tools still served exec, capture and shutdown on
every lab VM on 2026-11-07 (observed); update them deliberately, not as a side effect of `vagrant up`, in a lab that compares runs.

## prlsrvctl

`prlsrvctl info` (host, version, licence), `prlsrvctl net list` / `net info <id>` / `net set <id>` with `--type <bridged | host-only | shared>` for the virtual networks (VERIFIED_PRIMARY, CLI
reference p.10 and [parallels-cli-utility.md]). Changing a Parallels network changes every VM on it: a write that needs the operator.

> **Learned 2026-11-07** · prlctl exec · VERIFIED_PRIMARY · Source: smc-resiliency spike/vm/sm/setup_sm.sh (`put`, `verity`), commit a41842e9 · Falsifier: a 10 KB script passed inline to `prlctl exec` that arrives intact
> A long inline argument to `prlctl exec` fails ("Unable to open new session") or arrives cut while short commands work; stream files over stdin instead and check the hash on the guest:
> ```bash
> put() { base64 < "$1" | timeout 60 prlctl exec "$VM" "bash -c 'base64 -d > $2 && chmod $3 $2'"; }
> ```
> After a reset or reboot Parallels Tools take tens of seconds to accept sessions: wait with `until timeout 8 prlctl exec "$VM" true; do sleep 3; done`.

> **Learned 2026-11-08** · Parallels Desktop on macOS, Ubuntu 24.04 arm64 guest · VERIFIED_PRIMARY · Source: smc-resiliency `lab/adapters/transports.py` `PrlctlTransport`, commit 065b9a8f · Falsifier: `prlctl exec <vm> bash -c 'echo a b'` printing `a b` with the command given as separate arguments
> `prlctl exec` joins its arguments into one command line, so `prlctl exec vm bash -c "cmd with words"` passed as separate argv entries runs
> `bash -c cmd`: the rest became bash's positional arguments and a payload ran as an empty shell, silently, exit 0. Pass one quoted string.
> Tools refuse sessions now and then, most right after a boot (`PrlJob_GetRetCode: Invalid argument`, `PrlJob_GetResult: Invalid argument`,
> exit 255): retry a few times. Files go over stdin (a long command line fails to open a session). A linked clone keeps the source's static
> hostname and machine-id, so it is told apart by its Parallels name only:
>
> ```python
> for _ in range(3):  # Tools refuses a session now and then, most right after a boot
>   rc, out = _call(["prlctl", "exec", self.name, "bash -c " + shlex.quote(cmd)], timeout)  # prlctl joins its arguments into one line
>   if not (rc == 255 and out.lstrip().startswith("Prl")):
>     return rc, out
>   time.sleep(3)
> ```
>
> Also on such a guest, when /etc is a read-only merge: `lvextend` fails with `Cannot archive volume group metadata ... to read-only filesystem`
> (rc 5) after printing that the size changed; `--config 'backup { archive = 0 backup = 0 }'` makes the one change.

