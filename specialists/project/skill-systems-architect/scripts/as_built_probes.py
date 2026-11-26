"""Probe library for as_built.py: read-only capture of one declared target into {relative file: text} (DL-264, DL-265 in continuum).

Imported by scripts/as_built.py, never run on its own. Every probe only reads: shell commands over SSH or locally (`ssh = "local"` or no ssh), HTTPS
GETs, and reads of an API token's value from KeePassXC or a root-only secrets file ([capture] secrets; never written out). Each probe returns raw text;
masking and churn filtering happen in as_built.py so every probe gets them. Python 3.11+ (the Proxmox node runs 3.13).
Probe types (ssh = "local" or absent runs on this machine for all but http/cloudflare/hand): proxmox-node, pve-pool, pve-tenants, linux-host, tls-endpoint, http-endpoint, cloudflare-dns, cloudflare (DNS, tunnels, Access), command,
local-tools, hand. A tool-backed type
(cloudflare-export through cf-terraforming or octodns, ansible-facts, steampipe) is added here when a project needs it, after it passes the
identical-twice test.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shlex
import ssl
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

TIMEOUT = 120
AGENT_TIMEOUT = 60
KP = str(Path.home() / ".config/keepassxc/kp")
Runner = Callable[[list[str], str | None, int], tuple[int, str]]

# scripts/ is not a package: load the sibling tenant-review library by path.
_spec = importlib.util.spec_from_file_location("as_built_tenants", Path(__file__).with_name("as_built_tenants.py"))
tenants = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tenants)


def run_command(cmd: list[str], stdin: str | None = None, timeout: int = TIMEOUT) -> tuple[int, str]:
  """Run a command; the default runner.

  Args:
    cmd: the command.
    stdin: text for its standard input.
    timeout: seconds.

  Returns:
    (exit code, stdout with the last stderr line on failure); 124 on timeout.
  """
  try:
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout)
  except subprocess.TimeoutExpired:
    return 124, f"timed out after {timeout} s\n"
  tail = "" if p.returncode == 0 else "\n".join(p.stderr.strip().splitlines()[-1:])
  return p.returncode, p.stdout + (tail + "\n" if tail else "")


def ssh_argv(target: str, cfg: dict, overrides: dict | None = None) -> list[str]:
  """The ssh command prefix for a target, from the manifest's [capture] block and the target's own options.

  Args:
    target: user@host.
    cfg: the [capture] block (ssh_options, identity, known_hosts).
    overrides: per-target identity or known_hosts.

  Returns:
    The argv up to and including the destination.
  """
  o = {**cfg, **(overrides or {})}
  argv = ["ssh", *o.get("ssh_options", ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10"])]
  if o.get("known_hosts"):
    argv += ["-o", f"UserKnownHostsFile={Path(o['known_hosts']).expanduser()}", "-o", "StrictHostKeyChecking=yes"]
  if o.get("identity"):
    argv += ["-i", str(Path(o["identity"]).expanduser())]
  return [*argv, target]


def prefix_for(t: dict, cfg: dict, key: str = "ssh") -> list[str] | None:
  """The ssh prefix for a target, or None when it runs where the capture runs.

  Args:
    t: target options; t[key] is user@host, "local", or absent.
    cfg: the [capture] block.
    key: the option holding the destination (ssh, or via_ssh for tls-endpoint).

  Returns:
    The ssh argv, or None for local.
  """
  dest = t.get(key)
  return None if not dest or dest == "local" else ssh_argv(dest, cfg, t)


def argv_for(prefix: list[str] | None, line: str, sudo: bool = False) -> list[str]:
  """The argv that runs one shell line locally or over SSH.

  Args:
    prefix: ssh argv, or None to run locally.
    line: shell command line.
    sudo: over SSH, run it through sudo bash -c (a local capture already runs as the user it needs).

  Returns:
    The argv.
  """
  if prefix is None:
    return ["bash", "-c", line]
  return [*prefix, f"sudo bash -c {shlex.quote(line)}" if sudo else line]


def sections(run: Runner, prefix: list[str] | None, commands: dict[str, str], sudo: bool = False) -> str:
  """Run named commands, one '== name' section each, in name order.

  Args:
    run: the runner.
    prefix: ssh argv, or None to run locally.
    commands: section name to shell command line.
    sudo: run each remote command through sudo bash -c.

  Returns:
    The concatenated sections; a failed command keeps its exit code in the header.
  """
  out = []
  for name in sorted(commands):
    rc, text = run(argv_for(prefix, commands[name], sudo), None, TIMEOUT)
    out.append(f"== {name}" + ("" if rc == 0 else f" (rc {rc})") + "\n" + text.rstrip("\n") + "\n")
  return "".join(out)


def linux_commands(t: dict) -> dict[str, str]:
  """The standard read-only Linux commands, plus the target's extras.

  Args:
    t: target options (docker, dirs, apt_dropins, extra).

  Returns:
    Section name to command line.
  """
  c = {
    "os": '. /etc/os-release 2>/dev/null; echo "$PRETTY_NAME"; uname -r; hostname',
    "ssh": "sshd -T 2>/dev/null | grep -E '^(port|permitrootlogin|passwordauthentication|kbdinteractiveauthentication|x11forwarding|pubkeyauthentication) '",
    "host-keys": 'for f in /etc/ssh/ssh_host_*_key.pub; do ssh-keygen -lf "$f"; done',
    "apt-origins": "apt-config dump | grep -E 'Allowed-Origins::|Automatic-Reboot |Package-Blacklist::' | sort",
    "fstab": "grep -vE '^\\s*(#|$)' /etc/fstab",
    "mounts": "findmnt -rn -o TARGET,SOURCE,FSTYPE -t ext4,xfs,vfat,zfs | sort",
    "timers": "systemctl list-timers --all --no-legend --no-pager 2>/dev/null | awk '{print $(NF-1), $NF}' | grep -vE '^(-|n/a)' | sort -u",
    "listening": "ss -tulnH 2>/dev/null | awk '{print $1, $5}' | sort -u",
  }
  if t.get("apt_dropins"):
    c["apt-dropins"] = "for f in " + " ".join(shlex.quote(x) for x in t["apt_dropins"]) + '; do [ -f "$f" ] && { echo "-- $f"; cat "$f"; }; done'
  if t.get("docker", False):
    c["containers"] = "docker ps -a --format '{{.Names}} {{.Image}} {{.State}}' | sort"
    c["images"] = "docker image ls --digests --format '{{.Repository}}:{{.Tag}} {{.Digest}}' | sort"
  if t.get("dirs"):
    c["files"] = "find " + " ".join(shlex.quote(d) for d in t["dirs"]) + " -maxdepth 2 -printf '%m %u %p\\n' 2>/dev/null | sort"
  c.update(t.get("extra", {}))
  return c


def probe_linux_host(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """A Linux VM, LXC or bare host over SSH.

  Args:
    t: target (name, ssh = user@host | "local" | absent for the machine the capture runs on, sudo, docker, dirs, apt_dropins, extra,
      known_hosts, identity). Local runs need the rights the commands need (a nightly self-capture runs as root).
    cfg: [capture] block.
    run: runner.

  Returns:
    {"<name>.txt": text}.
  """
  prefix = prefix_for(t, cfg)
  return {f"{t['name']}.txt": sections(run, prefix, linux_commands(t), sudo=t.get("sudo", False))}


PVE_COMMANDS = {
  "pveversion": "pveversion -v",
  "storage": "pvesm status | awk 'NR>1 {print $1, $2, $3}' | sort; echo; cat /etc/pve/storage.cfg",
  "network": "cat /etc/network/interfaces",
  "cluster-firewall": "cat /etc/pve/firewall/cluster.fw 2>/dev/null",
  "datacenter": "cat /etc/pve/datacenter.cfg 2>/dev/null",
  "pools": 'pvesh get /pools --output-format json | python3 -c \'import json,sys;[print(p["poolid"]) for p in sorted(json.load(sys.stdin),key=lambda p:p["poolid"])]\'',
  "users-tokens": 'pveum user list --output-format json | python3 -c \'import json,sys;[print(u["userid"], u.get("enable",1), u.get("expire",0)) for u in sorted(json.load(sys.stdin),key=lambda u:u["userid"])]\'; for u in $(pveum user list --output-format json | python3 -c \'import json,sys;[print(u["userid"]) for u in json.load(sys.stdin)]\'); do pveum user token list "$u" --output-format json 2>/dev/null | python3 -c \'import json,sys;[print("token", t["tokenid"], t.get("privsep"), t.get("expire",0)) for t in sorted(json.load(sys.stdin),key=lambda t:t["tokenid"])]\' | sed "s|^token |token $u!|"; done',
  "acl": 'pveum acl list --output-format json | python3 -c \'import json,sys;[print(a["path"], a["ugid"], a["roleid"], a.get("propagate",1)) for a in sorted(json.load(sys.stdin),key=lambda a:(a["path"],a["ugid"],a["roleid"]))]\'',
  "roles": 'pveum role list --output-format json | python3 -c \'import json,sys;[print(r["roleid"], r.get("privs","")) for r in sorted(json.load(sys.stdin),key=lambda r:r["roleid"]) if not r.get("special")]\'',
  "images": 'cd /var/lib/vz && for f in import/* template/cache/* template/iso/* snippets/*; do [ -f "$f" ] && echo "$(sha256sum "$f" | cut -c1-64) $(stat -c %s "$f") $f"; done',
}


def probe_proxmox_node(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """A Proxmox VE node: versions, storage, network, firewall, pools, users, tokens (ids only), ACLs, roles, images and snippets.

  Args:
    t: target (name, ssh = user@host | "local" | absent for the node the capture runs on, script, extra).
    cfg: [capture] block.
    run: runner.

  Returns:
    {"<name>.txt": text}; with `script` set, that local shell script runs on the node (bash -s) instead of the built-in commands.
  """
  prefix = prefix_for(t, cfg)
  if t.get("script"):
    rc, text = run(["bash", "-s"] if prefix is None else [*prefix, "bash -s"], Path(t["script"]).read_text(), 300)
    return {f"{t['name']}.txt": ("" if rc == 0 else f"== script (rc {rc})\n") + text}
  return {f"{t['name']}.txt": sections(run, prefix, {**PVE_COMMANDS, **t.get("extra", {})})}


def probe_pve_pool(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """Every guest of a Proxmox pool: its config and firewall file, and inside it when running.

  Args:
    t: target (name, ssh = user@host | "local" | absent, pool, inside = "ssh" | "agent" | "none", agent_timeout, guest_user, guest_known_hosts,
      sudo, docker, dirs, extra). Running containers are read through `pct exec` on the node; running VMs over SSH at their ipconfig0 address
      (inside = "ssh") or through the QEMU guest agent, `qm guest exec` on the node (inside = "agent": the node needs no SSH key into guests).
    cfg: [capture] block.
    run: runner.

  Returns:
    {"<name>/<kind>-<vmid>.txt": text} per guest.
  """
  prefix = prefix_for(t, cfg)
  rc, raw = run(argv_for(prefix, f"pvesh get /pools/{shlex.quote(t['pool'])} --output-format json"), None, TIMEOUT)
  try:
    members = json.loads(raw).get("members", []) if rc == 0 else []
  except ValueError:
    members = []
  out = {}
  for m in sorted(members, key=lambda x: x.get("vmid", 0)):
    if m.get("type") not in ("lxc", "qemu"):
      continue
    vmid, kind = m["vmid"], m["type"]
    tool = "pct" if kind == "lxc" else "qm"
    text = sections(run, prefix, {"1-config": f"{tool} config {vmid}", "2-firewall": f"cat /etc/pve/firewall/{vmid}.fw 2>/dev/null"})
    if m.get("status") == "running" and kind == "lxc" and t.get("inside", "ssh") != "none":
      # A container has no ipconfig0 and often no SSH: read it from the node with pct exec (as root inside the container).
      inner = {k: f"pct exec {vmid} -- bash -c {shlex.quote(v)}" for k, v in linux_commands(t).items()}
      text += sections(run, prefix, inner)
    elif m.get("status") == "running" and t.get("inside", "ssh") == "agent":
      text += agent_sections(run, prefix, vmid, linux_commands(t), int(t.get("agent_timeout", AGENT_TIMEOUT)))
    elif m.get("status") == "running" and t.get("inside", "ssh") == "ssh":
      conf = run(argv_for(prefix, f"{tool} config {vmid}"), None, TIMEOUT)[1]
      ip = next((p.split("=", 1)[1].split("/")[0] for ln in conf.splitlines() if ln.startswith("ipconfig0:") for p in ln.split(",") if "ip=" in p), "")
      if ip:
        guest = ssh_argv(f"{t.get('guest_user', 'root')}@{ip}", cfg, {"known_hosts": t.get("guest_known_hosts", cfg.get("known_hosts"))})
        text += sections(run, guest, linux_commands(t), sudo=t.get("sudo", True))
      else:
        text += "== inside\nno ipconfig0 address\n"
    elif m.get("status") != "running":
      text += f"== inside\n{m.get('status')}, not read\n"
    out[f"{t['name']}/{kind}-{vmid}.txt"] = text
  return out


def agent_sections(run: Runner, prefix: list[str] | None, vmid: int, commands: dict[str, str], timeout: int) -> str:
  """Run named commands inside a VM through the QEMU guest agent, one '== name' section each, like sections().

  `qm guest exec <vmid> --timeout N -- bash -c <line>` (PVE 9.3 qm(1)) prints JSON; out-data is the command's output and exitcode its status. When
  the timeout is reached qm returns only the pid, so an answer without exitcode is recorded as rc 124 (timed out), which fails the target.

  Args:
    run: runner.
    prefix: ssh argv to the node, or None on the node.
    vmid: the VM.
    commands: section name to shell command line.
    timeout: seconds qm waits for each command.

  Returns:
    The concatenated sections.
  """
  out = []
  for name in sorted(commands):
    line = f"qm guest exec {vmid} --timeout {timeout} -- bash -c {shlex.quote(commands[name])}"
    rc, raw = run(argv_for(prefix, line), None, timeout + 30)
    text = raw
    if rc == 0:
      try:
        answer = json.loads(raw)
      except ValueError:
        answer = None
      if isinstance(answer, dict) and "exitcode" in answer:
        rc = int(answer["exitcode"])
        text = answer.get("out-data", "") + ("[output truncated by the guest agent]\n" if answer.get("out-truncated") else "")
      elif isinstance(answer, dict):
        rc, text = 124, f"guest agent did not finish within {timeout} s\n"
    out.append(f"== {name}" + ("" if rc == 0 else f" (rc {rc})") + "\n" + text.rstrip("\n") + "\n")
  return "".join(out)


def probe_pve_tenants(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """The Proxmox side of every tenant's guests, reviewed against the provider's rules (me/nas doc 10, DL-072): one file per pool and a summary.

  Args:
    t: target (name, ssh = user@host | "local" | absent, registry, budgets, provider). registry and budgets are made absolute by as_built.py
      (defaults config/tenants.conf and config/guest-budgets.conf under the project root); provider defaults to "me/nas".
    cfg: [capture] block.
    run: runner.

  Returns:
    {"tenants/<pool>.txt": text, ..., "tenants/summary.txt": text}.

  Raises:
    ValueError: the node read failed or returned no guests (nothing is written for an empty read).
  """
  prefix = prefix_for(t, cfg)
  rc, text = run(["bash", "-s"] if prefix is None else [*prefix, "bash -s"], tenants.node_script(), 300)
  if rc != 0:
    raise ValueError(f"node read failed (rc {rc})")
  registry = Path(t.get("registry", "config/tenants.conf"))
  files = tenants.review(
    text, registry.parent, int(time.time()), registry, Path(t.get("budgets", "config/guest-budgets.conf")), t.get("provider", tenants.PROVIDER)
  )
  if not files:
    raise ValueError("node read gave no guests")
  return files


def probe_tls_endpoint(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """Certificates: subject, issuer, expiry and names, read from where they are served (locally or on a host over SSH).

  Args:
    t: target (name, via_ssh or ssh = user@host | "local" | absent, endpoints = [{name, port, connect}]).
    cfg: [capture] block.
    run: runner.

  Returns:
    {"<name>.txt": text}.
  """
  prefix = prefix_for(t, cfg, "via_ssh" if t.get("via_ssh") else "ssh")
  cmds = {}
  for e in t["endpoints"]:
    host = e.get("connect", e["name"])
    cmds[f"{e['name']}:{e.get('port', 443)}"] = (
      f"echo | timeout 10 openssl s_client -connect {host}:{e.get('port', 443)} -servername {e['name']} 2>/dev/null"
      " | openssl x509 -noout -subject -issuer -enddate -ext subjectAltName 2>/dev/null"
    )
  return {f"{t['name']}.txt": sections(run, prefix, cmds)}


def http_get(url: str, headers: dict | None = None, timeout: int = 15) -> tuple[int, str]:
  """HTTPS GET with the system trust store.

  Args:
    url: the URL.
    headers: request headers.
    timeout: seconds.

  Returns:
    (status, body); 0 with the error text when the request did not complete.
  """
  req = urllib.request.Request(url, headers=headers or {})
  try:
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
      return r.status, r.read().decode(errors="replace")
  except urllib.error.HTTPError as e:
    return e.code, e.read().decode(errors="replace")
  except (urllib.error.URLError, OSError) as e:
    return 0, str(e)


def pick(doc: object, fields: list[str]) -> list[str]:
  """Allow-listed fields of a JSON document, one 'field = value' line each (dotted paths; lists of objects keep their order).

  Args:
    doc: parsed JSON.
    fields: dotted paths.

  Returns:
    The lines.
  """
  lines = []
  for f in fields:
    cur = doc
    for part in f.split("."):
      cur = cur.get(part) if isinstance(cur, dict) else None
    lines.append(f"{f} = {json.dumps(cur, sort_keys=True)}")
  return lines


def probe_http_endpoint(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """HTTP status and allow-listed JSON fields of public endpoints (nothing else of the body is kept).

  Args:
    t: target (name, endpoints = [{url, fields}]).
    cfg: [capture] block (unused).
    run: runner (unused: HTTP is done in-process).

  Returns:
    {"<name>.txt": text}.
  """
  out = []
  for e in sorted(t["endpoints"], key=lambda e: e["url"]):
    status, body = http_get(e["url"])
    out.append(f"== {e['url']}\nstatus {status}\n")
    if e.get("fields") and status == 200:
      try:
        out.append("\n".join(pick(json.loads(body), e["fields"])) + "\n")
      except ValueError:
        out.append("body is not JSON\n")
  return {f"{t['name']}.txt": "".join(out)}


def kp_secret(entry: str, run: Runner, cfg: dict | None = None) -> str:
  """An entry's password for an API call (kept in memory only), from the manifest's secret source.

  Args:
    entry: entry path.
    run: runner.
    cfg: [capture] block (its `secrets` picks the source); None means KeePassXC.

  Returns:
    The value, or "" when missing in KeePassXC.

  Raises:
    ValueError: from a secrets file (see file_secret).
    OSError: the secrets file cannot be read.
  """
  return kp_field(entry, "Password", run, cfg)


def secret_key(entry: str, field: str) -> str:
  """The secrets-file key for an entry's field: / and - become _, upper-cased, the field as a suffix.

  Args:
    entry: entry path, e.g. me/malik-nas/cloudflare/api-token.
    field: Password, UserName or URL.

  Returns:
    The key, e.g. ME_MALIK_NAS_CLOUDFLARE_API_TOKEN_PASSWORD.
  """
  return re.sub(r"[/-]", "_", entry).upper() + "_" + field.upper()


def file_secret(path: str, key: str) -> str:
  """One value from a root-only KEY=VALUE secrets file (the value is never printed).

  Args:
    path: the file.
    key: the key (secret_key()).

  Returns:
    The value.

  Raises:
    ValueError: the file is readable by group or others, or lacks the key (that target fails, the others go on).
    OSError: the file cannot be read.
  """
  p = Path(path).expanduser()
  if p.stat().st_mode & 0o077:
    raise ValueError(f"secrets file {p} is readable by group or others (chmod 600)")
  for line in p.read_text().splitlines():
    k, sep, v = line.partition("=")
    if sep and not line.lstrip().startswith("#") and k.strip() == key:
      return v.strip()
  raise ValueError(f"secret {key} not in {p}")


def probe_cloudflare_dns(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """DNS records of Cloudflare zones: type, name, content, proxied, ttl (the token is read from KeePassXC, used, never written).

  Args:
    t: target (name, token_entry, zones = [names]).
    cfg: [capture] block (unused).
    run: runner (for kp).

  Returns:
    {"<name>.txt": text}.
  """
  token = kp_secret(t["token_entry"], run, cfg)
  if not token:
    return {f"{t['name']}.txt": f"== error\nsecret {t['token_entry']} missing or empty\n"}
  headers = {"Authorization": f"Bearer {token}"}
  out = []
  for zone in sorted(t["zones"]):
    status, body = http_get(f"https://api.cloudflare.com/client/v4/zones?name={zone}", headers)
    zones = json.loads(body).get("result", []) if status == 200 else []
    if not zones:
      out.append(f"== {zone}\nzone lookup status {status}\n")
      continue
    status, body = http_get(f"https://api.cloudflare.com/client/v4/zones/{zones[0]['id']}/dns_records?per_page=500", headers)
    recs = json.loads(body).get("result", []) if status == 200 else []
    rows = sorted(f"{r['type']} {r['name']} {r['content']} proxied={r.get('proxied')} ttl={r.get('ttl')}" for r in recs)
    out.append(f"== {zone} (status {status})\n" + "\n".join(rows) + "\n")
  return {f"{t['name']}.txt": "".join(out)}


def kp_field(entry: str, field: str, run: Runner, cfg: dict | None = None) -> str:
  """One field of an entry, in memory only: from KeePassXC ([capture] secrets = "kp", the default) or a file (secrets = "file:<path>").

  Args:
    entry: entry path.
    field: Password, UserName or URL.
    run: runner.
    cfg: [capture] block; None means KeePassXC.

  Returns:
    The value, or "" when missing in KeePassXC.

  Raises:
    ValueError: from a secrets file (see file_secret).
    OSError: the secrets file cannot be read.
  """
  source = (cfg or {}).get("secrets", "kp")
  if source.startswith("file:"):
    return file_secret(source[len("file:") :], secret_key(entry, field))
  rc, out = run([KP, "show", "-s", "-a", field, entry], None, 30)
  return out.strip() if rc == 0 else ""


def cf_get(path: str, token: str) -> list | dict:
  """One Cloudflare API v4 GET, returning its result (empty on failure).

  Args:
    path: path after /client/v4/.
    token: API token.

  Returns:
    The result field.
  """
  status, body = http_get(f"https://api.cloudflare.com/client/v4/{path}", {"Authorization": f"Bearer {token}"})
  try:
    return json.loads(body).get("result") or [] if status == 200 else []
  except ValueError:
    return []


def probe_cloudflare(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """Cloudflare as JSON: DNS records per zone and, with an account id, tunnels with their ingress and Access apps and policies.

  Args:
    t: target (name, token_entry, account_field = "URL" holding the account id or omitted, zones, tunnels, access).
    cfg: [capture] block (unused).
    run: runner (for kp).

  Returns:
    {"<name>.json": sorted JSON}; emails are masked later by the engine.
  """
  token = kp_field(t["token_entry"], "Password", run, cfg)
  if not token:
    return {f"{t['name']}.json": f"== error\nsecret {t['token_entry']} missing or empty\n"}
  doc: dict = {"zones": {}}
  for zone in sorted(t.get("zones", [])):
    z = cf_get(f"zones?name={zone}", token)
    recs = cf_get(f"zones/{z[0]['id']}/dns_records?per_page=500", token) if z else []
    doc["zones"][zone] = sorted(
      ({k: r.get(k) for k in ("name", "type", "content", "proxied")} for r in recs), key=lambda r: (r["name"], r["type"], str(r["content"]))
    )
  account = kp_field(t["token_entry"], t["account_field"], run, cfg) if t.get("account_field") else ""
  if account and t.get("tunnels"):
    tunnels = []
    for tun in cf_get(f"accounts/{account}/cfd_tunnel?is_deleted=false", token):
      conf = cf_get(f"accounts/{account}/cfd_tunnel/{tun['id']}/configurations", token)
      tunnels.append({"name": tun.get("name"), "id": tun.get("id"), "ingress": (conf.get("config") or {}).get("ingress") if isinstance(conf, dict) else None})
    doc["tunnels"] = sorted(tunnels, key=lambda x: x["name"] or "")
  if account and t.get("access"):
    apps = cf_get(f"accounts/{account}/access/apps", token)
    doc["access_apps"] = sorted(
      (
        {
          "name": a.get("name"),
          "domain": a.get("domain"),
          "type": a.get("type"),
          "session_duration": a.get("session_duration"),
          "policies": sorted(p.get("name", "") for p in a.get("policies", [])),
        }
        for a in apps
      ),
      key=lambda x: x["name"] or "",
    )
    pols = cf_get(f"accounts/{account}/access/policies", token)
    doc["access_policies"] = sorted(
      ({"name": p.get("name"), "decision": p.get("decision"), "include": p.get("include"), "session_duration": p.get("session_duration")} for p in pols),
      key=lambda x: x["name"] or "",
    )
  return {f"{t['name']}.json": json.dumps(doc, indent=2, sort_keys=True) + "\n"}


def probe_command(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """Named read-only commands, locally or on a host over SSH (service status endpoints, tool outputs).

  Args:
    t: target (name, ssh = user@host | "local" | absent, sudo, commands, raw: exactly one command whose output is written as it is).
    cfg: [capture] block.
    run: runner.

  Returns:
    {"<name>.txt": text}.
  """
  prefix = prefix_for(t, cfg)
  if t.get("raw"):
    # One command whose output is the file as it is (a JSON document, for example); no section header.
    (line,) = t["commands"].values()
    rc, text = run(argv_for(prefix, line, bool(t.get("sudo"))), None, TIMEOUT)
    return {f"{t['name']}.txt": text if rc == 0 else f"== error (rc {rc})\n{text}"}
  return {f"{t['name']}.txt": sections(run, prefix, t["commands"], sudo=t.get("sudo", False))}


def probe_local_tools(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """Tool versions and git heads on the machine running the capture.

  Args:
    t: target (name, tools = {label: command}, git = [paths]).
    cfg: [capture] block (unused).
    run: runner.

  Returns:
    {"<name>.txt": text}.
  """
  cmds = {f"tool {k}": v for k, v in t.get("tools", {}).items()}
  for repo in t.get("git", []):
    cmds[f"git {repo}"] = f"git -C {shlex.quote(str(Path(repo).expanduser()))} log -1 --format='%h %s'"
  return {f"{t['name']}.txt": sections(run, None, cmds)}


def probe_hand(t: dict, cfg: dict, run: Runner) -> dict[str, str]:
  """Rows the operator records by hand (no API): router forwards, reservations, console settings.

  Args:
    t: target (name, rows = [{what, value, checked, source}]).
    cfg: [capture] block (unused).
    run: runner (unused).

  Returns:
    {"<name>.txt": text}.
  """
  rows = [f"{r['what']} | {r['value']} | checked {r.get('checked', '?')} | {r.get('source', '')}" for r in sorted(t["rows"], key=lambda r: r["what"])]
  return {f"{t['name']}.txt": "== hand rows (operator-checked)\n" + "\n".join(rows) + "\n"}


PROBES: dict[str, Callable[[dict, dict, Runner], dict[str, str]]] = {
  "proxmox-node": probe_proxmox_node,
  "pve-pool": probe_pve_pool,
  "pve-tenants": probe_pve_tenants,
  "linux-host": probe_linux_host,
  "tls-endpoint": probe_tls_endpoint,
  "http-endpoint": probe_http_endpoint,
  "cloudflare-dns": probe_cloudflare_dns,
  "cloudflare": probe_cloudflare,
  "command": probe_command,
  "local-tools": probe_local_tools,
  "hand": probe_hand,
}
