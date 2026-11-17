---
Title: skill-ascii-diagrams
Category: readme
Status: current
Authority: canonical
Scope: Root README.md of skill-ascii-diagrams
Last reviewed: 2026-11-17
Summary: "ASCII diagrams in documents: draw from a spec, repair hand-drawn ones, check edges and arrows"
Budget: 200 lines, 25 KB
---

# skill-ascii-diagrams

ASCII diagrams in documents: draw from a spec, repair hand-drawn ones, check edges and arrows

## Purpose

An agent writing or reviewing documents can draw an ASCII diagram that stays aligned, and can take a diagram someone drew by hand (or an agent typed) and repair it without restyling it: ragged right
edges closed, borders redrawn to their box, connectors snapped into line, arrows that miss their box reported. Next it lays out a graph of boxes and links with orthogonal routing (stage 2) and reads a
hand-drawn diagram back into that graph (stage 3). ASCII is the immediate diagram of a document; draw.io is drawn only when explicitly asked (operator, 2026-11-16).

## Folder index

- [SKILL.md](SKILL.md): the activation surface an agent loads; routes every reference.
- [references/](references/readme.md): one focused file per topic.
- [sources.yaml](sources.yaml) and [compatibility.yaml](compatibility.yaml): the claims the pack makes with their falsifiers, and the environments tested.
- [tests/](tests/scenarios.md): behaviour scenarios and the package contract test.
- [docs/](docs/): session records and history.

## Run

```bash
just bootstrap   # build the working-cache venv from the mise pin
just check       # governance checks; must exit 0 before work is called complete
just test        # package contract and helper tests
```

## Related

- **skill-drawio**: draw.io drawings and flow maps, only when explicitly asked; its routing rules feed stage 2 here.
- **skill-coder**: how this pack's scripts are written and tested; code-practice lessons go there.
