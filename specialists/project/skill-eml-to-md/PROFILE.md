# PROFILE

## Subject
- Type: project
- Name: eml_to_md
- Slug: skill-eml-to-md

## Stable Facts
- One cleaned markdown section should correspond to one email in the thread.
- Section headings should use the pattern `Email X - YYYYMMDD_hhmm - <summary>`.
- The cleaned markdown should keep human-written body text while removing signatures, legal disclaimers, inline image placeholders, and transport clutter.
- Header fields in the cleaned markdown should show names only in `From`, `To`, and `Cc` unless the user explicitly asks to preserve addresses.
- If timezone normalization is requested or already established in the project, convert message timestamps consistently and explicitly.
