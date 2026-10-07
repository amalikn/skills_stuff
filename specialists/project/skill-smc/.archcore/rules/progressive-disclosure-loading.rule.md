---
title: Progressive Disclosure Loading
type: rule
status: accepted
provenance: promoted from AGENTS.md + AI_NAVIGATION.md on 20260626
---

# Rule: Progressive Disclosure Loading

RUNBOOK.md is a navigation index only. Do not use it as a content source.

When loading reference material for a task, load only the specific numbered reference file needed:
- Identify the task type
- Consult RUNBOOK.md routing table (or AI_NAVIGATION.md reference routing) to find the correct file
- Load only that file — do not load all 13 references up front

Loading multiple references is only justified when the task genuinely spans multiple domains (e.g. live incident involving both `05_troubleshooting.md` and `07_hardware-overlay.md`).

**Rationale:** The 13 reference files total ~1700+ lines. Loading all up front consumes context that could be used for the actual task and degrades response quality on focused questions.
