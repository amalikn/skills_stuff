---
title: "A new skill starts from a seed and the shared scaffold"
status: accepted
tags: [skills]
---

Added 2026-11-12 (operator); [AGENTS.md](../../AGENTS.md) (Working rules) has one line pointing here.

## Rule

A new skill pack is built with `new-skill` ([references/new-skill.md](../../references/new-skill.md)): a seed from `templates/skill-seed.md` that records what the engagement learned, then the scaffold
from `templates/skill-pack/`, then `skill_pack_check.py` on the result. Never copy a sibling pack by hand. A change to the shape every pack shares (a SKILL.md section, a required file) is made once, in the
template and the check together, and recorded in the CHANGELOG; the five model packs (skill-nautobot, skill-vagrant, skill-coder, skill-network-architect, skill-systems-architect) are the reference. A seed is a folder in `pending_skills/<name>/`: its research and part files
are kept there permanently beside the seed (operator, 2026-11-12), never deleted or moved after the build.

## Rationale

Packs built by hand drifted from one another (skill-mikrotik, 2026-10-07) and the lessons of the work that produced them were not kept. One seed and one contract keep the shape and the knowledge.
