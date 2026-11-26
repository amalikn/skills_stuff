"""Tenant oversight for the node: the Proxmox side of every project's guests, checked against doc 10 (DL-072).

Lifted from me/nas scripts/lib/nas_tenants.py at 8d8af5c (continuum TASK-680, NAS DL-074/075) for the as-built engine's pve-tenants probe; the
only changes are review()'s optional registry, budgets and provider arguments (defaults give the original behaviour) and this paragraph.

The NAS project runs Proxmox as a service; other projects (Continuum first) are its tenants. This module turns one read of the node into stable
per-pool files under docs/as-built/captures/tenants/: each guest's Proxmox config (never inside the guest: that belongs to its project) and a
rule review, plus a summary across pools. Values that change every night (backup times, exact bytes used) are bucketed so a healthy node gives
byte-identical files and a diff appears only when something changes or breaks.

Run: not run directly; as_built_probes.probe_pve_tenants runs node_script() on the node and review() on the result. Tests: tests/test_as_built_tenants.py.
Safety: pure functions; reads the tenant registry and guest-budget files only (default config/tenants.conf, config/guest-budgets.conf). Runtime budget: under 1 s for tens of guests.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DISK = re.compile(r"^(scsi|virtio|sata|ide|efidisk|tpmstate|rootfs|mp|unused)\d*$")
HIDDEN = ("cipassword", "sshkeys", "digest")
BACKUP_MAX_AGE = 26 * 3600
GIB = 1024**3
PROVIDER = "me/nas"  # the owning project in config/tenants.conf whose pool is the provider's own: doc 10 tenant rules do not apply

NODE_SCRIPT = r"""
echo "== resources"; pvesh get /cluster/resources --type vm --output-format json
ids='import json,sys;[print(r["type"]+"/"+str(r["vmid"])) for r in json.load(sys.stdin)]'
for g in $(pvesh get /cluster/resources --type vm --output-format json | python3 -c "$ids"); do
  echo "== config $g"; pvesh get "/nodes/localhost/$g/config" --output-format json
done
echo "== unprotected"; pvesh get /cluster/backup-info/not-backed-up --output-format json
echo "== zfs"; zfs get -Hp -o name,property,value quota,used -d 1 tank 2>/dev/null
for s in $(awk '$1 == "storage" {print $2}' /etc/pve/jobs.cfg | sort -u); do
  echo "== backups $s"; pvesh get "/nodes/localhost/storage/$s/content" --content backup --output-format json
