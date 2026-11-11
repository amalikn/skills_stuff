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

> **Learned 2026-11-11** · ansible-core 2.17 (container) and 2.21.6 source · VERIFIED_PRIMARY (module source `ansible/modules/apt_key.py` `main()` and
> `parse_output_for_keys`; reproduced in ubuntu:22.04 against a keyring missing the new subkey) · Source: ansible-wifi `roles/smc_lynis/tasks/main.yml`
> (master `9d504a89`, rise `c4d2ef51`) · Falsifier: `apt_key` with `url` and no `id` importing a key whose primary is already in the keyring
> `apt_key` decides "present" before it imports: with `url` and no `id` it takes the first fingerprint of the downloaded key (the primary) and
> compares it with every `pub` and `sub` id already listed, so a vendor key that gained a new signing subkey is never refreshed (task `ok`, apt still
> `NO_PUBKEY <subkey>`). Pin `id` to the newest subkey's fingerprint so the check fails and the URL is imported, or put the key file under
> `/etc/apt/keyrings` with `get_url` (`force: true`) and `signed-by=`, which replaces it whenever the content changes.
>
> ```yaml
> - name: Download key from cisofy
>   ansible.builtin.apt_key:
>     id: 3E82FB7C68F57341349ED2C17A9A1D9D5B27C6D3  # newest signing subkey
>     url: https://packages.cisofy.com/keys/cisofy-software-public.key
>     state: present
> ```
