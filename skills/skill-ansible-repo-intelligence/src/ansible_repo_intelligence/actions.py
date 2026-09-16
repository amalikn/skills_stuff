"""Deterministic managed-resource extraction from parsed task args.

Turns a task's raw module + args into a compact, normalized *fact* record —
never an interpretation. The CLI emits these facts; the agent forms the
conclusion. This is what lets a bounded query be a *sufficient, source-traceable
answer* to routine "how is X configured" questions without opening source.

Design constraints:
- Facts only. No prose, no "installed from source" conclusions.
- Compact. Values are length-capped; only salient keys are kept, so enrichment
  does not bloat graph.yaml (measured, gated at <=25%).
- Risk-based verification flag: when a fact is dynamic/critical/complex, the
  record recommends opening source, with a reason.
- Never surface secret values (copy `content`, vault) — note presence only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_MAXLEN = 200  # cap any single string value to keep the graph compact

# Collection prefixes stripped to a short leaf name for extractor lookup.
_PREFIXES = (
    "ansible.builtin.", "ansible.posix.", "ansible.netcommon.",
    "community.general.", "community.mysql.", "community.postgresql.",
    "community.crypto.", "community.docker.",
)

# Short module name -> operation label.
OPERATION = {
    "package": "install_package", "apt": "install_package", "dnf": "install_package",
    "yum": "install_package", "apt_rpm": "install_package", "pip": "install_package",
    "service": "service_state", "systemd": "service_state",
    "systemd_service": "service_state", "sysvinit": "service_state",
    "template": "render_template",
    "copy": "copy_file",
    "file": "manage_path",
    "command": "execute_command", "shell": "execute_command", "raw": "execute_command",
    "script": "run_script",
    "user": "manage_user", "group": "manage_group",
    "lineinfile": "edit_file", "blockinfile": "edit_file", "replace": "edit_file",
    "get_url": "download", "unarchive": "extract_archive", "git": "git_checkout",
    "mount": "manage_mount", "cron": "manage_cron", "uri": "http_request",
    "apt_repository": "manage_repo", "yum_repository": "manage_repo",
    "apt_key": "manage_repo",
    "set_fact": "set_fact", "debug": "diagnostic", "assert": "diagnostic",
    "meta": "diagnostic",
}

# Modules whose free-form command warrants source verification by default.
_FREEFORM = {"command", "shell", "raw", "script"}
# Known-good short names (anything else custom/unknown -> verify).
_KNOWN = set(OPERATION) | {
    "parted", "filesystem", "lvg", "lvol", "mysql_db", "postgresql_db",
    "mysql_user", "postgresql_user", "iptables", "firewalld", "ufw", "nmcli",
    "reboot", "sysctl", "authorized_key", "known_hosts", "pip3", "make",
}


@dataclass
class Action:
    operation: str
    resource: dict[str, Any] = field(default_factory=dict)
    verification_recommended: bool = False
    verification_reason: str | None = None

    def to_attrs(self) -> dict[str, Any]:
        d: dict[str, Any] = {"operation": self.operation}
        if self.resource:
            d["resource"] = self.resource
        if self.verification_recommended:
            d["verification"] = {"recommended": True, "reason": self.verification_reason}
        return d


def short_module(module_key: str, normalized: str) -> str:
    m = module_key or normalized or ""
    for p in _PREFIXES:
        if m.startswith(p):
            return m[len(p):]
    return m


def _cap(v: Any) -> Any:
    if isinstance(v, str):
        s = v.strip()
        return s[:_MAXLEN] + "…" if len(s) > _MAXLEN else s
    if isinstance(v, (int, float, bool)) or v is None:
        return v
    if isinstance(v, list):
        return [_cap(x) for x in v[:20]]
    return _cap(str(v))


def _has_jinja(v: Any) -> bool:
    if isinstance(v, str):
        return "{{" in v or "{%" in v
    if isinstance(v, dict):
        return any(_has_jinja(x) for x in v.values())
    if isinstance(v, list):
        return any(_has_jinja(x) for x in v)
    return False


def extract_action(module_key: str, normalized_module: str, args: Any,
                   when: list[str], is_critical: bool) -> Action | None:
    """Extract a compact Action fact record. Returns None for include/meta-only."""
    short = short_module(module_key, normalized_module)
    op = OPERATION.get(short, "module_action")
    res = _extract_resource(short, args)
    action = Action(operation=op, resource=res)

    # --- risk-based verification policy ---
    reasons: list[str] = []
    if short in _FREEFORM:
        reasons.append("Free-form command; verify exact behaviour against source")
    if _has_jinja(res):
        reasons.append("Contains a Jinja-derived value (dynamic)")
    if when and (len(when) > 1 or any(_complex_when(w) for w in when)):
        reasons.append("Complex conditional (when); verify applicability")
    if short not in _KNOWN and op == "module_action":
        reasons.append("Custom/unknown module; verify against source")
    if is_critical:
        reasons.append("Critical operation; verify against source")
    if reasons:
        action.verification_recommended = True
        action.verification_reason = "; ".join(reasons)
    return action


def _complex_when(w: str) -> bool:
    wl = str(w).lower()
    return " and " in wl or " or " in wl or "|" in wl or "{{" in wl


def _extract_resource(short: str, args: Any) -> dict[str, Any]:
    d = args if isinstance(args, dict) else None
    s = args if isinstance(args, str) else None

    if short in ("package", "apt", "dnf", "yum", "apt_rpm", "pip"):
        return _keep(d, extra=("name", "state", "version"), rename={"name": "packages"})
    if short in ("service", "systemd", "systemd_service", "sysvinit"):
        return _keep(d, extra=("name", "state", "enabled", "daemon_reload"))
    if short == "template":
        return _keep(d, extra=("src", "dest", "owner", "mode"))
    if short == "copy":
        r = _keep(d, extra=("src", "dest", "owner", "mode"))
        if d and "content" in d and "src" not in r:
            r["content"] = "<inline content present>"
        return r
    if short == "file":
        return _keep(d, extra=("path", "state", "mode", "owner", "group"))
    if short in ("command", "shell", "raw"):
        if s is not None:
            return {"command": _cap(s)}
        return _keep(d, extra=("cmd", "chdir", "creates", "removes"), rename={"cmd": "command"})
    if short == "script":
        if s is not None:
            return {"script": _cap(s)}
        return _keep(d, extra=("cmd", "creates"), rename={"cmd": "script"})
    if short == "user":
        return _keep(d, extra=("name", "groups", "shell", "state", "system"))
    if short == "group":
        return _keep(d, extra=("name", "state", "gid"))
    if short in ("lineinfile", "blockinfile", "replace"):
        return _keep(d, extra=("path", "regexp", "marker", "state"))
    if short == "get_url":
        return _keep(d, extra=("url", "dest"))
    if short == "unarchive":
        return _keep(d, extra=("src", "dest", "remote_src"))
    if short == "git":
        return _keep(d, extra=("repo", "dest", "version"))
    if short == "mount":
        return _keep(d, extra=("path", "src", "fstype", "state"))
    if short == "cron":
        return _keep(d, extra=("name", "job", "minute", "hour", "state"))
    if short == "uri":
        return _keep(d, extra=("url", "method", "status_code"))
    if short in ("apt_repository", "yum_repository"):
        return _keep(d, extra=("repo", "name", "baseurl", "state"))
    if short == "apt_key":
        return _keep(d, extra=("url", "keyserver", "id"))
    if short == "set_fact":
        return {"keys": sorted(d.keys())} if d else {}
    if short in ("debug", "assert", "meta"):
        return {}
    # generic fallback: keep only the arg KEY names (not values) — compact + safe.
    if d:
        return {"keys": sorted(k for k in d.keys())[:12]}
    if s is not None:
        return {"value": _cap(s)}
    return {}


def _keep(d: dict | None, extra: tuple[str, ...] = (),
          rename: dict[str, str] | None = None) -> dict[str, Any]:
    """Keep only the named keys from a task-arg dict, capped and renamed."""
    if not isinstance(d, dict):
        return {}
    rename = rename or {}
    out: dict[str, Any] = {}
    for k in extra:
        if k in d and d[k] is not None:
            out[rename.get(k, k)] = _cap(d[k])
    return out
