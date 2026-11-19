#!/usr/bin/env python3
"""Group each inventory flavor's topology_vars files by layout, with site and host names normalised, to find the standard layout and the sites off it.

Run: python3 scripts/ansible/topology_variance.py [--repo /Volumes/Data/_ansible/ansible-wifi] [--show 8] [flavor ...]   (or `just topology_variance`)
Read-only: reads inventories/<flavor>/topology_vars/*.yml (never the hidden .<site>.yml caches) and prints one line per layout. Use it before
changing a topology template (skill-smc templates/inventory/) or adding a site, to see which layout most sites share; on 2026-11-19 it showed
315 of 328 rct sites on one layout, and rcp 24 files in 19 layouts. Whitespace is ignored, so a layout differing only in trailing spaces counts
as the same. Exit 0, or 2 on a missing repo or flavor.
"""

import argparse
import collections
import hashlib
import re
import sys
from pathlib import Path

DEFAULT_REPO = "/Volumes/Data/_ansible/ansible-wifi"
DEFAULT_FLAVORS = ("rct", "wh", "nbn_wh", "nbn_accelerate", "rcp")


def parse_args(argv):
  """Read the command line.

  Args:
    argv: arguments after the program name.

  Returns:
    the parsed argparse.Namespace.
  """
  p = argparse.ArgumentParser(description=(__doc__ or "Group topology_vars files by layout.").splitlines()[0])
  p.add_argument("--repo", default=DEFAULT_REPO, help="ansible-wifi checkout (default %(default)s)")
  p.add_argument("--show", type=int, default=8, help="layouts to list per flavor, largest first (default %(default)s)")
  p.add_argument("flavors", nargs="*", default=list(DEFAULT_FLAVORS), help="inventory flavors (default: %(default)s)")
  return p.parse_args(argv)


def normalise(text, site):
  """Replace a site's own names with SITE and drop whitespace differences, so two sites with one layout compare equal.

  Args:
    text: topology_vars file content.
    site: the file's site name (its stem).

  Returns:
    the normalised text.
  """
  text = re.sub(rf"{re.escape(site)}(-[a-z]*\d+)?", "SITE", text)
  return "\n".join(re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip())


def layouts(topo_dir):
  """Group a flavor's topology files by normalised content.

  Args:
    topo_dir: inventories/<flavor>/topology_vars.

  Returns:
    a list of (layout id, [site, ...]), largest group first, then by first site.
  """
  groups = collections.defaultdict(list)
  for f in sorted(Path(topo_dir).glob("*.yml")):
    if not f.name.startswith("."):
      digest = hashlib.sha1(normalise(f.read_text(), f.stem).encode()).hexdigest()[:8]
      groups[digest].append(f.stem)
  return sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[1][0]))


def main(argv):
  """Print the layout groups per flavor.

  Args:
    argv: arguments after the program name.

  Returns:
    the exit code.
  """
  a = parse_args(argv)
  rc = 0
  for flavor in a.flavors:
    topo_dir = Path(a.repo, "inventories", flavor, "topology_vars")
    if not topo_dir.is_dir():
      print(f"bad usage: no {topo_dir}", file=sys.stderr)
      rc = 2
      continue
    groups = layouts(topo_dir)
    print(f"== {flavor}: {sum(len(s) for _, s in groups)} files, {len(groups)} layouts")
    for digest, sites in groups[: a.show]:
      more = f" (+{len(sites) - 4} more)" if len(sites) > 4 else ""
      print(f"  {digest} x{len(sites)}: {', '.join(sites[:4])}{more}")
  return rc


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
