#!/usr/bin/env python3
"""Grow a VM's disk and then its partition and filesystem: AWS EBS, Proxmox VM or container, libvirt/QEMU, or an offline qemu-img image.

Usage: just disk-grow <platform> <options> [--check | --apply]
  (or: <venv python> scripts/disk_grow.py aws --volume-id vol-0abc --size 500 --type gp3 --guest-ssh 'ssh root@host' --apply)
Platforms: aws, proxmox-vm, proxmox-ct, libvirt, qemu-img. Sizes are whole GiB and absolute (the new total, never a delta).
Order for every platform: read the current state, snapshot (skip with --no-snapshot), grow the virtual disk, wait where the
platform is asynchronous (EBS), then run disk_grow_guest.sh in the guest (growpart + pvresize/lvextend + resize2fs/xfs_growfs/btrfs).
Safety: default prints the plan and runs nothing. --check runs only the read steps (describe/config and the guest script without
--apply). --apply runs every step in order and stops at the first failure. No platform here can shrink a disk: EBS, qm/pct resize,
virsh blockresize --extend and qemu-img resize (without --shrink) all refuse a smaller size. A production disk is a production write:
run --apply only on the operator's explicit go.
Runtime budget: each command 120 s; the guest grow 600 s; the EBS wait 900 s (it returns at "optimizing", when the new size is usable).
Exit 0: plan printed or all steps ran, 1: a step failed, 2: invalid arguments.
"""

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

GUEST_SCRIPT = Path(__file__).with_name("disk_grow_guest.sh")
CMD_TIMEOUT_S = 120
GUEST_TIMEOUT_S = 600
EBS_WAIT_S = 900
EBS_POLL_S = 15
MAX_GIB = 65536


@dataclass
class Step:
  """One ordered action of a grow plan.

  Attributes:
    what: Human description.
    argv: Command and arguments, already prefixed with the host transport.
    write: True when the step changes state (skipped by --check).
    kind: "cmd", "ebs-wait" (poll until the modification is usable) or "guest" (pipe the guest script on stdin).
  """

  what: str
  argv: list
  write: bool
  kind: str = "cmd"


def transport(prefix, argv):
  """Prefix a command with a host transport such as 'ssh root@pve1', or return it unchanged for local runs.

  Args:
    prefix: Transport command line, or empty for local.
    argv: Command to run on that host.
  Returns:
    The argv to execute locally.
  Raises:
    ValueError: When the prefix cannot be split.
  """
  if not prefix:
    return list(argv)
  return shlex.split(prefix) + [shlex.join(argv)]


def guest_step(guest_ssh, mount):
  """Build the in-guest grow step, or nothing when no guest transport was given.

  Args:
    guest_ssh: ssh-style transport to the guest as root ('ssh root@host', 'tsh ssh --proxy=p root@host'), or empty.
    mount: Mount point to grow.
  Returns:
    A list with the guest Step, or an empty list.
  Raises:
    ValueError: When the prefix cannot be split.
  """
  if not guest_ssh:
    return []
  remote = ["bash", "-s", "--", "--mount", mount]
  return [Step(f"grow partition and filesystem under {mount} in the guest", transport(guest_ssh, remote), True, "guest")]


