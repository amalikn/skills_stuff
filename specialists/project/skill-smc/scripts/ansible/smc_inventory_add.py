#!/usr/bin/env python3
"""Add one new SMC (one site, one SMC) to an ansible-wifi inventory, any flavor: the three groups and the three vars files.

Run it with python3 on the controller (needs ansible-playbook on PATH; tsh only for --siteid-from-box):
  smc_inventory_add.py --flavor rct --env prod --host arrkapa-smc01 --siteid 663 --iridium            # plan only
  smc_inventory_add.py --flavor rcp --env prod --host new-smc01 --siteid 700 --size small --apply      # write
  smc_inventory_add.py --flavor rcp --env prod --host new-smc01 --siteid 700 --topology-from jigalong  # clone a sibling's layout
Plan by default; writes only with --apply, never overwrites a file, and refuses a host or site that is already there.
What it writes, following the convention of every existing site (skill-smc references/08_ansible-authoring.md, "Adding a new SMC"):
  inventories/<flavor>/<env>        [<site>_smc_bases] with the host; <site>_smc_bases under [smc_bases:children]; [<site>:children]
  group_vars/<site>.yml, host_vars/<host>.yml   rendered by ansible from this skill's templates/inventory/ (<flavor>/ first, then common/)
  topology_vars/<site>.yml          per flavor (FLAVORS below): the standard template, the sized nbn_accelerate template, an rcp reference
                                    profile (inventories/rcp/topology_vars/small.yml or big.yml), or any sibling site with --topology-from.
The repo's generator role (smc_generate_smc_files) is not used: it rewrites the whole inventory file through a JSON round-trip (reorders groups,
drops comments), and its rct template wrote the Iridium flag as the string "True". The site ID sets the backdoor tunnel port (50000 + id);
--siteid-from-box reads it from the SMC's own autossh -R port.
Exit 0 on a clean plan or apply, 1 when a check refuses, 2 on bad usage.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_REPO = "/Volumes/Data/_ansible/ansible-wifi"
TEMPLATES = Path(__file__).resolve().parents[2] / "templates" / "inventory"
BACKDOOR_BASE = 50000
TIMEOUT_S = 60
SIZES = ("small", "big")
# How each flavor gets its topology. "template": templates/inventory/<flavor or common>/topology_vars.j2. "sized_template": the same, with
# smc_size set from --size (--booth switches to common/). "sized_profile": clone inventories/<flavor>/topology_vars/<size>.yml from the repo.
FLAVORS = {
  "rct": "template",
  "wh": "template",
  "nbn_wh": "template",
  "nbn_accelerate": "sized_template",
  "rcp": "sized_profile",
}
FLAVOR_NOTES = {
  "rcp": "rcp host_vars usually carry the VoIP settings (smc_bases_sip_*, smc_bases_extension_*, smc_bases_main_did): add them by hand.",
  "nbn_wh": "nbn_wh: bungardi and darlngunaya change only on an operator decision; a new site does not touch them.",
}
RENDER_PLAY = """---
- hosts: localhost
  gather_facts: false
  connection: local
  tasks:
    - ansible.builtin.template:
        src: "{{ item.src }}"
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
  p = argparse.ArgumentParser(description=(__doc__ or "Add one new SMC to an ansible-wifi inventory.").splitlines()[0])
  p.add_argument("--repo", default=DEFAULT_REPO, help="ansible-wifi checkout (default %(default)s)")
  p.add_argument("--templates", default=str(TEMPLATES), help="template folder with common/ and <flavor>/ (default: this skill's)")
  p.add_argument("--flavor", required=True, choices=sorted(FLAVORS), help="inventory flavor")
  p.add_argument("--env", required=True, choices=["stage", "prod"], help="inventory file inside the flavor")
  p.add_argument("--host", required=True, help="SMC hostname as on Teleport, e.g. arrkapa-smc01")
  p.add_argument("--site", help="site name (default: host without its -smcNN/-rctNN/-whNN suffix)")
  sid = p.add_mutually_exclusive_group(required=True)
  sid.add_argument("--siteid", type=int, help="Eclipse site ID")
  sid.add_argument("--siteid-from-box", action="store_true", help="read the ID from the SMC's autossh -R port over tsh")
  p.add_argument("--iridium", action="store_true", help="set smc_bases_iridium: true in host_vars")
  p.add_argument("--size", choices=SIZES, help="x86 hardware size: nbn_accelerate template NIC names, rcp reference profile")
  p.add_argument("--booth", action="store_true", help="nbn_accelerate only: the standard one-NIC booth topology")
  p.add_argument("--topology-from", metavar="SITE", help="clone inventories/<flavor>/topology_vars/<SITE>.yml, host renamed (any flavor)")
  p.add_argument("--allow-shared-siteid", action="store_true", help="accept a site ID another host_vars already uses")
  p.add_argument("--apply", action="store_true", help="write the files and the inventory (default: plan only)")
  return p.parse_args(argv)


