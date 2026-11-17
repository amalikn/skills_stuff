---
Title: Skill intake: skill-ascii-diagrams
Category: skill-intake
Status: draft
Authority: >-
  Interview record for a new skill pack: the operator's answers and the research plan the seed is built from; written with `new-skill intake` and filled by the agent in rounds
Scope: What the operator wants the skill to do, what to harvest from existing work, and which topics need online research
Last reviewed: 20261117_1141
Summary: >-
  Intake for skill-ascii-diagrams: the questions asked in rounds, the answers recorded as USER_STATED, the material to harvest, the neighbour skills to study and the research topics that become research briefs.
---

# Skill intake: skill-ascii-diagrams

<!-- intake: the agent runs this interview; the script only holds the form. Protocol (references/new-skill.md, "Stage 1"):
1. Search before asking: read the conversation, the files and repos the operator names, and the model packs; fill every answer they already give, tagged with its source.
2. Ask only what is left, at most four questions per round, each with two to four options and a recommended one; use the question tool; never ask something a file answers.
3. Record each answer in the operator's own words under the question, labelled USER_STATED (or the source file when inferred, labelled VERIFIED_PRIMARY or UNVERIFIED).
4. An answer of "not sure" becomes an open question in the seed, marked later or blocking.
5. When every TODO(intake) is gone, run `new-skill research-briefs`, dispatch the briefs, save the reports under research/, then build the seed with `new-skill seed --from-intake`. -->

## Contents

