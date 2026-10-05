"""Mirror OpenWISP 1.3 device health into a source of truth's fields, writing only what changed. Stdlib only; plans, never writes.

Why (2026-09-22, promoted 2026-10-05): an engagement wanted OpenWISP's health visible on each inventory record, refreshed hourly, without
touching the inventory's own status (that stays the record's intent). Writing every device every hour would add about 72,000 change-log
entries a day at fleet size, so only a device whose health changed is written, together with a "synced" timestamp that then reads
"health since". A record that still carries a health value but is no longer registered in OpenWISP has both fields cleared: empty means
"not monitored".

Health is DeviceMonitoring's status (ok, problem, critical, unknown, deactivated; a device with no monitoring row reads `unknown`), read
server-side by `hardware_id` because the 1.3 REST serializers do not expose that field. Field names are the caller's; so are the reads and
the write: `plan_mirror` returns a bulk PATCH body (`[{"id", "custom_fields"}]`) and the caller applies it, or does not on a dry run.

Usage:
    from openwisp_registry import django_shell
    from openwisp_health_mirror import read_health, plan_mirror
    wanted = read_health(django_shell("<dashboard-container>"))           # {record id: health}
    plan = plan_mirror(wanted, current, "health_field", "synced_field", now_iso)
    print(plan.summary(now_iso)); body = plan.patch_body()               # caller PATCHes body when not a dry run
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

from openwisp_identity import from_hardware_id
from openwisp_registry import ShellRunner

#: One `H <hardware_id> <health>` line per device that has a hardware_id.
HEALTH_PROGRAM = """
from swapper import load_model
Device = load_model('config', 'Device')
for hw, status in Device.objects.exclude(hardware_id__isnull=True).exclude(hardware_id='').values_list('hardware_id', 'monitoring__status'):
    print('H', hw, status or 'unknown')
"""


class HealthReadError(RuntimeError):
    """The shell failed and returned no health at all."""


def read_health(runner: ShellRunner, key: Callable[[str], str] = from_hardware_id) -> dict[str, str]:
    """{record id: health} for every registered device; `key` turns a hardware_id into the record id (default: the dashed UUID).

    A failing shell that still printed health lines is accepted (Django can exit non-zero on teardown); one that printed none raises.
    """
    out = runner(HEALTH_PROGRAM, None)
    health = {key(line.split()[1]): line.split()[2] for line in (out.stdout or "").splitlines() if line.startswith("H ")}
    if out.returncode != 0 and not health:
        raise HealthReadError(f"could not read OpenWISP health: {(out.stderr or out.stdout)[-300:]}")
    return health


@dataclass
class MirrorPlan:
    """What a mirror run would write: `changes` (health changed or new) and `cleared` (no longer registered), both PATCH items."""

    wanted: dict[str, str]
    current: dict[str, str | None]
    changes: list[dict] = field(default_factory=list)
    cleared: list[dict] = field(default_factory=list)
    health_field: str = "health"

    def counts(self) -> dict[str, int]:
        """Registered devices per health value, keys sorted."""
        values = list(self.wanted.values())
        return {h: values.count(h) for h in sorted(set(values))}

    def summary(self, now: str) -> str:
        return (f"{now} registered={len(self.wanted)} {json.dumps(self.counts())} "
                f"changed={len(self.changes)} cleared={len(self.cleared)}")

    def change_lines(self) -> list[str]:
        """`  <id>: <old or -> -> <new>` per change, in the order planned."""
        return [f"  {c['id']}: {self.current.get(c['id']) or '-'} -> {c['custom_fields'][self.health_field]}" for c in self.changes]

    def patch_body(self) -> list[dict]:
        """The bulk PATCH body: changes, then clears. Empty when there is nothing to write."""
        return self.changes + self.cleared


def plan_mirror(wanted: dict[str, str], current: dict[str, str | None], health_field: str, synced_field: str, now: str) -> MirrorPlan:
    """Plan the writes. `wanted` is OpenWISP's {record id: health}; `current` is {record id: mirrored health} for every record that
    carries one. A record is written when its mirrored value differs (health + synced = `now`), cleared (both None) when unregistered."""
    changes = [{"id": rid, "custom_fields": {health_field: h, synced_field: now}} for rid, h in wanted.items() if current.get(rid) != h]
    cleared = [{"id": rid, "custom_fields": {health_field: None, synced_field: None}} for rid in current if rid not in wanted]
    return MirrorPlan(wanted, current, changes, cleared, health_field)
