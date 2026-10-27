---
Title: Authority and promotion
Category: reference
Status: current
Authority: local-supplement; operator decisions 2026-10-27 (derived first, promotion by topic page, gates); handoff sections 3 and 6; design doc sections 3.3 and 4.1
Scope: Who owns which knowledge, what a derived page is, and the gated route from derived view to authoritative page to archived sources
Last reviewed: 2026-10-27
Summary: >-
  knowledge/ starts as a derived view that never outranks its sources; one category page at a time can be promoted to authoritative through four gates,
  after which an archive plan for the absorbed sources can be produced. Settles source conflicts C1 and C2.
---

# Authority and promotion

## Contents

- [Ownership](#ownership)
- [Three stages of a knowledge page](#three-stages-of-a-knowledge-page)
- [Promotion gates](#promotion-gates)
- [After promotion](#after-promotion)
- [Revocation](#revocation)
- [Settled source conflicts](#settled-source-conflicts)

## Ownership

| Component                                        | Owns                                                                               | Must not own                                                 |
| ------------------------------------------------ | ---------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| skill-knowledge-curator                          | Inventory, claim ledger, evidence checks, overlap and conflict analysis, review    | Approving a disputed fact; editing a source document or a    |
|                                                  |   cards, derived pages, promotion records, archive plans                           |   governing file; commits and pushes                         |
| The operator                                     | Every conflict decision, every promotion, every archive run                        | Nothing is decided for them by recency, length or repetition |
| Source documents and governing files             | The authority until a page covering them is promoted                               | Silent edits by the curator                                  |
|   (`AGENTS.md`, decision registers,              |                                                                                    |                                                              |
|   status files)                                  |                                                                                    |                                                              |
| skill-slurp-chat                                 | Session capture, memory writes, governed-record routing, its Step 6b               | Curation internals (it calls the curator, after the pilot)   |
|                                                  |   coverage audit                                                                   |                                                              |
| Memory backends (memory-keeper, project-context) | General session memory                                                             | Canonical curated knowledge                                  |
| skill-goal-guard                                 | MVP scope control                                                                  | Knowledge categorisation                                     |

**Authority invariant.** A claim is an indexed representation of what a source says, not new evidence. Two conflicting sources stay two claims and one open conflict until the operator decides. Recency
is evidence of time, not of authority (INV-008).

## Three stages of a knowledge page

```text
  sources (authoritative)
        |
        |  kc inventory, worksheet, claims, candidates, relate, decide
        v
  +-----------------------+   kc render         derived page: summarises its sources,
  | knowledge/<cat>.md    |------------------>  sources stay authoritative,
  | Status: derived       |                     regenerated freely
  +-----------+-----------+
              |  kc promote --approve-digest ... --apply   (all gates pass)
              v
  +-----------------------+                     promoted page: authoritative itself,
  | knowledge/<cat>.md    |                     never overwritten by render; changes
  | Status: promoted      |                     arrive as .kc/proposals/ for review
  +-----------+-----------+
              |  kc archive-plan                (v1: plan and restore rehearsal only)
              v
  sources fully absorbed by promoted pages become archive candidates
```

The promotion unit is one category page (`architecture`, `requirements`, `technical`, `governance`, `operations`), operator 2026-10-27. `history.md`, `open-issues.md` and `index.md` stay derived.

## Promotion gates

`kc promote --page knowledge/<cat>.md` evaluates the gates without writing; `--apply` with `--approve-digest` and `--reason` records the promotion only when all configured gates pass and the page
equals a fresh rendering.

| Gate                | Passes when                                                                                | Chosen by                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| `no_open_p0_p1`     | No claim on the page has an open P0 or P1 conflict                                         | operator, 2026-10-27                                                              |
| `operator_decision` | `--approve-digest` equals the SHA-256 of the page body (everything after                   | operator, 2026-10-27                                                              |
|                     |   `<!-- kc:body -->`): approval is bound to the exact text reviewed, not a generic yes     |                                                                                   |
| `governing_files`   | A file in `governing_files` (default `AGENTS.md`) names the page path, so agents read it   | operator, 2026-10-27                                                              |
|                     |   first. The curator prints the line to add; it never edits the file                       |                                                                                   |
| `evidence_verified` | Every evidence span of the page's current claims still matches its source (relocated spans | added by default after review (a source edited after render would otherwise be    |
|                     |   pass with a note)                                                                        |   promoted stale); a project may drop it in `.kc/config.yaml`                     |

Exit 4 when an open P0/P1 conflict blocks; exit 3 for any other failed gate.

## After promotion

- The page's front matter says `Status: promoted` and the banner names the promotion decision.
- `kc render` never rewrites it. A changed rendering is written to `.kc/proposals/knowledge/<cat>.md`; reviewing and promoting again adopts it.
- `kc validate` fails if the page body no longer matches the promoted digest (a hand edit outside review).
- `kc archive-plan` treats every claim on the page as absorbed. See [archive-safety.md](archive-safety.md).

## Revocation

`kc promote --page ... --revoke --reason ... --apply` appends a `revoked` promotion record naming the earlier one. The page returns to `Status: derived` on the next render. Nothing is deleted
(INV-016).

## Settled source conflicts

- **C1, authority of `knowledge/`:** derived by default, promotable per page through the gates above (operator, 2026-10-27). The handoff's "never a competing authority" holds until a page is promoted;
  the design's "curated current truth" holds after.
- **C2, archival:** plan only in v1 (operator, 2026-10-27). Sources are never moved; see [archive-safety.md](archive-safety.md).
- **C7, writes into projects:** read-only by default; `--apply` writes only `.kc/` and `knowledge/` inside the project root, never a source or governing file.
