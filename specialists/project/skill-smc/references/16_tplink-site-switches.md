# TP-Link Site Switches — Access, Quirks and Config Capture

The on-site TP-Link switches that sit on a site's management network behind the SMC box. They carry the SMC's VLAN trunks (management, client Wi-Fi, R195P provisioning and the `internetNN` WAN VLANs),
so they are the "switching layer" that `01_overview.md` refers to. First reached 2026-09-24 at kalumburu. Tooling: `scripts/tplink-switch.sh` and `scripts/tplink_cli_driver.py` (see
`scripts/README.md`).

## Contents

- [Where they are](#where-they-are)
- [Credentials](#credentials)
- [Access path and SSH quirks](#access-path-and-ssh-quirks)
- [Privilege: enable with and without a password](#privilege-enable-with-and-without-a-password)
- [Discovery: why ARP is not enough](#discovery-why-arp-is-not-enough)
- [Config capture](#config-capture)
- [Kalumburu as found (2026-09-24)](#kalumburu-as-found-2026-09-24)
- [Pitfalls](#pitfalls)

## Where they are

Candidates from unified-network-controller's discovery sweeps (`docs/reports/inventory/*-discovery-sweep-*.md`), by TP-Link OUI only; a TP-Link OUI is not proof of a switch until `--discover` shows
the `TPSSH` banner or a login confirms it:

| Site         | TP-Link addresses in the sweep           | Confirmed                           |
| ------------ | ---------------------------------------- | ----------------------------------- |
| kalumburu    | 10.255.0.2, 10.255.0.3                   | Both, SG2428P switches (2026-09-24) |
| aurukun      | 10.255.1.1-2, 10.255.2.1-2, 10.255.3.1-2 | No                                  |
| bidyadanga   | 10.255.0.2-4                             | No                                  |
| burringurrah | 10.255.0.2-3                             | No                                  |
| doomadgee    | 10.255.0.2-3                             | No                                  |
| galiwinku    | 10.255.0.2-4                             | No                                  |
| hope-vale    | 10.255.0.2-4                             | No                                  |
| kowanyama    | 10.255.0.2-3                             | No                                  |
| pukatja      | 10.255.0.2-3                             | No                                  |

The pattern at most sites is `10.255.0.2` upward, directly after the SMC's own `bridge_500` address `10.255.0.1`. Galiwinku's WAN trunks name their switches `switch01`/`switch02` in topology_vars
(`01_overview.md` "WAN Uplink Topology Pattern").

## Credentials

KeePass entry `/Network/tplink switch`, user `admin`; its Notes list `10.255.0.2` and `10.255.0.3`. Read with the `kp` wrapper, never printed: the script pipes the password over stdin to the SMC, so
it never appears in a command line, process list or transcript. Verified at kalumburu only. Whether the same password holds at other sites is unknown until each is tried; the script allows one
password attempt per run (`NumberOfPasswordPrompts=1`) so a wrong entry cannot build up failures against a lockout. Override the entry with `TPLINK_KP_ENTRY`, and name a separate enable password with
`TPLINK_KP_ENABLE_ENTRY`.

## Access path and SSH quirks

Workstation -> `tsh ssh --proxy=<cluster> root@<site>-smc01` -> `ssh admin@<switch>` from the SMC. Found on SG2428P firmware 5.30.1 Build 20240202 (SSH server `TPSSH-1.0.0`):

| Quirk           | Symptom without the fix                                                                                                | Fix                                       |
| --------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| MAC list        | `Unable to negotiate ... no matching MAC found. Their offer: hmac-sha1-160,hmac-sha2-256,hmac-sha2-512,hmac-ripemd160` | `-o MACs=hmac-sha2-256`                   |
| Host key        | Session closes straight after `SSH2_MSG_SERVICE_ACCEPT`, before any auth method is offered                             | `-o HostKeyAlgorithms=+ssh-rsa`           |
| Pubkey          | Root's key is offered first (`sign_and_send_pubkey: no mutual signature supported`) and the switch drops the session   | `-o PubkeyAuthentication=no`              |
| No exec channel | `ssh switch "show ..."` and a piped stdin both log in and close at once (`ssh_tty_make_modes: no fd or tio`)           | A real pty: the driver uses `pty.fork()`  |
| Enter           | LF does nothing; commands run together (`show system-infoexit`)                                                        | Send CR (`\r`)                            |
| First keystroke | The first command after login is swallowed                                                                             | Send a blank CR first                     |
| Banner order    | The server sends its version banner only after the client's                                                            | Send `SSH-2.0-...\r\n` first when probing |

Kex and cipher are not an issue: `diffie-hellman-group16-sha512` and `aes128-ctr` negotiate by default. Telnet (tcp/23) is refused; HTTPS (tcp/443) is open for the web UI, reachable with
`scripts/teleport-tunnel.sh <site> <switch_ip> <port> 443`. Plain HTTP on 80 gave no answer.

## Privilege: enable with and without a password

After login the prompt is `>` (for example `Switch1>`), and `show system-info` returns `Error: Bad command` there, so `enable` comes first. Three cases, handled by the driver and reported on stderr as
`privilege: ...`:

- `enable-no-password`: `enable` goes straight to `#`. Both kalumburu switches.
- `enable-password`: `enable` asks for a password. The driver sends the `TPLINK_KP_ENABLE_ENTRY` password, or the login password when none is set; one attempt only, exit 6 on failure. Not yet seen
  live.
- `already-privileged`: the login lands on `#`, so no `enable` is sent. Not yet seen live.

The driver also answers an in-CLI `User:`/`Username:` prompt, in case a firmware asks for a CLI login after SSH. Not yet seen live.

## Discovery: why ARP is not enough

The SMC's ARP table cannot be used as the host list. `net.ipv4.neigh.default.gc_thresh1` is **1** on the SMCs checked (kalumburu, mornington;
kernel 5.15, upstream default 128, and no sysctl file, `/etc`, `/usr/local`, `/opt` or ansible-wifi setting found to explain it), so the garbage collector may purge any unused
entry once `gc_stale_time` (60 s) passes; the switches rarely talk to the SMC and vanish between runs. `--discover` therefore runs `fping -a` over the management subnet only (routes on `bridge_500` or in `10.255.x`) and probes each
live host's SSH banner for `TPSSH` (about 30 s at kalumburu's /19).

**Never sweep the client bridges.** A first version swept every connected `10.x` route, which included `bridge_501`, a /18 of public Wi-Fi clients: it pinged customer devices, took 4.5 minutes, and
flooded the neighbour table with thousands of `INCOMPLETE` entries. Without `fping` the script falls back to ARP and warns that quiet switches can be missed.

## Config capture

`scripts/tplink-switch.sh <site> <ip> --backup <dir>` runs `show system-info` and `show running-config`, redacts every `password`/`secret`/`community`/`key`/`passphrase`/`psk` value, refuses to write
if the known login or enable password survives, and writes `<dir>/<site>/<system-name>_<ip>_<YYYYMMDD_hhmm>.cfg` with the system-info as a `!` comment header. The paging prompt (`Press any key to
continue`) is answered automatically. Unified-network-controller keeps these as durable, git-tracked samples under `captures/tplink-switch-configs/` (operator, 2026-09-24): capture each switch's
config as each site is visited.

## Kalumburu as found (2026-09-24)

|             | 10.255.0.2                                                 | 10.255.0.3        |
| ----------- | ---------------------------------------------------------- | ----------------- |
| System name | Switch1                                                    | Switch 2          |
| Model       | SG2428P 5.30 (Omada 28-port Gigabit Smart Switch, 24 PoE+) | SG2428P 5.30      |
| Firmware    | 5.30.1 Build 20240202 Rel.61907                            | same              |
| Serial      | 22480S0000948                                              | 22480S0000014     |
| MAC         | B0-19-21-EA-92-3B                                          | B0-19-21-EA-8E-95 |

Switch1's VLANs: 1 System-VLAN, 500 Management, 501 Public Wifi, 502 R195 Prov, 503 Private Wifi, 521-528 Internet 1-8 (each on its own access port, Gi1/0/9-16, and tagged on the Gi1/0/1 uplink).
Ports 25-28 are SFP, all down.

## Pitfalls

- On 2026-09-24 the login password was sent after an `enable` that asked for none; the CLI took it as a command (`Error: Event not found`), so it may sit in Switch1's CLI history. Never send a
  password unless a password prompt is on screen; the driver waits for one.
- Stale host keys: every connection uses `UserKnownHostsFile=/dev/null`, because multi-SMC sites and swapped units change keys (`01_overview.md`).
- Writes: the script is read-only by default (`show`, `ping`, `tracert` only). `--write` sends config commands to a production switch and needs the operator's explicit go-ahead.
