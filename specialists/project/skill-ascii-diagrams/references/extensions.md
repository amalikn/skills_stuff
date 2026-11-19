---
Title: Ascii Diagrams reference: Extensions
Category: reference
Status: current
Authority: >-
  skill-ascii-diagrams canonical reference; claims carry evidence labels and cite sources.yaml
Scope: What was researched and set aside
Last reviewed: 2026-11-19
Summary: >-
  Upstream ASCII tools researched on 2026-11-17, their licences, what each could give, why it is not used yet and how to enable it.
---

# Extensions

## Scope

Everything researched and not used yet, so stage 2 and stage 3 start without repeating the research. Not covered here: see the non-goals in [SKILL.md](../SKILL.md#role-and-non-goals).

## Contents of this reference

- [Decision rules](#decision-rules)
- [Worked example](#worked-example)
- [Further reading](#further-reading)

## Decision rules

| Item                              | Licence                         | Gives                                      | Why not now        | How to enable                                   |
| --------------------------------- | ------------------------------- | ------------------------------------------ | ------------------ | ----------------------------------------------- |
| mermaid-ascii (Go)                | MIT                             | A* routing, port choice, path merging      | stage 2            | port `getPath`, `mergePath` to `scripts/ascii/` |
| svgbob (Rust)                     | Apache-2.0                      | fragments, contacts, rectangle recognition | stage 3            | port `endorse_rect` with a NOTICE line          |
| asciiflow (TypeScript)            | MIT                             | junction normalisation                     | partly used (snap) | junction repair once Unicode is read            |
| MonoSketch (Kotlin)               | Apache-2.0                      | side-and-ratio attachment, joint masks     | stages 2 and 3     | reimplement with a NOTICE line                  |
| aafigure (Python)                 | BSD-style (clauses not checked) | claimed-cell mask, line tracing            | stage 3            | check its licence clauses first                 |
| ditaa (Java)                      | LGPL-3.0                        | open/closed boundary sets for nesting      | stage 3            | the idea only, never its code                   |
| Graph::Easy (Perl)                | GPL-2.0                         | grid layout, A*                            | not needed         | the idea only                                   |
| ascii-diagram-validator (Perl)    | none                            | alignment rules                            | no licence         | read only                                       |
| asciidiagrams.github.io           | none                            | 2156 real diagrams, tags                   | test corpus        | use as test input, never copy into the pack     |
| mcpmarket ascii-diagram-generator | unknown                         | Node grid engine (claimed)                 | repository 404     | none                                            |

- Licences were read from each repository (GitHub API) on 2026-11-17; MIT and Apache-2.0 code may be ported with its notice kept, LGPL and GPL never. `VERIFIED_PRIMARY` (C-AD03 for the finding that no
  tool parses and re-routes).

## Worked example

To port a function: copy the upstream file into `documents/ascii-sources-<date>/` (with `.txt`), add its row to that folder's `readme.md`, write the Python with a header line naming the upstream file,
licence and copyright, and add a test that fails without it.

## Further reading

- `documents/ascii-sources-20261117/readme.md` (URLs, fetch date, licences).
