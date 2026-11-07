---
Title: ansible override - before any change trace every reference
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/ansible.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The before any change trace every reference part of the ansible override; the entry file holds the tools and the core rule mapping.
---

# ansible: before any change trace every reference

Part of [ansible.md](../ansible.md).

Operator directive: understand the complete impact of any change by going through every reference to it in other roles and files. Before editing any identifier (tag, variable, handler, role name, file
path):

1. Search the whole repository with every file type that can hold it: `*.yml`, `*.yaml`, `*.j2`, `*.sh`, `*.cfg`, `*.ini`, `*.json`, `*.md`. **Templates (`*.j2`) are the ones people forget**; they
   consume variables, and a YAML-only search misses them.
2. **Classify every hit** as tag declaration, variable, or unrelated namesake before changing anything. The same word is often both a tag and a variable. Anchor any edit pattern (for example
   `^\s*tags:\s*<name>$`) rather than replacing blindly.
3. Check external callers: CI jobs, scripts and runbooks that pass `--tags` or `--skip-tags`.
4. Collision-check a new name against the repository's existing tag vocabulary.
5. Verify selection with `--list-tasks` and behaviour with a `--check --diff` dry run; `--syntax-check` and `--list-tasks` do not show that a selected task is destructive.
6. **Decide the transition explicitly.** When every caller is inside the repository, rename in one change and update them all. When a caller may sit outside it (another repository, a job template, a
   scheduler, an operator's notes), list both names for one transition (`tags: [<new>, <old>]`), record the old name and its removal condition in the change log, and remove it once no caller remains.
   This is the shim rule for code moves ([references/refactoring-and-promotion.md](../references/refactoring-and-promotion.md)) applied to a tag: the old name keeps working until nothing uses it, and
   it is never left in place without a recorded end (USER_STATED: the operator's renames keep an old name readable during a transition, 2026-10-19).

**A renamed tag fails silently.** Ansible does not warn on an unmatched tag: the old command still exits 0 and runs only the tasks tagged `always`, while selecting none of the intended ones. After a
rename, update every runbook and history copy (USER_STATED; the documentation's `always` and `never` tag behaviour is VERIFIED_PRIMARY, the lack of a warning is from the operator's incident).

Why: a tag added to fix one bug once made a destructive wipe-and-re-clone reachable under a name that read like a repair, coupled to a template in another role.
