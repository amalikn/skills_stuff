---
id: derived-context-authority
type: rule
title: Generated context is derivative
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from AGENTS.md
tags: [governance, authority]
---

# Generated context is derivative

Generated `.ai-context/` artifacts are navigation metadata, not source of truth, and never outrank a target repo's existing `.archcore/` or `context-map.yaml` authority. Source files are always authoritative; the scanner registers its outputs as derived and must not create a competing first-read sequence.
