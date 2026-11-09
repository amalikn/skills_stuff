---
title: Memory channel is exactly vagrant
type: rule
status: accepted
tags: [memory]
created: 2026-11-07
Last reviewed: 2026-11-09
---

# Rule: Memory channel is exactly `vagrant`

Status: accepted 2026-11-09 by the operator (proposed 2026-11-07).

## Rule

memory-keeper entries about this pack use the channel `vagrant` — exactly that string. Project-specific lab notes may also go to the engaging project's channel.

## Why

One channel per platform pack makes recall for Vagrant work one query across projects.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `vagrant` is unaffected by either.