def aws_plan(a):
  """Steps for an EBS volume: describe, snapshot, modify-volume, wait, guest grow.

  Args:
    a: Parsed arguments (volume_id, size, type, profile, region, snap_name, no_snapshot, guest_ssh, mount).
  Returns:
    Ordered list of Step.
  Raises:
    ValueError: When a transport cannot be split.
  """
  base = ["aws"] + (["--profile", a.profile] if a.profile else []) + (["--region", a.region] if a.region else []) + ["ec2"]
  steps = [
    Step(
      "read the volume (size, type, IOPS, attachment)",
      base + ["describe-volumes", "--volume-ids", a.volume_id, "--query", "Volumes[0].[Size,VolumeType,Iops,Throughput,State]", "--output", "text"],
      False,
    ),
    Step(
      "list earlier modifications (EBS allows a limited number per rolling 24 h)",
      base + ["describe-volumes-modifications", "--filters", f"Name=volume-id,Values={a.volume_id}", "--output", "text"],
      False,
    ),
  ]
  if not a.no_snapshot:
    tags = f"ResourceType=snapshot,Tags=[{{Key=Name,Value={a.snap_name}}}]"
    steps.append(
      Step(
        "snapshot the volume (point in time at initiation; the modify need not wait for it)",
        base + ["create-snapshot", "--volume-id", a.volume_id, "--description", a.snap_name, "--tag-specifications", tags],
        True,
      )
    )
  modify = base + ["modify-volume", "--volume-id", a.volume_id, "--size", str(a.size)] + (["--volume-type", a.type] if a.type else [])
  steps.append(Step(f"grow the volume to {a.size} GiB" + (f" and set type {a.type}" if a.type else ""), modify, True))
  steps.append(
    Step(
      "wait for the modification to reach optimizing or completed",
      base + ["describe-volumes-modifications", "--volume-ids", a.volume_id, "--query", "VolumesModifications[0].ModificationState", "--output", "text"],
      True,
      "ebs-wait",
    )
  )
  return steps + guest_step(a.guest_ssh, a.mount)


def proxmox_vm_plan(a):
  """Steps for a Proxmox QEMU VM disk: config, snapshot, qm disk resize, guest grow.

  Args:
    a: Parsed arguments (vmid, disk, size, host_ssh, snap_name, no_snapshot, guest_ssh, mount).
  Returns:
    Ordered list of Step.
  Raises:
    ValueError: When a transport cannot be split.
  """
  h = a.host_ssh
  steps = [Step(f"read VM {a.vmid} config (disk {a.disk} and its size)", transport(h, ["qm", "config", str(a.vmid), "--current", "1"]), False)]
  if not a.no_snapshot:
    steps.append(
      Step("snapshot the VM (needs snapshot-capable storage: ZFS, LVM-thin, Ceph, qcow2)", transport(h, ["qm", "snapshot", str(a.vmid), a.snap_name]), True)
    )
  steps.append(Step(f"grow {a.disk} to {a.size} GiB", transport(h, ["qm", "disk", "resize", str(a.vmid), a.disk, f"{a.size}G"]), True))
  return steps + guest_step(a.guest_ssh, a.mount)


def proxmox_ct_plan(a):
  """Steps for a Proxmox container mount point: config, snapshot, pct resize (which also grows the filesystem), df.

  Args:
    a: Parsed arguments (vmid, disk, size, host_ssh, snap_name, no_snapshot).
  Returns:
    Ordered list of Step.
  Raises:
    ValueError: When a transport cannot be split.
  """
  h = a.host_ssh
  steps = [Step(f"read CT {a.vmid} config", transport(h, ["pct", "config", str(a.vmid), "--current", "1"]), False)]
  if not a.no_snapshot:
    steps.append(Step("snapshot the container", transport(h, ["pct", "snapshot", str(a.vmid), a.snap_name]), True))
  steps.append(Step(f"grow {a.disk} to {a.size} GiB (pct grows the filesystem too)", transport(h, ["pct", "resize", str(a.vmid), a.disk, f"{a.size}G"]), True))
  steps.append(Step("show the container's filesystem size", transport(h, ["pct", "exec", str(a.vmid), "--", "df", "-hT", a.mount]), False))
  return steps


def libvirt_plan(a):
  """Steps for a running libvirt/QEMU domain: domblklist, internal snapshot, blockresize --extend, guest grow.

  Args:
    a: Parsed arguments (domain, target, size, host_ssh, snap_name, no_snapshot, guest_ssh, mount).
  Returns:
    Ordered list of Step.
  Raises:
    ValueError: When a transport cannot be split.
  """
  h = a.host_ssh
  steps = [Step(f"list {a.domain} disks (target names and images)", transport(h, ["virsh", "domblklist", a.domain, "--details"]), False)]
  if not a.no_snapshot:
    steps.append(
      Step(
        "internal snapshot (qcow2 only; for raw or LVM disks use --no-snapshot and a backup)",
        transport(h, ["virsh", "snapshot-create-as", a.domain, a.snap_name, "--atomic"]),
        True,
      )
    )
  steps.append(Step(f"grow {a.target} to {a.size} GiB", transport(h, ["virsh", "blockresize", a.domain, a.target, f"{a.size}G", "--extend"]), True))
  return steps + guest_step(a.guest_ssh, a.mount)


