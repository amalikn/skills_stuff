# SMC Captive Portal

## Contents

- [11. Captive Portal — Architecture, Known Gaps, and Troubleshooting](#11-captive-portal--architecture-known-gaps-and-troubleshooting)
- Two-tier architecture (incl. PHP SAPI — mod_php, NOT PHP-FPM)
- APN vs NBN Accelerate protocol differences
- Eclipse config.txt sync
- View template versions
- Apache + PHP-FPM wiring (⚠️ historical, ff-smc01 only — never reached production)
- PHP short_open_tag issue
- Kohana exception handler issues
- End-to-end portal verification
- `Directory APPPATH/cache must be writable` — portal dead at bootstrap
- What the portal keeps on the box (state inventory for a disposable writable area)

## 11. Captive Portal — Architecture, Known Gaps, and Troubleshooting

### 11.1 Two-tier architecture

The captive portal is a two-tier system:

| Tier   | Component                                   | Role                                                                              |
| ------ | ------------------------------------------- | --------------------------------------------------------------------------------- |
| Remote | Eclipse server (`wifi.activ8me.net.au:443`) | Site config source of truth; pushes config.txt; can run arbitrary Commands on SMC |
| Local  | Kohana PHP app at `/var/www/html/wifi`      | Renders portal; reads config.txt; calls Eclipse on each page load                 |

Apache serves the portal and the Kohana framework handles routing, templating, and Eclipse integration.

**PHP SAPI — corrected 2026-07-28.** This file previously stated flatly that "PHP-FPM processes `.php` files". That is **not true of the production fleet**. Verified on three sampled `rcp` hosts
(horn-island, kalumburu, mornington): **zero** `php*-fpm` packages installed, `libapache2-mod-php` installed, `apache2ctl -M` shows `php_module (shared)`, and no `/etc/php/8.1/fpm/` directory exists
at all. Production SMCs run **mod_php, executing as `www-data` inside the Apache process** — there is no FPM pool, no socket, and no `proxy_fcgi`.

This matters for any permissions question: file/directory access is decided by `www-data`'s rights, and there is no FPM pool config (`open_basedir`, `chroot`, unit sandboxing) to blame when something
is unwritable. See §11.8.

The PHP-FPM material in §11.4 below describes work done on `family-friendly-smc01` in June 2026 that was **reverted and never reached the production fleet** — read it as history, not as current
architecture.

### 11.2 Eclipse config.txt sync

**Location**: `/var/www/html/wifi/application/config/config.txt` (NOT the web root — `config.txt` in `/var/www/html/wifi/` is never read)

**How it gets populated**: On every PHP page request, `WiFi_Config::sync()` calls `run_eclipse_command()` which:
1. Reads the `Command` field from the current config.txt
2. If non-empty, executes it via `system($command)` — used for software updates (e.g. `git pull`)
3. Fetches fresh site config JSON from Eclipse and writes it to config.txt

**What Eclipse syncs**: JSON blob containing `VIEW_TEMPLATE_VERSION`, `WELCOME_MSG`, `VLAN_501_ACCESS_METHOD`, `PREPAID_BLOCKS`, `TC_SPEED`, `Limited_Sites`, `Asterisk`, `Hardware_List`,
`Software_List`, `Command`, etc.

**What Eclipse does NOT sync**: PHP view template files — those come from the Bitbucket git clone at provision time and are only updated if Eclipse sends a `Command` with a git pull.

**First-request bootstrap**: If config.txt is missing (fresh provision, no Eclipse contact yet), the app defaults to `VIEW_TEMPLATE_VERSION=v1` → serves the v1 template with `p.a8me.au` base URLs.
After first PHP request hits the live host, Eclipse populates config.txt (v3, `wifi.a8me.au`).

**Check Eclipse reachability**:
```bash
curl -sk https://wifi.activ8me.net.au/ -o /dev/null -w "%{http_code}"
# or
telnet wifi.activ8me.net.au 443
```

**Check current config.txt**:
```bash
cat /var/www/html/wifi/application/config/config.txt | python3 -m json.tool
grep VIEW_TEMPLATE_VERSION /var/www/html/wifi/application/config/config.txt
```

### 11.3 View template versions

| Version | Base href              | Notes                                                       |
| ------- | ---------------------- | ----------------------------------------------------------- |
| v1      | `https://p.a8me.au/`   | Old/legacy; loads when config.txt missing                   |
| v3      | `http://wifi.a8me.au/` | Standard for RCP/NBN SMCs (NBN-59-config-management branch) |
| v4      | `http://wifi.a8me.au/` | SMP variant (release/rct_v4 branch)                         |

Eclipse sets `VIEW_TEMPLATE_VERSION` in config.txt. If the portal is showing `p.a8me.au` URLs, config.txt is missing or stale.

### 11.4 Apache + PHP-FPM wiring — HISTORICAL, ff-smc01 only (⚠️ corrected 2026-07-28)

> ⚠️ **Supersession note.** This section was written as if the PHP-FPM wiring was fleet-wide and permanently fixed in Ansible on 2026-06-26. **Both claims are wrong.** Verified 2026-07-28:
> - Repo-wide grep finds **no `SetHandler` in any role template** (the only hit in the tree is a vendored `community.general` test fixture). `portal-site.conf.j2` contains no PHP handler config.
> - The enabled-modules list in `roles/smc_application/tasks/ubuntu-apache-install-configure.yml` is only `rewrite` and `ssl` — **no `proxy`, no `proxy_fcgi`**.
> - Production `rcp` hosts have **no `php*-fpm` package installed** and run mod_php instead (see §11.1).
>
> This matches the long-standing SCRATCHPAD open item recording that the Ansible PHP-FPM change was reverted and needs a different approach. Treat everything below as a record of the
> `family-friendly-smc01` hotfix work only. **Do not use it to reason about production portal behaviour.**

**Symptom**: Portal returns raw PHP source code instead of rendered HTML.

**Cause**: Apache does not know to proxy `.php` requests to PHP-FPM unless explicitly configured.

**Required configuration** (now in `portal-site.conf.j2`):
```apache
<FilesMatch "\.php$">
    SetHandler "proxy:unix:/run/php/php8.1-fpm.sock|fcgi://localhost"
</FilesMatch>
```

**Required Apache modules** (now in `ubuntu-apache-install-configure.yml`):
```yaml
- proxy        # must be enabled before proxy_fcgi
- proxy_fcgi   # handles the unix socket proxy to PHP-FPM
```

**Check Apache is passing PHP to FPM**:
```bash
apache2ctl -M | grep -E "proxy|fcgi"   # should show proxy_module, proxy_fcgi_module
systemctl status php8.1-fpm
ls /run/php/php8.1-fpm.sock            # socket must exist
curl -s http://localhost/ | head -5    # should be HTML, not <?php
```

**Alternative approach (Ubuntu packaged config — applied as live hotfix 2026-06-23)**:
```bash
a2enmod proxy_fcgi setenvif
a2enconf php8.1-fpm     # enables /etc/apache2/conf-available/php8.1-fpm.conf (installed by php8.1-fpm package)
systemctl restart apache2
```
This enables the PHP-packaged Apache config which sets `SetHandler` globally. The Ansible template approach (above) would embed `SetHandler` directly in the VirtualHost, making it self-contained and
not dependent on `a2enconf php8.1-fpm`. ~~the Ansible template approach is now canonical~~ — **neither is canonical**; the Ansible template change was reverted and production runs mod_php with no FPM
at all (§11.1).

**Historical note (corrected 2026-07-28)**: the live hotfix on `family-friendly-smc01` 2026-06-23 (`a2enconf php8.1-fpm`) did happen. The follow-on claim that a permanent Ansible fix "landed
2026-06-26" is **false** — the change was reverted and is not in the repo. Note also that `ubuntu-php-install-configure.yml`'s `php_pkg_suffixes` list *does* include `fpm`, but that install path is
gated behind `php_reinstall_needed`, and no production `rcp` host actually has an FPM package installed. Do not infer the running SAPI from the package list — check `apache2ctl -M` on the box.

### 11.5 PHP short_open_tag issue (Kohana v3 views)

**Symptom**: Portal renders but shows `Undefined variable $error`, `Undefined variable $captive_portal_message`, or `Undefined variable $version` inline in the HTML. Action buttons (Terms and
Conditions, Start Browsing) may be absent.

**Root cause**: PHP 8.1 has `short_open_tag = Off` by default.
- `<? if (isset($var)) { ?>` → **NOT processed** as PHP; passes through as literal text
- `<?= $var; ?>` → **always processed** (echo shorthand enabled since PHP 5.4)
- Result: the `isset()` guard never runs; `<?= $var ?>` executes unconditionally; undefined variable echoes through Kohana error handler
- Orphan `<?php } ?>` closing tags halt PHP execution mid-template, cutting off all subsequent HTML output

**Affected files** (Bitbucket wifi.git, NBN-59-config-management branch):
- `application/views/v3/wifi/welcome.php`
- `application/views/v3/wifi/welcome_contents.php`
- `application/views/v3/wifi/base.php`
- `application/views/v3/wifi/prepaid/resume.php`
- `application/views/v3/wifi/prepaid/success.php`

**Hotfix on live host** (not persistent across software updates):
```bash
# Find all short tags in v3 views
grep -rn "^<? " /var/www/html/wifi/application/views/v3/

# Fix — sed (note: double-substitution hazard if <?php already exists)
sed -i 's/<?\s*/<?php /' /path/to/file.php
# Always follow with cleanup pass for double-substitution artifacts:
grep -rl "<?phpphp" /var/www/html/wifi/application/views/v3/ | xargs sed -i 's/<?phpphp/<?php/g'
```

**Permanent fix**: Replace all `<? ?>` with `<?php ?>` in Bitbucket wifi.git `NBN-59-config-management` branch. Raised to dev team 2026-06-26.

**Check short_open_tag setting**:
```bash
php -r "echo ini_get('short_open_tag');"   # 0 = off (PHP 8.1 default)
grep short_open_tag /etc/php/8.1/fpm/php.ini
```

### 11.6 Kohana exception handler issues (fixed 2026-06-24 on ff-smc01)

**Symptom 1**: Portal returns blank 500 page.
**Cause**: `email_exception()` called in exception handler but function never defined → Fatal Error → empty body.
**Fix**: Guard call with `if (function_exists('email_exception'))`.

**Symptom 2**: Exception message text appears in page body.
**Cause**: Debug line `echo $e->getMessage(); exit;` left in exception handler.
**Fix**: Remove the debug echo.

**Symptom 3**: E_NOTICE errors echoed to page via Kohana error handler.
**Cause**: `error_reporting(E_ALL | E_STRICT)` in Kohana `index.php` converts E_NOTICE to ErrorException via `set_error_handler`.
**Fix**: Change to `error_reporting(E_ALL & ~E_NOTICE)` in `index.php`, or fix the underlying undefined variables.

### 11.7 End-to-end portal verification

```bash
# From SMC itself — check portal responds with HTML
# Must use the real ServerName. Probing localhost with a Host: header hits 000-default
# and returns /var/www/html/index.html (10671 bytes) even when the portal is fully dead.
curl -s wifi.a8me.au | grep -E "btn-apn|Terms|Start Browsing|Undefined|base href"

# From client on VLAN 501 — check captive redirect
curl -s http://1.1.1.1/ -L | grep -i "wifi\|activ8me\|Terms"

# Check which PHP SAPI is actually live (expect php_module = mod_php, NOT proxy_fcgi)
apache2ctl -M | grep -E "php_module|proxy_fcgi"

# Check cache/logs are writable by www-data — a 0755 here kills the whole portal (§11.8)
stat -c '%a %U:%G' /var/www/html/wifi/application/cache /var/www/html/wifi/application/logs

# Check Apache logs for PHP errors
# NOTE: the §11.8 bootstrap failure leaves NOTHING here — an empty log does not mean healthy
tail -50 /var/log/apache2/error.log | grep -E "PHP|AH"

# Check Eclipse sync happened
stat /var/www/html/wifi/application/config/config.txt
python3 -m json.tool /var/www/html/wifi/application/config/config.txt | grep VIEW_TEMPLATE
```

**Portal responding is not the same as pins being issued.** §11.7 above confirms the portal is *reachable*; it says nothing about whether anyone completing the flow actually gets online. For that —
pin validity right now (`iptables -t mangle -L ECLIPSE_MARK`) vs pin issuance over time (the `wifi/access` Apache log audit trail) — see the dedicated `references/14_pin-activation-diagnosis.md`,
including its `audit-pin-activation.sh` tool and the pitfalls in reading either mechanism alone.

---

### 11.8 `Directory APPPATH/cache must be writable` — portal dead at bootstrap (2026-07-28)

**Symptom**: every portal request returns a 40-byte plain-text body `Directory APPPATH/cache must be writable`, with **HTTP status 200**, and **nothing in `/var/log/apache2/error.log`**.

**Mechanism**: Kohana checks writability unconditionally during `Kohana::init()`, before any routing:

```
/var/www/kohana-base/system/classes/kohana/core.php:281
    if ( ! is_writable(Kohana::$cache_dir))
        throw new Kohana_Exception('Directory :dir must be writable', ...);
```

`Debug::path()` rewrites the `APPPATH` prefix to the literal token `APPPATH/`, which is why no real path appears in the message. Kohana catches and *prints* the exception, which is why the status is
200 and apache's error log stays silent — **a status-code-only health check cannot detect this**.

**The same exception exists for logs** at `system/classes/kohana/log/file.php:31`. Fix both `application/cache` and `application/logs`, or the failure just moves one step later.

**Cause**: the directories are `0755 root:root` while Apache runs mod_php as `www-data` (§11.1). They land at 0755 whenever git recreates them — the tracked content is only a `.gitignore` stub, so a
fresh clone applies umask 022. `roles/smc_application` chmods them to `0777` explicitly; if that task is skipped, the portal dies.

**Check**:
```bash
stat -c '%a %U:%G' /var/www/html/wifi/application/cache /var/www/html/wifi/application/logs
# expect 777 root:root on both

V=$(ls /etc/apache2/sites-enabled/ | grep -v 000-default | head -1 | sed 's/.conf$//')
curl -s http://$V/ | head -c 40
# expect HTML, not the error string
```

⚠️ **Do not probe `http://localhost/` with a `Host:` header** — Apache serves the `000-default` vhost regardless and returns `/var/www/html/index.html` (10671 bytes), which looks healthy on a
completely dead portal. This produced a wrong "no impact" conclusion during the 2026-07-28 incident. Always curl the real ServerName.

**Fix**:
```bash
ansible -i inventories/<flavor>/prod <hosts> -m file \
  -a "path=/var/www/html/wifi/application/cache state=directory recurse=yes owner=root group=root mode=0777"
# repeat for .../application/logs
```

**Incident**: 2026-07-21 → 07-28, 10 of 16 in-scope `rcp` sites fully down for 7 days. Root cause was an Ansible tag gap, not drift — see `08_ansible-authoring.md` and rule-005 in the ansible-wifi
repo. Undetected because the Kohana usage/status crons run as **root**, for whom a 0755 root-owned dir is writable, so they kept succeeding and Eclipse kept receiving data throughout. Full RCA:
`local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md`.

### 11.9 APN vs NBN Accelerate portal protocol differences (2026-08-03, code-inspection only — not live-validated)

Everything in §11.1–11.8 above was extracted from APN-cluster (`rcp`) incidents and live hosts. Two group_vars-level differences apply on the NBN Accelerate cluster (`nbn_accelerate`/`nbn_wh`) that
are **not yet confirmed against a live cw-cluster host**:

| Var                              | APN cluster (`rcp`/`rct`/`wh`)  | NBN Accelerate cluster (`nbn_accelerate`/`nbn_wh`) |
| -------------------------------- | ------------------------------- | -------------------------------------------------- |
| `smc_bases_portal_protocol`      | `http`                          | `https` — cw-side portals are HTTPS-only           |
| `smc_bases_blocked_url_redirect` | `activ8me.net.au/blocked/wifi/` | `blocked.communitywifi.net.au`                     |

Implications worth checking before assuming §11.1–11.8 troubleshooting steps transfer directly to a cw-cluster host:
- The `curl` verification commands in §11.7 (`curl -s wifi.a8me.au | grep ...`) use APN-cluster hostnames/base-hrefs (`p.a8me.au`/`wifi.a8me.au`, §11.3) — a cw-cluster host's equivalent hostname and
  expected base href are not documented anywhere in this pack yet.
- HTTPS termination on the cw side means an Apache vhost/TLS-cert config exists that has no APN-side equivalent to reference — not yet located or documented.
- The 0755-vs-0777 cache/logs permissions bug (§11.8) is Kohana-framework-level and independent of transport protocol, so it plausibly applies identically on cw-cluster hosts, but this is inferred,
  not confirmed live.

See `01_overview.md` "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" for the source of these two var values, and `13_known-issues.md` "NBN Accelerate cluster coverage gap" for the
broader live-validation gap this note is part of.

### 11.10 What the portal keeps on the box (2026-10-21, repo and live)

Asked by smc-resiliency: can a rebuild of the writable area lose `/var/www/html/wifi`? Read-only on two rct boxes, 2026-10-21 17:24 AEDT:
`black-craggy-smc01` and `paradise-farm-smc01` (portal commit `c11c230`, overlayroot mounted on both). Repo: ansible-wifi `c0ea35ec`.

**Answer: the portal holds no local data of its own. Everything is pulled again from Eclipse within 5 minutes, and on an overlayroot rct box it is
already lost at every reboot.**

| Store | Live (both boxes) | Source | Lost at a rebuild |
| --- | --- | --- | --- |
| Code tree | 7.1 MB, `git status`: only the four paths below differ | wifi.git `wifi_git.commit` | Nothing, if the image ships it |
| `config/site.txt` | modified vs git | `eclipse_siteid` (Ansible) | Identity: must be rewritten, or portal and Teleport `id` label break |
| `config/config.txt` | 1,849 and 2,650 bytes, rewritten 17:20 (untracked) | Eclipse reply to `status:update:status` | Rewritten within 5 min; until then `site_config()` falls back to defaults |
| `config/sites/<id>/` | 244 files, all dated 2025-08-15 (clone date) | Tracked in wifi.git | Nothing |
| `application/cache`, `application/logs` | empty (only `.gitignore`, mode 0777) | none | Nothing; must exist at 0777 (§11.8) |
| SQLite / MySQL | none; no `/var/lib/mysql`, mariadb inactive | none | Nothing |
| `ECLIPSE_MARK` (iptables, not disk) | 0 and 1 rules | Eclipse `fetch_clients_by_classes` | Re-added at the next 5-min status run |

Commands: `ls`, `find`, `stat`, `du`, `git status` and `grep`/`sed` of the PHP, over `tsh ssh` with a TERM/KILL deadline watcher; from data files only the
JSON key names of `config.txt` were printed.

**How sessions come back** (on-box code, `application/command/status.php` and `classes/model/wifi/config.php`): `status:update:status` posts status to
Eclipse, stores the reply as `config.txt`, then `enforce_config()` calls `confirm_clients()`, which fetches the site's active PINs from Eclipse and adds an
`ECLIPSE_MARK` rule for each one missing locally. `status:clean:up` (daily) flushes the chain and rebuilds it from Eclipse the same way.

```php
// application/command/status.php (update_status), portal c11c230
if (is_object($response) && !empty($response)) {
    file_put_contents('application/config/config.txt',json_encode($response));
} else { syslog(LOG_NOTICE,"WiFi: Invalid Config Download"); }   // keeps the last one
$config = Model::factory('WiFi_Config');
$config->enforce_config();                                          // -> confirm_clients()
// classes/model/wifi/config.php confirm_clients()
$current_clients = $iptables->authorised_clients_byclass();
$clients = Model::factory('WIFI_API')->fetch_clients_by_classes($site);
foreach ($clients as $client) foreach ($client as $mac => $class)
    if (!isset($current_clients[$class])) { $iptables->deauthorise_client($mac,$class); $iptables->authorise_client($mac,$class); }
```

`status:update:usage` (every minute, `smc_bases_usage_cron` is 1 in all five flavours) reads the iptables byte counters and posts usage to
Eclipse. It writes nothing to disk; usage counted since the last post (at most 1 min) is lost when the counters reset.

**No local database is deployed for the portal.** The MariaDB import in `smc_application` is commented out. It was for `mobile_app`/`community_connect`
(nbn_accelerate, see `14_pin-activation-diagnosis.md` §14.6), not Kohana:

```yaml
# roles/smc_application/tasks/ubuntu-apache-install-configure.yml:110
# - name: Install and configure mariadb on Ubuntu
#   import_tasks: ubuntu-mariadb-install-configure.yml
```

The disk-write audit's "DB + cache writes every 1min; operational" row (smc-file-writing-analysis `docs/smc-audit-data.csv` row 31) came from
`malik-rct01`, the Vagrant lab VM, on 2026-04-20. Production boxes show no such database or cache.

Effect of a rebuild: a guest who is online keeps their PIN (held in Eclipse) and is re-marked within 5 minutes. If Eclipse cannot be reached after the
rebuild, there is no `config.txt`, so portal settings run on defaults and the chain stays empty until Eclipse answers. On overlayroot boxes the same is
already true after every reboot, because `config.txt` lives in the tmpfs upper layer.

## PHP security status: CVE-2026-109618 / CVE-2026-109619 (2026-10-22)

php.net's 2026-10-21 advisory covers two unauthenticated RCEs and rates Apache mod_php the highest-risk setup, which is what every SMC runs. Ubuntu 22.04's fix is `php8.1 8.1.2-1ubuntu2.28` (USN-8948-1). `php -v` prints `8.1.2` on every box, patched or not, so compare the package version (`dpkg-query -W libapache2-mod-php8.1`). On 2026-10-22 no reachable SMC had the fix, and builds differ even on the Pis: `.13`, `.14`, `.18`, `.19`, `.20`, `.21` and `.24` were all seen. No SMC has `php*-fpm` or `php*-cgi`. The rcp boxes held stale apt lists (newest candidate `.26`), so they need `apt-get update` first. On rct/wh the upgrade must reach the lower root, or a reboot drops it (`07_hardware-overlay.md`). The non-SMC servers (cnMaestro, Graylog, Jenkins, Prometheus, Teleport) have no PHP. Fleet CSV, report and probe scripts: `local-knowledge-ansible/ansible-wifi/evidence/php-cve-2026-109618-20261022_1128/`. Re-run it with `scripts/probes/php_package_probe.sh` (`just php_package_probe`). Probe logic (`raw/php_probe.sh`):

```bash
v=$(php -r 'echo PHP_VERSION;' 2>/dev/null || echo none)
m=$(dpkg-query -W -f='${Package}=${Version}\n' 'libapache2-mod-php*' 2>/dev/null | grep -v '=$' | tr '\n' ' ')
c=$(apt-cache policy php8.1-common 2>/dev/null | awk '/Candidate/{print $2}')
```

Backdoor pitfall found the same day: port 50501 (`family-friendly-smc01`'s backdoor) answered as `nocprov-smc01`, a box in no inventory. Check `hostname` before attributing a backdoor session to a site.

**Other PHP processes to restart after a PHP upgrade (survey 2026-10-22).** Restarting apache2 is not enough on every flavor:

- **rct:** `php -S 10.254.0.1:8080`, PHP's built-in web server for rct-tstik (`/var/www/html/rct-tstik/public`), runs as root, started by a cron entry every 5 minutes. It is a second PHP web server beside Apache; INPUT accepts 8080 on `bridge_500` and the policy is ACCEPT. Source, `roles/smc_application/tasks/main.yml` (branch `rise`, 0979a596):

```yaml
        - name: Tstik PHP Built-In Web Server
          minute: "*/5"
          job: "cd /var/www/html/rct-tstik/public && nohup php -S 10.254.0.1:8080 &>/dev/null"
          state: present
      ...
      when: hotspot_flavor == 'rct'
```

- **rcp, nbn_accelerate, nbn_wh:** `apn-mqtt-client` (`cd /var/www/apn-mqtt-client && php Start.php`, root, cron `*/5`, crontab tag `#Ansible: apn-mqtt-client`, not defined in ansible-wifi roles). No listening port.
- `pkill` either one after the upgrade; cron starts it again within 5 minutes on the new build. `kohana` / `php artisan` cron jobs are short-lived.
- `dpkg-query -W 'php8.1-*'` lists about 20 known-but-not-installed packages; filter on `${db:Status-Abbrev}` = `ii` before passing the list to `apt-get install`.
- No SMC holds any PHP or Apache package, and unattended-upgrades is disabled (masked on rcp), so no box patches itself.
