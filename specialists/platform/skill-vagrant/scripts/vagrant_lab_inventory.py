#!/usr/bin/env python3
"""Read-only inventory of a local Vagrant lab: machines, Parallels and VirtualBox VMs, linked clones, Tools state, boxes and pins.

Why: a lab session starts by knowing what exists, which VM is a linked clone of which, and whether each box pin is installed and current;
`vagrant global-status` is a cache and names no machines, `prlctl list` knows nothing about Vagrantfiles. Promoted from the 2026-11-07
smc-resiliency lab work (skill-vagrant, operator 2026-11-07).

Usage:
  vagrant_lab_inventory.py [--json] [--latest] [--no-edition]
    --json        one JSON document instead of tables
    --latest      also ask the public box registry for each pinned box's newest version (network, 20 s per box)
    --no-edition  skip `prlsrvctl info --license --json` (only `edition` and `status` are ever read from it)

Safety: read-only. It runs `vagrant global-status --machine-readable`, `vagrant box list --machine-readable`, `prlctl list -a -i -j`,
`VBoxManage list vms`, `VBoxManage list runningvms` and `prlsrvctl info --license --json`, each under a deadline, reads Vagrantfiles and
`.vagrant/machines/*/<provider>/id` files (parallels, virtualbox, qemu, libvirt), and changes no VM. The vagrant commands are required; a
hypervisor CLI that is missing or fails is reported as unavailable (2026-11-09: one Mac runs four providers, not every Mac runs all).
Runtime budget: 5 s without --latest on a 20-VM lab (measured 2026-11-07: about 1.5 s; 2026-11-09 with VirtualBox listed: 2 s).
Exit: 0 report printed; 1 a required command failed; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: Seconds any one vagrant or prlctl call may take.
CALL_TIMEOUT_S = 60
#: Seconds one registry request may take.
HTTP_TIMEOUT_S = 20
#: Box registry API; {name} is "<user>/<box>".
REGISTRY_URL = "https://vagrantcloud.com/api/v2/box/{name}"

#: Provider folders under .vagrant/machines/<name>/ whose `id` file names the VM.
PROVIDERS = ("parallels", "virtualbox", "qemu", "libvirt")

Runner = Callable[[list[str]], str]


class InventoryError(RuntimeError):
  """A required read-only command failed or returned output this script cannot parse."""


@dataclass
class Machine:
  """One Vagrant environment row from global-status, joined to its Vagrantfile and Parallels VM."""

  machine_id: str
  provider: str
  home: str
  state: str
  names: list[str] = field(default_factory=list)
  vm_uuids: dict[str, str] = field(default_factory=dict)
  vm_providers: dict[str, str] = field(default_factory=dict)
  boxes: list[tuple[str, str]] = field(default_factory=list)


def run_command(argv: list[str]) -> str:
  """Run one read-only command under the call deadline.

  Args:
    argv: the command and its arguments.

  Returns:
    Its standard output.

  Raises:
    InventoryError: when it is missing, exits non-zero or passes the deadline.
  """
  try:
    done = subprocess.run(argv, capture_output=True, text=True, timeout=CALL_TIMEOUT_S, check=False)
  except (OSError, subprocess.TimeoutExpired) as exc:
    raise InventoryError(f"{argv[0]}: {exc}") from exc
  if done.returncode != 0:
    raise InventoryError(f"{' '.join(argv)} exited {done.returncode}: {done.stderr.strip()[:200]}")
  return done.stdout


def machine_readable(text: str) -> list[tuple[str, list[str]]]:
  """Split Vagrant's --machine-readable output into (type, data fields), unescaping commas and newlines.

  Args:
    text: the command's output.

  Returns:
    One (type, fields) pair per line that has a type.
  """
  rows = []
  for line in text.splitlines():
    parts = line.split(",")
    if len(parts) < 3:
      continue
    data = [p.replace("%!(VAGRANT_COMMA)", ",").replace("\\n", "\n") for p in parts[3:]]
    rows.append((parts[2], data))
  return rows


def parse_global_status(text: str) -> list[Machine]:
  """Machines from `vagrant global-status --machine-readable` (machine-id, provider-name, machine-home, state groups).

  Args:
    text: the command's output.

  Returns:
    One Machine per environment, in output order.
  """
  machines: list[Machine] = []
  current: dict[str, str] = {}
  keys = {"machine-id": "machine_id", "provider-name": "provider", "machine-home": "home", "state": "state"}
  for kind, data in machine_readable(text):
    if kind not in keys:
      continue
    if kind == "machine-id" and current:
      machines.append(Machine(**{**dict.fromkeys(keys.values(), ""), **current}))
      current = {}
    current[keys[kind]] = data[0] if data else ""
  if current:
    machines.append(Machine(**{**dict.fromkeys(keys.values(), ""), **current}))
  return machines


def parse_box_list(text: str) -> list[dict[str, str]]:
  """Installed boxes from `vagrant box list --machine-readable`.

  Args:
    text: the command's output.

  Returns:
    Dicts with name, provider, version and architecture.
  """
  boxes: list[dict[str, str]] = []
  keys = {"box-name": "name", "box-provider": "provider", "box-version": "version", "box-architecture": "architecture"}
  for kind, data in machine_readable(text):
    if kind not in keys:
      continue
    if kind == "box-name":
      boxes.append({})
    if boxes:
      boxes[-1][keys[kind]] = data[0] if data else ""
  return boxes


def parse_vms(text: str) -> list[dict[str, object]]:
  """Parallels VMs from `prlctl list -a -i -j`: name, uuid, state, parent, Tools state and network adapters.

  Args:
    text: the JSON the command printed.

  Returns:
    One dict per VM.

  Raises:
    InventoryError: when the output is not a JSON list.
  """
  try:
    raw = json.loads(text)
  except json.JSONDecodeError as exc:
    raise InventoryError(f"prlctl list -a -i -j: not JSON ({exc})") from exc
  match raw:
    case list():
      pass
    case _:
      raise InventoryError("prlctl list -a -i -j: expected a JSON list")
  vms = []
  for vm in raw:
    hardware = vm.get("Hardware") or {}
    nets = {k: f"{v.get('type', '?')}/{v.get('state', 'connected')}" for k, v in hardware.items() if re.fullmatch(r"net\d+", k)}
    vms.append(
      {
        "name": vm.get("Name", ""),
        "uuid": str(vm.get("ID", "")).strip("{}"),
        "state": vm.get("State", ""),
        "parent": vm.get("Parent VM") or "",
        "tools": (vm.get("GuestTools") or {}).get("state", ""),
        "nets": nets,
      }
    )
  return vms


def parse_vbox_vms(listing: str, running: str) -> list[dict[str, object]]:
  """VirtualBox VMs from `VBoxManage list vms` and `VBoxManage list runningvms`: name, uuid and running or not.

  Args:
    listing: output of `VBoxManage list vms` (lines `"name" {uuid}`).
    running: output of `VBoxManage list runningvms`, same shape.

  Returns:
    One dict per VM, in listing order; lines of another shape are skipped.
  """
  line = re.compile(r'^"(?P<name>.*)" \{(?P<uuid>[0-9a-fA-F-]+)\}\s*$')
  up = {m.group("uuid") for m in map(line.match, running.splitlines()) if m}
  vms = []
  for found in map(line.match, listing.splitlines()):
    if found:
      uuid = found.group("uuid")
      vms.append({"name": found.group("name"), "uuid": uuid, "state": "running" if uuid in up else "not running"})
  return vms


def optional(run: Runner, argv: list[str]) -> tuple[str, str]:
  """Run a hypervisor CLI that may be absent on this Mac.

  Args:
    run: the command runner.
    argv: the read-only command.

  Returns:
    (output, "ok"), or ("", "unavailable: <reason>") when the command is missing or fails.
  """
  try:
    return run(argv), "ok"
  except InventoryError as exc:
    return "", f"unavailable: {str(exc)[:120]}"


def vagrantfile_boxes(text: str) -> list[tuple[str, str]]:
  """(box, box_version) pairs written as literals in a Vagrantfile; a missing version is "" and a computed one "?".

  Args:
    text: the Vagrantfile.

  Returns:
    One pair per `vm.box =` assignment, in file order.
  """
  pairs = []
  lines = [ln.split("#", 1)[0] for ln in text.splitlines()]
  for i, line in enumerate(lines):
    box = re.search(r"\.vm\.box\s*=\s*(\S.*)$", line)
    if not box:
      continue
    name = box.group(1).strip().strip("\"'") if re.fullmatch(r"\s*[\"'][^\"']+[\"']\s*", box.group(1)) else "?"
    version = ""
    for other in lines[i : i + 6]:
      found = re.search(r"\.vm\.box_version\s*=\s*(\S.*)$", other)
      if found:
        literal = re.fullmatch(r"\s*[\"']([^\"']+)[\"']\s*", found.group(1))
        version = literal.group(1) if literal else "?"
        break
    pairs.append((name, version))
  return pairs


def attach_homes(machines: list[Machine]) -> None:
  """Fill each machine's Vagrantfile box pins and its provider VM ids from its home folder (read-only).

  Args:
    machines: rows from parse_global_status; changed in place.

  Returns:
    None.
  """
  for m in machines:
    home = Path(m.home)
    vagrantfile = home / "Vagrantfile"
    if vagrantfile.is_file():
      m.boxes = vagrantfile_boxes(vagrantfile.read_text(encoding="utf-8", errors="replace"))
    for id_file in sorted(home.glob(".vagrant/machines/*/*/id")):
      provider = id_file.parent.name
      if provider not in PROVIDERS:
        continue
      name = id_file.parent.parent.name
      m.names.append(name)
      m.vm_uuids[name] = id_file.read_text(encoding="utf-8").strip().strip("{}")
      m.vm_providers[name] = provider


def latest_version(name: str, fetch: Callable[[str], bytes] | None = None) -> str:
  """The newest active version of a registry box, or "" when it cannot be read.

  Args:
    name: "<user>/<box>".
    fetch: callable returning the response body for a URL (default: urllib with HTTP_TIMEOUT_S).

  Returns:
    The version string, or "" on any failure.
  """

  def _get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_S) as response:
      return response.read()

  try:
    body = json.loads((fetch or _get)(REGISTRY_URL.format(name=name)))
  except (OSError, ValueError):
    return ""
  current = body.get("current_version") or {}
  return str(current.get("version", ""))


def edition(run: Runner) -> str:
  """Parallels Desktop edition and licence status, never the key.

  Args:
    run: the command runner.

  Returns:
    "edition/status", or "unknown" when prlsrvctl cannot be read.
  """
  try:
    data = json.loads(run(["prlsrvctl", "info", "--license", "--json"]))
  except (InventoryError, ValueError):
    return "unknown"
  return f"{data.get('edition', '?')}/{data.get('status', '?')}"


def collect(run: Runner, want_latest: bool, want_edition: bool, fetch: Callable[[str], bytes] | None = None) -> dict[str, object]:
  """Gather the whole inventory.

  Args:
    run: the command runner (run_command, or a fake in tests).
    want_latest: also ask the registry for each pinned box's newest version.
    want_edition: read the Parallels edition.
    fetch: optional URL fetcher passed to latest_version.

  Returns:
    A dict with machines, vms (Parallels), vbox_vms, hypervisors (CLI status), boxes, pins and edition.

  Raises:
    InventoryError: when a required vagrant command fails.
  """
  machines = parse_global_status(run(["vagrant", "global-status", "--machine-readable"]))
  attach_homes(machines)
  boxes = parse_box_list(run(["vagrant", "box", "list", "--machine-readable"]))
  prl_out, prl_status = optional(run, ["prlctl", "list", "-a", "-i", "-j"])
  vms = parse_vms(prl_out) if prl_out else []
  vbox_out, vbox_status = optional(run, ["VBoxManage", "list", "vms"])
  running_out, _ = optional(run, ["VBoxManage", "list", "runningvms"]) if vbox_out else ("", "")
  vbox_vms = parse_vbox_vms(vbox_out, running_out)
  installed = {(b.get("name"), b.get("version")) for b in boxes}
  pins = []
  newest: dict[str, str] = {}
  for name, version in sorted({pair for m in machines for pair in m.boxes}):
    have = (name, version) in installed if version else any(n == name for n, _ in installed)
    row = {"box": name, "pin": version or "(none)", "installed": have}
    if want_latest and name not in ("", "?"):
      if name not in newest:
        newest[name] = latest_version(name, fetch)
      row["latest"] = newest[name]
    pins.append(row)
  return {
    "edition": edition(run) if want_edition else "skipped",
    "machines": [asdict(m) for m in machines],
    "vms": vms,
    "vbox_vms": vbox_vms,
    "hypervisors": {"parallels": prl_status, "virtualbox": vbox_status},
    "boxes": boxes,
    "pins": pins,
  }


def vm_name(provider: str, vm_id: str, by_uuid: dict[str, dict[str, object]]) -> str:
  """The hypervisor's name for a Vagrant machine's VM id.

  Args:
    provider: the provider folder the id came from.
    vm_id: the id from `.vagrant/machines/<m>/<provider>/id`.
    by_uuid: Parallels and VirtualBox VMs by uuid.

  Returns:
    The VM name; "not registered" for a listed provider without that VM; "qemu id <id>" or "libvirt id <id>" for providers
    this script does not list.
  """
  if provider in ("qemu", "libvirt"):
    return f"{provider} id {vm_id}"
  return str(by_uuid.get(vm_id, {}).get("name", "not registered"))


def report(inv: dict[str, object]) -> list[str]:
  """Plain-text tables for a person.

  Args:
    inv: the result of collect().

  Returns:
    Output lines.
  """
  by_uuid = {vm["uuid"]: vm for vm in [*inv["vms"], *inv["vbox_vms"]]}
  status = ", ".join(f"{k} {v}" for k, v in inv["hypervisors"].items())
  lines = [f"Hypervisor CLIs: {status}", f"Parallels edition/status: {inv['edition']}", "", "VMS (prlctl): name | state | linked clone of | tools | adapters"]
  for vm in sorted(inv["vms"], key=lambda v: v["name"]):
    nets = " ".join(f"{k}={v}" for k, v in sorted(vm["nets"].items())) or "-"
    lines.append(f"  {vm['name']} | {vm['state']} | {vm['parent'] or '-'} | {vm['tools'] or '-'} | {nets}")
  lines += ["", "VMS (VBoxManage): name | state"]
  for vm in sorted(inv["vbox_vms"], key=lambda v: v["name"]):
    lines.append(f"  {vm['name']} | {vm['state']}")
  lines += ["", "VAGRANT ENVIRONMENTS (global-status cache, one row per folder): home | states | machine (provider) -> VM | box pins"]
  seen: dict[str, list[str]] = {}
  for m in inv["machines"]:
    seen.setdefault(m["home"], []).append(m["state"])
  for m in inv["machines"]:
    if m["home"] not in seen:
      continue
    states = ",".join(seen.pop(m["home"]))
    named = ", ".join(f"{n} ({m['vm_providers'].get(n, '?')})->{vm_name(m['vm_providers'].get(n, ''), u, by_uuid)}" for n, u in m["vm_uuids"].items()) or "-"
    pins = ", ".join(f"{b}@{v or 'UNPINNED'}" for b, v in m["boxes"]) or "-"
    lines.append(f"  {m['home']} | {states} | {named} | {pins}")
  lines += ["", "BOX PINS: box | pinned | installed | latest"]
  for p in inv["pins"]:
    lines.append(f"  {p['box']} | {p['pin']} | {'yes' if p['installed'] else 'NO'} | {p.get('latest', '-') or 'unknown'}")
  return lines


def main(argv: list[str] | None = None, run: Runner = run_command) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).
    run: the command runner (tests pass a fake).

  Returns:
    0 on success, 1 when a required command failed, 2 on bad arguments (argparse exits).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("--json", action="store_true", help="print JSON")
  ap.add_argument("--latest", action="store_true", help="ask the box registry for newer versions (network)")
  ap.add_argument("--no-edition", action="store_true", help="skip reading the Parallels edition")
  args = ap.parse_args(argv)
  try:
    inv = collect(run, args.latest, not args.no_edition)
  except InventoryError as exc:
    print(f"inventory failed: {exc}", file=sys.stderr)
    return 1
  print(json.dumps(inv, indent=2) if args.json else "\n".join(report(inv)))
  return 0


if __name__ == "__main__":
  sys.exit(main())
