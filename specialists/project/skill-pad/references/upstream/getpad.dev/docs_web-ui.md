**Title:** Web UI Guide

**Source:** [https://www.getpad.dev/docs/web-ui](https://www.getpad.dev/docs/web-ui)

---

# Page Structure Map
```text
Web UI Guide
├── Dashboard
├── Collections
│   ├── Board View
│   ├── List View
│   └── Table View
├── Item Editor
└── Real-Time Updates
```

---

Pad includes a full web dashboard that runs locally at `http://localhost:7777`. It starts automatically when you use any `pad` command.

## Dashboard

The main dashboard shows an overview of your workspace:

- **Collection summaries** — item counts grouped by status
- **Active plans** — progress bars for in-progress plans
- **Attention items** — overdue tasks, stalled work, orphaned items
- **Recent activity** — latest changes across the workspace
- **Suggested next** — recommended items to work on

## Collections

Each collection has its own view with three display modes:

### Board View

A kanban-style board with columns for each status. Drag and drop items between columns to update their status. Best for tasks and workflows.

### List View

A compact list with key fields visible. Best for quick scanning and triaging.

### Table View

A full table view with all fields visible as columns. Sortable and groupable by any field. Best for browsing and bulk review.

Switch between views using the toggle in the collection header.

## Item Editor

Click any item to open the detail view:

- **Fields panel** — edit status, priority, assignee, and custom fields
- **Content editor** — rich markdown editor with formatting toolbar
- **Wiki links** — type `[[` to search and link to other items
- **Activity** — see the history of changes to this item

The content editor supports:

- Headings, bold, italic, strikethrough
- Bullet and numbered lists
- Code blocks with syntax highlighting
- Blockquotes
- Tables
- Wiki links with `[[Item Title]]` syntax
- **Sidebar** — lists all collections with item counts, plus quick links to the dashboard
- **Search** — global search accessible from the header, searches across all items
- **Keyboard shortcuts** — navigate quickly with keyboard

## Real-Time Updates

The web UI uses Server-Sent Events (SSE) to receive real-time updates. When you create or update items via the CLI or AI agent, the web UI reflects changes immediately — no refresh needed.
