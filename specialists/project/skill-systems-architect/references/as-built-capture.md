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

## Probe types

| Type | Captures | Options |
| ---- | -------- | ------- |
| `proxmox-node` | versions, storage, network, cluster firewall, datacenter, pools, users and token ids, ACLs, roles, image and snippet checksums | `ssh`, `script` (run a project script with `bash -s` instead), `extra` |
| `pve-pool` | per guest: Proxmox config and firewall file; inside a running guest the `linux-host` set | `ssh`, `pool`, `inside` (`ssh` or `none`), `guest_user`, `guest_known_hosts`, `sudo`, `docker`, `dirs`, `apt_dropins`, `extra` |
| `linux-host` | OS, sshd settings, host key fingerprints, update origins, fstab, mounts, timers, listening ports; containers and image digests; file names and modes | `ssh`, `sudo`, `docker`, `dirs`, `apt_dropins`, `extra` |
| `tls-endpoint` | subject, issuer, expiry and names, read where served | `via_ssh`, `endpoints = [{name, port, connect}]` |
| `http-endpoint` | status and allow-listed JSON fields | `endpoints = [{url, fields}]` |
| `cloudflare-dns` | type, name, content, proxied, ttl per record | `token_entry` (KeePassXC), `zones` |
| `command` | named read-only commands, locally or over SSH | `ssh`, `sudo`, `commands`, `raw` (one command, output as is, e.g. JSON) |
| `cloudflare` | DNS records per zone; with an account id, tunnels with ingress, Access apps and policies; sorted JSON | `token_entry`, `account_field`, `zones`, `tunnels`, `access` |
| `local-tools` | tool versions, git heads | `tools`, `git` |
| `hand` | operator-checked rows | `rows = [{what, value, checked, source}]` |

Planned, optional, off until identical twice: `tofu-plan` (`tofu plan -detailed-exitcode`, exit 2 = drift; NAS DL-072), `pve-tenants`
(Proxmox side of each tenant pool from a tenants file; NAS DL-073), `cloudflare-export` (cf-terraforming 0.31.0 or octodns), `ansible-facts`,
`steampipe`.

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

## Masking and churn

- Masked before anything is compared or written: `key=value` and `key: value` for password, secret, token, API key, private key, passphrase and
  cipassword; OpenBao-style `hvs.`/`s.` tokens; NetBird `nbp_` tokens; every email address. Projects add regexes in `mask`.
- Churn: lines matching `drop` (manifest-wide and per target) are removed, trailing whitespace stripped. Typical churn: snapshot times, clock and
  NTP readings, random loopback ports of container runtimes, container "Up 3 hours" text (the engine records State instead).

## Why not an existing tool

A survey of 22 FOSS tools (continuum docs/research/as-built-capture-tools-20261126_1500.md) found none that writes stable masked per-area files
across hypervisor, guests, services and cloud APIs; and none captures application services (OpenBao, Keycloak, NetBird, OpenFGA). Tools such as
Ansible facts or Steampipe would cover only the host, DNS and certificate layer; they can be added as probe types later (DL-265).
