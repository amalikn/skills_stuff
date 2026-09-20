# Device Access and the KeePassXC Vault

## Contents

- [Rule: No Plaintext Secrets](#rule-no-plaintext-secrets)
- [Vault Structure — Flat, Not Nested](#vault-structure--flat-not-nested)
- [Rogue / Legacy-Password Units](#rogue--legacy-password-units)
- [`kp` Wrapper Gotchas](#kp-wrapper-gotchas)
- [Reference Convention](#reference-convention)
- [Confirmed Live Network Path to a Site (Hope Vale, 2026-09-17)](#confirmed-live-network-path-to-a-site-hope-vale-2026-09-17)
- [cnMaestro REST API v2 Access (2026-09-18)](#cnmaestro-rest-api-v2-access-2026-09-18)

---

## Rule: No Plaintext Secrets

Never write a device password into a repo, a chat log, a memory-keeper entry, or any markdown file — including while describing an anomaly in the value (learned the hard way 2026-09-17: a password
string ended up quoted in two files and one memory-keeper entry while documenting a formatting quirk in it, caught by post-edit grep and fixed). Store the real value in the vault; everywhere else, use
the `<secret:keepassxc:...>` reference syntax below.

## Vault Structure — Flat, Not Nested

Vault: `~/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx`, group `cambium-devices/`. Structure decided 2026-09-16, operator-corrected mid-build from an initial nested
`cambium-devices/<family>/admin` layout to a **flat** one:

| Entry                                 | Covers                                                                                                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `cambium-devices/enterprise-wifi`     | XV2-2T0, XV2-22H, E500, E430 (standard password)                                                                                                             |
| `cambium-devices/enterprise-wifi-\`   | Un-recredentialed XV2 stragglers (old factory password)                                                                                                      |
|   `legacy`                            |                                                                                                                                                              |
| `cambium-devices/epmp-ap`             | ePMP 3000, ePMP 3000L (standard password)                                                                                                                    |
| `cambium-devices/epmp-ap-legacy`      | ePMP 1000, ePMP 1000 2.4 GHz / 5 GHz Connectorized (old default)                                                                                             |
| `cambium-devices/epmp-sm`             | Force 300-16, Force 300-25 (standard password)                                                                                                               |
| `cambium-devices/epmp-sm-legacy`      | Force 180; un-recredentialed Force 300 stragglers (old default)                                                                                              |
| `cambium-devices/cnpilot-r-series`    | R195P                                                                                                                                                        |
| `cambium-devices/cnwave-60ghz`        | V5000, V3000, V2000, V1000                                                                                                                                   |
| `cambium-devices/apn-snmp-ro`         | SNMPv2c read-only community, `rcp`-flavour sites (2026-09-17)                                                                                                |
| `cambium-devices/apn-snmp-rw`         | SNMPv2c read-write community, `rcp`-flavour sites — untested                                                                                                 |
| `cambium-devices/nbn-snmp-ro`         | SNMPv2c read-only community, `nbn_accelerate`-flavour sites                                                                                                  |
| `cambium-devices/nbn-snmp-rw`         | SNMPv2c read-write community, `nbn_accelerate`-flavour sites — untested                                                                                      |
| `cambium-devices/nbn-cnmaestro-api`   | cnMaestro REST API v2 OAuth2 client (URL/UserName = client_id, Password = client_secret) for the `cw-cnmaestro01`/`nbn_accelerate` controller — see "cnMaestro |
|                                       |   REST API v2 Access" below                                                                                                                                  |

Every entry's username is `admin`. Don't create a fresh sub-group per family — put the family/variant name directly in the entry title under the flat `cambium-devices/` group.

## Rogue / Legacy-Password Units

A minority of individual Enterprise Wi-Fi (XV2) and ePMP SM (Force 300) field units were never re-credentialed from the old factory default to the standard password. There's no way (as of 2026-09-17)
to tell which specific serials from the asset registers or family matrix alone — try the family's primary vault entry first, fall back to the matching `-legacy` entry per device if it fails.

## `kp` Wrapper Gotchas

The `kp` wrapper (`~/.config/keepassxc/kp`) only pipes **one** line to stdin — the vault's own master password (from Keychain, service `KEEPASS_MASTER`). Learned building this vault structure
2026-09-16:

- `keepassxc-cli mkdir` creates exactly **one** group level per call — no recursive parent creation. Create every intermediate group explicitly before adding an entry under it.
- `keepassxc-cli add`/`edit` **fail** if a parent group doesn't exist yet — the error is a generic "Could not create entry", not "group missing".
- `add -p` / `edit -p` need a **second** stdin line (the entry's own password) — the `kp` wrapper doesn't supply that. For scripted adds, call `keepassxc-cli` directly:

  ```bash
  DB="$HOME/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx"
  PW=$(security find-generic-password -a "$USER" -s KEEPASS_MASTER -w)
  printf '%s\n%s\n' "$PW" "<entry password>" | keepassxc-cli add -q -u admin -p "$DB" "cambium-devices/<name>"
  ```
- Always verify a write by reading it back: `kp show -a Username -a Password "cambium-devices/<name>"`.

## Reference Convention

In any file, reference a device's access value as `<secret:keepassxc:cambium-devices/<entry>>` — never the value. This matches `cambium-swap`'s own
`.archcore/rules/no-plaintext-values-or-binaries.rule.md` convention; use the same syntax in any other consuming project.

## Confirmed Live Network Path to a Site (Hope Vale, 2026-09-17)

Verified end-to-end from an agent session: `tsh ssh root@hope-vale-smc01` (Teleport target `teleport.communitywifi.net.au`, per `skill-smc`'s `nbn_accelerate` → communitywifi project split) reaches
the site's SMC box directly — no `~/.ssh/config` ProxyCommand entry needed, `tsh ssh` is sufficient on its own. From that box, `bridge_500` (`10.255.0.1/19`) is the device management network and spans
the whole `10.255.0.0–31.255` range used by both Hope Vale and Burringurrah naming conventions (see `03_asset-register-conventions.md`) — a device's `management_ip` from `device-inventory.csv` is
reachable by plain `ping`/`ssh` from the SMC box once the Teleport session is up. Not reachable from a workstation directly (no route over the general APN/community-wifi VPN tunnel); the SMC box is
the only hop.

**Resolved (2026-09-17):** the credential-materialization block above was fixed with a narrow `Bash(kp show ... cambium-devices/*)` allow-list added to the calling project's own
`.claude/settings.local.json` — scope it to `kp show` reads only, never a blanket credential allow. Separately, `kp` itself was not resolving on `PATH` inside the Bash tool's shell (no shell rc file
adds `~/.config/keepassxc`) — fixed globally with `ln -sf ~/.config/keepassxc/kp ~/.local/bin/kp` (a directory already on that shell's `PATH`). With both fixed, a real login was completed end-to-end:
`tsh ssh root@hope-vale-smc01` then `sshpass -p "$PASS" ssh admin@10.255.3.1 'show version'` (password captured into a shell variable via `kp show -s -a Password ...`, never printed) returned a
genuine device response — Enterprise Wi-Fi XV2-2T0, serial `WLYB0501N05R`, firmware `6.6.0.3-r9`, confirming the whole vault→Teleport→device chain works, not just each piece in isolation.

**Web UI access, canonical form (2026-09-17):** the SSH-nested-command approach above works, but the operator's own standard practice is a local-port-forward tunnel straight to the device's web UI —
see `skill-smc`'s `references/01_overview.md` for the exact `tsh ssh --proxy <teleport> -L <local_port>:<device_ip>:<device_port> root@<smc-hostname>` form (the explicit `--proxy` flag is what made it
reliable — an earlier attempt without it was flaky). Verified live against the same Tower 1 AP on port 443 (HTTP 200 through the tunnel). Port convention: `443` for current Cambium web UIs (Enterprise
Wi-Fi, ePMP 3000-family), `80` for older ones — operator-stated example: ePMP 1000 serves plain HTTP, not HTTPS.

**`--proxy=` is required, `--cluster=` is wrong, for EVERY `tsh` command against `teleport.communitywifi.net.au` — not just this tunnel case.** `--cluster=` routes to it as a subordinate target (a
trust relationship that doesn't exist — it's its own root), and fails with `transport: authentication handshake failed: EOF`, an error that convincingly fakes a real outage or a missing/decommissioned
node. Real incident, 2026-09-18: two agent sessions doing Cambium device work here hit exactly this and wrongly concluded Hope Vale's `hope-vale-smc01` was down/deregistered. It wasn't — `tsh ls
--proxy=teleport.communitywifi.net.au` and `tsh ssh --proxy=teleport.communitywifi.net.au root@hope-vale-smc01` both worked immediately once the right flag was used. Full detail: skill-smc's
`references/01_overview.md`.

**Enterprise Wi-Fi (XV2/Falcon UI) REST API, confirmed live 2026-09-17:** the web UI is an AngularJS app ("falcon") calling a JSON REST API on the device itself, not just a config form. Auth: `POST
/api/login` with JSON body `{"username": "...", "password": "..."}` (header `Content-Type: application/json`); success returns `{"success":true}` plus two cookies, `api_token` and `XSRF-TOKEN`. Every
subsequent authenticated call must send the cookies AND echo the `XSRF-TOKEN` cookie value back as an `X-XSRF-TOKEN` request header, or it 401s even with valid cookies alone. `POST /api/logout` (same
cookies/header, explicit `Content-Length: 0` if sending no body) ends the session. Confirmed working end-to-end against Tower 1's AP: `GET /api/platform-info` and `GET /api/device-summary` both
returned full structured JSON (hardware SKU, firmware/bootloader/kernel versions, live per-port traffic counters, IP/VLAN/DNS/gateway config, radio channel list, station count, and live cnMaestro
connection status). The API surface is large — 30+ `/api/*` routes visible in the served JS bundle (`radio-config`, `create-wlan`, `packet_capture_status`, `exec-command`, `reboot`, etc.) — only
read-only `GET` endpoints were exercised; **never call a write/exec/reboot endpoint against a production device without explicit operator authorization**, same rule as SSH CLI.

**SSH CLI vs. web UI/API, observed difference (2026-09-17, same device):** SSH's `show version` returns a compact human-readable text summary (model, firmware, serial, uptime, MAC — roughly a dozen
fields). The REST API's `/api/device-summary` alone returned a much larger structured JSON object with everything `show version` has plus per-port RX/TX counters, full network config (IP/mask/
gateway/DNS/VLAN), radio channel list, station count, and — notably — the device's live cnMaestro connection state and target hostname. The web UI/API is the richer, more complete management surface;
SSH's `show` commands look like a narrower read-only convenience layer on the same underlying state. Not yet explored: the SSH CLI's full command set beyond `show version` — untested whether deeper
`show` subcommands reach API parity.

## cnMaestro REST API v2 Access (2026-09-18)

Confirmed live against the `cw-cnmaestro01` on-prem controller for the `nbn_accelerate` fleet — host resolves publicly to `13.237.46.180` (reachable directly, no Teleport tunnel needed for the API
itself), instance version `3.0.0-r34` (operator-confirmed), though the API v2 shape matches the archived `cnmaestro-onprem-6.0.0` user guide exactly.

**Auth — the one real gotcha:** OAuth2 client_credentials against `/api/v2/access/token`, **not** `/api/v2/token`. The wrong path still returns HTTP 400 with plausible-looking OAuth2 error bodies
(`{"error":"unauthorized_client"}` for HTTP Basic auth, `{"error":"invalid_request"}` for credentials-in-body) instead of a 404, so a wrong-path guess reads exactly like a credential problem — cost
real time before the correct path was found in `evidence/archived-docs/E01-cnmaestro-onprem-6.0.0-user-guide.txt` (cambium-swap), line 20330, "Access API" chapter. Correct form:

```bash
curl -sk -X POST -u "<client_id>:<client_secret>" -d "grant_type=client_credentials" \
  https://13.237.46.180/api/v2/access/token
# -> {"access_token":"...","token_type":"bearer","expires_in":3600}
```

Credential = `cambium-devices/nbn-cnmaestro-api` (URL/UserName field = client_id, Password field = client_secret — cnMaestro calls this an "API Client", created under its own System → API Clients
page, named `cw-teleport01` on this instance).

**Site/tower device grouping — the actual payoff.** cnMaestro organises every device into a named `network` object (roughly: site, or a site's sub-chain — e.g. `Doomadgee`, `Doomadgee -T1-T5`,
`Pukatja - T1-T15-P2P`). `GET /api/v2/networks` lists them all; `GET /api/v2/devices?network=<name>&fields=mac,name` (query-string filter, **not** a `/networks/{id}/devices` path segment — this
instance's v2 API explicitly rejects the path form: `"Network/Tower/Site/ManagedAccount filters are not supported at path level in V2. ... rewrite as api/v2/devices?network=default&site=office"`)
returns that network's member devices. This is authoritative device→site ground truth from cnMaestro's own admin-configured hierarchy — a materially better source than inferring site from device
naming conventions or from live ARP tables on each site's SMC box (both of which cambium-swap tried first; see cambium-swap evidence E124 for the full three-pass resolution chain applied to a
635-device multi-site export). Resolved a site (`Aurukun`, 83 devices across 8 network sub-objects) that neither the device-name-prefix pass nor the ARP-table pass had found any trace of at all.

Never called a write endpoint (config/reboot/onboard) against this API — only `GET /api/v2/access/token`, `GET /api/v2/networks`, `GET /api/v2/devices`.
