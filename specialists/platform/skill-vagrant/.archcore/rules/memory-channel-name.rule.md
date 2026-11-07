---
title: Memory channel is exactly vagrant
type: rule
status: proposed
tags: [memory]
created: 2026-11-07
---

# Rule: Memory channel is exactly `vagrant`

Status: proposed (2026-11-07), awaiting the operator; mirrors skill-nautobot's `nautobot` rule.

## Rule

memory-keeper entries about this pack use the channel `vagrant` — exactly that string. Project-specific lab notes may also go to the engaging project's channel.

## Why

One channel per platform pack makes recall for Vagrant work one query across projects.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `vagrant` is unaffected by either.
