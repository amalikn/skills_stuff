---
name: github-explorer
description: "Deep-dive analysis of a GitHub repo: architecture, health, competitive context."
---

# GitHub Explorer — Project Deep Dive

> The README is a starting point. Useful evidence also lives in releases, commits, issues, discussions, and independent user reports.

## Workflow

```text
[project] -> [locate repository] -> [gather evidence] -> [analyse] -> [structured report]
```

### 1. Locate the repository

- Search for `site:github.com <project-name>` and verify the organisation and repository.
- Read the repository page for its README, license, contributors, releases, stars, forks, and recent activity.
- Use official project documentation and primary project material first.

### 2. Gather evidence proportionately

Inspect only sources that help answer the question.

| Source | What to collect | Preferred approach |
| --- | --- | --- |
| GitHub repository | README, architecture cues, contributors, license | fetch the repository page |
| GitHub issues and discussions | well-supported technical trade-offs and maintainers' responses | inspect selected high-signal threads |
| Releases and commits | maintenance cadence, major changes, project stage | review recent release and commit history |
| Official documentation | supported usage, integration limits, roadmap evidence | fetch official documentation |
| Independent technical and community discussion | real-world experience, alternatives, adoption constraints | search, then link primary posts |

When a page is dynamic, blocked, malformed, or missing material content, use an alternate retrieval method. Do not invent data or claim a page was read when it was not.

### 3. Analyse

Evaluate the evidence against the user’s actual decision:

- **Project stage:** experimental, growing, mature, maintenance, or apparently stalled. Base this on dated evidence.
- **Architecture:** explain the core mechanism in plain language and distinguish documented facts from inference.
- **Project health:** consider maintenance activity, releases, contributor concentration, issue response, license, and ecosystem fit.
- **Issues:** select three to five threads only when they reveal meaningful technical trade-offs or adoption risks.
- **Alternatives:** identify relevant competitors from official comparisons, documentation, issues, and cited sources.
- **Community evidence:** summarise specific attributable claims with links, never vague popularity statements.

### 4. Report

Every factual external claim needs a direct source link. Mark unavailable information as “Not found” rather than filling gaps with guesswork.

```markdown
# [Project Name](https://github.com/org/repo)

**One-line position**

What it is, the problem it addresses, and the likely user.

**Core mechanism**

Plain-language architecture and key technologies, with sources.

**Project health**

- Stars, forks, license, contributors, and recent activity, each dated and linked.
- A concise project-stage assessment with supporting evidence.

**High-signal issues**

Three to five linked issues or discussions, including why each matters. Write “Not found” when none are useful.

**Where it fits**

Concrete jobs, requirements, and conditions where it is a good choice.

**Limits and risks**

Known constraints, unresolved issues, and conditions where another option is safer.

**Alternatives**

- **vs [Alternative](URL)** — relevant difference and source.

**References and community evidence**

Specific linked documentation, posts, or discussions; describe the claim each supports.

**Assessment**

Decision-oriented recommendation, confidence, unresolved evidence, and a sensible next action.
```

## Quality Checklist

- [ ] Repository title is a clickable GitHub link.
- [ ] Every issue, alternative, and external claim has a direct source link.
- [ ] Community evidence contains attributable details rather than generic popularity language.
- [ ] Facts, inference, and unknowns are explicitly distinguished.
- [ ] The report states whether the project is suitable for the requested use case.

## Dependencies

Use the available browser, search, and web-fetching capabilities. Prefer official repository and documentation sources; use independent discussion only as supporting context.