- [Parameters](#parameters)
- [Round 1: purpose and callers](#round-1-purpose-and-callers)
- [Round 2: boundaries and safety](#round-2-boundaries-and-safety)
- [Round 3: knowledge to keep](#round-3-knowledge-to-keep)
- [Round 4: quality and install](#round-4-quality-and-install)
- [Material to harvest](#material-to-harvest)
- [Neighbour skills to study](#neighbour-skills-to-study)
- [Research topics](#research-topics)

---

## Parameters

Filled from the answers below; `new-skill seed --from-intake` copies them into the seed. `forbidden_terms` are project, customer and people names that must never appear in the finished pack or in a
research brief.

```text intake-parameters
name: skill-ascii-diagrams
family: specialists/project
short_description: ASCII diagrams in documents: draw from a spec, repair hand-drawn ones, check edges and arrows
scripts: yes
operator_context: no
memory_channel: skill-ascii-diagrams
related: skill-drawio, skill-coder
forbidden_terms: APN, apn, smc-resiliency, unified-network-controller, UNC, enterprise-strategy
```

## Round 1: purpose and callers

<!-- Options for Q1.3: specialists/project (method or practice for any project), specialists/platform (one product or tool), skills (single-file contract), personal. -->

- Q1.1 In one sentence, what should an agent be able to do with this skill that it cannot do reliably now? Answer: draw an ASCII diagram for a document that stays aligned, and repair an existing one that drifted, without restyling it (USER_STATED 2026-11-17: "if there is an existing diagram, we can pass that diagram to the skill and it can fix it").
- Q1.2 Who or what calls it, and in which situations (the operator, another skill, a project)? Give the phrases you would say. Answer: any project writing Markdown docs; "add/update and improve ascii diagrams where needed", "why is the right side alignment not fixed", "fix this diagram" (USER_STATED 2026-11-17).
- Q1.3 Is it a method or practice for any project, one product or tool, a single-file contract, or personal? Answer: specialists/project (USER_STATED 2026-11-17).
- Q1.4 What should it be called (skill-topic, lowercase) and is a slash alias wanted? Answer: skill-ascii-diagrams; no alias (USER_STATED 2026-11-17).

## Round 2: boundaries and safety

- Q2.1 What must it not do, and which neighbouring skill owns that instead? Answer: no draw.io drawings (skill-drawio, only when explicitly asked: operator 2026-11-16); no domain facts shown in a diagram (the domain skill); no restyling of a correct drawing.
- Q2.2 What may it write, what needs your approval or `--apply`, and what must it never do (send, publish, delete, touch live systems)? Answer: read-only by default; `--apply` writes the fixed ```text blocks of the named file only; never a file with a GENERATED banner (fix its source); words never change.
- Q2.3 Will it need scripts (checks, builders, converters), or is it guidance only? Answer: scripts (renderer, fixer, checks; stage 2 graph renderer, stage 3 parser).
- Q2.4 Which rules are yours alone (tone, spelling, naming, estate) and belong in an operator layer, and which names must never appear in the shared pack? Answer: no operator layer; ASCII first, draw.io only when asked (operator 2026-11-16) is a standing rule; project names in forbidden_terms.

## Round 3: knowledge to keep

- Q3.1 Which work has taught you what the skill must hold (sessions, projects, files, transcripts)? List each; the agent harvests them. Answer: the session of 2026-11-17 (ascii-fix built and corrected over real documents), skill-drawio's ASCII renderer promotion (2026-11-16), skill-drawio references/data-first-diagrams.md Learned 2026-11-16 and 2026-11-17.
- Q3.2 What went wrong first, and what fixed it? These become rules. Answer: restyling correct drawings, grid dividers read as bottoms, glued connectors split, a generated file written, borders carrying arrows unrecognised, ragged-row tails anchored to the wrong column, stale .pyc in mutation tests; fixes in the seed's What was learned.
- Q3.3 Which code or scripts already exist and are likely to be reused (paths)? Answer: skill-drawio scripts/ascii_flow_render.py, scripts/ascii_fix.py, scripts/ascii/ (checks.py), tests/test_ascii_flow_render.py, tests/test_ascii_fix.py, documents/ascii-sources-20261117/.
- Q3.4 Which products, formats and versions are in scope, and which are explicitly out? Answer: plain ASCII in Markdown ```text blocks and plain-text files; Unicode box drawing read later (stage 3), not drawn (USER_STATED 2026-11-17); Mermaid and draw.io out.

## Round 4: quality and install

- Q4.1 Give three to five example prompts, including one that must not trigger the skill and one where the agent must stop and ask. Answer: inferred from the session: "fix the diagrams in this doc"; "draw the boot flow as ASCII"; "why is the right edge ragged"; must not trigger: "make a draw.io drawing of the flows"; stop and ask: a diagram in a generated file, or a change that would restyle a deliberate layout.
- Q4.2 What evidence standard applies (primary sources only, or practice accepted if labelled)? Answer: global policy: labelled claims; behaviour proven by tests with mutation checks and a sweep over real documents.
- Q4.3 Which decisions are still open, and which block the build? Answer: later: whether the projects' edge checker (owned by another project) retires into this skill; stage 2 and 3 designs. None blocking.

## Material to harvest

<!-- Everything the agent must read for lessons: the current conversation, files, repositories, earlier session records. One row each; delete the placeholder row if none. -->

| Source       | Where        | What to extract |
| ------------ | ------------ | --------------- |
| This session transcript | Claude Code session 6efe1009, 2026-11-17 | every ascii-fix fault found and its fix |
| skill-drawio ASCII code | specialists/platform/skill-drawio/scripts/ascii*, tests/test_ascii_* | the code to move |
| skill-drawio reference | references/data-first-diagrams.md Learned 2026-11-16, 2026-11-17 | lessons to move |
| Research reports | research/ (this seed folder) | upstream tools, licences, reusable parts |

## Neighbour skills to study

<!-- Model packs and neighbouring skills the agent reads before writing the seed: skill-nautobot, skill-vagrant, skill-coder, skill-network-architect and skill-systems-architect set the shape. -->

- skill-drawio (the neighbour this splits from; routing rules in references/layout-and-routing.md), skill-coder (code practice, testing), skill-vagrant (a small read-only tool pack's shape).

## Research topics

<!-- One row per area for web research. Each becomes a research brief with generic queries (no forbidden term), dispatched to a research agent; reports are saved under research/. Cover tools and libraries
with their licences, existing skills and public examples, standards and authoritative methods, and failure modes. -->

| Area         | Questions the research must answer | Products, formats or versions in scope |
| ------------ | ---------------------------------- | -------------------------------------- |
| ASCII diagram tools | Done 2026-11-17: which tools parse, route, lint or fix ASCII box diagrams, with licences | svgbob, mermaid-ascii, asciiflow, box-diagram, aafigure, ditaa, Graph::Easy, Diagon, goat, MonoSketch, the asciidiagrams catalogue |
