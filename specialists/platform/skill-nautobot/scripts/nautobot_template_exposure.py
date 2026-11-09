"""Read-only exposure check for Nautobot's template-sandbox and cable-path advisories (GHSA-2v7j-x3g6-qj94, GHSA-8f2w-54mq-66gg, GHSA-m6h7-g92h-9p44).

The template advisories need a user who can author templates Nautobot renders against objects (Custom Links, Job Buttons, Export Templates,
Computed Fields and similar); the cable-path one needs constrained view permissions on cable terminations, cables or devices. A grant over a
whole app (all of `extras`) is how a machine account picks these up unnoticed (found 2026-11-09 on one deployment: its machine-writer group held
Custom Link and Secret authoring through an app-wide grant).

Two steps, stdlib only here: `--query` prints a read-only snippet for `nautobot-server nbshell` (or a project's read-only query runner) that
dumps the facts as one JSON line (version, active users and groups, enabled ObjectPermissions, template texts; no token, hash or secret value);
`--report FILE` (or `-` for stdin) classifies that JSON: AUTHORING grants, CONSTRAINED_CABLE_VIEW grants, templates naming `user` or `request`.

Run: python3 nautobot_template_exposure.py --query > q.py; <run q.py in nbshell> > facts.json; python3 nautobot_template_exposure.py --report facts.json
Exit: 0 report printed; 2 bad input. Runtime: one shell start plus a few queries; the report is instant.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

TEMPLATE_MODELS = frozenset({("extras", m) for m in ("customlink", "jobbutton", "exporttemplate", "computedfield", "webhook", "secret", "graphqlquery")})
CABLE_MODELS = frozenset({("dcim", m) for m in ("cable", "interface", "frontport", "rearport", "consoleport", "consoleserverport", "powerport",
                                               "poweroutlet", "powerfeed", "device")} | {("circuits", "circuittermination")})
_REF = re.compile(r"\b(user|request)\b")

#: Read-only nbshell snippet: prints one line `FACTS <json>`. No ORM write verbs, no token or secret fields.
QUERY = '''import json
from django.contrib.auth import get_user_model
from nautobot import __version__
from nautobot.extras import models as em
from nautobot.users.models import ObjectPermission
F = {"CustomLink": ("text", "target_url"), "JobButton": ("text",), "ExportTemplate": ("template_code",), "ComputedField": ("template",)}
facts = {"version": __version__,
  "users": [{"name": u.username, "superuser": u.is_superuser, "groups": sorted(g.name for g in u.groups.all())}
            for u in get_user_model().objects.filter(is_active=True).order_by("username")],
  "permissions": [{"name": p.name, "actions": list(p.actions), "constraints": p.constraints,
                   "types": sorted([c.app_label, c.model] for c in p.object_types.all()),
                   "members": sorted(u.username for u in p.users.all()) + sorted("group:" + g.name for g in p.groups.all())}
                  for p in ObjectPermission.objects.filter(enabled=True)],
  "templates": [{"model": m, "name": str(r), "texts": [str(getattr(r, f, "") or "") for f in fs]}
                for m, fs in F.items() for r in getattr(em, m).objects.all()]}
print("FACTS " + json.dumps(facts, default=str))
'''


def classify(perm: dict) -> list[str]:
  """Name the advisory-relevant grants one ObjectPermission makes.

  Args:
    perm: {"name", "actions": list, "types": iterable of (app_label, model), "constraints": dict or None, "members": list}.

  Returns:
    Finding lines: AUTHORING for add/change on a template-bearing model, CONSTRAINED_CABLE_VIEW for constrained view on a cable-path model.
  """
  out = []
  actions, types = set(perm["actions"]), {tuple(t) for t in perm["types"]}
  if types & TEMPLATE_MODELS and actions & {"add", "change"}:
    out.append(f"AUTHORING {perm['name']}: {sorted(actions)} on {sorted(m for _, m in types & TEMPLATE_MODELS)}; members {perm['members']}")
  if types & CABLE_MODELS and "view" in actions and perm.get("constraints"):
    out.append(f"CONSTRAINED_CABLE_VIEW {perm['name']}: {sorted(m for _, m in types & CABLE_MODELS)}; members {perm['members']}")
  return out


def referencing(texts: list[str]) -> bool:
  """Whether any rendered text of a template refers to `user` or `request`.

  Args:
    texts: the template's rendered fields.

  Returns:
    True when one names `user` or `request` as a word.
  """
  return any(_REF.search(t or "") for t in texts)


def report(facts: dict) -> list[str]:
  """Turn the dumped facts into report lines.

  Args:
    facts: the JSON object QUERY prints.

  Returns:
    Lines: version, users, findings, per-model template counts and references.
  """
  lines = [f"nautobot_version {facts['version']}"]
  lines += [f"user {u['name']} superuser {u['superuser']} groups {u['groups']}" for u in facts["users"]]
  for p in facts["permissions"]:
    lines += classify(p)
  counts: dict[str, list[str]] = {m: [] for m in ("ComputedField", "CustomLink", "ExportTemplate", "JobButton")}
  for t in facts["templates"]:
    hits = counts.setdefault(t["model"], [])
    if referencing(t["texts"]):
      hits.append(t["name"])
  totals = {m: sum(1 for t in facts["templates"] if t["model"] == m) for m in counts}
  lines += [f"{m} count {totals[m]} referencing_user_or_request {counts[m]}" for m in sorted(counts)]
  return lines


def main(argv: list[str] | None = None) -> int:
  """Print the query, or classify dumped facts.

  Args:
    argv: command-line arguments (default sys.argv[1:]).

  Returns:
    0 on success, 2 when the facts cannot be read.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  mode = ap.add_mutually_exclusive_group(required=True)
  mode.add_argument("--query", action="store_true", help="print the read-only nbshell snippet")
  mode.add_argument("--report", metavar="FILE", help="classify the snippet's output (a file, or - for stdin)")
  args = ap.parse_args(argv)
  if args.query:
    print(QUERY, end="")
    return 0
  text = sys.stdin.read() if args.report == "-" else open(args.report, encoding="utf-8").read()
  line = next((ln for ln in text.splitlines() if ln.startswith("FACTS ")), None)
  if line is None:
    print("no FACTS line in the input", file=sys.stderr)
    return 2
  print("\n".join(report(json.loads(line[6:]))))
  return 0


if __name__ == "__main__":
  sys.exit(main())
