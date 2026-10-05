"""Read the devices registered in OpenWISP 1.3 by `hardware_id` and compare each with its source-of-truth record. Stdlib only, read-only.

Why (2026-09-22): in the engagement this was promoted from (2026-10-05), a scheduled poll and a manual run shared fixed local tunnel ports,
so one run could read a device through a tunnel opened to another. A registration fed that way carries another unit's MAC or address and
nothing else notices. Comparing every registered device with the inventory record its `hardware_id` names proves no record was corrupted;
run it after any incident that could mix identities, and after upgrades. MACs are compared normalised (`openwisp_identity.normalise_mac`):
OpenWISP may hold `AA-BB-CC-DD-EE-0F` where the inventory holds `aa:bb:cc:dd:ee:0f`.

`hardware_id` is not in the 1.3 REST serializers (references/operations-cookbook.md section 2), so the read is a server-side Django shell
program. The caller injects the I/O: a shell runner (`django_shell(container)` for docker-openwisp, or any callable with the same
signature) and a lookup returning the source-of-truth record for a hardware_id.

Usage:
    from openwisp_registry import django_shell, read_registered, find_mismatches, SourceRecord
    devices = read_registered(django_shell("<dashboard-container>"))
    mismatches = find_mismatches(devices, lambda hw: SourceRecord(name=..., macs={...}, management_ip=...))
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Callable, Iterable

from openwisp_identity import normalise_mac

#: Runs a Django shell program on the OpenWISP side: (program, stdin or None) -> the completed process with text output.
ShellRunner = Callable[[str, "str | None"], subprocess.CompletedProcess]

#: One `R <hardware_id> <mac or -> <management_ip or -> <name>` line per device that has a hardware_id.
REGISTERED_PROGRAM = """
from swapper import load_model
D = load_model('config', 'Device')
for d in D.objects.exclude(hardware_id__isnull=True).exclude(hardware_id=''):
    print('R', d.hardware_id, d.mac_address or '-', d.management_ip or '-', d.name)
"""


class RegistryReadError(RuntimeError):
    """The shell returned no registered device, which is never a valid answer from a populated deployment."""


def django_shell(container: str, timeout: int = 120) -> ShellRunner:
    """A runner for docker-openwisp: `docker exec -i <container> python manage.py shell -c <program>`, stdin passed through."""

    def run(program: str, stdin: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(["docker", "exec", "-i", container, "python", "manage.py", "shell", "-c", program],
                              input=stdin, capture_output=True, text=True, timeout=timeout)

    return run


@dataclass(frozen=True)
class RegisteredDevice:
    """One OpenWISP device as registered; `mac` and `management_ip` are None when OpenWISP holds none."""

    hardware_id: str
    mac: str | None
    management_ip: str | None
    name: str


@dataclass(frozen=True)
class SourceRecord:
    """The source of truth's view of the same unit: its name, every MAC it records (any notation) and its management IP."""

    name: str
    macs: frozenset = field(default_factory=frozenset)
    management_ip: str | None = None


def parse_registered(stdout: str) -> list[RegisteredDevice]:
    """The `R` lines of REGISTERED_PROGRAM's output; other lines (Django warnings) are ignored."""
    out = []
    for line in stdout.splitlines():
        if line.startswith("R "):
            _, hw, mac, ip, name = line.split(" ", 4)
            out.append(RegisteredDevice(hw, None if mac == "-" else mac, None if ip == "-" else ip, name))
    return out


def read_registered(runner: ShellRunner) -> list[RegisteredDevice]:
    """Every registered device; raises RegistryReadError, carrying the tail of the shell's output, when none is read."""
    out = runner(REGISTERED_PROGRAM, None)
    devices = parse_registered(out.stdout or "")
    if not devices:
        raise RegistryReadError(f"no registered OpenWISP devices read: {(out.stderr or out.stdout)[-200:]}")
    return devices


def compare(device: RegisteredDevice, record: SourceRecord, source: str = "source of truth") -> list[str]:
    """The differences between one registration and its record, worded with `source` (the source of truth's name).

    A record with no MAC or no management IP is not compared on that field; a registration with no management IP is not compared on it.
    """
    issues = []
    known = {normalise_mac(m) for m in record.macs}
    if known and normalise_mac(device.mac) not in known:
        issues.append(f"MAC {device.mac or '-'} is not one of {source}'s")
    if record.management_ip and device.management_ip is not None and device.management_ip != record.management_ip:
        issues.append(f"management IP {device.management_ip}, {source} {record.management_ip}")
    return issues


def find_mismatches(devices: Iterable[RegisteredDevice], lookup: Callable[[str], SourceRecord], source: str = "source of truth") -> list[str]:
    """`<record name>: <issue>; <issue>` for every device that differs, in the order read. Errors raised by `lookup` propagate."""
    bad = []
    for device in devices:
        record = lookup(device.hardware_id)
        issues = compare(device, record, source)
        if issues:
            bad.append(f"{record.name}: " + "; ".join(issues))
    return bad
