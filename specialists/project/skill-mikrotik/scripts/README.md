---
Title: skill-mikrotik scripts
Category: script-inventory
Status: current
Authority: local-supplement
Scope: Reusable tooling for MikroTik devices behind SMC boxes
Last reviewed: 2026-10-07
Summary: Read-only RouterOS access through a Teleport port-forward, a fleet survey, a deep per-site capture, and the pack's governance checker.
---

# scripts/

Raw output goes to the investigation folder you name (under `local-knowledge-ansible/ansible-wifi/issues/`), never into this pack.

| Script                     | Touches                                    | Safety                         | Notes                                                                                     |
| -------------------------- | ------------------------------------------ | ------------------------------ | ----------------------------------------------------------------------------------------- |
| `mikrotik-exec.sh`         | One MikroTik via Teleport forward through  | **read-only**                  | Password from KeePass into `SSHPASS` only; batches commands into one SSH session; retries |
|                            |   the SMC                                  |   unless `MT_ALLOW_WRITE=1`    |   a refused login twice                                                                   |
| `mikrotik-fleet-survey.sh` | Every MikroTik behind every SMC of         | **read-only**                  | CSV of identity, model, version, uptime, voltage, temperature, link-downs; `WORKERS`      |
|                            |   a flavor                                 |                                |   parallel sites                                                                          |
| `mikrotik-site-capture.sh` | One site's switch and AP                   | **read-only**                  | Full log, port monitor, bridge layout, `/export terse` (secrets hidden by RouterOS 7);    |
|                            |                                            |                                |   `WAIT_UP=1` waits for the SMC                                                           |
| `check_governance.py`      | This pack's own files                      | **read-only**                  | Stdlib only; `just check`                                                                 |

## mikrotik-exec.sh

```bash
./mikrotik-exec.sh delye-smc01 10.255.0.5 '/system resource print' '/system health print'
MT_BATCH=0 ./mikrotik-exec.sh <smc> <ip> '<cmd>'      # one session per command, for debugging
```

Opens `tsh ssh -N -L` to the device's port 22 through the SMC, runs `sshpass -e ssh` locally. Batch mode joins the commands with `;` and `:put "### N"` markers, then relabels them, so a device costs
one SSH login (about 15 s over satellite instead of about 50 s). `SSH_ASKPASS_REQUIRE=never` stops ssh using an X11 askpass when `DISPLAY` is set. Reasoning for the design:
`../references/02_device-access.md`.

## mikrotik-fleet-survey.sh

```bash
WORKERS=10 ./mikrotik-fleet-survey.sh <outdir>                       # every flavor=rct *-smc01 in Teleport
DEVICES=10.255.0.5 ./mikrotik-fleet-survey.sh <outdir> delye-smc01   # named sites, switch only
```

297 `rct` sites took 19 minutes at `WORKERS=10` (2026-10-07); a few sites' forwards do not open within 30 s and show as not reached. Each site sends a few KB.

## mikrotik-site-capture.sh

```bash
./mikrotik-site-capture.sh delye-smc01 <outdir>
WAIT_UP=1 MAX_WAIT=86400 POLL=120 ./mikrotik-site-capture.sh arrkapa-smc01 <outdir>   # wait for the SMC to reappear in Teleport
```

Capture before any power-cycle: the RouterOS log is in memory only.

## survey-summary.py

```bash
./survey-summary.py <outdir>/survey.csv            # add --no-prom to skip the SMC uptime comparison
```

A device whose uptime is more than a day shorter than its SMC's was power-cycled after the SMC booted (on `rct`, usually the TSTIK app). The AP shares the switch's
uptime at every site surveyed, consistent with the AP being powered from the switch.
