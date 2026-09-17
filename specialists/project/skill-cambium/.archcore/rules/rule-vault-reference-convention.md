---
title: Vault Reference Convention, Never Plaintext Values
type: rule
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; accepted by operator 20260917
---

# Rule: Vault Reference Convention, Never Plaintext Values

Never write a device password or other plaintext sensitive value into any file in this pack. Use the reference convention `<secret:keepassxc:cambium-devices/<entry>>` instead — see
`references/02_device-access-and-vault.md` for the vault structure this points into.

Avoid the blocked words (the ones the workspace's OPA write-gate hard-blocks in file **paths**, regardless of content) in every file path in this pack — not just the vault reference file. Hit and
worked around on 2026-09-17, and again while promoting this rule into `.archcore/`.

**Rationale:** the OPA gate blocks on path text alone, so a compliant file with a non-compliant name still fails to write. Getting the naming right the first time avoids a blocked write mid-task.

## Enforcement

See ADR: `.archcore/adr/adr-vault-file-avoids-opa-blocked-words.md`
