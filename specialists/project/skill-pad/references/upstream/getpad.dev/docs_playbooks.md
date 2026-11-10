**Title:** Playbooks

**Source:** [https://www.getpad.dev/docs/playbooks](https://www.getpad.dev/docs/playbooks)

---

# Page Structure Map
```text
Playbooks
├── Invocation model
├── Creating a playbook
├── Fields explained
│   ├── invocation\slug (optional)
│   ├── arguments (optional, JSON array)
│   └── Two-way binding
├── Authoring the ## Arguments section
├── Test invocation helper
├── The seeded ship playbook
├── Bootstrap returns playbook metadata
└── Related
```

---

A **playbook** is a workspace-owned, user-editable procedure that an agent (or a human) can invoke directly. Think `/pad ship PLAN-42` from Claude Code or `pad playbook run release 0.5.0` in your shell. Each playbook is just an item in the `playbooks` collection with two fields that turn it into something callable: an **invocation slug** and an **arguments contract**.

This is the headline difference between a *playbook* and a *convention*. Conventions teach the agent how to work (rules); playbooks give the agent a named procedure to run (recipes).

## Invocation model

A playbook can be invoked three ways. The same procedure, the same argument contract, three surfaces:

- **Claude Code (agent NL):** `/pad ship PLAN-42 stop-after-each merge-strategy=rebase`. The `/pad` skill matches the first token against the workspace’s playbook slug list and binds the rest using flexible natural-language parsing (“ship PLAN-42 squashed, no install” → `target=PLAN-42, merge-strategy=squash, no-install=true`).
- **CLI (strict):** `pad playbook run ship PLAN-42 stop-after-each merge-strategy=rebase`. The server applies strict positional + bareword-flag + `key=value` parsing.
- **MCP:** the `pad_playbook` tool with `action: run`. Pass `args` (pre-parsed map) or `raw_args` (CLI tokens); the server returns the rendered body + bound args + any required args you forgot to supply.

The server **never executes** a playbook — it parses the args and hands the body back. The agent (or a human reading the output) does the work.

## Creating a playbook

The web UI’s playbook editor is the canonical path: visit `/{username}/{workspace}/playbooks`, click ”+ New Playbook”, and fill in the structured form. The editor pre-fills a skeleton template, validates the slug live (kebab-case + workspace uniqueness), and offers a “Test invocation” helper that previews the three command forms.

The editor exists specifically because the structured `arguments` field is a JSON value — declaring it through a built-up form (with type dropdowns, required toggles, enum option lists) is much friendlier than hand-writing JSON. The structured arguments and the body’s `## Arguments` section are two-way bound; edit either and the other updates.

From the CLI you can author the title, slug, trigger, scope, status, and body. The structured argument spec lands in the editor:

```
# Trigger-only playbook (no arguments — fully CLI-authorable)
pad item create playbook "Release checklist" \
  --field trigger=on-release \
  --field scope=all \
  --field status=active \
  --stdin <<'EOF'
1. Run full test suite
2. Update CHANGELOG
3. Tag the release
EOF

# Slug-invocable playbook with arguments — author shell from the CLI,
# then declare the argument spec in the web editor.
pad item create playbook "Cut a release" \
  --field invocation_slug=release \
  --field trigger=manual \
  --field status=active \
  --stdin <<'EOF'
Cut a Pad release.

## Arguments

- `version` (string, required) — semver, e.g. 0.5.0
- `dry-run` (flag, default=false) — validate without tagging

## Steps

1. Verify the tree is clean and on main
2. Run `make test`
3. If `dry-run`, stop here and print what would have happened
4. Tag with `git tag v$VERSION && git push --tags`
5. Verify CI release workflow succeeded
EOF
# Then open /{username}/{workspace}/playbooks/release in the web UI and declare
# the argument spec in the structured form. The body's ## Arguments
# section above is the human-readable mirror; the structured field
# is what the strict CLI parser binds against.
```

## Fields explained

### invocation\_slug (optional)

The kebab-case routing token. Pattern: `^[a-z0-9][a-z0-9-]*[a-z0-9]$` — lowercase letters, digits, hyphens; minimum 2 chars; no leading or trailing hyphen.

- **Set it** to make the playbook directly invokable: `/pad <slug>`, `pad playbook run <slug>`, `pad_playbook` MCP.
- **Leave it blank** for playbooks that should only run when the user describes the intent. Example: a `Release checklist` playbook with `trigger=on-release` and no slug auto-loads when the user says “let’s do a release,” but typing `/pad release-checklist` doesn’t route to it directly.

Slugs are workspace-unique. The editor’s debounced uniqueness check flags conflicts as you type.

### arguments (optional, JSON array)

The structured argument contract. Five types are supported:

| Type | Example value | Notes |
| --- | --- | --- |
| `ref` | `TASK-5` or item slug | Resolves to a Pad item |
| `string` | `"0.5.0"` | Free-form text |
| `flag` | `true` / `false` | Presence-based boolean; no value in CLI form |
| `enum` | `"squash"` (from a fixed list) | Carries an `enum: [...]` option list |
| `number` | `5`, `3.14` | Finite float; NaN/Inf rejected |

Each entry is `{name, type, required, default, description, enum}`. The web editor renders this as a card-per-argument form; the body’s `## Arguments` section is the human-readable mirror.

### Two-way binding

The structured `arguments` JSON field is the canonical, queryable form. The body’s `## Arguments` section is the human-readable mirror. The web UI editor keeps them in sync:

- Editing an argument card updates the body’s `## Arguments` section live.
- Editing the markdown section re-parses back into the structured form on the next save.

The CLI’s strict parser (`pad playbook run`) reads the structured field. The agent’s NL parser reads the body section. Both stay consistent because the editor enforces canonical formatting on save.

## Authoring the ## Arguments section

The canonical bullet format the parser round-trips cleanly:

```
## Arguments

- `target` (ref, required) — what to ship
- `stop-after-each` (flag, default=false) — pause for confirmation between merges
- `merge-strategy` (enum, default=squash, options: squash|merge|rebase) — how PRs get merged
- `limit` (number) — ship at most N tasks from the list
```

Each bullet declares: name (backticked), parenthetical type + options (comma-separated), and a description after the em-dash. The parser is permissive on unknown tokens, so hand-written sections survive a round-trip-then-re-render.

## Test invocation helper

The web editor includes a “Test invocation” panel that renders three copy-pasteable forms from a slug + sample arg values:

```
/pad ship PLAN-1377 stop-after-each merge-strategy=rebase
```
```
pad playbook run ship PLAN-1377 stop-after-each merge-strategy=rebase
```
```
{
  "action": "run",
  "ref": "ship",
  "args": {
    "target": "PLAN-1377",
    "stop-after-each": true,
    "merge-strategy": "rebase"
  }
}
```

Use this to verify the spec lines up with what you’d type before saving.

## The seeded ship playbook

Fresh `pad workspace init --template startup` workspaces ship a generic `ship` playbook out of the box — `invocation_slug=ship`, full body, declared arguments. It’s the canonical worked example: open it in the editor (`/{username}/{workspace}/playbooks/ship`) and see how the slug, arguments, and body fit together.

Try it:

```
pad playbook show ship --format markdown
pad playbook run ship PLAN-42 stop-after-each
```

## Bootstrap returns playbook metadata

When the `/pad` skill loads at session start, `pad bootstrap` returns the workspace’s playbook metadata in one round-trip:

```
{
  "playbooks": [
    {
      "ref": "PLAYB-1160",
      "title": "Cut a release",
      "slug": "cut-a-release",
      "invocation_slug": "release",
      "trigger": "manual",
      "scope": "all",
      "status": "active",
      "has_arguments": true,
      "summary": "Cut a Pad release."
    }
  ]
}
```

No bodies. The agent reads the metadata, knows which slugs are routable, and only loads the full body (`pad playbook show <slug>`) when it’s actually invoking. Keeps the skill’s context window light while still letting `/pad <slug>` route without a tool call.

The same payload is available on demand via `pad_meta.action: bootstrap`, the `pad://workspace/{ws}/bootstrap` MCP resource, and `pad_set_workspace`’s embedded response.

## Related

- [Agent integration →](https://www.getpad.dev/docs/agent-integration) — how conventions and playbooks feed the agent
- [MCP tools →](https://www.getpad.dev/docs/mcp/tools) — the `pad_playbook` tool’s catalog entry
- [CLI →](https://www.getpad.dev/docs/cli) — `pad playbook list | show | run`
