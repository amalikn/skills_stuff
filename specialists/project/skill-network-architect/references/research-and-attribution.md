---
Title: Research and sourcing review
Category: reference
Status: current
Authority: authored-guidance
Scope: Shared by skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: >-
  How the packs research, compare and cite external material: method, the copy rule, sources evaluated with corrected attribution, conventions verified,
  explicit negatives and a review checklist.
---

# Research and sourcing review

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Sources evaluated](#sources-evaluated)
- [Conventions verified](#conventions-verified)
- [Limits and explicit negatives](#limits-and-explicit-negatives)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Researching, comparing or citing external material for either pack, and any reuse of external text or code.
- The full 2026-10-29 survey lives in skill-network-architect at `docs/research/similar-skills-survey-20261029_1758.md`.
- Licence facts for tools live in [FOSS and tool selection](foss-and-tool-selection.md).

## Decision rules

Research method:
- Open the primary source: the standard, the vendor page, the upstream file. A listing or aggregator only locates it.
- Record URL, date read, version or commit, and an evidence label beside each claim.
- `main`, `master` and `latest` URLs move. Pin a commit or an archived copy before relying on exact text.
- Check the licence of the exact file, not only the repository root. Aggregators often mix licences per folder.
- Download counts, stars, marketplace grades and safety badges are not quality or security evidence.

Copy rule:
- The packs paraphrase. They bundle no external text, templates, diagrams or code today.
- Any verbatim copy, however short, needs a `THIRD_PARTY_NOTICES.md` at the pack root in the same change.
  - The notice keeps the upstream copyright line and licence text, and the file names the source, commit and change made.
  - An inline line sits beside the copied text: `Adapted from <repo>/<path> @ <commit>, <licence>, <holder>`.
- Apache-2.0 sources: state that the text was modified and carry any upstream NOTICE content.
- CC BY 4.0 sources (C4 model): credit author, link the licence, state the change.
- CC BY-SA 4.0 sources (arc42): adapted text carries the same licence if shared outside the organisation.
- CC BY-NC-ND 4.0 sources (Google SRE books): cite facts and link; never adapt the text.
- Unlicensed or proprietary pages (vendor docs, Azure and AWS guidance): link and paraphrase only.
- Hyperlinks and original summaries do not relicense upstream material.

## Sources evaluated

| Source              | What it offered                    | Licence                      | Decision                                  |
| ------------------- | ---------------------------------- | ---------------------------- | ----------------------------------------- |
| [wshobson agents][s-wsh] | network agent, triage, postmortem  | MIT                          | cross-check; incident shape paraphrased   |
| [Jeffallan skills][s-jeff] | load-when routing, chaos design    | MIT, no holder named         | routing and failure-injection paraphrased |
| [VoltAgent subagents][s-volt] | role checklists, handoffs          | MIT                          | handoff idea only; fixed targets rejected |
| [sickn33 skills][s-sick] | aggregated skills                  | per skill; one AGPL-3.0-only | not independent; see correction           |
| [C4 checklist][s-c4] | diagram review questions           | CC BY 4.0                    | paraphrased in diagrams reference         |
| [Batfish][s-bf], [SuzieQ][s-sq] | config-model and live-state checks | Apache-2.0                   | named validation step; tools only         |

[s-wsh]: https://github.com/wshobson/agents
[s-jeff]: https://github.com/Jeffallan/claude-skills
[s-volt]: https://github.com/VoltAgent/awesome-claude-code-subagents
[s-sick]: https://github.com/sickn33/antigravity-awesome-skills
[s-c4]: https://c4model.com/diagrams/checklist
[s-bf]: https://github.com/batfish/batfish
[s-sq]: https://github.com/netenglabs/suzieq

Correction to earlier ledgers (survey section 8, 2026-10-29):
- sickn33's network-engineer skill carries the same description as wshobson's network-engineer agent. It is a duplicate, not a second source.
- Its per-skill licences differ from the repository root; at least one skill is AGPL-3.0-only. The root MIT file does not cover every skill.
- Attribute any idea to the original repository (wshobson) and check the per-file licence before any reuse.
- `sources.json` entries SICK and SICK-L still imply an independent MIT source. They need the same correction (owner of sources.json).

Rejected content:
- Fixed universal targets ("99.99% uptime", "automation coverage over 90%") contradict the packs' rule. Targets come from user need.
- "A postmortem for every incident" conflicts with proportionality. The post-incident-review template uses agreed triggers instead.

## Conventions verified

| Convention                                                                        | Evidence                   | Label            |
| --------------------------------------------------------------------------------- | -------------------------- | ---------------- |
| Portable core is name and description front matter, optional licence and metadata | [Agent Skills specification](https://agentskills.io/specification) | VERIFIED_PRIMARY |
| Codex discovers `.agents/skills` at repository and user scope                     | [Codex documentation](https://learn.chatgpt.com/docs/build-skills) | VERIFIED_PRIMARY |
| Claude Code discovers `.claude/skills` at personal and project scope              | [Claude Code documentation](https://code.claude.com/docs/en/skills) | VERIFIED_PRIMARY |
| References one level deep from SKILL.md; third-person descriptions                | [Anthropic best practices][s-bp] | VERIFIED_PRIMARY |

[s-bp]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

- The packs use no provider-specific tool restrictions, model choice, hooks or orchestration.
- SKILL.md routes to AGENTS.md explicitly. An AGENTS.md inside a skill is not loaded automatically by every host.

## Limits and explicit negatives

- No inspected source covered the full network and systems pair without substantial new work.
- No live network, server, hypervisor, radio, controller or endpoint was contacted during research.
- No Codex or Claude discovery round trip, and no local-LLM run, was executed.
- Apple pages returned 429; Apple token, escrow and recovery details stay UNVERIFIED.
- Proxmox rendered docs returned 403; upstream source was read instead.
- Domain references were rechecked against primary sources on 2026-10-29. These are moving pages, not pinned copies.

## Review checklist

- [ ] Every load-bearing claim has a URL, date and evidence label beside it
- [ ] Primary source opened, not only an aggregator or listing
- [ ] Licence read on the exact file reused, not only the repository root
- [ ] No verbatim external text, or a notices file added in the same change
- [ ] Moving URLs pinned to a commit or archive when exact text matters
- [ ] Duplicated sources traced to their original and counted once

## Further reading

All links resolved 2026-10-29.

Finding and pinning sources:
- [IETF Datatracker](https://datatracker.ietf.org/): an RFC's status, errata and obsoleting documents before citing it.
- [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html): what upper-case MUST, SHOULD and MAY require.
- [Internet Archive Wayback Machine](https://web.archive.org/): a dated copy of a moving vendor page.
- [Software Heritage](https://www.softwareheritage.org/): an immutable snapshot of upstream source.

Licensing and attribution:
- [SPDX license list](https://spdx.org/licenses/): exact licence identifiers for the source ledger.
- GitHub, what an unlicensed public repository permits:
  - <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository>
- [REUSE](https://reuse.software/): per-file licence and copyright conventions.
- [OpenSSF Scorecard](https://scorecard.dev/): repeatable health signals when comparing upstream projects.
