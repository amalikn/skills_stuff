---
name: skill-code-context-notes
description: "Read/write Code Context Notes via its MCP server instead of inline comments."
metadata:
  short-description: Annotate code without touching source
  aliases: skill-ccn
  upstream: https://github.com/jnahian/code-context-notes
version: 0.7.0
---

# Skill: Code Context Notes

## Contents

- [When to use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Surface routing — the decision that matters](#surface-routing--the-decision-that-matters)
- [Read before you edit](#read-before-you-edit)
- [Writing notes](#writing-notes)
- [How notes survive edits](#how-notes-survive-edits)
- [Scripts](#scripts)
- [Metadata conventions](#metadata-conventions)
- [Trust model and response shapes](#trust-model-and-response-shapes)
- [Per-repo setup](#per-repo-setup)
- [Anti-patterns](#anti-patterns)
- [Reference](#reference)

## When to use

Invoke when any of these are true:

- A fact about code is worth keeping but does not belong in the file — a hazard, a rationale, a constraint discovered the hard way.
- You are about to edit code in a repo that has a `.code-context-notes/` directory, and prior context may exist.
- The operator asks to record why a change was made, or to leave a handoff for the next session.
- A repo needs the extension wired up.

Do **not** invoke for general note-taking, project status, or session memory. Those go to `memory-keeper`, `mcp-project-context`, or `SCRATCHPAD.md`.

## Prerequisites

Notes are written **only** through the MCP server. Never hand-write files into `.code-context-notes/` — the extension and server serialize writes through advisory locks in
`.code-context-notes/.locks/`, and the
on-disk format is versioned via `@jnahian/code-notes-core`. A foreign writer corrupts both guarantees.

Check the server is available before attempting a write. If the `code-notes` MCP tools are absent, go to [Per-repo setup](#per-repo-setup) rather than falling back to file edits.

Read tools are always present. Write tools (`create_note`, `edit_note`, `delete_note`, `add_handoff`, `add_decision`) appear only when the server was started with `--agent`. If you see the read tools
but no write tools, the server is in read-only mode — report that, do not work around it.

## Surface routing — the decision that matters

Three surfaces compete for the same fact. Choosing wrong is the main failure mode of this tool: notes that should have been comments get lost to readers who never install the extension, and governance
that should have been a doc gets buried at a line number.

| Fact                                                       | Surface                              | Why                                                                                              |
| ---------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Reader must see it to not break the line they are editing  | Inline comment in source             | A note is invisible without the extension. Safety-critical context must not be opt-in.           |
| Why this code exists, what was tried, what the constraint was | Code note (`rationale` / `decision`) | Long-form why bloats the file and pollutes git blame; the note survives without cost to readers. |
| Applies to a whole role, playbook, or subsystem            | Governance doc (`AGENTS.md`, `.agents/*.md`) | Line-anchored storage is the wrong shape for subsystem-wide rules.                               |
| Outstanding work at a specific location                    | Code note (`todo`)                   | Keeps the file clean and shows in the sidebar with priority.                                     |
| Where the next session should resume                       | Code note (`handoff`)                | Purpose-built, auto-expires in 7 days.                                                           |

Rule of thumb: **if being unaware of it would cause a bug, it goes in the file.** Everything else that is location-specific goes in a note.

## Read before you edit

Before modifying files in a repo that has notes, pull the relevant context. This is cheap and prevents re-deriving a constraint someone already recorded.

- `get_notes_for_changes` — pass the changed `files` or a unified `diff`; returns notes ranked by relevance. Use this at the start of an edit task.
- `list_instructions` — active `instruction` and `warning` notes. Treat a `warning` as a hard constraint on the change you are about to make.
- `get_notes_for_file` — everything on one file, including directory-scoped notes that cover it.
- `search_notes` — full-text with `type` / `tags` / `file` filters.
- `get_handoffs` — resume points from prior sessions.

`.code-context-notes/AGENTS.md` is an auto-generated digest hoisting `instruction`, `warning`, and `handoff` notes. It is readable without the MCP server — useful as a fallback, but never edit it, it
is
regenerated on every note change.

## Writing notes

Prefer the specific tool over the generic one — each enforces its own contract.

- `add_decision` — architectural decision plus rationale. **Requires at least one reference**, so the why stays traceable. Use for "we chose X over Y because Z".
- `add_handoff` — resume point. Defaults to a 7-day expiry. Use at session end when work is genuinely unfinished.
- `create_note` — everything else. Set `type`, `priority`, `scope`, `tags` explicitly rather than accepting defaults.
- `edit_note` — appends a history entry; prior content is preserved. Prefer editing over delete-and-recreate, which loses the trail.

Content discipline: write the note as prose a colleague reads at 3am during an incident. State the observed behaviour, the cause, and the constraint. Do not restate what the code plainly says.

Anchor to the **narrowest line range that carries the meaning**. Notes track by content hash, so a tight range survives refactors above it but breaks when those exact lines are rewritten — which is
precisely when the note needs review anyway.

### Order of operations when converting comments to notes

**Edit the file first, then anchor the notes.** Notes store an absolute line range plus a content hash. The hash is what lets the extension re-anchor, but **the MCP server does not re-anchor on read**
— it returns the stored range. So notes written *before* a large deletion keep pointing at the old line numbers until the VS Code extension next scans the file, and a `get_notes_for_file` in between
returns ranges that are silently wrong, sometimes past EOF.

Verified 2026-08-26 on `smc_rsyslog/tasks/main.yml`: stripping 85 lines left nine freshly-written notes stale, while a note the extension already held re-anchored exactly (297 -> 240, matching the 57
lines removed above it). Re-anchoring works; it just needs the extension, not the server. If you must write first, tell the operator to reload the window before trusting any line number.

### Never put an inline marker inside a block scalar

When leaving a one-line hazard marker in source, check what the line is part of. A `#` added inside a `content: |` / `script: |` / heredoc is **not a source comment** — it becomes part of the file or
command that gets deployed to the target. Put the marker on the key above the block instead.

Caught on the same file: the `su root syslog` line most needing a marker sits inside a `content: |` that is written to `/run/...logrotate` on the remote host. The marker went above `content:`, and
`yaml.safe_load` before and after compared equal, which is the check that proves the deployed payload is untouched.

## How notes survive edits

A note is anchored by a **normalized sha256** over its line range: each line `.trim()`ed, internal whitespace collapsed to single spaces, **blank lines dropped**, survivors joined with `\n`.
Reindenting, reflowing, or adding blank lines inside a range therefore leaves the hash unchanged and the note completely undisturbed.

On every `onDidChangeTextDocument` (debounced per file) the extension runs `updateNotePositions` over each note anchored in that file:

1. **Validate** — does the hash still match at the current `lineRange`? Then stop; nothing to do.
2. **Exact search** — slide a window of the same line count across the **whole file** from line 0. First exact hash match wins; the note moves there.
3. **Fuzzy search** — windows within **±50 lines** of the old range only, normalized Levenshtein similarity, best match kept if **≥ 0.7**.
4. **All three fail → the note silently keeps its old range.** Not deleted, not flagged, and it renders identically to a correct note.

| Edit | Outcome |
|---|---|
| Insert or delete lines above the note | Exact match found elsewhere; the note follows automatically |
| Reindent, reflow, add or remove blank lines inside the range | Hash unchanged; the note does not even need to move |
| Light edit to the anchored code | Fuzzy match ≥ 0.7 within ±50 lines; re-anchors, usually in place, leaving a **stale hash** |
| Heavy rewrite, or the block moves >50 lines *and* its text changed | Silently stale |
| Anchored code deleted | Silently stale — the note now describes whatever occupies those lines |

### Four ways this fails silently

1. **First-match wins.** The exact pass scans from line 0 and takes the first matching window. In files full of repeated idioms — Ansible task files especially — a note can jump to an **earlier
   identical block**. A hash cannot tell two copies apart.
2. **Step 4 is invisible.** A stale note looks exactly like a correct one in the sidebar. Nothing warns you.
3. **Re-anchoring only fires on VS Code document-change events.** A `git checkout`, a branch switch, a `sed` pass, or an ansible-lint autofix run in a terminal produces **no event**, so every note in
   the touched file is left stale with nothing reporting it. This is the mode most likely to bite a repo with active branch work.
4. **Agent writers never re-anchor.** `updateNotePositions` throws for them outright — notes written through the MCP server are repositioned only by a running extension instance, never by the write
   that created them.

### The rule that follows

**Run `check_note_anchors.py` after any branch switch or out-of-editor edit, not just after writing notes.** Authoring is the case everyone remembers; the silent ones are the case that costs an hour.

Verified 2026-08-27 by reimplementing the hash and reproducing it against live notes: **22 of 24 matched byte for byte**. The two that did not were the blocks whose inline markers had been edited
after anchoring — no exact-hash window existed anywhere in either file, so the extension had fallen through to the fuzzy pass and re-anchored them in place. **Correct range, stale hash** — a real
state that is invisible in the sidebar. `check_note_anchors.py` now detects it and reports it as `DRIFTED`; see [Scripts](#scripts).

## Scripts

Bundled under `scripts/`, beside this file. All three are standalone Python 3, no dependencies beyond PyYAML for the YAML gate.

| Script | Use |
|---|---|
| `check_note_anchors.py` | **Run after every edit to an annotated file, and after any branch switch or out-of-editor edit.** Verifies each live note's range is in bounds, verifies its `Content Hash` and classifies any mismatch as `MOVED` or `DRIFTED`, prints what it points at, and reports any note the sidebar will not show or will show in the wrong place. `--no-hash` skips the hash pass. |
| `map_comment_blocks.py` | Find comment blocks worth converting. `--min N` sets the run length; `--json` for machine use. Masks block scalars and heredocs, ignores trailing comments. |
| `strip_comment_blocks.py` | Apply the strip. Every edit asserts an expected substring on its first line and aborts on mismatch; YAML is gated on data-equality, not just "it parses". |

Typical order, which is also the safe order:

```bash
S=~/.claude/skills/skill-code-context-notes/scripts
python3 $S/map_comment_blocks.py path/to/file.yml --min 3      # 1. decide what moves
python3 $S/strip_comment_blocks.py path/to/file.yml \
        --edits edits.json --backup /tmp/ccn                    # 2. edit first
python3 $S/check_note_anchors.py                                # 3. then anchor, then verify
```

It also answers the second question that looks identical from the UI: **"the notes exist but the sidebar is empty."** `INDEX.json` and the `AGENTS.md` digest are written **only** by the
extension — the MCP server writes note `.md` files and touches neither. Whether the extension notices those writes depends on the watcher, which is where a relocated `.code-context-notes` bites:
see [When the storage directory is a symlink](#when-the-storage-directory-is-a-symlink). Where the watcher is blind, a note created over MCP is on disk and readable by any agent, yet absent
from the sidebar until the extension next activates. The script compares the index against the `.md` files **per note**, not by mtime: an mtime check cries
wolf, because every re-anchor rewrites a `.md` and leaves the index legitimately current while its mtime looks behind.
Note that `INDEX.json` stores `lineRange` 0-indexed like the MCP schema, while the `.md` header renders it 1-indexed.

Staleness is reported but is **not** an error — exit stays 0. It is the normal state immediately after writing notes, and the fix is a window reload, never a repair.

`check_note_anchors.py` exists because of a specific failure: out-of-range notes crash the extension's activation, and because activation crashes it never regenerates `INDEX.json`, so the bad state
survives a reload and every contributed command reports "command not found". The script catches that before it happens.

It **also verifies `Content Hash`** and, on a mismatch, classifies it by replaying the extension's own exact-match pass — sliding a same-line-count window across the whole file:

- **`MOVED`** — the stored hash matches a *different* range in the same file. The extension will relocate the note on its next document-change event; until then the stored range is stale.
- **`DRIFTED`** — the hash matches nowhere. The anchored code was edited, so the exact pass is spent and only the fuzzy fallback can still find it. The range is often still correct;
  this is exactly
  what a completed fuzzy re-anchor leaves behind.

**Neither is an error** — both leave exit 0, because they describe anchor *quality* rather than a broken extension. Out-of-range notes remain the only exit-1 condition, because they are the only one
that crashes activation. `--no-hash` skips the pass entirely.

## Metadata conventions

| Field        | Values                                                       | Guidance                                                                                                               |
| ------------ | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `type`       | `context` `instruction` `warning` `decision` `todo` `handoff` `rationale` | `instruction` and `warning` are hoisted into the agent digest — reserve them for things that genuinely bind behaviour. |
| `priority`   | `low` `normal` `high` `critical`                             | `critical` is always included in digests. Use it for hazards that cause outages, not for merely important context.     |
| `scope`      | `line` `function` `class` `file` `directory`                 | `directory` notes return for any file beneath them — the right shape for "everything under this role must…".           |
| `tags`       | free-form strings                                            | Keep a small controlled vocabulary per repo so filtering stays useful.                                                 |
| `references` | `pr` `issue` `commit` `test` `url` `note`                    | Required on `decision`. Prefer a commit SHA or issue over a URL that rots.                                             |
| `expiresAt`  | ISO 8601                                                     | Expiry hides, never deletes. Set it on anything tied to a temporary workaround.                                        |

Every note records `authorType`. Notes you write are `agent`; the operator's own edits in VS Code are `human`. Do not attempt to present agent-written notes as human-authored.

## Trust model and response shapes

`agentWriteMode` lives in `.code-context-notes/config.json` — a workspace-owned file. There is deliberately no server flag, so an agent cannot pick its own rails. Do not edit this file to widen your
own
permissions; if a write is blocked, report it.

| Mode              | What happens to your write                                                           |
| ----------------- | ------------------------------------------------------------------------------------ |
| `direct`          | Lands immediately.                                                                   |
| `audit` (default) | Lands immediately, appended to `.code-context-notes/_audit.log`, revertible by the operator. |
| `queue`           | Becomes a proposal in `.code-context-notes/_pending/`; a human approves it.                  |

Two response shapes that are **not** errors and must not trigger a retry loop:

- `{ "status": "pending", "proposalId": … }` — queue mode. The write succeeded as a proposal. Tell the operator it awaits approval in the **Pending agent proposals** view. Retrying changes nothing.
- `{ "error": "lock_timeout", "retryable": true }` — another writer held the lock. Retry **once** after a short delay. A second timeout is a real conflict: stop and report it.

## Per-repo setup

1. Confirm the extension is installed: `code --list-extensions | grep jnahian.code-context-notes`.
2. Write `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "code-notes": {
      "command": "npx",
      "args": ["-y", "@jnahian/code-notes-mcp", "--workspace", ".", "--agent", "claude-code"]
    }
  }
}
```

### Install the MCP server globally, not per repo

`--workspace .` resolves against the server's working directory, which is the project root, so **one global entry adapts to every repo**. Verified: launched from an unrelated directory it reports that
directory as its workspace, and with no notes present it starts in empty mode and creates **no** stray `.code-context-notes/`. The directory is created on first write only.

So prefer a single entry in `~/.claude.json` under top-level `mcpServers` over a `.mcp.json` per repo:

```json
"code-notes": {
  "command": "npx",
  "args": ["-y", "@jnahian/code-notes-mcp", "--workspace", ".", "--agent", "claude-code"]
}
```

Do **not** add `--require-existing` to a global entry — it makes startup fail (exit 3) in every repo that has no notes yet.

A per-repo `.mcp.json` still works and takes precedence, but it is a file in the shared repo that must then be excluded like `.code-context-notes` itself. The global entry avoids that entirely.

Skills install globally the same way: symlink the skill directory into `~/.claude/skills/` and `~/.codex/skills/` rather than copying, so all three agents read one canonical `SKILL.md`.

3. Decide whether notes are shared or private, then exclude accordingly.

**Shared repo where notes must stay private:** use `.git/info/exclude`, never `.gitignore` — a `.gitignore` edit is itself a commit, which announces your private tooling to everyone.

**Critical gotcha.** Write *both* forms:

```
.code-context-notes
.code-context-notes/
```

A trailing-slash pattern matches directories only, and git does not treat a **symlink to a directory** as a directory. If `.code-context-notes` is later relocated and symlinked back — a normal move
for
keeping notes outside a company repo — the trailing-slash-only pattern silently stops matching and the notes appear as untracked. Exclude `.mcp.json` the same way.

4. Verify with `git check-ignore -v .code-context-notes` and confirm `git status --porcelain` is clean.

If notes are relocated outside the repo, they are no longer versioned by anything. The extension keeps per-note edit history inside each `.md`, so note-level history survives, but file-level recovery
does not. Say so explicitly rather than implying the notes are backed up.

### When the storage directory is a symlink

Relocating `.code-context-notes` out of the repo and symlinking it back — the move above, and the one that keeps notes out of a company repo — has a second cost beyond versioning: **the extension
stops
seeing note changes live.**

The extension registers a real watcher:

```js
createFileSystemWatcher(new RelativePattern(workspaceFolders[0], `${storageDir}/**/*.{md,log}`))
```

`RelativePattern` anchors it to the **workspace folder**, and VS Code's file watcher does not follow a symlink out of that tree. Every note the MCP server writes lands on an inode outside the watched
path, so no event fires and the extension only re-reads on activation.

Verified 2026-08-27: touching a note `.md` through the symlink left `INDEX.json` unchanged for 20s. With a real (non-symlinked) `.code-context-notes`, MCP-written notes appear without a reload.

**This is a tradeoff, not a bug, and it is usually worth paying** — the relocation is what keeps notes out of the shared repo while still versioning them. Just do not promise live updates. Run
`check_note_anchors.py` after writing notes and tell the operator to reload; the script names exactly which notes the sidebar is missing or misplacing.

If live updates matter more than versioning, keep `.code-context-notes` a real directory excluded via `.git/info/exclude` and accept that the notes are then in no repository at all.

**The general shape is worth carrying beyond this tool:** relocating a directory out of a tree silently breaks anything anchored to that tree. It cost a gitignore match (trailing-slash patterns stop
matching a symlink) and a file watcher, in the same setup, and neither failed loudly.

## Anti-patterns

- Hand-writing or editing files under `.code-context-notes/` — bypasses locking and the versioned format.
- Editing `.code-context-notes/AGENTS.md` or `INDEX.json` — auto-generated, overwritten on the next note change.
- Changing `agentWriteMode` to unblock your own write.
- Marking routine context as `critical` or `instruction`, which drowns the digest and devalues real hazards.
- Recording a safety-critical constraint as a note when a reader without the extension would break the code.
- Retrying a `{ "status": "pending" }` response.
- Wide line ranges "to be safe" — they make content-hash tracking fail on any edit within the block.

## Reference

- Upstream repo: <https://github.com/jnahian/code-context-notes>
- MCP server package: `@jnahian/code-notes-mcp` — `npx -y @jnahian/code-notes-mcp --workspace <path> --agent <name>`
- Flags: `--workspace` (required), `--agent` (enables writes), `--storage-dir` (match `codeContextNotes.storageDirectory`), `--require-existing` (exit 3 if no notes dir)
- Docs: `docs/guide/agents-and-mcp.md`, `docs/guide/trust-model.md`, `docs/guide/note-types-metadata.md`, `docs/reference/note-schema.md`
- Keep the extension and MCP server on compatible versions — they share the on-disk format through `@jnahian/code-notes-core`.
