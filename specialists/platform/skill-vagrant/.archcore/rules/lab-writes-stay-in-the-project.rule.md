---
title: VM writes stay in the engaging project
type: rule
status: proposed
tags: [safety]
created: 2026-11-07
---

# Rule: VM writes stay in the engaging project

Status: proposed (2026-11-07), awaiting the operator.

## Rule

This pack's helpers and its own sessions run read-only `vagrant` and `prlctl` commands only (status, list, box list, global-status, capture). Starting, stopping, resetting, cloning,
snapshotting, reprovisioning or destroying a VM is done by the engaging project's tooling, behind its plan/`--apply` gate, with a fixed lab VM name and a deadline on every call.

## Why

The pack is shared by every project; a write helper here would run without the project's guards (its wrong-VM marker, its disk guard, its stage records). The brief that created the
pack said: "Do not start, stop, reset or change any VM; read-only vagrant/prlctl commands only."

## Enforcement

`tests/test_package_contract.py` requires a timeout on every subprocess call in `scripts/`; `scripts/README.md` labels each helper; a helper that writes would need a new rule here first.
