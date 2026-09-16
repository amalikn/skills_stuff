---
title: Progressive Disclosure Reference Structure
type: adr
status: accepted
date: 20260626
provenance: promoted from CHANGELOG.md v0.1.2 on 20260626
---

# ADR: Progressive Disclosure Reference Structure

## Status

Accepted (implemented as of v0.1.2)

## Context

The original skill-smc pack had a monolithic `RUNBOOK.md` containing 1724 lines across 13 major sections: overview, service map, communication flows, dependency tree, troubleshooting, failure modes,
hardware/overlayroot, Ansible authoring, URL capture, captive portal, Vagrant lab, content filtering, and known issues.

Loading this file in full consumed significant context before any task-specific work could begin. A focused troubleshooting question required reading the entire service architecture section to get to
the troubleshooting section.

## Decision

Split RUNBOOK.md into 13 numbered focused reference files under `references/`:

- `01_overview.md` through `13_known-issues.md`
- RUNBOOK.md replaced with a 48-line navigation index providing a task-to-reference routing table
- Files numbered to establish a progressive learning path from foundational to specialized topics

## Consequences

**Positive:**
- Agents load only the specific reference needed (e.g. `05_troubleshooting.md` for a live incident)
- Total token cost for focused tasks drops from ~1700 lines to the relevant section only
- Navigation index (RUNBOOK.md) is short enough to read as a routing step without cost

**Negative:**
- More files to maintain (13 references vs 1 monolithic file)
- Cross-reference discipline required: adding a reference file requires updating 4 surfaces
- Install step now copies a directory (`references/*.md`) rather than a single file

## Enforcement

See rules:
- `.archcore/rules/rule-progressive-disclosure-loading.md`
- `.archcore/rules/rule-reference-update-discipline.md`
