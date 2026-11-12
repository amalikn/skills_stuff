---
Title: Skill intake: <skill-name>
Category: skill-intake
Status: draft
Authority: >-
  Interview record for a new skill pack: the operator's answers and the research plan the seed is built from; written with `new-skill intake` and filled by the agent in rounds
Scope: What the operator wants the skill to do, what to harvest from existing work, and which topics need online research
Last reviewed: 2026-11-12
Summary: >-
  Intake for <skill-name>: the questions asked in rounds, the answers recorded as USER_STATED, the material to harvest, the neighbour skills to study and the research topics that become research briefs.
---

# Skill intake: <skill-name>

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
name: TODO(intake)
family: specialists/project
short_description: TODO(intake)
scripts: TODO(intake)
operator_context: TODO(intake)
memory_channel: TODO(intake)
related: TODO(intake)
forbidden_terms:
```

## Round 1: purpose and callers

<!-- Options for Q1.3: specialists/project (method or practice for any project), specialists/platform (one product or tool), skills (single-file contract), personal. -->

- Q1.1 In one sentence, what should an agent be able to do with this skill that it cannot do reliably now? Answer: TODO(intake)
- Q1.2 Who or what calls it, and in which situations (the operator, another skill, a project)? Give the phrases you would say. Answer: TODO(intake)
- Q1.3 Is it a method or practice for any project, one product or tool, a single-file contract, or personal? Answer: TODO(intake)
- Q1.4 What should it be called (skill-topic, lowercase) and is a slash alias wanted? Answer: TODO(intake)

## Round 2: boundaries and safety

- Q2.1 What must it not do, and which neighbouring skill owns that instead? Answer: TODO(intake)
- Q2.2 What may it write, what needs your approval or `--apply`, and what must it never do (send, publish, delete, touch live systems)? Answer: TODO(intake)
- Q2.3 Will it need scripts (checks, builders, converters), or is it guidance only? Answer: TODO(intake)
- Q2.4 Which rules are yours alone (tone, spelling, naming, estate) and belong in an operator layer, and which names must never appear in the shared pack? Answer: TODO(intake)

## Round 3: knowledge to keep

- Q3.1 Which work has taught you what the skill must hold (sessions, projects, files, transcripts)? List each; the agent harvests them. Answer: TODO(intake)
- Q3.2 What went wrong first, and what fixed it? These become rules. Answer: TODO(intake)
- Q3.3 Which code or scripts already exist and are likely to be reused (paths)? Answer: TODO(intake)
- Q3.4 Which products, formats and versions are in scope, and which are explicitly out? Answer: TODO(intake)

## Round 4: quality and install

- Q4.1 Give three to five example prompts, including one that must not trigger the skill and one where the agent must stop and ask. Answer: TODO(intake)
- Q4.2 What evidence standard applies (primary sources only, or practice accepted if labelled)? Answer: TODO(intake)
- Q4.3 Which decisions are still open, and which block the build? Answer: TODO(intake)

## Material to harvest

<!-- Everything the agent must read for lessons: the current conversation, files, repositories, earlier session records. One row each; delete the placeholder row if none. -->

| Source       | Where        | What to extract |
| ------------ | ------------ | --------------- |
| TODO(intake) | TODO(intake) | TODO(intake)    |

## Neighbour skills to study

<!-- Model packs and neighbouring skills the agent reads before writing the seed: skill-nautobot, skill-vagrant, skill-coder, skill-network-architect and skill-systems-architect set the shape. -->

- TODO(intake)

## Research topics

<!-- One row per area for web research. Each becomes a research brief with generic queries (no forbidden term), dispatched to a research agent; reports are saved under research/. Cover tools and libraries
with their licences, existing skills and public examples, standards and authoritative methods, and failure modes. -->

| Area         | Questions the research must answer | Products, formats or versions in scope |
| ------------ | ---------------------------------- | -------------------------------------- |
| TODO(intake) | TODO(intake)                       | TODO(intake)                           |
