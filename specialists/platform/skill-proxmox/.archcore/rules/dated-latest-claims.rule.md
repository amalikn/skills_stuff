---
title: Latest-version claims carry the date they were checked
type: rule
status: accepted
tags: [evidence, versioning]
created: 2026-11-09
---

# Rule: Latest-version claims carry the date they were checked

Status: accepted (operator, 2026-11-09; promoted from ARCHCORE_PROMOTION_CANDIDATES.md).

## Rule

Any statement that a Proxmox VE, PBS, PDM or bpg/proxmox release is "latest", "current" or "newest" names the date it was checked and the capture behind it (a file under
`documents/research-sources-<YYYYMMDD>/` or a dated `compatibility.yaml` row). An undated "latest" is wrong the day a new release ships and gives the next reader no way to tell.

## Why

Releases move under the pack: 9.2 for arm64 (2026-08-05), PBS 4.2 (2026-04-29) and PDM 1.1 (2026-05-28) all shipped after earlier text was written. Claim P-C27 and the 2026-11-09 Key anchors already
follow the form ("latest ... checked 2026-11-09").

## Enforcement

Scenario P-S20 prohibits stating "latest" without the date it was checked. No automated check yet.
