"""Converge OpenWISP 1.3 AlertSettings on a declared policy: per-metric defaults plus per-class overrides. Stdlib only; dry run unless told.

Why (2026-09-26, promoted 2026-10-05): an engagement needed alert thresholds per metric and per device family held in one file outside the
image, so they survive a version bump, and re-applied idempotently. openwisp-monitoring 1.3 stores a custom value equal to the metric's
default as NULL (AlertSettings.save), so "unset" and "equals the default" read the same (`AlertSettings.threshold` returns the effective
value) and a re-run plans 0 changes. Only `custom_threshold`, `custom_tolerance` and `is_active` of existing rows are touched; a metric a
device does not have is skipped, nothing is created. A device whose class the caller cannot resolve is reported and left alone.

The caller supplies everything outside OpenWISP: the policy as a dict (loaded from YAML or anything else), the device -> class mapping
(from its inventory), and a Django shell runner (`openwisp_registry.django_shell`). The comparison runs server-side in one shell, against
every row at once; `plan_differences` is the same rule offline, for tests and for callers that already hold the rows. The program is
generated per run, and the dry-run program contains no write statement at all: only `program(apply=True)` can save a row.

Usage:
    from openwisp_registry import django_shell
    from openwisp_alert_policy import AlertPolicy, AlertSettingsConverger, read_device_pks
    policy = AlertPolicy.from_dict(yaml.safe_load(text))                  # {defaults: {metric: {...}}, classes-key: {cls: {metric: {...}}}}
    devices = read_device_pks(django_shell("<dashboard-container>"))      # {hardware_id: OpenWISP device pk}
    conv = AlertSettingsConverger(policy, devices, classes)               # classes: {hardware_id: class or None}
    counts, lines, error = conv.converge(django_shell("<dashboard-container>", timeout=300), apply=False)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from openwisp_registry import ShellRunner

#: The keys openwisp-monitoring 1.3's AlertSettings carries; anything else in a policy entry (a `reason`, say) is documentation.
SETTING_KEYS = ("threshold", "tolerance", "is_active")

#: One `D <hardware_id> <pk>` line per device that has a hardware_id.
DEVICE_PK_PROGRAM = ("from swapper import load_model\n"
                     "for hw, pk in load_model('config','Device').objects.exclude(hardware_id__isnull=True).exclude(hardware_id='').values_list('hardware_id','pk'):"
                     " print('D', hw, pk)")

_PROGRAM_HEAD = """
import json, sys
from swapper import load_model
AlertSettings = load_model('monitoring', 'AlertSettings')
plan = json.loads(sys.stdin.read())
apply = plan['apply']
by_object = {}
for a in AlertSettings.objects.select_related('metric').filter(metric__object_id__in=list(plan['object_ids'])):
    by_object.setdefault(str(a.metric.object_id), {})[a.metric.configuration] = a
for hw, pk in plan['devices'].items():
    for conf, target in plan['want'][hw].items():
        a = by_object.get(pk, {}).get(conf)
        if a is None:
            continue
        current = {'threshold': a.threshold, 'tolerance': a.tolerance, 'is_active': a.is_active}
        diff = {k: (current[k], v) for k, v in target.items() if current[k] != v}
        if not diff:
            print('SAME', hw, conf)
            continue
        print('CHANGE' if apply else 'WOULD', hw, conf, json.dumps(diff))
"""
_PROGRAM_WRITE = """        if apply:
            if 'threshold' in target: a.custom_threshold = target['threshold']
            if 'tolerance' in target: a.custom_tolerance = target['tolerance']
            if 'is_active' in target: a.is_active = target['is_active']
            a.full_clean(); a.save()
