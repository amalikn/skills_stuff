---
Title: skill-mikrotik scripts
Category: script-inventory
Status: current
Authority: local-supplement
Scope: Reusable tooling for MikroTik devices behind SMC boxes
Last reviewed: 2026-10-08
Summary: Read-only RouterOS access through a Teleport port-forward, a fleet survey, a deep per-site capture, and the pack's governance checker.
---

# scripts/

Raw output goes to the investigation folder you name (under `local-knowledge-ansible/ansible-wifi/issues/`), never into this pack.

| Script                     | Touches                                    | Safety                         | Notes                                                                                     |
| -------------------------- | ------------------------------------------ | ------------------------------ | ----------------------------------------------------------------------------------------- |
| `mikrotik_exec.sh`         | One MikroTik via Teleport forward through  | **read-only**                  | Password from KeePass into `SSHPASS` only; batches commands into one SSH session; retries |
|                            |   the SMC                                  |   unless `MT_ALLOW_WRITE=1`    |   a refused login twice                                                                   |
| `mikrotik_fleet_survey.sh` | Every MikroTik behind every SMC of         | **read-only**                  | CSV of identity, model, version, uptime, voltage, temperature, link-downs; `WORKERS`      |
|                            |   a flavor                                 |                                |   parallel sites                                                                          |
| `mikrotik_site_capture.sh` | One site's switch and AP                   | **read-only**                  | Full log, port monitor, bridge layout, `/export terse` (secrets hidden by RouterOS 7);    |
|                            |                                            |                                |   `WAIT_UP=1` waits for the SMC                                                           |
| `check_governance.py`      | This pack's own files                      | **read-only**                  | Stdlib only; `just check`                                                                 |
| `mib_oids.py`              | A local MIB file                           | **read-only**                  | MIKROTIK-MIB object name -> numeric OID, syntax, units, status; optional name regex       |
| `confluence_fetch.py`      | help.mikrotik.com (web)                    | **read-only**                  | One documentation page by Confluence id, saved as text with its source and version line   |
| `product_text.py`          | A saved mikrotik.com product page          | **read-only**                  | Description and spec tables of a product page as text                                     |
| `snmp_via_smc.py`          | One device's SNMP agent, from its SMC      | **read-only** unless a `set:`  | Stdlib SNMP v2c get/walk/set sent to the SMC (no net-snmp on rct/wh); community from      |
|                            |                                            |   op is given                  |   KeePass on stdin, never on a command line or printed                                    |
| `mikrotik_snmp_community.py` | One device's SNMP settings               | **writes** (`enable`, `remove`); | Adds or removes a community from KeePass (value redacted in all output), disables         |
|                            |                                            |   `show` is read-only          |   `public`, turns SNMP on or off; needs operator approval per device                      |
| `routeros_firmware_fetch.py` | download.mikrotik.com (web); writes only | **read-only** towards devices; | Fetches and resumes one version's files, verifies size, ETag md5 and published `.sha256`; |
|                            |   into `firmware-files/<version>/`         |   `--verify-only` downloads nothing |   prints manifest YAML; stops on HTTP 429                                             |
| `mikrotik_mac_reset.py`    | One switch's ports and bridges             | **writes** with `--apply` only; | `reset-mac-address [find]` (known issue 11): saves the before-state, reads back, verifies |
|                            |                                            |   plan only by default         |   ports at `orig-mac-address` and auto-mac bridges on a factory MAC; JSON on stdout      |

## mikrotik_exec.sh

```bash
./mikrotik_exec.sh delye-smc01 10.255.0.5 '/system resource print' '/system health print'
MT_BATCH=0 ./mikrotik_exec.sh <smc> <ip> '<cmd>'      # one session per command, for debugging
```

