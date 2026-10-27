#!/usr/bin/env python3
"""Add one new SMC (one site, one box) to an ansible-wifi inventory: the three groups and the three vars files.

Run it with python3 on the controller (needs ansible-playbook on PATH; tsh only for --siteid-from-box):
  smc_inventory_add.py --flavor rct --env stage --host php-rct-smc01 --siteid-from-box          # plan only
  smc_inventory_add.py --flavor rct --env stage --host php-rct-smc01 --siteid 181 --apply       # write
Plan by default; writes only with --apply, never overwrites a file, and refuses a host or site that is already there.
What it writes, following the convention of every existing site (skill-smc references/08_ansible-authoring.md, "Adding a new SMC"):
  inventories/<flavor>/<env>        [<site>_smc_bases] with the host; <site>_smc_bases under [smc_bases:children]; [<site>:children]
  group_vars/<site>.yml, host_vars/<host>.yml, topology_vars/<site>.yml   rendered by ansible from the repo's own generator
                                    templates (roles/smc_generate_smc_files/templates/<flavor>/), so the output matches that role's.
The generator role itself is not used because it rewrites the whole inventory file through a JSON round-trip (reorders groups, drops
comments). The site ID sets the backdoor tunnel port (50000 + id); --siteid-from-box reads it from the box's own autossh -R port.
Exit 0 on a clean plan or apply, 1 when a check refuses, 2 on bad usage.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

DEFAULT_REPO = "/Volumes/Data/_ansible/ansible-wifi"
TEMPLATES = "roles/smc_generate_smc_files/templates"
BACKDOOR_BASE = 50000
TIMEOUT_S = 60
RENDER_PLAY = """---
- hosts: localhost
  gather_facts: false
  connection: local
  tasks:
    - ansible.builtin.template:
        src: "{{ tpl }}/{{ item.src }}"
        dest: "{{ out }}/{{ item.dest }}"
        mode: "0644"
      loop: "{{ files }}"
