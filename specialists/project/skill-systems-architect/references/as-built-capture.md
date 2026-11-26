---
Title: As-built capture standard and engine
Category: reference
Status: current
Authority: authored-guidance
Scope: How any project records and captures what is deployed (hosts, hypervisors, guests, services, certificates, DNS, tools, hand-set settings) with scripts/as_built.py
Last reviewed: 2026-11-26
Summary: >-
  Shared standard agreed by the continuum and home NAS projects (continuum DL-263 to DL-265, NAS DL-070 and DL-071): a same-day ledger row per change,
  a narrative for first deployments and incidents, and a read-only capture into stable per-area files that git versions; the manifest schema,
  probe types, masking, churn and the identical-twice acceptance test.
---

# As-built capture standard and engine

## Contents

- [The standard](#the-standard)
- [Manifest](#manifest)
- [Probe types](#probe-types)
- [Masking and churn](#masking-and-churn)
- [Why not an existing tool](#why-not-an-existing-tool)

## The standard

1. **Ledger row, same day**, for every change to a live system: date, what, how (command or recipe), evidence, codified form (script, OpenTofu,
   runbook). A **narrative record** only for a first deployment or an incident (what exists, every value, versions and digests, service answers,
   secret entry names, failures and fixes, redo and rollback).
2. **Capture after the change**: `just as-built --apply` (the project's recipe calling this engine) writes stable files, one per area, overwritten
   each run. Git history is the version store; `git diff <captures>` is the drift report. Never edit a capture by hand.
3. **Acceptance**: `--twice` must report identical before a target counts as captured. Every probe sorts its own output.
4. **Read-only, always**: probes run commands that read, HTTPS GETs and an API token's value held in memory for a call; no secret file's contents
   are read; output is masked.
5. **Operator parts** (router, consoles without an API) are `hand` rows in the manifest, with the date they were checked.
6. Each project's AGENTS.md carries one line linking its manifest and this page.
7. **Additions adopted with NAS DL-072** (2026-11-26, for every project): a scheduled capture (nightly) that commits only on change; a health
   area, so a failure diff shows what changed since the last green run; annotated milestone tags `asbuilt/<yyyymmdd>-<name>` at gate passes; on
   a failure, the journal slice goes into the incident narrative before capped logs age out. Open risk: a job on a laptop records nothing while it
   sleeps, and local commits stay local until pushed (decided per project).

## Manifest

`as-built.toml` at the project root:

```toml
[capture]
out = "deploy/as-built/captures"          # relative to the manifest
identity = "~/.ssh/<key>"                  # optional
known_hosts = "<project known_hosts file>" # optional; StrictHostKeyChecking=yes when set
secrets = "kp"                             # default: KeePassXC through kp; "file:<path>" on a host without it (below)
drop = ['<regex of churn lines, all targets>']
mask = ['<extra regex to mask>']

[[target]]
name = "guests"                 # file name (or folder for pve-pool)
type = "pve-pool"               # one of the probe types below
ssh = "root@<node>"
pool = "<pool>"
guest_user = "ubuntu"
drop = ['<target-only churn regex>']
```

No addresses in a manifest when a project keeps them elsewhere: `{resolver:key}` placeholders are filled by `[capture.resolvers]` commands run in
the project folder (`lan = "python3 -I scripts/lib/nas_lan.py ip {key}"`). A target's `file` sets its output name (keep a project's existing names
so git history continues). Dry runs: `--root <project> --out <copy>` against a copy of the committed captures.

Capture on the Proxmox node itself (NAS DL-074/075; continuum TASK-680): `ssh = "local"`, or no `ssh`, runs `proxmox-node`, `pve-pool`,
`pve-tenants`, `tls-endpoint` and `command` where the engine runs. `secrets = "file:<path>"` reads API tokens from a root-only (mode 600) `KEY=VALUE`
file instead of KeePassXC: the key is the entry with `/` and `-` turned to `_`, upper-cased, plus the field (`me/malik-nas/cloudflare/api-token` +
Password -> `ME_MALIK_NAS_CLOUDFLARE_API_TOKEN_PASSWORD`; the URL field -> `..._URL`). The value is never printed; a missing key, or a file readable by
group or others, fails that target only. The engine needs Python 3.11 or later (the node runs 3.13).

## Probe types

| Type | Captures | Options |
| ---- | -------- | ------- |
| `proxmox-node` | versions, storage, network, cluster firewall, datacenter, pools, users and token ids, ACLs, roles, image and snippet checksums | `ssh` (or `local`), `script` (run a project script with `bash -s` instead), `extra` |
| `pve-pool` | per guest: Proxmox config and firewall file; inside a running guest the `linux-host` set (LXC through `pct exec`) | `ssh` (or `local`), `pool`, `inside` (`ssh`, `agent` or `none`), `agent_timeout` (s, default 60), `guest_user`, `guest_known_hosts`, `sudo`, `docker`, `dirs`, `apt_dropins`, `extra` |
| `pve-tenants` | the Proxmox side of every tenant pool, reviewed against the host's tenant rules: `tenants/<pool>.txt` and `tenants/summary.txt` (as_built_tenants.py, lifted from me/nas) | `ssh` (or `local`), `registry` (default `config/tenants.conf`), `budgets` (default `config/guest-budgets.conf`), `provider` (default `me/nas`), `strip` (default false) |
| `linux-host` | OS, sshd settings, host key fingerprints, update origins, fstab, mounts, timers, listening ports; containers and image digests; file names and modes | `ssh`, `sudo`, `docker`, `dirs`, `apt_dropins`, `extra` |
| `tls-endpoint` | subject, issuer, expiry and names, read where served | `via_ssh` or `ssh` (or `local`), `endpoints = [{name, port, connect}]` |
| `http-endpoint` | status and allow-listed JSON fields | `endpoints = [{url, fields}]` |
| `cloudflare-dns` | type, name, content, proxied, ttl per record | `token_entry` (from `secrets`), `zones` |
| `command` | named read-only commands, locally or over SSH | `ssh` (or `local`), `sudo`, `commands`, `raw` (one command, output as is, e.g. JSON) |
| `cloudflare` | DNS records per zone; with an account id, tunnels with ingress, Access apps and policies; sorted JSON | `token_entry`, `account_field`, `zones`, `tunnels`, `access` |
| `local-tools` | tool versions, git heads | `tools`, `git` |
| `hand` | operator-checked rows | `rows = [{what, value, checked, source}]` |

`inside = "agent"` reads a running VM with `qm guest exec <vmid> --timeout <agent_timeout> -- bash -c <commands>` on the node (PVE 9.3.1 qm(1),
VERIFIED_PRIMARY 2026-11-26), so the node needs no SSH key into guests; `exitcode` and `out-data` of its JSON become the section. When the timeout is
reached qm returns only the pid: the section is recorded `rc 124` and the target fails. The JSON field names come from the guest-agent API, not
qm(1) (UNVERIFIED until the first node run).

Planned, optional, off until identical twice: `tofu-plan` (`tofu plan -detailed-exitcode`, exit 2 = drift; NAS DL-072), `cloudflare-export`
(cf-terraforming 0.31.0 or octodns), `ansible-facts`, `steampipe`.

Measured 2026-11-26: the NAS draft manifest (14 files: node script, guests by SSH and pct exec, Cloudflare tunnels and Access, DigitalPlat,
Tailscale, Healthchecks, certificates, KeePassXC names, Nextcloud) ran in 86 s and was identical twice; `os-images.txt` matched the NAS's own
capture byte for byte.

> **Learned 2026-11-26** · first runs of the engine · VERIFIED_PRIMARY (continuum-app as-built.toml: 11 files, 29 s per run; first twice-run differed
> on an unsorted `pveum role list`, identical after sorting) · Source: continuum-app e6ec936 · Falsifier: an unsorted JSON listing from the Proxmox
> API returning the same order on every call
> Proxmox's JSON listings are not ordered: sort them in the probe. The first capture also showed a leftover `_acme-challenge` TXT record in
> Cloudflare from failed DNS-01 attempts, which no other check had shown; captures find drift nobody looks for.

> **Learned 2026-11-26** · ownership between projects sharing a host · USER_STATED (operator: a project owns its own guests; the host and other
> guests belong to the host's project) · Source: continuum and NAS sessions · Falsifier: none, an ownership rule
> A project's manifest captures only what it owns. The host project publishes a tenant view of each tenant's pool (configs, budget, quota, backups,
> rules) in its own capture; the tenant reads that committed file (`git -C <host repo> show HEAD:./<path>`) instead of reading the host. A dry
> run for another project is that project's to run: hand it the engine and a draft, not your reads of its systems.

> **Learned 2026-11-26** · twin captures, one manifest · VERIFIED_PRIMARY (continuum-app 83a752f: `just as-built-twin` byte-identical for three
> VMs) · Source: continuum DL-270; me/nas as-built-node.toml · Falsifier: a VM's self-capture differing from the Mac run with no change between.
> When a machine captures itself (nightly, ssh = "local") and a central run also captures it, build the machine's manifest from the central
> manifest's own target for it (ssh replaced by local, everything else copied), write the same file name, and check byte equality; two
> hand-kept manifests drift. Resolve addresses from the infrastructure-as-code settings (`{vm:<key>}` from OpenTofu tfvars), never literals.

## Masking and churn

- Masked before anything is compared or written: `key=value` and `key: value` for password, secret, token, API key, private key, passphrase and
  cipassword; OpenBao-style `hvs.`/`s.` tokens; NetBird `nbp_` tokens; every email address. Projects add regexes in `mask`.
- Churn: lines matching `drop` (manifest-wide and per target) are removed, trailing whitespace stripped (`strip = false` on a target keeps it, for
  files that must stay byte-identical to an earlier writer's; `pve-tenants` defaults to false because a nameless guest's header ends in a space). Typical churn: snapshot times, clock and
  NTP readings, random loopback ports of container runtimes, container "Up 3 hours" text (the engine records State instead).

## Why not an existing tool

A survey of 22 FOSS tools (continuum docs/research/as-built-capture-tools-20261126_1500.md) found none that writes stable masked per-area files
across hypervisor, guests, services and cloud APIs; and none captures application services (OpenBao, Keycloak, NetBird, OpenFGA). Tools such as
Ansible facts or Steampipe would cover only the host, DNS and certificate layer; they can be added as probe types later (DL-265).

> **Learned 2026-11-26** · the capture run on the node itself, pushing to Git · VERIFIED_PRIMARY (home NAS: node plan showed every shared file
> "same" as the Mac run except real changes; first run pushed; health file all ok) · Source: me/nas `as-built-node.toml`,
> `scripts/node/pve_capture_nightly.sh`, `scripts/mac/nas_capture_node.sh` (amalikn/nas 4204326) · Falsifier: a target whose output differs
> only by where it runs (then the two runs flip the file every night).
> A node-side twin manifest (`ssh = "local"`, `secrets = "file:<root-only file>"`) must write the same files as the workstation run; prove it with
> a plan run on the node ("same") and a `--out <scratch> --apply` diff, since plan mode writes nothing even with `--out`. Targets that need the
> workstation's keys (password manager names, an account-wide registrar key, SSH into guests) stay workstation-only and the manifest says why.
> A health file (each target ok or failed, no timestamps) changes only when a status flips, so "commit only on change" still records failures.
> Before giving a box a Git write key: a GitHub deploy key covers a whole repository, so a project inside a monorepo of personal records is split
> out first (`git subtree split`, the old repo keeps a submodule) and the key goes on the small repo; gitleaks scans `origin/main..HEAD` before
> each push and a hit keeps the commit local and fails the health check.

```bash
# me/nas scripts/node/pve_capture_nightly.sh (amalikn/nas 4204326)
git commit -q -m "as-built: nightly node capture $(date +%F)"
if ! timeout 120 gitleaks git --no-banner --redact --log-opts="origin/main..HEAD" . >"$D/gitleaks.log" 2>&1; then
  hc /fail "gitleaks found a possible secret in the new commit; not pushed"; return 1
fi
timeout 120 git push -q origin HEAD:main || { timeout 120 git pull -q --rebase origin main && timeout 120 git push -q origin HEAD:main; }
```
