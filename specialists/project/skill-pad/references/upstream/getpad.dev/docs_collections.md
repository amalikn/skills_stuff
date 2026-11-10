**Title:** Collections & Schemas

**Source:** [https://www.getpad.dev/docs/collections](https://www.getpad.dev/docs/collections)

---

# Page Structure Map
```text
Collections & Schemas
├── Default Collections
│   ├── Tasks
│   ├── Ideas
│   ├── Plans
│   ├── Docs
│   ├── Conventions
│   └── Playbooks
├── Custom Collections
├── Field Types
├── Items
├── Wiki Links
└── Slugs
```

---

Collections are the core organizational unit in Pad. Each collection defines a type of item with its own set of typed fields and behaviors.

## Default Collections

Every new workspace comes with six default collections:

### Tasks

Track work items, bugs, and to-dos.

| Field | Type | Options |
| --- | --- | --- |
| status | select | `open`, `in-progress`, `done`, `cancelled` |
| priority | select | `low`, `medium`, `high`, `critical` |
| assignee | text | — |
| due\_date | date | — |
| effort | select | `xs`, `s`, `m`, `l`, `xl` |
| *(parent link)* | — | *Any item can be a child of another item via `--parent`* |

### Ideas

Capture ideas, feature requests, and inspiration.

| Field | Type | Options |
| --- | --- | --- |
| status | select | `new`, `exploring`, `planned`, `rejected` |
| impact | select | `low`, `medium`, `high` |
| category | text | — |

### Plans

Track project plans and milestones.

| Field | Type | Options |
| --- | --- | --- |
| status | select | `planned`, `active`, `completed`, `paused` |
| start\_date | date | — |
| end\_date | date | — |
| progress | number | computed, auto-calculated from linked tasks |

### Docs

Documentation, notes, and reference material.

| Field | Type | Options |
| --- | --- | --- |
| status | select | `draft`, `published`, `archived` |
| category | text | — |

### Conventions

Project-specific rules that AI agents follow automatically.

| Field | Type | Options |
| --- | --- | --- |
| status | select | `active`, `draft`, `disabled` |
| trigger | select | `always`, `on-task-start`, `on-task-complete`, `on-implement`, `on-commit`, `on-pr-create`, `on-plan` |
| scope | select | `all`, `backend`, `frontend`, `mobile`, `docs`, `devops` |
| priority | select | `must`, `should`, `nice-to-have` |

### Playbooks

Multi-step workflows for specific actions or scenarios.

| Field | Type | Options |
| --- | --- | --- |
| status | select | `active`, `draft`, `deprecated` |
| trigger | select | `always`, `on-task-start`, `on-task-complete`, `on-implement`, `on-commit`, `on-pr-create`, `on-plan` |
| scope | select | `all`, `backend`, `frontend`, `mobile`, `docs`, `devops` |

## Custom Collections

Create your own collections with custom schemas:

```
pad collection create "Bugs" \
  --fields "severity:select:low,medium,high,critical; browser:text; reproducible:select:yes,no,sometimes" \
  --icon "🐛"
```

## Field Types

| Type | Description | Example |
| --- | --- | --- |
| `text` | Free-form text | assignee, category |
| `select` | Single choice from options | status, priority |
| `multi_select` | Multiple choices from options | tags, labels |
| `number` | Numeric value | progress, story points |
| `date` | Date value | due\_date, start\_date |
| `checkbox` | Boolean true/false | reproducible, verified |
| `url` | URL value | link, repository |
| `relation` | Link to another collection | linked references between items |

## Items

Items belong to a collection and have:

- **Title** — the item name, used to generate a URL-friendly slug
- **Fields** — structured data matching the collection’s schema
- **Content** — optional rich markdown body (notes, descriptions, documentation)
- **Tags** — free-form labels for additional categorization

## Wiki Links

Connect items across collections using `[[wiki links]]`:

```
This task implements the design from [[Auth Architecture]].
See also [[OAuth Bug]] for the related issue.
```

Wiki links resolve by title across all items in the workspace. In the web UI, they render as clickable links. In the CLI, they’re preserved as-is in markdown content.

## Slugs

Every item gets a URL-friendly slug derived from its title:

- “Fix OAuth Redirect” → `fix-oauth-redirect`
- “Plan 2: API Redesign” → `plan-2-api-redesign`

Slugs are unique within a workspace and used in CLI commands:

```
pad item show fix-oauth-redirect
pad item update fix-oauth-redirect --status done
```