"""


def parse_args(argv):
  """Read the command line.

  Args:
    argv: arguments after the program name.

  Returns:
    the parsed argparse.Namespace.
  """
  p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  p.add_argument("--repo", default=DEFAULT_REPO, help="ansible-wifi checkout (default %(default)s)")
  p.add_argument("--flavor", required=True, help="inventory flavor: rct, wh, nbn_accelerate (needs generator templates)")
  p.add_argument("--env", required=True, choices=["stage", "prod"], help="inventory file inside the flavor")
  p.add_argument("--host", required=True, help="box hostname as on Teleport, e.g. arrkapa-smc01")
  p.add_argument("--site", help="site name (default: host without its -smcNN/-rctNN suffix)")
  sid = p.add_mutually_exclusive_group(required=True)
  sid.add_argument("--siteid", type=int, help="Eclipse site ID")
  sid.add_argument("--siteid-from-box", action="store_true", help="read the ID from the box's autossh -R port over tsh")
  p.add_argument("--iridium", action="store_true", help="rct only: set smc_bases_iridium")
  p.add_argument("--booth", action="store_true", help="nbn_accelerate only: use topology_vars_booth.j2")
  p.add_argument("--allow-shared-siteid", action="store_true", help="accept a site ID another host_vars already uses")
  p.add_argument("--apply", action="store_true", help="write the files and the inventory (default: plan only)")
  return p.parse_args(argv)


def default_site(host):
  """Derive the site name from a hostname, as the fleet names boxes <site>-smcNN.

  Args:
    host: box hostname.

  Returns:
    the site name, or the host unchanged when it has no -smcNN/-rctNN/-whNN suffix.
  """
  return re.sub(r"-(smc|rct|wh)\d+$", "", host)


def siteid_from_box(host):
  """Read the site ID from the box's reverse tunnel (autossh -R <50000+id>:127.0.0.1:22).

  Args:
    host: box hostname reachable with tsh ssh root@<host>.

  Returns:
    the site ID as an int.

  Raises:
    SystemExit: when tsh fails or no single backdoor port is found.
  """
  try:
    out = subprocess.run(["tsh", "ssh", f"root@{host}", "ps -eo args"], capture_output=True, text=True, timeout=TIMEOUT_S, check=True).stdout
  except (subprocess.SubprocessError, OSError) as exc:
    sys.exit(f"REFUSED: could not read processes on {host} over tsh: {exc}")
  ports = sorted(set(re.findall(r"-R (5\d{4}):127\.0\.0\.1:22\b", out)))
  if len(ports) != 1:
    sys.exit(f"REFUSED: expected one autossh -R <port>:127.0.0.1:22 on {host}, found {ports or 'none'}; pass --siteid")
  return int(ports[0]) - BACKDOOR_BASE


def checks(repo, inv_file, flavor, host, site, siteid, allow_shared):
  """Refuse a host or site already in the inventory; report a site ID other host_vars already use.

  Args:
    repo: ansible-wifi checkout.
    inv_file: path of the inventory file to change.
    flavor: inventory flavor.
    host: new hostname.
    site: new site name.
    siteid: new site ID.
    allow_shared: accept a site ID already used.

  Returns:
    a list of problem lines (empty when all checks pass).
  """
  problems = []
  inv_dir = os.path.join(repo, "inventories", flavor)
  text = open(inv_file).read()
  if re.search(rf"^{re.escape(host)}\s*$", text, re.M):
    problems.append(f"host {host} is already in {inv_file}")
  if re.search(rf"^\[{re.escape(site)}(_smc_bases|:children)\]", text, re.M):
    problems.append(f"site group {site} is already in {inv_file}")
  for sub, name in (("group_vars", site), ("host_vars", host), ("topology_vars", site)):
    if os.path.exists(os.path.join(inv_dir, sub, f"{name}.yml")):
      problems.append(f"{sub}/{name}.yml already exists")
  pat = re.compile(rf"^site_eclipse_siteid:\s*{siteid}\s*$", re.M)
  shared = []
  for inv in sorted(os.listdir(os.path.join(repo, "inventories"))):
    hv = os.path.join(repo, "inventories", inv, "host_vars")
    if os.path.isdir(hv):
      shared += [f"{inv}/{f}" for f in sorted(os.listdir(hv)) if f.endswith(".yml") and pat.search(open(os.path.join(hv, f)).read())]
  if shared:
    msg = f"site ID {siteid} (backdoor port {BACKDOOR_BASE + siteid}) is already used by {', '.join(shared)}"
    if allow_shared:
      print(f"WARN  {msg}")
    else:
      problems.append(msg + " (a box still on a generic image's ID? confirm, then --allow-shared-siteid)")
  return problems


def render(repo, flavor, host, site, siteid, iridium, booth, out):
  """Render the generator's three templates for one row into out/, using ansible so the output matches the generator role.

  Args:
    repo: ansible-wifi checkout.
    flavor: inventory flavor (a folder under the generator templates).
    host: the CSV row's smc_name.
    site: the CSV row's site_name.
    siteid: the CSV row's eclipse_site_ID.
    iridium: rct smc_bases_iridium.
    booth: nbn_accelerate booth topology.
    out: empty directory to render into.

  Returns:
    {"group_vars": path, "host_vars": path, "topology_vars": path}.

  Raises:
    SystemExit: when the flavor has no templates or ansible fails.
  """
  tpl = os.path.join(repo, TEMPLATES, flavor)
  if not os.path.isdir(tpl):
    sys.exit(f"REFUSED: no generator templates for flavor {flavor} under {TEMPLATES}/; add the files by hand from a sibling site")
  topo = "topology_vars_booth.j2" if booth else "topology_vars.j2"
  files = [{"src": "group_vars.j2", "dest": "group_vars.yml"}, {"src": "host_vars.j2", "dest": "host_vars.yml"}, {"src": topo, "dest": "topology_vars.yml"}]
  ev = {"tpl": tpl, "out": out, "files": files, "smc_name": host, "site_name": site, "eclipse_site_ID": siteid, "smc_bases_iridium": iridium}
  play, evars = os.path.join(out, "render.yml"), os.path.join(out, "vars.json")
  open(play, "w").write(RENDER_PLAY)
  json.dump(ev, open(evars, "w"))
  r = subprocess.run(["ansible-playbook", play, "-e", f"@{evars}"], capture_output=True, text=True, timeout=TIMEOUT_S * 3)
  if r.returncode:
    sys.exit(f"REFUSED: rendering failed:\n{r.stdout[-2000:]}{r.stderr[-1000:]}")
  return {k: os.path.join(out, f"{k}.yml") for k in ("group_vars", "host_vars", "topology_vars")}


def insert_groups(text, host, site):
  """Add the three groups to an inventory file's text in the existing sites' layout.

  Args:
    text: current inventory file content.
    host: new hostname.
    site: new site name.

  Returns:
    the new content.

  Raises:
    SystemExit: when the file has no [smc_bases:children] section.
  """
  lines = text.split("\n")
  try:
    kids = lines.index("[smc_bases:children]")
  except ValueError:
    sys.exit("REFUSED: inventory has no [smc_bases:children] section; add the groups by hand")
  end = kids + 1
  while end < len(lines) and lines[end].strip() and not lines[end].startswith("["):
    end += 1
  lines.insert(end, f"{site}_smc_bases")
  lines[kids:kids] = [f"[{site}_smc_bases]", host, ""]
  tail = len(lines)
  while tail > 0 and (not lines[tail - 1].strip() or lines[tail - 1].lstrip().startswith("#")):
    tail -= 1
  lines[tail:tail] = ["", f"[{site}:children]", f"{site}_smc_bases"]
  return "\n".join(lines)


def main(argv):
  """Plan, and with --apply write, a new SMC's inventory entries and vars files.

  Args:
    argv: arguments after the program name.

  Returns:
    the exit code.
  """
  a = parse_args(argv)
  site = a.site or default_site(a.host)
  inv_file = os.path.join(a.repo, "inventories", a.flavor, a.env)
  if not os.path.isfile(inv_file):
    print(f"bad usage: no inventory file {inv_file}", file=sys.stderr)
    return 2
  siteid = siteid_from_box(a.host) if a.siteid_from_box else a.siteid
  print(f"PLAN  {a.host}: flavor {a.flavor}, env {a.env}, site {site}, site ID {siteid} (backdoor port {BACKDOOR_BASE + siteid})")
  problems = checks(a.repo, inv_file, a.flavor, a.host, site, siteid, a.allow_shared_siteid)
  if problems:
    print("\n".join(f"REFUSED: {p}" for p in problems))
    return 1
  with tempfile.TemporaryDirectory() as out:
    rendered = render(a.repo, a.flavor, a.host, site, siteid, a.iridium, a.booth, out)
    targets = {"group_vars": site, "host_vars": a.host, "topology_vars": site}
    for sub, src in rendered.items():
      dest = os.path.join(a.repo, "inventories", a.flavor, sub, f"{targets[sub]}.yml")
      print(f"{'WRITE' if a.apply else 'PLAN '} {os.path.relpath(dest, a.repo)} ({sum(1 for _ in open(src))} lines)")
      if a.apply:
        with open(src) as f, open(dest, "x") as g:
          g.write(f.read())
    new = insert_groups(open(inv_file).read(), a.host, site)
    print(f"{'WRITE' if a.apply else 'PLAN '} {os.path.relpath(inv_file, a.repo)}: [{site}_smc_bases], smc_bases:children, [{site}:children]")
    if a.apply:
      open(inv_file, "w").write(new)
  if not a.apply:
    print("plan only; rerun with --apply to write")
    return 0
  r = subprocess.run(["ansible-inventory", "-i", inv_file, "--graph", site], capture_output=True, text=True, timeout=TIMEOUT_S, cwd=a.repo)
  print(r.stdout.strip() or r.stderr.strip())
  if r.returncode or a.host not in r.stdout:
    print("CHECK FAILED: ansible-inventory does not show the host under the site group")
    return 1
  print("next: lint (./lint_new.sh), then a check run, e.g. smc_change.yml -l", a.host)
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
