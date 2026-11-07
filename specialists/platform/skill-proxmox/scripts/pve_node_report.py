#!/usr/bin/env python3
"""Read-only health and inventory report for one Proxmox VE node: version, pending updates, repositories, storage use, guests,
pools, users and tokens, and the least-privilege audit. Read-only unless asked: it does not run `apt update` (only
`--refresh --apply` asks PVE to refresh the list); it reads the list PVE cached at its last daily refresh and says when that ran.

Why: the operator asked on 2026-11-07 for one command that answers "what is on this node and is it healthy" before any
OpenTofu or upgrade work, without touching the node. All reads go in one SSH round trip (pve_ssh).

Usage:
  pve_node_report.py --host pve.example.internal [--json] [--storage-warn 85]
  pve_node_report.py --host pve.example.internal --refresh [--apply]   (plan, or refresh the package list first: a write)
  pve_node_report.py --from-dir saved/          (keys below as <key>.json / <key>.txt)
Exit: 0 report printed and no warning; 1 report printed with at least one warning; 2 bad arguments or a read failed.
"""

from __future__ import annotations

import argparse
import json
import sys

import pve_ssh
import pve_token_audit

#: Percent used at which a storage is a warning.
STORAGE_WARN_PCT = 85.0
#: The one write this script can do, and only with --refresh --apply: PVE's own package-list refresh (apt update).
REFRESH = "pvesh create /nodes/localhost/apt/update"
#: Package names whose pending update matters most (the PVE stack itself).
PVE_CORE = ("proxmox-ve", "pve-manager", "qemu-server", "pve-qemu-kvm", "pve-edk2-firmware-ovmf", "pve-container",
            "libpve-access-control", "proxmox-kernel-helper")
READS = {
  "version": pve_ssh.pvesh("/nodes/localhost/version"),
  "status": pve_ssh.pvesh("/nodes/localhost/status"),
  "cluster": pve_ssh.pvesh("/cluster/status"),
  "updates": pve_ssh.pvesh("/nodes/localhost/apt/update"),
  "repos": pve_ssh.pvesh("/nodes/localhost/apt/repositories"),
  "storage": pve_ssh.pvesh("/nodes/localhost/storage"),
  "resources": pve_ssh.pvesh("/cluster/resources"),
  "pools": pve_ssh.pvesh("/pools"),
  "daily": "systemctl show pve-daily-update.service -p ExecMainExitTimestamp -p Result",
  **pve_token_audit.READS,
}


def summarise(raw: dict[str, str], storage_warn: float = STORAGE_WARN_PCT) -> dict:
  """Build the report from raw command outputs.

  Args:
    raw: key -> text, from pve_ssh.read_all or a dir reader.
    storage_warn: percent used that makes a storage a warning.

  Returns:
    Report dict with sections and a `warnings` list.

  Raises:
    pve_ssh.PveReadError: an output that should be JSON is not.
  """
  def j(key: str, default: object = None) -> object:
    """One key's output as JSON.

    Args:
      key: which output.
      default: when the output is empty.

    Returns:
      The parsed value.
    """
    return pve_ssh.as_json(raw, key, default)

  warnings: list[str] = []
  version = j("version", {}) or {}
  status = j("status", {}) or {}
  updates = j("updates", []) or []
  core = sorted(f"{u['Package']} {u.get('OldVersion', '?')} -> {u.get('Version', '?')}" for u in updates if u.get("Package") in PVE_CORE)
  daily = dict(line.split("=", 1) for line in raw.get("daily", "").splitlines() if "=" in line)
  if updates:
    warnings.append(f"{len(updates)} package updates pending ({len(core)} in the PVE stack); upgrade with apt full-upgrade, never apt upgrade")
  if daily.get("Result") not in (None, "success"):
    warnings.append(f"pve-daily-update last result {daily.get('Result')}: the update list may be stale")
  repos = []
  for f in (j("repos", {}) or {}).get("files", []):
    for r in f.get("repositories", []):
      repos.append({"file": f["path"], "format": f.get("file-type"), "enabled": bool(r.get("Enabled")),
                    "suites": r.get("Suites"), "components": r.get("Components")})
  if any(r["enabled"] and r["format"] == "list" for r in repos):
    warnings.append("an enabled repository uses the legacy one-line .list format; on trixie run `apt modernize-sources`")
  storage = []
  for s in j("storage", []) or []:
    pct = round(100.0 * s.get("used", 0) / s["total"], 1) if s.get("total") else None
    storage.append({"storage": s["storage"], "type": s.get("type"), "content": s.get("content"), "active": s.get("active"),
                    "used_pct": pct})
    if pct is not None and pct >= storage_warn:
      warnings.append(f"storage {s['storage']} {pct}% used")
    if not s.get("active") and s.get("enabled", 1):
      warnings.append(f"storage {s['storage']} enabled but not active")
  guests = sorted(({"vmid": r["vmid"], "type": r["type"], "name": r.get("name"), "status": r.get("status"), "pool": r.get("pool"),
                    "template": bool(r.get("template"))} for r in j("resources", []) or [] if r.get("type") in ("qemu", "lxc")),
                  key=lambda g: g["vmid"])
  users = j("users", []) or []
  identities = [{"userid": u["userid"], "enabled": bool(u.get("enable", 1)),
                 "tokens": [{"tokenid": t["tokenid"], "privsep": t.get("privsep"), "expire": t.get("expire")} for t in u.get("tokens") or []]}
                for u in users]
  acl = j("acl", []) or []
  findings = pve_token_audit.audit(users, acl, j("roles", []) or [])
  if any(f.severity == "high" for f in findings):
    warnings.append(f"{sum(f.severity == 'high' for f in findings)} high access finding(s): see access")
  return {
    "version": version.get("version"), "release": version.get("release"),
    "kernel": (status.get("current-kernel") or {}).get("release") or status.get("kversion"),
    "uptime_s": status.get("uptime"),
    "memory_pct": round(100.0 * status["memory"]["used"] / status["memory"]["total"], 1) if status.get("memory", {}).get("total") else None,
    "rootfs_pct": round(100.0 * status["rootfs"]["used"] / status["rootfs"]["total"], 1) if status.get("rootfs", {}).get("total") else None,
    "cluster": [{"name": c.get("name"), "type": c.get("type"), "quorate": c.get("quorate"), "online": c.get("online")} for c in j("cluster", []) or []],
    "updates": {"pending": len(updates), "pve_stack": core, "list_refreshed": daily.get("ExecMainExitTimestamp"),
                "refresh_result": daily.get("Result")},
    "repositories": repos, "storage": storage, "guests": guests,
    "pools": [p.get("poolid") for p in j("pools", []) or []],
    "identities": identities, "acl_entries": len(acl),
    "access": [vars(f) for f in findings],
    "warnings": warnings,
  }


