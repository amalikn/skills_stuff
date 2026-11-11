---
Title: docs/history layout
Category: reference
Status: current
Authority: skill-module
Scope: Where rotated records live, how their index is built, and how a project moves from the flat layout
Last reviewed: 2026-11-11
Summary: >-
  docs/history holds one subfolder per kind of rotated record (changelog, scratchpad, roadmap, session-records, sync); its readme index is generated with a summary line
  per file; history_migrate.py moves a flat folder and repoints every reference.
---

# docs/history layout

The standard since 2026-11-11 (operator: "create sub directories and make it a standard ... other entries should also have this sort of summary like the session records have"). One flat folder had
grown to 152 files in smc-resiliency and 369 in unified-network-controller, and its index said only "1 entries from CHANGELOG.md".

## Contents

- [Layout](#layout)
- [The index](#the-index)
- [Who writes what](#who-writes-what)
- [Migrating a flat folder](#migrating-a-flat-folder)
- [Pitfalls](#pitfalls)

## Layout

```text
docs/history/
  readme.md                         index: hand-written intro, then the generated block
  rotation-audit-baseline.txt       audit_rotations.py baseline (stays at the top)
  changelog/        changelog-<stamp>.md         rotate_records.py
  scratchpad/       scratchpad-<stamp>.md        rotate_records.py (also *-outbox.md variants)
  roadmap/          roadmap-<stamp>.md           roadmap_trim.py
  session-records/  session-record-<stamp>.md    slurp closeouts (skill-slurp-chat Step 8)
  sync/             sync-archive-<stamp>.md      apn scripts/project_sync.py
```

File names do not change; the kind is the name's prefix (`scripts/records/history_layout.py` `KINDS`). A file of no known kind stays at the top and is listed under "Other" in the index.

## The index

`docs/history/readme.md` keeps whatever is above `<!-- history-index:start ... -->` (title, intro) and the generator rebuilds everything between the markers: one section per kind, newest first, each
line `- [name](kind/name) <count and dates>: <what it is about>`:

| Kind            | Summary built from                               |
| --------------- | ------------------------------------------------ |
| changelog       | the archived entries' titles                     |
| scratchpad      | section and first words of each archived entry   |
| roadmap         | the done items' first words                      |
| sync            | the ticked items' first words                    |
| session-records | the record's front-matter `Summary` (or `Title`) |

A description written by hand on an index line is kept (anything that is not the old generated "N entries from ..." form). Preview a project's index: `python3 scripts/records/history_layout.py
--project-root <project>` (read-only).

## Who writes what

Every writer asks `history_layout.archive_dir(root, kind)` where to write and calls `write_index(root)` after writing; every reader uses `archives(root, kind)`, which finds both layouts. A project
that still has flat archives of a kind keeps writing that kind flat until it is migrated, so a half-migrated folder never happens. Archives keep their content verbatim except relative links, which are
recomputed for the folder the text lands in (`history_layout.relink`).

## Migrating a flat folder

```bash
just history-migrate <project>            # plan: moves per kind, files whose references change
just history-migrate <project> --apply    # git mv, rewrite links, regenerate the index, verify links
```

`scripts/records/history_migrate.py` refuses with uncommitted changes under docs/history (`--allow-dirty` overrides), moves each file with `git mv`, recomputes the links inside it, repoints links to
it anywhere under the git top level (`--refs-root` to change), repoints plain mentions `docs/history/<name>` in the project's own files and `<project>/docs/history/<name>` elsewhere (another project's
archive of the same name is never touched), skips `.remember/`, regenerates the index and fails when a link that resolved before no longer does. Then run the project's `just check` and commit the
folder.

## Pitfalls

- A project that keeps its own copy of a records script (UNC `scripts/render/roadmap_trim.py`) or a recipe that globs `docs/history/*.md` must be repointed by hand: search the project for
  `docs/history` after the migration.
- `glob("*.md")` on docs/history finds nothing after the move: use `archives()`, `all_history_md()` or `rglob`.
- An archive's index table copies an entry's first line; before 2026-11-11 that copy was not relinked, so an old row can hold a link that never resolved. The migration reports it; fix the row by hand.
