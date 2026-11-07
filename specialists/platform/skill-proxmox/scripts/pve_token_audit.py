#!/usr/bin/env python3
"""Least-privilege audit of Proxmox VE users, API tokens and ACLs. Read-only: it reads /access/users, /access/acl and
/access/roles (over SSH, or from saved captures) and reports findings; it changes nothing.

Why: an automation identity (OpenTofu, an MCP server, a monitoring probe) is often made with a token that shares its user's
full rights and an Administrator-class role on `/`. The operator asked on 2026-11-07 for a check that names those, so a
lab or production node can be held to the pool-scoped, privilege-separated pattern in references/access-control.md.

Usage:
  pve_token_audit.py --host pve.example.internal [--json] [--allow-user root@pam ...]
  pve_token_audit.py --from-dir saved/          (users.json, acl.json, roles.json)
Exit: 0 no high finding; 1 at least one high finding; 2 bad arguments or a read failed.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass

import pve_ssh

#: Privileges that change the node, other identities or the permission system itself, or run arbitrary code in a guest.
#: Source: pveum chapter "Privileges" (Sys.Modify and Permissions.Modify carry the documented warning).
DANGEROUS = frozenset({
  "Permissions.Modify", "Sys.Modify", "Sys.Console", "Sys.PowerMgmt", "Sys.Incoming", "User.Modify", "Group.Allocate",
  "Realm.Allocate", "Realm.AllocateUser", "Datastore.Allocate", "VM.GuestAgent.Unrestricted", "VM.GuestAgent.FileWrite",
  "SDN.Allocate", "Mapping.Modify", "Pool.Allocate",
})
#: Identities exempt from the broad-grant rule by default: root@pam is the built-in superuser.
DEFAULT_ALLOWED = frozenset({"root@pam"})
READS = {
  "users": pve_ssh.pvesh("/access/users") + " --full 1",
  "acl": pve_ssh.pvesh("/access/acl"),
  "roles": pve_ssh.pvesh("/access/roles"),
}


@dataclass(frozen=True)
class Finding:
  """One audit finding.

  Args:
    severity: high, medium, low or info.
    rule: short rule id.
    subject: the user or token (user@realm!tokenid).
    detail: what was seen and why it matters.
  """

  severity: str
  rule: str
  subject: str
  detail: str


def role_privs(roles: list[dict]) -> dict[str, set[str]]:
  """Role id -> set of privileges.

  Args:
    roles: rows of GET /access/roles (privs is a comma-separated string, built-in roles included).

  Returns:
    The mapping.
  """
  return {r["roleid"]: {p for p in str(r.get("privs", "")).split(",") if p} for r in roles}


def user_of(ugid: str) -> str:
  """The user part of a token id, or the id itself.

  Args:
    ugid: user@realm or user@realm!tokenid.

  Returns:
    user@realm.
  """
  return ugid.split("!", 1)[0]


def covers(acl_path: str, propagate: bool, path: str) -> bool:
  """Whether an ACL entry on acl_path applies to path.

  Args:
    acl_path: where the entry is set.
    propagate: whether it is inherited below.
    path: the path in question.

  Returns:
    True when equal, or when path is below acl_path and the entry propagates.
  """
  if acl_path == path:
    return True
  base = acl_path.rstrip("/") + "/"
  return propagate and (acl_path == "/" or path.startswith(base))


def audit(users: list[dict], acl: list[dict], roles: list[dict], allowed: frozenset[str] = DEFAULT_ALLOWED) -> list[Finding]:
  """Audit identities against the least-privilege pattern.

  Rules: a token without privilege separation (high: it carries every right of its user); a grant on `/` with a role holding
  a dangerous privilege to anyone not allowed (high); a dangerous privilege granted to a token anywhere (medium); a
  privilege-separated token with an ACL its user lacks on that path (medium: the token's rights are the intersection, so the
  grant does nothing); a token that never expires (low); an enabled user or token with no ACL at all (info).

  Args:
    users: GET /access/users --full 1 rows (each may carry tokens).
    acl: GET /access/acl rows (path, roleid, type user/group/token, ugid, propagate).
    roles: GET /access/roles rows.
    allowed: identities exempt from the broad-grant rule.

  Returns:
    Findings, highest severity first.
  """
  privs = role_privs(roles)
  out: list[Finding] = []
  by_ugid: dict[str, list[dict]] = {}
  for row in acl:
    by_ugid.setdefault(row.get("ugid", ""), []).append(row)
  for user in users:
    uid = user["userid"]
    tokens = user.get("tokens") or []
    if not by_ugid.get(uid) and (tokens or user.get("enable", 1)) and uid not in allowed:
      out.append(Finding("info", "no-acl", uid, "user has no ACL entry of its own (group grants not checked)"))
    for tok in tokens:
      tid = f"{uid}!{tok['tokenid']}"
      if not tok.get("privsep", 1):
        out.append(Finding("high", "token-not-separated", tid,
                           "privsep=0: the token has every right of its user; recreate it with --privsep 1 and give it its own ACLs"))
      if not tok.get("expire"):
        out.append(Finding("low", "token-no-expiry", tid, "expire=0: the token never expires"))
  for row in acl:
    ugid, path, role = row.get("ugid", ""), row.get("path", ""), row.get("roleid", "")
    bad = sorted(privs.get(role, set()) & DANGEROUS)
    is_token = row.get("type") == "token"
    if path == "/" and bad and user_of(ugid) not in allowed:
      out.append(Finding("high", "broad-root-grant", ugid,
                         f"role {role} on / (propagate={row.get('propagate', 1)}) includes {', '.join(bad[:6])}"
                         f"{' ...' if len(bad) > 6 else ''}; scope it to a pool, storages and zones"))
    elif bad and is_token:
      out.append(Finding("medium", "dangerous-privilege", ugid, f"role {role} on {path} includes {', '.join(bad)}"))
    if is_token:
      user_rows = [r for r in by_ugid.get(user_of(ugid), []) if r.get("type") == "user"]
      if not any(covers(r["path"], bool(r.get("propagate", 1)), path) for r in user_rows):
        sep = next((t.get("privsep", 1) for u in users if u["userid"] == user_of(ugid) for t in (u.get("tokens") or [])
                    if f"{u['userid']}!{t['tokenid']}" == ugid), 1)
        if sep:
          out.append(Finding("medium", "token-acl-without-user", ugid,
                             f"token has {role} on {path} but its user has no grant there; the effective right is empty"))
  rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
  return sorted(out, key=lambda f: (rank[f.severity], f.subject, f.rule))


def render(findings: list[Finding]) -> str:
  """Plain-text report.

  Args:
    findings: from audit().

  Returns:
    One line per finding and a summary line.
  """
  lines = [f"{f.severity:<6} {f.rule:<24} {f.subject}: {f.detail}" for f in findings]
  counts = {s: sum(f.severity == s for f in findings) for s in ("high", "medium", "low", "info")}
  lines.append("summary: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
  return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 no high finding, 1 at least one, 2 bad arguments or a failed read.
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  src = ap.add_mutually_exclusive_group(required=True)
  src.add_argument("--host", help="node to read over SSH (key auth)")
  src.add_argument("--from-dir", help="folder with users.json, acl.json, roles.json")
  ap.add_argument("--ssh-user", default="root", help="SSH user (default root)")
  ap.add_argument("--allow-user", action="append", default=[], help="identity exempt from the broad-grant rule (repeatable)")
  ap.add_argument("--json", action="store_true", help="print findings as JSON")
  args = ap.parse_args(argv)
  try:
    if args.host:
      raw = pve_ssh.read_all(pve_ssh.ssh_runner(args.host, args.ssh_user), READS)
    else:
      raw = pve_ssh.dir_runner(args.from_dir)(READS)
    findings = audit(pve_ssh.as_json(raw, "users", []), pve_ssh.as_json(raw, "acl", []), pve_ssh.as_json(raw, "roles", []),
                     DEFAULT_ALLOWED | set(args.allow_user))
  except pve_ssh.PveReadError as exc:
    print(f"error: {exc}", file=sys.stderr)
    return 2
  print(json.dumps([asdict(f) for f in findings], indent=2) if args.json else render(findings))
  return 1 if any(f.severity == "high" for f in findings) else 0


if __name__ == "__main__":
  sys.exit(main())