"""
TAGS = ("SAME", "WOULD", "CHANGE")


def program(apply: bool) -> str:
    """The server-side program. It reads the plan as JSON on stdin and prints one `SAME|WOULD|CHANGE <hw> <metric> [diff]` per row.
    Without `apply` the write statements are not in the program, so a dry run cannot save even if the plan says otherwise."""
    return _PROGRAM_HEAD + (_PROGRAM_WRITE if apply else "")


def _strip(values: dict | None) -> dict:
    return {k: v for k, v in (values or {}).items() if k in SETTING_KEYS}


@dataclass
class AlertPolicy:
    """Per-metric defaults and per-class overrides, both `{metric: {threshold, tolerance, is_active}}`."""

    defaults: dict[str, dict] = field(default_factory=dict)
    classes: dict[str, dict[str, dict]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict | None, classes_key: str = "classes") -> "AlertPolicy":
        """From a loaded document: `defaults` and `classes_key` (the caller's name for its classes, e.g. `families`). Unknown keys dropped."""
        data = data or {}
        return cls(defaults={m: _strip(v) for m, v in (data.get("defaults") or {}).items()},
                   classes={c: {m: _strip(v) for m, v in (metrics or {}).items()} for c, metrics in (data.get(classes_key) or {}).items()})

    def wanted(self, device_class: str | None) -> dict[str, dict]:
        """Per-metric targets for one class: the defaults, then the class's overrides on top. An unknown or None class gets the defaults."""
        out = {m: dict(v) for m, v in self.defaults.items()}
        for m, v in self.classes.get(device_class or "", {}).items():
            out.setdefault(m, {}).update(v)
        return out


def diff_settings(current: dict, target: dict) -> dict:
    """{key: (current, wanted)} for each targeted key whose current value differs; the rule the server-side program applies."""
    return {k: (current[k], v) for k, v in target.items() if current[k] != v}


def plan_differences(policy: AlertPolicy, devices: dict[str, str], classes: dict[str, str | None],
                     rows: dict[str, dict[str, dict]]) -> list[tuple[str, str, str, dict]]:
    """Offline planner. `rows` is {device pk: {metric: {threshold, tolerance, is_active}}} as currently effective. Returns
    (SAME|WOULD, hardware_id, metric, diff) per existing row of every resolvable device, in device then policy order."""
    out = []
    for hw, pk in devices.items():
        if hw not in classes:
            continue
        for conf, target in policy.wanted(classes[hw]).items():
            current = rows.get(pk, {}).get(conf)
            if current is None:
                continue
            diff = diff_settings(current, target)
            out.append(("WOULD" if diff else "SAME", hw, conf, diff))
    return out


def parse_device_pks(stdout: str) -> dict[str, str]:
    return {line.split()[1]: line.split()[2] for line in stdout.splitlines() if line.startswith("D ")}


def read_device_pks(runner: ShellRunner) -> dict[str, str]:
    """{hardware_id: OpenWISP device pk} for every registered device. An empty or failed read returns {} (the caller decides)."""
    return parse_device_pks(runner(DEVICE_PK_PROGRAM, None).stdout or "")


class AlertSettingsConverger:
    """Plans and (with apply) writes the per-device AlertSettings differences in one Django shell.

    Devices whose hardware_id is not in `classes` are `unresolved` and left out of the plan; a resolved device with class None gets
    the defaults.
    """

    def __init__(self, policy: AlertPolicy, devices: dict[str, str], classes: dict[str, str | None]):
        self.policy = policy
        self.devices = {hw: pk for hw, pk in devices.items() if hw in classes}
        self.unresolved = sorted(hw for hw in devices if hw not in classes)
        self.classes = classes

    def plan(self, apply: bool) -> dict:
        """The JSON document the program reads on stdin."""
        return {"apply": apply, "devices": self.devices, "object_ids": sorted(self.devices.values()),
                "want": {hw: self.policy.wanted(self.classes[hw]) for hw in self.devices}}

    @staticmethod
    def parse(stdout: str) -> tuple[dict[str, int], list[str]]:
        """(counts by SAME/WOULD/CHANGE, the non-SAME lines)."""
        counts, lines = {t: 0 for t in TAGS}, []
        for line in stdout.splitlines():
            tag = line.split(" ", 1)[0]
            if tag in counts:
                counts[tag] += 1
                if tag != "SAME":
                    lines.append(line)
        return counts, lines

    def converge(self, runner: ShellRunner, apply: bool = False) -> tuple[dict[str, int], list[str], str | None]:
        """Returns (counts by SAME/WOULD/CHANGE, the change lines, the stderr tail if the shell failed). Writes only when `apply`."""
        out = runner(program(apply), json.dumps(self.plan(apply)))
        counts, lines = self.parse(out.stdout or "")
        return counts, lines, ((out.stderr or "")[-500:] if out.returncode != 0 else None)