def default_site(host):
  """Derive the site name from a hostname, as the fleet names SMCs <site>-smcNN.

  Args:
    host: SMC hostname.

  Returns:
    the site name, or the host unchanged when it has no -smcNN/-rctNN/-whNN suffix.
  """
  return re.sub(r"-(smc|rct|wh)\d+$", "", host)


def topology_source(a):
  """Decide where the new site's topology comes from, from the flavor and the options.

  Args:
    a: parsed arguments (flavor, size, booth, topology_from).

  Returns:
    ("template", name, smc_size or None) or ("clone", site, None).

  Raises:
    SystemExit: (exit 2) on an option that does not fit the flavor or a missing --size.
  """
  kind = FLAVORS[a.flavor]
  if a.booth and a.flavor != "nbn_accelerate":
    usage("--booth is for nbn_accelerate only")
  if a.topology_from:
    if a.booth or a.size:
      usage("--topology-from takes the whole layout from the sibling; drop --size/--booth")
    return ("clone", a.topology_from, None)
  if kind == "template":
    if a.size:
      usage(f"--size does not apply to {a.flavor} (one standard layout)")
    return ("template", "topology_vars.j2", None)
  if kind == "sized_template" and a.booth:
    return ("template", "common/topology_vars.j2", None)
  if not a.size:
    usage(f"{a.flavor} needs --size {'|'.join(SIZES)} (or --topology-from <site>{', or --booth' if kind == 'sized_template' else ''})")
  if kind == "sized_template":
    return ("template", "topology_vars.j2", a.size)
  return ("clone", a.size, None)


def usage(msg):
  """Stop with a usage error.

  Args:
    msg: what was wrong.

  Raises:
    SystemExit: always, with exit code 2.
  """
  print(f"bad usage: {msg}", file=sys.stderr)
  raise SystemExit(2)


def template_path(tdir, flavor, name):
  """Find a template: the flavor's own first, then common/; a name with a folder ("common/x.j2") is taken as given.

  Args:
    tdir: template folder.
    flavor: inventory flavor.
    name: template file name, or folder/name.

  Returns:
    the template path.

  Raises:
    SystemExit: when no folder has it.
  """
  for sub in [""] if "/" in name else [flavor, "common"]:
    p = Path(tdir, sub, name)
    if p.is_file():
      return p
  sys.exit(f"REFUSED: no template {name} under {tdir}/{flavor}/ or common/")


