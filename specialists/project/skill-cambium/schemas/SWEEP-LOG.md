---
Title: Cambium Schema Sweep Log
Category: device-reference
Status: current
Authority: primary — the run record behind the contract in this tree
Scope: Every sweep run that produced or corrected the device response schemas, with its settings, result and defects
Last reviewed: 2026-09-20
Summary: Per-run record of the five sweeps of 2026-09-20 — what each run was configured to do, what it produced, what it got wrong, and why two of them had to be discarded and repeated.
---

# Cambium Schema Sweep Log

Five runs on 2026-09-20 produced the contract in this tree. Two produced confidently wrong data and had to be repeated; two more recovered gaps the first pass had left. This file keeps that history because the merged schema does not: a
contract shows what was concluded, not how much of the evidence behind it was discarded, and the two defects below are the kind that recur.

The standard itself is in [README.md](README.md); per-endpoint disagreement is in [DIVERGENCE.md](DIVERGENCE.md).

## Contents

- [Run summary](#run-summary)
- [Run 1 — full fleet, all families](#run-1--full-fleet-all-families)
- [Run 2 — Wi-Fi re-sweep, session reuse](#run-2--wi-fi-re-sweep-session-reuse)
- [Run 3 — Wi-Fi re-sweep, parser fixed](#run-3--wi-fi-re-sweep-parser-fixed)
- [Run 4 — gap retry at full timeout](#run-4--gap-retry-at-full-timeout)
- [Run 5 — legacy credential fallback](#run-5--legacy-credential-fallback)
- [Defects found in the sweep tooling](#defects-found-in-the-sweep-tooling)
- [Tuning history and what it cost](#tuning-history-and-what-it-cost)
- [Findings files](#findings-files)

## Run summary

| #   | Scope            | Completed (UTC) | Sites | Observations | Findings | Outcome                                                |
| --- | ---------------- | --------------- | ----- | ------------ | -------- | ------------------------------------------------------ |
| 1   | All 5 families   | 06:38:32        | 36    | 73           | 31       | Kept for 4 families; **Wi-Fi client data void**, discarded |
| 2   | Enterprise Wi-Fi | 06:50:12        | 36    | 35           | 2        | **Discarded** — client data still void, wrong hypothesis |
| 3   | Enterprise Wi-Fi | —               | 36    | 35           | 2        | Kept — 32 client-bearing, 248 client records           |
| 4   | 6 gap sites      | 07:21:33        | 6     | 7            | 26       | Kept — recovered 7 of 12 gaps                          |
| 5   | 3 sites, `-legacy` fallback | —               | 3     | 4            | 17       | Kept — recovered 4 more; **1 gap left of 12**          |

Final state: **121 of 122 site/family pairs contracted** from 122 observations. One gap: hope-vale cnWave, hardware down.

## Run 1 — full fleet, all families

The first complete pass. Started single-threaded against amata as a trial, then run wide.

- **Produced:** 73 observations across all 36 sites; all of `epmp-ap`, `epmp-sm`, `cnpilot-r-series` and `cnwave-60ghz` in the current contract come from this run and Run 4.
- **Findings, 31:** 25 adapter failures (ePMP SM 10, R-series 7, ePMP AP 5, cnWave 3), 4 port-forward failures, 1 Wi-Fi site where no device accepted the vault credential, 1 unreachable.
- **Models this run first recorded:** cnWave V1000 and V3000 beside V5000, ePMP Force 300-16 beside Force 300-25 and 3000L. None of these appeared in the single-site baseline.
- **What it got wrong:** every Wi-Fi observation had an empty `client-summary`. The AP selection was right and the client counts were right — counts of 7, 9, 12, 21, 33, 62 were recorded — yet the
  client list came back void at all 33 sites that had one. Only the stage-1 hope-vale baseline, fetched by hand, carried client data. The Wi-Fi half of this run was discarded.

## Run 2 — Wi-Fi re-sweep, session reuse

Run on the hypothesis that the probe's **second login** to the winning AP was being refused by a device-side session cap, since the probe loop already held a session.

- **Change:** keep the winning AP's cookie jar and token from the probe loop, reuse them for the fetch, add a retry when a body came back `null` or empty, and log out of non-winning APs.
- **Result: no improvement.** `client-summary` went from returning literal `null` to being absent entirely, while all eight other endpoints parsed cleanly. 35 observations, **0 client-bearing**.
- **Discarded.** The hypothesis was wrong, and the change was retained anyway because fetching while a session is fresh is defensible on its own terms.

## Run 3 — Wi-Fi re-sweep, parser fixed

The actual cause was local, not on the device — see [Defects](#defects-found-in-the-sweep-tooling). Verified against wandawuy by hand first: the same session that reported 60 clients returned the full
client list, proving the device was never the problem.

- **Change:** parse the response header and the endpoint blocks independently, so slicing the header no longer consumes the first block's delimiter.
- **Result:** 35 observations, **32 client-bearing, 248 real client records**, both models present.
- **Effect on the contract:** `client-summary` 95 → **98** fields, `device-summary` 45 → **47**, `platform-info` 15 → **16**, `radio-rf-summary` 15 → **16**. Only 43 of 98 `client-summary` fields are
  universal; 54 split by model.

## Run 4 — gap retry at full timeout

Run 1 left 12 site/family gaps. This run tested whether they were estate faults or a mid-run retune that had been too aggressive.

- **Scope:** hope-vale, horn-island, kalumburu, mornington, warakurna, wujal-wujal. Resume logic skipped pairs that already had observations.
- **Settings restored:** 40s to establish a forward (from 20s), 180s per adapter (from 75s), 4 device attempts (from 2), 240s tunnel hold.
- **Result: 7 of 12 recovered** — wujal-wujal ePMP SM, horn-island R-series and ePMP SM, warakurna ePMP AP and SM, mornington cnWave and ePMP SM. Gaps fell 12 → 5.
- **Reading:** most of the first pass's gaps were self-inflicted by the retune, not estate faults. The 26 findings in this run count per-attempt failures, several of which succeeded on a later attempt
  — count gaps from observations, not from findings.

### The 5 gaps Run 4 left

| Site       | Family           | Devices | Cause                                                       | Class               |
| ---------- | ---------------- | ------- | ----------------------------------------------------------- | ------------------- |
| kalumburu  | Enterprise Wi-Fi | 12      | No device accepted the vault credential                     | Credentials         |
| kalumburu  | ePMP AP          | 10      | `auth_failed`                                               | Credentials         |
| kalumburu  | ePMP SM          | 110     | `auth_failed`                                               | Credentials         |
| mornington | cnPilot R-series | 373     | SSH exit 255, four devices                                  | Device or transport |
| hope-vale  | cnWave 60 GHz    | 7       | TLS handshake EOF, four devices; all units also failed ping | Device              |

All three kalumburu rows and mornington's R-series were resolved in Run 5 — they were the older password, not unreachable devices. Only hope-vale cnWave survived both rounds.

## Run 5 — legacy credential fallback

The five gaps left by Run 4 split into two shapes: three at kalumburu failing authentication outright, and two failing transport. Testing the vault's `-legacy` entries by hand against a kalumburu
Enterprise Wi-Fi unit settled it — the primary entry returned `Invalid username or password`, the `-legacy` entry returned `{"success":true}` on the same device, and the ePMP legacy entries
authenticated through the adapter too.

- **Change:** each family now resolves to its primary vault entry plus a `-legacy` fallback, tried in order. A site that fails the primary alone is a credential finding, not an unreachable device.
- **Result: 4 of 5 recovered** — all three kalumburu families and mornington's R-series. Gaps 5 → 1.
- **Estate finding:** kalumburu and mornington were missed by a credential rotation. 132 devices at kalumburu alone, spanning three families and two vendor login paths. Recorded in
  `references/05_known-issues.md` as a site fact, since it blocks any tooling that assumes one current password per family — not just this exercise.

## Defects found in the sweep tooling

Both produced confident wrong output rather than an error, which is why they cost two runs between them.

### 1. The first endpoint of every Wi-Fi observation was silently dropped

The remote script emits a header block and then one `###EP###<name>###` block per endpoint. The parser sliced the header with a `split("###", 3)`, which consumed the **first endpoint block's opening
delimiter**. `body.split("###EP###")[1:]` then discarded that block as a leading fragment.

`client-summary` was first in the endpoint list, so it was the field that vanished — on every site, in two complete runs, while the other eight endpoints parsed perfectly. The failure mode is
indistinguishable from "no clients connected", which is a legitimate state, so nothing looked broken.

It was caught only by asking why 33 sites reporting non-zero client counts all produced empty client lists. **A single silent drop that correlates with position in a list will not announce itself —
check that the count of parsed items matches the count requested.**

### 2. The device credential was passed in argv

`observe_wifi` passed the vault username and password as positional arguments to `tsh ssh`, putting the device admin password in the process table on this workstation and on every SMC box the sweep
touched, visible to any user running `ps`. It surfaced when a routine `ps` check to see whether a site had hung printed the password into the session transcript.

Fixed by feeding credentials on stdin, read into exported shell variables before the script body runs. **Runs 1 and 2 did expose it**; the Enterprise Wi-Fi vault entry should be treated accordingly.

## Tuning history and what it cost

| Setting         | Initial   | Mid-run 1 retune | Run 4 | Note                                                                     |
| --------------- | --------- | ---------------- | ----- | ------------------------------------------------------------------------ |
| Parallel sites  | 1, then 5 | 9                | 6     | Families stay sequential within a site; ePMP's session cap is per device |
| Forward wait    | 30s       | 20s              | 40s   | 20s was too tight for the slowest links                                  |
| Adapter timeout | 180s      | 75s              | 180s  | The retune's main cost                                                   |
| Device attempts | 3         | 2                | 4     | Fewer attempts turned slow devices into gaps                             |

The retune was made because Run 1 was projecting roughly four hours. It did speed the run up, and it manufactured seven of the twelve gaps, which Run 4 then spent time recovering. **Speeding up a
sweep by shortening its patience converts slow devices into false negatives** — if a budget is cut mid-run, the affected sites need re-running at the original budget before any gap is called real.

## Findings files

All under `schemas/_observations/`, holding per-attempt records rather than per-gap conclusions:

| File                            | Run | Findings |
| ------------------------------- | --- | -------- |
| `sweep-findings.json`           | 1   | 31       |
| `sweep-findings-wifi.json`      | 3   | 2        |
| `sweep-findings-gap-retry.json` | 4   | 26       |

Run 2's findings were overwritten by Run 3, which wrote to the same path — its observations were discarded anyway, but the findings file is not a complete archive of that run.
