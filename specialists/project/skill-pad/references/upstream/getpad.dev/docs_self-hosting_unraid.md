**Title:** Run Pad on Unraid

**Source:** [https://www.getpad.dev/docs/self-hosting/unraid](https://www.getpad.dev/docs/self-hosting/unraid)

---

# Page Structure Map
```text
Run Pad on Unraid
├── Prerequisites
├── Install
├── First-run setup
│   └── Bypass the token (open setup)
├── Form fields explained
├── Where your data lives
├── Backups
├── Upgrading
├── Reverse proxy
├── Email (optional)
├── Connect your CLI and agents
├── Troubleshooting
└── Going further
```

---

Pad is in Unraid’s Community Applications index. Single container, SQLite by default, no telemetry, your data stays on your tower. About a minute from the **Apps** tab to your first item.

## Prerequisites

- Unraid 6.12 or later
- Community Applications plugin installed

## Install

1. Open **Apps** in the Unraid web UI.
2. Search for **Pad**. It’s listed under **Productivity / AI**, published by Perpetual Software LLC.
3. Click **Install**, review the form (defaults are fine for most setups; see Form fields), click **Apply**.
4. Wait for the container to come up. The health check polls `/api/v1/health` and turns green within a few seconds.
5. Click **Logs**, find the banner that starts with `Pad first-run setup`, copy the URL.

The URL looks like `http://<your-tower>:7777/setup#token=<TOKEN>`. Paste it in your browser, fill in email, name, and password, and you’re in.

The template itself lives at github.com/PerpetualSoftware/unraid-templates (`pad/pad.xml`). The container image is `ghcr.io/perpetualsoftware/pad:latest`.

## First-run setup

Pad’s first-admin endpoint is gated to the container’s loopback interface, so the plain “open the URL and create an admin” path doesn’t work for a remote container: the request would come from your laptop, not from inside the container. Pad solves this with a **one-time token logged on first start**.

When the container starts with no users, it generates the token, writes it to `.bootstrap-token` in appdata (mode 0600), and prints a banner to the container log:

```
========================================================================
  Pad first-run setup
========================================================================

  No users exist yet. To create the first admin account, visit:

      http://<your-host>:7777/setup#token=<TOKEN>

  This token is one-time. After the first admin is created the token
  is consumed and this banner stops appearing.

  To regenerate, delete /data/.bootstrap-token and restart.

========================================================================
```

To find it: Unraid → **Docker** → click the Pad container → **Logs**. Scroll for “Pad first-run setup”. Copy the URL.

The `#token=` part is a URL **fragment**. Fragments are browser-only and never sent to a server, so the token can’t land in proxy logs, access logs, or shared browser history. The setup page reads the fragment, scrubs it from the address bar, and submits the token in an `X-Bootstrap-Token` header. The banner deliberately goes to the log as plain text and not as a structured log field, so log aggregators don’t get an easy-to-extract copy of the token.

The token can only be regenerated on an instance that has **never been bootstrapped**. Once a user exists, the server deletes any leftover `.bootstrap-token` on every startup, and the bootstrap endpoint answers `409 Conflict` (“This Pad instance has already been initialized”) to any further attempt.

### Bypass the token (open setup)

If the container is on a network you already trust (Unraid behind your home firewall, a Tailscale-only deployment, anything not reachable from the open internet), flip **Bypass Setup Token** to `true` and skip the copy-from-logs step. Visit `http://<your-tower>:7777/setup`, fill in email, name, and password, and the admin is created in one round-trip.

What changes when the field is `true`:

- No bootstrap token is generated and no `.bootstrap-token` file is written.
- The log shows a different banner, `Pad first-run setup (open mode)`, plus a WARN-level log line so log aggregators can flag it.
- The bootstrap endpoint accepts the first-admin request from any IP without a token header, **but only while zero users exist**. The moment you create the admin the surface closes, and further requests get `409 Conflict` regardless of the flag.

When NOT to use it:

- The WebUI port is reachable from the public internet (port-forwarded on your router, exposed on a cloud provider). Anyone who reaches `/setup` first becomes admin.
- The instance runs in cloud mode (`PAD_CLOUD=true` / `PAD_MODE=cloud`). The flag is ignored there by design, with a warning in the log, and the loopback-only gate stays on.

You can set it back to `false` after the admin exists. It has no effect at that point either way, but unsetting it keeps the configuration honest.

## Form fields explained

| Field | Default | What it does |
| --- | --- | --- |
| **WebUI Port** | `7777` | Host port Pad listens on. Change if 7777 is in use. |
| **Appdata** | `/mnt/user/appdata/pad/` | Where Pad stores its database, attachments, encryption key, logs, and config. Mounted at `/data` in the container. |
| **PUID** | `99` | UID the pad process runs as inside the container. `99` = Unraid `nobody` (matches the appdata default). |
| **PGID** | `100` | GID similarly. `100` = Unraid `users`. |
| **Log Level** | `info` | Verbosity for the server log: `debug`, `info`, `warn`, or `error`. Set to `debug` when troubleshooting. |
| **Bypass Setup Token** | `false` | If `true`, the first admin can be created directly at `http://<your-tower>:7777/setup` with no bootstrap token. Only safe on trusted networks; see Bypass the token. |
| **Public URL** | (empty) | Set if reverse-proxying. Required so emailed invitation links point at the real hostname instead of `http://<unraid-ip>:7777`. |
| **Maileroo API Key** | (empty) | Optional. Enables email invitations. Without it, invites use copyable join codes. Masked in the form. |
| **Email From** | (empty) | Sender address (required if the Maileroo key is set). Must be on a domain you control. |
| **Email From Name** | `Pad` | Display name on outbound emails. |

PUID, PGID, Log Level, Public URL, and the email fields are under **Show more settings** in the install form.

PUID and PGID are validated by the container’s entrypoint: `0` (root), empty, and non-numeric values are rejected with a clear message at the top of the log and the container exits. The default `99:100` matches Unraid’s `nobody:users` convention, so you should rarely need to change them.

## Where your data lives

All persistent state lives under the appdata path you set in the form (default `/mnt/user/appdata/pad/`):

| Path | What | Critical? |
| --- | --- | --- |
| `pad.db` + `pad.db-wal` + `pad.db-shm` | SQLite database | **yes** |
| `encryption.key` | Encryption key for sensitive fields (TOTP seeds, OAuth tokens) | **yes. Losing this bricks the encrypted data even if the database survives** |
| `attachments/` | Uploaded attachment blobs | yes |
| `logs/server.log` | Server log | nice-to-have |
| `config.toml` | Server config | nice-to-have |
| `pad.pid` | PID file | ephemeral |
| `.bootstrap-token` | First-run setup token (deleted when the first admin is created) | one-time |

One mount, complete coverage. The default appdata field gives you all of this without thinking about it.

## Backups

Stop the container first so SQLite isn’t mid-write. Then:

```
# Backup
tar -C /mnt/user/appdata -czf "pad-backup-$(date +%F).tar.gz" pad/

# Restore
tar -C /mnt/user/appdata -xzf "pad-backup-2026-05-06.tar.gz"
```

The `-C` flag makes both archive and restore relative to `/mnt/user/appdata`, so the `pad/` directory inside the tarball always lands at `/mnt/user/appdata/pad/` regardless of where you run the command. Without `-C`, GNU tar stores relative paths anyway (with a “Removing leading /” warning), and extracting from a different directory would scatter the data.

The container’s entrypoint runs `chown -R` to your configured `PUID:PGID` on every start, so PUID and PGID don’t have to match between the source and destination Unraid hosts. If some files can’t be chowned, the entrypoint logs a warning and starts Pad anyway rather than locking you out.

## Upgrading

Unraid → **Docker** → click the Pad container → **Force Update**. Unraid pulls a fresh `:latest`, recreates the container, and your appdata persists.

Pad releases are at github.com/PerpetualSoftware/pad/releases. Watching that repo on GitHub gets you a notification when a new version ships.

## Reverse proxy

If you front Pad with **SWAG** or **NGINX Proxy Manager** for HTTPS and a real hostname:

1. In the template’s **Public URL** field, enter your external URL: `https://pad.example.com`.
2. In your reverse proxy, point `pad.example.com` at `<unraid-host>:7777`.
3. Standard reverse-proxy headers are fine. Pad doesn’t need any special config beyond Public URL.

The **Public URL** field is what makes emailed invitations point at your real hostname. Without it, invitation links default to `http://<unraid-ip>:7777`, which recipients off your network can’t reach.

For the broader self-hosting reverse-proxy guide (Caddy, Nginx full config, TLS hardening), see Self-Hosting → Reverse Proxy.

## Email (optional)

If you want Pad to send workspace invitations by email:

1. Sign up at maileroo.com (the free tier is fine for low volumes).
2. Paste the API key into the **Maileroo API Key** field. It’s masked in the form and won’t show in the container logs.
3. Set **Email From** to a sender address on a domain you control.
4. Optionally customize **Email From Name** (defaults to “Pad”).

Without these, invitations fall back to copyable join codes that the invitee redeems with `pad workspace join`. Not worse, just different.

## Connect your CLI and agents

Once Pad is running and you’ve claimed the first admin, point your local CLI and AI coding tool at the Unraid instance.

**CLI + skill setup** (on your laptop, NOT in the container):

```
pad init --url http://<your-tower>:7777 --workspace <your-workspace-slug>
pad agent install claude   # installs the /pad skill into Claude Code
                           # "cursor" covers Cursor, Codex, Windsurf and OpenCode;
                           # "codex" and "windsurf" also work on their own
```

`pad init --url` configures the local CLI to talk to your remote Pad instance. `pad agent install` installs the natural-language `/pad` skill into your AI tool of choice. Reach across the LAN with `<your-tower>:7777`, or use Tailscale or Cloudflare Tunnel for off-network access.

**MCP setup** (separate from the skill above): if your tool is an MCP client, Pad also runs as a local MCP server:

```
pad mcp install claude-desktop   # or: cursor, windsurf, claude-code
```

See MCP — Local for the full MCP setup walkthrough (per-client config files, troubleshooting). The skill (`pad agent install`) and MCP (`pad mcp install`) are independent integrations. Use either, both, or neither.

> **Public URL ≠ agent target.** The Public URL template field controls server-generated links (emailed invitations, share URLs); `pad init --url` controls how the CLI on each device finds the server. You typically want both: Public URL for clean email links, `pad init --url` on each agent host.

For per-tool walkthroughs see Agent Integration, Connect a Workspace, and MCP — Local.

## Troubleshooting

- **Port 7777 already in use** → change the **WebUI Port** field to a free port (e.g. 7778).
- **Container exits immediately** → check the **Logs** for an entrypoint error at the top. The usual cause is an invalid PUID or PGID: the entrypoint rejects `0`, empty, and non-numeric values and exits with a message naming the bad value.
- **Image won’t pull** → verify GHCR is reachable: `docker pull ghcr.io/perpetualsoftware/pad:latest` from any machine.
- **Reverse proxy returns 502** → it’s a reachability problem, not a Pad config problem. Check:
	- The proxy’s `proxy_pass` / `reverse_proxy` upstream points at `<unraid-host>:7777` (or whatever WebUI Port you set) with scheme `http://` for the in-LAN hop.
		- The Pad container is running and healthy (Docker tab → green health check).
		- If your proxy is in a different Docker network, the two need to share a network (or the proxy needs to reach Unraid’s host IP on the published port).
		- `PAD_TRUSTED_PROXIES` does NOT cause 502s. When unset, Pad ignores forwarded headers and the client IP falls back to the TCP peer. Set it only if you want accurate client IPs in rate limits, audit logs, and the bootstrap loopback check.
- **Emailed invitation links point at the wrong hostname** → set the **Public URL** field to the URL users actually browse to (e.g. `https://pad.example.com`).
- **First-run banner not showing in logs** → it prints on every start while zero users exist; once an admin exists it stops. On a not-yet-bootstrapped instance: stop the container, delete `/mnt/user/appdata/pad/.bootstrap-token`, start it again. If you set **Bypass Setup Token** to `true` you’ll see the open-mode banner instead: same gate, different message. If the token can’t be written at all (read-only appdata, permissions), the log says so and setup falls back to the loopback path: `docker exec -it Pad pad auth setup` runs the first-admin setup from inside the container.
- **/setup keeps asking for a token even though Bypass Setup Token is set** → check that the env var actually reached the container: **Docker** → click Pad → **Edit** → confirm `PAD_BYPASS_SETUP_TOKEN=true`. Then **Force Update** (a value change without a recreate doesn’t re-evaluate startup-time env vars). Cloud mode also ignores the flag, so make sure `PAD_CLOUD` / `PAD_MODE` aren’t set.

## Going further

- Connect a workspace: wire your laptop CLI into the Unraid instance.
- Agent integration: Claude Code / Cursor / Windsurf / Codex setup.
- MCP — Local: Pad as an MCP server for MCP-aware tools.
- Self-Hosting: fundamentals (auth, security, Pad Cloud comparison) that apply to any host, not just Unraid.
- Unraid forum support thread: Unraid-specific install and runtime questions.
- Pad source: github.com/PerpetualSoftware/pad
- Unraid template source: github.com/PerpetualSoftware/unraid-templates, the canonical home of `pad.xml`. PRs to tweak the template (typo, new env var, polished overview) go there.