def qemu_img_plan(a):
  """Steps for an image of a stopped VM: info, internal snapshot, qemu-img resize; the guest grow runs after the next boot.

  Args:
    a: Parsed arguments (image, size, host_ssh, snap_name, no_snapshot, guest_ssh, mount).
  Returns:
    Ordered list of Step.
  Raises:
    ValueError: When a transport cannot be split.
  """
  h = a.host_ssh
  steps = [Step("read the image (format, virtual size, snapshots); the VM must be stopped", transport(h, ["qemu-img", "info", a.image]), False)]
  if not a.no_snapshot:
    steps.append(Step("internal snapshot (qcow2 only)", transport(h, ["qemu-img", "snapshot", "-c", a.snap_name, a.image]), True))
  steps.append(Step(f"grow the image to {a.size} GiB", transport(h, ["qemu-img", "resize", a.image, f"{a.size}G"]), True))
  return steps + guest_step(a.guest_ssh, a.mount)


PLANS = {"aws": aws_plan, "proxmox-vm": proxmox_vm_plan, "proxmox-ct": proxmox_ct_plan, "libvirt": libvirt_plan, "qemu-img": qemu_img_plan}


def parse_args(argv):
  """Parse the platform subcommand and its options.

  Args:
    argv: Command-line arguments without the program name.
  Returns:
    argparse.Namespace.
  Raises:
    SystemExit: Exit 2 on invalid arguments.
  """
  p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  sub = p.add_subparsers(dest="platform", required=True)

  def common(sp, guest=True):
    """Add the size, snapshot, mount, guest and mode options shared by every platform.

    Args:
      sp: Subparser to extend.
      guest: Whether the platform has an in-guest grow step.
    Returns:
      None.
    Raises:
      None.
    """
    sp.add_argument("--size", type=int, required=True, help="new total size in GiB")
    sp.add_argument("--snap-name", default="", help="snapshot name (default: pre-grow-<size>g-<yyyymmdd>)")
    sp.add_argument("--no-snapshot", action="store_true", help="skip the snapshot (only with a tested backup)")
    sp.add_argument("--mount", default="/", help="mount point to grow in the guest (default /)")
    if guest:
      sp.add_argument("--guest-ssh", default="", help="transport to the guest as root, e.g. 'ssh root@host'; empty skips the guest step")
    mode = sp.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="run only the read steps")
    mode.add_argument("--apply", action="store_true", help="run every step")

  def host(sp):
    """Add the hypervisor host transport option.

    Args:
      sp: Subparser to extend.
    Returns:
      None.
    Raises:
      None.
    """
    sp.add_argument("--host-ssh", default="", help="transport to the hypervisor host, e.g. 'ssh root@pve1'; empty runs locally")

  sp = sub.add_parser("aws", help="EBS volume")
  sp.add_argument("--volume-id", required=True)
  sp.add_argument("--type", default="", help="new volume type, e.g. gp3 (omit to keep)")
  sp.add_argument("--profile", default="")
  sp.add_argument("--region", default="")
  common(sp)
  sp = sub.add_parser("proxmox-vm", help="Proxmox QEMU VM disk")
  sp.add_argument("--vmid", type=int, required=True)
  sp.add_argument("--disk", required=True, help="e.g. scsi0, virtio0")
  host(sp)
  common(sp)
  sp = sub.add_parser("proxmox-ct", help="Proxmox LXC mount point")
  sp.add_argument("--vmid", type=int, required=True)
  sp.add_argument("--disk", default="rootfs", help="rootfs or mpN")
  host(sp)
  common(sp, guest=False)
  sp = sub.add_parser("libvirt", help="running libvirt/QEMU domain")
  sp.add_argument("--domain", required=True)
  sp.add_argument("--target", required=True, help="disk target from virsh domblklist, e.g. vda")
  host(sp)
  common(sp)
  sp = sub.add_parser("qemu-img", help="image of a stopped VM")
  sp.add_argument("--image", required=True)
  host(sp)
  common(sp)

  a = p.parse_args(argv)
  if not 1 <= a.size <= MAX_GIB:
    p.error(f"--size must be 1..{MAX_GIB} GiB")
  if not a.snap_name:
    a.snap_name = f"pre-grow-{a.size}g-{time.strftime('%Y%m%d')}"
  return a


