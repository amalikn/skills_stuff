---
Title: Project AGENTS.md write-back line for skill-coder
Category: template
Status: current
Authority: local-supplement
Scope: The line a project adds to its AGENTS.md so its agents write programming lessons back to skill-coder
Last reviewed: 2026-10-19
Summary: Copy the block below into a project's AGENTS.md (its required-skills or working-rules section); it adds the trigger without restating the contract.
---

# Project AGENTS.md write-back line for skill-coder

Copy this into the project's `AGENTS.md`, in the section that names the skills it uses:

```markdown
- **skill-coder** (`/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-coder`): invoke it before writing, refactoring or promoting code. A session that used it, applied its
  rules or ran its helpers owes its write-back at closeout: reusable programming practice goes to skill-coder as a dated Learned entry (its `references/evolution-and-write-back.md`), a fact about
  this project stays here. Entries that could not be written there wait under `## skill-coder write-back candidates`; `write_back.py --project-root .` from the skill lists them.
```
