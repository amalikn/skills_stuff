---
Title: Local source store
Category: evidence-store
Status: current
Authority: generated-evidence
Scope: Local copies of the sources both architect packs cite
Last reviewed: 2026-10-29
Summary: RFC text, PDFs and Markdown snapshots of cited pages, so references can be read offline; index.json maps each URL to its file, hash and retrieval time.
---

# Local source store

Shared by skill-network-architect (canonical) and skill-systems-architect (symlink). Filled by `just fetch-sources --apply`; never edit files here by hand.

- `index.json`: cited URL -> `path`, `kind` (rfc, pdf, web), `method` (direct or all-scraper), `sha256`, `bytes`, `retrieved` (UTC), `cited_in`.
- `rfc/rfcNNNN.txt`: RFC text from rfc-editor.org, for every RFC linked or named in either pack.
- `pdf/<host>/<slug>.pdf`: PDFs cited directly (NIST, ITU, vendor papers).
- `web/<host>/<slug>.md.txt`: Markdown snapshots of cited web pages, taken with all-scraper; a snapshot is the page as retrieved, not a maintained copy.

To find a local copy, look the URL up in `index.json` (RFCs: `rfc/rfc<number>.txt`). A snapshot shows what the page said on its `retrieved` date; recheck the live page
before relying on a value that may have changed. Copyright stays with each publisher; the copies are kept for private reference in this private repository.
