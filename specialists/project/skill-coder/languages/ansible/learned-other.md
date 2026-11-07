---
Title: ansible override - learned other
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned other part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: learned other

Part of [ansible.md](../ansible.md).

> **Learned 2026-10-27 (k)** · ansible-core 2.21.5 · VERIFIED_PRIMARY (seen in smc_change run output, fixed and re-rendered in a scratch copy) · Source: local-knowledge-ansible `plans/smc-change-resume-20261027_1038/prepare-once.patch` (`tasks/plan.yml`) · Falsifier: a `to_json` value
> inside a `debug` message list printed without backslashes
> `debug` prints its `msg` as JSON, so a list item built with `to_json` is encoded twice and every quote shows as `\"`
> (`BACKUP   {\"paths\": [\"/etc/php\", ...]}`). For operator-facing lines, write the values as words (`join(', ')`, a phrase per flag), and
> keep `to_json` for files and machine records.
>
> ```yaml
> - 'BACKUP   ' ~ ((smc_change_spec.backup.paths | default([]) | join(', ')) or 'no paths')
>   ~ ('; repack the packages about to change' if smc_change_spec.backup.repack | default(false) else '')
> ```
