---
Title: Local patches to third-party submodules
Category: folder-index
Status: current
Authority: canonical
Scope: Local edits to upstream submodules in skills_stuff that cannot be pushed to their authors' repos
Last reviewed: 2026-10-14
Summary: >-
  One patch per third-party submodule (SKILL.md descriptions shortened to one line for token budget). Reapply after an upstream update with
  git apply; regenerate when the local edit changes.
---

# Local patches to third-party submodules

The submodules below track other people's public repos, so local edits cannot be pushed there (operator, 2026-10-14: keep them as patches).
Each patch is `git diff` inside the submodule, taken against the base commit shown.

## Index

| Patch | Submodule path | Upstream | Base commit | Change |
|---|---|---|---|---|
| [diagram-design.patch](diagram-design.patch) | `diagram-design/` | cathrynlavery/diagram-design | `30764f2` | SKILL.md description on one line |
| [anydoc-github.patch](anydoc-github.patch) | `skills/skill-anydoc/anydoc-github/` | firecrawl/anydoc | `4a45add` | SKILL.md description edited |
| [strategy-os.patch](strategy-os.patch) | `strategy-os/` | BellaBe/strategy-os | `8240090` | 8 SKILL.md descriptions on one line |

The three are registered in `.gitmodules` with `ignore = dirty` (2026-10-14), so `git status` no longer lists them for these local edits; a
new commit inside one still shows. `git -C <submodule> status` shows the edits.

## Reapply after an upstream update

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff
git -C diagram-design apply --3way ../patches/diagram-design.patch
git -C skills/skill-anydoc/anydoc-github apply --3way ../../../patches/anydoc-github.patch
git -C strategy-os apply --3way ../patches/strategy-os.patch
```

Check first with `git -C <submodule> apply --check <patch>`. After changing a local edit, regenerate its patch with
`git -C <submodule> diff > patches/<name>.patch` and update the base commit here.
