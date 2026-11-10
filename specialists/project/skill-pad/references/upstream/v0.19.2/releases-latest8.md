## v0.19.2 (2026-11-08)

## Highlights

v0.19.2 is v0.19.1 plus one fix: **a reference that names the wrong collection never opens a different item** (BUG-4119). A ref such as `TASK-42` used to fall back to "item number 42 in any collection" when no collection with that prefix had it, so a stale or mistyped ref, or a wiki link such as `[[TASK-42]]`, could resolve to an unrelated item and write a wrong link. A ref now resolves only through its own prefix, or through the move history of an item that left that collection.

**Behaviour change.** A ref whose prefix names no live collection and no move history no longer resolves. That includes the old refs of a collection whose prefix was only renamed, and of an item moved before the move log existed. A ref that parses as a ref but finds nothing no longer falls through to a lookup by slug, so an item whose slug itself looks like a ref (for example `IDENT-10`) is reached by its current ref, not by that slug. If a link of yours stops resolving, use the item's current ref.

**Comments** (BUG-4119). `pad item comment` reads the item's ref from the server's reply, so it works against an older server that does not return one.

**Release plumbing.** The Nix package reports 0.19.2. CI and Nix now also run on pull requests into release branches, and the Nix vulnerability scan accepts GO-2026-6911 (the mcp-go client transport, which Pad does not link), as main already does.

## Install
```
brew install PerpetualSoftware/tap/pad
docker pull ghcr.io/perpetualsoftware/pad:0.19.2
```
Archives for Linux, macOS and Windows are attached below.

## Verifying
```
cosign verify-blob \
  --certificate-identity-regexp "^https://github.com/PerpetualSoftware/pad/.github/workflows/release.yml@.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  --bundle checksums.txt.sigstore.json checksums.txt
```

---

## Changelog




## v0.19.1 (2026-11-07)

## Highlights

v0.19.1 ships the same code as v0.19.0-rc.3. The v0.19.0 tag was cut but not published, because its release build could not run.

**Behaviour change: a workspace-pinned API token now works only in its workspace** (BUG-3982). A token created for one workspace used to be accepted on other workspaces its owner could reach, and on account-wide routes. It is now refused outside its pinned workspace and on global routes, such as creating a workspace, the event stream, export and import status, and workspace tabs. It can list and revoke only tokens pinned to the same workspace. If a script or integration used a pinned token across workspaces or for account-wide calls, give it an unpinned token.

**Security updates.** Go toolchain 1.26.10 (GO-2026-6809) and golang.org/x/net v0.62.0 (GO-2026-6866, GO-2026-6860). The user read path no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019).

**Sign-in and session fixes.** A browser-approved CLI token gets its own lifetime (TASK-3975). Changing your password or 2FA keeps the session's sliding window (BUG-3978). `pad auth 2fa disable` exits non-zero when it can't save the rotated session (BUG-3882).

**Account settings keep to the signed-in account** (TASK-4129). If the signed-in account changed without a page reload while a settings action was still running (a password change, 2FA setup, a new API token, a data export, linking or unlinking a sign-in provider, or an account deletion), its result could appear under the new account, including a 2FA setup secret, recovery codes or a new token's secret. The page now drops a result that belongs to the previous account, and an account change clears its per-account form state.

**CLI and MCP correctness.** `pad item list --format json` pages to completion when `--limit` isn't set (BUG-4024). MCP numeric parameters are checked strictly on both transports: a non-number or non-integer is refused instead of being dropped or changed (BUG-4056, BUG-4061, BUG-4065, BUG-4070). `pad session list` reads "unknown" instead of "dead" across a PID namespace (BUG-4090). A relative `PAD_DATA_DIR` or `PAD_DB_PATH` now warns (BUG-4066).

