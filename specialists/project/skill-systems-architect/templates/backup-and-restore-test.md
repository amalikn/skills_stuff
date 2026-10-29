---
Title: Backup and restore test template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: RPO and RTO per dataset, copy placement against the 3-2-1 rule, restore estimate and a restore drill record with measured time against target.
---

# <scope> backup and restore test

Based on: NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems (https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final), for RTO, RPO and testing.

## How to use

- A completed backup job is not recovery evidence. Only a measured restore to a usable service is.
- Set RPO and RTO per dataset from the consequence of loss, not per tool.
- Choose the DR rung first (backup and restore, pilot light, warm standby, active/active); see the
  [DR strategy ladder](../references/backup-disaster-recovery.md#dr-strategy-ladder).
- 3-2-1 check: at least three copies, on two different media or systems, one off site.
- Add one offline or immutable copy where ransomware is in scope.
- Estimate restore time with `just capacity <plan.json>` ([capacity_check.py](../scripts/capacity_check.py)).
  Its `restore` block takes `data_gib`, `throughput_mbps`, `efficiency`, `fixed_seconds`, `rto_seconds`.
- The estimate is a serialised lower bound. RTO also includes detection, decision, provisioning, replay, startup and validation, so drill it.

## 1. Datasets and targets

| Dataset   | Service   | Size (GiB) and growth | Consistency need (crash, app, DB log) | RPO     | RTO     | Owner  | Label       |
| --------- | --------- | --------------------- | ------------------------------------- | ------- | ------- | ------ | ----------- |
| <dataset> | <service> |                       |                                       | <n> min | <n> min | <role> | USER_STATED |

## 2. Copies and placement

| Dataset | Copy           | Location / failure domain | Medium or system | Schedule | Retention | Immutable / offline | Encryption key custody | Last success |
| ------- | -------------- | ------------------------- | ---------------- | -------- | --------- | ------------------- | ---------------------- | ------------ |
|         | 1 production   |                           |                  |          |           |                     |                        |              |
|         | 2 local backup |                           |                  |          |           |                     |                        |              |
|         | 3 off site     |                           |                  |          |           |                     |                        |              |

3-2-1 result per dataset: *copies <n>, media <n>, off site yes/no, immutable yes/no.*

```text
Copy and restore paths for <dataset> (fill in; mark any shared failure domain with X)

  [production <site/rack>] --<schedule>--> [backup store <domain>]
  [backup store <domain>]  --<pull sync>--> [off-site copy <domain>]
  restore: [off-site copy] --<link, Mbit/s>--> [recovery target <domain>]
  Shares a domain with production?  yes (X) / no
  Legend: --> data flow   X shared failure domain
```

## 3. Restore estimate

| Dataset | data_gib | throughput_mbps | efficiency | fixed_seconds | Estimated seconds | rto_seconds | Exit code |
| ------- | -------- | --------------- | ---------- | ------------- | ----------------- | ----------- | --------- |
|         |          |                 |            |               |                   |             |           |

## 4. Restore drill record

| Field                                                                     | Value                                                       |
| ------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Drill ID / date / operator                                                | <RD-nnn> / <YYYY-MM-DD> / <role>                            |
| Scenario                                                                  | *single file, VM, full dataset, site loss, credential loss* |
| Restore point chosen and its age                                          |                                                             |
| Recovery target and isolation from production                             |                                                             |
| Dependencies needed (keys, identity, DNS, licences) and whether available |                                                             |

| Phase                      | Start | End | Measured duration  | Notes       |
| -------------------------- | ----- | --- | ------------------ | ----------- |
| Detection and decision     |       |     |                    |             |
| Provision target           |       |     |                    |             |
| Data transfer              |       |     |                    |             |
| Replay / consistency       |       |     |                    |             |
| Start and validate service |       |     |                    |             |
| **Total vs RTO**           |       |     | <n> min vs <n> min | pass / fail |

Data loss measured vs RPO: *<n> min of changes lost vs <n> min allowed.* Validation: *user-outcome test used to declare service usable.*

## 5. Findings and actions

| Finding | Effect on RTO/RPO | Action | Owner | Due |
| ------- | ----------------- | ------ | ----- | --- |
|         |                   |        |       |     |

## 6. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
