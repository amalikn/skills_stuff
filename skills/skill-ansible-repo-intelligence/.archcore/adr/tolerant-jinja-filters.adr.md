---
id: tolerant-jinja-filters
type: adr
title: Tolerant Jinja filter map for parse-only var extraction
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ARCHITECTURE.md
tags: [jinja, parsing]
---

# Tolerant Jinja filter map for parse-only var extraction

Decision: give the Jinja Environment a filter/test map returning an identity callable for unknown names. `meta.find_undeclared_variables` runs a codegen pass that rejects unknown Ansible filters (dict2items, ipaddr, ...). The identity callable is never invoked — parsing only — so this stays strictly parse-only.
