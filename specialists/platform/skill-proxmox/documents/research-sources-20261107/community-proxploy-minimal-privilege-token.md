Contents of https://docs.proxploy.dev/getting-started/proxmox-token/:
# The minimal-privilege API token

## Why per-capability tokens, not one broad login

[Section titled “Why per-capability tokens, not one broad login”](#why-per-capability-tokens-not-one-broad-login)

Proxploy never asks for your `root@pam` password, even transiently. Instead,
it creates one dedicated PVE user (`proxploy@pve`) and one custom role per
*capability* (read-only monitoring, lifecycle, console, backup, node power)
and issues one API token per capability you actually enable. Nothing is granted
until you opt into the feature that needs it: enabling only monitoring
gets Proxploy a token that can read your cluster and nothing else.

Tokens use Proxmox’s privilege-separated mode (`--privsep 1`), so a token’s
effective permissions are the *intersection* of its own ACLs and the backing
user’s: the token itself can’t reach further than what you granted it
directly, even if the user account it belongs to later gains more.

| Capability | Custom role | PVE privileges | Used for |
| --- | --- | --- | --- |
| Read-only monitoring (always required) | `ProxployAudit` | `VM.Audit`, `Datastore.Audit`, `Sys.Audit`, `Pool.Audit`, `SDN.Audit` | Pollers, the dashboard, metrics, Apps/VMs read views, storage/network read pages |
| Lifecycle | `ProxployLifecycle` | `VM.PowerMgmt`, `VM.Config.Disk`, `VM.Config.CPU`, `VM.Config.Memory`, `VM.Config.Network`, `VM.Config.Options`, `VM.Allocate`, `VM.Clone`, `VM.Snapshot`, `VM.Snapshot.Rollback`, `VM.Migrate`, `Sys.Modify`, `Datastore.Allocate`, `Datastore.AllocateSpace` | Start/stop/restart/pause, resource edits, snapshots, clone, cluster-native migration, CT/VM create-destroy through the API, plus the node-level infrastructure edits guest lifecycle depends on: network bridge staging/apply (`Sys.Modify`), attaching/detaching a storage pool definition (`Datastore.Allocate`), and storage content writes such as an uploaded ISO or a stray volume delete (`Datastore.AllocateSpace`) |
| Console | `ProxployConsole` | `VM.Console`; `Sys.Console` only if you opt into node shells | CT/VM console tickets (the in-browser terminal and noVNC); node shell needs `Sys.Console` as a separate opt-in. On real hardware, a node shell opened this way lands on the node’s `/bin/login` prompt, not a root shell: you still need the node’s own root password to get further, so this privilege is a gate on reaching that prompt, not root access by itself |
| Backup | `ProxployBackup` | `VM.Backup`, `Datastore.AllocateSpace`, `Datastore.Audit` | vzdump/PBS backup and restore jobs, backup listing |
| Node power | `ProxployNodePower` | `Sys.PowerMgmt` | Reboot/power off the node itself. Its own role and token, never folded into Lifecycle: rebooting the hypervisor is a different blast radius than restarting one guest on it, so a leaked Lifecycle token must not carry node power. Independent of which other capabilities you enable |

Monitoring is mandatory; lifecycle, console, backup, and node power are
checkboxes in the host wizard. Enable only what you plan to use.

ACLs are granted at path `/` with propagation on by default, since Proxploy
is meant to manage a whole host. If you’d rather scope Proxploy to one
resource pool, grant the same roles on `/pool/<name>` instead; the
onboarding verifier (below) reports exactly what Proxploy can see either
way.

## How onboarding generates it

[Section titled “How onboarding generates it”](#how-onboarding-generates-it)

1. You enter the host’s URL and choose which capabilities to enable.
   Proxploy fetches the static [capability catalogue](/reference/hosts/#get-apiv1hostscapabilities)
   so the wizard can show you what each capability grants and what you
   give up by unticking one.
2. The wizard generates a **copy-paste `pveum` script** for exactly the
   capabilities you chose: it creates `proxploy@pve`, the custom roles,
   ACLs for both the user and each token (privilege-separated tokens need
   their own ACLs), and one token per enabled capability. The script is
   generated server-side by `POST /hosts/token-script` so the token IDs
   and secrets are never assembled in the browser.
3. You run that script yourself, in a node shell you already own; Proxploy
   never sees or asks for root credentials at any point.
4. You paste the resulting token id(s) and secret(s) back into the wizard.
5. Proxploy verifies: it calls `GET /version` to confirm connectivity and
   TLS, then `GET /access/permissions` for each token and diffs the granted
   privileges against what that capability expects, reporting both
   anything missing (a feature will fail) and anything extra (you granted
   more than needed, and it says so). You can re-run this check later from
   Settings.

Enabling a capability later re-enters the wizard for just that capability’s
role and token. Disabling one deletes the stored token from Proxploy and
tells you the `pveum` commands to remove the matching role and token on the
PVE side too.

Token secrets are encrypted at rest the moment they’re saved and are never
written to a log or an audit row in plaintext.
