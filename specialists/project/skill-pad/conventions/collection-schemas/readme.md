---
Title: Pad collection schemas
Category: reference
Status: current
Authority: canonical
Scope: The CollectionSchema JSON files for the collections the apn workspaces add to Pad's startup template
Last reviewed: 2026-11-10
Summary: Asks, Bugs, Feature Requests and Tech Debt schemas: Pad's web templates plus section and order fields and declared closed statuses.
---

# Pad collection schemas

Use with `pad collection create "<Name>" --schema @<file> --icon <icon> --layout balanced --default-view board` (the CLI has no template flag).

| File                    | Collection       | Closed statuses (abandoned)     | Source                                                               |
| ----------------------- | ---------------- | ------------------------------- | -------------------------------------------------------------------- |
| `asks.json`             | Asks             | answered, withdrawn (withdrawn) | usage guidelines 3.1; also `--awaits-human true --tracks-work false` |
| `bugs.json`             | Bugs             | fixed, wont-fix (wont-fix)      | web template Bug Tracker, plus tracker_id, section, order            |
| `feature-requests.json` | Feature Requests | shipped, declined (declined)    | web template Feature Requests (declares none), plus section, order   |
| `tech-debt.json`        | Tech Debt        | resolved                        | web template Tech Debt (declares none), plus section, order          |

`section` and `order` let `scripts/pad_tracker.py` rebuild the Markdown tracker files exactly. Templates: [../../references/upstream/v0.19.2/web_src_lib_components_collections_collection-templates.ts](../../references/upstream/v0.19.2/web_src_lib_components_collections_collection-templates.ts).