**Retrying a write safely** (BUG-3999, reported by @thomasthinks in #2250). The `/pad` skill no longer says a retry is safe on its own. Each run sends a new idempotency key, so a retry is deduplicated only when both runs pass the same `--op-key`. When a write that sent a key fails or times out, the CLI now prints that key on stderr, so you can re-run with `--op-key <k>`. `--format json` output on stdout is unchanged.

**New items land on top** (BUG-4005). A new item with no parent now goes to the top of its collection's manual order. A child still goes to the end of its parent's list. Children created in the same second keep their creation order, and items seeded by a template or an app install keep their manifest order.

**2FA after an app's social sign-in** (BUG-4136, server half TASK-4137). The server can bind a 2FA challenge to the app's PKCE verifier instead of its IP address, so an app that hands social sign-in to the browser can finish the 2FA step from the app. A request without a PKCE challenge is IP-bound exactly as before, so existing clients are unchanged. The Pad mobile apps use it from their next release.

**Smaller fixes.** Inviting with an unknown role answers 400, not 500 (BUG-3861). A workspace whose owner no longer resolves never produces a `//` link (BUG-4050). Toasts with an action or link stay up about 10 seconds (TASK-3973). The new-item dialogs label their dismiss button Close, not Cancel (BUG-4004).

## Changelog
### Features
* 096bde69540751e401b1778ec6e734a8ee8aaf14: feat(apps): admin Apps toggle, paused webhook status, app-name attribution, developer docs (TASK-3980) (#2258) (@xarmian)
* e09b11cc2e33fafb36f45eb3866756770a46f44d: feat(attachments): in-app previews for text, Markdown and CSV/TSV (TASK-4074) (#2310) (@xarmian)
* 875bbaa24e973d6d9413a575d79bd7a0e18c5378: feat(attachments): sandboxed in-pane PDF viewer with page navigation (TASK-4075) (#2333) (@xarmian)
* 30fa047904ae9971661fbbbf1425790a11a27095: feat(auth): bind an app's 2FA challenge to its PKCE verifier on oauth-login (BUG-4136 2a, TASK-4137) (#2350) (@xarmian)
* fdbba1a31ea58afbd867898ae30964ba703274e8: feat(cli,mcp): pad project catch-up and pad_project action=catch-up, read-only (TASK-4035) (#2290) (@xarmian)
* 16aaaf54509b22f2c8817a7c0abc28546c43a915: feat(collections): awaits_human collection setting (TASK-3919) (#2244) (@xarmian)
* e432d0f5bcc9c8db90e83b780d317acd5b2a52e0: feat(decision): debounce decision re-asks with decision_jobs.not_before (TASK-3916) (#2230) (@xarmian)
* e598bc4f64880da0e59dccac621ac4e3d510e4da: feat(decision): effort, effort_medium and high_stakes on the attention set, staged; drain-paced backfill (TASK-3921) (#2236) (@xarmian)
* 6f8d43e2eb5bac4811929680987186f812a4c5b8: feat(metrics): signup and first-write funnel metrics; TouchUserWrite reports the first write (TASK-3926) (#2227) (@xarmian)
* dd412a022de1745bb428da7c2f8448123d3c0374: feat(needs): GET /me/needs, the cross-workspace needs-you inbox and its router (TASK-3920) (#2253) (@xarmian)
* 5aa9e49ab45a0ce714caece593ddbbade035f65e: feat(needs): importance and simplicity scorers on /me/needs (TASK-3959, part 1b) (#2273) (@xarmian)
* eb7f8a200c36b6b186afe07b2bebfa69e7361be6: feat(needs): per-user dismiss/defer storage and the needs/snooze routes (TASK-3918) (#2231) (@xarmian)
* ca184cff9632ac97551f0eda3158e61df28bdc42: feat(needs): sort=importance|simplicity with a score-keyed cursor (TASK-3959, part 2) (#2274) (@xarmian)
* 94191b2bdc3c5524b75379ff7537679b42b85d70: feat(needs): store reads for importance and simplicity scoring (TASK-3959, part 1a) (#2271) (@xarmian)
* 6cfe322461cb646978c656d16320710cfb4e21f7: feat(push): GET /me/notifications/{id} enrichment and the real-enqueue mention leg (TASK-3939 part B2b) (#2284) (@xarmian)
* 20a150064ffbd9e50d4403f52c5ec46ac28d4d17: feat(push): gateway client and notification claim lifecycle (TASK-3939, part A of 3) (#2278) (@xarmian)
* eaa1b0da16e112e79718c2291a19611da091eeed: feat(push): start the push dispatcher at server startup when a gateway is set (TASK-3939 B2c) (#2286) (@xarmian)
* 2a98237e4268670ee9b8d0d419c57f3ce7c2355a: feat(push): summary push, 30/h cap, retry matrix and expire/prune sweeps (TASK-3939 part B2a) (#2283) (@xarmian)
* dbbbefda75d4fc4aaeac7bdaecd65eab772f00a9: feat(push): the push dispatcher core and its privacy gates, not yet wired (TASK-3939, part B1) (#2280) (@xarmian)
* b1dce0eddb2beba588db9991e8b953a6b45f86a8: feat(server): log every unguarded content write the PLAN-3555 counter counts (TASK-4062) (#2301) (@xarmian)
* 9dc679e786dfd9ea2f85c004ac2c840a87b62073: feat(server): per-user catch-up digest and read cursor (TASK-3615, PR A) (#2219) (@xarmian)
* d76f06d1998f262d03461edc28558747ecfab00a: feat(server): push device registration and notification settings API (TASK-3938) (#2269) (@xarmian)
* 8204f03d25ff2e5e5bad5faec0d3ef3e9dc63f4a: feat(server): push dispatch timings are configurable, and a bad value refuses startup (TASK-3939) (#2288) (@xarmian)
* 1e9b87759e47dbf18055e57b0afcfef52d8fa475: feat(store): @mention index on comments (TASK-3917) (#2243) (@xarmian)
* 423d312b775b01f46cb997012a282544c09eb9b8: feat(store): @mentions enqueue a push notification (TASK-3946) (#2272) (@xarmian)
* 104f809e67f45afb67f34fbcc511af1ab81da32d: feat(store): enqueue push notifications at four store sites (TASK-3937 part B) (#2268) (@xarmian)
* 9af942a1697f1761c849de4c353611bb643d9000: feat(store): push notification schema and settings store (TASK-3937 part A) (#2265) (@xarmian)
* ffc11387e1b181493b16d645e6f13fd79eb39bf8: feat(verify): verification evidence tied to a revision, slice 1 (TASK-3617) (#2228) (@xarmian)
* dd93b7cbc2d80fafa62930f54f736a23e1c8654f: feat(web): Notifications section in account settings (TASK-3940) (#2276) (@xarmian)
* ed559deb4d9ea5322ff9918801e066651ca8754d: feat(web): catch-up card, Mark caught up, and See everything into Activity (TASK-3615, PR B) (#2226) (@xarmian)
* ce2ca4fcab8ba84c236743f83b9f218da7924b3a: feat(web): quick add gains Cancel and 'Add and open' buttons (TASK-3972) (#2247) (@xarmian)
* 2bacd545586633f001a07491011e55346eb5e12c: feat(web): the Needs you page at /console/needs (TASK-3923) (#2287) (@xarmian)
* 5eeca6f730c935af39a6402654dd1fa9b5983ad2: feat(web): the side pane can widen to 90% of the usable width (TASK-3971) (#2246) (@xarmian)
* bae3601a767e1c7c71c456bb3b573ce46a66dd7c: feat(web): the workspace import toasts the unique values it dropped (TASK-3842) (#2259) (@xarmian)
### Bug fixes
* 393d986ea9ece0dccf69a4a4a0ce9eee1b4f4609: fix(auth): a browser-approved CLI token gets its own lifetime (TASK-3975) (#2252) (@xarmian)
* 2655ad5d601e4d2c463357d3466f78516fbd4dd6: fix(auth): a credential-change rotation keeps the session's own sliding window (BUG-3978) (#2254) (@xarmian)
* 94c6d3cc527147cb862e91570813c50e74946c11: fix(brand): the favicon's gaps tighten to match the mark (TASK-3974) (#2248) (@xarmian)
* 7c9f29b2f3eb0e83e3e6ec22883f3e993cfb41f5: fix(ci): Go toolchain 1.26.10 (GO-2026-6809) and markdown-it 14.3.3 (TASK-4007) (#2267) (@xarmian)
* 0e051112e50a21229e5ffff9a3f18df115cb8cb0: fix(cli): 2fa disable exits non-zero when the rotated session cannot be saved (BUG-3882) (#2264) (@xarmian)
* aad3c35bdb087ff3f606d7ca9d2bfc6ddcbac78f: fix(cli): pad item list --format json pages to completion when --limit is not set (BUG-4024) (#2279) (@xarmian)
* 786406e569f05ad4084c0fa5c9d5a735161cde92: fix(cli): print the op_key of a failed write; stop claiming a re-run is safe (BUG-3999) (#2346) (@xarmian)
* a8af168304c55385699f0caa34cc375333b00612: fix(cli): session liveness reads unknown, not dead, across a PID namespace (BUG-4090) (#2328) (@xarmian)
* cba880ca1735b32b598bbba4abaa20a6e834cc21: fix(config): warn on a relative PAD_DATA_DIR / PAD_DB_PATH; anchor install-refresh's marker and config reads (BUG-4066 phase 1) (#2308) (@xarmian)
* 25153bcda56505e22d5ade92dee44cc626e97e94: fix(decision): a failure the store refuses is still counted, and an empty message is never a supersede (BUG-4022) (#2317) (@xarmian)
* b1785f895207d3ace8e7494c32970f37bfa0d996: fix(decision): retire text-derived blocked, waiting_on_external and conventions_comments; keep a pending answer on the dashboard (TASK-3915, TASK-3924) (#2229) (@xarmian)
* 6dfc43140202ef9f316b277c459c2fca794051a7: fix(deps): bump golang.org/x/net to v0.62.0 for GO-2026-6866 and GO-2026-6860 (TASK-4115) (#2331) (@xarmian)
* adbbb89a218d24e23e8b3d604219c4a4cc2ad64f: fix(links): wiki-link code-span check walks the spans once per call (BUG-3968) (#2261) (@xarmian)
* b13e84274007012ea4c7fe425092cf697cda5aae: fix(mcp): a refused tool call is audited as denied, not ok (BUG-3879) (#2222) (@xarmian)
* 0ed34ea9f7e95dc030833e40f4328e558061ce62: fix(mcp): integral numbers keep decimal notation on both transports (BUG-4056) (#2300) (@xarmian)
* 82f81ee8289195243c8216342a3dd635b08f7c59: fix(mcp): refuse a non-number for a numeric parameter instead of reading it as absent (BUG-4065) (#2306) (@xarmian)
* ba981cb4f2a67543aecded5b723104cbc1c3edbd: fix(mcp): refuse a numeric parameter that is not a whole int64 instead of changing it (BUG-4061) (#2303) (@xarmian)
* 729ae5f69c0dc3c5d59651f95c911a9b4709823d: fix(mcp): stdio applies remote's number rule before a value becomes CLI text (BUG-4070) (#2313) (@xarmian)
* 6402eb30554a3b660715ea5d31e8fdb58c8c8992: fix(mcp): stdio's item patch gives line_hint remote's rule through one shared helper (BUG-4082) (#2315) (@xarmian)
* 07215d49539fe709a2e78ba1f95ef61ef6033433: fix(plugin): session start runs nothing; presence and the arm check wait for the first use of Pad (TASK-3970) (#2249) (@xarmian)
* b039f111eb257189a47193cf269a7b096b63e9dc: fix(push): bound re-sends when the sent record fails after a gateway 'sent' (TASK-4032) (#2285) (@xarmian)
* 0a32eff2747004404992deccf7a2f41de88c1bfc: fix(scripts): install-refresh removes pad.pid only when it is provably not a live sibling's (BUG-4068) (#2311) (@xarmian)
* 3e7f9e18cf3a59737542f7ab3493128abb107d19: fix(scripts): install-refresh restarts the server logging to cfg.LogFile() (BUG-4064) (#2304) (@xarmian)
* 5035168e5c4ec68b47318afb8dd4126f7242e390: fix(security)!: a workspace-pinned API token is confined to its workspace (BUG-3982) (#2266) (@xarmian)
* a16d76f9d5a9ec42f591bda825ec5087fcd89bbb: fix(server): a typed settings member over non-object stored settings answers 400 (BUG-3976) (#2256) (@xarmian)
* d36f11cf40673ca7d54c82972a15a182040f95ef: fix(server): a workspace whose owner no longer resolves never yields a '//' path (BUG-4050) (#2334) (@xarmian)
* 164768dab87c17a105120456cfc602c1f8abbab6: fix(server): an invite with an unknown role answers 400, not 500 (BUG-3861) (#2255) (@xarmian)
* ba3a0ab69b4c0b6d01e1c2e343f62adb3e2ca8fe: fix(store): a same-user push re-register keeps the device's created_at and row (TASK-4027) (#2281) (@xarmian)
* 527fa47e0fbb9db3bada3c227f70b587d185b960: fix(store): a user read no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019) (#2275) (@xarmian)
* 9d563aaf091acda5abde99955282b2d172c9e5e4: fix(store): collection settings must be a JSON object at every write door (BUG-3985) (#2260) (@xarmian)
* d6dcc2d89b0abc6f841d807cf5a813d721972728: fix(store): decision last_error is sanitised and cut at a rune boundary (BUG-4018) (#2277) (@xarmian)
* 2b3b7f91157a6409d9b7e1a7db1776c936e681d5: fix(store): new board items land at the top of their lane; children keep appending in creation order (BUG-4005) (#2348) (@xarmian)
* d97c528d1c0824953706cf6d182ad069f8a9d8f8: fix(store): push token ownership follows a registration sequence, not updated_at (TASK-4031) (#2282) (@xarmian)
* 27bc097f5a086c36b7c91728bda0421d189e1dfd: fix(store): refuse writes to read cursors and app installs after migrate-to-pg, and classify every table (BUG-3958) (#2257) (@xarmian)
* 019dc3f5e14fcf47c4c8f814f78c9796f593ead1: fix(web): identity-fence the settings page's auth settles and reset per-identity state (TASK-4129) (#2356) (@xarmian)
* 0821f97bf4d8170eb4f27c64ac6471d58b19538b: fix(web): label the new-item dialogs' dismiss button Close, not Cancel (BUG-4004) (#2345) (@xarmian)
* 1bbca0753f213c2b18e8dd9535fa8fe7bb98deaa: fix(web): toasts with an action or link stay ~10s (TASK-3973) (#2245) (@xarmian)
### Other changes
* 94e0ab19b615ec989b3168d394a0638ba0c85daa: Merge main (b721dfb74) into release-0.19.x for v0.19.0-rc.3 (@xarmian)
* a0c7d68aa921bde31f67bd10b78ff2a46c1cb730: build(web): SvelteKit 3 + adapter-static 4 (TASK-3423 PR B) (#1835) (@xarmian)


## v0.19.0-rc.3 (2026-10-31)

## Since rc.2

**Account settings keep to the signed-in account** (TASK-4129). If the signed-in account changed without a page reload while a settings action was still running (a password change, 2FA setup, a new API token, a data export, linking or unlinking a sign-in provider, or an account deletion), its result could appear under the new account, including a 2FA setup secret, recovery codes or a new token's secret. The page now drops a result that belongs to the previous account, and an account change clears its per-account form state.

## Highlights

**Behaviour change: a workspace-pinned API token now works only in its workspace** (BUG-3982). A token created for one workspace used to be accepted on other workspaces its owner could reach, and on account-wide routes. It is now refused outside its pinned workspace and on global routes, such as creating a workspace, the event stream, export and import status, and workspace tabs. It can list and revoke only tokens pinned to the same workspace. If a script or integration used a pinned token across workspaces or for account-wide calls, give it an unpinned token.

**Security updates.** Go toolchain 1.26.10 (GO-2026-6809) and golang.org/x/net v0.62.0 (GO-2026-6866, GO-2026-6860). The user read path no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019).

**Sign-in and session fixes.** A browser-approved CLI token gets its own lifetime (TASK-3975). Changing your password or 2FA keeps the session's sliding window (BUG-3978). `pad auth 2fa disable` exits non-zero when it can't save the rotated session (BUG-3882).

**CLI and MCP correctness.** `pad item list --format json` pages to completion when `--limit` isn't set (BUG-4024). MCP numeric parameters are checked strictly on both transports: a non-number or non-integer is refused instead of being dropped or changed (BUG-4056, BUG-4061, BUG-4065, BUG-4070). `pad session list` reads "unknown" instead of "dead" across a PID namespace (BUG-4090). A relative `PAD_DATA_DIR` or `PAD_DB_PATH` now warns (BUG-4066).

**Retrying a write safely** (BUG-3999, reported by @thomasthinks in #2250). The `/pad` skill no longer says a retry is safe on its own. Each run sends a new idempotency key, so a retry is deduplicated only when both runs pass the same `--op-key`. When a write that sent a key fails or times out, the CLI now prints that key on stderr, so you can re-run with `--op-key <k>`. `--format json` output on stdout is unchanged.

**New items land on top** (BUG-4005). A new item with no parent now goes to the top of its collection's manual order. A child still goes to the end of its parent's list. Children created in the same second keep their creation order, and items seeded by a template or an app install keep their manifest order.

**2FA after an app's social sign-in** (BUG-4136, server half TASK-4137). The server can bind a 2FA challenge to the app's PKCE verifier instead of its IP address, so an app that hands social sign-in to the browser can finish the 2FA step from the app. A request without a PKCE challenge is IP-bound exactly as before, so existing clients are unchanged. The Pad mobile apps use it from their next release.

**Smaller fixes.** Inviting with an unknown role answers 400, not 500 (BUG-3861). A workspace whose owner no longer resolves never produces a `//` link (BUG-4050). Toasts with an action or link stay up about 10 seconds (TASK-3973). The new-item dialogs label their dismiss button Close, not Cancel (BUG-4004).

## Changelog
### Features
* 096bde69540751e401b1778ec6e734a8ee8aaf14: feat(apps): admin Apps toggle, paused webhook status, app-name attribution, developer docs (TASK-3980) (#2258) (@xarmian)
* e09b11cc2e33fafb36f45eb3866756770a46f44d: feat(attachments): in-app previews for text, Markdown and CSV/TSV (TASK-4074) (#2310) (@xarmian)
* 875bbaa24e973d6d9413a575d79bd7a0e18c5378: feat(attachments): sandboxed in-pane PDF viewer with page navigation (TASK-4075) (#2333) (@xarmian)
* 30fa047904ae9971661fbbbf1425790a11a27095: feat(auth): bind an app's 2FA challenge to its PKCE verifier on oauth-login (BUG-4136 2a, TASK-4137) (#2350) (@xarmian)
* fdbba1a31ea58afbd867898ae30964ba703274e8: feat(cli,mcp): pad project catch-up and pad_project action=catch-up, read-only (TASK-4035) (#2290) (@xarmian)
* 16aaaf54509b22f2c8817a7c0abc28546c43a915: feat(collections): awaits_human collection setting (TASK-3919) (#2244) (@xarmian)
* e432d0f5bcc9c8db90e83b780d317acd5b2a52e0: feat(decision): debounce decision re-asks with decision_jobs.not_before (TASK-3916) (#2230) (@xarmian)
* e598bc4f64880da0e59dccac621ac4e3d510e4da: feat(decision): effort, effort_medium and high_stakes on the attention set, staged; drain-paced backfill (TASK-3921) (#2236) (@xarmian)
* 6f8d43e2eb5bac4811929680987186f812a4c5b8: feat(metrics): signup and first-write funnel metrics; TouchUserWrite reports the first write (TASK-3926) (#2227) (@xarmian)
* dd412a022de1745bb428da7c2f8448123d3c0374: feat(needs): GET /me/needs, the cross-workspace needs-you inbox and its router (TASK-3920) (#2253) (@xarmian)
* 5aa9e49ab45a0ce714caece593ddbbade035f65e: feat(needs): importance and simplicity scorers on /me/needs (TASK-3959, part 1b) (#2273) (@xarmian)
* eb7f8a200c36b6b186afe07b2bebfa69e7361be6: feat(needs): per-user dismiss/defer storage and the needs/snooze routes (TASK-3918) (#2231) (@xarmian)
* ca184cff9632ac97551f0eda3158e61df28bdc42: feat(needs): sort=importance|simplicity with a score-keyed cursor (TASK-3959, part 2) (#2274) (@xarmian)
* 94191b2bdc3c5524b75379ff7537679b42b85d70: feat(needs): store reads for importance and simplicity scoring (TASK-3959, part 1a) (#2271) (@xarmian)
* 6cfe322461cb646978c656d16320710cfb4e21f7: feat(push): GET /me/notifications/{id} enrichment and the real-enqueue mention leg (TASK-3939 part B2b) (#2284) (@xarmian)
* 20a150064ffbd9e50d4403f52c5ec46ac28d4d17: feat(push): gateway client and notification claim lifecycle (TASK-3939, part A of 3) (#2278) (@xarmian)
* eaa1b0da16e112e79718c2291a19611da091eeed: feat(push): start the push dispatcher at server startup when a gateway is set (TASK-3939 B2c) (#2286) (@xarmian)
* 2a98237e4268670ee9b8d0d419c57f3ce7c2355a: feat(push): summary push, 30/h cap, retry matrix and expire/prune sweeps (TASK-3939 part B2a) (#2283) (@xarmian)
* dbbbefda75d4fc4aaeac7bdaecd65eab772f00a9: feat(push): the push dispatcher core and its privacy gates, not yet wired (TASK-3939, part B1) (#2280) (@xarmian)
* b1dce0eddb2beba588db9991e8b953a6b45f86a8: feat(server): log every unguarded content write the PLAN-3555 counter counts (TASK-4062) (#2301) (@xarmian)
* 9dc679e786dfd9ea2f85c004ac2c840a87b62073: feat(server): per-user catch-up digest and read cursor (TASK-3615, PR A) (#2219) (@xarmian)
* d76f06d1998f262d03461edc28558747ecfab00a: feat(server): push device registration and notification settings API (TASK-3938) (#2269) (@xarmian)
* 8204f03d25ff2e5e5bad5faec0d3ef3e9dc63f4a: feat(server): push dispatch timings are configurable, and a bad value refuses startup (TASK-3939) (#2288) (@xarmian)
* 1e9b87759e47dbf18055e57b0afcfef52d8fa475: feat(store): @mention index on comments (TASK-3917) (#2243) (@xarmian)
* 423d312b775b01f46cb997012a282544c09eb9b8: feat(store): @mentions enqueue a push notification (TASK-3946) (#2272) (@xarmian)
* 104f809e67f45afb67f34fbcc511af1ab81da32d: feat(store): enqueue push notifications at four store sites (TASK-3937 part B) (#2268) (@xarmian)
* 9af942a1697f1761c849de4c353611bb643d9000: feat(store): push notification schema and settings store (TASK-3937 part A) (#2265) (@xarmian)
* ffc11387e1b181493b16d645e6f13fd79eb39bf8: feat(verify): verification evidence tied to a revision, slice 1 (TASK-3617) (#2228) (@xarmian)
* dd93b7cbc2d80fafa62930f54f736a23e1c8654f: feat(web): Notifications section in account settings (TASK-3940) (#2276) (@xarmian)
* ed559deb4d9ea5322ff9918801e066651ca8754d: feat(web): catch-up card, Mark caught up, and See everything into Activity (TASK-3615, PR B) (#2226) (@xarmian)
* ce2ca4fcab8ba84c236743f83b9f218da7924b3a: feat(web): quick add gains Cancel and 'Add and open' buttons (TASK-3972) (#2247) (@xarmian)
* 2bacd545586633f001a07491011e55346eb5e12c: feat(web): the Needs you page at /console/needs (TASK-3923) (#2287) (@xarmian)
* 5eeca6f730c935af39a6402654dd1fa9b5983ad2: feat(web): the side pane can widen to 90% of the usable width (TASK-3971) (#2246) (@xarmian)
* bae3601a767e1c7c71c456bb3b573ce46a66dd7c: feat(web): the workspace import toasts the unique values it dropped (TASK-3842) (#2259) (@xarmian)
### Bug fixes
* 393d986ea9ece0dccf69a4a4a0ce9eee1b4f4609: fix(auth): a browser-approved CLI token gets its own lifetime (TASK-3975) (#2252) (@xarmian)
* 2655ad5d601e4d2c463357d3466f78516fbd4dd6: fix(auth): a credential-change rotation keeps the session's own sliding window (BUG-3978) (#2254) (@xarmian)
* 94c6d3cc527147cb862e91570813c50e74946c11: fix(brand): the favicon's gaps tighten to match the mark (TASK-3974) (#2248) (@xarmian)
* 7c9f29b2f3eb0e83e3e6ec22883f3e993cfb41f5: fix(ci): Go toolchain 1.26.10 (GO-2026-6809) and markdown-it 14.3.3 (TASK-4007) (#2267) (@xarmian)
* 0e051112e50a21229e5ffff9a3f18df115cb8cb0: fix(cli): 2fa disable exits non-zero when the rotated session cannot be saved (BUG-3882) (#2264) (@xarmian)
* aad3c35bdb087ff3f606d7ca9d2bfc6ddcbac78f: fix(cli): pad item list --format json pages to completion when --limit is not set (BUG-4024) (#2279) (@xarmian)
* 786406e569f05ad4084c0fa5c9d5a735161cde92: fix(cli): print the op_key of a failed write; stop claiming a re-run is safe (BUG-3999) (#2346) (@xarmian)
* a8af168304c55385699f0caa34cc375333b00612: fix(cli): session liveness reads unknown, not dead, across a PID namespace (BUG-4090) (#2328) (@xarmian)
* cba880ca1735b32b598bbba4abaa20a6e834cc21: fix(config): warn on a relative PAD_DATA_DIR / PAD_DB_PATH; anchor install-refresh's marker and config reads (BUG-4066 phase 1) (#2308) (@xarmian)
* 25153bcda56505e22d5ade92dee44cc626e97e94: fix(decision): a failure the store refuses is still counted, and an empty message is never a supersede (BUG-4022) (#2317) (@xarmian)
* b1785f895207d3ace8e7494c32970f37bfa0d996: fix(decision): retire text-derived blocked, waiting_on_external and conventions_comments; keep a pending answer on the dashboard (TASK-3915, TASK-3924) (#2229) (@xarmian)
* 6dfc43140202ef9f316b277c459c2fca794051a7: fix(deps): bump golang.org/x/net to v0.62.0 for GO-2026-6866 and GO-2026-6860 (TASK-4115) (#2331) (@xarmian)
* adbbb89a218d24e23e8b3d604219c4a4cc2ad64f: fix(links): wiki-link code-span check walks the spans once per call (BUG-3968) (#2261) (@xarmian)
* b13e84274007012ea4c7fe425092cf697cda5aae: fix(mcp): a refused tool call is audited as denied, not ok (BUG-3879) (#2222) (@xarmian)
* 0ed34ea9f7e95dc030833e40f4328e558061ce62: fix(mcp): integral numbers keep decimal notation on both transports (BUG-4056) (#2300) (@xarmian)
* 82f81ee8289195243c8216342a3dd635b08f7c59: fix(mcp): refuse a non-number for a numeric parameter instead of reading it as absent (BUG-4065) (#2306) (@xarmian)
* ba981cb4f2a67543aecded5b723104cbc1c3edbd: fix(mcp): refuse a numeric parameter that is not a whole int64 instead of changing it (BUG-4061) (#2303) (@xarmian)
* 729ae5f69c0dc3c5d59651f95c911a9b4709823d: fix(mcp): stdio applies remote's number rule before a value becomes CLI text (BUG-4070) (#2313) (@xarmian)
* 6402eb30554a3b660715ea5d31e8fdb58c8c8992: fix(mcp): stdio's item patch gives line_hint remote's rule through one shared helper (BUG-4082) (#2315) (@xarmian)
* 07215d49539fe709a2e78ba1f95ef61ef6033433: fix(plugin): session start runs nothing; presence and the arm check wait for the first use of Pad (TASK-3970) (#2249) (@xarmian)
* b039f111eb257189a47193cf269a7b096b63e9dc: fix(push): bound re-sends when the sent record fails after a gateway 'sent' (TASK-4032) (#2285) (@xarmian)
* 0a32eff2747004404992deccf7a2f41de88c1bfc: fix(scripts): install-refresh removes pad.pid only when it is provably not a live sibling's (BUG-4068) (#2311) (@xarmian)
* 3e7f9e18cf3a59737542f7ab3493128abb107d19: fix(scripts): install-refresh restarts the server logging to cfg.LogFile() (BUG-4064) (#2304) (@xarmian)
* 5035168e5c4ec68b47318afb8dd4126f7242e390: fix(security)!: a workspace-pinned API token is confined to its workspace (BUG-3982) (#2266) (@xarmian)
* a16d76f9d5a9ec42f591bda825ec5087fcd89bbb: fix(server): a typed settings member over non-object stored settings answers 400 (BUG-3976) (#2256) (@xarmian)
* d36f11cf40673ca7d54c82972a15a182040f95ef: fix(server): a workspace whose owner no longer resolves never yields a '//' path (BUG-4050) (#2334) (@xarmian)
* 164768dab87c17a105120456cfc602c1f8abbab6: fix(server): an invite with an unknown role answers 400, not 500 (BUG-3861) (#2255) (@xarmian)
* ba3a0ab69b4c0b6d01e1c2e343f62adb3e2ca8fe: fix(store): a same-user push re-register keeps the device's created_at and row (TASK-4027) (#2281) (@xarmian)
* 527fa47e0fbb9db3bada3c227f70b587d185b960: fix(store): a user read no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019) (#2275) (@xarmian)
* 9d563aaf091acda5abde99955282b2d172c9e5e4: fix(store): collection settings must be a JSON object at every write door (BUG-3985) (#2260) (@xarmian)
* d6dcc2d89b0abc6f841d807cf5a813d721972728: fix(store): decision last_error is sanitised and cut at a rune boundary (BUG-4018) (#2277) (@xarmian)
* 2b3b7f91157a6409d9b7e1a7db1776c936e681d5: fix(store): new board items land at the top of their lane; children keep appending in creation order (BUG-4005) (#2348) (@xarmian)
* d97c528d1c0824953706cf6d182ad069f8a9d8f8: fix(store): push token ownership follows a registration sequence, not updated_at (TASK-4031) (#2282) (@xarmian)
* 27bc097f5a086c36b7c91728bda0421d189e1dfd: fix(store): refuse writes to read cursors and app installs after migrate-to-pg, and classify every table (BUG-3958) (#2257) (@xarmian)
* 019dc3f5e14fcf47c4c8f814f78c9796f593ead1: fix(web): identity-fence the settings page's auth settles and reset per-identity state (TASK-4129) (#2356) (@xarmian)
* 0821f97bf4d8170eb4f27c64ac6471d58b19538b: fix(web): label the new-item dialogs' dismiss button Close, not Cancel (BUG-4004) (#2345) (@xarmian)
* 1bbca0753f213c2b18e8dd9535fa8fe7bb98deaa: fix(web): toasts with an action or link stay ~10s (TASK-3973) (#2245) (@xarmian)
### Other changes
* 94e0ab19b615ec989b3168d394a0638ba0c85daa: Merge main (b721dfb74) into release-0.19.x for v0.19.0-rc.3 (@xarmian)
* a0c7d68aa921bde31f67bd10b78ff2a46c1cb730: build(web): SvelteKit 3 + adapter-static 4 (TASK-3423 PR B) (#1835) (@xarmian)




## v0.19.0-rc.2 (2026-10-30)

## Highlights

**Behaviour change: a workspace-pinned API token now works only in its workspace** (BUG-3982). A token created for one workspace used to be accepted on other workspaces its owner could reach, and on account-wide routes. It is now refused outside its pinned workspace and on global routes, such as creating a workspace, the event stream, export and import status, and workspace tabs. It can list and revoke only tokens pinned to the same workspace. If a script or integration used a pinned token across workspaces or for account-wide calls, give it an unpinned token.

**Security updates.** Go toolchain 1.26.10 (GO-2026-6809) and golang.org/x/net v0.62.0 (GO-2026-6866, GO-2026-6860). The user read path no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019).

**Sign-in and session fixes.** A browser-approved CLI token gets its own lifetime (TASK-3975). Changing your password or 2FA keeps the session's sliding window (BUG-3978). `pad auth 2fa disable` exits non-zero when it can't save the rotated session (BUG-3882).

**CLI and MCP correctness.** `pad item list --format json` pages to completion when `--limit` isn't set (BUG-4024). MCP numeric parameters are checked strictly on both transports: a non-number or non-integer is refused instead of being dropped or changed (BUG-4056, BUG-4061, BUG-4065, BUG-4070). `pad session list` reads "unknown" instead of "dead" across a PID namespace (BUG-4090). A relative `PAD_DATA_DIR` or `PAD_DB_PATH` now warns (BUG-4066).

**Retrying a write safely** (BUG-3999, reported by @thomasthinks in #2250). The `/pad` skill no longer says a retry is safe on its own. Each run sends a new idempotency key, so a retry is deduplicated only when both runs pass the same `--op-key`. When a write that sent a key fails or times out, the CLI now prints that key on stderr, so you can re-run with `--op-key <k>`. `--format json` output on stdout is unchanged.

**New items land on top** (BUG-4005). A new item with no parent now goes to the top of its collection's manual order. A child still goes to the end of its parent's list. Children created in the same second keep their creation order, and items seeded by a template or an app install keep their manifest order.

**2FA after an app's social sign-in** (BUG-4136, server half TASK-4137). The server can bind a 2FA challenge to the app's PKCE verifier instead of its IP address, so an app that hands social sign-in to the browser can finish the 2FA step from the app. A request without a PKCE challenge is IP-bound exactly as before, so existing clients are unchanged. The Pad mobile apps use it from their next release.

**Smaller fixes.** Inviting with an unknown role answers 400, not 500 (BUG-3861). A workspace whose owner no longer resolves never produces a `//` link (BUG-4050). Toasts with an action or link stay up about 10 seconds (TASK-3973). The new-item dialogs label their dismiss button Close, not Cancel (BUG-4004).

## Changelog
### Features
* 096bde69540751e401b1778ec6e734a8ee8aaf14: feat(apps): admin Apps toggle, paused webhook status, app-name attribution, developer docs (TASK-3980) (#2258) (@xarmian)
* e09b11cc2e33fafb36f45eb3866756770a46f44d: feat(attachments): in-app previews for text, Markdown and CSV/TSV (TASK-4074) (#2310) (@xarmian)
* 875bbaa24e973d6d9413a575d79bd7a0e18c5378: feat(attachments): sandboxed in-pane PDF viewer with page navigation (TASK-4075) (#2333) (@xarmian)
* 30fa047904ae9971661fbbbf1425790a11a27095: feat(auth): bind an app's 2FA challenge to its PKCE verifier on oauth-login (BUG-4136 2a, TASK-4137) (#2350) (@xarmian)
* fdbba1a31ea58afbd867898ae30964ba703274e8: feat(cli,mcp): pad project catch-up and pad_project action=catch-up, read-only (TASK-4035) (#2290) (@xarmian)
* 16aaaf54509b22f2c8817a7c0abc28546c43a915: feat(collections): awaits_human collection setting (TASK-3919) (#2244) (@xarmian)
* e432d0f5bcc9c8db90e83b780d317acd5b2a52e0: feat(decision): debounce decision re-asks with decision_jobs.not_before (TASK-3916) (#2230) (@xarmian)
* e598bc4f64880da0e59dccac621ac4e3d510e4da: feat(decision): effort, effort_medium and high_stakes on the attention set, staged; drain-paced backfill (TASK-3921) (#2236) (@xarmian)
* 6f8d43e2eb5bac4811929680987186f812a4c5b8: feat(metrics): signup and first-write funnel metrics; TouchUserWrite reports the first write (TASK-3926) (#2227) (@xarmian)
* dd412a022de1745bb428da7c2f8448123d3c0374: feat(needs): GET /me/needs, the cross-workspace needs-you inbox and its router (TASK-3920) (#2253) (@xarmian)
* 5aa9e49ab45a0ce714caece593ddbbade035f65e: feat(needs): importance and simplicity scorers on /me/needs (TASK-3959, part 1b) (#2273) (@xarmian)
* eb7f8a200c36b6b186afe07b2bebfa69e7361be6: feat(needs): per-user dismiss/defer storage and the needs/snooze routes (TASK-3918) (#2231) (@xarmian)
* ca184cff9632ac97551f0eda3158e61df28bdc42: feat(needs): sort=importance|simplicity with a score-keyed cursor (TASK-3959, part 2) (#2274) (@xarmian)
* 94191b2bdc3c5524b75379ff7537679b42b85d70: feat(needs): store reads for importance and simplicity scoring (TASK-3959, part 1a) (#2271) (@xarmian)
* 6cfe322461cb646978c656d16320710cfb4e21f7: feat(push): GET /me/notifications/{id} enrichment and the real-enqueue mention leg (TASK-3939 part B2b) (#2284) (@xarmian)
* 20a150064ffbd9e50d4403f52c5ec46ac28d4d17: feat(push): gateway client and notification claim lifecycle (TASK-3939, part A of 3) (#2278) (@xarmian)
* eaa1b0da16e112e79718c2291a19611da091eeed: feat(push): start the push dispatcher at server startup when a gateway is set (TASK-3939 B2c) (#2286) (@xarmian)
* 2a98237e4268670ee9b8d0d419c57f3ce7c2355a: feat(push): summary push, 30/h cap, retry matrix and expire/prune sweeps (TASK-3939 part B2a) (#2283) (@xarmian)
* dbbbefda75d4fc4aaeac7bdaecd65eab772f00a9: feat(push): the push dispatcher core and its privacy gates, not yet wired (TASK-3939, part B1) (#2280) (@xarmian)
* b1dce0eddb2beba588db9991e8b953a6b45f86a8: feat(server): log every unguarded content write the PLAN-3555 counter counts (TASK-4062) (#2301) (@xarmian)
* 9dc679e786dfd9ea2f85c004ac2c840a87b62073: feat(server): per-user catch-up digest and read cursor (TASK-3615, PR A) (#2219) (@xarmian)
* d76f06d1998f262d03461edc28558747ecfab00a: feat(server): push device registration and notification settings API (TASK-3938) (#2269) (@xarmian)
* 8204f03d25ff2e5e5bad5faec0d3ef3e9dc63f4a: feat(server): push dispatch timings are configurable, and a bad value refuses startup (TASK-3939) (#2288) (@xarmian)
* 1e9b87759e47dbf18055e57b0afcfef52d8fa475: feat(store): @mention index on comments (TASK-3917) (#2243) (@xarmian)
* 423d312b775b01f46cb997012a282544c09eb9b8: feat(store): @mentions enqueue a push notification (TASK-3946) (#2272) (@xarmian)
* 104f809e67f45afb67f34fbcc511af1ab81da32d: feat(store): enqueue push notifications at four store sites (TASK-3937 part B) (#2268) (@xarmian)
* 9af942a1697f1761c849de4c353611bb643d9000: feat(store): push notification schema and settings store (TASK-3937 part A) (#2265) (@xarmian)
* ffc11387e1b181493b16d645e6f13fd79eb39bf8: feat(verify): verification evidence tied to a revision, slice 1 (TASK-3617) (#2228) (@xarmian)
* dd93b7cbc2d80fafa62930f54f736a23e1c8654f: feat(web): Notifications section in account settings (TASK-3940) (#2276) (@xarmian)
* ed559deb4d9ea5322ff9918801e066651ca8754d: feat(web): catch-up card, Mark caught up, and See everything into Activity (TASK-3615, PR B) (#2226) (@xarmian)
* ce2ca4fcab8ba84c236743f83b9f218da7924b3a: feat(web): quick add gains Cancel and 'Add and open' buttons (TASK-3972) (#2247) (@xarmian)
* 2bacd545586633f001a07491011e55346eb5e12c: feat(web): the Needs you page at /console/needs (TASK-3923) (#2287) (@xarmian)
* 5eeca6f730c935af39a6402654dd1fa9b5983ad2: feat(web): the side pane can widen to 90% of the usable width (TASK-3971) (#2246) (@xarmian)
* bae3601a767e1c7c71c456bb3b573ce46a66dd7c: feat(web): the workspace import toasts the unique values it dropped (TASK-3842) (#2259) (@xarmian)
### Bug fixes
* 393d986ea9ece0dccf69a4a4a0ce9eee1b4f4609: fix(auth): a browser-approved CLI token gets its own lifetime (TASK-3975) (#2252) (@xarmian)
* 2655ad5d601e4d2c463357d3466f78516fbd4dd6: fix(auth): a credential-change rotation keeps the session's own sliding window (BUG-3978) (#2254) (@xarmian)
* 94c6d3cc527147cb862e91570813c50e74946c11: fix(brand): the favicon's gaps tighten to match the mark (TASK-3974) (#2248) (@xarmian)
* 7c9f29b2f3eb0e83e3e6ec22883f3e993cfb41f5: fix(ci): Go toolchain 1.26.10 (GO-2026-6809) and markdown-it 14.3.3 (TASK-4007) (#2267) (@xarmian)
* 0e051112e50a21229e5ffff9a3f18df115cb8cb0: fix(cli): 2fa disable exits non-zero when the rotated session cannot be saved (BUG-3882) (#2264) (@xarmian)
* aad3c35bdb087ff3f606d7ca9d2bfc6ddcbac78f: fix(cli): pad item list --format json pages to completion when --limit is not set (BUG-4024) (#2279) (@xarmian)
* 4e121ab757b498d8b6b9d9bfa614d2db8049e3b9: fix(cli): print the op_key of a failed write; stop claiming a re-run is safe (BUG-3999) (#2346) (@xarmian)
* a8af168304c55385699f0caa34cc375333b00612: fix(cli): session liveness reads unknown, not dead, across a PID namespace (BUG-4090) (#2328) (@xarmian)
* cba880ca1735b32b598bbba4abaa20a6e834cc21: fix(config): warn on a relative PAD_DATA_DIR / PAD_DB_PATH; anchor install-refresh's marker and config reads (BUG-4066 phase 1) (#2308) (@xarmian)
* 25153bcda56505e22d5ade92dee44cc626e97e94: fix(decision): a failure the store refuses is still counted, and an empty message is never a supersede (BUG-4022) (#2317) (@xarmian)
* b1785f895207d3ace8e7494c32970f37bfa0d996: fix(decision): retire text-derived blocked, waiting_on_external and conventions_comments; keep a pending answer on the dashboard (TASK-3915, TASK-3924) (#2229) (@xarmian)
* 6dfc43140202ef9f316b277c459c2fca794051a7: fix(deps): bump golang.org/x/net to v0.62.0 for GO-2026-6866 and GO-2026-6860 (TASK-4115) (#2331) (@xarmian)
* adbbb89a218d24e23e8b3d604219c4a4cc2ad64f: fix(links): wiki-link code-span check walks the spans once per call (BUG-3968) (#2261) (@xarmian)
* b13e84274007012ea4c7fe425092cf697cda5aae: fix(mcp): a refused tool call is audited as denied, not ok (BUG-3879) (#2222) (@xarmian)
* 0ed34ea9f7e95dc030833e40f4328e558061ce62: fix(mcp): integral numbers keep decimal notation on both transports (BUG-4056) (#2300) (@xarmian)
* 82f81ee8289195243c8216342a3dd635b08f7c59: fix(mcp): refuse a non-number for a numeric parameter instead of reading it as absent (BUG-4065) (#2306) (@xarmian)
* ba981cb4f2a67543aecded5b723104cbc1c3edbd: fix(mcp): refuse a numeric parameter that is not a whole int64 instead of changing it (BUG-4061) (#2303) (@xarmian)
* 729ae5f69c0dc3c5d59651f95c911a9b4709823d: fix(mcp): stdio applies remote's number rule before a value becomes CLI text (BUG-4070) (#2313) (@xarmian)
* 6402eb30554a3b660715ea5d31e8fdb58c8c8992: fix(mcp): stdio's item patch gives line_hint remote's rule through one shared helper (BUG-4082) (#2315) (@xarmian)
* 07215d49539fe709a2e78ba1f95ef61ef6033433: fix(plugin): session start runs nothing; presence and the arm check wait for the first use of Pad (TASK-3970) (#2249) (@xarmian)
* b039f111eb257189a47193cf269a7b096b63e9dc: fix(push): bound re-sends when the sent record fails after a gateway 'sent' (TASK-4032) (#2285) (@xarmian)
* 0a32eff2747004404992deccf7a2f41de88c1bfc: fix(scripts): install-refresh removes pad.pid only when it is provably not a live sibling's (BUG-4068) (#2311) (@xarmian)
* 3e7f9e18cf3a59737542f7ab3493128abb107d19: fix(scripts): install-refresh restarts the server logging to cfg.LogFile() (BUG-4064) (#2304) (@xarmian)
* 5035168e5c4ec68b47318afb8dd4126f7242e390: fix(security)!: a workspace-pinned API token is confined to its workspace (BUG-3982) (#2266) (@xarmian)
* a16d76f9d5a9ec42f591bda825ec5087fcd89bbb: fix(server): a typed settings member over non-object stored settings answers 400 (BUG-3976) (#2256) (@xarmian)
* d36f11cf40673ca7d54c82972a15a182040f95ef: fix(server): a workspace whose owner no longer resolves never yields a '//' path (BUG-4050) (#2334) (@xarmian)
* 164768dab87c17a105120456cfc602c1f8abbab6: fix(server): an invite with an unknown role answers 400, not 500 (BUG-3861) (#2255) (@xarmian)
* ba3a0ab69b4c0b6d01e1c2e343f62adb3e2ca8fe: fix(store): a same-user push re-register keeps the device's created_at and row (TASK-4027) (#2281) (@xarmian)
* 527fa47e0fbb9db3bada3c227f70b587d185b960: fix(store): a user read no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019) (#2275) (@xarmian)
* 9d563aaf091acda5abde99955282b2d172c9e5e4: fix(store): collection settings must be a JSON object at every write door (BUG-3985) (#2260) (@xarmian)
* d6dcc2d89b0abc6f841d807cf5a813d721972728: fix(store): decision last_error is sanitised and cut at a rune boundary (BUG-4018) (#2277) (@xarmian)
* 2b3b7f91157a6409d9b7e1a7db1776c936e681d5: fix(store): new board items land at the top of their lane; children keep appending in creation order (BUG-4005) (#2348) (@xarmian)
* d97c528d1c0824953706cf6d182ad069f8a9d8f8: fix(store): push token ownership follows a registration sequence, not updated_at (TASK-4031) (#2282) (@xarmian)
* 27bc097f5a086c36b7c91728bda0421d189e1dfd: fix(store): refuse writes to read cursors and app installs after migrate-to-pg, and classify every table (BUG-3958) (#2257) (@xarmian)
* 0821f97bf4d8170eb4f27c64ac6471d58b19538b: fix(web): label the new-item dialogs' dismiss button Close, not Cancel (BUG-4004) (#2345) (@xarmian)
* 1bbca0753f213c2b18e8dd9535fa8fe7bb98deaa: fix(web): toasts with an action or link stay ~10s (TASK-3973) (#2245) (@xarmian)
### Other changes
* a0c7d68aa921bde31f67bd10b78ff2a46c1cb730: build(web): SvelteKit 3 + adapter-static 4 (TASK-3423 PR B) (#1835) (@xarmian)




## v0.19.0-rc.1 (2026-10-29)

## Highlights

**Behaviour change: a workspace-pinned API token now works only in its workspace** (BUG-3982). A token created for one workspace used to be accepted on other workspaces its owner could reach, and on account-wide routes. It is now refused outside its pinned workspace and on global routes, such as creating a workspace, the event stream, export and import status, and workspace tabs. It can list and revoke only tokens pinned to the same workspace. If a script or integration used a pinned token across workspaces or for account-wide calls, give it an unpinned token.

**Security updates.** Go toolchain 1.26.10 (GO-2026-6809) and golang.org/x/net v0.62.0 (GO-2026-6866, GO-2026-6860). The user read path no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019).

**Sign-in and session fixes.** A browser-approved CLI token gets its own lifetime (TASK-3975). Changing your password or 2FA keeps the session's sliding window (BUG-3978). `pad auth 2fa disable` exits non-zero when it can't save the rotated session (BUG-3882).

**CLI and MCP correctness.** `pad item list --format json` pages to completion when `--limit` isn't set (BUG-4024). MCP numeric parameters are checked strictly on both transports: a non-number or non-integer is refused instead of being dropped or changed (BUG-4056, BUG-4061, BUG-4065, BUG-4070). `pad session list` reads "unknown" instead of "dead" across a PID namespace (BUG-4090). A relative `PAD_DATA_DIR` or `PAD_DB_PATH` now warns (BUG-4066).

**Smaller fixes.** Inviting with an unknown role answers 400, not 500 (BUG-3861). A workspace whose owner no longer resolves never produces a `//` link (BUG-4050). Toasts with an action or link stay up about 10 seconds (TASK-3973).

## Changelog
### Features
* 096bde69540751e401b1778ec6e734a8ee8aaf14: feat(apps): admin Apps toggle, paused webhook status, app-name attribution, developer docs (TASK-3980) (#2258) (@xarmian)
* e09b11cc2e33fafb36f45eb3866756770a46f44d: feat(attachments): in-app previews for text, Markdown and CSV/TSV (TASK-4074) (#2310) (@xarmian)
* 875bbaa24e973d6d9413a575d79bd7a0e18c5378: feat(attachments): sandboxed in-pane PDF viewer with page navigation (TASK-4075) (#2333) (@xarmian)
* fdbba1a31ea58afbd867898ae30964ba703274e8: feat(cli,mcp): pad project catch-up and pad_project action=catch-up, read-only (TASK-4035) (#2290) (@xarmian)
* 16aaaf54509b22f2c8817a7c0abc28546c43a915: feat(collections): awaits_human collection setting (TASK-3919) (#2244) (@xarmian)
* e432d0f5bcc9c8db90e83b780d317acd5b2a52e0: feat(decision): debounce decision re-asks with decision_jobs.not_before (TASK-3916) (#2230) (@xarmian)
* e598bc4f64880da0e59dccac621ac4e3d510e4da: feat(decision): effort, effort_medium and high_stakes on the attention set, staged; drain-paced backfill (TASK-3921) (#2236) (@xarmian)
* 6f8d43e2eb5bac4811929680987186f812a4c5b8: feat(metrics): signup and first-write funnel metrics; TouchUserWrite reports the first write (TASK-3926) (#2227) (@xarmian)
* dd412a022de1745bb428da7c2f8448123d3c0374: feat(needs): GET /me/needs, the cross-workspace needs-you inbox and its router (TASK-3920) (#2253) (@xarmian)
* 5aa9e49ab45a0ce714caece593ddbbade035f65e: feat(needs): importance and simplicity scorers on /me/needs (TASK-3959, part 1b) (#2273) (@xarmian)
* eb7f8a200c36b6b186afe07b2bebfa69e7361be6: feat(needs): per-user dismiss/defer storage and the needs/snooze routes (TASK-3918) (#2231) (@xarmian)
* ca184cff9632ac97551f0eda3158e61df28bdc42: feat(needs): sort=importance|simplicity with a score-keyed cursor (TASK-3959, part 2) (#2274) (@xarmian)
* 94191b2bdc3c5524b75379ff7537679b42b85d70: feat(needs): store reads for importance and simplicity scoring (TASK-3959, part 1a) (#2271) (@xarmian)
* 6cfe322461cb646978c656d16320710cfb4e21f7: feat(push): GET /me/notifications/{id} enrichment and the real-enqueue mention leg (TASK-3939 part B2b) (#2284) (@xarmian)
* 20a150064ffbd9e50d4403f52c5ec46ac28d4d17: feat(push): gateway client and notification claim lifecycle (TASK-3939, part A of 3) (#2278) (@xarmian)
* eaa1b0da16e112e79718c2291a19611da091eeed: feat(push): start the push dispatcher at server startup when a gateway is set (TASK-3939 B2c) (#2286) (@xarmian)
* 2a98237e4268670ee9b8d0d419c57f3ce7c2355a: feat(push): summary push, 30/h cap, retry matrix and expire/prune sweeps (TASK-3939 part B2a) (#2283) (@xarmian)
* dbbbefda75d4fc4aaeac7bdaecd65eab772f00a9: feat(push): the push dispatcher core and its privacy gates, not yet wired (TASK-3939, part B1) (#2280) (@xarmian)
* b1dce0eddb2beba588db9991e8b953a6b45f86a8: feat(server): log every unguarded content write the PLAN-3555 counter counts (TASK-4062) (#2301) (@xarmian)
* 9dc679e786dfd9ea2f85c004ac2c840a87b62073: feat(server): per-user catch-up digest and read cursor (TASK-3615, PR A) (#2219) (@xarmian)
* d76f06d1998f262d03461edc28558747ecfab00a: feat(server): push device registration and notification settings API (TASK-3938) (#2269) (@xarmian)
* 8204f03d25ff2e5e5bad5faec0d3ef3e9dc63f4a: feat(server): push dispatch timings are configurable, and a bad value refuses startup (TASK-3939) (#2288) (@xarmian)
* 1e9b87759e47dbf18055e57b0afcfef52d8fa475: feat(store): @mention index on comments (TASK-3917) (#2243) (@xarmian)
* 423d312b775b01f46cb997012a282544c09eb9b8: feat(store): @mentions enqueue a push notification (TASK-3946) (#2272) (@xarmian)
* 104f809e67f45afb67f34fbcc511af1ab81da32d: feat(store): enqueue push notifications at four store sites (TASK-3937 part B) (#2268) (@xarmian)
* 9af942a1697f1761c849de4c353611bb643d9000: feat(store): push notification schema and settings store (TASK-3937 part A) (#2265) (@xarmian)
* ffc11387e1b181493b16d645e6f13fd79eb39bf8: feat(verify): verification evidence tied to a revision, slice 1 (TASK-3617) (#2228) (@xarmian)
* dd93b7cbc2d80fafa62930f54f736a23e1c8654f: feat(web): Notifications section in account settings (TASK-3940) (#2276) (@xarmian)
* ed559deb4d9ea5322ff9918801e066651ca8754d: feat(web): catch-up card, Mark caught up, and See everything into Activity (TASK-3615, PR B) (#2226) (@xarmian)
* ce2ca4fcab8ba84c236743f83b9f218da7924b3a: feat(web): quick add gains Cancel and 'Add and open' buttons (TASK-3972) (#2247) (@xarmian)
* 2bacd545586633f001a07491011e55346eb5e12c: feat(web): the Needs you page at /console/needs (TASK-3923) (#2287) (@xarmian)
* 5eeca6f730c935af39a6402654dd1fa9b5983ad2: feat(web): the side pane can widen to 90% of the usable width (TASK-3971) (#2246) (@xarmian)
* bae3601a767e1c7c71c456bb3b573ce46a66dd7c: feat(web): the workspace import toasts the unique values it dropped (TASK-3842) (#2259) (@xarmian)
### Bug fixes
* 393d986ea9ece0dccf69a4a4a0ce9eee1b4f4609: fix(auth): a browser-approved CLI token gets its own lifetime (TASK-3975) (#2252) (@xarmian)
* 2655ad5d601e4d2c463357d3466f78516fbd4dd6: fix(auth): a credential-change rotation keeps the session's own sliding window (BUG-3978) (#2254) (@xarmian)
* 94c6d3cc527147cb862e91570813c50e74946c11: fix(brand): the favicon's gaps tighten to match the mark (TASK-3974) (#2248) (@xarmian)
* 7c9f29b2f3eb0e83e3e6ec22883f3e993cfb41f5: fix(ci): Go toolchain 1.26.10 (GO-2026-6809) and markdown-it 14.3.3 (TASK-4007) (#2267) (@xarmian)
* 0e051112e50a21229e5ffff9a3f18df115cb8cb0: fix(cli): 2fa disable exits non-zero when the rotated session cannot be saved (BUG-3882) (#2264) (@xarmian)
* aad3c35bdb087ff3f606d7ca9d2bfc6ddcbac78f: fix(cli): pad item list --format json pages to completion when --limit is not set (BUG-4024) (#2279) (@xarmian)
* a8af168304c55385699f0caa34cc375333b00612: fix(cli): session liveness reads unknown, not dead, across a PID namespace (BUG-4090) (#2328) (@xarmian)
* cba880ca1735b32b598bbba4abaa20a6e834cc21: fix(config): warn on a relative PAD_DATA_DIR / PAD_DB_PATH; anchor install-refresh's marker and config reads (BUG-4066 phase 1) (#2308) (@xarmian)
* 25153bcda56505e22d5ade92dee44cc626e97e94: fix(decision): a failure the store refuses is still counted, and an empty message is never a supersede (BUG-4022) (#2317) (@xarmian)
* b1785f895207d3ace8e7494c32970f37bfa0d996: fix(decision): retire text-derived blocked, waiting_on_external and conventions_comments; keep a pending answer on the dashboard (TASK-3915, TASK-3924) (#2229) (@xarmian)
* 6dfc43140202ef9f316b277c459c2fca794051a7: fix(deps): bump golang.org/x/net to v0.62.0 for GO-2026-6866 and GO-2026-6860 (TASK-4115) (#2331) (@xarmian)
* adbbb89a218d24e23e8b3d604219c4a4cc2ad64f: fix(links): wiki-link code-span check walks the spans once per call (BUG-3968) (#2261) (@xarmian)
* b13e84274007012ea4c7fe425092cf697cda5aae: fix(mcp): a refused tool call is audited as denied, not ok (BUG-3879) (#2222) (@xarmian)
* 0ed34ea9f7e95dc030833e40f4328e558061ce62: fix(mcp): integral numbers keep decimal notation on both transports (BUG-4056) (#2300) (@xarmian)
* 82f81ee8289195243c8216342a3dd635b08f7c59: fix(mcp): refuse a non-number for a numeric parameter instead of reading it as absent (BUG-4065) (#2306) (@xarmian)
* ba981cb4f2a67543aecded5b723104cbc1c3edbd: fix(mcp): refuse a numeric parameter that is not a whole int64 instead of changing it (BUG-4061) (#2303) (@xarmian)
* 729ae5f69c0dc3c5d59651f95c911a9b4709823d: fix(mcp): stdio applies remote's number rule before a value becomes CLI text (BUG-4070) (#2313) (@xarmian)
* 6402eb30554a3b660715ea5d31e8fdb58c8c8992: fix(mcp): stdio's item patch gives line_hint remote's rule through one shared helper (BUG-4082) (#2315) (@xarmian)
* 07215d49539fe709a2e78ba1f95ef61ef6033433: fix(plugin): session start runs nothing; presence and the arm check wait for the first use of Pad (TASK-3970) (#2249) (@xarmian)
* b039f111eb257189a47193cf269a7b096b63e9dc: fix(push): bound re-sends when the sent record fails after a gateway 'sent' (TASK-4032) (#2285) (@xarmian)
* 0a32eff2747004404992deccf7a2f41de88c1bfc: fix(scripts): install-refresh removes pad.pid only when it is provably not a live sibling's (BUG-4068) (#2311) (@xarmian)
* 3e7f9e18cf3a59737542f7ab3493128abb107d19: fix(scripts): install-refresh restarts the server logging to cfg.LogFile() (BUG-4064) (#2304) (@xarmian)
* 5035168e5c4ec68b47318afb8dd4126f7242e390: fix(security)!: a workspace-pinned API token is confined to its workspace (BUG-3982) (#2266) (@xarmian)
* a16d76f9d5a9ec42f591bda825ec5087fcd89bbb: fix(server): a typed settings member over non-object stored settings answers 400 (BUG-3976) (#2256) (@xarmian)
* d36f11cf40673ca7d54c82972a15a182040f95ef: fix(server): a workspace whose owner no longer resolves never yields a '//' path (BUG-4050) (#2334) (@xarmian)
* 164768dab87c17a105120456cfc602c1f8abbab6: fix(server): an invite with an unknown role answers 400, not 500 (BUG-3861) (#2255) (@xarmian)
* ba3a0ab69b4c0b6d01e1c2e343f62adb3e2ca8fe: fix(store): a same-user push re-register keeps the device's created_at and row (TASK-4027) (#2281) (@xarmian)
* 527fa47e0fbb9db3bada3c227f70b587d185b960: fix(store): a user read no longer decrypts the TOTP secret; only the second-factor check does (BUG-4019) (#2275) (@xarmian)
* 9d563aaf091acda5abde99955282b2d172c9e5e4: fix(store): collection settings must be a JSON object at every write door (BUG-3985) (#2260) (@xarmian)
* d6dcc2d89b0abc6f841d807cf5a813d721972728: fix(store): decision last_error is sanitised and cut at a rune boundary (BUG-4018) (#2277) (@xarmian)
* d97c528d1c0824953706cf6d182ad069f8a9d8f8: fix(store): push token ownership follows a registration sequence, not updated_at (TASK-4031) (#2282) (@xarmian)
* 27bc097f5a086c36b7c91728bda0421d189e1dfd: fix(store): refuse writes to read cursors and app installs after migrate-to-pg, and classify every table (BUG-3958) (#2257) (@xarmian)
* 1bbca0753f213c2b18e8dd9535fa8fe7bb98deaa: fix(web): toasts with an action or link stay ~10s (TASK-3973) (#2245) (@xarmian)
### Other changes
* a0c7d68aa921bde31f67bd10b78ff2a46c1cb730: build(web): SvelteKit 3 + adapter-static 4 (TASK-3423 PR B) (#1835) (@xarmian)




## v0.18.1 (2026-10-18)

## Highlights

A patch release with three fixes.

- **Manage Billing** opens the Stripe billing portal again instead of being swallowed by the page router, and it only appears for accounts that are billed through Stripe (BUG-3897, BUG-3898, #2224).
- **Account export** stops its database reads at the export deadline instead of running past it (BUG-3632, #2223).
- **MCP:** a refused call now says why, on both the stdio and HTTP transports (BUG-3864, #2218).

## Changelog
### Bug fixes
* ed89604ad87686d993dee6b24eaf50b62efd3060: fix(mcp): a refused call names its cause on both transports (BUG-3864) (#2218) (@xarmian)
* d5177e7a1f7ea3996e7ae78960b9846b981bca52: fix(server): the account export's store reads are cancelled at its deadline (BUG-3632) (#2223) (@xarmian)
* c29519f72b98429b450953e20782a067366973ba: fix(web): Manage Billing reaches the Stripe portal, and only for a billing account (BUG-3897, BUG-3898) (#2224) (@xarmian)


## v0.18.0 (2026-10-17)

## Highlights

**1. Agents and you in the same doc.**
An agent can now change part of an item instead of rewriting the whole body: `pad item patch` takes exact old/new text, and each `old` must match once (PLAN-3578, #2055). If the item is open in someone's editor, the patch lands in the live document as a replace of only the blocks it changes, so the person typing elsewhere keeps typing and keeps their cursor (#2056, #2082). `pad item patch --undo` reverses a patch as long as its new text is still there (#2058, #2089).

**2. Library updates for built-in conventions and playbooks.**
Conventions and playbooks made from Pad's library now remember where they came from. When Pad ships a better version, the Library page badges "Update available" (your copy is unedited) or "Library changed" (you edited it), and the item pane opens a review: what the library changed, what you changed, and which settings accepting would replace (TASK-3462, #1852, #1873). From a terminal, `pad library diff <ref>` shows the same and `pad library update <ref>` takes the library's text, guarded against a concurrent edit (#1875). Copies made before this release are matched once by exact title (#1878). The playbook editor offers the same review (BUG-3852, #2209). The Library now has its own link in the sidebar's Agent section and the mobile sheet (TASK-2258, #2013).

**3. The Pad pane in Claude Code.**
The pad plugin now includes a side panel, opened with `/pad-pane`: Now, Next, Browse, Find and Activity views of your workspace, and an item view where you can set status, comment, or tell Claude to work on it (TASK-3486, #1883). If Pad isn't set up yet, the pane's Get started view offers three paths: Pad Cloud, Pad on this machine, or your own server (PLAN-3490, #1888). One plugin install gives the skills, the pane and notifications; the plugin follows stable releases (TASK-3487, #1890), and `pad init` points Claude Code users at it (TASK-3488, #1898). The pane needs Claude Code 2.1.287 or later.

**4. Reference collections.**
A collection can be marked as reference material instead of work, with "Track as work" in the collection editor, `--tracks-work=false` in the CLI, or `tracks_work` on MCP (PLAN-3535, #1996). Reference items stop counting toward parent progress, no longer block a parent from closing, and drop out of Insights, dashboard open-work counts and `pad project next`/`standup` (#2000). On a parent they are listed in their own References group (#2005). Existing Conventions and Playbooks become reference; everything else, Docs included, stays work until you change it. New template Docs collections start as reference.

**5. Board and search.**
- Needs Attention comes first on the dashboard when it has anything in it (TASK-3588, #2064).
- Set an item's priority from its card (TASK-2214, #1956).
- A parent filter on any collection, built from the parents its items actually have (TASK-2215, #1958).
- A filtered view says so: the active view's name, a one-line filter summary with Clear, and "12 of 84" counts (TASK-3592, #2072).
- The command palette has a persistent scope control, and "All" searches every workspace you can see, including ones you haven't opened yet (TASK-3604, #2085).

## Also new

**Agent writes.**
- Agent body writes are version-checked, phase 1: an unversioned write is counted and warned about (PLAN-3555, #2054).
- Idempotency keys for item create, patch writes, comments, notes, decisions, copy/move and push, so a retried request does not repeat (TASK-3585, #2062, #2065, #2068, #2070, #2071).
- `pad item context` / `pad_item action=context` / `GET /items/{ref}/context` return one brief for working an item; the skill and ship playbook load it (PLAN-3598, #2094, #2099, #2104, #2107).
- Leases default to the agent's name, `pad project next`/`ready` skip items another agent holds, and leases are held by an opaque worker id so two agents under one name don't share one (TASK-1809 #1900, TASK-3613 #2102). Remote /mcp writes are agent writes named by the client (BUG-2772, BUG-3496, #1903).
- MCP gains `pad_item` reminders/unremind and link-pr/unlink-pr, and typed field writes now work over local stdio too (TASK-3611).

**Typing is not lost.**
- Closing an item, signing out, or saving a changed body asks first when typing may not have reached the server (BUG-3556, BUG-3571, BUG-3540, TASK-3548; #2037, #2041, #2011, #2025).
- A tab that dies with unconfirmed edits offers them on the next open (TASK-3606, #2086), and restoring a kept draft applies only your changes, so a newer version is kept (TASK-3607, #2093).
- Restoring a kept draft no longer reports a false conflict when the stored body ends in a newline. A kept draft whose starting point may be missing edits the server already holds (a collaborator's, or your own that reached the server before the tab died) is not applied as a patch: the notice says why and offers Copy, so restore never duplicates text (BUG-3850, TASK-3856; #2207, #2213).
- Op-log recovery refuses an incomplete replay and sets aside the whole log on a schema rebuild; dormant op-logs compact into one snapshot (TASK-3574, TASK-3531). A peer that drops loses its caret at once, and the Live badge reflects a dead connection and catches up on reconnect (TASK-2206 #1932, TASK-2197 #1895).
- A kept draft you are looking at stays put: newer kept text from another tab cannot replace it before you choose (BUG-3863, #2215).
- Markdown round-trip fixes: `<Button>` and `Promise<T>` stay text, bold/italic/strike serialize back, `[[REF]]` from an agent is a link (BUG-3583, BUG-3582; #2057, #2052).

**Onboarding and getting started.**
- `/pad onboard` on an existing project asks where its open work lives (TODO files, GitHub issues) and offers to bring it in, after confirming (TASK-3454, #1853). Onboarding says "Agent activity detected" rather than claiming a connection (TASK-3596, #2077).
- In-app tutorials on Pad Cloud, from a first-time card and a Tutorials entry in the user menu; self-hosted instances link to getpad.dev/learn instead (TASK-3452, #1839).
- Workspace import reports what it carried, marks a partial import until its owner keeps or deletes it, and a guide walks a self-hosted workspace to Pad Cloud (TASK-3612, TASK-896; #2100, #1923). `pad workspace link <slug> --url <server>` re-points a directory to another server and keeps `.pad.toml`'s other keys (#2103).

**Collections and schema.**
- Schema edits say what they will do to existing items, and removing an option is never a silent rename (TASK-2187, TASK-2188, #1877).
- Archived collections can be listed, restored and undone; the archive confirm shows how many items it holds (TASK-2189, #1874).

**Web UI.**
- Quick capture keeps your place (TASK-3590, #2067); the mobile view sheet lists saved views and "All" (TASK-3589, #2066); list group headers get the board lane's bulk actions (TASK-2222, #2012); the dashboard's attention and plan lists are capped with a Show-all toggle (TASK-2210, #1896).
- Someone whose only access to an item is a direct share now sees it leave when it is archived, instead of keeping a live copy until they refresh (BUG-3796, #2212).
- Other people's creations are batched into one toast, and only their events count as unread (TASK-3593, #2073).
- Add Relationship offers both directions and says which way each points (TASK-2217, #1957). The playbook editor and collection dialogs keep a draft (TASK-2191, #1882).
- Search takes `include_archived` and an `is:archived` token (TASK-2864, #2001). Activity's collection and actor filters run on the server (TASK-2219, #1948). Insights buckets days in your time zone (TASK-3524, #1955).
- The sign-in pages follow your theme (TASK-3509, #1924), with the new Pad mark across the app's icons, header and link card (TASK-3514, #1926).
- One app dialog replaces native confirm/alert; the palette and quick-add are real dialogs; focus is taken, kept and returned; icon-only buttons and fields have names (TASK-2221, TASK-2235, TASK-2240, TASK-3515).
- Board lanes mount a window of cards, the item editor loads on demand, and lane reorder is one all-or-nothing request (TASK-2230, TASK-2226, TASK-3517; #1953, #1935, #1933). The server gzips responses (TASK-2225, #1934).
- Creating an API key, you choose Read only or Read and write, and the key list shows each key's access, including older keys (TASK-3866, #2216). A Rotate button on API tokens (TASK-3505, #1915). Quick-add is `c`, and one switch turns every single-key shortcut off (BUG-3465, #1851).
- `pad auth 2fa setup` and `disable` (TASK-403, #1927); the CLI sign-in page has Deny and shows what is asking (TASK-2253).

**Webhooks.**
- Owner webhooks keep per-endpoint delivery state, and 408/425/429 responses are retried (TASK-3409, #1809).


## Security / operators

- **Self-hosters who expose Pad directly (no reverse proxy) should upgrade.** /mcp middleware refusals now get the response write deadline (BUG-3834, #2199), and every non-stream response gets a rolling write deadline (BUG-3821, #2189).
- **MCP streams** (/mcp listen and SSE) keep alive, take a stream admission slot, and end when their credential does: a revoked session, PAT or OAuth token, or a deleted or disabled user ends the stream at the next check (BUG-3835 #2197, BUG-3837 #2201). Streams whose client stops reading now end instead of pinning a handler (BUG-3808 #2182, BUG-3637 #2172). A collab awareness frame's entry count is bounded by its bytes (BUG-3772, #2204).
- **History:** the History tab could return a 500 for an item with a damaged version row. Version rows now record their body hash and the walk refuses what it cannot verify (BUG-3820, #2192); version writers no longer diff text that is not valid UTF-8 (BUG-3839, #2200).
- **Import** drops duplicate scalar unique-field values and reports them instead of failing; a hand-edited archive with a composite slug collision is still refused (BUG-3825, #2194).
- **Accounts and sign-in:** two concurrent OAuth unlinks can no longer remove a user's last sign-in method (BUG-3816, #2191). An admin invitation resend revokes and re-creates in one transaction, so it cannot mint an invitation for a just-deleted workspace (BUG-3817, #2193). A password change kills outstanding reset links (BUG-3679, #2114); reset-password, register and bootstrap refuse a cross-site form (BUG-3680, #2146); the instance always keeps an active admin (BUG-3811, #2178).
- **Sharing:** a share link serves nothing once its item or collection is archived (BUG-3635, #2167); shared bodies are sanitized with the markdown allowlist and the SPA CSP restricts form-action (BUG-3669 #2145, BUG-3799 #2162).
- **CLI:** a workspace or ref string cannot re-route a request, and PAD_TOKEN is not sent to a server that only `.pad.toml` named (BUG-3645, BUG-3646, #2127). credentials.json is replaced atomically at 0600 and updated under a lock (BUG-3648, BUG-3649, #2170), including on macOS and Windows (BUG-3838, #2203).
- **Concurrency:** checks that read before a lock now re-check under it: unique_scope values, bulk move/tag, moves, legacy adoption, bulk status/priority updates (BUG-3812, BUG-3813, BUG-3665, BUG-3806, BUG-3831 #2202).
- **Network:** the outbound network policy blocks Azure WireServer (BUG-3660, #2155).
- **Releases:** release.yml smoke-starts each shipped binary and fails the release before publishing if one does not start (TASK-2035, #1980, #1983).
- **Workspaces:** a link between items is used only when both items live in the link's workspace, in every list, count, graph, progress and backlink reader (BUG-3776, #2208). A workspace slug is slugified whichever door supplies the name, including import with a name override; migrate-to-pg keeps existing slugs (BUG-3769, #2205).
- **Access changes reach live connections:** revoking access, or any access or credential change, re-checks live connections at once (#1744, #1746). A read-only OAuth token's write gets 403 insufficient_scope, and the /mcp challenge names the scope (TASK-2308, #1986).

- **Also hardened** in this cycle, listed in the full changelog: an authorization and tenancy sweep (#1723-#1743, including the outbound network policy #1738), OAuth fixes (BUG-3338, BUG-3398, BUG-3400, BUG-3678), BUG-3336, BUG-3350, BUG-3361, BUG-3768, and migration repairs (BUG-3663, BUG-3664, BUG-3751, BUG-3752).

## Behavior changes

- Lists that used to return everything (item lists, children, starred, shared collections, /changes) now return at most 1000 rows and page by cursor. Scripts calling the API directly should follow the cursor (BUG-3704, BUG-3789-3792; #2143, #2151, #2153).
- Agent body writes with no version token are counted and warned about (PLAN-3555 phase 1). A future release will refuse them.
- An OAuth or social sign-in whose provider answer has no stable account id is refused (BUG-3671, BUG-3797).
- Inviting an existing user now creates a pending invitation they accept or decline, from the web "+" menu, the invite link, or `pad workspace invitations|accept|decline`. It no longer adds them directly (BUG-2136, #1831, #1833).
- A pending invitation is accepted only while its inviter can still grant that access. If the inviter was removed, was demoted, or was restricted to some collections, the invite page says so and offers no Accept, and the invitation drops off the invitee's list (BUG-3770, #2214). Someone who is already a member and follows such a link is let in with the role they have (BUG-3870, #2217).
- `POST /api/v1/auth/tokens` refuses a `scopes` value it does not recognize, including null, `""` and `[]`, with 400. Omitting `scopes` still creates a full-access key (TASK-3866, #2216).
- Leases default to the agent's name, and `pad project next`/`ready` skip items another agent holds (TASK-1809, #1900).
- Existing Conventions and Playbooks collections become reference collections on upgrade (PLAN-3535, #1996).
- A collection schema that repeats or empties a field key or option is refused (TASK-3539, #2009); an item list filter naming no field is refused (BUG-3480, #1880).
- Quick-add moved to `c` (BUG-3465, #1851).
- On Pad Cloud, attachment storage is enforced at upload: Free 100 MB per workspace, Pro 1 GB pooled across the workspaces you own; imports and cross-workspace copies count. A refusal names the limit. Self-hosted stays unlimited (TASK-3619, BUG-3653, TASK-3625, TASK-3601; #2110, #2117, #2119, #2080).
- The workspace export download is shown only to an owner with unrestricted access (BUG-3614, #2105).
- The Claude Code plugin no longer starts an event monitor at session start; watching is opt-in (TASK-3513, #1925).


---

## Changelog
### Features
* 3631139de00089b726b98aa41ccf80cba3b71236: feat(acceptance): one Go reading of a body's acceptance criteria (PLAN-3598 slice (a)) (#2091) (@xarmian)
* 4226e8c5ef89bee2233e9b99ea76fa9e0c6cb916: feat(activity): the collection and actor filters run on the server, and the web/CLI badge says which (TASK-2219) (#1948) (@xarmian)
* 28872c24108e4d8ea54a83108c6072b7dbfff236: feat(admin): the MCP audit page names users and connections instead of truncated UUIDs (TASK-2255 C110) (#2032) (@xarmian)
* d5c2ecfe082954a7b03f5c30a52964639b1b36e3: feat(apps): 'via <App>' attribution on items, comments and history, and the members Apps section (TASK-3413, SPEC-6 U9c UI) (#1793) (@xarmian)
* ede0c22fc2824072b43de0e2f87bea6408a94c2f: feat(apps): Settings → Apps: install review, install-code handoff, and lifecycle controls (TASK-3413, SPEC-6 U9a) (#1785) (@xarmian)
* 37066f97bebe713d170a6c3436aa12de94232a86: feat(apps): app attachment routes: item-scoped upload, metadata, and a streamed download re-admitted before its first byte (TASK-3401, SPEC-6 U6c) (#1776) (@xarmian)
* 213ecc0fe315a610ad74f1295b3241353c1b6c2b: feat(apps): app install lifecycle: two-phase disable and rotate, re-enable, uninstall with the tombstone (TASK-3397, SPEC-6 U8c) (#1775) (@xarmian)
* 52dc41b96a5a6c382bcb1fd5c9f5ec66faa535ec: feat(apps): app install provisioning, install codes and redeem (TASK-3397, SPEC-6 U8b) (#1772) (@xarmian)
* ca158c22d8dfe942e327dc2accc163cbf6dcc7fb: feat(apps): app install staging: apps/1 manifest, fetch policy, pending reservations, preview (TASK-3397, U8a) (#1770) (@xarmian)
* 82c45f24cd468fa4e36537db8e641b815dd5e501: feat(apps): app item actions and context codes (TASK-3414, SPEC-6 U11) (#1784) (@xarmian)
* bec344822a5386b9db2643d1ee7d916dfea42227: feat(apps): app upgrade: staged preview with a classed diff, one-transaction confirm that re-derives it (TASK-3397, SPEC-6 U8b2) (#1777) (@xarmian)
* 68e306c76c0b8d84d147a803571a2453834c32fe: feat(apps): app webhook delivery behind an in-flight fence, signature v2 (TASK-3408, SPEC-6 U10b) (#1780) (@xarmian)
* e87ace01e0e3d19f927b386df4a0642cc9c90c20: feat(apps): app webhook events name the install that wrote them (TASK-3411, SPEC-6 U10d) (#1781) (@xarmian)
* 5e2accd17964e9daab594a0a4a75da2de460d1b4: feat(apps): app write routes: items create/update, comments create/update/delete, the write rule, SSE and watch parity (TASK-3401, SPEC-6 U6b) (#1773) (@xarmian)
* aadf3c09d6b2a623d223e4d8cbd5028a67fc8c17: feat(apps): app-owned webhooks, held until redeem hands out the secret (TASK-3408, SPEC-6 U10a) (#1778) (@xarmian)
* 41be1bf1138401334846d3966d1091865e5923a4: feat(apps): human-facing JSON names the app that wrote an item, comment or version (TASK-3413, SPEC-6 U9c) (#1787) (@xarmian)
* 8b8124ab5c972bc967c955e2700b3128c31049bc: feat(apps): item-pane link-out for installed apps' item actions (TASK-3413, SPEC-6 U9d) (#1794) (@xarmian)
* be5457595442f2e1b54d0ee2c7de8499f737ca81: feat(apps): per-endpoint webhook delivery state, a per-install rate cap, and a 24 h drop (TASK-3408, SPEC-6 U10c) (#1783) (@xarmian)
* b0dc7d51e527587e6719b9c8824a8835cfc0d6a6: feat(apps): the app API admits a person's delegated token (TASK-3399, SPEC-6 U5b-2) (#1782) (@xarmian)
* 282a42f69f920cdce5f3111a93ec6fd2b2fa1540: feat(apps): the installed-app API door, ceiling and read routes (TASK-3401, SPEC-6 U6a) (#1771) (@xarmian)
* 9ae4a0be45bf270e51ad3fc23a3bd7a96977987c: feat(apps): upgrade review and draft activation in Settings → Apps (TASK-3413, SPEC-6 U9b) (#1789) (@xarmian)
* 85c49cf2fdc6537c05c9842bee27f4a60288438f: feat(appstore): FencedTx, the appstore skeleton, and the boundary and write-capture guards (TASK-3388) (#1764) (@xarmian)
* 526001c199f8b14cdff4d7f6eec174c2a0de8946: feat(appstore): app attachment upload, read rule and caps behind FencedTx (TASK-3396, U7a) (#1768) (@xarmian)
* 35e4843772e2c0a7f35ae07a9f4ed9653a8b371f: feat(appstore): app comment create, edit and delete inside FencedTx (TASK-3391) (#1767) (@xarmian)
* a17e2c415ebf7ac78d77d7696b481b96c7914cdf: feat(appstore): app item create and field update inside the fence (TASK-3390) (#1765) (@xarmian)
* 55db86f68e5e7d9e7641ead86e5faf546fa26cec: feat(auth): Deny and request context on the CLI sign-in approval page (TASK-2253) (#1943) (@xarmian)
* 70c57f82029937fc703856bbc32f7c34ff4f9467: feat(auth): a first Cloud signup lands in its new workspace; OAuth comes first (TASK-3595) (#2075) (@xarmian)
* cc85c2f9da8dca6d78705974066c6950f3baca2d: feat(auth): social claim of a never-verified account, provider subjects, cloud-only sidecar routes (TASK-3351) (#1760) (@xarmian)
* b572f0739ca563c9ec6d302fcd8661e23f914e4b: feat(auth): the bot principal for installed apps: users.kind, kind gates on every sign-in door and credential, people-only counts (TASK-3392) (#1766) (@xarmian)
* d6a45bf339ee868029a9f416cd1acbfbe618468e: feat(billing): billing availability and prices come from the sidecar; PAD_BILLING=auto|off (TASK-3577) (#2048) (@xarmian)
* f3f90d0366d6532e625c09c706f65f64438142e3: feat(billing): the billing page says what Pro covers and who pays (TASK-3603) (#2084) (@xarmian)
* e8d680b135be7fcb5514f1aee80d9b6ed7e7cca1: feat(brand): the Pad mark is the brand: one vector master, the app's icons, header and link card from it (TASK-3514) (#1926) (@xarmian)
* d15b31077a1730c4954d14579406149dff7151e7: feat(chatgpt): a reset-and-verify script for the reviewer's demo workspace (TASK-3321 G8) (#1718) (@xarmian)
* 1339916b9c10e76761a44bf98adf22389e8be8e3: feat(chatgpt): serve OpenAI's domain challenge at /.well-known/openai-apps-challenge (TASK-3321 G4) (#1717) (@xarmian)
* 809d497399a165ae7ca0cab45b3b631d267b09f4: feat(chatgpt): the Pad plugin package for OpenAI's plugin directory (TASK-3321 U4) (#1712) (@xarmian)
* a55d15dbea4aa8674bf79fff914f5c40b0336e05: feat(ci): an advisory dependency-age check (cmd/depages) (TASK-1391) (#2014) (@xarmian)
* a896edf067dd22dce11fca519475e0c522dc8973: feat(cli): pad auth 2fa setup and disable; disable asks for the password, or a code on an account without one (TASK-403) (#1927) (@xarmian)
* 1d4f0606d9a990f3b78f28813e076a6ab71f8fbb: feat(cli): pad init points Claude Code users at the pad plugin (TASK-3488) (#1898) (@xarmian)
* 99aac1687bc75ad583455b83595db017a352d632: feat(cli): pad library diff and pad library update for built-in conventions and playbooks (TASK-3462 U3c) (#1875) (@xarmian)
* fbba819eb8d888a00134c8132c92f1f3c73a0032: feat(cli,mcp): pad item context and pad_item action=context (PLAN-3598 slice (c)) (#2099) (@xarmian)
* 8eebefde57cc3a319491d4e7cd5f5a6dcd1ed9ca: feat(cloud): GET /admin/billing-users pages the users the reconcile sweep re-syncs (TASK-3564, pad half) (#2042) (@xarmian)
* 3201342d3d68c134a22f1bdb993b48fb36612bce: feat(cloud): a Stripe event marker is a claim with a lease, so a handler that dies does not lose the event (BUG-3561, pad half) (#2043) (@xarmian)
* 772c1a86ba1c949a17e33049381f0e4fff54fe8b: feat(cloud): the Stripe customer link is compare-and-set, and readable by user (TASK-3549) (#2027) (@xarmian)
* bc3e23d55a8a766c281ba603ba35ce7de1623cfc: feat(collab): a patch to an item open in an editor applies as a narrowed replace (PLAN-3578 step 2) (#2056) (@xarmian)
* f67861218460b734b0085634823a100a89225da7: feat(collab): a peer that drops without saying goodbye loses its caret at once (TASK-2206) (#1932) (@xarmian)
* 1a803893414fe123dab1b9fcb3faaddab6d7481d: feat(collab): compact a dormant op-log into one Yjs snapshot (TASK-3531 U1+U2) (#1984) (@xarmian)
* 4f6d087232eac5e2fe96d5c749cd942651e0d6bd: feat(collab): count and log watermark stamps that cover content-bearing rows (TASK-3541 step 0) (#2023) (@xarmian)
* 3e8bf36f3d9cfa82cc8ddd9abf0e25eb2625f19a: feat(collab): count failed op-log appends (TASK-3574) (#2051) (@xarmian)
* 9a99f06c874c55b9184135114cc2475a01fee001: feat(collab): count resumes and force_refresh on resume, to measure offline editing (TASK-3501) (#1908) (@xarmian)
* 23c8e4f811be35385a33b2f322e5db9cc24c9ab0: feat(collab): the GC compacts dormant op-logs and a covered resume merges (TASK-3531 U3-U5) (#1985) (@xarmian)
* 4532eecffdeac4eeff1cd159ff1353df1ccac07b: feat(decision): conventions ask about the item without its comment trail, 12 questions a call (TASK-3119 U2a) (#1871) (@xarmian)
* deec62235ed433677818db2ec09773b1c7b12ff1: feat(decision): executable conventions, the server half (TASK-3119 U1a) (#1859) (@xarmian)
* cc1aa6902c6e75febf688096217be7d30c2b2510: feat(decision): log each evaluation's spend (TASK-3119) (#1861) (@xarmian)
* 8eb4519fe7c4678e1e6af2f55beef0d197ffd28b: feat(editor): a tab that dies with unconfirmed edits offers them on the next open (TASK-3606) (#2086) (@xarmian)
* d94a38978f2b1cca3379626291ff0cfabd8649e5: feat(import): a bundle import reports what it carried next to what arrived, and a guide walks a self-hosted workspace to Pad Cloud (TASK-3612) (#2100) (@xarmian)
* 136fac66098e7a3ff5f99e54995caf09dae1f07c: feat(import): a partly imported workspace is marked until its owner keeps or deletes it (TASK-896) (#1923) (@xarmian)
* 82395bde1cb7436bad7695c0594002b953817ba8: feat(import): mark rows a workspace import wrote, author not verified (BUG-3379) (#1755) (@xarmian)
* 0929f6570558b4c57148a0f0bb3fabfd15089677: feat(invitations): a mailbox-only proof on invitation emails verifies the invitee (TASK-3352) (#1757) (@xarmian)
* bc329fb7f47d70094f2963a90dbee89ccf52736b: feat(items): agent body writes are version-checked by default, phase 1: count, warn, replace (PLAN-3555) (#2054) (@xarmian)
* 0cc033edd889544c9d5cafbac45f4761ba96d63f: feat(items): content-anchored patch writes on an item with no live editor (PLAN-3578 step 1) (#2055) (@xarmian)
* 493498c977b986faf4258b4b42118b19d2385929: feat(items): idempotency keys for comments, notes and decisions; idempotency_target_gone is structured (TASK-3585) (#2068) (@xarmian)
* a05197c795d9602c3d9f6156df696fb575d243a5: feat(items): idempotency keys for cross-workspace copy and move (TASK-3585) (#2070) (@xarmian)
* c46ecc4cf865a345bc10c08aac7ffa2c297d7e3f: feat(items): idempotency keys for item create (TASK-3585) (#2065) (@xarmian)
* 7ec0191d450f229ea26b2d66b5a86d0d1b74b7b3: feat(items): idempotency keys for patch writes (TASK-3585) (#2062) (@xarmian)
* 78729db1a9b132e5554e67a1b3c8399003ee6a77: feat(items): pad item patch --undo, anchored on each edit's context (PLAN-3578 step 3) (#2058) (@xarmian)
* 43d7e050427638ef205921605a2caf1b1b0cdc6d: feat(items): restoring a kept draft applies only your changes, so a newer version is kept (TASK-3607) (#2093) (@xarmian)
* a6f96107f42b1123da3e442547ba4926a58f529c: feat(lease): an opaque worker id holds item leases, so two agents under one name do not share one (TASK-3613) (#2102) (@xarmian)
* 2dc5ac7058efb6ae0ff476ad46dddaa06259a9de: feat(mcp): ChatGPT item_history names who made each change; email-shaped names are masked (TASK-3321) (#1716) (@xarmian)
* d3b1209d04b9f0cee0cb8590115e5ab6e1a54a16: feat(mcp): ChatGPT responses are minimized through per-tool allow-lists (TASK-3321 U3) (#1713) (@xarmian)
* 26fd8a6a46a6eecc1f1dbc90a475307b2f033489: feat(mcp): ChatGPT tools declare their OAuth scope; a missing scope answers the sign-in challenge (TASK-3321 U2c) (#1720) (@xarmian)
* 0b0398b2c08ad63e0ddb8bce0d2b4b633ec4aef1: feat(mcp): count admitted MCP requests by method and client (TASK-2307) (#2003) (@xarmian)
* 6118f7065c43c61253fbe2a7b8cfb8eb5b36a023: feat(mcp): mount the ChatGPT catalog at /mcp/chatgpt, OAuth-only, off by default (TASK-3321 U2b) (#1719) (@xarmian)
* 1204a31a73950bf2bfbadda651e5e79333a03814: feat(mcp): pad_item link-pr links a PR from supplied metadata, and unlink-pr removes it (TASK-3611) (#2098) (@xarmian)
* bcb8d93516b71be3df7cb83780a1d1047b076377: feat(mcp): pad_item reminders lists an item's reminders and unremind disarms one (TASK-3611) (#2097) (@xarmian)
* 0c0874dc10f0c7e926983ceef0f089de428cd66e: feat(mcp): pad_item.history rows name who made the change (ToolSurface 0.63) (#1714) (@xarmian)
* eb987af709253d3d349921edcf1172baca02d07a: feat(mcp): pad_workspace destructive + open-world (invite emails), pad_playbook open-world (TASK-3321 U0b, ToolSurface 0.61) (#1707) (@xarmian)
* 58be45b35e97c8e615fc7948470c58f1d5f66e42: feat(mcp): remote /mcp writes are agent writes named by clientInfo; refused claims say lease_held (BUG-2772, BUG-3496) (#1903) (@xarmian)
* add4b624bdbb8e318ab7c2d57ea107cf2d3e7d22: feat(mcp): scope in the /mcp challenge, and a 403 insufficient_scope for read-only OAuth writes (TASK-2308) (#1986) (@xarmian)
* f2a1ca75e32b665c9ab069ce2c87dd6fb7b2a001: feat(mcp): structured and typed field values write over local stdio too (TASK-3611) (#2096) (@xarmian)
* 39a52595518cbeb1852f0b9eaf5a0b89a0393618: feat(mcp): the ChatGPT catalog, a one-tool-per-operation projection of /mcp (TASK-3321 U1, stacked on #1707) (#1708) (@xarmian)
* ed7219e2e72c12030f75e14fd860c7354ad00b5b: feat(oauth): RFC 9207 iss on every authorize redirect; JSON 404 for unowned /.well-known (TASK-3321 U0a) (#1706) (@xarmian)
* 5c53aae306fc61fbb283dbfa24afa1bac20c22c4: feat(oauth): a second canonical resource, with every token bound to one (TASK-3321 U2a) (#1715) (@xarmian)
* 681780486f42c7830b98955f4b32f2a2dcd23a4f: feat(oauth): count and log requests that omit the RFC 8707 resource (TASK-3363 phase 1) (#1748) (@xarmian)
* 7396ec42bbdfd5902ada9b202a983ff8f4059209: feat(oauth): delegated sign-in for installed apps through the issuance barrier, shipped closed (TASK-3399, SPEC-6 U5b-1) (#1779) (@xarmian)
* e5262160e115ac39258a9c622e819055234d0e2b: feat(oauth): install clients, service tokens and the issuance barrier for installed apps (TASK-3394, SPEC-6 U5a) (#1769) (@xarmian)
* 6066d42115b77b030c7dd2c3523ad18975cc3681: feat(outbox): freeze an app-projection block into item and comment events (TASK-3389) (#1763) (@xarmian)
* 5c598a18d3de5f72745787156248791cd2a3a4c5: feat(plugin): no event monitor at session start; an opted-in session's watch starts from the mod, and an unarmed one shows nothing (TASK-3513) (#1925) (@xarmian)
* b66af1e624c7736f92b62ea633bb57cc60263a56: feat(plugin): the Pad pane ships in the pad plugin (/pad-pane) (TASK-3486) (#1883) (@xarmian)
* 09135d15c557626b937905e70550008bbb92a433: feat(plugin): the pane's Get started view: Pad Cloud, this machine, or your own server (PLAN-3490) (#1888) (@xarmian)
* ccd915f1cc45f02395d0c7ca2a6111d296eef635: feat(push): idempotency keys for push, and the monitor drops a re-published push (TASK-3585) (#2071) (@xarmian)
* 0bdf539455e88dbcb26af4a3fdae16b592f4b0a7: feat(release): the Claude Code plugin follows stable releases; the release workflow pins the marketplace (TASK-3487) (#1890) (@xarmian)
* 480c5d351a229d8e8d7f1a20d5a255c1859931e5: feat(report): Insights buckets days in the viewer's time zone (TASK-3524) (#1955) (@xarmian)
* f61a07fe9ade952f4c9c296d8dc4e76488b054c9: feat(search): include_archived on /search, and an is:archived search token (TASK-2864) (#2001) (@xarmian)
* aa7bdd4f15ae6b4bfe84587ed4c77e9216373737: feat(server): GET /items/{ref}/context, one deterministic brief for working an item (PLAN-3598 slice (b)) (#2094) (@xarmian)
* 5c9c650ac39f04e6e7d219f036689bd09016378e: feat(server): a read-scoped token may run a playbook (TASK-2863) (#1987) (@xarmian)
* 56922e790a9fb3f0a2d9f4b139fd497816c1764f: feat(server): every access and credential change re-checks live connections (#1746) (@xarmian)
* 95046c9b3b519dca517444d5916c32ba5ebe90b2: feat(server): gzip what the client accepts, except streams, upgrades, ranges and secrets (TASK-2225) (#1934) (@xarmian)
* 560ab27b337edc69b569462655ff09c0c8000c38: feat(server): reference items stop counting as open work (PLAN-3535 PR 2) (#2000) (@xarmian)
* 484ca668a38c138e1a68130b37fef372c303450f: feat(server): revoking access re-checks live connections immediately (#1744) (@xarmian)
* 312a73c39a678dd12bc6f2490a99c89247f76cc5: feat(server): the health probe gets its own per-address rate-limit tier, and the search burst is 30 (TASK-3620 PR B) (#2108) (@xarmian)
* 559d9d1422e1d88ffb08860ce12f80b30be7a34c: feat(server): the item brief carries only the decisions Pad would surface, and counts the rest (TASK-3618) (#2107) (@xarmian)
* ff6d280bccc46d4ec1889395471175c37953cb40: feat(skill): the skill and the ship playbook load an item's brief with pad item context (PLAN-3598 slice (d)) (#2104) (@xarmian)
* aa49db396ee34bd7c5c64ecd632b8b2c31a01225: feat(storage): enforce plan storage limits at upload; Pro 1 GB pooled per account, Free 100 MB (TASK-3619) (#2110) (@xarmian)
* dab3acd1f1852b2cf882f735169eff8e79cb5a20: feat(store): a read-only diagnostic counts version tie groups migration 054 may have misordered (BUG-3751) (#2136) (@xarmian)
* bdea49af64bc208597c098daab02ca9d4c569f76: feat(store): copy a convention's role field into its role column at startup (PLAN-3598) (#2092) (@xarmian)
* 10f722e9fed443be9318a2bbe37518c541d2eff9: feat(web): "Possibly breaks CONVE-N" chips on the item page (TASK-3119 U1b) (#1860) (@xarmian)
* b831e9fe097e52d82c3c21cdccb9f41ae06da498: feat(web): + badge, Decline, and an accept/decline card on invitation links (BUG-2136 U2) (#1833) (@xarmian)
* d0ee9afaef78797030ec253e8cc983f32216722e: feat(web): Add Relationship offers both directions and says which way each points (TASK-2217) (#1957) (@xarmian)
* 697ce2d4495718c9650c9a493941d46935ab3351: feat(web): Needs Attention comes first on the dashboard when it has anything (TASK-3588) (#2064) (@xarmian)
* c78037adbf4a6f56334fd442a322af42509de667: feat(web): a Library link in the sidebar's Agent section and the mobile sheet (TASK-2258) (#2013) (@xarmian)
* fac299d9db87b91c27bd722c32cfd0c8eb052057: feat(web): a Rotate button on API tokens (TASK-3505) (#1915) (@xarmian)
* edb20ae6134ae24c709b8b6f36fb651245439100: feat(web): a filtered collection view says it is filtered (TASK-3592) (#2072) (@xarmian)
* 8efce995d9895095f7e0779226a95ad1a422dc34: feat(web): a parent filter on any collection, from the parents its items have (TASK-2215) (#1958) (@xarmian)
* 910a1aeb8d8d6f3fbdec954b963b5857f9403848: feat(web): batch other actors' creation toasts; only their events count as unread (TASK-3593) (#2073) (@xarmian)
* 6735b43450ab9386a265ff012d5afec6553c36b4: feat(web): cap the dashboard's attention and plan lists, with a Show-all toggle (TASK-2210) (#1896) (@xarmian)
* b901ec629cc73d192feec05f13c8a6488d61e648: feat(web): choose an API key's access when creating it, and see every key's access (TASK-3866) (#2216) (@xarmian)
* 6903eeeea5ee31c9baefc1b793a0ec973b822a70: feat(web): choose monthly or annual Pad Pro at checkout (TASK-3468) (#1856) (@xarmian)
* 4ac7f16084798348ed3b0cf2b977cfba47d70851: feat(web): gapped sort keys, so a reorder is one write (TASK-3525) (#1975) (@xarmian)
* 77b2c256fd719bac528e92dcb6f0109fc83864fb: feat(web): list group headers get the board lane's bulk actions (TASK-2222) (#2012) (@xarmian)
* c62b2b80da675e4e7b7fe27f867b285036348d57: feat(web): quick capture keeps your place (TASK-3590) (#2067) (@xarmian)
* 88a26afde03d550e0d410c41c82966ca0fe47ea9: feat(web): reference children are listed apart and leave progress (PLAN-3535 PR 3) (#2005) (@xarmian)
* 28501155b1b67b088af81a236e8b869f1111e1c0: feat(web): review and accept built-in updates from the Library page and the item pane (TASK-3462 U3b) (#1873) (@xarmian)
* b034236eb3dd77ef556bd1d07a27e7a6585190ca: feat(web): set an item's priority from its card (TASK-2214) (#1956) (@xarmian)
* 439bda2278fb22438a7f4682fe336f6e9fd15d64: feat(web): the auth pages follow the theme, with a toggle that survives sign-in, the Pad grid mark and a slim self-hosted header (TASK-3509) (#1924) (@xarmian)
* ebb293627230243934ebfc259c0eacfc654b23ed: feat(web): the mobile view sheet lists saved views and "All" (TASK-3589) (#2066) (@xarmian)
* 1ed71b0ecfa5cdd2a7d37637f1fc2d5ff571f878: feat(web): the playbook editor and collection dialogs keep a draft; Save stays; the arguments section is edited in place (TASK-2191) (#1882) (@xarmian)
* f6938b33a5d9aa5a68f61db127784afef7f55f2b: feat(webhooks): owner webhooks keep per-endpoint delivery state; 408/425/429 are retried (TASK-3409) (#1809) (@xarmian)
* f5a00d5b13da8855de7941d7356145c15b151766: feat: a collection can be reference material, not work (PLAN-3535 PR 1) (#1996) (@xarmian)
* cff306e05add177205a64ebcf2ddd940214ede50: feat: a plan-limit refusal is a persistent prompt that names the limit and who can lift it (TASK-3601) (#2080) (@xarmian)
* 9d2572eb7ba6f51a99be88743adde857c7f35730: feat: adopt pre-origin conventions and playbooks as built-ins, once, by exact title (TASK-3462 U4) (#1878) (@xarmian)
* 15c9f76366fc03bfbb03c8ddaff432cdaf4789c5: feat: archived collections can be listed, restored and undone; the archive confirm shows the count (TASK-2189) (#1874) (@xarmian)
* a23edba8561a4c0f25c9da231dd6b9a8f7484de5: feat: built-in update count in the bootstrap, and accepted updates record replaced fields (TASK-3462 U3a) (#1868) (@xarmian)
* c17865462f1568130861e9176dbb1a251d6551c0: feat: built-ins record their origin; an item made from one can be offered Pad's current text (TASK-3462 U1+U2) (#1852) (@xarmian)
* 5adbe0479739a694087b25d67a353f6b3e305adb: feat: bulk sort_order: one all-or-nothing request per lane reorder, one activity row per item collapsed per batch (TASK-3517) (#1933) (@xarmian)
* 79922d4bab09afa0d51b3a94d6a5e7fce0ee84bd: feat: conventions checked on each comment alone, with the chip on its card (TASK-3119 U2b) (#1872) (@xarmian)
* bc2a982591517708ac75b137486a11387f249a84: feat: every content change through the ChatGPT door is versioned first (TASK-3321 U1b) (#1711) (@xarmian)
* 4fdc6ed625758d73006dd0f4f04e1586d9351a2c: feat: in-app tutorials on Pad Cloud, links to getpad.dev/learn elsewhere (TASK-3452) (#1839) (@xarmian)
* 8d02818fd68825d241cd841a1b5731c063453e78: feat: leases default to the agent's name, and next/ready leave out others' leased items (TASK-1809) (#1900) (@xarmian)
* 1c23a1bcbcb911f58ce6b21189af36a34cacd073: feat: onboarding asks where an existing project's open work lives and offers to bring it in (TASK-3454) (#1853) (@xarmian)
* 3ffe879dee0ed3ffb36846f100047fe35b254590: feat: predictable palette search scope; "All" searches every workspace you can see (TASK-3604) (#2085) (@xarmian)
* 7b68125a30d811746fa71604ef65d03bb255ed72: feat: schema edits say what they do to items; removing an option is never a rename (TASK-2188, TASK-2187) (#1877) (@xarmian)
### Bug fixes
* 3bcef0e04da3d1f7e0aa91c32149edd5ee953c63: fix(access): system collections are ordinary collections for restricted members (TASK-3376) (#1756) (@xarmian)
* 3d21213b5781d5e19597e42698b661f19363b4c1: fix(account): account deletion needs an interactive, recently signed-in session (BUG-3336) (#1733) (@xarmian)
* ff9b9f3579a58f42fa9190d734382d74027d8e23: fix(account): account export reads run inside the deadline, from one snapshot per workspace (BUG-3659) (#2160) (@xarmian)
* 3a49a849081c0f3895046a804ce0df6da5b3d690: fix(activity): the feed and dashboard count only rows the caller may see (BUG-3687) (#2169) (@xarmian)
* 18000593688e2201e7c7399369d24f828f85f12a: fix(admin): the instance always keeps an active admin; demote, disable and self-delete share one locked guard (BUG-3811) (#2178) (@xarmian)
* 9bd191048d2880e88540d7437326de8bd0a7f1c9: fix(api): /changes is bounded at 1000 and continues by a cursor on the write order (BUG-3791) (#2151) (@xarmian)
* 30ba2ed3040f9662236960b389c2e8514ae60d80: fix(api): body-supplied IDs must name something in the authorized workspace (BUG-3346) (#1728) (@xarmian)
* fc9ceae92f8eca26edfa2e28dc35bb5aa3ee1e7f: fix(api): children, starred and shared-collection lists are bounded at 1000 and paged; MCP starred caps at 300 (BUG-3789, BUG-3790, BUG-3792) (#2153) (@xarmian)
* 858bd8514e89f18e6e3995ae297160e12e8047ab: fix(api): item lists are bounded at 1000 with has-more paging, and filter-key probing is bounded (BUG-3704, BUG-3703) (#2143) (@xarmian)
* 2246ea6f04294e13e6aff48cbbad319844029a32: fix(apps): a collection-restricted owner cannot grant an app whole-workspace access (BUG-3768) (#2123) (@xarmian)
* 4f277f836a345d86ea212a4581b37b6e1855572d: fix(apps): an app upload is charged against the plan's storage cap (BUG-3653 part B) (#2119) (@xarmian)
* 95ae3adbd91e944fe85d7a81a174257d590e0ac6: fix(apps): an installed app learns its workspace from the redeem, an unscoped /me and every webhook (BUG-3416) (#1797) (@xarmian)
* a04e35a67de6d72a39ebb9c0b2d0508fab3d6139: fix(apps): every list in an apps JSON response is a list, never null (BUG-3417) (#1796) (@xarmian)
* 83ca50f86111d50c1e65fa88d0935b9753b6c372: fix(apps): the apps UI tolerates null lists from the server (BUG-3417, client half) (#1795) (@xarmian)
* 17cbfa236e251a9db19e10ecd079a83c38936fae: fix(attachments): a refused upload, transform or import reclaims the blob it wrote (BUG-3652) (#2118) (@xarmian)
* 4e3988300f8b1b965e499ecf6c5a56de68441f72: fix(attachments): a thumbnail takes its original's binding at insert time (BUG-3385) (#1762) (@xarmian)
* 67d06fdf81941c45061268c339134c35c464b352: fix(auth): a CLI session is never a browser cookie, and sign-in refuses a cross-site form (BUG-3350) (#1747) (@xarmian)
* 15ffd0528604a3b3d798cb32400399808c7b34ed: fix(auth): a password change kills outstanding reset links (BUG-3679) (#2114) (@xarmian)
* 241dd316f9af5b780e3faba9ca9814c2193f7398: fix(auth): a social sign-in without a provider subject is refused on an account with one bound (BUG-3671) [deploy BEFORE pad-cloud #80] (#2144) (@xarmian)
* 551a338cbd92a80094b23024fa31f9004a29da80: fix(auth): a user-less legacy workspace token reaches only its own workspace (BUG-3353) (#1734) (@xarmian)
* 98871c7e017a459a63ba17f9db07aefcc5cef555: fix(auth): a verification link verifies only for its account's session; the mailbox owner can claim (BUG-3382) (#1758) (@xarmian)
* 7b41a0298ee46963a0e78d1e37a2f8647ab88dcc: fix(auth): account deletion's 2FA code goes through login's limiter and single-use claim (BUG-3482) (#1881) (@xarmian)
* ec5b60679a58c1e739ae0b0025ed51ff57269d0f: fix(auth): an OAuth sign-in without a provider subject is refused, bound or not (BUG-3797) [deploy AFTER pad-cloud #81] (#2152) (@xarmian)
* 66b4a9d4773fc0725a017a5132b4f87941a41523: fix(auth): disabling an account ends every credential, and a disabled account gets no new one (BUG-3349) (#1741) (@xarmian)
* 2bd0862af2d42daece3306248f9e93a0f96498bc: fix(auth): platform administration refuses an API token (BUG-3361) (#1742) (@xarmian)
* d4e69a566b7d1bbd27c9ab577fd15bd3e8e8f151: fix(auth): reset-password, register and bootstrap refuse a cross-site form, as login does (BUG-3680) (#2146) (@xarmian)
* 1f391d959187dd1d3277dbffa09cbf0e9a6b8508: fix(auth): store errors on access decisions fail closed (BUG-3334) (#1730) (@xarmian)
* db62001ad4ddf5932c3dadb8523fc03880f9c894: fix(billing): a plan past its expiry entitles nothing, and Stripe plan writes are ordered (BUG-3356) (#1753) (@xarmian)
* fb71a913411cff17d2aeca9f5d01348322412d1b: fix(billing): account deletion proceeds past a sidecar 400 only for the old sidecar's empty-customer refusal (BUG-3560, retro of #2036) (#2076) (@xarmian)
* 5d344d2b880641b4f0d1e77a4af26890d7ab9659: fix(billing): admin stats count upgrades by when the account became Pro (BUG-3591) (#2069) (@xarmian)
* 82064526e32d9c3267b91f0fe206d341d5ec0a48: fix(brand): name the entity as Perpetual Software LLC everywhere (TASK-3321) (#1722) (@xarmian)
* ac5f66f7bd3ca76f0d3cae34f385c407c95142f4: fix(changes): an archived granted item reaches its grantee through /changes (BUG-3796) (#2212) (@xarmian)
* ad6cfc2c5e53198732e204c59f6f833d4067357b: fix(cli): a bundle import shows progress, abandons a stalled upload, and resolves a lost answer (BUG-3476) (#1902) (@xarmian)
* a630f867f4aaad47b9fdff27957feb65d2c335bd: fix(cli): a credentials save stamps its own file's mtime before it truncates, so the empty-file memo holds off Linux (BUG-3838) (#2203) (@xarmian)
* 22dcce6e6c09486851b39cadc73b32f0d4f63e11: fix(cli): a failed stat fails the credentials write instead of skipping the truncate (BUG-3810) (#2181) (@xarmian)
* 1d08594dc0f5be84f97eece5f8936abe9ace2637: fix(cli): a locked credentials load re-reads an empty file before believing it (BUG-3829) (#2195) (@xarmian)
* 223c9734d8041de100c7f2a1d972a92fa13e532c: fix(cli): a workspace or ref string cannot re-route a request, and PAD_TOKEN is not sent to a server only .pad.toml named (BUG-3645, BUG-3646) (#2127) (@xarmian)
* e17f17f51335800fa40e6bb5a0aff1f98fe73f43: fix(cli): an empty credentials file read without the lock is unknown, and UpdateStore will not save over it (BUG-3828) (#2187) (@xarmian)
* 90a304765fa6e2a5d1a2cb61f9b73ebdec6371c4: fix(cli): copy --dry-run previews a big number with every digit (BUG-3456) (#1858) (@xarmian)
* a99a040cf3b5b6a7e844944a8fa3ad7dbb7f99ca: fix(cli): credentials.json is replaced atomically at 0600 and updated under a lock (BUG-3648, BUG-3649) (#2170) (@xarmian)
* c204dd3683fc995f2c4d860946f6097353715894: fix(cli): json fields print as JSON, metadata labelled for the item's kind; MCP 0.68 (BUG-3448) (#1838) (@xarmian)
* 833e309052d2d0843069eb4b8335d83472b6557f: fix(cli): whoami says what a failed check established, and exits non-zero (BUG-2706) (#1901) (@xarmian)
* 47fe81ab99782704c6a360b8646e9d1aa0338ed5: fix(cli,mcp): explicit-limit callers read every page or say they are truncated (BUG-3793) (#2154) (@xarmian)
* 0ecec8235708420c58354d97ffd0b3fb59329b54: fix(cli,server): a rate-limited health probe no longer starts a second server, and a start that loses the port touches nothing (TASK-3620 PR A) (#2106) (@xarmian)
* ba35908f2b2e79666e4725d8961594b6543e13d8: fix(cli,web): link re-points a directory to another server and keeps .pad.toml's other keys; the move-to-Cloud guide is browser-only (TASK-3612) (#2103) (@xarmian)
* 9f5483049d5679bbf1866b35a0821ac9226729f8: fix(cloud): a failed read of a Stripe event row is not a claim (BUG-3561) (#2083) (@xarmian)
* e3e76daae3eaf02a55c32bb6e023447aec352276: fix(cloud): account deletion asks the billing sidecar by user, so every Stripe customer the user owns is cancelled (BUG-3560) (#2036) (@xarmian)
* 5caf11f829fbe55d67fda16ea642bfdef75e122f: fix(collab): a REST content replacement fences tabs seeded from the old body, as a restore does (BUG-3746) (#2134) (@xarmian)
* 134d0a4e89a4abb69f6711899c6134d08cf74a36: fix(collab): a compaction snapshot covers only its own generation's cursors (BUG-3747) (#2142) (@xarmian)
* e64abacec3c78716ce684a021419544b5c1e530c: fix(collab): a delayed browser snapshot cannot overwrite a body built from more ops (BUG-3744) (#2132) (@xarmian)
* 6ed3c09f54e30d0671405b8be518c3a07f20059b: fix(collab): a markdown applier request that timed out is not re-sent to another tab (BUG-3748) (#2133) (@xarmian)
* 16a0243c5e48295bdc17c48125ad1dd390c37a97: fix(collab): a multi-block patch into an open editor leaves the unchanged blocks between edits untouched (PLAN-3578) (#2082) (@xarmian)
* ae52c96d02e3ebda76b66751752735d8a73f85e4: fix(collab): a patch whose applier times out is not re-sent to another tab (BUG-3586) (#2059) (@xarmian)
* db6f0cde1f1f2bedae245a4fa2e13cf58621b655: fix(collab): a schema rebuild sets aside the WHOLE op-log, so set-aside edits can be replayed (TASK-3574 (4)) (#2047) (@xarmian)
* 602ce1006ba912ac5db5b553e5f41a3208baf5a9: fix(collab): a websocket peer that stops reading or answering is closed within a bounded time (BUG-3771, BUG-3636) (#2124) (@xarmian)
* 64e6dfb68c051143ce9a1ce18a44a5f3b0482721: fix(collab): an applier ack reports persisted only when its bracket held no failed append (BUG-3749) (#2131) (@xarmian)
* c8a1eeb84b9d3dda8f34a301b93bd2f9c976d98e: fix(collab): an awareness frame's entry count is bounded by the bytes that carry it (BUG-3772) (#2204) (@xarmian)
* 5960cf1978e60a0c10852c52479abc4791028afe: fix(collab): an open tab refuses a content write over typing the server has not stored (BUG-3542) (#2016) (@xarmian)
* 2898bff09e67a3505594464934c240bf62832102: fix(collab): close a peer the op bus had to drop an op for (TASK-1273) (#1981) (@xarmian)
* d90ac1ebd14ddf9eb8776086ece39232250f385f: fix(collab): persist a typed burst's waiting frames in one transaction (BUG-3253) (#1909) (@xarmian)
* 78ec772226b5fa53ed7516f51290186494bd38f8: fix(collab): recovery refuses an incomplete op-log replay, and a failed compaction snapshot keeps the log (TASK-3574 (1) and (3)) (#2045) (@xarmian)
* d93a94a42caffb327e52cce3ef77f719ba704975: fix(collab): recovery replays SyncStep2 rows, which can hold the only copy of an edit (TASK-3574 (2)) (#2046) (@xarmian)
* 416aea2d14d362bfee49c1ba9b922c503d4ebd99: fix(collab): stop appending the whole document to the op-log on every reconnect (BUG-3523) (#1965) (@xarmian)
* a5409ed2e11db3897d5f7db309c33c08665ffb4e: fix(collab): the editor is read-only through a force_refresh recovery, so no typing is lost (BUG-3697) (#2128) (@xarmian)
* 33e7a503d512e8676d7a0fc72afc091637e5ef22: fix(dashboard): a task under two active plans no longer pins the skeleton (BUG-3538) (#2002) (@xarmian)
* 1fe9a1503787b8bfea8079d6b1d89ea014d0d0ad: fix(deploy): Kubernetes keeps attachments on a PVC, and uploads get a writable /tmp (BUG-3714) (#2141) (@xarmian)
* 6fd59627bd039a0956c328d24256a98a7fbd0fd5: fix(deploy): the Kubernetes manifests run one Pad replica with Recreate and no autoscaler, since collaboration needs a single writer (BUG-3573) (#2039) (@xarmian)
* 09ecc5e02faa697fa42186606e01047272b50479: fix(diff): version writers never diff text that is not valid UTF-8 (BUG-3839) (#2200) (@xarmian)
* daf94614ca7d8cee710a2ef0c05a88e8646c40ca: fix(documents): restore only a document of the URL's workspace (BUG-3335) (#1724) (@xarmian)
* 08a5f1c7d24a7e3e9fff156d2acab2dcdbb03efa: fix(editor): a block marker after a hard break stays text (BUG-3584) (#2060) (@xarmian)
* 6d3842b1f7ec1d59fc6f43a846346c359a0bbe9d: fix(editor): a line-start marker followed directly by marked text keeps its form (BUG-3600) (#2079) (@xarmian)
* 8d910dc20a0e777b9bc6db999635161b3dca0086: fix(editor): bold, italic and strike always serialize to markdown that reads back (BUG-3583) (#2057) (@xarmian)
* cfc5391581f28c94af5ffa8514a4e660a1f5942d: fix(events): a corrupted event sequence counter heals visibly into a new id space; the id is read back, not rendered through a double (BUG-2744) (#1906) (@xarmian)
* 828b656e924ea83ab087ee667f6edbe08e5d0f81: fix(export): an export reads one snapshot, so a concurrent write cannot leave an item without its collection (BUG-3654) (#2122) (@xarmian)
* 3b27a138e496455daf34b1efa2ba8243b14396b6: fix(grants): an item grant never opens a deleted collection (BUG-3333) (#1725) (@xarmian)
* 0978b9d818ac82c703291453b1d07f371fc7a784: fix(import): a bundle is not complete until its gzip footer verifies (BUG-3657) (#2158) (@xarmian)
* 3fe40aeff7f08eb8ef5a9ff75fe65b0d80dcbaa6: fix(import): bound the work a single bundle import can do (#1735) (@xarmian)
* 87101002a282ed1257e5fb0fed21d24c16c1c892: fix(import): bundle import remaps attachment references in version history, and on a kept partial import (BUG-3655, BUG-3656) (#2156) (@xarmian)
* 9ef346268c9d743f2cfdc61d7b5d720ed9278e06: fix(import): refuse duplicate source ids and attach by source id (#1740) (@xarmian)
* 77e1b386ef718a48cb992ae73363d7e8410e59d5: fix(import): relation defaults in imported schemas point at the imported items (BUG-3658) (#2159) (@xarmian)
* d51aba9adbe78d0a13be47038bf754dc3273b472: fix(invitations): a member accepting a dead invitation is already in, not told to get re-invited (BUG-3870) (#2217) (@xarmian)
* 7e7bb6198983dcba5d82fce122fa0f0d8f71c6ef: fix(invitations): a pending invitation dies with its inviter's authority (BUG-3770) (#2214) (@xarmian)
* 6dbe15e79574f9c25c7b990695eb0d062da5fbfe: fix(items): a keyed create claims its key before the plan-limit check (TASK-3585) (#2088) (@xarmian)
* b15a48345e00328e8bd9af3d841a33e35da847aa: fix(items): a keyed replay of an archived-source move re-checks the destination (TASK-3585) (#2087) (@xarmian)
* d509d7530865b48908828939281ea9ed3f2f76be: fix(items): a move uses the item as it stands under the lock (BUG-3665) (#2165) (@xarmian)
* 199fd208a801098ca3dda9bfd5231127fc7051ed: fix(items): undo of an emptied line; a patch that changes nothing is refused (PLAN-3578 retro fixes 5+6) (#2089) (@xarmian)
* 68a7e279a702c27efe268ada7e4fd194ce41575d: fix(leases): bind item leases to the claiming account (#1731) (@xarmian)
* 9ef94ba4d8ba0527e2e1e88142472681fec3095e: fix(links,store): wiki links stay on their item through a reference-shaped rename and legacy renumbering (BUG-3693, BUG-3750) (#2140) (@xarmian)
* 4ed3b5eca2f2760c97482476a2812a92f1349544: fix(materialize): a job's deadline scales with its op-log (BUG-3521) (#1946) (@xarmian)
* 202f53daeffc2d0689a8fcd3492337ba9385831a: fix(mcp): MCP's long-lived streams end with their credential (BUG-3837) (#2201) (@xarmian)
* 7825f3afc5c1853d2f9a81a3b919b73a26d6dbaa: fix(mcp): MCP's long-lived streams keep alive and take a stream admission slot (BUG-3835) (#2197) (@xarmian)
* fdcf0867cdd74a8f0211a3032c46cc9356134734: fix(mcp): a /mcp stream whose client stops reading ends instead of pinning its handler (BUG-3808) (#2182) (@xarmian)
* 23a0360991dde90fbc6632a84e8526e10a48c359: fix(mcp): a connection row decides workspace access, not the legacy token list (BUG-3337) (#1749) (@xarmian)
* f9937c76532d4f4a70d6ebdd85078f6ff5a6ecf1: fix(mcp): cloud refuses to start without an https origin for MCP OAuth; a blocked self-hosted MCP says so (TASK-1069) (#1920) (@xarmian)
* d2337fafe452803cd8faa5ea69347fd8e35f01ed: fix(mcp): escape the workspace and ref in pad_playbook.run's path (TASK-2863) (#1991) (@xarmian)
* 16edb942030d0609e00d8858c38293aa3827547a: fix(mcp): free tools/list headroom: reflow and condense descriptions (TASK-3536) (#2004) (@xarmian)
* 1d752e0ba68f8a91015cad68e257ed3e1853b5c8: fix(mcp): remote pad_item.import keeps its artifact (BUG-3533) (#1992) (@xarmian)
* 3901101c81d2e6fedeecabfa2904bd6e8265c1bb: fix(mcp): remote pad_set_workspace embeds the workspace bootstrap (BUG-3326, ToolSurface 0.62) (#1710) (@xarmian)
* 0f932b5880b45d7c4c8b4ec3cb0ef5e466cd55e1: fix(mcp): remote routes answer a missing workspace with no_workspace and the list (TASK-2314) (#1846) (@xarmian)
* 59772ffc34310cb07b3638239f11a317d08d860d: fix(members): a collection-restricted owner cannot grant beyond its scope through invitations or role changes (BUG-3634) (#2116) (@xarmian)
* d212eb65031b691346f546e3c33d590363ccee80: fix(members): keep a workspace's owner and at least one owner member (#1737) (@xarmian)
* c0e66c6700666656b7b94879a729de51402a80f6: fix(models): the fallback terminal lists cover every "won't fix" spelling (BUG-3546) (#2033) (@xarmian)
* fc64d92eceb05645959ef43a7751f8a97d217468: fix(netpolicy): block Azure WireServer, and pin the cloud metadata census (BUG-3660) (#2155) (@xarmian)
* c52f64e26357ec93610733ad4551568d290376be: fix(netpolicy): one outbound address policy for URL import and webhooks (#1738) (@xarmian)
* 6365ac08fae4639d3b01d399c3e8669e0b307bf6: fix(oauth): a revoked grant mints nothing, and one refresh token rotates once (BUG-3678) (#2121) (@xarmian)
* 7b95dae4f56976a5a30d302709f2fd6513f4f236: fix(oauth): another client's replay of a spent refresh token or code revokes nothing (BUG-3400) (#1807) (@xarmian)
* 5749671dd95b2fa84e6c210ab4f483f6a1caf254: fix(oauth): include_future_workspaces is no longer a control; limit to current is an action (BUG-3338) (#1751) (@xarmian)
* 2ef63e3b25cc2d2e773f628bc7f3eb829d755f02: fix(oauth): introspection describes only the caller's own client's access tokens (BUG-3398) (#1791) (@xarmian)
* a2e1c5d9ca3fabf31e091b34a541408109b1a7f7: fix(oauth): narrow current-only wildcard connections to their current workspaces (BUG-3338) (#1752) (@xarmian)
* 6f6af0cf2c8a7c15110f5ef3d8ee58db214f5f8f: fix(oauth): the consent screen names Pad, the instance, the user's workspaces and the return host (TASK-1071) (#2017) (@xarmian)
* b950f311c6eef821c6d5657a761cc5e50e2d30be: fix(playbooks): the shipped ship playbook loads conventions with --full and guards its status updates with expected_seq (TASK-3575) (#2040) (@xarmian)
* e774268d63706e560ff8f25d56905581e552ea38: fix(plugin): drop the pinned version so installs follow the commit (BUG-3463) (#1848) (@xarmian)
* 9f9304b294bd3748c67386eee31a4b7dbf7081dc: fix(plugin): the pane's copy link points at the server it talks to, not always Pad Cloud (BUG-3484) (#1899) (@xarmian)
* 505cac1bab94b63b06803120ec9baba2dc084934: fix(ratelimit): retention covers the full refill window, so an idle drained bucket is not reset (BUG-3638) (#2115) (@xarmian)
* 1d20ae56c8e38fd1b86d64f9a524f936b235694a: fix(release): the release smoke stops the server it boots, and checks that it did (TASK-2035) (#1983) (@xarmian)
* 9e6791d4f1b8d7d934a9bbae52a47885b50f5090: fix(scripts): install-refresh asks git in the caller's checkout, not the server's cwd (BUG-3403) (#1790) (@xarmian)
* 38c591673fd0058cc8bfab9308ce24e8a6b5e5b1: fix(search): scope workspace search to visible items (#1723) (@xarmian)
* 08a362ee5d1c2d5fb09d625bea5108b3651a0fa5: fix(server): /mcp middleware refusals get the response write deadline (BUG-3834) (#2199) (@xarmian)
* 698fe2ff6eb2bc84d21af7d22afa4e7a4b525801: fix(server): a collab revalidation tick that errors makes the conn read-only (BUG-3474) (#1866) (@xarmian)
* 8a1aaf61a80effb18860f939001bc3b766fc55cf: fix(server): a failed flush reaches the handler through chi's wrappers (BUG-3827) (#2186) (@xarmian)
* f3b753e3a82762fcf192ef96de65c354da543f15: fix(server): a non-cloud boot no longer makes a Pad Cloud database's free users unlimited (TASK-3551) (#2028) (@xarmian)
* a53160ec79d1ba32b852cb9332619ccdda1b23fd: fix(server): a shared collection lists items in the owner's arranged order (BUG-3530) (#1990) (@xarmian)
* 4d0944c4c824f2996ab41429d0eda494d9de7619: fix(server): a watch stream resolves each workspace slug once per tick, not per notification (BUG-3773) (#2210) (@xarmian)
* f17aaf26e2f5aa259e928e68fac8ccf444f9ddb7: fix(server): a workspace invite in the setup window answers setup_required, not 500 (BUG-3544) (#2034) (@xarmian)
* 9da6714ffc31c2b3c1d8fde40824db39f9d4b86e: fix(server): access_epoch hashes the set the item doors filter by (BUG-3347) (#1812) (@xarmian)
* b6f2d41043ba83ad2d7552a0911804503f032d04: fix(server): an account export that times out or fails says so, instead of arriving short (BUG-3626) (#2109) (@xarmian)
* fd63cc53ad08a27bb8e1af8f11dc3745e7b9cd91: fix(server): an event stream whose client stops reading ends instead of pinning its handler (BUG-3637) (#2172) (@xarmian)
* 250b5c2c0364a4ff9da470b4246dc5adb2943d50: fix(server): an interrupted import rolls back, and its outcome can be asked for (BUG-3475) (#1867) (@xarmian)
* b3cf4f529237e597b121a110e71b27980845df2e: fix(server): an ordinary open backlog fills Up next and `pad project ready` (BUG-3453) (#1854) (@xarmian)
* 4d6ebd426c80d41a45233c65f552547c3fe5f251: fix(server): attribution comes from the request, never the body (BUG-3372) (#1754) (@xarmian)
* 0328b8d961b8cb3fc29ec90d9d3333e1992b92fb: fix(server): bulk field update leaves coercion-only keys out of its patch and keeps any locked auto-date value (BUG-3831) (#2202) (@xarmian)
* 037e6166f18caafacc117695463059466aff90e8: fix(server): bulk move and bulk tag re-check what they read before the lock (BUG-3813) (#2188) (@xarmian)
* f9de1871ddf91212a646ddedfff41bb094f03abc: fix(server): cap the MCP request body at 7 MiB, answering 413 (BUG-3534) (#1988) (@xarmian)
* ed9de583cd99c48e084fe89675daedc779a36269: fix(server): every non-stream response write gets a rolling write deadline (BUG-3821) (#2189) (@xarmian)
* 4d017ddcff782ec99728f96095e2366c84f0a4de: fix(server): item context fills its budget past a part that does not fit, orders conventions by relevance, and widens implement to commit and PR rules (PLAN-3598) (#2101) (@xarmian)
* 0f5b567fe7179128740d637e3134875317d34211: fix(server): lineage and closure name only items the caller may see (#1743) (@xarmian)
* 4b53142589681ed27ea08a4df8d1194cac757250: fix(server): match accounts by email only once the address is verified (#1732) (@xarmian)
* 47ca9e521a55be32647c7c3f4c30973c65b20831: fix(server): refuse a collection schema that repeats or empties a field key or option (TASK-3539, PR B) (#2009) (@xarmian)
* f74f626fcbfa4d1ba9e0cdaf5cb37e3490fc0ddd: fix(server): register-with-code claims the invitation atomically; a gone invitation refuses and rolls the account back (BUG-3438) (#1834) (@xarmian)
* daed6bb441a842e5ac5bbe80b43e2f27a49a82f1: fix(server): removeUnusableWorkspace reports a failed delete as kept (BUG-3479) (#1870) (@xarmian)
* 119823d62d49629cf171a038f3a2d320de212292: fix(server): role-board reorder refuses another workspace's item and counts its rows (BUG-3342) (#1750) (@xarmian)
* fe9421322dc2d13b18682b5e44389cf9ec5908e1: fix(server): the /me summary mirrors the admin bypass; every admin route proven open to an admin session, closed to an admin PAT (BUG-1926) (#1918) (@xarmian)
* e3668f0fea0efbb1f86446a65201ea436c33cdd8: fix(server): the item-grant filter keeps an app request's read ceiling (BUG-3424) (#1825) (@xarmian)
* a1c36fca0492b12f6a21c4dfdab0d6021b8cfaea: fix(server): the upgrade diff states what a widened delegated access grants (BUG-3427) (#1817) (@xarmian)
* d75db3051563f27936bc6485dff41c1f6304d069: fix(server,store): unique_scope values are checked again inside the write, under its lock (BUG-3812) (#2184) (@xarmian)
* cd6dfdb318df4aa5648b61b7c44bbdd1413bdc13: fix(settings): Conventions and Playbooks start unchecked when a member is restricted (TASK-3384) (#1759) (@xarmian)
* 5578aeb04600004afe89fec28a3d36194b2d4fec: fix(settings): a late member-access response cannot fill or save another member's panel (BUG-3698) (#2126) (@xarmian)
* 76e029fff54477e2fb1391070188a23579a36171: fix(share): a share link serves nothing once its item or collection is archived (BUG-3635) (#2167) (@xarmian)
* 896b5561239888a7791ae6a79ac35afee0925ccd: fix(share): a shared body keeps only the classes and inputs the markdown renderer emits (BUG-3799) (#2162) (@xarmian)
* bf37b59e71a533ce773be3663cf0c523c85dd5c4: fix(share): a shared item body is sanitized with the markdown allowlist, and the SPA CSP restricts form-action (BUG-3669) (#2145) (@xarmian)
* 6e30a549a1814eedd617287754555e0ca89313f3: fix(share-links): a link stops resolving while its workspace is deleted (#1726) (@xarmian)
* 1f982df402e54e891d83d06d2b09009a9c0f85a2: fix(sse): an item event without a collection is not workspace-level (BUG-3343) (#1729) (@xarmian)
* aae955c9729df161519cbb48807143f049dfe88b: fix(storage): bundle import and cross-workspace copy are charged against the storage cap (BUG-3653, TASK-3625) (#2117) (@xarmian)
* c87587cad2f46c2ef70bd9bb183c07fcc292de05: fix(store): PG migration 054 breaks same-second version ties by id, not ctid (BUG-3751) (#2183) (@xarmian)
* 0aec8ed1a71227946c41129f42056a75b87e516b: fix(store): Postgres migration 004 drops the old doc_type CHECK before renaming phase-plan rows (BUG-3752) (#2130) (@xarmian)
* aa8975710db3b22d84d3ddbfc577e8737cbc5c9c: fix(store): a body rewritten without a version rebases the newest version's patch, so History stays exact (BUG-3745) (#2139) (@xarmian)
* 623652c71192458752c7239ad2f5f0e06327f494: fix(store): a link row counts only when both endpoints live in its workspace (BUG-3776) (#2208) (@xarmian)
* d95f90850caced80e22e4f1db87a41c4ca076fa4: fix(store): a role change or disable of a vanished user is 404, and the unguarded DisableUser is gone (BUG-3826) (#2196) (@xarmian)
* eac92797f49365b5bf4fc84ac326591dc33d0a0f: fix(store): a workspace slug is slugified whichever door supplies it; migrate-to-pg keeps existing slugs (BUG-3769) (#2205) (@xarmian)
* 5279c491405ba2858534c197da9890e07b11bd3c: fix(store): account deletion and workspace purge lock comments root first, and retry a residual deadlock (BUG-3395) (#1792) (@xarmian)
* 61f07d39ea0ae10a3f8b19bf7456d0976f54b3e8: fix(store): an API token mint or rotation reads its row back inside its own transaction, never panics on a concurrent delete (BUG-3405) (#1774) (@xarmian)
* 0c68bbc73de37ddf371b15cec464e83d7d12280a: fix(store): an admin resend revokes and re-creates in one transaction that re-reads the workspace (BUG-3817) (#2193) (@xarmian)
* fdce754f2077abbb4207efdaad25a7b89078f42a: fix(store): an item list with a search term keeps include_archived and sort, and the tag filter matches exactly (BUG-3686, BUG-3706) (#2147) (@xarmian)
* 812f68930b11cc6fb1f920a0637d42ba8adad61b: fix(store): an unlink re-checks that a sign-in method remains under the account lock (BUG-3816) (#2191) (@xarmian)
* eff70d7344d7f4037f9440d562e6ffa83afd2064: fix(store): compaction deletes exactly the rows it read (TASK-3532) (#1995) (@xarmian)
* a27df265bca7a2267f111b43d48b01bfe7c1f7d1: fix(store): concurrent re-invites no longer report a successful replace as an error (BUG-3460) (#1840) (@xarmian)
* 677081886471b6e1706dfc639e183c015122be0e: fix(store): every write that reads its row back does so inside its transaction (TASK-3406) (#1805) (@xarmian)
* 02806238d659d3eacd23d618f02ad7a2da791275: fix(store): import drops a unique value an earlier archive item holds, and says so (BUG-3825) (#2194) (@xarmian)
* aa7480290953f4a5fbd7097128dee12e71926eb3: fix(store): import indexes wiki-links, so an imported workspace has backlinks without waiting for a restart (BUG-3627) (#2111) (@xarmian)
* b9db178e1ed2ff600560b7fe85b98bcb90ba3cc6: fix(store): index api_tokens.token_hash on both backends (BUG-3668) (#2157) (@xarmian)
* 0479bf6cb1b505878b87ccfde9ca078260756dc2: fix(store): index status_transitions(seq) on both backends (BUG-3667) (#2164) (@xarmian)
* 107c38267c0f6ec221beedbc40211d4833206872: fix(store): legacy built-in adoption re-reads each item under the workspace lock (BUG-3806) (#2179) (@xarmian)
* be615377492e5ffa41a6b6c29c8bc5698e63076e: fix(store): legacy document version doors resolve from the body read in the same snapshot (BUG-3833) (#2198) (@xarmian)
* c97a054252e206de7a42da5f65c83a8190679080: fix(store): legacy per-collection item numbering is converted even after migration 056 dropped its marker (BUG-3664) (#2129) (@xarmian)
* 4c7774dfd77822387568fa78bd39bb2b94b08763: fix(store): log why a workspace import renumbered its items (TASK-2923) (#1994) (@xarmian)
* 8658db7275d8ca4b0f55fe8121ec26cece39c608: fix(store): migration 025 rebuilds documents with foreign keys off, so a database with versions can upgrade (BUG-3663) (#2120) (@xarmian)
* 1082c4aa16f608e4abc26da3a160a2fd2cc84e96: fix(store): reads exclude soft-deleted collections' items (BUG-3425) (#1820) (@xarmian)
* 1e75d19d1f9758e9c43f240581324d82f79660d3: fix(store): rebindQuery skips SQL comments and quoted identifiers (BUG-3430) (#1822) (@xarmian)
* f9d79aea94306c008212f515b66ab1a88e5c11ca: fix(store): relationship reads exclude soft-deleted collections (BUG-3434) (#1828) (@xarmian)
* a7f98c01fca0e20ca9c7ac039fcb06c4e0960754: fix(store): search, tags, children and progress exclude soft-deleted collections (BUG-3428, phase 1) (#1824) (@xarmian)
* 0d28c48e5873158893c592e9d777c6c3212c91e1: fix(store): startup secret encryption passes compare-and-set on the value read (BUG-3805) (#2177) (@xarmian)
* c912c2c6414249d82e91e67cb65771c12fb9ab59: fix(store): the wiki-link backfill re-reads each item under the workspace lock (BUG-3666) (#2168) (@xarmian)
* 6f75e252723b31080c41900326327efe61156353: fix(store): version doors resolve the patch chain from the body read in the same snapshot (BUG-3814) (#2190) (@xarmian)
* 01021632c9626352d12a8859f68247b7f4458ad6: fix(store): version rows record their body's hash, and the walk refuses what it cannot verify (BUG-3820) (#2192) (@xarmian)
* b3e6815e0c432d81d57214f0a1f267b4a2b9040f: fix(store): wiki backlinks exclude sources in soft-deleted collections (BUG-3344) (#1814) (@xarmian)
* db8fb3aabf369fd4df08d7736c479363cf5f815a: fix(store,server): an item write re-checks its fields under the seq lock when the schema it was validated against has moved (BUG-3407) (#1806) (@xarmian)
* 48c3ca066c9ddaffb38267c58ad1873b6a896901: fix(test): test temp dirs stop leaking into /tmp (BUG-3412) (#1786) (@xarmian)
* 2f3cf402b173d4bc83f2139fd07e289326f96799: fix(timeline): 'commented on update' only for a comment an update carried (BUG-3437) (#1832) (@xarmian)
* 8bb4616a3d753e880c3c84067d1438d750ffad87: fix(urlimport): marshal OpenAPI examples with libopenapi's own yaml package (TASK-3422) (#1818) (@xarmian)
* d5ca8a7eb0978fc8c28d00d641ee878ddc35597d: fix(versions): an applier-path body write leaves a version row (BUG-3327) (#1709) (@xarmian)
* 69d2be842903a6d45b27b0b7c24cd27dc3be8870: fix(versions): restoring or diffing a version whose patch failed is refused with 409 (BUG-3815) (#2180) (@xarmian)
* 540925cd0bd5895a3322e87abfa55dd5febef5f4: fix(watchevents): a frame that wins the receive select after Close records and reports nothing (BUG-2741) (#1905) (@xarmian)
* 0663b05752b3b9ba4fe25c1c2dddd7b9d8d846c8: fix(web): Activity, Tags, a tag's items, Starred, Members and the Library say when they failed to load (TASK-2203) (#1930) (@xarmian)
* f7b255819656352947cae4cdbf0906a6c6163c40: fix(web): ESC closes the pane before its ItemDetail has loaded (BUG-3148) (#2053) (@xarmian)
* 52d90ea31ed08334bc231b0832accbaf0530fd4d: fix(web): Insights throughput labels read as dates, and hours in local time (TASK-2220) (#1951) (@xarmian)
* 03a3617dbb0589fcaea33789fea0bf7832f1d836: fix(web): Library, Playbooks, Conventions and the playbook editor find their collections by trait (BUG-3481) (#1876) (@xarmian)
* 56f8a49fe0438b9f98d365cc273e0098b8312df4: fix(web): SSE bursts coalesce their reconcile and collections reload; the timeline ignores other items' comments (TASK-2224) (#1844) (@xarmian)
* b87f63ae56aeabad202d4c299e82cf19d4c06729: fix(web): a failed logout always lets items save again, and a sign-out discards what it stands down (BUG-3571, retro review of #2041) (#2074) (@xarmian)
* 3377637e68a59511eb82061adccc80b73d715f40: fix(web): a failed version restore says so, restore needs edit permission, and a child reorder that does not land says why (TASK-2205) (#1929) (@xarmian)
* 71f21dd29ce2cac61e530ec6e332f90d749e6b07: fix(web): a json field keeps its type in the schema editor (TASK-2194) (#1971) (@xarmian)
* c0faa52b2e59b337a58bf20b7ec60c9323341e35: fix(web): a kept draft with a stale base says it can't be applied and offers only Copy (TASK-3856) (#2213) (@xarmian)
* 9e886ddc00c6c27143087a38525f033bcce36dd6: fix(web): a link that opens elsewhere never keeps window.opener (BUG-3359) (#1739) (@xarmian)
* 791f25a946fd62a2bb9bd1ff6b28a31894ce69a1: fix(web): a palette search that fails says so, with Retry, instead of "No results" (TASK-3587) (#2063) (@xarmian)
* edf7e2226219942bf1d27f1a8c9e040fb3bb3e64: fix(web): a raw markdown save carries its base and asks, not replaces, over a changed body (BUG-3540) (#2011) (@xarmian)
* 56eeceabcafb912b5565c7356eac61385caff442: fix(web): a reorder settles to what the server stored and never leaves an unconfirmed order looking settled (BUG-3699, BUG-3700) (#2150) (@xarmian)
* 1fc60d72b47a6edbe55b65e2fcc283639153f52a: fix(web): a save refused for an open tab's unconfirmed typing asks, and Overwrite lands (TASK-3548) (#2025) (@xarmian)
* b5df3f96df516ab4bc3301d723c2fc9295c86669: fix(web): a share link's sign-in comes back to it, and a gone or unreachable link says so (TASK-2249) (#1940) (@xarmian)
* fc2e768dbf40ae816097cfda449c6b5e70a6548e: fix(web): a shared ?view=table link opens the table, and the remembered view is per workspace (TASK-2212) (#1947) (@xarmian)
* c086457939a77d4a7582fd5bd6756f886d6554fa: fix(web): a shown kept draft is held, so newer kept text cannot replace it (BUG-3863) (#2215) (@xarmian)
* 6647ca5444edfeeb3ac785c79a60811cd39b4689: fix(web): a split-pane switch makes each request once (TASK-2228) (#1937) (@xarmian)
* 89d9298ad0fd8f3942f11341c245bb0c0b69cd5a: fix(web): a tag filter matching nothing says No matches; tag pages get Show completed (TASK-2211) (#1913) (@xarmian)
* 92b472f1d749b12ba19df9c3b3ea81a3193b0031: fix(web): a teardown flush over the keepalive budget goes as an ordinary request (BUG-3522) (#1949) (@xarmian)
* eb3f8f0f19af50d3666b1aeb2c4f2b87236052c8: fix(web): a workspace opens with its requests in parallel; the dashboard poll pauses when hidden or live (TASK-2229, TASK-2227) (#1912) (@xarmian)
* 20690ae9fb56481ffdf389aaf12796ea5ee6fd78: fix(web): admin user rows, settings tabs and the console nav work from the keyboard (TASK-2238) (#1962) (@xarmian)
* e5997aee097e97203a776cf09d53abec1a4e08d1: fix(web): an agent's [[REF]] applied to an open tab is a link, not bracket text (BUG-3582) (#2052) (@xarmian)
* 34d17e44f1ff905fa83a56fae17d43be977bb58c: fix(web): an item load no longer waits for the index to catch up (BUG-3473) (#1887) (@xarmian)
* 7aa5fa67f7cbdf2a2da0e27135a34f588a333a07: fix(web): an open mobile sheet stops page pull-to-refresh, and a pull from its list top closes it (BUG-3386) (#1830) (@xarmian)
* 721c9597f4ffd475aee42ae337d56479a8a16d4e: fix(web): an unknown invitation code says so, the header names the workspace, and the login link keeps the code (TASK-2251) (#1917) (@xarmian)
* 1eecf710c8fef732e9f3eb69ebc796b7a8f5e8c1: fix(web): angle-bracketed prose survives the editor: `<Button>`, `Promise<T>`, comments and unknown tags are text, not dropped markup (BUG-3557) (#2035) (@xarmian)
* 1a76ca3f58274e431a5828510ee028f1edf3b3a7: fix(web): app dialog and toasts replace native confirm/alert; sticky save and sync status (TASK-2221) (#2015) (@xarmian)
* cbf90f4542420a3788aabebad60d850f883f1fd1: fix(web): cards, sidebar rows and table headers stop nesting controls (TASK-2237) (#1968) (@xarmian)
* c0beb4da34c44b8323b38004fc1db0fa8a0dc8fc: fix(web): closing or leaving an item asks first when typing may not have reached the server (BUG-3556) (#2037) (@xarmian)
* 80bfd26c6a676806f125165216f58e5f9ff8167c: fix(web): conventions, playbooks and the library say what their markers mean (TASK-2257 C72) (#1963) (@xarmian)
* 203a0b827f23a1c52bec44e8e2e2d092c2867f8a: fix(web): deleting a token or revoking a share asks first and says when it fails; a new token has a Copy button (TASK-2193) (#1910) (@xarmian)
* 35ca07bd6e4f3fbd37f70467de5c83c2995d122d: fix(web): drop the ⌘] binding that cancelled browser Forward for nothing (BUG-2666) (#1849) (@xarmian)
* 7222505d41b0d8d2847cbd3f58b549eb17633d6c: fix(web): every field shows a focus ring, and the sidebar add buttons reach 3:1 (TASK-2262) (#1843) (@xarmian)
* 41692af98100e7474695fee88792dba054cbab97: fix(web): every filter select and search input has a name; the share-link password gate is labelled, focused and announced (TASK-2236) (#1921) (@xarmian)
* 8384adc63122d5b3ef8907b52643a74afcfac6bb: fix(web): every text field has a name, not just a placeholder; an axe check proves it rendered (TASK-3515) (#1931) (@xarmian)
* 93b906b0b3efd4998347f648c818d8fc8e5ffd57: fix(web): field editor polish: a non-number says so and sends nothing, the select announces its highlight, the date clear is a sibling (TASK-2216) (#1919) (@xarmian)
* 999c4c82e8d8b9edbc313b4fe191b5a4abea8e96: fix(web): four retro-review findings on #2063, #2067 and #2072 (TASK-3599) (#2078) (@xarmian)
* b0f325e75109705763d19de3a473ac7059966376: fix(web): hand back an edit lost with its socket on force_refresh (BUG-3526) (#1973) (@xarmian)
* a867a8f7744df5c52666c97b2d5665e012d262ea: fix(web): icon-only buttons carry accessible names (TASK-2240) (#1974) (@xarmian)
* 46490b0612471e4dc15abb1bfe52b9539e4a9292: fix(web): keep unsaved text when the session ends under an open item (BUG-3571, part 2) (#2044) (@xarmian)
* f8faed647af03929575bd30f30bf7344f636ae67: fix(web): keyed lists render repeated keys instead of blanking the view (TASK-3539, PR A) (#2006) (@xarmian)
* c4354571d0bacc1464904fc4b3ec5ab58c39b5f8: fix(web): keys typed before the slash or [[ menu opens are its query (BUG-3547) (#2024) (@xarmian)
* 5ea7fde86b60d586575385c3d0926d3fd4c1c941: fix(web): keys typed into an editor frozen by force_refresh recovery stay in the editor (BUG-3786) (#2138) (@xarmian)
* e95135c499ca690b532cdd6bb974683b0cc22fe1: fix(web): links to the /-/r/ resolver open their target (TASK-3119) (#1862) (@xarmian)
* 25dca945e51327d6235a1ed46a5fbe7c313aaabe: fix(web): list and table j/k step the rows on screen (BUG-3492) (#1894) (@xarmian)
* 9b7ffdf897b2516825557106b82f64a133ceb28d: fix(web): long Active Plans titles stay inside their card at every width (BUG-3440) (#1855) (@xarmian)
* 6c4b54908c5865c4da4107f317c13ddbc840a07d: fix(web): looking at the template list no longer picks startup, and a chosen template stays named (TASK-2254) (#1961) (@xarmian)
* f323d810a6c29fbdd032d0a8ad0bb55942623f3c: fix(web): manual order breaks a sort_order tie oldest first, as the server does (BUG-3527) (#1969) (@xarmian)
* 92305fba4d6083b1832bcaec996fb3230c937bd9: fix(web): marks never sit on inline atoms, so a tab's editor equals its Y.Doc (BUG-3568) (#2038) (@xarmian)
* f392847024dcf5df98ae6c18ad0859bbf8d7c37d: fix(web): no field suppresses its focus ring any more (TASK-3461) (#1845) (@xarmian)
* fe838f146efb11efc9f4ea3b4b6e4ee7b4a2904d: fix(web): notifications, docked sheets and the Insights popover take, keep and return focus (TASK-2235 U1) (#1945) (@xarmian)
* f2a3a28e46852d5d44dd949835274aa427bcf78b: fix(web): offline edits are protected honestly: the badge says they live in this tab, closing or leaving asks, a discarding reload hands them back (TASK-2199) (#1892) (@xarmian)
* 75e1aa684e9c61c75fc6ed996c2fe945b921e2f5: fix(web): on HTTP/1.1 a browser holds at most three workspace streams; other tabs poll (BUG-3320) (#1904) (@xarmian)
* 5e914e79ff700cef4b0de20c83dbfa7e5b7631b1: fix(web): onboarding says "Agent activity detected"; live signals say "connected" and "ready to receive" (TASK-3596) (#2077) (@xarmian)
* 9a90368f6622de07c44d39c1d3ee29723faca76d: fix(web): one connection-recovered signal heals failed loads, and the dashboard and activity show stream status (TASK-2201) (#1960) (@xarmian)
* 35e5f4809e232e08f023899a14ad14ea569f75d8: fix(web): playbooks say how they run, and the library keeps its tab (TASK-2256) (#1966) (@xarmian)
* 13fa0c99e9f0d7a1fe5afb1c1d7aa67feb675c8b: fix(web): quick-add is `c`, and one switch turns every single-key shortcut off (BUG-3465) (#1851) (@xarmian)
* 64398c95c8c3011a5ed0dad427d0cc66f535b2d9: fix(web): rich crash drafts anchor on the editor's confirmed snapshot; patch restore waits for the open editor (BUG-3850) (#2207) (@xarmian)
* 9103aaeb243b422d92e55ad5344e95574fb874df: fix(web): section tab titles, one Mod+\ chrome state, a reachable and complete shortcuts sheet (TASK-2261) (#1972) (@xarmian)
* 0015f49c1ebfb88e5aa88e457ebf2eeb49348247: fix(web): settings say whose they are, roles and grants explain themselves, webhooks say where they live (TASK-2255 C59/C60/C109) (#2030) (@xarmian)
* 2b0652d1925e374866919aa257d6d8cf0ace0f31: fix(web): signing out asks first while an open item holds edits the server may not have (BUG-3571, part 1) (#2041) (@xarmian)
* 22a32efdb544977c3a922a7b3816cb682f215919: fix(web): skipped board cards keep their placeholder height, so a scroll to a far card lands on it (BUG-3553) (#2050) (@xarmian)
* 4c733467ef0bfc248e8c60f0b84b124f7c97df3d: fix(web): space between the pad wordmark and the first workspace tab (TASK-3545) (#2021) (@xarmian)
* 94d60f552e4a6ca42ff9829d14858d77ed843467: fix(web): state the password rule on every password field, and show its refusal there (TASK-2260) (#1941) (@xarmian)
* 022b23e86fbe2a81fd8ff9cda83029a69f0e63a8: fix(web): the auth pages are real forms, with labels, announced errors and a focused first field (TASK-2259, TASK-2236) (#1911) (@xarmian)
* ede34e908659991dba48804e5fc26925baeb4328: fix(web): the balanced fields grid follows the item body, not the viewport (TASK-2209) (#1897) (@xarmian)
* 69fbbe6453ec7c174a3729e198ca0b116eda61db: fix(web): the collection page's search ranks every match, so a filter cannot hide one past the cap (BUG-3710) (#2149) (@xarmian)
* 6071bf361a4394e37cb91261b2fc335eabf43697: fix(web): the collection search box writes the address on a debounce (TASK-2232) (#1939) (@xarmian)
* 5c3ed1b5e7162f14e8568d1e32aa17c631b6a015: fix(web): the command palette and quick-add are real dialogs (TASK-2235 U2) (#1950) (@xarmian)
* a7c559e431e1304c757fe291d755a26d676e5db9: fix(web): the command palette is an accessible combobox, axe-clean in both themes (TASK-2234) (#1847) (@xarmian)
* 4d90f45961d02daa9d473400a98ffaabf2f63341: fix(web): the conventions bulk toggle, the roles board and workspace create show what failed (TASK-2204) (#1928) (@xarmian)
* 3595a3c034e8ff240174a0a112e46c7aee689def: fix(web): the copy and push dialogs send an idempotency key, one per opening (TASK-3597) (#2090) (@xarmian)
* 1d022040e61510d316739dc9a80bde9b549d8c9b: fix(web): the field editor's advanced-section sync no longer depends on the Svelte runtime to stay alive (TASK-2186) (#1841) (@xarmian)
* c1d7988c7a95ce64c770acc07608a3057d95ee92: fix(web): the graph follows the light theme: readable labels, a glow that shows, completed items that recede (TASK-2239) (#1936) (@xarmian)
* b8c9b0ea6bce29535117ac35cddf89d2c34b6783: fix(web): the import dialog shows progress, stops on a stall, and says what was kept (BUG-3475) (#1869) (@xarmian)
* 84ddb3f693d9eb02f6e4127ccc22ef1bb0524bfc: fix(web): the list cursor no longer snaps back while the pane follows j/k (BUG-3204) (#1863) (@xarmian)
* 82f8ecc89810d3f437ac62c723984e122b3b3cce: fix(web): the page behind the palette, a docked sheet or the notification panel is inert (TASK-3520) (#1954) (@xarmian)
* 2e9bfc9a2a0f41c0224a74a3510c6d25bbd8b93a: fix(web): the palette's server searches keep a coll: qualifier as the collection filter (BUG-3709) (#2148) (@xarmian)
* 6ca32c2b147ce95f569cc83b78fc3f7b7e702020: fix(web): the playbook editor offers a built-in's library update (BUG-3852) (#2209) (@xarmian)
* 186ffdba63b790db05f5b6e22c6c47abbdb8f802: fix(web): the remaining native confirm() dialogs ask through the shared ConfirmDialog (TASK-3543) (#2018) (@xarmian)
* bd74960fe917fc8adcf75508a9dc59352190897c: fix(web): the role board reloads when the route's workspace changes (BUG-3701) (#2175) (@xarmian)
* d39cb9f00a150f19bd2a6f04420617613afab01f: fix(web): the selected tab is marked by an accent, not a background step (BUG-3420) (#1829) (@xarmian)
* 9d69d4e4dcb8e1ff23969b3baf85d55a51bc63ce: fix(web): the slash menu and [[ picker open where they can be seen, and [[ has a way in (TASK-2218) (#1952) (@xarmian)
* e091bcc63e4b2972ebe452692e8f05e92f15f1e7: fix(web): the workspace export download is shown only to whom the server lets export, an owner with unrestricted access (BUG-3614) (#2105) (@xarmian)
* bb38641ef71173a4f0f28e0ee3a87f9cdce58a32: fix(web): toasts are announced, errors linger, hover holds them, and an unreachable server says so (TASK-2202) (#1914) (@xarmian)
* fa66181b8827eb706273982b22de1870bd31e19b: fix(webhooks): a DNS failure is retried, and a redirect may not turn the POST into a bodyless GET (BUG-3661, BUG-3662) (#2163) (@xarmian)
* 7ee0bddc45b3a6eb93016dfb25386fb9dd4510fd: fix(webhooks): whole-workspace access to manage; no delivery for a deleted workspace (#1727) (@xarmian)
* f6f588b4d45c78e32f349d148723cbdeb71f074f: fix: a convention's stored metadata copy follows its ordinary fields (TASK-2257) (#1964) (@xarmian)
* 05c039f1317e04e1912cc6969d70dcb7c48eae5d: fix: agents load items with --agent; --format markdown stays body-verbatim and names an empty body (TASK-3451) (#1842) (@xarmian)
* 8c8deeeb898722009f94b3bf10a3eedce4515bc2: fix: an invite asks an existing user instead of adding them; decline; CLI invitations (BUG-2136 U1) (#1831) (@xarmian)
* a91fcce7f97eb52742e42c6d64da5693955b1dde: fix: blank workspaces accept the library's own triggers and scopes (BUG-3446) (#1836) (@xarmian)
* ee288cbebd3463a7b471a76b613869e78c343a36: fix: item lists refuse a filter key that names no field (BUG-3480) (#1880) (@xarmian)
* c81b5c07269b6a855b4fafb31c0d5737abf5075a: fix: owners cannot lock themselves out by mistake; accounts with no password can set one and turn 2FA off (TASK-2190) (#1879) (@xarmian)
* 3aff8e388f1275900c730dec2e83f4cfa3730589: fix: pad keeps an edited /pad skill and never downgrades a newer one (BUG-3466) (#1857) (@xarmian)
* 63e2830c756995de6900c048f65f070691c36ec1: fix: the Live badge reflects a dead SSE connection, and the reconnect catches up (TASK-2197) (#1895) (@xarmian)
* 10a1683b83da878a1d8d42cad4fa18b14d29010b: fix: the access epoch tracks the live collection set; deleted collections leave the local index; the open-children guard ignores them (BUG-3428 phase 2) (#1826) (@xarmian)
* 1d94d038a4d9251b8d1a1195ad175d4fa3fbdd0f: fix: the first-run launchpad follows an onboarding agent live (BUG-3447) (#1837) (@xarmian)
### Performance
* d9978cfb7a1b0fb6e51499993782e7d76061a2c5: perf(web): a board lane mounts a window of its cards (TASK-2230) (#1953) (@xarmian)
* f9713c9fbe6ce0bb7b41a441f7587f64d08c06fe: perf(web): tag and starred pages render from the local index (TASK-2231) (#1938) (@xarmian)
* 4acd2249c026dc05931550917fbd21b411a09ffd: perf(web): the collection page loads the item pane's editor on demand, not before first paint (TASK-2226) (#1935) (@xarmian)
* 1b78add84467399c477c48751310525df4bd6538: perf(web): the editor coalesces its markdown, not its dirty signal (TASK-2232) (#1942) (@xarmian)
### Refactors
* 01fba76bfc6e3de186910eae2db4c426a2038b58: refactor(cli): examples move from Long to cobra's Example field (TASK-2865, part 1) (#2020) (@xarmian)
* cf3cdefd0b2a2bf41c3c82ae060560109fa0b91e: refactor(web): drop the dead terminalStatuses prop chain (TASK-3537) (#2007) (@xarmian)
### Other changes
* 5614980edcd1b096bc1122eafb5632560df70102: Make database restore preserve live data on failure (#1703) (@mattfaltyn)
* 9a7b38ed12ae1684e906d5de968ad66316eceedb: build(deploy): docker compose runs the released, signed image; k8s pins a release (TASK-2034) (#2031) (@xarmian)
* 2c1706fbbb1058ab3ef3cea2573c655f58c58720: build(release): a shipped binary that does not start fails the release before it publishes (TASK-2035) (#1980) (@xarmian)
* e303c16116b3f3f71bdf4dd9abfcf54f0669375f: build(web): jsdom 30 (TASK-2586) (#2019) (@xarmian)
* b454f17928f619b7af6c3503148b03752ecdae8d: build(web): move the SvelteKit and Svelte config into vite.config.ts (TASK-3423, PR A) (#1823) (@xarmian)
* 41456fc7831b43f0897d9420e1040cbd5bf49d87: build: go1.26.9 and x/net v0.60.0 for twelve new standard-library advisories (#1922) (@xarmian)




## v0.18.0-rc.11 (2026-10-15)

## Security / operators

- **BUG-3834 (#2199):** self-hosters who expose pad directly (no reverse proxy in front) should upgrade. /mcp middleware refusals now get the response write deadline.
- **BUG-3839 (#2200), BUG-3820 (#2192):** the History tab could return a 500 for an item with a damaged version row. Fixed: version rows now record their body hash and the walk refuses what it cannot verify (BUG-3820). Version writers no longer diff text that is not valid UTF-8 (BUG-3839).
- **BUG-3825 (#2194):** workspace import now drops duplicate scalar unique-field values and reports them instead of failing. A hand-edited archive with a composite slug collision is still refused.
- **BUG-3835 (#2197) + BUG-3837 (#2201):** MCP's long-lived streams (/mcp listen and SSE) keep alive, take a stream admission slot, and end when their credential does. A revoked session, PAT or OAuth token, or a deleted or disabled user ends the stream at the next check. Streams whose client stops reading now end instead of pinning a handler (BUG-3808 #2182, BUG-3637 #2172).
- Also: a share link serves nothing once its item or collection is archived (BUG-3635, #2167); shared bodies are sanitized with the markdown allowlist and the SPA CSP restricts form-action (BUG-3669 #2145, BUG-3799 #2162); reset-password, register and bootstrap refuse a cross-site form (BUG-3680, #2146); a password change kills outstanding reset links (BUG-3679, #2114); the instance always keeps an active admin (BUG-3811, #2178); the network policy blocks Azure WireServer (BUG-3660, #2155).

## Pipeline

release.yml now smoke-starts each shipped binary and fails the release before publishing if one does not start (TASK-2035, #1980). This is why this is an RC.

## Highlights

**Agents write to items more safely.**
- Content-anchored patch writes work on an item with no live editor, and on one open in an editor they apply as a narrowed replace; `pad item patch --undo` reverses an edit (PLAN-3578, #2055, #2056, #2058).
- Agent body writes are version-checked by default, phase 1: count, warn, replace (PLAN-3555, #2054).
- Idempotency keys for item create, patch writes, comments, notes, decisions, copy/move and push, so a retried request does not repeat (TASK-3585, #2062, #2065, #2068, #2070, #2071).
- `pad item context` / `pad_item action=context` / `GET /items/{ref}/context` return one deterministic brief for working an item; the skill and ship playbook load it (PLAN-3598, #2094, #2099, #2104, #2107). MCP gains reminders, link-pr and typed field writes over stdio (TASK-3611).
- Item leases are held by an opaque worker id, so two agents under one name do not share one (TASK-3613, #2102).

**Editing and collaboration do not lose typing.**
- Closing an item, signing out, or saving a changed body asks first when typing may not have reached the server (BUG-3556, BUG-3571, BUG-3540, TASK-3548; #2037, #2041, #2011, #2025). A tab that dies with unconfirmed edits offers them on the next open (TASK-3606, #2086).
- Op-log recovery refuses an incomplete replay, replays SyncStep2 rows, and sets aside the whole log on a schema rebuild (TASK-3574, #2045-#2047). Dormant op-logs are compacted into one snapshot (TASK-3531, #1984, #1985).
- Markdown round-trip fixes: `<Button>` and `Promise<T>` stay text, bold/italic/strike serialize back, `[[REF]]` from an agent is a link (BUG-3583, BUG-3582; #2057, #2052).

**Storage, billing and reference material.**
- Plan storage limits are enforced at upload: Pro 1 GB pooled per account, Free 100 MB; imports and cross-workspace copies are charged too (TASK-3619, BUG-3653; #2110, #2117). A plan-limit refusal names the limit and who can lift it (TASK-3601, #2080); the billing page says what Pro covers (TASK-3603, #2084).
- A collection can be reference material: its items stop counting as open work and are listed apart from children (PLAN-3535, #1996, #2000, #2005).
- Workspace import reports what it carried, marks a partial import until its owner keeps or deletes it, and a guide walks a self-hosted workspace to Pad Cloud (TASK-3612, TASK-896; #2100, #1923). Import also remaps attachment references in history and indexes wiki-links (BUG-3655, BUG-3656, BUG-3627).

**Web UI: accessibility, dialogs, speed.**
- Native confirm/alert are replaced by one dialog; the palette and quick-add are real dialogs; focus is taken, kept and returned; icon-only buttons and text fields have names (TASK-2221, TASK-2235, TASK-2240, TASK-3515).
- Needs Attention comes first on the dashboard when it has anything (TASK-3588); a filtered view says it is filtered (TASK-3592); set priority from a card (TASK-2214); a parent filter on any collection (TASK-2215); palette search scope is predictable and "All" searches every workspace (TASK-3604).
- Board lanes mount a window of cards, the item editor loads on demand, and lane reorder is one all-or-nothing request (TASK-2230, TASK-2226, TASK-3517; #1953, #1935, #1933). The server gzips what the client accepts (TASK-2225, #1934).
- `pad auth 2fa setup` and `disable` (TASK-403, #1927); the CLI sign-in page has Deny and request context (TASK-2253).

**Bounded lists and concurrency.**
- Item lists, children, starred, shared-collection lists and /changes are bounded at 1000 and page by cursor (BUG-3704, BUG-3789-3792; #2143, #2151, #2153); explicit-limit CLI/MCP callers read every page or say they are truncated (BUG-3793, #2154).
- Checks that read before a lock now re-check under it: unique_scope values, bulk move/tag, moves, legacy adoption (BUG-3812, BUG-3813, BUG-3665, BUG-3806).
- credentials.json is replaced atomically at 0600 and updated under a lock (BUG-3648, BUG-3649, #2170). Every non-stream response gets a rolling write deadline (BUG-3821, #2189).

## Behavior changes

- Lists that used to return everything (item lists, children, starred, shared collections, /changes) now return at most 1000 rows and page by cursor. Scripts calling the API directly should follow the cursor.
- Agent body writes with no version token are counted and warned about (PLAN-3555 phase 1). A future release will refuse them.
- An OAuth or social sign-in whose provider answer has no stable account id is refused (BUG-3671, BUG-3797).

## Deploy notes (Pad Cloud and anyone running the auth sidecar)

- #2144 (BUG-3671) must be deployed BEFORE pad-cloud #80, and #2152 (BUG-3797) AFTER pad-cloud #81. Both pad-cloud PRs are merged. Do not move Pad Cloud onto this image until the order is settled.


## Changelog
### Features
* 3631139de00089b726b98aa41ccf80cba3b71236: feat(acceptance): one Go reading of a body's acceptance criteria (PLAN-3598 slice (a)) (#2091) (@xarmian)
* 4226e8c5ef89bee2233e9b99ea76fa9e0c6cb916: feat(activity): the collection and actor filters run on the server, and the web/CLI badge says which (TASK-2219) (#1948) (@xarmian)
* 28872c24108e4d8ea54a83108c6072b7dbfff236: feat(admin): the MCP audit page names users and connections instead of truncated UUIDs (TASK-2255 C110) (#2032) (@xarmian)
* d5c2ecfe082954a7b03f5c30a52964639b1b36e3: feat(apps): 'via <App>' attribution on items, comments and history, and the members Apps section (TASK-3413, SPEC-6 U9c UI) (#1793) (@xarmian)
* ede0c22fc2824072b43de0e2f87bea6408a94c2f: feat(apps): Settings → Apps: install review, install-code handoff, and lifecycle controls (TASK-3413, SPEC-6 U9a) (#1785) (@xarmian)
* 37066f97bebe713d170a6c3436aa12de94232a86: feat(apps): app attachment routes: item-scoped upload, metadata, and a streamed download re-admitted before its first byte (TASK-3401, SPEC-6 U6c) (#1776) (@xarmian)
* 213ecc0fe315a610ad74f1295b3241353c1b6c2b: feat(apps): app install lifecycle: two-phase disable and rotate, re-enable, uninstall with the tombstone (TASK-3397, SPEC-6 U8c) (#1775) (@xarmian)
* 52dc41b96a5a6c382bcb1fd5c9f5ec66faa535ec: feat(apps): app install provisioning, install codes and redeem (TASK-3397, SPEC-6 U8b) (#1772) (@xarmian)
* ca158c22d8dfe942e327dc2accc163cbf6dcc7fb: feat(apps): app install staging: apps/1 manifest, fetch policy, pending reservations, preview (TASK-3397, U8a) (#1770) (@xarmian)
* 82c45f24cd468fa4e36537db8e641b815dd5e501: feat(apps): app item actions and context codes (TASK-3414, SPEC-6 U11) (#1784) (@xarmian)
* bec344822a5386b9db2643d1ee7d916dfea42227: feat(apps): app upgrade: staged preview with a classed diff, one-transaction confirm that re-derives it (TASK-3397, SPEC-6 U8b2) (#1777) (@xarmian)
* 68e306c76c0b8d84d147a803571a2453834c32fe: feat(apps): app webhook delivery behind an in-flight fence, signature v2 (TASK-3408, SPEC-6 U10b) (#1780) (@xarmian)
* e87ace01e0e3d19f927b386df4a0642cc9c90c20: feat(apps): app webhook events name the install that wrote them (TASK-3411, SPEC-6 U10d) (#1781) (@xarmian)
* 5e2accd17964e9daab594a0a4a75da2de460d1b4: feat(apps): app write routes: items create/update, comments create/update/delete, the write rule, SSE and watch parity (TASK-3401, SPEC-6 U6b) (#1773) (@xarmian)
* aadf3c09d6b2a623d223e4d8cbd5028a67fc8c17: feat(apps): app-owned webhooks, held until redeem hands out the secret (TASK-3408, SPEC-6 U10a) (#1778) (@xarmian)
* 41be1bf1138401334846d3966d1091865e5923a4: feat(apps): human-facing JSON names the app that wrote an item, comment or version (TASK-3413, SPEC-6 U9c) (#1787) (@xarmian)
* 8b8124ab5c972bc967c955e2700b3128c31049bc: feat(apps): item-pane link-out for installed apps' item actions (TASK-3413, SPEC-6 U9d) (#1794) (@xarmian)
* be5457595442f2e1b54d0ee2c7de8499f737ca81: feat(apps): per-endpoint webhook delivery state, a per-install rate cap, and a 24 h drop (TASK-3408, SPEC-6 U10c) (#1783) (@xarmian)
* b0dc7d51e527587e6719b9c8824a8835cfc0d6a6: feat(apps): the app API admits a person's delegated token (TASK-3399, SPEC-6 U5b-2) (#1782) (@xarmian)
* 282a42f69f920cdce5f3111a93ec6fd2b2fa1540: feat(apps): the installed-app API door, ceiling and read routes (TASK-3401, SPEC-6 U6a) (#1771) (@xarmian)
* 9ae4a0be45bf270e51ad3fc23a3bd7a96977987c: feat(apps): upgrade review and draft activation in Settings → Apps (TASK-3413, SPEC-6 U9b) (#1789) (@xarmian)
* 85c49cf2fdc6537c05c9842bee27f4a60288438f: feat(appstore): FencedTx, the appstore skeleton, and the boundary and write-capture guards (TASK-3388) (#1764) (@xarmian)
* 526001c199f8b14cdff4d7f6eec174c2a0de8946: feat(appstore): app attachment upload, read rule and caps behind FencedTx (TASK-3396, U7a) (#1768) (@xarmian)
* 35e4843772e2c0a7f35ae07a9f4ed9653a8b371f: feat(appstore): app comment create, edit and delete inside FencedTx (TASK-3391) (#1767) (@xarmian)
* a17e2c415ebf7ac78d77d7696b481b96c7914cdf: feat(appstore): app item create and field update inside the fence (TASK-3390) (#1765) (@xarmian)
* 55db86f68e5e7d9e7641ead86e5faf546fa26cec: feat(auth): Deny and request context on the CLI sign-in approval page (TASK-2253) (#1943) (@xarmian)
* 70c57f82029937fc703856bbc32f7c34ff4f9467: feat(auth): a first Cloud signup lands in its new workspace; OAuth comes first (TASK-3595) (#2075) (@xarmian)
* cc85c2f9da8dca6d78705974066c6950f3baca2d: feat(auth): social claim of a never-verified account, provider subjects, cloud-only sidecar routes (TASK-3351) (#1760) (@xarmian)
* b572f0739ca563c9ec6d302fcd8661e23f914e4b: feat(auth): the bot principal for installed apps: users.kind, kind gates on every sign-in door and credential, people-only counts (TASK-3392) (#1766) (@xarmian)
* d6a45bf339ee868029a9f416cd1acbfbe618468e: feat(billing): billing availability and prices come from the sidecar; PAD_BILLING=auto|off (TASK-3577) (#2048) (@xarmian)
* f3f90d0366d6532e625c09c706f65f64438142e3: feat(billing): the billing page says what Pro covers and who pays (TASK-3603) (#2084) (@xarmian)
* e8d680b135be7fcb5514f1aee80d9b6ed7e7cca1: feat(brand): the Pad mark is the brand: one vector master, the app's icons, header and link card from it (TASK-3514) (#1926) (@xarmian)
* d15b31077a1730c4954d14579406149dff7151e7: feat(chatgpt): a reset-and-verify script for the reviewer's demo workspace (TASK-3321 G8) (#1718) (@xarmian)
* 1339916b9c10e76761a44bf98adf22389e8be8e3: feat(chatgpt): serve OpenAI's domain challenge at /.well-known/openai-apps-challenge (TASK-3321 G4) (#1717) (@xarmian)
* 809d497399a165ae7ca0cab45b3b631d267b09f4: feat(chatgpt): the Pad plugin package for OpenAI's plugin directory (TASK-3321 U4) (#1712) (@xarmian)
* a55d15dbea4aa8674bf79fff914f5c40b0336e05: feat(ci): an advisory dependency-age check (cmd/depages) (TASK-1391) (#2014) (@xarmian)
* a896edf067dd22dce11fca519475e0c522dc8973: feat(cli): pad auth 2fa setup and disable; disable asks for the password, or a code on an account without one (TASK-403) (#1927) (@xarmian)
* 1d4f0606d9a990f3b78f28813e076a6ab71f8fbb: feat(cli): pad init points Claude Code users at the pad plugin (TASK-3488) (#1898) (@xarmian)
* 99aac1687bc75ad583455b83595db017a352d632: feat(cli): pad library diff and pad library update for built-in conventions and playbooks (TASK-3462 U3c) (#1875) (@xarmian)
* fbba819eb8d888a00134c8132c92f1f3c73a0032: feat(cli,mcp): pad item context and pad_item action=context (PLAN-3598 slice (c)) (#2099) (@xarmian)
* 8eebefde57cc3a319491d4e7cd5f5a6dcd1ed9ca: feat(cloud): GET /admin/billing-users pages the users the reconcile sweep re-syncs (TASK-3564, pad half) (#2042) (@xarmian)
* 3201342d3d68c134a22f1bdb993b48fb36612bce: feat(cloud): a Stripe event marker is a claim with a lease, so a handler that dies does not lose the event (BUG-3561, pad half) (#2043) (@xarmian)
* 772c1a86ba1c949a17e33049381f0e4fff54fe8b: feat(cloud): the Stripe customer link is compare-and-set, and readable by user (TASK-3549) (#2027) (@xarmian)
* bc3e23d55a8a766c281ba603ba35ce7de1623cfc: feat(collab): a patch to an item open in an editor applies as a narrowed replace (PLAN-3578 step 2) (#2056) (@xarmian)
* f67861218460b734b0085634823a100a89225da7: feat(collab): a peer that drops without saying goodbye loses its caret at once (TASK-2206) (#1932) (@xarmian)
* 1a803893414fe123dab1b9fcb3faaddab6d7481d: feat(collab): compact a dormant op-log into one Yjs snapshot (TASK-3531 U1+U2) (#1984) (@xarmian)
* 4f6d087232eac5e2fe96d5c749cd942651e0d6bd: feat(collab): count and log watermark stamps that cover content-bearing rows (TASK-3541 step 0) (#2023) (@xarmian)
* 3e8bf36f3d9cfa82cc8ddd9abf0e25eb2625f19a: feat(collab): count failed op-log appends (TASK-3574) (#2051) (@xarmian)
* 9a99f06c874c55b9184135114cc2475a01fee001: feat(collab): count resumes and force_refresh on resume, to measure offline editing (TASK-3501) (#1908) (@xarmian)
* 23c8e4f811be35385a33b2f322e5db9cc24c9ab0: feat(collab): the GC compacts dormant op-logs and a covered resume merges (TASK-3531 U3-U5) (#1985) (@xarmian)
* 4532eecffdeac4eeff1cd159ff1353df1ccac07b: feat(decision): conventions ask about the item without its comment trail, 12 questions a call (TASK-3119 U2a) (#1871) (@xarmian)
* deec62235ed433677818db2ec09773b1c7b12ff1: feat(decision): executable conventions, the server half (TASK-3119 U1a) (#1859) (@xarmian)
* cc1aa6902c6e75febf688096217be7d30c2b2510: feat(decision): log each evaluation's spend (TASK-3119) (#1861) (@xarmian)
* 8eb4519fe7c4678e1e6af2f55beef0d197ffd28b: feat(editor): a tab that dies with unconfirmed edits offers them on the next open (TASK-3606) (#2086) (@xarmian)
* d94a38978f2b1cca3379626291ff0cfabd8649e5: feat(import): a bundle import reports what it carried next to what arrived, and a guide walks a self-hosted workspace to Pad Cloud (TASK-3612) (#2100) (@xarmian)
* 136fac66098e7a3ff5f99e54995caf09dae1f07c: feat(import): a partly imported workspace is marked until its owner keeps or deletes it (TASK-896) (#1923) (@xarmian)
* 82395bde1cb7436bad7695c0594002b953817ba8: feat(import): mark rows a workspace import wrote, author not verified (BUG-3379) (#1755) (@xarmian)
* 0929f6570558b4c57148a0f0bb3fabfd15089677: feat(invitations): a mailbox-only proof on invitation emails verifies the invitee (TASK-3352) (#1757) (@xarmian)
* bc329fb7f47d70094f2963a90dbee89ccf52736b: feat(items): agent body writes are version-checked by default, phase 1: count, warn, replace (PLAN-3555) (#2054) (@xarmian)
* 0cc033edd889544c9d5cafbac45f4761ba96d63f: feat(items): content-anchored patch writes on an item with no live editor (PLAN-3578 step 1) (#2055) (@xarmian)
* 493498c977b986faf4258b4b42118b19d2385929: feat(items): idempotency keys for comments, notes and decisions; idempotency_target_gone is structured (TASK-3585) (#2068) (@xarmian)
* a05197c795d9602c3d9f6156df696fb575d243a5: feat(items): idempotency keys for cross-workspace copy and move (TASK-3585) (#2070) (@xarmian)
* c46ecc4cf865a345bc10c08aac7ffa2c297d7e3f: feat(items): idempotency keys for item create (TASK-3585) (#2065) (@xarmian)
* 7ec0191d450f229ea26b2d66b5a86d0d1b74b7b3: feat(items): idempotency keys for patch writes (TASK-3585) (#2062) (@xarmian)
* 78729db1a9b132e5554e67a1b3c8399003ee6a77: feat(items): pad item patch --undo, anchored on each edit's context (PLAN-3578 step 3) (#2058) (@xarmian)
* 43d7e050427638ef205921605a2caf1b1b0cdc6d: feat(items): restoring a kept draft applies only your changes, so a newer version is kept (TASK-3607) (#2093) (@xarmian)
* a6f96107f42b1123da3e442547ba4926a58f529c: feat(lease): an opaque worker id holds item leases, so two agents under one name do not share one (TASK-3613) (#2102) (@xarmian)
* 2dc5ac7058efb6ae0ff476ad46dddaa06259a9de: feat(mcp): ChatGPT item_history names who made each change; email-shaped names are masked (TASK-3321) (#1716) (@xarmian)
* d3b1209d04b9f0cee0cb8590115e5ab6e1a54a16: feat(mcp): ChatGPT responses are minimized through per-tool allow-lists (TASK-3321 U3) (#1713) (@xarmian)
* 26fd8a6a46a6eecc1f1dbc90a475307b2f033489: feat(mcp): ChatGPT tools declare their OAuth scope; a missing scope answers the sign-in challenge (TASK-3321 U2c) (#1720) (@xarmian)
* 0b0398b2c08ad63e0ddb8bce0d2b4b633ec4aef1: feat(mcp): count admitted MCP requests by method and client (TASK-2307) (#2003) (@xarmian)
* 6118f7065c43c61253fbe2a7b8cfb8eb5b36a023: feat(mcp): mount the ChatGPT catalog at /mcp/chatgpt, OAuth-only, off by default (TASK-3321 U2b) (#1719) (@xarmian)
* 1204a31a73950bf2bfbadda651e5e79333a03814: feat(mcp): pad_item link-pr links a PR from supplied metadata, and unlink-pr removes it (TASK-3611) (#2098) (@xarmian)
* bcb8d93516b71be3df7cb83780a1d1047b076377: feat(mcp): pad_item reminders lists an item's reminders and unremind disarms one (TASK-3611) (#2097) (@xarmian)
* 0c0874dc10f0c7e926983ceef0f089de428cd66e: feat(mcp): pad_item.history rows name who made the change (ToolSurface 0.63) (#1714) (@xarmian)
* eb987af709253d3d349921edcf1172baca02d07a: feat(mcp): pad_workspace destructive + open-world (invite emails), pad_playbook open-world (TASK-3321 U0b, ToolSurface 0.61) (#1707) (@xarmian)
* 58be45b35e97c8e615fc7948470c58f1d5f66e42: feat(mcp): remote /mcp writes are agent writes named by clientInfo; refused claims say lease_held (BUG-2772, BUG-3496) (#1903) (@xarmian)
* add4b624bdbb8e318ab7c2d57ea107cf2d3e7d22: feat(mcp): scope in the /mcp challenge, and a 403 insufficient_scope for read-only OAuth writes (TASK-2308) (#1986) (@xarmian)
* f2a1ca75e32b665c9ab069ce2c87dd6fb7b2a001: feat(mcp): structured and typed field values write over local stdio too (TASK-3611) (#2096) (@xarmian)
* 39a52595518cbeb1852f0b9eaf5a0b89a0393618: feat(mcp): the ChatGPT catalog, a one-tool-per-operation projection of /mcp (TASK-3321 U1, stacked on #1707) (#1708) (@xarmian)
* ed7219e2e72c12030f75e14fd860c7354ad00b5b: feat(oauth): RFC 9207 iss on every authorize redirect; JSON 404 for unowned /.well-known (TASK-3321 U0a) (#1706) (@xarmian)
* 5c53aae306fc61fbb283dbfa24afa1bac20c22c4: feat(oauth): a second canonical resource, with every token bound to one (TASK-3321 U2a) (#1715) (@xarmian)
* 681780486f42c7830b98955f4b32f2a2dcd23a4f: feat(oauth): count and log requests that omit the RFC 8707 resource (TASK-3363 phase 1) (#1748) (@xarmian)
* 7396ec42bbdfd5902ada9b202a983ff8f4059209: feat(oauth): delegated sign-in for installed apps through the issuance barrier, shipped closed (TASK-3399, SPEC-6 U5b-1) (#1779) (@xarmian)
* e5262160e115ac39258a9c622e819055234d0e2b: feat(oauth): install clients, service tokens and the issuance barrier for installed apps (TASK-3394, SPEC-6 U5a) (#1769) (@xarmian)
* 6066d42115b77b030c7dd2c3523ad18975cc3681: feat(outbox): freeze an app-projection block into item and comment events (TASK-3389) (#1763) (@xarmian)
* 5c598a18d3de5f72745787156248791cd2a3a4c5: feat(plugin): no event monitor at session start; an opted-in session's watch starts from the mod, and an unarmed one shows nothing (TASK-3513) (#1925) (@xarmian)
* b66af1e624c7736f92b62ea633bb57cc60263a56: feat(plugin): the Pad pane ships in the pad plugin (/pad-pane) (TASK-3486) (#1883) (@xarmian)
* 09135d15c557626b937905e70550008bbb92a433: feat(plugin): the pane's Get started view: Pad Cloud, this machine, or your own server (PLAN-3490) (#1888) (@xarmian)
* ccd915f1cc45f02395d0c7ca2a6111d296eef635: feat(push): idempotency keys for push, and the monitor drops a re-published push (TASK-3585) (#2071) (@xarmian)
* 0bdf539455e88dbcb26af4a3fdae16b592f4b0a7: feat(release): the Claude Code plugin follows stable releases; the release workflow pins the marketplace (TASK-3487) (#1890) (@xarmian)
* 480c5d351a229d8e8d7f1a20d5a255c1859931e5: feat(report): Insights buckets days in the viewer's time zone (TASK-3524) (#1955) (@xarmian)
* f61a07fe9ade952f4c9c296d8dc4e76488b054c9: feat(search): include_archived on /search, and an is:archived search token (TASK-2864) (#2001) (@xarmian)
* aa7bdd4f15ae6b4bfe84587ed4c77e9216373737: feat(server): GET /items/{ref}/context, one deterministic brief for working an item (PLAN-3598 slice (b)) (#2094) (@xarmian)
* 5c9c650ac39f04e6e7d219f036689bd09016378e: feat(server): a read-scoped token may run a playbook (TASK-2863) (#1987) (@xarmian)
* 56922e790a9fb3f0a2d9f4b139fd497816c1764f: feat(server): every access and credential change re-checks live connections (#1746) (@xarmian)
* 95046c9b3b519dca517444d5916c32ba5ebe90b2: feat(server): gzip what the client accepts, except streams, upgrades, ranges and secrets (TASK-2225) (#1934) (@xarmian)
* 560ab27b337edc69b569462655ff09c0c8000c38: feat(server): reference items stop counting as open work (PLAN-3535 PR 2) (#2000) (@xarmian)
* 484ca668a38c138e1a68130b37fef372c303450f: feat(server): revoking access re-checks live connections immediately (#1744) (@xarmian)
* 312a73c39a678dd12bc6f2490a99c89247f76cc5: feat(server): the health probe gets its own per-address rate-limit tier, and the search burst is 30 (TASK-3620 PR B) (#2108) (@xarmian)
* 559d9d1422e1d88ffb08860ce12f80b30be7a34c: feat(server): the item brief carries only the decisions Pad would surface, and counts the rest (TASK-3618) (#2107) (@xarmian)
* ff6d280bccc46d4ec1889395471175c37953cb40: feat(skill): the skill and the ship playbook load an item's brief with pad item context (PLAN-3598 slice (d)) (#2104) (@xarmian)
* aa49db396ee34bd7c5c64ecd632b8b2c31a01225: feat(storage): enforce plan storage limits at upload; Pro 1 GB pooled per account, Free 100 MB (TASK-3619) (#2110) (@xarmian)
* dab3acd1f1852b2cf882f735169eff8e79cb5a20: feat(store): a read-only diagnostic counts version tie groups migration 054 may have misordered (BUG-3751) (#2136) (@xarmian)
* bdea49af64bc208597c098daab02ca9d4c569f76: feat(store): copy a convention's role field into its role column at startup (PLAN-3598) (#2092) (@xarmian)
* 10f722e9fed443be9318a2bbe37518c541d2eff9: feat(web): "Possibly breaks CONVE-N" chips on the item page (TASK-3119 U1b) (#1860) (@xarmian)
* b831e9fe097e52d82c3c21cdccb9f41ae06da498: feat(web): + badge, Decline, and an accept/decline card on invitation links (BUG-2136 U2) (#1833) (@xarmian)
* d0ee9afaef78797030ec253e8cc983f32216722e: feat(web): Add Relationship offers both directions and says which way each points (TASK-2217) (#1957) (@xarmian)
* 697ce2d4495718c9650c9a493941d46935ab3351: feat(web): Needs Attention comes first on the dashboard when it has anything (TASK-3588) (#2064) (@xarmian)
* c78037adbf4a6f56334fd442a322af42509de667: feat(web): a Library link in the sidebar's Agent section and the mobile sheet (TASK-2258) (#2013) (@xarmian)
* fac299d9db87b91c27bd722c32cfd0c8eb052057: feat(web): a Rotate button on API tokens (TASK-3505) (#1915) (@xarmian)
* edb20ae6134ae24c709b8b6f36fb651245439100: feat(web): a filtered collection view says it is filtered (TASK-3592) (#2072) (@xarmian)
* 8efce995d9895095f7e0779226a95ad1a422dc34: feat(web): a parent filter on any collection, from the parents its items have (TASK-2215) (#1958) (@xarmian)
* 910a1aeb8d8d6f3fbdec954b963b5857f9403848: feat(web): batch other actors' creation toasts; only their events count as unread (TASK-3593) (#2073) (@xarmian)
* 6735b43450ab9386a265ff012d5afec6553c36b4: feat(web): cap the dashboard's attention and plan lists, with a Show-all toggle (TASK-2210) (#1896) (@xarmian)
* 6903eeeea5ee31c9baefc1b793a0ec973b822a70: feat(web): choose monthly or annual Pad Pro at checkout (TASK-3468) (#1856) (@xarmian)
* 4ac7f16084798348ed3b0cf2b977cfba47d70851: feat(web): gapped sort keys, so a reorder is one write (TASK-3525) (#1975) (@xarmian)
* 77b2c256fd719bac528e92dcb6f0109fc83864fb: feat(web): list group headers get the board lane's bulk actions (TASK-2222) (#2012) (@xarmian)
* c62b2b80da675e4e7b7fe27f867b285036348d57: feat(web): quick capture keeps your place (TASK-3590) (#2067) (@xarmian)
* 88a26afde03d550e0d410c41c82966ca0fe47ea9: feat(web): reference children are listed apart and leave progress (PLAN-3535 PR 3) (#2005) (@xarmian)
* 28501155b1b67b088af81a236e8b869f1111e1c0: feat(web): review and accept built-in updates from the Library page and the item pane (TASK-3462 U3b) (#1873) (@xarmian)
* b034236eb3dd77ef556bd1d07a27e7a6585190ca: feat(web): set an item's priority from its card (TASK-2214) (#1956) (@xarmian)
* 439bda2278fb22438a7f4682fe336f6e9fd15d64: feat(web): the auth pages follow the theme, with a toggle that survives sign-in, the Pad grid mark and a slim self-hosted header (TASK-3509) (#1924) (@xarmian)
* ebb293627230243934ebfc259c0eacfc654b23ed: feat(web): the mobile view sheet lists saved views and "All" (TASK-3589) (#2066) (@xarmian)
* 1ed71b0ecfa5cdd2a7d37637f1fc2d5ff571f878: feat(web): the playbook editor and collection dialogs keep a draft; Save stays; the arguments section is edited in place (TASK-2191) (#1882) (@xarmian)
* f6938b33a5d9aa5a68f61db127784afef7f55f2b: feat(webhooks): owner webhooks keep per-endpoint delivery state; 408/425/429 are retried (TASK-3409) (#1809) (@xarmian)
* f5a00d5b13da8855de7941d7356145c15b151766: feat: a collection can be reference material, not work (PLAN-3535 PR 1) (#1996) (@xarmian)
* cff306e05add177205a64ebcf2ddd940214ede50: feat: a plan-limit refusal is a persistent prompt that names the limit and who can lift it (TASK-3601) (#2080) (@xarmian)
* 9d2572eb7ba6f51a99be88743adde857c7f35730: feat: adopt pre-origin conventions and playbooks as built-ins, once, by exact title (TASK-3462 U4) (#1878) (@xarmian)
* 15c9f76366fc03bfbb03c8ddaff432cdaf4789c5: feat: archived collections can be listed, restored and undone; the archive confirm shows the count (TASK-2189) (#1874) (@xarmian)
* a23edba8561a4c0f25c9da231dd6b9a8f7484de5: feat: built-in update count in the bootstrap, and accepted updates record replaced fields (TASK-3462 U3a) (#1868) (@xarmian)
* c17865462f1568130861e9176dbb1a251d6551c0: feat: built-ins record their origin; an item made from one can be offered Pad's current text (TASK-3462 U1+U2) (#1852) (@xarmian)
* 5adbe0479739a694087b25d67a353f6b3e305adb: feat: bulk sort_order: one all-or-nothing request per lane reorder, one activity row per item collapsed per batch (TASK-3517) (#1933) (@xarmian)
* 79922d4bab09afa0d51b3a94d6a5e7fce0ee84bd: feat: conventions checked on each comment alone, with the chip on its card (TASK-3119 U2b) (#1872) (@xarmian)
* bc2a982591517708ac75b137486a11387f249a84: feat: every content change through the ChatGPT door is versioned first (TASK-3321 U1b) (#1711) (@xarmian)
* 4fdc6ed625758d73006dd0f4f04e1586d9351a2c: feat: in-app tutorials on Pad Cloud, links to getpad.dev/learn elsewhere (TASK-3452) (#1839) (@xarmian)
* 8d02818fd68825d241cd841a1b5731c063453e78: feat: leases default to the agent's name, and next/ready leave out others' leased items (TASK-1809) (#1900) (@xarmian)
* 1c23a1bcbcb911f58ce6b21189af36a34cacd073: feat: onboarding asks where an existing project's open work lives and offers to bring it in (TASK-3454) (#1853) (@xarmian)
* 3ffe879dee0ed3ffb36846f100047fe35b254590: feat: predictable palette search scope; "All" searches every workspace you can see (TASK-3604) (#2085) (@xarmian)
* 7b68125a30d811746fa71604ef65d03bb255ed72: feat: schema edits say what they do to items; removing an option is never a rename (TASK-2188, TASK-2187) (#1877) (@xarmian)
### Bug fixes
* 3bcef0e04da3d1f7e0aa91c32149edd5ee953c63: fix(access): system collections are ordinary collections for restricted members (TASK-3376) (#1756) (@xarmian)
* 3d21213b5781d5e19597e42698b661f19363b4c1: fix(account): account deletion needs an interactive, recently signed-in session (BUG-3336) (#1733) (@xarmian)
* ff9b9f3579a58f42fa9190d734382d74027d8e23: fix(account): account export reads run inside the deadline, from one snapshot per workspace (BUG-3659) (#2160) (@xarmian)
* 3a49a849081c0f3895046a804ce0df6da5b3d690: fix(activity): the feed and dashboard count only rows the caller may see (BUG-3687) (#2169) (@xarmian)
* 18000593688e2201e7c7399369d24f828f85f12a: fix(admin): the instance always keeps an active admin; demote, disable and self-delete share one locked guard (BUG-3811) (#2178) (@xarmian)
* 9bd191048d2880e88540d7437326de8bd0a7f1c9: fix(api): /changes is bounded at 1000 and continues by a cursor on the write order (BUG-3791) (#2151) (@xarmian)
* 30ba2ed3040f9662236960b389c2e8514ae60d80: fix(api): body-supplied IDs must name something in the authorized workspace (BUG-3346) (#1728) (@xarmian)
* fc9ceae92f8eca26edfa2e28dc35bb5aa3ee1e7f: fix(api): children, starred and shared-collection lists are bounded at 1000 and paged; MCP starred caps at 300 (BUG-3789, BUG-3790, BUG-3792) (#2153) (@xarmian)
* 858bd8514e89f18e6e3995ae297160e12e8047ab: fix(api): item lists are bounded at 1000 with has-more paging, and filter-key probing is bounded (BUG-3704, BUG-3703) (#2143) (@xarmian)
* 2246ea6f04294e13e6aff48cbbad319844029a32: fix(apps): a collection-restricted owner cannot grant an app whole-workspace access (BUG-3768) (#2123) (@xarmian)
* 4f277f836a345d86ea212a4581b37b6e1855572d: fix(apps): an app upload is charged against the plan's storage cap (BUG-3653 part B) (#2119) (@xarmian)
* 95ae3adbd91e944fe85d7a81a174257d590e0ac6: fix(apps): an installed app learns its workspace from the redeem, an unscoped /me and every webhook (BUG-3416) (#1797) (@xarmian)
* a04e35a67de6d72a39ebb9c0b2d0508fab3d6139: fix(apps): every list in an apps JSON response is a list, never null (BUG-3417) (#1796) (@xarmian)
* 83ca50f86111d50c1e65fa88d0935b9753b6c372: fix(apps): the apps UI tolerates null lists from the server (BUG-3417, client half) (#1795) (@xarmian)
* 17cbfa236e251a9db19e10ecd079a83c38936fae: fix(attachments): a refused upload, transform or import reclaims the blob it wrote (BUG-3652) (#2118) (@xarmian)
* 4e3988300f8b1b965e499ecf6c5a56de68441f72: fix(attachments): a thumbnail takes its original's binding at insert time (BUG-3385) (#1762) (@xarmian)
* 67d06fdf81941c45061268c339134c35c464b352: fix(auth): a CLI session is never a browser cookie, and sign-in refuses a cross-site form (BUG-3350) (#1747) (@xarmian)
* 15ffd0528604a3b3d798cb32400399808c7b34ed: fix(auth): a password change kills outstanding reset links (BUG-3679) (#2114) (@xarmian)
* 241dd316f9af5b780e3faba9ca9814c2193f7398: fix(auth): a social sign-in without a provider subject is refused on an account with one bound (BUG-3671) [deploy BEFORE pad-cloud #80] (#2144) (@xarmian)
* 551a338cbd92a80094b23024fa31f9004a29da80: fix(auth): a user-less legacy workspace token reaches only its own workspace (BUG-3353) (#1734) (@xarmian)
* 98871c7e017a459a63ba17f9db07aefcc5cef555: fix(auth): a verification link verifies only for its account's session; the mailbox owner can claim (BUG-3382) (#1758) (@xarmian)
* 7b41a0298ee46963a0e78d1e37a2f8647ab88dcc: fix(auth): account deletion's 2FA code goes through login's limiter and single-use claim (BUG-3482) (#1881) (@xarmian)
* ec5b60679a58c1e739ae0b0025ed51ff57269d0f: fix(auth): an OAuth sign-in without a provider subject is refused, bound or not (BUG-3797) [deploy AFTER pad-cloud #81] (#2152) (@xarmian)
* 66b4a9d4773fc0725a017a5132b4f87941a41523: fix(auth): disabling an account ends every credential, and a disabled account gets no new one (BUG-3349) (#1741) (@xarmian)
* 2bd0862af2d42daece3306248f9e93a0f96498bc: fix(auth): platform administration refuses an API token (BUG-3361) (#1742) (@xarmian)
* d4e69a566b7d1bbd27c9ab577fd15bd3e8e8f151: fix(auth): reset-password, register and bootstrap refuse a cross-site form, as login does (BUG-3680) (#2146) (@xarmian)
* 1f391d959187dd1d3277dbffa09cbf0e9a6b8508: fix(auth): store errors on access decisions fail closed (BUG-3334) (#1730) (@xarmian)
* db62001ad4ddf5932c3dadb8523fc03880f9c894: fix(billing): a plan past its expiry entitles nothing, and Stripe plan writes are ordered (BUG-3356) (#1753) (@xarmian)
* fb71a913411cff17d2aeca9f5d01348322412d1b: fix(billing): account deletion proceeds past a sidecar 400 only for the old sidecar's empty-customer refusal (BUG-3560, retro of #2036) (#2076) (@xarmian)
* 5d344d2b880641b4f0d1e77a4af26890d7ab9659: fix(billing): admin stats count upgrades by when the account became Pro (BUG-3591) (#2069) (@xarmian)
* 82064526e32d9c3267b91f0fe206d341d5ec0a48: fix(brand): name the entity as Perpetual Software LLC everywhere (TASK-3321) (#1722) (@xarmian)
* ad6cfc2c5e53198732e204c59f6f833d4067357b: fix(cli): a bundle import shows progress, abandons a stalled upload, and resolves a lost answer (BUG-3476) (#1902) (@xarmian)
* 22dcce6e6c09486851b39cadc73b32f0d4f63e11: fix(cli): a failed stat fails the credentials write instead of skipping the truncate (BUG-3810) (#2181) (@xarmian)
* 1d08594dc0f5be84f97eece5f8936abe9ace2637: fix(cli): a locked credentials load re-reads an empty file before believing it (BUG-3829) (#2195) (@xarmian)
* 223c9734d8041de100c7f2a1d972a92fa13e532c: fix(cli): a workspace or ref string cannot re-route a request, and PAD_TOKEN is not sent to a server only .pad.toml named (BUG-3645, BUG-3646) (#2127) (@xarmian)
* e17f17f51335800fa40e6bb5a0aff1f98fe73f43: fix(cli): an empty credentials file read without the lock is unknown, and UpdateStore will not save over it (BUG-3828) (#2187) (@xarmian)
* 90a304765fa6e2a5d1a2cb61f9b73ebdec6371c4: fix(cli): copy --dry-run previews a big number with every digit (BUG-3456) (#1858) (@xarmian)
* a99a040cf3b5b6a7e844944a8fa3ad7dbb7f99ca: fix(cli): credentials.json is replaced atomically at 0600 and updated under a lock (BUG-3648, BUG-3649) (#2170) (@xarmian)
* c204dd3683fc995f2c4d860946f6097353715894: fix(cli): json fields print as JSON, metadata labelled for the item's kind; MCP 0.68 (BUG-3448) (#1838) (@xarmian)
* 833e309052d2d0843069eb4b8335d83472b6557f: fix(cli): whoami says what a failed check established, and exits non-zero (BUG-2706) (#1901) (@xarmian)
* 47fe81ab99782704c6a360b8646e9d1aa0338ed5: fix(cli,mcp): explicit-limit callers read every page or say they are truncated (BUG-3793) (#2154) (@xarmian)
* 0ecec8235708420c58354d97ffd0b3fb59329b54: fix(cli,server): a rate-limited health probe no longer starts a second server, and a start that loses the port touches nothing (TASK-3620 PR A) (#2106) (@xarmian)
* ba35908f2b2e79666e4725d8961594b6543e13d8: fix(cli,web): link re-points a directory to another server and keeps .pad.toml's other keys; the move-to-Cloud guide is browser-only (TASK-3612) (#2103) (@xarmian)
* 9f5483049d5679bbf1866b35a0821ac9226729f8: fix(cloud): a failed read of a Stripe event row is not a claim (BUG-3561) (#2083) (@xarmian)
* e3e76daae3eaf02a55c32bb6e023447aec352276: fix(cloud): account deletion asks the billing sidecar by user, so every Stripe customer the user owns is cancelled (BUG-3560) (#2036) (@xarmian)
* 5caf11f829fbe55d67fda16ea642bfdef75e122f: fix(collab): a REST content replacement fences tabs seeded from the old body, as a restore does (BUG-3746) (#2134) (@xarmian)
* 134d0a4e89a4abb69f6711899c6134d08cf74a36: fix(collab): a compaction snapshot covers only its own generation's cursors (BUG-3747) (#2142) (@xarmian)
* e64abacec3c78716ce684a021419544b5c1e530c: fix(collab): a delayed browser snapshot cannot overwrite a body built from more ops (BUG-3744) (#2132) (@xarmian)
* 6ed3c09f54e30d0671405b8be518c3a07f20059b: fix(collab): a markdown applier request that timed out is not re-sent to another tab (BUG-3748) (#2133) (@xarmian)
* 16a0243c5e48295bdc17c48125ad1dd390c37a97: fix(collab): a multi-block patch into an open editor leaves the unchanged blocks between edits untouched (PLAN-3578) (#2082) (@xarmian)
* ae52c96d02e3ebda76b66751752735d8a73f85e4: fix(collab): a patch whose applier times out is not re-sent to another tab (BUG-3586) (#2059) (@xarmian)
* db6f0cde1f1f2bedae245a4fa2e13cf58621b655: fix(collab): a schema rebuild sets aside the WHOLE op-log, so set-aside edits can be replayed (TASK-3574 (4)) (#2047) (@xarmian)
* 602ce1006ba912ac5db5b553e5f41a3208baf5a9: fix(collab): a websocket peer that stops reading or answering is closed within a bounded time (BUG-3771, BUG-3636) (#2124) (@xarmian)
* 64e6dfb68c051143ce9a1ce18a44a5f3b0482721: fix(collab): an applier ack reports persisted only when its bracket held no failed append (BUG-3749) (#2131) (@xarmian)
* 5960cf1978e60a0c10852c52479abc4791028afe: fix(collab): an open tab refuses a content write over typing the server has not stored (BUG-3542) (#2016) (@xarmian)
* 2898bff09e67a3505594464934c240bf62832102: fix(collab): close a peer the op bus had to drop an op for (TASK-1273) (#1981) (@xarmian)
* d90ac1ebd14ddf9eb8776086ece39232250f385f: fix(collab): persist a typed burst's waiting frames in one transaction (BUG-3253) (#1909) (@xarmian)
* 78ec772226b5fa53ed7516f51290186494bd38f8: fix(collab): recovery refuses an incomplete op-log replay, and a failed compaction snapshot keeps the log (TASK-3574 (1) and (3)) (#2045) (@xarmian)
* d93a94a42caffb327e52cce3ef77f719ba704975: fix(collab): recovery replays SyncStep2 rows, which can hold the only copy of an edit (TASK-3574 (2)) (#2046) (@xarmian)
* 416aea2d14d362bfee49c1ba9b922c503d4ebd99: fix(collab): stop appending the whole document to the op-log on every reconnect (BUG-3523) (#1965) (@xarmian)
* a5409ed2e11db3897d5f7db309c33c08665ffb4e: fix(collab): the editor is read-only through a force_refresh recovery, so no typing is lost (BUG-3697) (#2128) (@xarmian)
* 33e7a503d512e8676d7a0fc72afc091637e5ef22: fix(dashboard): a task under two active plans no longer pins the skeleton (BUG-3538) (#2002) (@xarmian)
* 1fe9a1503787b8bfea8079d6b1d89ea014d0d0ad: fix(deploy): Kubernetes keeps attachments on a PVC, and uploads get a writable /tmp (BUG-3714) (#2141) (@xarmian)
* 6fd59627bd039a0956c328d24256a98a7fbd0fd5: fix(deploy): the Kubernetes manifests run one Pad replica with Recreate and no autoscaler, since collaboration needs a single writer (BUG-3573) (#2039) (@xarmian)
* 09ecc5e02faa697fa42186606e01047272b50479: fix(diff): version writers never diff text that is not valid UTF-8 (BUG-3839) (#2200) (@xarmian)
* daf94614ca7d8cee710a2ef0c05a88e8646c40ca: fix(documents): restore only a document of the URL's workspace (BUG-3335) (#1724) (@xarmian)
* 08a5f1c7d24a7e3e9fff156d2acab2dcdbb03efa: fix(editor): a block marker after a hard break stays text (BUG-3584) (#2060) (@xarmian)
* 6d3842b1f7ec1d59fc6f43a846346c359a0bbe9d: fix(editor): a line-start marker followed directly by marked text keeps its form (BUG-3600) (#2079) (@xarmian)
* 8d910dc20a0e777b9bc6db999635161b3dca0086: fix(editor): bold, italic and strike always serialize to markdown that reads back (BUG-3583) (#2057) (@xarmian)
* cfc5391581f28c94af5ffa8514a4e660a1f5942d: fix(events): a corrupted event sequence counter heals visibly into a new id space; the id is read back, not rendered through a double (BUG-2744) (#1906) (@xarmian)
* 828b656e924ea83ab087ee667f6edbe08e5d0f81: fix(export): an export reads one snapshot, so a concurrent write cannot leave an item without its collection (BUG-3654) (#2122) (@xarmian)
* 3b27a138e496455daf34b1efa2ba8243b14396b6: fix(grants): an item grant never opens a deleted collection (BUG-3333) (#1725) (@xarmian)
* 0978b9d818ac82c703291453b1d07f371fc7a784: fix(import): a bundle is not complete until its gzip footer verifies (BUG-3657) (#2158) (@xarmian)
* 3fe40aeff7f08eb8ef5a9ff75fe65b0d80dcbaa6: fix(import): bound the work a single bundle import can do (#1735) (@xarmian)
* 87101002a282ed1257e5fb0fed21d24c16c1c892: fix(import): bundle import remaps attachment references in version history, and on a kept partial import (BUG-3655, BUG-3656) (#2156) (@xarmian)
* 9ef346268c9d743f2cfdc61d7b5d720ed9278e06: fix(import): refuse duplicate source ids and attach by source id (#1740) (@xarmian)
* 77e1b386ef718a48cb992ae73363d7e8410e59d5: fix(import): relation defaults in imported schemas point at the imported items (BUG-3658) (#2159) (@xarmian)
* 6dbe15e79574f9c25c7b990695eb0d062da5fbfe: fix(items): a keyed create claims its key before the plan-limit check (TASK-3585) (#2088) (@xarmian)
* b15a48345e00328e8bd9af3d841a33e35da847aa: fix(items): a keyed replay of an archived-source move re-checks the destination (TASK-3585) (#2087) (@xarmian)
* d509d7530865b48908828939281ea9ed3f2f76be: fix(items): a move uses the item as it stands under the lock (BUG-3665) (#2165) (@xarmian)
* 199fd208a801098ca3dda9bfd5231127fc7051ed: fix(items): undo of an emptied line; a patch that changes nothing is refused (PLAN-3578 retro fixes 5+6) (#2089) (@xarmian)
* 68a7e279a702c27efe268ada7e4fd194ce41575d: fix(leases): bind item leases to the claiming account (#1731) (@xarmian)
* 9ef94ba4d8ba0527e2e1e88142472681fec3095e: fix(links,store): wiki links stay on their item through a reference-shaped rename and legacy renumbering (BUG-3693, BUG-3750) (#2140) (@xarmian)
* 4ed3b5eca2f2760c97482476a2812a92f1349544: fix(materialize): a job's deadline scales with its op-log (BUG-3521) (#1946) (@xarmian)
* 202f53daeffc2d0689a8fcd3492337ba9385831a: fix(mcp): MCP's long-lived streams end with their credential (BUG-3837) (#2201) (@xarmian)
* 7825f3afc5c1853d2f9a81a3b919b73a26d6dbaa: fix(mcp): MCP's long-lived streams keep alive and take a stream admission slot (BUG-3835) (#2197) (@xarmian)
* fdcf0867cdd74a8f0211a3032c46cc9356134734: fix(mcp): a /mcp stream whose client stops reading ends instead of pinning its handler (BUG-3808) (#2182) (@xarmian)
* 23a0360991dde90fbc6632a84e8526e10a48c359: fix(mcp): a connection row decides workspace access, not the legacy token list (BUG-3337) (#1749) (@xarmian)
* f9937c76532d4f4a70d6ebdd85078f6ff5a6ecf1: fix(mcp): cloud refuses to start without an https origin for MCP OAuth; a blocked self-hosted MCP says so (TASK-1069) (#1920) (@xarmian)
* d2337fafe452803cd8faa5ea69347fd8e35f01ed: fix(mcp): escape the workspace and ref in pad_playbook.run's path (TASK-2863) (#1991) (@xarmian)
* 16edb942030d0609e00d8858c38293aa3827547a: fix(mcp): free tools/list headroom: reflow and condense descriptions (TASK-3536) (#2004) (@xarmian)
* 1d752e0ba68f8a91015cad68e257ed3e1853b5c8: fix(mcp): remote pad_item.import keeps its artifact (BUG-3533) (#1992) (@xarmian)
* 3901101c81d2e6fedeecabfa2904bd6e8265c1bb: fix(mcp): remote pad_set_workspace embeds the workspace bootstrap (BUG-3326, ToolSurface 0.62) (#1710) (@xarmian)
* 0f932b5880b45d7c4c8b4ec3cb0ef5e466cd55e1: fix(mcp): remote routes answer a missing workspace with no_workspace and the list (TASK-2314) (#1846) (@xarmian)
* 59772ffc34310cb07b3638239f11a317d08d860d: fix(members): a collection-restricted owner cannot grant beyond its scope through invitations or role changes (BUG-3634) (#2116) (@xarmian)
* d212eb65031b691346f546e3c33d590363ccee80: fix(members): keep a workspace's owner and at least one owner member (#1737) (@xarmian)
* c0e66c6700666656b7b94879a729de51402a80f6: fix(models): the fallback terminal lists cover every "won't fix" spelling (BUG-3546) (#2033) (@xarmian)
* fc64d92eceb05645959ef43a7751f8a97d217468: fix(netpolicy): block Azure WireServer, and pin the cloud metadata census (BUG-3660) (#2155) (@xarmian)
* c52f64e26357ec93610733ad4551568d290376be: fix(netpolicy): one outbound address policy for URL import and webhooks (#1738) (@xarmian)
* 6365ac08fae4639d3b01d399c3e8669e0b307bf6: fix(oauth): a revoked grant mints nothing, and one refresh token rotates once (BUG-3678) (#2121) (@xarmian)
* 7b95dae4f56976a5a30d302709f2fd6513f4f236: fix(oauth): another client's replay of a spent refresh token or code revokes nothing (BUG-3400) (#1807) (@xarmian)
* 5749671dd95b2fa84e6c210ab4f483f6a1caf254: fix(oauth): include_future_workspaces is no longer a control; limit to current is an action (BUG-3338) (#1751) (@xarmian)
* 2ef63e3b25cc2d2e773f628bc7f3eb829d755f02: fix(oauth): introspection describes only the caller's own client's access tokens (BUG-3398) (#1791) (@xarmian)
* a2e1c5d9ca3fabf31e091b34a541408109b1a7f7: fix(oauth): narrow current-only wildcard connections to their current workspaces (BUG-3338) (#1752) (@xarmian)
* 6f6af0cf2c8a7c15110f5ef3d8ee58db214f5f8f: fix(oauth): the consent screen names Pad, the instance, the user's workspaces and the return host (TASK-1071) (#2017) (@xarmian)
* b950f311c6eef821c6d5657a761cc5e50e2d30be: fix(playbooks): the shipped ship playbook loads conventions with --full and guards its status updates with expected_seq (TASK-3575) (#2040) (@xarmian)
* e774268d63706e560ff8f25d56905581e552ea38: fix(plugin): drop the pinned version so installs follow the commit (BUG-3463) (#1848) (@xarmian)
* 9f9304b294bd3748c67386eee31a4b7dbf7081dc: fix(plugin): the pane's copy link points at the server it talks to, not always Pad Cloud (BUG-3484) (#1899) (@xarmian)
* 505cac1bab94b63b06803120ec9baba2dc084934: fix(ratelimit): retention covers the full refill window, so an idle drained bucket is not reset (BUG-3638) (#2115) (@xarmian)
* 1d20ae56c8e38fd1b86d64f9a524f936b235694a: fix(release): the release smoke stops the server it boots, and checks that it did (TASK-2035) (#1983) (@xarmian)
* 9e6791d4f1b8d7d934a9bbae52a47885b50f5090: fix(scripts): install-refresh asks git in the caller's checkout, not the server's cwd (BUG-3403) (#1790) (@xarmian)
* 38c591673fd0058cc8bfab9308ce24e8a6b5e5b1: fix(search): scope workspace search to visible items (#1723) (@xarmian)
* 08a362ee5d1c2d5fb09d625bea5108b3651a0fa5: fix(server): /mcp middleware refusals get the response write deadline (BUG-3834) (#2199) (@xarmian)
* 698fe2ff6eb2bc84d21af7d22afa4e7a4b525801: fix(server): a collab revalidation tick that errors makes the conn read-only (BUG-3474) (#1866) (@xarmian)
* 8a1aaf61a80effb18860f939001bc3b766fc55cf: fix(server): a failed flush reaches the handler through chi's wrappers (BUG-3827) (#2186) (@xarmian)
* f3b753e3a82762fcf192ef96de65c354da543f15: fix(server): a non-cloud boot no longer makes a Pad Cloud database's free users unlimited (TASK-3551) (#2028) (@xarmian)
* a53160ec79d1ba32b852cb9332619ccdda1b23fd: fix(server): a shared collection lists items in the owner's arranged order (BUG-3530) (#1990) (@xarmian)
* f17aaf26e2f5aa259e928e68fac8ccf444f9ddb7: fix(server): a workspace invite in the setup window answers setup_required, not 500 (BUG-3544) (#2034) (@xarmian)
* 9da6714ffc31c2b3c1d8fde40824db39f9d4b86e: fix(server): access_epoch hashes the set the item doors filter by (BUG-3347) (#1812) (@xarmian)
* b6f2d41043ba83ad2d7552a0911804503f032d04: fix(server): an account export that times out or fails says so, instead of arriving short (BUG-3626) (#2109) (@xarmian)
* fd63cc53ad08a27bb8e1af8f11dc3745e7b9cd91: fix(server): an event stream whose client stops reading ends instead of pinning its handler (BUG-3637) (#2172) (@xarmian)
* 250b5c2c0364a4ff9da470b4246dc5adb2943d50: fix(server): an interrupted import rolls back, and its outcome can be asked for (BUG-3475) (#1867) (@xarmian)
* b3cf4f529237e597b121a110e71b27980845df2e: fix(server): an ordinary open backlog fills Up next and `pad project ready` (BUG-3453) (#1854) (@xarmian)
* 4d6ebd426c80d41a45233c65f552547c3fe5f251: fix(server): attribution comes from the request, never the body (BUG-3372) (#1754) (@xarmian)
* 037e6166f18caafacc117695463059466aff90e8: fix(server): bulk move and bulk tag re-check what they read before the lock (BUG-3813) (#2188) (@xarmian)
* f9de1871ddf91212a646ddedfff41bb094f03abc: fix(server): cap the MCP request body at 7 MiB, answering 413 (BUG-3534) (#1988) (@xarmian)
* ed9de583cd99c48e084fe89675daedc779a36269: fix(server): every non-stream response write gets a rolling write deadline (BUG-3821) (#2189) (@xarmian)
* 4d017ddcff782ec99728f96095e2366c84f0a4de: fix(server): item context fills its budget past a part that does not fit, orders conventions by relevance, and widens implement to commit and PR rules (PLAN-3598) (#2101) (@xarmian)
* 0f5b567fe7179128740d637e3134875317d34211: fix(server): lineage and closure name only items the caller may see (#1743) (@xarmian)
* 4b53142589681ed27ea08a4df8d1194cac757250: fix(server): match accounts by email only once the address is verified (#1732) (@xarmian)
* 47ca9e521a55be32647c7c3f4c30973c65b20831: fix(server): refuse a collection schema that repeats or empties a field key or option (TASK-3539, PR B) (#2009) (@xarmian)
* f74f626fcbfa4d1ba9e0cdaf5cb37e3490fc0ddd: fix(server): register-with-code claims the invitation atomically; a gone invitation refuses and rolls the account back (BUG-3438) (#1834) (@xarmian)
* daed6bb441a842e5ac5bbe80b43e2f27a49a82f1: fix(server): removeUnusableWorkspace reports a failed delete as kept (BUG-3479) (#1870) (@xarmian)
* 119823d62d49629cf171a038f3a2d320de212292: fix(server): role-board reorder refuses another workspace's item and counts its rows (BUG-3342) (#1750) (@xarmian)
* fe9421322dc2d13b18682b5e44389cf9ec5908e1: fix(server): the /me summary mirrors the admin bypass; every admin route proven open to an admin session, closed to an admin PAT (BUG-1926) (#1918) (@xarmian)
* e3668f0fea0efbb1f86446a65201ea436c33cdd8: fix(server): the item-grant filter keeps an app request's read ceiling (BUG-3424) (#1825) (@xarmian)
* a1c36fca0492b12f6a21c4dfdab0d6021b8cfaea: fix(server): the upgrade diff states what a widened delegated access grants (BUG-3427) (#1817) (@xarmian)
* d75db3051563f27936bc6485dff41c1f6304d069: fix(server,store): unique_scope values are checked again inside the write, under its lock (BUG-3812) (#2184) (@xarmian)
* cd6dfdb318df4aa5648b61b7c44bbdd1413bdc13: fix(settings): Conventions and Playbooks start unchecked when a member is restricted (TASK-3384) (#1759) (@xarmian)
* 5578aeb04600004afe89fec28a3d36194b2d4fec: fix(settings): a late member-access response cannot fill or save another member's panel (BUG-3698) (#2126) (@xarmian)
* 76e029fff54477e2fb1391070188a23579a36171: fix(share): a share link serves nothing once its item or collection is archived (BUG-3635) (#2167) (@xarmian)
* 896b5561239888a7791ae6a79ac35afee0925ccd: fix(share): a shared body keeps only the classes and inputs the markdown renderer emits (BUG-3799) (#2162) (@xarmian)
* bf37b59e71a533ce773be3663cf0c523c85dd5c4: fix(share): a shared item body is sanitized with the markdown allowlist, and the SPA CSP restricts form-action (BUG-3669) (#2145) (@xarmian)
* 6e30a549a1814eedd617287754555e0ca89313f3: fix(share-links): a link stops resolving while its workspace is deleted (#1726) (@xarmian)
* 1f982df402e54e891d83d06d2b09009a9c0f85a2: fix(sse): an item event without a collection is not workspace-level (BUG-3343) (#1729) (@xarmian)
* aae955c9729df161519cbb48807143f049dfe88b: fix(storage): bundle import and cross-workspace copy are charged against the storage cap (BUG-3653, TASK-3625) (#2117) (@xarmian)
* c87587cad2f46c2ef70bd9bb183c07fcc292de05: fix(store): PG migration 054 breaks same-second version ties by id, not ctid (BUG-3751) (#2183) (@xarmian)
* 0aec8ed1a71227946c41129f42056a75b87e516b: fix(store): Postgres migration 004 drops the old doc_type CHECK before renaming phase-plan rows (BUG-3752) (#2130) (@xarmian)
* aa8975710db3b22d84d3ddbfc577e8737cbc5c9c: fix(store): a body rewritten without a version rebases the newest version's patch, so History stays exact (BUG-3745) (#2139) (@xarmian)
* d95f90850caced80e22e4f1db87a41c4ca076fa4: fix(store): a role change or disable of a vanished user is 404, and the unguarded DisableUser is gone (BUG-3826) (#2196) (@xarmian)
* 5279c491405ba2858534c197da9890e07b11bd3c: fix(store): account deletion and workspace purge lock comments root first, and retry a residual deadlock (BUG-3395) (#1792) (@xarmian)
* 61f07d39ea0ae10a3f8b19bf7456d0976f54b3e8: fix(store): an API token mint or rotation reads its row back inside its own transaction, never panics on a concurrent delete (BUG-3405) (#1774) (@xarmian)
* fdce754f2077abbb4207efdaad25a7b89078f42a: fix(store): an item list with a search term keeps include_archived and sort, and the tag filter matches exactly (BUG-3686, BUG-3706) (#2147) (@xarmian)
* eff70d7344d7f4037f9440d562e6ffa83afd2064: fix(store): compaction deletes exactly the rows it read (TASK-3532) (#1995) (@xarmian)
* a27df265bca7a2267f111b43d48b01bfe7c1f7d1: fix(store): concurrent re-invites no longer report a successful replace as an error (BUG-3460) (#1840) (@xarmian)
* 677081886471b6e1706dfc639e183c015122be0e: fix(store): every write that reads its row back does so inside its transaction (TASK-3406) (#1805) (@xarmian)
* 02806238d659d3eacd23d618f02ad7a2da791275: fix(store): import drops a unique value an earlier archive item holds, and says so (BUG-3825) (#2194) (@xarmian)
* aa7480290953f4a5fbd7097128dee12e71926eb3: fix(store): import indexes wiki-links, so an imported workspace has backlinks without waiting for a restart (BUG-3627) (#2111) (@xarmian)
* b9db178e1ed2ff600560b7fe85b98bcb90ba3cc6: fix(store): index api_tokens.token_hash on both backends (BUG-3668) (#2157) (@xarmian)
* 0479bf6cb1b505878b87ccfde9ca078260756dc2: fix(store): index status_transitions(seq) on both backends (BUG-3667) (#2164) (@xarmian)
* 107c38267c0f6ec221beedbc40211d4833206872: fix(store): legacy built-in adoption re-reads each item under the workspace lock (BUG-3806) (#2179) (@xarmian)
* be615377492e5ffa41a6b6c29c8bc5698e63076e: fix(store): legacy document version doors resolve from the body read in the same snapshot (BUG-3833) (#2198) (@xarmian)
* c97a054252e206de7a42da5f65c83a8190679080: fix(store): legacy per-collection item numbering is converted even after migration 056 dropped its marker (BUG-3664) (#2129) (@xarmian)
* 4c7774dfd77822387568fa78bd39bb2b94b08763: fix(store): log why a workspace import renumbered its items (TASK-2923) (#1994) (@xarmian)
* 8658db7275d8ca4b0f55fe8121ec26cece39c608: fix(store): migration 025 rebuilds documents with foreign keys off, so a database with versions can upgrade (BUG-3663) (#2120) (@xarmian)
* 1082c4aa16f608e4abc26da3a160a2fd2cc84e96: fix(store): reads exclude soft-deleted collections' items (BUG-3425) (#1820) (@xarmian)
* 1e75d19d1f9758e9c43f240581324d82f79660d3: fix(store): rebindQuery skips SQL comments and quoted identifiers (BUG-3430) (#1822) (@xarmian)
* f9d79aea94306c008212f515b66ab1a88e5c11ca: fix(store): relationship reads exclude soft-deleted collections (BUG-3434) (#1828) (@xarmian)
* a7f98c01fca0e20ca9c7ac039fcb06c4e0960754: fix(store): search, tags, children and progress exclude soft-deleted collections (BUG-3428, phase 1) (#1824) (@xarmian)
* 0d28c48e5873158893c592e9d777c6c3212c91e1: fix(store): startup secret encryption passes compare-and-set on the value read (BUG-3805) (#2177) (@xarmian)
* c912c2c6414249d82e91e67cb65771c12fb9ab59: fix(store): the wiki-link backfill re-reads each item under the workspace lock (BUG-3666) (#2168) (@xarmian)
* 6f75e252723b31080c41900326327efe61156353: fix(store): version doors resolve the patch chain from the body read in the same snapshot (BUG-3814) (#2190) (@xarmian)
* 01021632c9626352d12a8859f68247b7f4458ad6: fix(store): version rows record their body's hash, and the walk refuses what it cannot verify (BUG-3820) (#2192) (@xarmian)
* b3e6815e0c432d81d57214f0a1f267b4a2b9040f: fix(store): wiki backlinks exclude sources in soft-deleted collections (BUG-3344) (#1814) (@xarmian)
* db8fb3aabf369fd4df08d7736c479363cf5f815a: fix(store,server): an item write re-checks its fields under the seq lock when the schema it was validated against has moved (BUG-3407) (#1806) (@xarmian)
* 48c3ca066c9ddaffb38267c58ad1873b6a896901: fix(test): test temp dirs stop leaking into /tmp (BUG-3412) (#1786) (@xarmian)
* 2f3cf402b173d4bc83f2139fd07e289326f96799: fix(timeline): 'commented on update' only for a comment an update carried (BUG-3437) (#1832) (@xarmian)
* 8bb4616a3d753e880c3c84067d1438d750ffad87: fix(urlimport): marshal OpenAPI examples with libopenapi's own yaml package (TASK-3422) (#1818) (@xarmian)
* d5ca8a7eb0978fc8c28d00d641ee878ddc35597d: fix(versions): an applier-path body write leaves a version row (BUG-3327) (#1709) (@xarmian)
* 69d2be842903a6d45b27b0b7c24cd27dc3be8870: fix(versions): restoring or diffing a version whose patch failed is refused with 409 (BUG-3815) (#2180) (@xarmian)
* 540925cd0bd5895a3322e87abfa55dd5febef5f4: fix(watchevents): a frame that wins the receive select after Close records and reports nothing (BUG-2741) (#1905) (@xarmian)
* 0663b05752b3b9ba4fe25c1c2dddd7b9d8d846c8: fix(web): Activity, Tags, a tag's items, Starred, Members and the Library say when they failed to load (TASK-2203) (#1930) (@xarmian)
* f7b255819656352947cae4cdbf0906a6c6163c40: fix(web): ESC closes the pane before its ItemDetail has loaded (BUG-3148) (#2053) (@xarmian)
* 52d90ea31ed08334bc231b0832accbaf0530fd4d: fix(web): Insights throughput labels read as dates, and hours in local time (TASK-2220) (#1951) (@xarmian)
* 03a3617dbb0589fcaea33789fea0bf7832f1d836: fix(web): Library, Playbooks, Conventions and the playbook editor find their collections by trait (BUG-3481) (#1876) (@xarmian)
* 56f8a49fe0438b9f98d365cc273e0098b8312df4: fix(web): SSE bursts coalesce their reconcile and collections reload; the timeline ignores other items' comments (TASK-2224) (#1844) (@xarmian)
* b87f63ae56aeabad202d4c299e82cf19d4c06729: fix(web): a failed logout always lets items save again, and a sign-out discards what it stands down (BUG-3571, retro review of #2041) (#2074) (@xarmian)
* 3377637e68a59511eb82061adccc80b73d715f40: fix(web): a failed version restore says so, restore needs edit permission, and a child reorder that does not land says why (TASK-2205) (#1929) (@xarmian)
* 71f21dd29ce2cac61e530ec6e332f90d749e6b07: fix(web): a json field keeps its type in the schema editor (TASK-2194) (#1971) (@xarmian)
* 9e886ddc00c6c27143087a38525f033bcce36dd6: fix(web): a link that opens elsewhere never keeps window.opener (BUG-3359) (#1739) (@xarmian)
* 791f25a946fd62a2bb9bd1ff6b28a31894ce69a1: fix(web): a palette search that fails says so, with Retry, instead of "No results" (TASK-3587) (#2063) (@xarmian)
* edf7e2226219942bf1d27f1a8c9e040fb3bb3e64: fix(web): a raw markdown save carries its base and asks, not replaces, over a changed body (BUG-3540) (#2011) (@xarmian)
* 56eeceabcafb912b5565c7356eac61385caff442: fix(web): a reorder settles to what the server stored and never leaves an unconfirmed order looking settled (BUG-3699, BUG-3700) (#2150) (@xarmian)
* 1fc60d72b47a6edbe55b65e2fcc283639153f52a: fix(web): a save refused for an open tab's unconfirmed typing asks, and Overwrite lands (TASK-3548) (#2025) (@xarmian)
* b5df3f96df516ab4bc3301d723c2fc9295c86669: fix(web): a share link's sign-in comes back to it, and a gone or unreachable link says so (TASK-2249) (#1940) (@xarmian)
* fc2e768dbf40ae816097cfda449c6b5e70a6548e: fix(web): a shared ?view=table link opens the table, and the remembered view is per workspace (TASK-2212) (#1947) (@xarmian)
* 6647ca5444edfeeb3ac785c79a60811cd39b4689: fix(web): a split-pane switch makes each request once (TASK-2228) (#1937) (@xarmian)
* 89d9298ad0fd8f3942f11341c245bb0c0b69cd5a: fix(web): a tag filter matching nothing says No matches; tag pages get Show completed (TASK-2211) (#1913) (@xarmian)
* 92b472f1d749b12ba19df9c3b3ea81a3193b0031: fix(web): a teardown flush over the keepalive budget goes as an ordinary request (BUG-3522) (#1949) (@xarmian)
* eb3f8f0f19af50d3666b1aeb2c4f2b87236052c8: fix(web): a workspace opens with its requests in parallel; the dashboard poll pauses when hidden or live (TASK-2229, TASK-2227) (#1912) (@xarmian)
* 20690ae9fb56481ffdf389aaf12796ea5ee6fd78: fix(web): admin user rows, settings tabs and the console nav work from the keyboard (TASK-2238) (#1962) (@xarmian)
* e5997aee097e97203a776cf09d53abec1a4e08d1: fix(web): an agent's [[REF]] applied to an open tab is a link, not bracket text (BUG-3582) (#2052) (@xarmian)
* 34d17e44f1ff905fa83a56fae17d43be977bb58c: fix(web): an item load no longer waits for the index to catch up (BUG-3473) (#1887) (@xarmian)
* 7aa5fa67f7cbdf2a2da0e27135a34f588a333a07: fix(web): an open mobile sheet stops page pull-to-refresh, and a pull from its list top closes it (BUG-3386) (#1830) (@xarmian)
* 721c9597f4ffd475aee42ae337d56479a8a16d4e: fix(web): an unknown invitation code says so, the header names the workspace, and the login link keeps the code (TASK-2251) (#1917) (@xarmian)
* 1eecf710c8fef732e9f3eb69ebc796b7a8f5e8c1: fix(web): angle-bracketed prose survives the editor: `<Button>`, `Promise<T>`, comments and unknown tags are text, not dropped markup (BUG-3557) (#2035) (@xarmian)
* 1a76ca3f58274e431a5828510ee028f1edf3b3a7: fix(web): app dialog and toasts replace native confirm/alert; sticky save and sync status (TASK-2221) (#2015) (@xarmian)
* cbf90f4542420a3788aabebad60d850f883f1fd1: fix(web): cards, sidebar rows and table headers stop nesting controls (TASK-2237) (#1968) (@xarmian)
* c0beb4da34c44b8323b38004fc1db0fa8a0dc8fc: fix(web): closing or leaving an item asks first when typing may not have reached the server (BUG-3556) (#2037) (@xarmian)
* 80bfd26c6a676806f125165216f58e5f9ff8167c: fix(web): conventions, playbooks and the library say what their markers mean (TASK-2257 C72) (#1963) (@xarmian)
* 203a0b827f23a1c52bec44e8e2e2d092c2867f8a: fix(web): deleting a token or revoking a share asks first and says when it fails; a new token has a Copy button (TASK-2193) (#1910) (@xarmian)
* 35ca07bd6e4f3fbd37f70467de5c83c2995d122d: fix(web): drop the ⌘] binding that cancelled browser Forward for nothing (BUG-2666) (#1849) (@xarmian)
* 7222505d41b0d8d2847cbd3f58b549eb17633d6c: fix(web): every field shows a focus ring, and the sidebar add buttons reach 3:1 (TASK-2262) (#1843) (@xarmian)
* 41692af98100e7474695fee88792dba054cbab97: fix(web): every filter select and search input has a name; the share-link password gate is labelled, focused and announced (TASK-2236) (#1921) (@xarmian)
* 8384adc63122d5b3ef8907b52643a74afcfac6bb: fix(web): every text field has a name, not just a placeholder; an axe check proves it rendered (TASK-3515) (#1931) (@xarmian)
* 93b906b0b3efd4998347f648c818d8fc8e5ffd57: fix(web): field editor polish: a non-number says so and sends nothing, the select announces its highlight, the date clear is a sibling (TASK-2216) (#1919) (@xarmian)
* 999c4c82e8d8b9edbc313b4fe191b5a4abea8e96: fix(web): four retro-review findings on #2063, #2067 and #2072 (TASK-3599) (#2078) (@xarmian)
* b0f325e75109705763d19de3a473ac7059966376: fix(web): hand back an edit lost with its socket on force_refresh (BUG-3526) (#1973) (@xarmian)
* a867a8f7744df5c52666c97b2d5665e012d262ea: fix(web): icon-only buttons carry accessible names (TASK-2240) (#1974) (@xarmian)
* 46490b0612471e4dc15abb1bfe52b9539e4a9292: fix(web): keep unsaved text when the session ends under an open item (BUG-3571, part 2) (#2044) (@xarmian)
* f8faed647af03929575bd30f30bf7344f636ae67: fix(web): keyed lists render repeated keys instead of blanking the view (TASK-3539, PR A) (#2006) (@xarmian)
* c4354571d0bacc1464904fc4b3ec5ab58c39b5f8: fix(web): keys typed before the slash or [[ menu opens are its query (BUG-3547) (#2024) (@xarmian)
* 5ea7fde86b60d586575385c3d0926d3fd4c1c941: fix(web): keys typed into an editor frozen by force_refresh recovery stay in the editor (BUG-3786) (#2138) (@xarmian)
* e95135c499ca690b532cdd6bb974683b0cc22fe1: fix(web): links to the /-/r/ resolver open their target (TASK-3119) (#1862) (@xarmian)
* 25dca945e51327d6235a1ed46a5fbe7c313aaabe: fix(web): list and table j/k step the rows on screen (BUG-3492) (#1894) (@xarmian)
* 9b7ffdf897b2516825557106b82f64a133ceb28d: fix(web): long Active Plans titles stay inside their card at every width (BUG-3440) (#1855) (@xarmian)
* 6c4b54908c5865c4da4107f317c13ddbc840a07d: fix(web): looking at the template list no longer picks startup, and a chosen template stays named (TASK-2254) (#1961) (@xarmian)
* f323d810a6c29fbdd032d0a8ad0bb55942623f3c: fix(web): manual order breaks a sort_order tie oldest first, as the server does (BUG-3527) (#1969) (@xarmian)
* 92305fba4d6083b1832bcaec996fb3230c937bd9: fix(web): marks never sit on inline atoms, so a tab's editor equals its Y.Doc (BUG-3568) (#2038) (@xarmian)
* f392847024dcf5df98ae6c18ad0859bbf8d7c37d: fix(web): no field suppresses its focus ring any more (TASK-3461) (#1845) (@xarmian)
* fe838f146efb11efc9f4ea3b4b6e4ee7b4a2904d: fix(web): notifications, docked sheets and the Insights popover take, keep and return focus (TASK-2235 U1) (#1945) (@xarmian)
* f2a3a28e46852d5d44dd949835274aa427bcf78b: fix(web): offline edits are protected honestly: the badge says they live in this tab, closing or leaving asks, a discarding reload hands them back (TASK-2199) (#1892) (@xarmian)
* 75e1aa684e9c61c75fc6ed996c2fe945b921e2f5: fix(web): on HTTP/1.1 a browser holds at most three workspace streams; other tabs poll (BUG-3320) (#1904) (@xarmian)
* 5e914e79ff700cef4b0de20c83dbfa7e5b7631b1: fix(web): onboarding says "Agent activity detected"; live signals say "connected" and "ready to receive" (TASK-3596) (#2077) (@xarmian)
* 9a90368f6622de07c44d39c1d3ee29723faca76d: fix(web): one connection-recovered signal heals failed loads, and the dashboard and activity show stream status (TASK-2201) (#1960) (@xarmian)
* 35e5f4809e232e08f023899a14ad14ea569f75d8: fix(web): playbooks say how they run, and the library keeps its tab (TASK-2256) (#1966) (@xarmian)
* 13fa0c99e9f0d7a1fe5afb1c1d7aa67feb675c8b: fix(web): quick-add is `c`, and one switch turns every single-key shortcut off (BUG-3465) (#1851) (@xarmian)
* 9103aaeb243b422d92e55ad5344e95574fb874df: fix(web): section tab titles, one Mod+\ chrome state, a reachable and complete shortcuts sheet (TASK-2261) (#1972) (@xarmian)
* 0015f49c1ebfb88e5aa88e457ebf2eeb49348247: fix(web): settings say whose they are, roles and grants explain themselves, webhooks say where they live (TASK-2255 C59/C60/C109) (#2030) (@xarmian)
* 2b0652d1925e374866919aa257d6d8cf0ace0f31: fix(web): signing out asks first while an open item holds edits the server may not have (BUG-3571, part 1) (#2041) (@xarmian)
* 22a32efdb544977c3a922a7b3816cb682f215919: fix(web): skipped board cards keep their placeholder height, so a scroll to a far card lands on it (BUG-3553) (#2050) (@xarmian)
* 4c733467ef0bfc248e8c60f0b84b124f7c97df3d: fix(web): space between the pad wordmark and the first workspace tab (TASK-3545) (#2021) (@xarmian)
* 94d60f552e4a6ca42ff9829d14858d77ed843467: fix(web): state the password rule on every password field, and show its refusal there (TASK-2260) (#1941) (@xarmian)
* 022b23e86fbe2a81fd8ff9cda83029a69f0e63a8: fix(web): the auth pages are real forms, with labels, announced errors and a focused first field (TASK-2259, TASK-2236) (#1911) (@xarmian)
* ede34e908659991dba48804e5fc26925baeb4328: fix(web): the balanced fields grid follows the item body, not the viewport (TASK-2209) (#1897) (@xarmian)
* 69fbbe6453ec7c174a3729e198ca0b116eda61db: fix(web): the collection page's search ranks every match, so a filter cannot hide one past the cap (BUG-3710) (#2149) (@xarmian)
* 6071bf361a4394e37cb91261b2fc335eabf43697: fix(web): the collection search box writes the address on a debounce (TASK-2232) (#1939) (@xarmian)
* 5c3ed1b5e7162f14e8568d1e32aa17c631b6a015: fix(web): the command palette and quick-add are real dialogs (TASK-2235 U2) (#1950) (@xarmian)
* a7c559e431e1304c757fe291d755a26d676e5db9: fix(web): the command palette is an accessible combobox, axe-clean in both themes (TASK-2234) (#1847) (@xarmian)
* 4d90f45961d02daa9d473400a98ffaabf2f63341: fix(web): the conventions bulk toggle, the roles board and workspace create show what failed (TASK-2204) (#1928) (@xarmian)
* 3595a3c034e8ff240174a0a112e46c7aee689def: fix(web): the copy and push dialogs send an idempotency key, one per opening (TASK-3597) (#2090) (@xarmian)
* 1d022040e61510d316739dc9a80bde9b549d8c9b: fix(web): the field editor's advanced-section sync no longer depends on the Svelte runtime to stay alive (TASK-2186) (#1841) (@xarmian)
* c1d7988c7a95ce64c770acc07608a3057d95ee92: fix(web): the graph follows the light theme: readable labels, a glow that shows, completed items that recede (TASK-2239) (#1936) (@xarmian)
* b8c9b0ea6bce29535117ac35cddf89d2c34b6783: fix(web): the import dialog shows progress, stops on a stall, and says what was kept (BUG-3475) (#1869) (@xarmian)
* 84ddb3f693d9eb02f6e4127ccc22ef1bb0524bfc: fix(web): the list cursor no longer snaps back while the pane follows j/k (BUG-3204) (#1863) (@xarmian)
* 82f8ecc89810d3f437ac62c723984e122b3b3cce: fix(web): the page behind the palette, a docked sheet or the notification panel is inert (TASK-3520) (#1954) (@xarmian)
* 2e9bfc9a2a0f41c0224a74a3510c6d25bbd8b93a: fix(web): the palette's server searches keep a coll: qualifier as the collection filter (BUG-3709) (#2148) (@xarmian)
* 186ffdba63b790db05f5b6e22c6c47abbdb8f802: fix(web): the remaining native confirm() dialogs ask through the shared ConfirmDialog (TASK-3543) (#2018) (@xarmian)
* bd74960fe917fc8adcf75508a9dc59352190897c: fix(web): the role board reloads when the route's workspace changes (BUG-3701) (#2175) (@xarmian)
* d39cb9f00a150f19bd2a6f04420617613afab01f: fix(web): the selected tab is marked by an accent, not a background step (BUG-3420) (#1829) (@xarmian)
* 9d69d4e4dcb8e1ff23969b3baf85d55a51bc63ce: fix(web): the slash menu and [[ picker open where they can be seen, and [[ has a way in (TASK-2218) (#1952) (@xarmian)
* e091bcc63e4b2972ebe452692e8f05e92f15f1e7: fix(web): the workspace export download is shown only to whom the server lets export, an owner with unrestricted access (BUG-3614) (#2105) (@xarmian)
* bb38641ef71173a4f0f28e0ee3a87f9cdce58a32: fix(web): toasts are announced, errors linger, hover holds them, and an unreachable server says so (TASK-2202) (#1914) (@xarmian)
* fa66181b8827eb706273982b22de1870bd31e19b: fix(webhooks): a DNS failure is retried, and a redirect may not turn the POST into a bodyless GET (BUG-3661, BUG-3662) (#2163) (@xarmian)
* 7ee0bddc45b3a6eb93016dfb25386fb9dd4510fd: fix(webhooks): whole-workspace access to manage; no delivery for a deleted workspace (#1727) (@xarmian)
* f6f588b4d45c78e32f349d148723cbdeb71f074f: fix: a convention's stored metadata copy follows its ordinary fields (TASK-2257) (#1964) (@xarmian)
* 05c039f1317e04e1912cc6969d70dcb7c48eae5d: fix: agents load items with --agent; --format markdown stays body-verbatim and names an empty body (TASK-3451) (#1842) (@xarmian)
* 8c8deeeb898722009f94b3bf10a3eedce4515bc2: fix: an invite asks an existing user instead of adding them; decline; CLI invitations (BUG-2136 U1) (#1831) (@xarmian)
* a91fcce7f97eb52742e42c6d64da5693955b1dde: fix: blank workspaces accept the library's own triggers and scopes (BUG-3446) (#1836) (@xarmian)
* ee288cbebd3463a7b471a76b613869e78c343a36: fix: item lists refuse a filter key that names no field (BUG-3480) (#1880) (@xarmian)
* c81b5c07269b6a855b4fafb31c0d5737abf5075a: fix: owners cannot lock themselves out by mistake; accounts with no password can set one and turn 2FA off (TASK-2190) (#1879) (@xarmian)
* 3aff8e388f1275900c730dec2e83f4cfa3730589: fix: pad keeps an edited /pad skill and never downgrades a newer one (BUG-3466) (#1857) (@xarmian)
* 63e2830c756995de6900c048f65f070691c36ec1: fix: the Live badge reflects a dead SSE connection, and the reconnect catches up (TASK-2197) (#1895) (@xarmian)
* 10a1683b83da878a1d8d42cad4fa18b14d29010b: fix: the access epoch tracks the live collection set; deleted collections leave the local index; the open-children guard ignores them (BUG-3428 phase 2) (#1826) (@xarmian)
* 1d94d038a4d9251b8d1a1195ad175d4fa3fbdd0f: fix: the first-run launchpad follows an onboarding agent live (BUG-3447) (#1837) (@xarmian)
### Performance
* d9978cfb7a1b0fb6e51499993782e7d76061a2c5: perf(web): a board lane mounts a window of its cards (TASK-2230) (#1953) (@xarmian)
* f9713c9fbe6ce0bb7b41a441f7587f64d08c06fe: perf(web): tag and starred pages render from the local index (TASK-2231) (#1938) (@xarmian)
* 4acd2249c026dc05931550917fbd21b411a09ffd: perf(web): the collection page loads the item pane's editor on demand, not before first paint (TASK-2226) (#1935) (@xarmian)
* 1b78add84467399c477c48751310525df4bd6538: perf(web): the editor coalesces its markdown, not its dirty signal (TASK-2232) (#1942) (@xarmian)
### Refactors
* 01fba76bfc6e3de186910eae2db4c426a2038b58: refactor(cli): examples move from Long to cobra's Example field (TASK-2865, part 1) (#2020) (@xarmian)
* cf3cdefd0b2a2bf41c3c82ae060560109fa0b91e: refactor(web): drop the dead terminalStatuses prop chain (TASK-3537) (#2007) (@xarmian)
### Other changes
* 5614980edcd1b096bc1122eafb5632560df70102: Make database restore preserve live data on failure (#1703) (@mattfaltyn)
* 9a7b38ed12ae1684e906d5de968ad66316eceedb: build(deploy): docker compose runs the released, signed image; k8s pins a release (TASK-2034) (#2031) (@xarmian)
* 2c1706fbbb1058ab3ef3cea2573c655f58c58720: build(release): a shipped binary that does not start fails the release before it publishes (TASK-2035) (#1980) (@xarmian)
* e303c16116b3f3f71bdf4dd9abfcf54f0669375f: build(web): jsdom 30 (TASK-2586) (#2019) (@xarmian)
* b454f17928f619b7af6c3503148b03752ecdae8d: build(web): move the SvelteKit and Svelte config into vite.config.ts (TASK-3423, PR A) (#1823) (@xarmian)
* 41456fc7831b43f0897d9420e1040cbd5bf49d87: build: go1.26.9 and x/net v0.60.0 for twelve new standard-library advisories (#1922) (@xarmian)




