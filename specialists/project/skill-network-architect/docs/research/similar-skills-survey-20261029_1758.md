---
Title: Survey of comparable network and systems architecture skills
Category: research-report
Status: current
Authority: research
Scope: skill-network-architect and skill-systems-architect; comparable published agent skills, subagents and architecture frameworks
Last reviewed: 2026-10-29
Summary: >-
  Survey of published skills, subagents and frameworks comparable to the two architect packs, with licences checked, a ranked list of concrete adoptions,
  copyable excerpts where the licence permits, triggering improvements and findings that contradict the packs.
---

# Survey of comparable network and systems architecture skills

## Contents

- [1. Scope and method](#1-scope-and-method)
- [2. What the packs already have](#2-what-the-packs-already-have)
- [3. Candidates reviewed](#3-candidates-reviewed)
- [4. Frameworks worth borrowing from](#4-frameworks-worth-borrowing-from)
- [5. Ranked adoptions](#5-ranked-adoptions)
- [6. Triggering and description improvements](#6-triggering-and-description-improvements)
- [7. Structural patterns that make an agent more effective](#7-structural-patterns-that-make-an-agent-more-effective)
- [8. Findings that contradict the packs](#8-findings-that-contradict-the-packs)
- [9. Attribution and licence rules for any copy](#9-attribution-and-licence-rules-for-any-copy)
- [10. Limits](#10-limits)

## 1. Scope and method

Research done 2026-10-29 by reading pages online (raw GitHub files, GitHub REST API for licence metadata, vendor documentation pages). Nothing was cloned or kept on disk. Licences were checked by
opening each repository's `LICENSE` file or the per-skill `LICENSE.txt`; where that was not possible the licence is marked UNVERIFIED and the source is treated as link-only. Evidence labels follow the
packs: VERIFIED_PRIMARY (the file or page itself was read), VERIFIED_SECONDARY, UNVERIFIED. All `main`-branch URLs are moving references; pin a commit before copying any text.

Search surface: the repositories named in the brief, GitHub code search for `"network architect" filename:SKILL.md` (about 7,000 hits, mostly unrelated; two network-architect skills were relevant),
the Anthropic and OpenAI skill catalogues, and the reliability frameworks listed in section 4.

## 2. What the packs already have

Read for this survey: both `SKILL.md`, both `RUNBOOK.md`, the `references/`, `templates/` and `scripts/` listings, `scripts/README.md`, `sources.json`, `evals/` and [research-and-attribution.md](../../references/research-and-attribution.md). In
short:

- A shared method ([architecture-method.md](../../references/architecture-method.md)): seven engagement modes with exit evidence, measurable requirements, evidence labels, options and ADRs, quantitative reasoning with units, validation tiers.
- Network references (17 modules) and systems references (19 modules), each ending in Further reading; shared modules are canonical in the network pack and symlinked into the systems pack.
- Templates: the network pack now has 15 (design, ADR, handoff, interface contract, change and validation, capacity model, current-state discovery, failure-mode analysis, IP plan, post-incident
  review, requirements, risk register, routing policy, site design, test and acceptance); the systems pack has 5. Other agents are editing these now; this report does not touch them.
- Offline helpers: `availability.py`, `ip_plan_check.py`, `link_budget.py`, `mtu_budget.py`, `capacity_check.py`, `check_package.py`.
- Behavioural evals: 10 network cases, a 16-point rubric, a staged protocol. Trigger checks exist only as prose in [evals/README.md](../../evals/README.md).
- A standing write-back contract with dated `Learned` entries and falsifiers. No other surveyed skill has anything comparable; keep it.

The packs are already deeper than every candidate below on evidence discipline, cross-domain handoff, physical/RF and on-premises scope. The gaps are in agent ergonomics: symptom-to-question
catalogues, concrete trigger tests, copyable per-mode checklists, worked numeric examples and a few missing method tools (DR strategy ladder, failure-injection plan, pre-change model validation).

## 3. Candidates reviewed

| #   | Source                                                            | Licence (checked)          | Covers                 | Genuinely good                        | Weak                         |
| --- | ----------------------------------------------------------------- | -------------------------- | ---------------------- | ------------------------------------- | ---------------------------- |
| C1  | [wonsukchoi/domain-experts network-architect](https://github.com/wonsukchoi/domain-experts/blob/main/roles/network-architect/SKILL.md) | MIT, [LICENSE](https://github.com/wonsukchoi/domain-experts/blob/main/LICENSE) "Copyright | Redundancy, busy-hour  | First-principles core, mental-model   | Narrow (five principles); no |
|     |                                                                   |   (c) 2026 Wonsuk Choi and |   capacity,            |   defaults, decision framework,       |   evidence labels; draft     |
|     |                                                                   |   Domain                   |   segmentation,        |   common failure modes, a numeric     |   maturity; quotes "commonly |
|     |                                                                   |   Experts contributors"    |   real-time QoS,       |   worked example, and a [red-flags.md](https://github.com/wonsukchoi/domain-experts/blob/main/roles/network-architect/references/red-flags.md) |   cited" voice thresholds    |
|     |                                                                   |                            |   routing choice       |   catalogue in "Usually means / First |   without a source           |
|     |                                                                   |                            |                        |   question / Data to pull" form       |                              |
| C2  | [domain-experts devops-sre](https://github.com/wonsukchoi/domain-experts/blob/main/roles/devops-sre/SKILL.md) and [computer-systems-engineer-architect](https://github.com/wonsukchoi/domain-experts/blob/main/roles/computer-systems-engineer-architect/SKILL.md) | MIT (same repo)            | SRE judgement;         | Common failure modes (chasing 100%    | Generic to software; no      |
|     |                                                                   |                            |   whole-system         |   uptime, alert fatigue, toil creep,  |   on-premises or             |
|     |                                                                   |                            |   decomposition,       |   drift, big-bang deploys);           |   endpoint depth             |
|     |                                                                   |                            |   interface control    |   error-budget worked example with    |                              |
|     |                                                                   |                            |   documents, build     |   the arithmetic shown                |                              |
|     |                                                                   |                            |   vs buy               |                                       |                              |
| C3  | [wshobson/agents connectivity-triage](https://github.com/wshobson/agents/blob/main/plugins/incident-response/skills/connectivity-triage/SKILL.md) | MIT, [LICENSE](https://github.com/wshobson/agents/blob/main/LICENSE) "Copyright | Read-only macOS        | Best diagnostic contract found:       | macOS-only commands;         |
|     |                                                                   |   (c) 2024 Seth Hobson"    |   connectivity         |   symptom-to-fault-domain flow,       |   endpoint view only         |
|     |                                                                   |                            |   fault isolation      |   Observed / Inferred / Unknown       |                              |
|     |                                                                   |                            |                        |   labels, a list of what each probe   |                              |
|     |                                                                   |                            |                        |   does not prove, exactly one         |                              |
|     |                                                                   |                            |                        |   fault-domain category with          |                              |
|     |                                                                   |                            |                        |   confidence, one "next safest        |                              |
|     |                                                                   |                            |                        |   check", explicit no-change          |                              |
|     |                                                                   |                            |                        |   safety list                         |                              |
| C4  | [wshobson network-engineer](https://github.com/wshobson/agents/blob/main/plugins/cloud-infrastructure/agents/network-engineer.md), | MIT (same repo)            | Cloud networking, load | Breadth checklist; "Response          | Capability lists, not        |
|     |   [cloud-architect](https://github.com/wshobson/agents/blob/main/plugins/cloud-infrastructure/agents/cloud-architect.md), [hybrid-cloud-architect](https://github.com/wshobson/agents/blob/main/plugins/cloud-infrastructure/agents/hybrid-cloud-architect.md) |                            |   balancing, DNS, TLS, |   Approach" numbered steps; example   |   method; cloud-first; no    |
|     |                                                                   |                            |   mesh,                |   interactions useful as              |   evidence or failure-domain |
|     |                                                                   |                            |   hybrid placement     |   trigger seeds                       |   discipline; "Use           |
|     |                                                                   |                            |                        |                                       |   PROACTIVELY" trigger       |
|     |                                                                   |                            |                        |                                       |   is broad                   |
| C5  | [wshobson postmortem-writing](https://github.com/wshobson/agents/blob/main/plugins/incident-response/skills/postmortem-writing/SKILL.md) and [slo-implementation](https://github.com/wshobson/agents/blob/main/plugins/observability-monitoring/skills/slo-implementation/SKILL.md) | MIT (same repo)            | Blameless review, 5    | Blame-focused vs blameless table;     | 5 Whys converges on a single |
|     |                                                                   |                            |   Whys,                |   postmortem trigger list; SLI        |   root cause; SLO example    |
|     |                                                                   |                            |   SLI/SLO/error budget |   type examples                       |   targets are illustrative,  |
|     |                                                                   |                            |                        |                                       |   not derived                |
| C6  | [Jeffallan/claude-skills sre-engineer](https://github.com/Jeffallan/claude-skills/blob/main/skills/sre-engineer/SKILL.md), | MIT, [LICENSE](https://github.com/Jeffallan/claude-skills/blob/main/LICENSE) "Copyright | SRE, architecture      | "Reference Guide" table with a "Load  | NFR checklist maps           |
|     |   [architecture-designer](https://github.com/Jeffallan/claude-skills/blob/main/skills/architecture-designer/SKILL.md), [chaos-engineer](https://github.com/Jeffallan/claude-skills/blob/main/skills/chaos-engineer/SKILL.md) |   (c) 2025" (no            |   decisions,           |   When" column; MUST DO / MUST NOT DO |   availability tiers to use  |
|     |                                                                   |   holder named)            |   failure injection    |   blocks; `metadata.triggers`; a      |   cases ("99.99% Financial   |
|     |                                                                   |                            |                        |   [chaos experiment template](https://github.com/Jeffallan/claude-skills/blob/main/skills/chaos-engineer/references/experiment-design.md) with |   systems"); "write          |
|     |                                                                   |                            |                        |   hypothesis, steady state, blast     |   postmortems for all        |
|     |                                                                   |                            |                        |   radius, abort triggers and success  |   incidents";                |
|     |                                                                   |                            |                        |   criteria; an [NFR checklist](https://github.com/Jeffallan/claude-skills/blob/main/skills/architecture-designer/references/nfr-checklist.md) phrased |   cloud-provider focus       |
|     |                                                                   |                            |                        |   as questions                        |                              |
| C7  | [VoltAgent awesome-claude-code-subagents, 03-infrastructure](https://github.com/VoltAgent/awesome-claude-code-subagents/tree/main/categories/03-infrastructure) | MIT, [LICENSE](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/LICENSE) "Copyright | Broad infra roles      | Phased workflow (analysis,            | Checklists are fixed numeric |
|     |   (network-engineer, cloud-architect, sre-engineer,               |   (c) 2025 VoltAgent"      |                        |   implementation, excellence);        |   goals ("Network uptime     |
|     |   platform-engineer, kubernetes-specialist, windows-infra-admin)  |                            |                        |   windows-infra-admin "safe change    |   99.99% achieved", "Latency |
|     |                                                                   |                            |                        |   engineering" framing                |   < 50ms", "Automation       |
|     |                                                                   |                            |                        |                                       |   coverage > 90%", "Cost     |
|     |                                                                   |                            |                        |                                       |   optimization > 30%         |
|     |                                                                   |                            |                        |                                       |   realized"); "query context |
|     |                                                                   |                            |                        |                                       |   manager" JSON assumes a    |
|     |                                                                   |                            |                        |                                       |   harness that does not      |
|     |                                                                   |                            |                        |                                       |   exist here                 |
| C8  | [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) (network-engineer, | Repo MIT ([LICENSE](https://github.com/sickn33/antigravity-awesome-skills/blob/main/LICENSE), | Aggregator of other    | [disaster-recovery](https://github.com/sickn33/antigravity-awesome-skills/blob/main/skills/disaster-recovery/SKILL.md) defines RTO from | [network-engineer](https://github.com/sickn33/antigravity-awesome-skills/blob/main/skills/network-engineer/SKILL.md) carries the |
|     |   disaster-recovery, c4-*, hybrid-cloud-networking,               |   "Copyright (c) 2026      |   repos' skills        |   disruption to verified recovery and |   same description as the    |
|     |   slo-implementation, postmortem-writing and others)              |   Antigravity User");      |                        |   warns replicas may be stale or      |   wshobson agent (C4) plus   |
|     |                                                                   |   per-skill licences       |                        |   corrupted; good provenance fields   |   generic "use when"         |
|     |                                                                   |   differ, e.g.             |                        |   (`source_repo`, `license_source`)   |   boilerplate; licence per   |
|     |                                                                   |   [architecture-review](https://github.com/sickn33/antigravity-awesome-skills/blob/main/skills/architecture-review/SKILL.md) |                        |   on newer imports                    |   file must be checked       |
|     |                                                                   |   is AGPL-3.0-only         |                        |                                       |                              |
| C9  | [anthropics/skills skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) | Apache-2.0, [LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/skill-creator/LICENSE.txt) | How to build and tune  | Description optimisation: 20          | Tooling (`run_loop.py`)      |
|     |                                                                   |                            |   a skill              |   realistic trigger queries, 8-10     |   needs `claude -p`; not     |
|     |                                                                   |                            |                        |   should-trigger and 8-10 should-not, |   domain content             |
|     |                                                                   |                            |                        |   the negatives being near-misses     |                              |
|     |                                                                   |                            |                        |   that share keywords; note that      |                              |
|     |                                                                   |                            |                        |   models tend to undertrigger, so     |                              |
|     |                                                                   |                            |                        |   descriptions should be "a little    |                              |
|     |                                                                   |                            |                        |   bit pushy"                          |                              |
| C10 | [Anthropic skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Documentation (link only)  | Skill structure        | Descriptions in third person stating  | General guidance only        |
|     |                                                                   |                            |                        |   what and when; references one level |                              |
|     |                                                                   |                            |                        |   deep from SKILL.md; copyable        |                              |
|     |                                                                   |                            |                        |   progress checklists; degrees of     |                              |
|     |                                                                   |                            |                        |   freedom matched to fragility; build |                              |
|     |                                                                   |                            |                        |   evaluations first; SKILL.md under   |                              |
|     |                                                                   |                            |                        |   500 lines                           |                              |
| C11 | [openai/skills security-threat-model](https://github.com/openai/skills/blob/main/skills/.curated/security-threat-model/SKILL.md) | Apache-2.0, [LICENSE.txt](https://github.com/openai/skills/blob/main/skills/.curated/security-threat-model/LICENSE.txt) | Evidence-grounded      | Trust boundaries as concrete edges    | Scoped to source             |
|     |                                                                   |                            |   threat modelling     |   with protocol, auth, encryption,    |   repositories, not          |
|     |                                                                   |                            |                        |   validation and rate limiting;       |   running networks           |
|     |                                                                   |                            |                        |   attacker capabilities and explicit  |                              |
|     |                                                                   |                            |                        |   non-capabilities; 1-3 targeted      |                              |
|     |                                                                   |                            |                        |   questions and a pause before the    |                              |
|     |                                                                   |                            |                        |   final report; a pre-final quality   |                              |
|     |                                                                   |                            |                        |   check list                          |                              |
| C12 | [rloisell/rl-agents-n-skills network-architect](https://github.com/rloisell/rl-agents-n-skills/blob/main/network-architect/SKILL.md) | None declared (GitHub API  | Cisco                  | Vendor-concrete tables                | Cheat-sheet, not method;     |
|     |                                                                   |   reports no licence): all |   CCNP-depth reference |                                       |   recommends /30 for         |
|     |                                                                   |   rights reserved, do      |                        |                                       |   point-to-point links       |
|     |                                                                   |   not copy                 |                        |                                       |                              |
| C13 | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | None declared              | Curated list           | Nothing network or                    | Not a source of content      |
|     |                                                                   |                            |                        |   infrastructure specific             |                              |

The earlier comparison in [research-and-attribution.md](../../references/research-and-attribution.md) covered C4, C6, C7 and C8 at topic level. C1-C3, C5, C9-C11 are new.

## 4. Frameworks worth borrowing from

| Framework                                          | Licence for reuse                                      | What to borrow                              | Where                                    |
| -------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------- | ---------------------------------------- |
| [Azure Well-Architected reliability checklist](https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist) | UNVERIFIED: the page's source repo                     | A ten-item review checklist (simplicity,    | Review-mode checklist in                 |
|   RE:01-RE:10 and [failure mode analysis](https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis) |   (`MicrosoftDocs/well-architected-pr`) is not public; |   flow criticality, FMA, targets,           |   architecture-method.md; FMA template   |
|                                                    |   MicrosoftDocs/azure-docs is CC-BY-4.0 but that does  |   redundancy, scaling, self-healing,        |                                          |
|                                                    |   not prove this page is. Paraphrase only              |   resilience testing, DR, health            |                                          |
|                                                    |                                                        |   measurement); FMA vocabulary (blast       |                                          |
|                                                    |                                                        |   radius, failure mode,                     |                                          |
|                                                    |                                                        |   mitigation, detection)                    |                                          |
| [AWS Reliability pillar design principles](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/design-principles.html) | AWS site terms; link and paraphrase only               | KPIs measured in business value; test       | systems `backup-disaster-recovery.md`    |
|   and [DR options](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html) |                                                        |   recovery procedures; four DR strategies   |                                          |
|                                                    |                                                        |   (backup and restore, pilot light, warm    |                                          |
|                                                    |                                                        |   standby, multi-site active/active)        |                                          |
|                                                    |                                                        |   ordered by cost and RTO/RPO               |                                          |
| [Google SRE workbook](https://sre.google/workbook/implementing-slos/), | CC BY-NC-ND 4.0 (stated on the page): no derivatives,  | Error budget policy as a pre-agreed         | Already cited in                         |
|   [error budget policy](https://sre.google/workbook/error-budget-policy/), [SRE book ch. 32 PRR](https://sre.google/sre-book/evolving-sre-engagement-model/) |   link and cite facts only                             |   decision rule; production readiness       |   observability-troubleshooting.md for   |
|                                                    |                                                        |   review as an engagement gate              |   burn rates; add PRR as a review mode   |
| [C4 model review checklist](https://c4model.com/diagrams/checklist) | CC BY 4.0 (stated on [c4model.com](https://c4model.com/)) | Diagram review questions: title, type,      | diagrams-and-deliverables.md             |
|                                                    |                                                        |   scope, legend; every element named and    |                                          |
|                                                    |                                                        |   typed; every arrow labelled with intent   |                                          |
|                                                    |                                                        |   and technology; every colour, shape and   |                                          |
|                                                    |                                                        |   line style explained                      |                                          |
| [arc42](https://arc42.org/license)                 | CC BY-SA 4.0                                           | Already used as the base of                 | Keep the existing attribution line       |
|                                                    |                                                        |   templates/design.md; share-alike applies  |                                          |
|                                                    |                                                        |   to any adapted template that              |                                          |
|                                                    |                                                        |   is distributed                            |                                          |
| [NIST SP 800-160 Vol. 2 Rev. 1](https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final) | US Government work                                     | Cyber-resiliency goals: anticipate,         | security-and-segmentation.md,            |
|                                                    |                                                        |   withstand, recover from, adapt            |   capacity-and-resilience.md             |
| [MADR](https://github.com/adr/madr)                | MIT OR CC0-1.0 ([LICENSE](https://github.com/adr/madr/blob/main/LICENSE)) | "Considered options", "Decision drivers",   | templates/decision-record.md (owned by   |
|                                                    |                                                        |   "Confirmation" sections                   |   the template editors)                  |
| [Batfish](https://github.com/batfish/batfish) and [SuzieQ](https://github.com/netenglabs/suzieq) | Apache-2.0 (GitHub API)                                | Pre-change configuration model analysis;    | foss-and-tool-selection.md,              |
|                                                    |                                                        |   multi-vendor state collection             |   automation-and-safety.md               |
|                                                    |                                                        |   and assertions                            |                                          |

Cisco Validated Designs and Juniper design guides are proprietary vendor documents: cite them for platform facts, never copy. No public, licensable summary of Cisco PPDIOO or Oppenheimer's top-down
method was found that adds anything beyond the existing method module; not recommended.

## 5. Ranked adoptions

Ranked by expected gain in agent behaviour per unit of effort. "Excerpt" means short verbatim text that may be copied with the attribution given in section 9.

### A1. Red-flag catalogue per domain (both packs)

- **Change:** add `references/red-flags.md` to each pack (network: redundancy, capacity, segmentation, routing, Wi-Fi/RF, DNS/DHCP/time, automation; systems: cluster quorum, storage, backup, identity,
  patching, capacity), each entry in the form *Signal / Usually means / First question / Data to pull / Owning reference*. Route it from SKILL.md for review and incident modes.
- **Why it beats what we have:** the packs state rules but give an agent no symptom-to-question index. A review agent scanning a design needs "what does this smell mean and what do I ask next"; the
  format forces a question and a data pull rather than an opinion.
- **Source:** [domain-experts red-flags.md](https://github.com/wonsukchoi/domain-experts/blob/main/roles/network-architect/references/red-flags.md), MIT. Excerpt:

  > ### Two "redundant" links or devices haven't been traced through their full physical path
  > - **Usually means:** A shared conduit, entry point, switch, or power source could create a hidden single point of failure despite apparent redundancy at the layer being reviewed.
  > - **First question:** Has the complete physical path (conduit, cabling, entry point, power) for each redundant path been traced and confirmed independent?
  > - **Data to pull:** Physical infrastructure diagrams, conduit/entry point documentation for each path.

### A2. Concrete trigger eval set with near-misses (both packs)

- **Change:** add `evals/trigger-cases.json` (20 per pack: 8-10 should-trigger, 8-10 near-miss should-not) and a recipe to review it; replace the prose "Trigger checks" in [evals/README.md](../../evals/README.md) with a
  pointer. Near-misses to include: "what firmware is on the Cambium AP at site X" (skill-cambium), "why is the ansible-wifi report missing a site" (skill-smc), "move this box left in the drawio"
  (skill-drawio), "add a custom field in Nautobot" (skill-nautobot), "size the Proxmox cluster" (systems, not network), "VLAN for the new storage network" (both, collaboration).
- **Why:** the only trigger guidance now is prose; nothing tests the boundary with the five platform packs and the peer, which is where misrouting will happen.
- **Source:** [anthropics/skills skill-creator, "Description Optimization"](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), Apache-2.0. Excerpt:

  > For the **should-not-trigger** queries (8-10), the most valuable ones are the near-misses — queries that share keywords or concepts with the skill but actually need something different.

### A3. Fault-domain diagnostic contract (network observability-troubleshooting.md; systems observability-and-incident.md)

- **Change:** add an "Incident result format" to the incident mode: Symptom; Observations (each Observed, Inferred or Unknown); exactly one primary fault domain with low/medium/high confidence; one
  Next safest check. Add a "what a probe does not prove" list. Fault domains for network: local link/LAN, L2 domain, addressing/DHCP, DNS, routing/path, policy (firewall/NAT), RF/radio, remote
  service, inconclusive.
- **Why:** [observability-troubleshooting.md](../../references/observability-troubleshooting.md) already diagnoses by competing hypotheses but has no fixed return shape; a fixed shape is what makes an agent stop early and hand over cleanly, and maps
  onto the packs' evidence labels.
- **Source:** [wshobson connectivity-triage](https://github.com/wshobson/agents/blob/main/plugins/incident-response/skills/connectivity-triage/SKILL.md), MIT. Excerpt:

  > Never treat one probe as proof of root cause. In particular:
  > - failed `ping` can reflect ICMP filtering rather than an outage;
  > - successful `ping` does not prove an application is healthy;
  > - non-responsive traceroute hops do not prove packet loss at those routers;
  > - successful DNS resolution does not prove reachability;
  > - high HTTP first-byte time can be dominated by remote application processing.
  >
  > When observations conflict, prefer `inconclusive` over a confident guess.

### A4. Rewrite both descriptions: third person, what plus when, near-miss exclusions

- **Change:** both SKILL.md `description` fields (see section 6 for proposed text).
- **Why:** the current descriptions start "Use when" and list domains; they do not say what the skill produces, and the trigger vocabulary misses common user words (VLAN, subnet, BGP, firewall rule,
  failover, "redundant ISP", Wi-Fi coverage, ZFS pool, backup restore, Proxmox HA).
- **Source:** [Anthropic best practices, "Writing effective descriptions"](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (link only) and [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) (Apache-2.0) on undertriggering.

### A5. Route every reference directly from SKILL.md with a "Load when" column

- **Change:** move the RUNBOOK.md reference routing table (or a compact copy of it) into SKILL.md as a three-column table *Topic / Reference / Load when*, so each reference is one link from SKILL.md.
  Keep RUNBOOK.md for templates and recipes.
- **Why:** Anthropic advises keeping references one level deep from SKILL.md, because nested references may be only partly read. Today an agent must read SKILL.md, then RUNBOOK.md, then the reference.
  Jeffallan's "Load When" column turns the table into a trigger for the agent rather than an index.
- **Source:** [Anthropic best practices, "Keep references one level deep"](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); pattern from [Jeffallan sre-engineer "Reference Guide"](https://github.com/Jeffallan/claude-skills/blob/main/skills/sre-engineer/SKILL.md), MIT.

### A6. Copyable per-mode checklists (architecture-method.md, shared)

- **Change:** under each engagement mode add a short `- [ ]` checklist the agent copies into its reply and ticks (for example Brownfield review: scope and owner stated; current state labelled; red
  flags scanned; each finding tied to an observation; ranked by service impact; peer or specialist review requested where an interface is shared; next measurements named).
- **Why:** the mode table gives exit evidence but no step tracking; on long reviews agents skip steps. A checklist in the reply is also an audit trail for the evals.
- **Source:** [Anthropic best practices, "Use workflows for complex tasks"](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (link only). Content: own wording.

### A7. Common failure modes plus a numeric worked example per domain reference

- **Change:** add a "Common failure modes" list and one worked example with arithmetic to capacity-and-resilience.md (busy hour vs 24-hour average; real-time reservation), to systems
  capacity-and-performance.md (N+1 memory after host loss) and observability (error budget left after a burn). Add matching eval cases N11-N13 with arithmetic oracles.
- **Why:** the references are rule-dense but example-light; worked examples are what anchor an agent's arithmetic and give the evals an oracle.
- **Source:** [domain-experts network-architect](https://github.com/wonsukchoi/domain-experts/blob/main/roles/network-architect/SKILL.md) and [devops-sre](https://github.com/wonsukchoi/domain-experts/blob/main/roles/devops-sre/SKILL.md), MIT. Excerpt (network-architect, Common failure modes):

  > - Sizing link capacity based on 24-hour average utilization, missing that busy-hour utilization is already near saturation.
  > - Segmenting a network around organizational department names rather than actual trust boundaries and traffic isolation needs.

Do not copy the example's "commonly cited around 150ms one-way latency, 30ms jitter" without a primary source (ITU-T G.114 for delay); the upstream gives none.

### A8. DR strategy ladder (systems backup-disaster-recovery.md)

- **Change:** add a decision table: backup and restore, pilot light, warm standby, active/active, each with what is running at the recovery site, typical RTO/RPO class, cost drivers, what has to be
  tested, and the correlated failure each does not cover. Keep it vendor-neutral (Proxmox/ZFS replication, PBS, cold spare hardware are implementations).
- **Why:** the module has RPO/RTO rules and restore testing but no strategy vocabulary; an agent asked "what DR do we need" has nothing to compare options against.
- **Source:** [AWS DR options whitepaper](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html) (paraphrase, link only). Also adopt the RTO definition wording idea from [sickn33 disaster-recovery](https://github.com/sickn33/antigravity-awesome-skills/blob/main/skills/disaster-recovery/SKILL.md) ("From the agreed service disruption point to verified
  recovery; record detection/declaration separately"), which it marks as adapted from [BagelHole/DevOps-Security-Agent-Skills](https://github.com/BagelHole/DevOps-Security-Agent-Skills) (MIT as stated; that upstream licence was not opened, so paraphrase).

### A9. Failure-injection test plan section (test-and-acceptance-plan template, after the current edit lands)

- **Change:** a section with Hypothesis (given / when / then / measured by), Steady state metrics, Blast radius (environment, share of traffic or hosts, duration), Abort triggers and the maximum
  rollback time, Success criteria, Who may stop it.
- **Why:** the packs say "a redundant drawing is not resilience" but give no form for proving failover; this is the form.
- **Source:** [Jeffallan chaos-engineer experiment-design.md](https://github.com/Jeffallan/claude-skills/blob/main/skills/chaos-engineer/references/experiment-design.md), MIT; concept also in Azure RE:08 (link only). Excerpt (structure keys):

  > `hypothesis`, `steady_state`, `blast_radius` (`environment`, `traffic_percentage`, `duration_seconds`, `max_error_rate`, `auto_rollback`), `safety` (`rollback_triggers`,
  > `rollback_time_limit_seconds`), `success_criteria`

### A10. Pre-change network model validation tier (automation-and-safety.md, foss-and-tool-selection.md)

- **Change:** name configuration-model analysis as its own validation tier between static lint and lab: Batfish for reachability, ACL/firewall and routing-policy questions against candidate configs;
  SuzieQ for collected-state assertions before and after a change; containerlab (already listed, BSD-3-Clause) for lab.
- **Why:** the method separates static, lab, canary and production evidence, but the network pack names no FOSS tool for the "will this config do what we think" tier.
- **Source:** [batfish/batfish](https://github.com/batfish/batfish) and [netenglabs/suzieq](https://github.com/netenglabs/suzieq), both Apache-2.0. Verify current versions before writing commands.

### A11. Diagram review checklist (diagrams-and-deliverables.md, shared)

- **Change:** add a pre-handover diagram checklist; extend it with network items (every link labelled with medium, speed and VLAN/VRF; trust zones bounded; failure domains shaded; current vs target
  never mixed on one view).
- **Why:** the module guides what to draw but not how to check a drawing; skill-drawio renders, it does not judge architecture content.
- **Source:** [C4 model review checklist](https://c4model.com/diagrams/checklist), CC BY 4.0. Excerpt:

  > Does every arrow have a label describing the intent of that relationship? Does the description match the relationship direction? Where applicable, do you understand the technology choices
  > associated with every relationship? (e.g. protocols for inter-process communication)

### A12. Trust-boundary threat pass (security-and-segmentation.md; systems security-and-service-identity.md)

- **Change:** add a short procedure: list trust boundaries as concrete edges with protocol, authentication, encryption and filtering; list assets; state attacker capabilities and explicit
  non-capabilities; rank abuse paths by likelihood x impact adjusted for existing controls; ask 1-3 targeted questions before finalising; run a coverage check (every boundary has a threat or an
  explicit "none").
- **Why:** segmentation is currently argued from zones; there is no step that walks each boundary and no guard against inflated severity.
- **Source:** [openai/skills security-threat-model](https://github.com/openai/skills/blob/main/skills/.curated/security-threat-model/SKILL.md), Apache-2.0. Excerpt:

  > Enumerate trust boundaries as concrete edges between components, noting protocol, auth, encryption, validation, and rate limiting.
  >
  > Explicitly note non-capabilities to avoid inflated severity.

### Further adoptions (lower rank)

| #   | Change                                                                                            | File                                                    | Source                           |
| --- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | -------------------------------- |
| A13 | Reliability review checklist (ten items paraphrased from Azure RE:01-RE:10) as the Brownfield     | architecture-method.md                                  | [Azure WAF checklist](https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist), paraphrase |
|     |   review default for a service                                                                    |                                                         |                                  |
| A14 | Production readiness review as an eighth engagement mode (gate before a service is handed         | architecture-method.md                                  | [SRE book ch. 32](https://sre.google/sre-book/evolving-sre-engagement-model/), link only |
|     |   to operations)                                                                                  |                                                         |                                  |
| A15 | Error budget policy as a pre-agreed decision (what freezes, who decides, what resets)             | systems observability-and-incident.md                   | [SRE workbook appendix B](https://sre.google/workbook/error-budget-policy/), |
|     |                                                                                                   |                                                         |   link only                      |
| A16 | MUST / MUST NOT block in SKILL.md replacing the prose "Common Errors" paragraph                   | both SKILL.md                                           | Pattern from [Jeffallan](https://github.com/Jeffallan/claude-skills/blob/main/skills/architecture-designer/SKILL.md), MIT |
| A17 | Blame-focused vs blameless table and postmortem trigger list                                      | templates/post-incident-review.md (after current edit)  | [wshobson postmortem-writing](https://github.com/wshobson/agents/blob/main/plugins/incident-response/skills/postmortem-writing/SKILL.md), MIT |
| A18 | Cyber-resiliency goals (anticipate, withstand, recover, adapt) as the resilience                  | security-and-segmentation.md,                           | [NIST SP 800-160 v2 r1](https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final) |
|     |   objective vocabulary                                                                            |   capacity-and-resilience.md                            |                                  |
| A19 | "Considered options / Decision drivers / Confirmation" sections                                   | templates/decision-record.md (after current edit)       | [MADR](https://github.com/adr/madr), MIT OR CC0-1.0 |
| A20 | NFR question bank phrased as questions, without the use-case-to-availability column               | templates/requirements-and-constraints.md (after        | [Jeffallan nfr-checklist](https://github.com/Jeffallan/claude-skills/blob/main/skills/architecture-designer/references/nfr-checklist.md), MIT |
|     |                                                                                                   |   current edit)                                         |                                  |

## 6. Triggering and description improvements

The [Agent Skills specification](https://agentskills.io/specification) caps `description` at 1024 characters; both current descriptions are well under it. Proposed network description (about 700 characters):

```text
Designs, reviews and troubleshoots network architecture and produces decision-ready outputs: target designs, IP and VLAN/VRF plans, routing and segmentation
policy, failure-domain and capacity models, migration and cutover plans, and validation tests. Use for campus, datacenter, WAN/SD-WAN, VPN, Wi-Fi and
radio links, IPv4/IPv6 addressing, BGP/OSPF, firewalls and trust zones, DNS/DHCP/NTP, redundant ISPs and failover, MTU and link budgets, or any
connectivity problem that spans devices or layers, even when the user does not say "architecture". Not for one device's commands or firmware
(skill-smc, skill-cambium, skill-mikrotik), diagram layout (skill-drawio) or code (skill-coder); collaborates with skill-systems-architect on hosts,
storage and recovery.
```

Proposed systems description, same shape: lead with outputs (sizing and failure-scenario models, cluster and storage designs, backup/DR plans with RPO/RTO and restore tests, OS/identity/endpoint
standards, migration waves), then user vocabulary (Proxmox, HA, quorum, ZFS, Ceph, NAS, VM, container, Kubernetes, Linux, Windows/AD, macOS/MDM, patching, backup, restore, disaster recovery,
capacity), then the not-for line and the peer.

Other triggering changes:

- Add the A2 trigger set and run it whenever a description changes; record results in evals/results.md separately from behavioural cases.
- Keep the Not-for line in the description, not only in the body: the description is the only text the host reads before choosing.
- Do not add `metadata.triggers` keyword lists for discovery (Jeffallan does): no host surveyed reads them; put the words in the description.

## 7. Structural patterns that make an agent more effective

| Pattern                                                                | Seen in    | Status in our packs                               | Recommendation                            |
| ---------------------------------------------------------------------- | ---------- | ------------------------------------------------- | ----------------------------------------- |
| Red-flag catalogue (signal, meaning, first question, data)             | C1         | Absent                                            | Adopt (A1)                                |
| Fixed diagnostic return shape with one fault domain and one next check | C3         | Partial (hypotheses, no shape)                    | Adopt (A3)                                |
| Trigger eval set with near-misses                                      | C9         | Prose only                                        | Adopt (A2)                                |
| Copyable per-mode progress checklist                                   | C10        | Mode table only                                   | Adopt (A6)                                |
| References one hop from SKILL.md with "Load when"                      | C6, C10    | Two hops via RUNBOOK.md                           | Adopt (A5)                                |
| Worked numeric example per domain                                      | C1, C2, C6 | Few                                               | Adopt (A7)                                |
| MUST / MUST NOT block                                                  | C6         | Prose "Common Errors"                             | Adopt (A16)                               |
| Explicit non-capabilities / severity calibration                       | C11        | Absent                                            | Adopt in security (A12)                   |
| Pause for 1-3 questions before final output                            | C11        | "Ask only questions that can change the decision" | Already equivalent; add the 1-3 cap       |
| Scoring rubric                                                         | ours       | 16-point rubric                                   | Ours is stronger than any candidate; keep |
| Fixed numeric checklists (uptime, latency, coverage)                   | C7         | Rejected by design                                | Do not adopt (section 8)                  |
| "Query context manager" JSON protocol                                  | C7         | Neutral handoff template                          | Keep ours; theirs assumes a harness       |
| Standing write-back with falsifiers                                    | ours only  | Present                                           | Keep; no candidate has it                 |

## 8. Findings that contradict the packs

1. **Fixed universal targets.** VoltAgent's checklists ("Network uptime 99.99% achieved", "Latency < 50ms regional maintained", "Automation coverage > 90%", "Cost optimization > 30% realized";
   [network-engineer](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/03-infrastructure/network-engineer.md), [cloud-architect](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/03-infrastructure/cloud-architect.md)) and Jeffallan's NFR table mapping "99.99%" to "Financial systems" contradict the packs' rule against universal percentages. The packs are right: the [SRE workbook](https://sre.google/workbook/implementing-slos/)
   derives SLOs from user need. Do not import these numbers.
2. **Reference depth.** [Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) say to keep references one level deep from SKILL.md; both packs route most references SKILL.md, then RUNBOOK.md, then reference (A5).
3. **Description voice.** The same guidance asks for third person stating what the skill does and when; ours state only when ("Use when ..."). Not wrong, but weaker for selection (A4).
4. **Source attribution in our ledger.** [sickn33 network-engineer](https://github.com/sickn33/antigravity-awesome-skills/blob/main/skills/network-engineer/SKILL.md) has the same description as [wshobson network-engineer](https://github.com/wshobson/agents/blob/main/plugins/cloud-infrastructure/agents/network-engineer.md) and is not an independent source. `sources.json` (SICK, SICK-L) and
   research-and-attribution.md treat it as one, and SICK-L implies the repo MIT licence covers it; the aggregator's per-skill licences differ (one is AGPL-3.0-only). Attribute any reuse to the
   original repo and check the per-file licence.
5. **Reuse policy.** [research-and-attribution.md](../../references/research-and-attribution.md) says the pack "bundles no external text or code". Adopting any excerpt above changes that; the licence section and a third-party notices file must be
   updated in the same change (section 9).
6. **Jeffallan licence holder.** The [LICENSE](https://github.com/Jeffallan/claude-skills/blob/main/LICENSE) reads "Copyright (c) 2025" with no holder; `sources.json` JEFF-L says only MIT. Attribute as "Jeffallan/claude-skills (https://github.com/Jeffallan), MIT".
7. **Point-to-point prefix.** rloisell's network-architect recommends /30 for point-to-point links; the packs follow [RFC 3021](https://www.rfc-editor.org/rfc/rfc3021) /31. No change; the source is unlicensed anyway.
8. **"Postmortems for all incidents"** (Jeffallan, VoltAgent) conflicts with the packs' proportionality rule; wshobson's trigger list (SEV1/2, data loss, near-misses, novel failure modes) is closer to
   ours.

No candidate contradicted a technical rule in the packs' references (burn-rate figures, availability arithmetic, RFC citations). The error-budget figure 99.9% over 30 days = 43.2 minutes appears
identically in [Jeffallan sre-engineer](https://github.com/Jeffallan/claude-skills/blob/main/skills/sre-engineer/SKILL.md) and our observability-troubleshooting.md.

## 9. Attribution and licence rules for any copy

- **MIT (C1-C8):** a short excerpt is safest treated as a "substantial portion": keep the upstream copyright line and the MIT permission notice in a `THIRD_PARTY_NOTICES.md` at the pack root, and put
  an inline line beside the excerpt: `Adapted from <repo>/<path> @ <commit>, MIT, Copyright (c) <year> <holder>`.
- **Apache-2.0 (C9, C11, Batfish, SuzieQ):** keep the licence text reference, state the change ("modified"), and include any upstream NOTICE file content if one exists (none was checked).
- **CC BY 4.0 (C4 model):** credit "C4 model, Simon Brown, https://c4model.com/, CC BY 4.0", link the licence, state changes.
- **CC BY-SA 4.0 (arc42):** adapted templates carry the same licence if distributed outside the organisation.
- **CC BY-NC-ND 4.0 (Google SRE books):** no adapted text; cite facts and link.
- **Unverified or proprietary (Azure WAF, AWS, Cisco, Juniper, rloisell, travisvn):** link and paraphrase only.
- Pin a commit SHA in `sources.json` for every copied excerpt; this survey read `main`.

## 10. Limits

- Online reading only; no candidate skill was executed, and no A/B trigger test was run against either host.
- Per-skill NOTICE files for Apache-2.0 sources were not checked. BagelHole/DevOps-Security-Agent-Skills licence was taken from sickn33's metadata, not opened.
- The Azure Well-Architected source repository is not public, so its content licence is UNVERIFIED.
- GitHub code search returned about 7,000 hits for "network architect" in SKILL.md files; only the first page was reviewed. Other good packs may exist (for example the [VincentChuWaiChow OCI and GCP
  network-architect skills](https://github.com/VincentChuWaiChow/vanguard-frontier-agentic) seen in results were not opened).
- Templates and references were being edited by other agents during this survey; the template list in section 2 is a snapshot at 2026-10-29 17:58.
