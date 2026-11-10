**Title:** MCP — Troubleshooting

**Source:** [https://www.getpad.dev/docs/mcp/troubleshooting](https://www.getpad.dev/docs/mcp/troubleshooting)

---

# Page Structure Map
```text
MCP — Troubleshooting
├── Connection refused or DNS
├── OAuth window closes immediately
├── Provider not linked
├── 401 after working previously
├── 403 forbidden
├── Unknown workspace
├── Tools missing after restart
└── Still stuck?
```

---

If the connect flow didn’t work, find the symptom you’re seeing in the table below. Each row links to a fuller explanation in the sections that follow.

| Symptom | Likely cause | Section |
| --- | --- | --- |
| Agent says “Connection failed” / “Could not reach the server” | Network or URL typo | [Connection refused / DNS](#connection-refused-or-dns) |
| OAuth window opens then closes immediately | Cookies disabled or third-party cookie restrictions | [OAuth window closes immediately](#oauth-window-closes-immediately) |
| “That GitHub/Google account isn’t linked to a Pad account” | You have a password-based Pad account that hasn’t linked the SSO provider | [Provider not linked](#provider-not-linked) |
| Tool call returns 401 unexpectedly | Token revoked or membership changed | [401 after working previously](#401-after-working-previously) |
| Tool call returns 403 | Capability tier or workspace role insufficient | [403 forbidden](#403-forbidden) |
| Tool call returns `unknown_workspace` | The workspace isn’t in your token’s allow-list | [Unknown workspace](#unknown-workspace) |
| Agent doesn’t see Pad’s tools at all | Re-handshake needed | [Tools missing after restart](#tools-missing-after-restart) |

---

## Connection refused or DNS

```
Connection failed: ENOTFOUND mcp.getpad.dev
```
- **Check the URL.** It’s `https://mcp.getpad.dev` — `mcp` then `getpad.dev`. Trailing slashes are fine; the agent client handles them.
- **Check your network.** Some corporate proxies block uncategorized domains; try from a personal network if you can.
- **Try `curl`** from the same machine: `curl -I https://mcp.getpad.dev/.well-known/oauth-protected-resource`. A 200 response means the network path works and the issue is in the agent client’s HTTP layer (often fixable by restarting the client).

## OAuth window closes immediately

The OAuth handshake requires cookies on `app.getpad.dev`. If your agent’s embedded browser has third-party cookies disabled or is in a strict-isolation mode, the consent flow can’t complete because the post-login redirect can’t read the session.

- **Try the explicit-browser path.** Most agents have a setting like “Open auth in external browser” — that uses your default browser, which has normal cookie support.
- **Allow `*.getpad.dev` cookies** in your browser settings. We use `app.getpad.dev` for auth and `mcp.getpad.dev` for transport; both are first-party from your perspective.

## Provider not linked

If you signed up to Pad with email + password and haven’t linked GitHub or Google to your account, sign-in via SSO will fail with:

> *That GitHub/Google account isn’t linked to a Pad account. Sign in with your password below, or retry with a different account.*

This is a deliberate security feature — it prevents someone with access to your inbox from silently linking a new SSO provider to your account.

**Fix:**

1. Sign in with your existing Pad password on the sign-in page.
2. Open `app.getpad.dev/console/settings`.
3. Under **OAuth providers**, click **Link GitHub** or **Link Google**. Complete the OAuth flow once.
4. Future SSO sign-ins from your agent will work.

## 401 after working previously

Your agent connected successfully yesterday but today every tool call returns 401. Two common causes:

1. **Token revoked.** You (or another admin on a workspace you had access to) revoked the connection from `app.getpad.dev/console/connected-apps`. Reconnect: most agent clients show a “Re-authenticate” button on the connector that triggers a fresh OAuth handshake without re-pasting the URL.
2. **Token expired and refresh failed.** Pad’s tokens are long-lived (30 days for the access token, with refresh) but if your machine was offline through the entire refresh window, the refresh token might have expired. Re-authenticate to issue a fresh pair.

## 403 forbidden

Returned when the token is valid but the operation isn’t allowed. The error envelope tells you why:

```
{
  "code": "permission_denied",
  "message": "...",
  "details": { "required_role": "Editor", "current_role": "Viewer" }
}
```
- `required_role` is what the operation needs (e.g. Editor for `pad_item.action: create`).
- `current_role` is what your account currently has in the workspace.

**Fix:** ask the workspace owner to bump your role, OR ask the agent to do a read-only operation instead.

If `current_role` is `null`, your membership in that workspace was revoked since the token was issued. The token is still valid for *other* workspaces in its allow-list, just not this one.

## Unknown workspace

```
{
  "code": "unknown_workspace",
  "message": "...",
  "details": { "available_workspaces": ["foo", "bar"] }
}
```

You asked the agent to operate on a workspace that isn’t in this connection’s allow-list. Either:

- **You forgot you didn’t grant access to that workspace.** Reconnect (re-run the OAuth flow) and tick the additional workspace at the consent screen, OR
- **You consented to “any workspace” originally** — but a new workspace you created later isn’t picked up by an existing token until you reconnect or re-authenticate. Click **Re-authenticate** on the connector.

## Tools missing after restart

After upgrading your agent client (Claude Desktop, Cursor, etc.), the connector is still listed but the tools are gone from the in-conversation surface.

- **Disconnect and reconnect.** The MCP handshake runs on connection establishment; restarting the agent client without explicitly reconnecting can leave the tools field empty.
- **Check the handshake.** If the agent client has a developer / inspector view, look at the initialize response under `result.capabilities.experimental.padToolSurface.version`. It should be `"0.9"`. The same value is also reachable via the `pad://_meta/version` resource (`tool_surface_version`) or the `pad_meta` tool with `action: version`. If it’s missing or different, file an issue.

---

## Still stuck?

- Check `app.getpad.dev/console/audit-log` for `mcp.tool_call_failed` events on your account. The reason is logged.
- Open an issue on [GitHub](https://github.com/PerpetualSoftware/pad/issues) with the agent name + version, the URL you pasted, and (if available) the OAuth client ID from the consent screen.

[← Remote MCP overview](https://www.getpad.dev/mcp/remote)
