**Title:** Pad v0.11: open items in a pane, keep your place

**Author:** The Pad Team

**Date:** 2026-07-23

**Source:** [https://www.getpad.dev/blog/pad-v0-11-item-pane](https://www.getpad.dev/blog/pad-v0-11-item-pane)

---

# Page Structure Map
```text
Pad v0.11: open items in a pane, keep your place
├── Open an item without losing your place
├── Collections default to a Board
├── Collaboration and version history got sturdier
├── Cross-workspace access hardening (multi-user / cloud)
├── MCP and platform
└── The boring-but-important end
```

---

```
brew upgrade pad
# or
docker pull ghcr.io/perpetualsoftware/pad:0.11.0
```

Pad v0.11 is mostly one feature: a detail pane that opens items next to your list instead of navigating away from it. Around it, new collections default to a Board, real-time collaboration and version history got more robust, and a batch of cross-workspace access gaps closed. All of it ships in the same single self-hosted Go binary. No new services.

## Open an item without losing your place

Clicking a row used to be a full-page navigation. You’d land on the item, read it, hit Back, and your list would reset: scroll position gone, filters re-applied, the thread you were following lost. v0.11 replaces that with a pane.

Click a row and the item opens beside the list; the list stays exactly where it was. The pane’s `?item=` ref lives in the URL, so a paned view is shareable and survives a refresh — send someone the link and they land on the same list, same item open.

From there the pane behaves like a browser. Click a linked item, a child, a relationship, or a graph node’s Open link and the pane re-targets in place, building a back stack as it goes. You walk that stack with the in-pane Back chevron, browser Back, or a depth-aware `ESC` that pops one level at a time. A structural parent breadcrumb shows where the current item lives. `j`/`k` follows your list selection until you drill in, after which the pane detaches. Drag the divider to resize, or click the list’s dead space to collapse the pane.

The same pane mounts on the full-page item view. There, the item you started on freezes read-only while you peek at another, so you can check a dependency without tearing down its live collab session. On mobile the split collapses to a full-screen overlay with focus trapping and full ARIA-modal isolation.

## Collections default to a Board

New collections now open as a Board instead of a List: in the create modal, `pad collection create`, the MCP `collection` create, and the runtime fallback for collections with no stored setting (IDEA-2274). Existing collections keep their stored `default_view`; there’s no migration, and an explicit picker or `--default-view` choice always wins.

Because the Board default is unconditional, the few collections that don’t suit a status board are set by hand. Contacts is a seeded collection grouped by `relationship`, and the Meeting Notes, Decisions, and OKRs presets stay List. A custom collection with no `status` field still defaults to Board and shows a single `Uncategorized` lane until you switch it to List (IDEA-2287). Items with no value for the grouping field now collect in that `Uncategorized` lane instead of dropping off the Board (IDEA-2275). Board and List cards also show an abbreviated item age (`3h ago`, `5d ago`, then a short date) opposite the status, reusing the same `relativeTime()` the item header uses (IDEA-2286).

## Collaboration and version history got sturdier

Restoring an old version no longer lets a live editor silently overwrite the restored content: restore now prunes the collab op-log and reseeds every peer from the restored content, so a stale `Y.Doc` flush can’t clobber it (BUG-2264). Restore also flushes the live editor before it snapshots the undo-point version, so an in-flight edit lands in version history instead of vanishing when the op-log is pruned (BUG-2271).

Concurrent field edits now merge instead of clobbering. The web editor sends a single-key `fields_patch` with `expected_updated_at` and retries on a 409 rather than replacing the whole `fields` blob (BUG-2273); collection settings got the same optimistic-concurrency treatment (BUG-2265). Same-second versions now sort deterministically thanks to a per-item monotonic tie-breaker (BUG-2270).

## Cross-workspace access hardening (multi-user / cloud)

A batch of authorization fixes closes cross-workspace access gaps. These only surface once a workspace has more than one member, so they matter most to multi-user and Pad Cloud deployments; a single-user self-host was never exposed.

Collaborative-editing WebSocket writes now require edit permission, so a workspace viewer can join a live document and appear in presence but no longer persist changes to it (TASK-265). SSE event subscriptions check workspace membership at connect time, so a non-member can’t open a connection against another workspace’s stream — the events were already filtered, but the open connection was a slot-exhaustion and existence-oracle gap (TASK-264). Webhook and token mutations now verify both the object ID and its workspace ownership, closing cross-workspace IDOR paths (TASK-266). On the remote `/mcp` transport, an OAuth token’s consented workspace allow-list now scopes workspace-global reads like `pad_workspace list`, so a token scoped to one workspace can’t enumerate the slugs of others (BUG-2102).

## MCP and platform

Remote `/mcp`, the cloud transport, now serves the read-only resource set that used to be stdio-only: items, dashboard, collections, bootstrap, and bounded attachment images, all behind the same auth and consent perimeter as the tool dispatchers (TASK-2101). A new “unparented only” filter lands end to end: the item index and delta payloads carry an optional `is_unparented` bit (TASK-2096), and the web FilterBar exposes it as a chip that round-trips through URLs and saved views (TASK-2099).

## The boring-but-important end

Under the features, the usual round of hardening. The MCP attachment image resource got a stricter label and a 1 MiB download bound (#933). Two narrow degraded-mode races in the restore path were fenced, including reconciling a lost Postgres commit-ack as a durable commit rather than a rollback (cloud and Postgres deployments only, BUG-2276). The toolchain moved to Vite 8.1 and SvelteKit 2.70; the same change fixed a pane pop-focus regression the bump surfaced (#1001).

Upgrade with `brew upgrade pad` or pull `ghcr.io/perpetualsoftware/pad:0.11.0`. Every artifact is cosign-signed with SBOMs and SLSA provenance — see [/blog/homebrew-signed-releases](https://www.getpad.dev/blog/homebrew-signed-releases) for how to verify.
