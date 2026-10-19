---
title: Pack text stays generic and safe
type: rule
status: accepted
tags: [pack-content, checkers]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Pack text stays generic and safe

Status: accepted (stated in `AGENTS.md` "Working rules"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

No customer names, hostnames, private addresses, tokens, credentials or production domains in pack files. A governed project is named only as a rule's source. Verbatim third-party captures under
`documents/` are exempt from the address and domain checks (a specification's section numbers look like addresses), never from the credential and key checks.

## Why

The pack is installed into every agent and read by every project; anything specific in it leaks one environment into all of them.

## Enforcement

`tests/test_package_contract.py` (`test_text_is_safe`, proven able to fail by `test_unsafe_text`) catches credentials, private keys, private addresses and production domains. Customer names and
hostnames are not machine-checked; review.
