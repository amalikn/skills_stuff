# RUNBOOK

## Use When
Use this specialist when a user wants an `.eml` email thread converted into a cleaned markdown thread, or when an existing cleaned thread needs to be refreshed after the source `.eml` changes.

## Workflow
1. Inspect the source `.eml` and any existing cleaned markdown thread.
2. Decide whether the cleaned markdown should be created fresh, regenerated, or appended.
3. Extract one section per email in chronological order unless the user explicitly asks for reverse chronology.
4. Add a TOC at the top.
5. Format each email section as:
   - `## Email X - YYYYMMDD_hhmm - <summary>`
   - `Date`, `From`, `To`, `Cc`, `Subject`
   - cleaned body text
6. Convert timestamps consistently when timezone normalization is requested or already established for the project.
7. Keep names only in `From`, `To`, and `Cc` unless the user explicitly asks to keep email addresses.
8. Remove everything after the human signature block, including:
   - legal disclaimers
   - contact cards
   - inline image placeholders
   - transport / MIME clutter
9. Preserve the substance of the human-written email body; do not rewrite the message beyond formatting cleanup.
10. If the source `.eml` is newer than the cleaned markdown, reconcile the markdown before updating any downstream documentation.

## Rules
- Do not invent missing emails, dates, or attachments.
- Do not claim an attachment or earlier email is present in the cleaned markdown unless it is actually reproduced there.
- If the source thread contains earlier referenced emails not fully reproduced in the extracted markdown, say so explicitly.
- If summary wording is needed for the heading, keep it short and factual.
- If a project already has an established date/time display convention, follow it consistently.

## Validation
- Verify the cleaned markdown includes the newest email present in the source `.eml`.
- Verify TOC entries match the actual section headings.
- Verify heading timestamps match the chosen timezone convention.
- Verify names-only formatting in `From`, `To`, and `Cc` unless instructed otherwise.
- Verify obvious disclaimer / signature clutter is removed from each cleaned section.