def siteid_from_box(host):
  """Read the site ID from the SMC's reverse tunnel (autossh -R <50000+id>:127.0.0.1:22).

  Args:
    host: SMC hostname reachable with tsh ssh root@<host>.

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
  text = Path(inv_file).read_text()
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
    hv = Path(repo, "inventories", inv, "host_vars")
    if hv.is_dir():
      shared += [f"{inv}/{f.name}" for f in sorted(hv.glob("*.yml")) if pat.search(f.read_text())]
  if shared:
    msg = f"site ID {siteid} (backdoor port {BACKDOOR_BASE + siteid}) is already used by {', '.join(shared)}"
    if allow_shared:
      print(f"WARN  {msg}")
    else:
      problems.append(msg + " (an SMC still on a generic image's ID? confirm, then --allow-shared-siteid)")
  return problems


def render(tdir, flavor, files, values, out):
  """Render templates into out/ with ansible, so Jinja behaves as in the repo's own runs.

  Args:
    tdir: template folder.
    flavor: inventory flavor.
    files: {output key: template name}.
    values: template variables (smc_name, site_name, eclipse_site_ID, smc_bases_iridium, smc_size).
    out: empty directory to render into.

  Returns:
    {output key: rendered path}.

  Raises:
    SystemExit: when a template is missing or ansible fails.
  """
  loop = [{"src": str(template_path(tdir, flavor, name)), "dest": f"{key}.yml"} for key, name in files.items()]
  play, evars = os.path.join(out, "render.yml"), os.path.join(out, "vars.json")
  Path(play).write_text(RENDER_PLAY)
  Path(evars).write_text(json.dumps({"out": out, "files": loop, **values}))
  r = subprocess.run(["ansible-playbook", play, "-e", f"@{evars}"], capture_output=True, text=True, timeout=TIMEOUT_S * 3)
  if r.returncode:
    sys.exit(f"REFUSED: rendering failed:\n{r.stdout[-2000:]}{r.stderr[-1000:]}")
  return {key: os.path.join(out, f"{key}.yml") for key in files}


def rename_hosts(text, from_site, host):
  """Replace every whole host name of a site in a topology text with the new host name.

  The whole token is replaced: `generic-rct01-iridium-20241121` becomes the new host, not `<host>-iridium-20241121`. A `\\b` after the digits
  matched inside such a name and kept the suffix, so the topology vars plugin keyed the clone under a name no host had and every topology
  variable was undefined for the new box (malik-bench-rct01, 2026-11-20).

  Args:
    text: the topology_vars file text.
    from_site: the source site (hosts are `<from_site>-smcNN`, `-rctNN` or `-whNN`, with any suffix).
    host: the new hostname.

  Returns:
    (new text, number of names replaced).
  """
  return re.subn(rf"(?<![\w.-]){re.escape(from_site)}-(?:smc|rct|wh)\d+[\w.-]*(?![\w.-])", host, text)


def clone_topology(repo, flavor, from_site, host, out):
  """Copy a sibling site's topology_vars with its host renamed to the new one.

  Args:
    repo: ansible-wifi checkout.
    flavor: inventory flavor.
    from_site: the site whose topology_vars/<from_site>.yml is copied (an rcp size profile is a site too).
    host: new hostname.
    out: directory to write topology_vars.yml into.

  Returns:
    the written path.

  Raises:
    SystemExit: when the sibling file is missing or names no host to rename.
  """
  src = Path(repo, "inventories", flavor, "topology_vars", f"{from_site}.yml")
  if not src.is_file():
    sys.exit(f"REFUSED: no {src.relative_to(repo)} to clone")
  new, n = rename_hosts(src.read_text(), from_site, host)
  if not n:
    sys.exit(f"REFUSED: {src.relative_to(repo)} names no {from_site}-smcNN host to rename; copy it by hand")
  # Fleet files carry trailing spaces and "key:  value"; YAML ignores both, the pre-push lint does not.
  tidy = [re.sub(r"^(\s*[\w-]+:) {2,}(?=\S)", r"\1 ", line.rstrip()) for line in new.splitlines()]
  dest = os.path.join(out, "topology_vars.yml")
  Path(dest).write_text("\n".join(tidy) + "\n")
  return dest


def output_faults(paths):
  """Find faults the repo's pre-push lint or a run would trip on in the files about to be written.

  Args:
    paths: {output key: file path}.

  Returns:
    a list of fault lines (empty when clean).
  """
  faults = []
  for key, p in paths.items():
    for i, line in enumerate(Path(p).read_text().splitlines(), 1):
      if line != line.rstrip():
        faults.append(f"{key}.yml:{i}: trailing whitespace")
      if re.match(r"\s*name:\s*$", line):
        faults.append(f"{key}.yml:{i}: empty name (an interface without its NIC name?)")
      if re.match(r"\s*smc_bases_iridium:\s*[\"']", line):
        faults.append(f"{key}.yml:{i}: smc_bases_iridium quoted; the fleet writes a plain true")
  return faults


def nic_summary(path):
  """List the NIC names and VLAN IDs in a topology file, for the operator to check against the SMC.

  Args:
    path: topology_vars file.

  Returns:
    one line: the NIC names and the VLAN IDs.
  """
  text = Path(path).read_text()
  nics = sorted(set(re.findall(r"^\s*name:\s*((?:en|eth|wl)\S+)\s*$", text, re.M)))
  vlans = re.findall(r"^\s*vlanid:\s*(\d+)\s*$", text, re.M)
  return f"NICs {', '.join(nics) or 'none'}; VLAN IDs {', '.join(vlans) or 'none'}"


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


def build(a, site, siteid, out):
  """Produce the three vars files for the new SMC in out/.

  Args:
    a: parsed arguments.
    site: site name.
    siteid: Eclipse site ID.
    out: empty directory.

  Returns:
    ({output key: path}, a description of the topology source).

  Raises:
    SystemExit: on a missing template or sibling, or a failed render.
  """
  kind, name, size = topology_source(a)
  values = {"smc_name": a.host, "site_name": site, "eclipse_site_ID": siteid, "smc_bases_iridium": a.iridium, "smc_size": size or ""}
  files = {"group_vars": "group_vars.j2", "host_vars": "host_vars.j2"}
  if kind == "template":
    files["topology_vars"] = name
  paths = render(a.templates, a.flavor, files, values, out)
  if kind == "clone":
    paths["topology_vars"] = clone_topology(a.repo, a.flavor, name, a.host, out)
    return paths, f"clone of {a.flavor}/topology_vars/{name}.yml"
  return paths, f"template {template_path(a.templates, a.flavor, name).relative_to(a.templates)}" + (f" (smc_size {size})" if size else "")


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
  print(
    f"PLAN  {a.host}: flavor {a.flavor}, env {a.env}, site {site}, site ID {siteid} (backdoor port {BACKDOOR_BASE + siteid})"
    + (", Iridium" if a.iridium else "")
  )
  problems = checks(a.repo, inv_file, a.flavor, a.host, site, siteid, a.allow_shared_siteid)
  if problems:
    print("\n".join(f"REFUSED: {p}" for p in problems))
    return 1
  with tempfile.TemporaryDirectory() as out:
    paths, topo = build(a, site, siteid, out)
    faults = output_faults(paths)
    if faults:
      print("\n".join(f"REFUSED: {f}" for f in faults))
      return 1
    targets = {"group_vars": site, "host_vars": a.host, "topology_vars": site}
    for sub, src in paths.items():
      dest = os.path.join(a.repo, "inventories", a.flavor, sub, f"{targets[sub]}.yml")
      note = f"; {topo}" if sub == "topology_vars" else ""
      print(f"{'WRITE' if a.apply else 'PLAN '} {os.path.relpath(dest, a.repo)} ({len(Path(src).read_text().splitlines())} lines{note})")
      if a.apply:
        with open(dest, "x") as g:
          g.write(Path(src).read_text())
    print(f"CHECK {nic_summary(paths['topology_vars'])}: match them to the SMC (tsh ssh root@{a.host} ip -br link)")
    new = insert_groups(Path(inv_file).read_text(), a.host, site)
    print(f"{'WRITE' if a.apply else 'PLAN '} {os.path.relpath(inv_file, a.repo)}: [{site}_smc_bases], smc_bases:children, [{site}:children]")
    if a.apply:
      Path(inv_file).write_text(new)
  if a.flavor in FLAVOR_NOTES:
    print(f"NOTE  {FLAVOR_NOTES[a.flavor]}")
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
