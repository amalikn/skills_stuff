---
Title: ansible override - learned tooling
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned tooling part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned tooling

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-23 (e)** · task comments · USER_STATED (operator, 2026-10-23: "not for every task but the simple ones you can ignore but the ones which should have some description you can add") · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/` · Falsifier: the operator asks for a comment on every task, or for none
> A comment goes above a task only when it says something the name does not: why the task exists, a constraint, a non-obvious effect or
> failure mode. Simple tasks (a stage banner, a debug print, an include whose name says it all) carry none. Each task file starts with a
> header block: purpose, Called by, Reads, Sets, Notes.

> **Learned 2026-11-05 (j)** · ansible-core 2.18.8 (controller VM) and 2.21.5 (source read), `find` depth, `async`, extra vars · VERIFIED_PRIMARY (module source; observed on an EFS-backed store) · Source: `ansible/modules/find.py` lines 569-579 (2.21.5); ansible-malik `smc_get_pcapv8.yml` (2026-11-05) · Falsifier: a `find` with `depth: N` whose run time does not grow with the number of entries inside the depth-N directories