done
"""


def node_script() -> str:
  """Return the read-only shell run on the node as root.

  Args:
    None.

  Returns:
    Shell text that prints `== <section>` headers followed by JSON or tab-separated lines.

  """
  return NODE_SCRIPT


def parse(text: str) -> dict:
  """Split the node script's output into resources, configs, ZFS figures and backups.

  Args:
    text: stdout of node_script().

  Returns:
    {"resources", "configs" {vmid: {..}}, "zfs" {dataset: {"quota", "used"}}, "backups", "unprotected" [vmid]}; a failed section is empty.

  """
  data: dict = {"resources": [], "configs": {}, "zfs": {}, "backups": [], "unprotected": []}
  for block in re.split(r"^== ", text, flags=re.M)[1:]:
    head, _, body = block.partition("\n")
    try:
      if head == "resources":
        data["resources"] = json.loads(body or "[]")
      elif head.startswith("config "):
        data["configs"][int(head.rsplit("/", 1)[1])] = json.loads(body or "{}")
      elif head == "unprotected":
        data["unprotected"] = [int(g.get("vmid", -1)) for g in json.loads(body or "[]")]
      elif head.startswith("backups "):
        data["backups"] += json.loads(body or "[]")
      elif head == "zfs":
        for line in body.splitlines():
          name, prop, value = (line.split("\t") + ["", "", ""])[:3]
          if value.isdigit():
            data["zfs"].setdefault(name, {})[prop] = int(value)
    except ValueError:
      continue
  return data


def read_conf(path: Path, fields: int) -> dict[str, list[str]]:
  """Read a `|`-separated config file, skipping comments.

  Args:
    path: the file.
    fields: number of fields each line must have.

  Returns:
    {first field: the other fields}; an absent file gives {}.

  """
  out = {}
  if path.exists():
    for line in path.read_text(encoding="utf-8").splitlines():
      parts = line.strip().split("|")
      if line.strip() and not line.startswith("#") and len(parts) == fields:
        out[parts[0]] = parts[1:]
  return out


def disks(conf: dict) -> list[tuple[str, str]]:
  """List the guest's disks and mount points, without CD-ROMs.

  Args:
    conf: guest config.

  Returns:
    [(key, value)] sorted by key.

  """
  return sorted((k, str(v)) for k, v in conf.items() if DISK.match(k) and "media=cdrom" not in str(v))


def guest_findings(vmid: int, conf: dict, pool: str, vmid_range: tuple[int, int] | None) -> list[str]:
  """Check the doc 10 rules that the Proxmox config alone can show.

  Args:
    vmid: guest ID.
    conf: guest config.
    pool: the guest's pool.
    vmid_range: (first, last) VMIDs for the pool, or None when the pool is not registered.

  Returns:
    Findings, empty when the guest follows every rule checked.

  """
  found = []
  if vmid_range and not vmid_range[0] <= vmid <= vmid_range[1]:
    found.append(f"VMID {vmid} outside the pool's range {vmid_range[0]}-{vmid_range[1]} (rule 1)")
  if str(conf.get("protection", "0")) != "1" and str(conf.get("template", "0")) != "1":
    found.append("protection is off (rule 5)")
  allowed = {"local", "local-zfs", f"tank-{pool}"}
  for key, value in disks(conf):
    storage = value.split(":", 1)[0] if ":" in value.split(",", 1)[0] else ""
    if storage and storage not in allowed:
      found.append(f"{key} on storage {storage}, not one of {', '.join(sorted(allowed))} (rule 1)")
    if storage == f"tank-{pool}" and "backup=0" not in value:
      found.append(f"{key} is a data disk without backup=0 (rule 5, DL-044)")
  for key, value in sorted(conf.items()):
    if "secure" in str(value) and (DISK.match(key) or key.startswith(("virtiofs", "hostpci", "mp"))):
      found.append(f"{key} refers to tank/secure (rule 4)")
  return found


def backup_state(vmid: int, backups: list[dict], now: int) -> str:
  """Bucket the age of the guest's newest backup so a healthy night changes nothing.

  Args:
    vmid: guest ID.
    backups: backup volumes (vmid, ctime) from every vzdump storage.
    now: current Unix time.

  Returns:
    "ok (within 26 h)", "STALE: newest N days old" or "NONE: no backup found".

  """
  times = [int(b.get("ctime", 0)) for b in backups if int(b.get("vmid", -1)) == vmid]
  if not times:
    return "NONE: no backup found"
  age = now - max(times)
  return "ok (within 26 h)" if age <= BACKUP_MAX_AGE else f"STALE: newest {age // 86400} days old"


def show_config(conf: dict) -> str:
  """Render the guest config as sorted `key: value` lines, secrets and the digest left out.

  Args:
    conf: guest config.

  Returns:
    Text, one line per key.

  """
  return "".join(f"{k}: {v}\n" for k, v in sorted(conf.items()) if k not in HIDDEN)


def pool_file(
  pool: str, members: list[dict], data: dict, conf_dir: Path, now: int, registry: Path | None = None, budgets_file: Path | None = None, provider: str = PROVIDER
) -> tuple[str, list[str]]:
  """Build one pool's file: budget, quota, then each guest's rules, backup and config.

  Args:
    pool: pool name.
    members: the pool's guests from /cluster/resources.
    data: parse() output.
    conf_dir: the project's config/ folder.
    now: current Unix time.
    registry: the tenant registry; default conf_dir/tenants.conf.
    budgets_file: the guest budgets; default conf_dir/guest-budgets.conf.
    provider: the owning project whose pool is the provider's own.

  Returns:
    (file text, findings for the summary).

  """
  tenants = read_conf(registry or conf_dir / "tenants.conf", 4)
  budgets = read_conf(budgets_file or conf_dir / "guest-budgets.conf", 3)
  found = []
  row = tenants.get(pool)
  vmid_range = (int(row[0]), int(row[1])) if row else None
  text = f"== pool {pool}\nowner: {row[2] if row else 'NOT REGISTERED in config/tenants.conf'}\n"
  if not row:
    found.append(f"pool {pool} is not registered in config/tenants.conf")
  mem = sum(int(m.get("maxmem", 0)) for m in members) // 1024**2
  cpu = sum(int(m.get("maxcpu", 0)) for m in members)
  if pool in budgets:
    over = mem > int(budgets[pool][0]) or cpu > int(budgets[pool][1])
    text += f"budget: {mem} MiB / {cpu} vCPUs allocated of {budgets[pool][0]} MiB / {budgets[pool][1]} vCPUs ({'OVER' if over else 'ok'})\n"
    found += [f"pool {pool} over its RAM or vCPU budget (rule 3)"] if over else []
  else:
    text += f"budget: {mem} MiB / {cpu} vCPUs allocated; no budget in config/guest-budgets.conf\n"
  zfs = data["zfs"].get(f"tank/{pool}")
  if zfs and zfs.get("quota"):
    text += f"quota tank/{pool}: {zfs['quota'] // GIB} GiB, used {zfs.get('used', 0) // (10 * GIB) * 10}-{zfs.get('used', 0) // (10 * GIB) * 10 + 10} GiB\n"
  for m in sorted(members, key=lambda x: x["vmid"]):
    vmid, conf = m["vmid"], data["configs"].get(m["vmid"], {})
    rules = [] if row and row[2] == provider else guest_findings(vmid, conf, pool, vmid_range)
    backup = "NOT IN ANY BACKUP JOB" if vmid in data["unprotected"] else backup_state(vmid, data["backups"], now)
    found += [f"{pool} {m['type']} {vmid}: {f}" for f in rules + ([backup] if not backup.startswith("ok") else [])]
    text += f"\n== {m['type']} {vmid} {conf.get('name', '')}\nstatus: {m.get('status')}\nbackup: {backup}\n"
    text += "rules: " + ("provider pool, doc 10 not applied" if row and row[2] == provider else "; ".join(rules) or "ok") + "\n"
    text += f"== config {vmid}\n" + show_config(conf)
  return text, found


def addresses(configs: dict) -> dict[str, list[int]]:
  """Collect static IPv4 addresses from cloud-init ipconfig lines and LXC net lines.

  Args:
    configs: {vmid: config}.

  Returns:
    {address: [vmids]}.

  """
  out: dict[str, list[int]] = {}
  for vmid, conf in configs.items():
    for key, value in conf.items():
      if key.startswith(("ipconfig", "net")):
        for ip in re.findall(r"\bip=(\d+\.\d+\.\d+\.\d+)", str(value)):
          out.setdefault(ip, []).append(vmid)
  return out


def review(text: str, conf_dir: Path, now: int, registry: Path | None = None, budgets_file: Path | None = None, provider: str = PROVIDER) -> dict[str, str]:
  """Build every tenants/ file from one node read.

  Args:
    text: stdout of node_script().
    conf_dir: the project's config/ folder.
    now: current Unix time.
    registry: the tenant registry; default conf_dir/tenants.conf.
    budgets_file: the guest budgets; default conf_dir/guest-budgets.conf.
    provider: the owning project whose pool is the provider's own.

  Returns:
    {relative file under captures/: text}; empty when the node read gave no guests.

  """
  data = parse(text)
  pools: dict[str, list[dict]] = {}
  for r in data["resources"]:
    pools.setdefault(r.get("pool") or "(no pool)", []).append(r)
  if not pools:
    return {}
  files, found = {}, []
  for pool in sorted(pools):
    if pool == "(no pool)":
      found += [f"{r['type']} {r['vmid']} is in no pool" for r in pools[pool]]
      continue
    files[f"tenants/{pool}.txt"], pool_found = pool_file(pool, pools[pool], data, conf_dir, now, registry, budgets_file, provider)
    found += pool_found
  for ip, ids in sorted(addresses(data["configs"]).items()):
    if len(ids) > 1:
      found.append(f"address {ip} used by guests {', '.join(map(str, sorted(ids)))}")
  summary = "== tenants: one file per pool; Proxmox side only, never inside a tenant's guest (doc 10, DL-072)\n"
  summary += "".join(f"{p}: {len(pools[p])} guest(s)\n" for p in sorted(pools))
  summary += "== findings\n" + ("".join(f"- {f}\n" for f in found) if found else "none\n")
  files["tenants/summary.txt"] = summary
  return files
