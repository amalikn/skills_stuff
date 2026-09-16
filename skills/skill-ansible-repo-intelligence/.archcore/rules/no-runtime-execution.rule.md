---
id: no-runtime-execution
type: rule
title: No runtime execution during indexing
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from AGENTS.md invariants
tags: [security, safety]
---

# No runtime execution during indexing

The scanner must never execute repository code. Jinja is parsed via AST only (`.parse()`, never `render()`); custom vars plugins are analyzed with `ast`, never imported/executed; Ansible Vault is detected but never decrypted; no network/remote host is contacted; repository scripts are never run. This is a hard safety contract and must never regress.
