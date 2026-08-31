---
name: team
description: "Form a temporary AI-agent team for a task by selecting the smallest suitable group from the persona library."
argument-hint: "[task description]"
disable-model-invocation: true
---

# Form a Temporary Team

Use this skill to choose a focused temporary team from `personas/` for the task below.

## Task

$ARGUMENTS

## Available Personas

| Persona | File | Primary contribution |
| --- | --- | --- |
| CEO | `ceo-bezos` | strategy, priorities, business model, decision narratives |
| CTO | `cto-vogels` | architecture, technology choices, system design |
| Critic | `critic-munger` | independent challenge, pre-mortems, assumption review |
| Product | `product-norman` | product definition, usability, human-centred decisions |
| UI Design | `ui-duarte` | visual design, design systems, interface hierarchy |
| Interaction Design | `interaction-cooper` | user flows, personas, interaction models |
| Full-Stack Engineering | `fullstack-dhh` | implementation, technical plans, product delivery |
| Quality Assurance | `qa-bach` | test strategy, release confidence, defect analysis |
| DevOps / SRE | `devops-hightower` | delivery, infrastructure, monitoring, operational readiness |
| Marketing | `marketing-godin` | positioning, demand, content, audience development |
| Operations | `operations-pg` | customer learning, growth, community, product-market fit |
| Sales | `sales-ross` | pipeline, conversion, customer conversations |
| CFO | `cfo-campbell` | pricing, financial model, cost discipline, unit economics |
| Research | `research-thompson` | market research, competition, industry evidence |

## Procedure

### 1. Choose the smallest useful team

Select two to five personas whose work is necessary for the task.

- Match the task, rather than maximising the number of agents.
- Cover necessary hand-offs, such as product to design to engineering.
- Avoid overlapping roles unless a deliberate independent review is valuable.
- Briefly state who was selected and why before team work begins.

### 2. Create focused assignments

Give each member a concrete outcome, relevant context, boundaries, and a location for its output. Include the complete persona file as role guidance when the runtime supports it.

Use an English, kebab-case team name. Keep the team temporary and avoid assigning a persona authority the human operator has not delegated.

### 3. Coordinate and synthesise

Collect outputs, reconcile conflicts, and clearly separate evidence, inference, and open decisions. The operator remains the final decision maker. Dissolve the temporary team after the task is
complete.

## Output Expectations

Store role-specific working material under `docs/<role>/` only when that project convention applies. Return a unified conclusion, disagreements that need a human decision, and the next action.