def run_cmd(argv, stdin_path=None, timeout=CMD_TIMEOUT_S):
  """Run one command, streaming its output, with a timeout.

  Args:
    argv: Command to run.
    stdin_path: File fed on standard input, or None.
    timeout: Seconds before the command is killed.
  Returns:
    Pair of (exit status, captured stdout text).
  Raises:
    None: a timeout or missing program is returned as status 1.
  """
  try:
    if stdin_path:
      with open(stdin_path, "rb") as fh:
        res = subprocess.run(argv, stdin=fh, capture_output=True, timeout=timeout, check=False)
    else:
      res = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout, check=False)
  except (subprocess.TimeoutExpired, OSError) as exc:
    print(f"  ! {exc}", file=sys.stderr)
    return 1, ""
  out = res.stdout.decode(errors="replace")
  sys.stdout.write(out)
  sys.stdout.flush()
  sys.stderr.write(res.stderr.decode(errors="replace"))
  return res.returncode, out


def ebs_wait(argv):
  """Poll an EBS modification until it is usable (optimizing or completed).

  Args:
    argv: describe-volumes-modifications command that prints the state.
  Returns:
    0 when usable, 1 on failure or timeout.
  Raises:
    None.
  """
  deadline = time.monotonic() + EBS_WAIT_S
  while time.monotonic() < deadline:
    rc, out = run_cmd(argv)
    state = out.strip()
    if rc != 0 or state == "failed":
      return 1
    if state in ("optimizing", "completed"):
      return 0
    time.sleep(EBS_POLL_S)
  print(f"  ! modification not usable after {EBS_WAIT_S} s", file=sys.stderr)
  return 1


def execute(steps, mode):
  """Print or run the plan.

  Args:
    steps: Ordered Step list.
    mode: "plan", "check" or "apply".
  Returns:
    Exit status: 0 ok, 1 a step failed.
  Raises:
    None.
  """
  started = time.monotonic()
  for n, s in enumerate(steps, 1):
    tag = "WRITE" if s.write else "read"
    argv = list(s.argv)
    if s.kind == "guest":
      argv[-1] += " --apply" if mode == "apply" else ""
      tag = "WRITE" if mode == "apply" else "read"
    print(f"[{n}/{len(steps)}] {tag}: {s.what}\n  $ {shlex.join(argv)}" + (f" < {GUEST_SCRIPT.name}" if s.kind == "guest" else ""), flush=True)
    if mode == "plan" or (mode == "check" and s.write and s.kind != "guest"):
      continue
    if s.kind == "ebs-wait":
      rc = ebs_wait(argv)
    elif s.kind == "guest":
      rc, _ = run_cmd(argv, GUEST_SCRIPT, GUEST_TIMEOUT_S)
    else:
      rc, _ = run_cmd(argv)
    if rc != 0:
      print(f"step {n} failed (exit {rc}); later steps not run", file=sys.stderr)
      return 1
  if mode != "plan":
    print(json.dumps({"mode": mode, "steps": len(steps), "runtime_s": round(time.monotonic() - started, 1)}))
  return 0


def main(argv=None):
  """Build the plan for the chosen platform and print, check or apply it.

  Args:
    argv: Arguments without the program name; None reads sys.argv.
  Returns:
    Exit status.
  Raises:
    SystemExit: From argparse on invalid arguments.
  """
  a = parse_args(sys.argv[1:] if argv is None else argv)
  try:
    steps = PLANS[a.platform](a)
  except ValueError as exc:
    print(f"invalid transport: {exc}", file=sys.stderr)
    return 2
  mode = "apply" if a.apply else "check" if a.check else "plan"
  return execute(steps, mode)


if __name__ == "__main__":
  sys.exit(main())
