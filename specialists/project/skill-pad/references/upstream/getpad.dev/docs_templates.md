**Title:** Templates

**Source:** [https://www.getpad.dev/docs/templates](https://www.getpad.dev/docs/templates)

---

# Page Structure Map
```text
Templates
├── Software
│   ├── Startup (default)
│   ├── Scrum
│   ├── Product
│   └── Demo
├── People
│   ├── Hiring
│   └── Interviewing
├── Custom
│   └── Blank
├── Custom Setup
└── Choosing a Template
```

---

When you initialize a workspace with `pad init`, you can choose a template that pre-configures collections and workflows for your project type. Templates ship grouped by category so Pad fits more than software work.

Run `pad workspace init --list-templates` for the live catalog. Below covers the templates available today.

## Software

### Startup (default)

The default template, designed for small teams and solo developers building a product.

```
pad init
# or explicitly:
pad init --template startup
```

**Collections:** Tasks, Ideas, Plans, Docs, Conventions, Playbooks

Best for: side projects, startups, open source projects, solo developers.

### Scrum

Configured for agile teams running sprints.

```
pad init --template scrum
```

**Collections:**

- **Backlog** — items with status, priority, story points, and sprint fields
- **Sprints** — sprint planning with start/end dates and goals
- **Bugs** — bug tracking with severity and component fields
- **Docs**, **Conventions**, **Playbooks**

Best for: teams using scrum methodology, sprint-based development.

### Product

Designed for product management workflows with roadmap planning.

```
pad init --template product
```

**Collections:**

- **Features** — feature tracking with status, priority, and owner
- **Feedback** — customer feedback with source, customer, and impact fields
- **Roadmap Items** — roadmap entries with quarter and team fields
- **Docs**, **Conventions**, **Playbooks**

Best for: product teams, roadmap-driven development, multi-quarter planning.

### Demo

The startup template pre-loaded with realistic sample data — handy for exploring Pad’s features before committing to a real workspace. It’s **hidden from the interactive picker** but can be built explicitly by name:

```
pad init --template demo
```

**Collections:** Same as Startup, with example items already created.

## People

Pad’s data model — typed collections, parent/child links, conventions — works just as well for people-oriented workflows as for code. Two templates ship today:

### Hiring

Company-side hiring pipeline. Track open roles end-to-end: requisitions, candidates moving through interview loops, structured feedback.

```
pad init --template hiring
```

**Collections:**

- **Requisitions** — open roles with team, level, status (open / on-hold / closed)
- **Candidates** — applicants linked to a requisition, stage in the pipeline, source
- **Interview Loops** — scheduled loops with interviewers, panel composition, slot status
- **Feedback** — structured per-interview feedback with hire/no-hire signal and rubric scores
- **Docs** — role briefs, scorecards, calibration notes

Best for: hiring managers, recruiters, interview coordinators running structured loops.

### Interviewing

Candidate-side job search. Track applications across companies, prep notes, contacts, and interviews.

```
pad init --template interviewing
```

**Collections:**

- **Applications** — companies you’ve applied to with stage, role, salary band
- **Interviews** — upcoming interviews linked to applications with prep notes and outcomes
- **Companies** — company-level notes (research, mission, values, recent news)
- **Contacts** — recruiters, hiring managers, referrers — linked to companies and applications
- **Docs** — resume versions, cover letter snippets, behavioural-question prep

Best for: anyone running a multi-company job search who wants more structure than a spreadsheet.

## Custom

### Blank

System collections only — **Conventions** and **Playbooks** — with no pre-seeded sample items. Its sole seeded content is the `/pad onboard` playbook.

```
pad init --template blank
```

`blank` is the entry point for the agent-driven `/pad onboard` flow: instead of adapting a stock template, an AI agent (Claude Code, Cursor, an MCP client, …) interviews you and shapes collections, conventions, and roles to match your actual project from scratch. Run `/pad onboard` in an agent session inside the workspace to kick it off.

**Collections:** Conventions, Playbooks (with the `/pad onboard` playbook seeded and ready to run)

Best for: projects that don’t fit a stock template, or anyone who wants the `/pad onboard` agent to build the workspace conversationally.

## Custom Setup

Templates are just starting points. After initializing, you can:

- **Add collections** with `pad collection create`
- **Modify defaults** through the web UI
- **Create conventions** to encode your team’s workflow rules
```
# Add a custom collection after init
pad collection create "Bugs" \
  --fields "severity:select:low,medium,high,critical; browser:text" \
  --icon "🐛"
```

## Choosing a Template

| Template | Category | Best for |
| --- | --- | --- |
| `startup` | Software | Solo / small team building a product — simple, minimal overhead |
| `scrum` | Software | Agile teams running sprints with story points |
| `product` | Software | Product teams doing roadmap planning across quarters |
| `hiring` | People | Hiring managers + recruiters running structured interview loops |
| `interviewing` | People | Candidates running a multi-company job search |
| `blank` | Custom | Starting from scratch — system collections only; `/pad onboard` builds the rest |
| `demo` | Software | Exploring Pad — startup template + sample data (hidden from the picker; build with `--template demo`) |
