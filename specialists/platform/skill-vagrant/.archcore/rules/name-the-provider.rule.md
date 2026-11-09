---
title: A lab names its provider
type: rule
status: accepted
tags: [provider, safety]
created: 2026-11-09
Last reviewed: 2026-11-09
---

# Rule: A lab names its provider

Status: accepted 2026-11-09 by the operator (proposed 2026-11-09).

## Rule

A lab's Vagrantfile has exactly one `config.vm.provider` block for the provider it runs on, or its driver passes `--provider=<name>` on every
`vagrant up`. A Vagrantfile meant for several providers puts its preferred provider's block first and says so in its header.

## Why

Four providers are installed on the lab Mac (2026-11-09). Without `--provider`, Vagrant takes `VAGRANT_DEFAULT_PROVIDER`, then the first usable
provider block in file order, then plugin priority (`references/providers-and-choice.md`, claim V-C27), so the same file can come up on a
different hypervisor on another Mac or after a plugin install, with other networks, other guest agents and another VM name space.

## Enforcement

`vagrantfile_lint.py --provider <name>` fails a file with no block for that provider. Not enforced: a file with blocks for several providers in an
unintended order (candidate check).