Opens `tsh ssh -N -L` to the device's port 22 through the SMC, runs `sshpass -e ssh` locally. Batch mode joins the commands with `;` and `:put "### N"` markers, then relabels them, so a device costs
one SSH login (about 15 s over satellite instead of about 50 s). `SSH_ASKPASS_REQUIRE=never` stops ssh using an X11 askpass when `DISPLAY` is set. Reasoning for the design:
`../references/02_device-access.md`.

## mikrotik_fleet_survey.sh

```bash
WORKERS=10 ./mikrotik_fleet_survey.sh <outdir>                       # every flavor=rct *-smc01 in Teleport
DEVICES=10.255.0.5 ./mikrotik_fleet_survey.sh <outdir> delye-smc01   # named sites, switch only
```

297 `rct` sites took 19 minutes at `WORKERS=10` (2026-10-07); a few sites' forwards do not open within 30 s and show as not reached. Each site sends a few KB.

## mikrotik_site_capture.sh

```bash
./mikrotik_site_capture.sh delye-smc01 <outdir>
WAIT_UP=1 MAX_WAIT=86400 POLL=120 ./mikrotik_site_capture.sh arrkapa-smc01 <outdir>   # wait for the SMC to reappear in Teleport
```

Capture before any power-cycle: the RouterOS log is in memory only.

## mikrotik_mac_reset.py

```bash
just mac_reset glen-hill-smc01 10.255.0.5 <capture-dir>            # plan only: before-state saved, per-port mac vs orig-mac, nothing written
just mac_reset glen-hill-smc01 10.255.0.5 <capture-dir> --apply    # reset, wait 20 s, read back (retried every 30 s up to 10 min: the Teleport tunnel drops 4-5 min), verify
```

One switch per run, by operator rule (2026-10-08); a list of hosts is refused. The remedy for the cloned port MACs of known issue 11, proven on glen-hill
2026-10-08: RouterOS 7.8 has the command, the `auto-mac` bridges follow without a reboot and the SMC re-learns the switch by ARP. Each run writes
the raw before, reset and after reads and the summary JSON to `<capture-dir>/mac-reset-<smc>-<ip>-<stamp>/`. The JSON (serial, before and after MAC per
port and bridge, `result`: `nothing_to_do`, `planned`, `pass` or `fail`) is what an inventory update reads. Exit 1 on a failed verification; 4 when the
port-forward did not come up twice. `--apply` needs the operator's go-ahead per switch.

## survey_summary.py

```bash
./survey_summary.py <outdir>/survey.csv            # add --no-prom to skip the SMC uptime comparison
```

A device whose uptime is more than a day shorter than its SMC's was power-cycled after the SMC booted (on `rct`, usually the TSTIK app). The AP shares the switch's
uptime at every site surveyed, consistent with the AP being powered from the switch.

## routeros_firmware_fetch.py

```bash
just firmware_fetch 7.24.5                       # fetch missing files, resume truncated ones, into firmware-files/7.24.5/
just firmware_fetch 7.12.2 --verify-only         # HEAD requests only: compare local files with the host
just firmware_fetch 7.24.5 --arch mipsbe --dest <folder>
```

Checks size against Content-Length, md5 against the ETag, and sha256 against MikroTik's `<url>.sha256` sidecar, saved beside the file where one is
published (none for 7.8 or 7.12.x). A 0-byte `wireless-<v>-mipsbe.npk` before 7.13 is a placeholder and is skipped. The YAML on stdout pastes into
`../references/firmware-manifest.yaml`; add the curated fields (channel, kind, models, firmware_type, retrieved) by hand. Exit 1 on any missing or
mismatched file, 2 on HTTP 429.

## doc-freshness-baseline.json

Data, not a script: the findings skill-ai-it's `doc_freshness` grandfathered when this pack adopted the governed-file standard (2026-10-10).
`just check` fails only on findings not in it; regenerate with `just stale` reviewed first, then `doc_freshness.py --project-root . --write-baseline`
from the skill-ai-it package. A file over its budget may shrink, never grow.
