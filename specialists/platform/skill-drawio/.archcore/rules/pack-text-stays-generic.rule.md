---
title: Pack text stays generic
type: rule
status: accepted
tags: [pack-content, safety]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Pack text stays generic

Status: accepted (source `AGENTS.md` working rules; promoted 2026-10-19 on the operator's instruction "promote and accept")

## Rule

No customer names, hostnames, private addresses or tokens in pack text. A governed project is named only as a rule's source. Verbatim vendor captures may show the vendor's example addresses.

## Enforcement

`tests/test_package_contract.py` `test_text_is_safe` (captures exempt from the address check only).
