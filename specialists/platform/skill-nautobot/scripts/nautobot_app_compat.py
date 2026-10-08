"""Check Nautobot apps against a Nautobot and Python version from their PyPI metadata. Read-only, stdlib only.

For each `package` or `package==version` it reads `https://pypi.org/pypi/<package>/json` (latest) or `/<package>/<version>/json` and prints
the version, its release date, `requires_python`, the `nautobot` requirement from `requires_dist`, and whether `--nautobot` and `--python`
satisfy them. Why: an app pin is chosen before an image rebuild, and the app's declared ranges are the first gate; they are not proof that
the app migrates and runs (that needs the install itself, see references/upgrade-and-troubleshooting.md).

The specifier check is deliberately small: comma-joined `>=`, `>`, `<=`, `<`, `==` (with a trailing `.*` wildcard), `!=` and `~=` over
dotted numeric release segments; a pre-release, post-release or local suffix is cut off before comparing. Anything it cannot parse is
reported as unknown, never as compatible.

Usage:
    python3 nautobot_app_compat.py nautobot-ssot==4.7.0 nautobot-device-lifecycle-mgmt==4.2.0 --nautobot 3.2.3 --python 3.13
    from nautobot_app_compat import assess, satisfies
Exit 0 when every package is compatible, 1 when any is not or cannot be judged, 2 when PyPI could not be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Callable

PYPI = "https://pypi.org/pypi"
_OPS = ("~=", "==", "!=", "<=", ">=", "<", ">")


def release(version: str) -> tuple[int, ...]:
    """The numeric release segment of a version (`3.2.3rc1` -> (3, 2, 3)); raises ValueError when there is none."""
    m = re.match(r"^\s*v?(\d+(?:\.\d+)*)", version)
    if not m:
        raise ValueError(f"not a version: {version!r}")
    return tuple(int(p) for p in m.group(1).split("."))


def _cmp(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    """-1, 0 or 1 comparing two release tuples, the shorter padded with zeros (3.13 == 3.13.0)."""
    n = max(len(a), len(b))
    a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
    return (a > b) - (a < b)


def satisfies(version: str, spec: str) -> bool | None:
    """Whether `version` meets every clause of a comma-joined specifier; True for an empty spec, None when a clause cannot be parsed."""
    try:
        v = release(version)
    except ValueError:
        return None
    for clause in (c.strip() for c in spec.split(",") if c.strip()):
        op = next((o for o in _OPS if clause.startswith(o)), None)
        if op is None:
            return None
        target = clause[len(op):].strip()
        try:
            if op in ("==", "!=") and target.endswith(".*"):
                prefix = release(target[:-2])
                hit = v[:len(prefix)] + (0,) * max(0, len(prefix) - len(v)) == prefix
                ok = hit if op == "==" else not hit
            else:
                t = release(target)
                c = _cmp(v, t)
                ok = {"==": c == 0, "!=": c != 0, "<": c < 0, "<=": c <= 0, ">": c > 0, ">=": c >= 0,
                      "~=": c >= 0 and len(t) >= 2 and _cmp(v[:len(t) - 1], t[:-1]) == 0}[op]
        except ValueError:
            return None
        if not ok:
            return False
    return True


def nautobot_requirement(requires_dist: list[str] | None) -> str | None:
    """The specifier of the `nautobot` entry in requires_dist (`nautobot<4.0.0,>=3.1.0` or `nautobot (>=2.0,<3)`), '' when unpinned, None when absent.

    An entry with an environment marker (`; extra == "x"`) is skipped: an extra's requirement is not the app's own.
    """
    for entry in requires_dist or []:
        req, _, marker = entry.partition(";")
        if "extra" in marker:
            continue
        m = re.match(r"^\s*nautobot(?![\w.-])\s*(?:\[[^\]]*\])?\s*\(?\s*([^)]*?)\s*\)?\s*$", req)   # not nautobot-<app>
        if m:
            return m.group(1).replace(" ", "")
    return None


def assess(meta: dict, nautobot: str, python: str) -> dict:
    """One package's row from its PyPI JSON: version, released, requires_python, nautobot spec, and the two verdicts plus `compatible`.

    `compatible` is True only when both verdicts are True; a missing nautobot requirement leaves it None (cannot be judged from metadata).
    """
    info = meta.get("info") or {}
    files = meta.get("urls") or []
    released = min((f.get("upload_time_iso_8601") or f.get("upload_time") or "" for f in files), default="")[:10] or None
    req_py = info.get("requires_python") or ""
    nb_spec = nautobot_requirement(info.get("requires_dist"))
    py_ok = satisfies(python, req_py)
    nb_ok = None if nb_spec is None else satisfies(nautobot, nb_spec)
    return {"package": info.get("name"), "version": info.get("version"), "released": released, "requires_python": req_py or None,
            "nautobot_requirement": nb_spec, "nautobot_ok": nb_ok, "python_ok": py_ok,
            "compatible": True if (nb_ok is True and py_ok is True) else False if (nb_ok is False or py_ok is False) else None}


def fetch_pypi(package: str, version: str | None = None) -> dict:
    """PyPI's JSON for a package (latest) or one version; raises RuntimeError on an HTTP or network failure."""
    url = f"{PYPI}/{package}/{version}/json" if version else f"{PYPI}/{package}/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=30) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, ValueError) as e:
        raise RuntimeError(f"{url}: {e}") from None


def main(argv: list[str] | None = None, fetch: Callable[[str, str | None], dict] = fetch_pypi) -> int:
    """Print one line per package (and JSON with --json); exit 0 when all are compatible."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("packages", nargs="+", help="package or package==version")
    ap.add_argument("--nautobot", required=True, help="Nautobot version to check, e.g. 3.2.3")
    ap.add_argument("--python", required=True, help="Python version to check, e.g. 3.13")
    ap.add_argument("--json", action="store_true", help="print the rows as JSON instead of lines")
    a = ap.parse_args(argv)
    rows = []
    for item in a.packages:
        name, _, ver = item.partition("==")
        try:
            rows.append(assess(fetch(name.strip(), ver.strip() or None), a.nautobot, a.python))
        except RuntimeError as e:
            print(e, file=sys.stderr)
            return 2
    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        verdict = {True: "compatible", False: "NOT compatible", None: "cannot judge"}
        for r in rows:
            print(f"{r['package']} {r['version']} (released {r['released']}): nautobot {r['nautobot_requirement']!r} -> {r['nautobot_ok']}, "
                  f"python {r['requires_python']!r} -> {r['python_ok']}: {verdict[r['compatible']]} with Nautobot {a.nautobot} / Python {a.python}")
    return 0 if all(r["compatible"] is True for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
