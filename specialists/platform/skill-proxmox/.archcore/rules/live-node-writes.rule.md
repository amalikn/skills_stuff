---
title: Writes to a live node need the engaging project's authorization, a plan and --apply
type: rule
status: accepted
tags: [safety, writes]
created: 2026-11-09
---

# Rule: Writes to a live node need authorization, a plan and --apply

Status: accepted (operator, 2026-11-09: "promote and accept all"; promoted from `AGENTS.md` Working rules and `SKILL.md` Read, write, and evidence boundaries).

## Rule

Reading a node (API GETs, `pvesh get`, `qm config`, `pveversion`) is fine where the engaging project allows read-only access. Every write needs that project's authorization, prints its plan first and
runs only with `--apply`: a `pvesh create|set|delete`, `qm set`, `pct set`, `pveum`, `apt update` (a write, it refreshes the package lists), `apt full-upgrade`, a node network change (it can cut off
access) and an OpenTofu apply. Skill use never authorizes a write by itself.

## Why

A node is shared infrastructure owned by the engaging project; a write from a skill session can stop guests, cut off management access or change what other automation sees.

## Enforcement

The pack's helpers read by default and gate their one write (`pve_node_report.py --refresh --apply`); skill-coder's `write_gates` check covers `scripts/`. Commands typed by an agent are covered by
this rule and the engaging project's own approval rules, which outrank it.
