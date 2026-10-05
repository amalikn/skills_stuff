#!/usr/bin/env python3
"""Read-only health probe for a docker-openwisp 26.09.0 deployment: effective settings, Celery worker liveness, data freshness.

Why: a container shown Up says nothing about OpenWISP's workers, because the image starts them detached behind a `tail` process
(/opt/openwisp/init_command.sh). On 2026-10-05 a deployment had no worker for a week while every container was Up and every push
returned HTTP 200. Custom settings load through a silent `try/except ImportError`, so an override can be missing without an error.
This probe checks the three things that silence hides. It writes nothing, restarts nothing and prints no secret.

Usage:
    python3 openwisp_probe.py workers --container <celery-container> [--expect 5]
    python3 openwisp_probe.py freshness --container <influxdb-container> [--database openwisp] [--measurement ping] [--max-age 3600]
    python3 openwisp_probe.py settings --containers <dashboard>,<api>,<celery> --expected expected.json
Exit 0 when everything checked is healthy, 1 otherwise. `expected.json` maps setting names to expected values: `NAME` for a Django setting,
`module:ATTR` for an app's effective value (e.g. `openwisp_controller.config.settings:DEVICE_NAME_UNIQUE`).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

Runner = Callable[[list[str]], subprocess.CompletedProcess]
#: A plain NAME is read from django.conf.settings (`__UNSET__` when not defined there, so the app's own default applies). A
#: `module:ATTR` name is read from that module, which is how OpenWISP apps expose effective values with defaults applied
#: (for example `openwisp_controller.config.settings:DEVICE_NAME_UNIQUE`).
_SETTINGS_PROGRAM = (
    "import json, importlib; from django.conf import settings; names = {names!r}\n"
    "def value(n):\n"
    "    if ':' in n:\n"
    "        mod, attr = n.split(':', 1)\n"
    "        return getattr(importlib.import_module(mod), attr, '__MISSING__')\n"
    "    return getattr(settings, n, '__UNSET__')\n"
    "print('PROBE ' + json.dumps({{n: value(n) for n in names}}, default=str))"
)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


@dataclass
class Finding:
    check: str
    healthy: bool
    detail: str
    data: dict = field(default_factory=dict)


class OpenWispProbe:
    """Each check runs read-only commands through `runner`, so tests can feed recorded output."""

    def __init__(self, runner: Runner = run):
        self.runner = runner

    def workers(self, container: str, expect: int = 5) -> Finding:
        """Celery nodes answering `inspect ping`. The 26.09.0 image runs five: celery, network, firmware_upgrader, monitoring, monitoring_checks."""
        out = self.runner(["docker", "exec", "-w", "/opt/openwisp", container, "celery", "-A", "openwisp", "inspect", "ping", "--json", "--timeout", "5"])
        nodes: list[str] = []
        for line in (out.stdout or "").splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    nodes = sorted(json.loads(line))
                except json.JSONDecodeError:
                    pass
        healthy = len(nodes) >= expect
        return Finding("workers", healthy, f"{len(nodes)} of {expect} Celery nodes answered" + ("" if nodes else "; none replied"), {"nodes": nodes})

    def freshness(self, container: str, database: str = "openwisp", measurement: str = "ping", max_age: int = 3600,
                  now: datetime | None = None) -> Finding:
        """Age of the newest point of `measurement`. Old data with live workers points at the collector; old data without workers at OpenWISP."""
        query = f"SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1"
        out = self.runner(["docker", "exec", container, "influx", "-database", database, "-format", "json", "-precision", "rfc3339", "-execute", query])
        try:
            series = json.loads(out.stdout)["results"][0]["series"][0]
            newest = series["values"][0][series["columns"].index("time")]
        except (json.JSONDecodeError, KeyError, IndexError, ValueError):
            return Finding("freshness", False, f"no point found in {database}.{measurement}", {})
        stamp = datetime.fromisoformat(newest.replace("Z", "+00:00"))
        age = int(((now or datetime.now(timezone.utc)) - stamp).total_seconds())
        return Finding("freshness", age <= max_age, f"newest {measurement} point {newest}, {age} s old (limit {max_age} s)", {"newest": newest, "age": age})

    def settings(self, containers: list[str], expected: dict) -> Finding:
        """Effective Django settings in each container, compared with `expected`. Reports names only for a missing setting, never values of
        names that look secret."""
        program = _SETTINGS_PROGRAM.format(names=sorted(expected))
        problems, seen = [], {}
        for container in containers:
            out = self.runner(["docker", "exec", "-i", "-w", "/opt/openwisp", container, "python", "manage.py", "shell", "-c", program])
            line = next((l for l in (out.stdout or "").splitlines() if l.startswith("PROBE ")), None)
            if line is None:
                problems.append(f"{container}: settings not readable")
                continue
            values = json.loads(line[len("PROBE "):])
            seen[container] = values
            for name, want in sorted(expected.items()):
                got = values.get(name, "__MISSING__")
                if got != want:
                    shown = "<differs>" if _secretish(name) else f"{got!r} (expected {want!r})"
                    problems.append(f"{container}: {name} = {shown}")
        return Finding("settings", not problems, "; ".join(problems) or f"{len(expected)} settings as expected in {len(containers)} containers",
                       {"problems": problems})


def _secretish(name: str) -> bool:
    return any(word in name.upper() for word in ("KEY", "SECRET", "PASSWORD", "TOKEN"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("workers"); w.add_argument("--container", required=True); w.add_argument("--expect", type=int, default=5)
    f = sub.add_parser("freshness"); f.add_argument("--container", required=True); f.add_argument("--database", default="openwisp")
    f.add_argument("--measurement", default="ping"); f.add_argument("--max-age", type=int, default=3600)
    s = sub.add_parser("settings"); s.add_argument("--containers", required=True); s.add_argument("--expected", required=True)
    args = ap.parse_args(argv)
    probe = OpenWispProbe()
    if args.cmd == "workers":
        finding = probe.workers(args.container, args.expect)
    elif args.cmd == "freshness":
        finding = probe.freshness(args.container, args.database, args.measurement, args.max_age)
    else:
        with open(args.expected, encoding="utf-8") as fh:
            finding = probe.settings(args.containers.split(","), json.load(fh))
    print(f"{finding.check}: {'ok' if finding.healthy else 'PROBLEM'} — {finding.detail}")
    return 0 if finding.healthy else 1


if __name__ == "__main__":
    sys.exit(main())