def render(rep: dict) -> str:
  """Plain-text form of the report.

  Args:
    rep: from summarise().

  Returns:
    The text.
  """
  out = [f"Proxmox VE {rep['version']} (release {rep['release']}), kernel {rep['kernel']}, uptime {rep['uptime_s']} s,"
         f" memory {rep['memory_pct']}%, rootfs {rep['rootfs_pct']}%"]
  for c in rep["cluster"]:
    out.append(f"cluster: {c['type']} {c['name']} quorate={c['quorate']} online={c['online']}")
  u = rep["updates"]
  out.append(f"updates: {u['pending']} pending; list refreshed {u['list_refreshed']} ({u['refresh_result']}); apt update NOT run by this report")
  out += [f"  {line}" for line in u["pve_stack"]]
  out.append("repositories:")
  out += [f"  {'on ' if r['enabled'] else 'off'} {r['format']:<7} {' '.join(r['suites'] or [])} {' '.join(r['components'] or [])}  {r['file']}"
          for r in rep["repositories"]]
  out.append("storage:")
  out += [f"  {s['storage']:<14} {s['type']:<8} {s['used_pct']}% used  {s['content']}" for s in rep["storage"]]
  out.append(f"guests ({len(rep['guests'])}):")
  out += [f"  {g['vmid']:>5} {g['type']:<4} {g['status']:<8} {g['name']} pool={g['pool'] or '-'}{' template' if g['template'] else ''}"
          for g in rep["guests"]]
  out.append(f"pools: {', '.join(rep['pools']) or '-'}")
  out.append(f"identities ({len(rep['identities'])}), ACL entries {rep['acl_entries']}:")
  for i in rep["identities"]:
    toks = ", ".join(f"{t['tokenid']}(privsep={t['privsep']}, expire={t['expire']})" for t in i["tokens"]) or "no tokens"
    out.append(f"  {i['userid']}{'' if i['enabled'] else ' (disabled)'}: {toks}")
  out.append("access findings:")
  out += [f"  {f['severity']:<6} {f['rule']}: {f['subject']}: {f['detail']}" for f in rep["access"]] or ["  none"]
  out.append("warnings:")
  out += [f"  {w}" for w in rep["warnings"]] or ["  none"]
  return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 no warning, 1 warnings, 2 bad arguments or a failed read.
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  src = ap.add_mutually_exclusive_group(required=True)
  src.add_argument("--host", help="node to read over SSH (key auth)")
  src.add_argument("--from-dir", help="folder of captures named by key")
  ap.add_argument("--ssh-user", default="root", help="SSH user (default root)")
  ap.add_argument("--storage-warn", type=float, default=STORAGE_WARN_PCT, help="percent used that warns (default 85)")
  ap.add_argument("--json", action="store_true", help="print the report as JSON")
  ap.add_argument("--refresh", action="store_true", help="refresh the package list before reading (a write: needs --apply)")
  ap.add_argument("--apply", action="store_true", help="carry out --refresh; without it --refresh only prints the plan")
  args = ap.parse_args(argv)
  if args.refresh and not args.host:
    ap.error("--refresh needs --host")
  try:
    if args.refresh and not args.apply:
      print(f"plan: on {args.host} run `{REFRESH}` (apt update through PVE), then report; add --apply to do it", file=sys.stderr)
    elif args.refresh:
      print(f"refreshing the package list on {args.host}", file=sys.stderr)
      pve_ssh.ssh_runner(args.host, args.ssh_user)(REFRESH)
    if args.host:
      raw = pve_ssh.read_all(pve_ssh.ssh_runner(args.host, args.ssh_user), READS)
    else:
      raw = pve_ssh.dir_runner(args.from_dir)(READS)
    rep = summarise(raw, args.storage_warn)
  except pve_ssh.PveReadError as exc:
    print(f"error: {exc}", file=sys.stderr)
    return 2
  print(json.dumps(rep, indent=2) if args.json else render(rep))
  return 1 if rep["warnings"] else 0


if __name__ == "__main__":
  sys.exit(main())
