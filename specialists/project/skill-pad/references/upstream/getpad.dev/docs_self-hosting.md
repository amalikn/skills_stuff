**Title:** Self-Hosting

**Source:** [https://www.getpad.dev/docs/self-hosting](https://www.getpad.dev/docs/self-hosting)

---

# Page Structure Map
```text
Self-Hosting
├── Running as a Service
│   ├── systemd (Linux)
│   ├── Docker
│   └── Docker Compose (PostgreSQL + Redis)
├── Reverse Proxy
│   ├── Caddy
│   └── Nginx
├── Data & Backups
│   └── Backing up
├── Authentication
│   ├── First-time setup
│   │   └── Docker: create the first admin from the container logs
│   ├── Subsequent logins
│   ├── Forgotten password (locked out)
│   ├── User accounts and roles
│   └── API tokens
└── Security Considerations
```

---

Pad is local-first. By default it runs on your laptop and binds to `127.0.0.1:7777` — that’s the recommended setup for solo use.

If you want to reach **your own** Pad from multiple devices you control — laptop + phone + work machine on the same LAN, Tailscale, or home VPN — running it on a small server or NAS works well. This page covers that single-user, multi-device setup.

> **Running Pad on Unraid?** There’s a one-click Community Applications template — skip the systemd / Docker recipes below and use the Unraid-specific walkthrough instead.

> **Setting up Pad for a team?** Pad Cloud is the supported path for multi-user setups — managed hosting, OAuth, team billing, automatic backups, no operator burden. The recipes below assume one user across multiple devices.

## Running as a Service

### systemd (Linux)

Create a service file at `/etc/systemd/system/pad.service`:

```
[Unit]
Description=Pad
After=network.target

[Service]
Type=simple
User=pad
Group=pad
ExecStart=/usr/local/bin/pad server start --host 0.0.0.0 --port 7777
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```
sudo systemctl enable pad
sudo systemctl start pad
```

The Pad data directory defaults to `$HOME/.pad` for the user running the service — with `User=pad`, that’s `/home/pad/.pad/pad.db`. Override with `PAD_DATA_DIR=/srv/pad` (or similar) in the service `Environment=` if you want a different location.

### Docker

```
docker run -p 7777:7777 -v pad-data:/data ghcr.io/perpetualsoftware/pad:0.17.2
```

Pin the release you run, as above. Tags are the bare version with no leading `v` (see the releases). The untagged name means `latest`, which moves to each new stable release, never a release candidate, the next time the image is pulled. To upgrade, back up `/data`, then start the new tag on the same volume. Migrations run on start. Every image is multi-arch and cosign-signed.

### Docker Compose (PostgreSQL + Redis)

The repository’s `docker-compose.yml` runs Pad with PostgreSQL and Redis, using the released image rather than a build of the checkout:

```
git clone https://github.com/PerpetualSoftware/pad
cd pad
cp .env.example .env    # set POSTGRES_PASSWORD, PAD_ENCRYPTION_KEY, and PAD_VERSION
docker compose up -d
```

Set `PAD_VERSION` in `.env` to pin a release; unset, it is `latest`. To upgrade, change `PAD_VERSION`, then run `docker compose pull && docker compose up -d`. The full guide, including the production overlay and Kubernetes manifests, is docs/deployment.md in the repository.

Or build the image yourself:

```
git clone https://github.com/PerpetualSoftware/pad
cd pad
docker build -t pad .
docker run -p 7777:7777 -v pad-data:/data pad
```

Inside the container, Pad writes to `/data` — back up that volume. The default port publishing above (`-p 7777:7777`) exposes Pad on every host interface; for a single-user host bind to a specific interface (e.g. your Tailscale IP) or stick with `-p 127.0.0.1:7777:7777` and reach Pad through a reverse proxy.

## Reverse Proxy

A reverse proxy in front gives you HTTPS — required if you want session cookies to be flagged `Secure` (set `PAD_SECURE_COOKIES=true`).

### Caddy

```
pad.example.com {
    reverse_proxy localhost:7777
}
```

Caddy automatically handles TLS via Let’s Encrypt. Simplest option.

### Nginx

```
server {
    listen 443 ssl;
    server_name pad.example.com;

    ssl_certificate /etc/ssl/certs/pad.pem;
    ssl_certificate_key /etc/ssl/private/pad.key;

    location / {
        proxy_pass http://127.0.0.1:7777;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;  # Required for SSE
    }
}
```

If you put any reverse proxy in front, also set `PAD_TRUSTED_PROXIES` to the proxy’s IP/CIDR so Pad will honor the forwarded headers (rate limits, audit logs, the bootstrap loopback check).

## Data & Backups

Pad stores everything in a single SQLite database file. The path depends on how you’re running it:

| Setup | Database path |
| --- | --- |
| Local install (the default) | `~/.pad/pad.db` |
| systemd (`User=pad`) | `/home/pad/.pad/pad.db` |
| Docker | `/data/pad.db` (inside the container; persisted by the named volume) |

Override the location with `PAD_DATA_DIR=/some/path` — the database lives at `$PAD_DATA_DIR/pad.db`.

### Backing up

```
# Local install — stop Pad first OR use SQLite's online backup
sqlite3 ~/.pad/pad.db ".backup '~/.pad/pad.db.backup'"

# systemd
sudo systemctl stop pad
sudo cp /home/pad/.pad/pad.db /home/pad/.pad/pad.db.backup
sudo systemctl start pad

# Docker — copy the volume contents
docker run --rm -v pad-data:/data -v "$PWD":/backup alpine \
    cp /data/pad.db /backup/pad.db.backup
```

The database file is the single source of truth. There are no external dependencies to back up.

## Authentication

Pad uses **user accounts** with email + password. On a fresh install, there are no users — the server runs unauthenticated until the first admin is bootstrapped, then every API request and the web UI require auth.

### First-time setup

```
# On the server host (loopback-only — see note below):
pad auth setup
```

`pad auth setup` is gated on the loopback check: it runs only when the request comes from the server itself. That’s deliberate — it creates the unauthenticated window during which the first admin is minted, and forces you to be physically on the server (or `docker exec`\-ing into the container) to do it.

#### Docker: create the first admin from the container logs

With Docker (or Compose), the setup request comes from your laptop, not from inside the container — so the plain “open the URL and create an admin” path is blocked by the same loopback gate. Pad handles this with a **one-time token logged on first start**. When the container comes up with zero users, it writes a banner to stderr (captured by `docker logs`) containing a setup URL:

```
========================================================================
  Pad first-run setup
========================================================================

  No users exist yet. To create the first admin account, visit:

      http://<your-host>:7777/setup#token=<TOKEN>

  This token is one-time. After the first admin is created the token
  is consumed and this banner stops appearing.
========================================================================
```

To use it:

```
# Grep the banner out of the container logs:
docker logs <container> 2>&1 | grep -A8 'Pad first-run setup'
```

Copy the full `http://<your-host>:7777/setup#token=<TOKEN>` line and open it in your browser — use the exact host and port from the banner, not `localhost` (which won’t reach a container on another machine). Fill in email/name/password and you’re the admin. The `#token=` part is a URL **fragment** — browser-only, never transmitted to a server, so it can’t leak into proxy or access logs; the frontend reads it and submits the token via an `X-Bootstrap-Token` header. Once the first admin exists the token is consumed and the banner stops.

Two alternatives to the logs-token dance:

- **CLI inside the container** — `docker exec -it <container> pad auth setup`. Running inside the container counts as loopback, which the bootstrap gate allows.
- **Skip the token (trusted networks only)** — set `PAD_BYPASS_SETUP_TOKEN=true`. No token is generated; the first visit to `http://<your-host>:7777/setup` takes email/name/password directly and creates the admin in one round-trip. Only safe when the WebUI port **isn’t** reachable from the open internet (anyone who races you to `/setup` becomes admin). Ignored in cloud mode (`PAD_CLOUD=true` / `PAD_MODE=cloud`), where the loopback gate always stays on.

### Subsequent logins

```
pad auth login    # email + password prompt
pad auth whoami   # show current user
pad auth logout
```

Credentials are stored at `~/.pad/credentials.json` (mode 0600). The CLI auto-attaches the auth token to all API requests.

### Forgotten password (locked out)

If email is configured (a Maileroo API key is set), the web UI’s **Forgot password** link emails a reset link as usual. Without an email provider, recover the account **from the server host** — the same loopback trust model as `pad auth setup`:

```
# Run on the server itself. Prints a single-use reset link to open in a browser:
pad auth reset-password admin@example.com

# Headless box with no browser? Set a random temporary password instead.
# Log in with it, then change it immediately — existing sessions are signed out:
pad auth reset-password admin@example.com --temp-password
```

This calls a loopback-only endpoint: no login required (you’re locked out, after all), but it **only** accepts a direct request from the server itself — proxied or remote requests are refused. The web **Forgot password** page detects when no email provider is configured and shows these same instructions instead of a dead “we emailed you a link” message.

As a fallback, submitting the web reset form on an instance with no email also logs the reset path, e.g. `reset_path=/reset-password/<token>` — open `<your-base-url>/reset-password/<token>` to finish the reset by hand.

### User accounts and roles

Once the first admin exists, add more people by inviting them to a workspace:

```
# Invite a user to a workspace
pad workspace invite user@example.com --role editor

# If they already have an account they're added directly; otherwise Pad prints
# a join code (or emails an invite when email is configured). They accept with:
pad workspace join <code>
```

Roles:

| Role | Permissions |
| --- | --- |
| `owner` | Full workspace access including settings, member management |
| `editor` | Create / edit / delete items |
| `viewer` | Read-only |

### API tokens

For CI, agents, or scripts, create user-scoped API tokens from the web console: sign in and open **Settings → API Tokens** (`/console/settings`). Enter a name and click **Create** — the token is shown once, so copy it then. Pass it in the `Authorization: Bearer <token>` header, and delete it from the same screen to revoke it.

Each token is **Read and write** or **Read only**: pick one under **Access** when creating it (or `pad token create --scopes read`), and the token list shows each key’s access. A token never exceeds your role in a workspace. See the API reference for what read-only allows and for creating tokens over the API.

## Security Considerations

- Run `pad auth setup` immediately after first start. Until you do, the server accepts unauthenticated requests from loopback.
- For anything reachable beyond your laptop, terminate TLS in front (reverse proxy) and set `PAD_SECURE_COOKIES=true` so session cookies are flagged `Secure`.
- Set `PAD_CORS_ORIGINS` to the comma-separated origins of your web UI hosts. Without it, cookie-authenticated browser fetches from other origins are rejected.
- The SQLite database is unencrypted on disk. Protect it with filesystem permissions (the default `0600` is correct).
- The default bind is `127.0.0.1` — Pad won’t accept remote connections unless you opt in with `--host 0.0.0.0` or `PAD_HOST=0.0.0.0`.
