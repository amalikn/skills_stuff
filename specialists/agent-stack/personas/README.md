Title: Personas index
Category: library-index
Status: current
Scope: The judgement contracts Agent Stack routes to
Last reviewed: 20260903_2200
Summary: One row per persona, derived from each file's own frontmatter, so a persona added without an index row fails the coverage gate.

# Personas

A **persona** is a judgement contract: what this role is accountable for deciding, and what it refuses to decide. A **skill** is a repeatable procedure. When a change blurs that split, stop and ask
which layer owns it — the distinction is what lets one route combine several judgements without any of them dissolving into the others.

Personas are selected by [`routing.toml`](../routing.toml) and registered in [`manifest.yaml`](../manifest.yaml). The normal entry point is
[`skill-agent-stack`](../skills/skill-agent-stack/SKILL.md), which picks the smallest sufficient set rather than the largest defensible one; call a persona
directly only for a deliberately narrow single-domain task.

This index exists because `personas/` was the one library layer with no way in. It was found by the inverse sweep on 20260903 — the sweep that asks what exists
that no catalog names, rather than what a catalog names that has vanished. Only the first grows while nobody is looking.

## The 15 personas

| Persona | Role | Judges |
| --- | --- | --- |
| [`ceo-bezos`](ceo-bezos.md) | CEO — Customer-Backwards Executive | own enterprise direction, prioritisation, resource allocation, operating mechanisms, and high-stakes business decisions |
| [`cfo-campbell`](cfo-campbell.md) | CFO — Commercial and Capital Discipline | judge economic viability, pricing, monetisation, capital allocation, cash exposure, and financial resilience |
| [`critic-munger`](critic-munger.md) | Critic — Inversion and Decision-Quality Reviewer | independently challenge plans, forecasts, architecture, and recommendations before commitment |
| [`cto-vogels`](cto-vogels.md) | CTO — Architecture and Technical Strategy | own technical architecture, engineering leverage, reliability, security posture, and technology strategy |
| [`devops-hightower`](devops-hightower.md) | DevOps / SRE — Platform, Delivery, and Operations | make software delivery and infrastructure safe, repeatable, observable, recoverable, and operable by the owning team |
| [`fullstack-dhh`](fullstack-dhh.md) | Full-Stack Engineer — Pragmatic Product Builder | turn validated product intent into maintainable working software with minimal accidental complexity |
| [`interaction-cooper`](interaction-cooper.md) | Interaction Designer — Behaviour and Flow | design how users accomplish goals through states, flows, feedback, errors, and interaction models |
| [`marketing-godin`](marketing-godin.md) | Marketing — Positioning and Demand | create differentiated positioning, audience strategy, content systems, and permission-based demand generation |
| [`operations-pg`](operations-pg.md) | Operations / Early-Stage Operator — Learning and Execution | turn uncertain business ideas into fast learning loops, practical operating mechanisms, and evidence of product-market fit |
| [`orchestrator-follett`](orchestrator-follett.md) | Orchestrator — Mary Parker Follett | the coordination persona for multi-domain Agent Stack work. It classifies the task, selects the smallest sufficient personas and skills, defines hand-offs and decision gates, preserves disagreement, and returns one operator-facing synthesis |
| [`product-norman`](product-norman.md) | Product — Human-Centred Product Strategist | define the right product problem, user value, product requirements, prioritisation, and success criteria |
| [`qa-bach`](qa-bach.md) | QA — Risk-Based Quality Engineer | provide release confidence by modelling product risk, designing effective tests, and finding consequential failures |
| [`research-thompson`](research-thompson.md) | Research — Evidence and Competitive Intelligence | find, evaluate, triangulate, and synthesize external or internal evidence without overstating certainty |
| [`sales-ross`](sales-ross.md) | Sales — Pipeline and Customer Conversion | design and improve repeatable customer acquisition conversations, qualification, pipeline, outreach, and conversion |
| [`ui-duarte`](ui-duarte.md) | UI Design — Visual Communication and Design Systems | create clear, coherent visual interfaces and presentation hierarchy that support product intent and interaction behaviour |

## Reading one

Each file carries its mandate, the decisions it owns, the decisions it explicitly refuses, and how it reports disagreement. **Disagreement is preserved rather
than averaged** — where two personas conflict, the route surfaces the conflict and names what evidence would settle it, because a synthesis that splits the
difference between a correct and an incorrect view is worse than either.
