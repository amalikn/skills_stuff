---
Title: Lab safety and guards
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Rules for lab drivers: plan by default and --apply, an in-guest wrong-VM marker, deadlines and keepalives, quoting once, hash what arrived, disk fill, host guards, Vagrantfile copy checks.
---

# Lab safety and guards

Rules for scripts that drive lab VMs from the Mac. They follow skill-coder (plan by default, `--apply` for writes, a deadline on every call) and add what a VM lab needs: proof that the command reached
the intended VM, and a canonical Vagrantfile that the project copy cannot drift from.

## Contents

- [Plan by default, write with --apply](#plan-by-default-write-with---apply)
- [Refuse the wrong VM](#refuse-the-wrong-vm)
- [A deadline on every call](#a-deadline-on-every-call)
- [Quote the remote command once](#quote-the-remote-command-once)
- [Prove what arrived](#prove-what-arrived)
- [Filling a disk on purpose](#filling-a-disk-on-purpose)
- [Host guards](#host-guards)
- [Keep a project copy of the canonical Vagrantfile](#keep-a-project-copy-of-the-canonical-vagrantfile)

## Plan by default, write with --apply

A lab driver prints what it would do and exits 0 unless `--apply` is given; the VM name is fixed in the script, never taken from an argument that could name a site; the header says "Lab only" and what
each action writes (smc-resiliency `spike/to_vm.sh` @ 4e436e8d: "Without --apply it prints the plan and changes nothing. Lab only: the VM's name is fixed here; never point it at a site.").

## Refuse the wrong VM

A name or an address is not proof of which VM answered: a linked clone that shares the machine-id can take the original's DHCP lease, and then `vagrant ssh <original>` reaches the clone
([clones-snapshots-and-identity.md](clones-snapshots-and-identity.md#machine-id)). Put a marker on the VM that must never be touched (or on the one that must), and test it inside the same remote command before anything else runs:

```bash
# smc-resiliency spike/to_vm.sh @ 4e436e8d: the SM clone carries /boot/smc-ramcow-installed; the spike VM does not
on_vm() { (cd "$VD" && vagrant ssh "$VM" -c "sudo bash -c $(printf %q "test ! -e /boot/smc-ramcow-installed || { echo \"refused: reached the SM clone, not the intended VM\" >&2; exit 97; }; $1")" "${SSH_OPTS[@]}"); }
```

The check runs in the guest, in the same shell as the command, so no race between "check" and "do" remains; a distinct exit code (97) lets callers tell a refusal from a failed command. Better still,
give each VM an identity file written at creation (`/etc/lab-role` with the VM name) and compare it with the name the script means.

```text
 driver.sh [--apply]                      VM name fixed in the script, never an argument
   ├─ no --apply ─► print the plan, exit 0
   └─ --apply
        ├─ host guards: free disk ≥ 8 GiB?  name matches?  ─► else refuse, exit non-zero
        └─ timeout N vagrant ssh <vm> -c "<marker test>; <command>" -- -o ConnectTimeout=15 ...
              one shell, inside the guest:
              ├─ marker says "wrong VM" ─► exit 97 (refused; nothing ran)
              └─ marker OK ───────────► run the command ─► its own exit code
```

## A deadline on every call

Every `vagrant`, `prlctl` and `ssh` call has a deadline: `timeout N` in shell, `timeout=` in Python's `subprocess.run`. `vagrant ssh` also gets SSH keepalives, so a dead guest ends the session instead
of hanging it:

```bash
SSH_OPTS=(-- -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)   # to_vm.sh @ 4e436e8d
```

Write `timeout` and its duration as separate words. A wrapper that read `timeout 30"cmd"` failed with "invalid time interval" (USER_STATED, lab 2026-11-07): `30"cmd"` is one word, so `timeout`
received `30cmd` as its duration. `scripts/vagrantfile_lint.py` does not see wrapper scripts; shellcheck and skill-coder's `call_timeouts.py` do, and a test that runs the wrapper once in plan mode
catches it.

## Quote the remote command once

`vagrant ssh -c` and `prlctl exec` each take the remote command as one string. Build it with `printf %q` (bash) or `shlex.quote` (Python) from the exact command, and never splice untrusted text into
it. Large files go over stdin (`base64 < file | prlctl exec vm "bash -c 'base64 -d > path'"`) or `vagrant upload`, not inside the command string.

## Prove what arrived

After copying code into a guest, compare a hash of what is there with the local one and stop on a mismatch (to_vm.sh `install` hashes the sorted `*.py` on both sides). `vagrant upload` into an
existing directory delivered stale files once; upload to a new path per run and move it into place.

## Filling a disk on purpose

Tests that fill a filesystem write with `head -c <N>M /dev/urandom >> <file>` in a loop, inside a transient unit so it survives the session:

```bash
# smc-resiliency spike/vm/sm/setup_sm.sh @ 2402b961 (exhaust: acceptance test A11)
onvm 30 "systemd-run --unit=smc-sm-fill --description='SM exhaustion fill (A11)' bash -c 'for i in \$(seq 1 $(( M / 10 ))); do head -c 10M /dev/urandom >> /var/tmp/smc-fill; sync; sleep 0.1; done'; uptime -s"
```

A hook in the operator's agent environment blocks `dd` (USER_STATED, 2026-11-07), so lab fill scripts use `head -c`. It also sets the rate by chunk size and sleep, and a stop is `systemctl stop
<unit>`.

## Host guards

- Refuse to create a clone or a large disk when the Mac's data volume is short of space (`setup_sm.sh` `disk_guard`: under 8 GiB free).
- Never run a lab driver against a VM whose name does not match the script's fixed name; never accept `--vm` from the command line in a driver that writes.
- Keep secrets out of Vagrantfiles and drivers: no tokens, passwords or private keys; a box registry token comes from the environment at run time.

## Keep a project copy of the canonical Vagrantfile

The canonical Vagrantfile lives in the Vagrant workspace (`vagrant_stuff/<lab>/Vagrantfile`); the project that depends on the lab keeps a copy (never the keys) and a check that fails when the copy is
missing or differs (operator, 2026-10-21: "for the Vagrant files always keep a copy locally as well"; USER_STATED). The project's check:

```python
# smc-resiliency scripts/govcheck/checks/paths.py @ a124c13a
def check_vagrant_copies() -> None:
  """Each Vagrantfile the lab runs on has a copy in the project, equal to its canonical file in vagrant_stuff (skipped when that is absent)."""
  for copy, canonical in VAGRANT_COPIES.items():
    counted()
    local = ROOT / copy
    if not local.is_file():
      fail("vagrant", f"{copy} is missing: copy it from {canonical}")
      continue
    source = Path(canonical)
    if source.is_file() and source.read_bytes() != local.read_bytes():
      fail("vagrant", f"{copy} differs from {canonical}: copy the canonical file over it")
```

(Indentation normalised to two spaces in this excerpt.) The generic form is `scripts/vagrant_copy_check.py` in this pack: `just copy-check <copy>=<canonical> ...` exits 1 when a copy is missing or
differs, and says which. The direction of a fix is always canonical to copy; a change made in the copy is moved to the canonical file first.
