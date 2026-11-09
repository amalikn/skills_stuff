---
title: Project facts stay in the engaging project; project rules outrank the pack
type: rule
status: accepted
tags: [boundary, redaction]
created: 2026-11-09
---

# Rule: Project facts stay in the engaging project

Status: accepted (operator, 2026-11-09: "promote and accept all"; promoted from `SKILL.md` Project boundary and `AGENTS.md` Working rules).

## Rule

Node names, addresses, VMID ranges, pools, token identities, password-manager entries and lab inventories belong to the engaging project, never to this pack. A worked case cited here (for example
smc-resiliency's x86 lab) is an example, not stock behaviour. A project's own Proxmox conventions (pools, token identities, VMID ranges, approval rules) outrank this pack: read its `AGENTS.md` before
any write.

## Why

The pack is cross-project and shareable; a project fact copied into it goes stale, leaks a site detail and misleads the next project.

## Enforcement

`tests/test_package_contract.py` scans every `.md`, `.yaml` and `.txt` file (generated ones included) for credentials, private addresses and production domains; facts that are not secrets (a node
name, a VMID range) rely on this rule.
