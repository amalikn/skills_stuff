---
Title: OpenWISP RADIUS, captive portal and Wi-Fi sessions
Category: skill-reference
Status: current
Authority: Installed OpenWISP images 26.09.0 (openwisp-radius 1.3, openwisp-monitoring 1.3) source and the versioned 26.09 documentation; the cited lines win over this summary
Scope: openwisp-radius with FreeRADIUS, organisation RADIUS settings, users and groups, registration, captive portal integration, accounting, and monitoring Wi-Fi sessions
Last reviewed: 2026-10-05
Summary: How a public Wi-Fi sign-up and terms-acceptance flow maps onto openwisp-radius and FreeRADIUS, what this install has switched on, and what monitoring's Wi-Fi sessions do and do not record.
---

# OpenWISP RADIUS, captive portal and Wi-Fi sessions

Verified against: OpenWISP images 26.09.0 (openwisp-radius 1.3, openwisp-monitoring 1.3, django-sendsms 0.5, django-allauth 65.19.2), checked 2026-10-05.

Module status in the checked install:

| Piece                                      | Installed | Enabled | Evidence                                                                                      |
| ------------------------------------------ | --------- | ------- | --------------------------------------------------------------------------------------------- |
| `openwisp_radius` (API, admin, models)     | Yes       | Yes     | `USE_OPENWISP_RADIUS=True`; in `INSTALLED_APPS`; URLs resolve                                 |
| FreeRADIUS server                          | No        | No      | No `openwisp-freeradius` container in the stack                                               |
| SMS verification                           | Yes       | No      | `OPENWISP_RADIUS_SMS_VERIFICATION_ENABLED` False; `SENDSMS_BACKEND` unset (in-memory backend) |
| Social login (allauth Facebook, Google)    | Yes       | No      | Providers in `INSTALLED_APPS`; `OPENWISP_RADIUS_SOCIAL_REGISTRATION_ENABLED` False            |
| SAML login                                 | No        | No      | `import djangosaml2` fails: `ModuleNotFoundError`                                             |
| RADIUS metrics (`integrations.monitoring`) | Yes       | No      | Not in `INSTALLED_APPS`                                                                       |
| Monitoring Wi-Fi sessions                  | Yes       | Yes     | `OPENWISP_MONITORING_WIFI_SESSIONS_ENABLED` default True                                      |

Citations name the installed file as `$P/<module>/<file>:<line>`, where `$P` is `/usr/local/lib/python3.14/site-packages` in `openwisp-dashboard:26.09.0`. FreeRADIUS itself is not installed here: its
configuration below comes from the 26.09 deploy guide and is marked as such. Anything else not read from source or a versioned page is UNVERIFIED.

## Summary

| Job                          | Use                                | Key syntax                                        | Trap                                                               | Section |
| ---------------------------- | ---------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------ | ------- |
| See the moving parts         | NAS, FreeRADIUS, openwisp-radius   | `/api/v1/freeradius/\`                            | FreeRADIUS hosts must be in the allowed list or every call is 403  | [1](#1-architecture-and-the-request-path) |
|                              |                                    |   `{authorize,postauth,accounting}/`              |                                                                    |         |
| Point FreeRADIUS at OpenWISP | `rlm_rest`                         | `mods-enabled/rest`, `sites-enabled/default`      | Bearer method needs one site per organisation                      | [2](#2-freeradius-configuration) |
| Per-organisation behaviour   | Organization RADIUS settings       | `token`, `registration_enabled`,                  | Fields fall back to the global setting when left at default        | [3](#3-organisation-radius-settings) |
|                              |                                    |   `sms_verification`, `login_url`                 |                                                                    |         |
| Limit sessions               | RADIUS groups and counters         | `Max-Daily-Session`, `Max-Daily-Session-Traffic`  | Default group `users` caps 3 h and 300 MB a day                    | [4](#4-users-groups-and-limits) |
| Self sign-up and terms       | Registration REST API + login      | `POST /api/v1/radius/organization/<slug>/\`       | The API has no terms field; terms live in the login-pages          | [5](#5-registration-and-verification) |
|                              |   pages app                        |   `account/`                                      |   front end                                                        |         |
| Log a user into the portal   | Radius user token                  | `.../account/token/` then POST to the NAS with    | Disposable by default: one token, one login                        | [6](#6-captive-portal-login-flow) |
|                              |                                    |   the token as password                           |                                                                    |         |
| Count sessions and usage     | RadiusAccounting                   | `/api/v1/radius/sessions/`,                       | Retention is a beat task: `CRON_DELETE_OLD_RADACCT` days           | [7](#7-accounting-and-sessions) |
|                              |                                    |   `.../account/session/`                          |                                                                    |         |
| Report Wi-Fi clients         | Monitoring WifiSession, WifiClient | `/api/v1/monitoring/wifi-session/`                | Built only from pushed `wireless.clients`; no beat cleanup         | [8](#8-wi-fi-sessions-from-monitoring) |
|   without RADIUS             |                                    |                                                   |   in docker                                                        |         |

## Contents

- [Summary](#summary)
- [1. Architecture and the request path](#1-architecture-and-the-request-path)
- [2. FreeRADIUS configuration](#2-freeradius-configuration)
- [3. Organisation RADIUS settings](#3-organisation-radius-settings)
- [4. Users, groups and limits](#4-users-groups-and-limits)
- [5. Registration and verification](#5-registration-and-verification)
- [6. Captive portal login flow](#6-captive-portal-login-flow)
- [7. Accounting and sessions](#7-accounting-and-sessions)
- [8. Wi-Fi sessions from monitoring](#8-wi-fi-sessions-from-monitoring)

## 1. Architecture and the request path

Decision: OpenWISP is the user store and policy engine; FreeRADIUS is a thin RADIUS-to-REST bridge; the NAS (captive portal gateway) talks only RADIUS.

```text
client browser -> captive portal (NAS: coova-chilli, pfSense, other) -> RADIUS -> FreeRADIUS (rlm_rest)
  -> HTTPS -> /api/v1/freeradius/authorize/   -> control:Auth-Type Accept|Reject + reply attributes
  -> HTTPS -> /api/v1/freeradius/postauth/
  -> HTTPS -> /api/v1/freeradius/accounting/  (Start, Interim-Update, Stop)
sign-up page (e.g. OpenWISP WiFi Login Pages) -> /api/v1/radius/organization/<slug>/account/...
```

FreeRADIUS endpoints authenticate in one of three ways (`FreeradiusApiAuthentication`):

| Method            | How the organisation is identified                                     | When                                        |
| ----------------- | ---------------------------------------------------------------------- | ------------------------------------------- |
| Radius user token | The password is a token the user obtained from the login API           | Several organisations behind one FreeRADIUS |
| Bearer            | `Authorization: Bearer <org-uuid> <org-radius-token>` on every request | One organisation per FreeRADIUS site        |
| Query string      | `?uuid=<org-uuid>&token=<org-radius-token>`                            | Testing only; tokens land in web logs       |

- Every method finally checks the client IP against the organisation's `freeradius_allowed_hosts` or the global `OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS` (set from the env var in docker).
- Reject answers 401 `{"control:Auth-Type": "Reject"}`; a quota reject answers 200 with `Reply-Message`, because some NAS treat other codes as bad credentials.
- With `OPENWISP_RADIUS_API_AUTHORIZE_REJECT` False (default) an unknown user gets `200` and no body, leaving the reject to FreeRADIUS.

Gotcha: a request body must never carry `organization`; the authentication class rejects it.

Source: `$P/openwisp_radius/api/freeradius_views.py:87-234` (authentication), `:236-290` (authorize); `$P/openwisp_radius/api/urls.py` (paths); `$P/openwisp_radius/settings.py:45`, `:64`;
`/opt/openwisp/openwisp/settings.py` (`OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS` from env); https://openwisp.io/docs/26.09/radius/user/rest-api.html (snapshot
`documents/openwisp-26.09-radius-rest-api.html`).

## 2. FreeRADIUS configuration

Decision: install FreeRADIUS 3 with `freeradius-rest`, point `rlm_rest` at the three endpoints, and add the server's address to the allowed hosts. From the 26.09 deploy guide; not installed here.

```sh
apt install freeradius freeradius-rest
ln -s /etc/freeradius/mods-available/rest /etc/freeradius/mods-enabled/rest
```

```text
# /etc/freeradius/mods-enabled/rest
connect_uri = "https://openwisp.example"
authorize {
    uri = "${..connect_uri}/api/v1/freeradius/authorize/"
    method = 'post'
    body = 'json'
    data = '{"username": "%{User-Name}", "password": "%{User-Password}", "called_station_id": "%{Called-Station-ID}", "calling_station_id": "%{Calling-Station-ID}"}'
    tls = ${..tls}
}
authenticate {}
post-auth {
    uri = "${..connect_uri}/api/v1/freeradius/postauth/"
    method = 'post'
    body = 'json'
    data = '{"username": "%{User-Name}", "password": "%{User-Password}", "reply": "%{reply:Packet-Type}", "called_station_id": "%{Called-Station-ID}", "calling_station_id": "%{Calling-Station-ID}"}'
    tls = ${..tls}
}
accounting {
    uri = "${..connect_uri}/api/v1/freeradius/accounting/"
    method = 'post'
    body = 'json'
    data = '{"status_type": "%{Acct-Status-Type}", "session_id": "%{Acct-Session-Id}", "unique_id": "%{Acct-Unique-Session-Id}", "username": "%{User-Name}", "realm": "%{Realm}", "nas_ip_address": "%{NAS-IP-Address}", "nas_port_id": "%{NAS-Port}", "nas_port_type": "%{NAS-Port-Type}", "session_time": "%{Acct-Session-Time}", "authentication": "%{Acct-Authentic}", "input_octets": "%{Acct-Input-Octets}", "output_octets": "%{Acct-Output-Octets}", "called_station_id": "%{Called-Station-Id}", "calling_station_id": "%{Calling-Station-Id}", "terminate_cause": "%{Acct-Terminate-Cause}", "service_type": "%{Service-Type}", "framed_protocol": "%{Framed-Protocol}", "framed_ip_address": "%{Framed-IP-Address}"}'
    tls = ${..tls}
}
```

```text
# /etc/freeradius/sites-enabled/default (Bearer method: uncomment the header lines, one site per organisation)
server default {
    # api_token_header = "Authorization: Bearer <org_uuid> <org_radius_api_token>"
    authorize {
        # update control { &REST-HTTP-Header += "${...api_token_header}" }
        rest
    }
    authenticate {}
    post-auth {
        rest
        Post-Auth-Type REJECT { rest }
    }
    accounting { rest }
}
preacct { acct_unique }
```

```sh
freeradius -X                                           # debug in the foreground
radtest <username> <password> 127.0.0.1 10 <radius-shared-secret>
```

- `acct_unique` must be in `preacct` so `unique_id` is filled.
- docker-openwisp ships an `openwisp-freeradius` image (`MODULE_NAME=freeradius`, `FREERADIUS_DEBUG_MODE`); custom raddb files are mounted per the customisation page.

Gotcha: the rest module sends the cleartext password to OpenWISP; keep `connect_uri` on HTTPS with `tls` configured, or place FreeRADIUS beside the API on a private network.

Source: https://openwisp.io/docs/26.09/radius/deploy/freeradius.html (snapshot `documents/openwisp-26.09-radius-freeradius.html`); `/opt/openwisp/init_command.sh` (freeradius branch);
https://openwisp.io/docs/26.09/docker/user/customization.html. Not executed: no FreeRADIUS in this install (UNVERIFIED end to end).

## 3. Organisation RADIUS settings

Decision: set per-organisation behaviour on its Organization RADIUS settings, and leave a field at its fallback to inherit the global Django setting.

| Field                                                                      | Purpose                                                         | Global fallback                                       |
| -------------------------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------------- |
| `token`                                                                    | Organisation RADIUS API token (Bearer and query-string methods) | none                                                  |
| `registration_enabled`                                                     | Allow self sign-up through the API                              | `OPENWISP_RADIUS_REGISTRATION_API_ENABLED` (True)     |
| `sms_verification`, `sms_sender`, `sms_message`, `sms_cooldown`            | Phone verification by SMS                                       | `OPENWISP_RADIUS_SMS_VERIFICATION_ENABLED` (False)    |
| `needs_identity_verification`                                              | Require a verified method before login                          | `OPENWISP_RADIUS_NEEDS_IDENTITY_VERIFICATION` (False) |
| `social_registration_enabled`,                                             | Alternative sign-up and roaming                                 | matching `OPENWISP_RADIUS_*_ENABLED` (False)          |
|   `saml_registration_enabled`, `mac_addr_roaming_enabled`                  |                                                                 |                                                       |
| `first_name`, `last_name`, `location`, `birth_date`                        | Optional registration fields: disabled, allowed or mandatory    | `OPENWISP_RADIUS_OPTIONAL_REGISTRATION_FIELDS`        |
| `freeradius_allowed_hosts`, `coa_enabled`, `allowed_mobile_prefixes`       | Network and phone policy                                        | matching global settings                              |
| `login_url`, `status_url`, `password_reset_url`                            | Links used by e-mails and the login pages                       | `password_reset_url` has a global default             |

Gotcha: the Fallback fields make an organisation's effective value depend on a Django setting nobody sees in the admin row; read both before concluding a feature is on or off.

Source: `$P/openwisp_radius/base/models.py` (`AbstractOrganizationRadiusSettings` fields); `$P/openwisp_radius/settings.py:28-113`; https://openwisp.io/docs/26.09/radius/user/settings.html.

## 4. Users, groups and limits

Decision: model service tiers as RADIUS groups with check attributes; let openwisp-radius counters enforce them inside `authorize`, not FreeRADIUS `sqlcounter`.

| Counter (PostgreSQL)                                             | Check attribute               | Reply attribute                |
| ---------------------------------------------------------------- | ----------------------------- | ------------------------------ |
| `openwisp_radius.counters.postgresql.daily_counter.DailyCounter` | `Max-Daily-Session`           | `Session-Timeout`              |
| `...daily_traffic_counter.DailyTrafficCounter`                   | `Max-Daily-Session-Traffic`   | `CoovaChilli-Max-Total-Octets` |
| `...monthly_traffic_counter.MonthlyTrafficCounter`               | `Max-Monthly-Session-Traffic` | `CoovaChilli-Max-Total-Octets` |

- Groups created by the initial migrations: `users` (default; 3 hours and 300 MB daily) and `power-users` (no checks). The default group is assigned to new users and cannot be deleted.
- REST: `/api/v1/radius/group/`, `/api/v1/users/user/<user_pk>/radius-group/`.
- Bulk users: a RadiusBatch with `strategy` `csv` (file in private storage) or `prefix` (`[prefix][number]`); PDFs at `/api/v1/radius/organization/<slug>/batch/<pk>/pdf/`.
- Change the traffic reply attribute with `OPENWISP_RADIUS_TRAFFIC_COUNTER_REPLY_NAME` when the NAS is not CoovaChilli.

Gotcha: counters live in the authorize endpoint, so they apply only at login; an open session over its limit is cut by the NAS honouring the reply attribute, or by CoA when `coa_enabled`.

Source: `$P/openwisp_radius/settings.py:177-195`; `$P/openwisp_radius/counters/base.py:151-183`; `$P/openwisp_radius/base/models.py:954-996` (batch); `$P/openwisp_radius/api/urls.py`;
https://openwisp.io/docs/26.09/radius/user/enforcing_limits.html.

## 5. Registration and verification

Decision: let users self-register through the organisation's registration endpoint; collect terms acceptance in the front end, which owns that step.

```bash
R="$OW/api/v1/radius/organization/<org-slug>/account"
curl -s -X POST "$R/" -H "Content-Type: application/json" \
  -d '{"username": "user01", "email": "user01@example.org", "password1": "<pw>", "password2": "<pw>", "method": ""}'
```

- Parameters: `username`, `email`, `password1`, `password2`, `phone_number` (required only with SMS verification), optional `first_name`, `last_name`, `birth_date`, `location`, and `method`.
- `method` values in the installed registry: `""`, `manual`, `email`, `mobile_phone`, `pending_verification`, plus `social_login` registered by the app; SAML would add `saml` but is not installed.
- An existing user registering on another organisation gets `409` with the organisations already joined.
- SMS flow (user Bearer key): `POST $R/phone/token/`, `GET $R/phone/token/active/`, `POST $R/phone/verify/` with `code`; limits `OPENWISP_RADIUS_SMS_TOKEN_MAX_ATTEMPTS` 5, `..._MAX_USER_DAILY` 5,
  `..._MAX_IP_DAILY` 999, cooldown 30 s.

Gotcha: in this install `SENDSMS_BACKEND` is unset, so django-sendsms uses `sendsms.backends.locmem.SmsBackend`: an SMS "sent" never leaves the process. Configure a real backend before enabling SMS
verification.

Source: `$P/openwisp_radius/registration.py:8-60`; `$P/openwisp_radius/apps.py:61`; `$P/openwisp_radius/api/serializers.py:634` (`RegisterSerializer`); `$P/openwisp_radius/settings.py:83-104`;
`$P/sendsms/api.py:71`; https://openwisp.io/docs/26.09/radius/user/rest-api.html; https://openwisp.io/docs/26.09/wifi-login-pages/user/intro.html ("Configurable Terms of Services and Privacy Policy
for each organization").

## 6. Captive portal login flow

Decision: use the radius user token method so one FreeRADIUS site serves every organisation.

```bash
# 1. the login page obtains a token for the user
curl -s -X POST "$R/token/" -d "username=user01" -d "password=<pw>"
#    -> {"radius_user_token": "...", "key": "...", "is_active": true, "is_verified": false, "method": "", ...}
# 2. the page posts to the NAS login URL with the radius user token as the password (NAS-specific form)
curl -s -X POST "https://captive.example/login" -d "auth_user=user01&auth_pass=<radius-user-token>"
# 3. later calls by the page use the API key
curl -s "$R/session/" -H "Authorization: Bearer <user-key>"
curl -s -X POST "$R/token/validate/" -d "token=<user-key>"
```

- `token/` answers `401` with the same body for an inactive or unverified user, so the page can branch to verification.
- `OPENWISP_RADIUS_DISPOSABLE_RADIUS_USER_TOKEN` (True) makes the token single-use; False keeps it valid until an accounting Stop.
- One account can be logged into one organisation at a time with this method.
- MAC-address roaming (`mac_addr_roaming_enabled`) re-authorises a known device by its Calling-Station-Id while it has an open session.

Gotcha: the NAS form fields (`auth_user`, `auth_pass` above) are the NAS's own; the 26.09 docs show a pfSense-style example. Check your NAS's external-portal contract (UNVERIFIED for any specific
NAS).

Source: `$P/openwisp_radius/settings.py:52`, `:62`; `$P/openwisp_radius/api/freeradius_views.py:150-197`; https://openwisp.io/docs/26.09/radius/user/rest-api.html.

## 7. Accounting and sessions

Decision: read sessions from RadiusAccounting; keep retention aligned with any legal record-keeping duty before trusting the defaults.

```bash
curl -s "$OW/api/v1/radius/sessions/?page_size=100" -H "Authorization: Bearer $OW_TOKEN"     # admin view, org-scoped
```

- RadiusAccounting fields include `session_id`, `unique_id`, `username`, `groupname`, `realm`, `nas_ip_address`, `nas_port_id`, `nas_port_type`, `start_time`, `update_time`, `stop_time`, `interval`,
  `session_time`, `input_octets`, `output_octets`, `called_station_id`, `calling_station_id`, `terminate_cause`.
- Retention in docker (beat task `radius-periodic-tasks`, daily at 03:30): `delete_old_radacct`, `delete_old_postauth`, `cleanup_stale_radacct`, `delete_old_radiusbatch_users`, each taking the day
  count from `CRON_DELETE_OLD_RADACCT`, `CRON_DELETE_OLD_POSTAUTH`, `CRON_CLEANUP_STALE_RADACCT`, `CRON_DELETE_OLD_RADIUSBATCH_USERS` (365 each here).
- RADIUS charts (registrations, unique sessions, traffic) need `openwisp_radius.integrations.monitoring` in `INSTALLED_APPS` plus its beat entry; not enabled here.

Gotcha: `OPENWISP_RADIUS_API_ACCOUNTING_AUTO_GROUP` (True) stamps `groupname` from the user's group; a later group change does not rewrite past rows.

Source: `$P/openwisp_radius/base/models.py:354-430`; `$P/openwisp_radius/api/freeradius_views.py:471-560`; `$P/openwisp_radius/settings.py:63`; `/opt/openwisp/celery.py` (`radius_schedule`);
`/opt/openwisp/openwisp/tasks.py:9-23`; https://openwisp.io/docs/26.09/radius/user/radius_monitoring.html.

## 8. Wi-Fi sessions from monitoring

Decision: use monitoring's WifiSession for "who was associated where" reporting when there is no RADIUS, and RadiusAccounting when there is; they are different facts.

```bash
curl -s "$OW/api/v1/monitoring/wifi-session/?device__organization=<org-uuid>&stop_time__isnull=true" -H "Authorization: Bearer $OW_TOKEN"
curl -s "$OW/api/v1/monitoring/wifi-session/?start_time__gte=2026-10-01T00:00:00Z&device__group=<group-uuid>" -H "Authorization: Bearer $OW_TOKEN"
```

- Built by `save_wifi_clients_and_sessions` from each DeviceMonitoring push: only `interfaces[]` with `type: wireless` and `wireless.mode: access_point`; each `wireless.clients[]` entry keyed by
  `mac`.
- WifiClient keeps `mac_address`, `vendor`, `ht`, `vht`, `he`, `wmm`, `wds`, `wps`; WifiSession keeps `device`, `wifi_client`, `ssid`, `interface_name`, `start_time`, `stop_time`.
- Filters: `device__organization`, `device`, `device__group`, `start_time` and `stop_time` with `gt/gte/lt/lte` (`stop_time__isnull` for open sessions).
- Disable with `OPENWISP_MONITORING_WIFI_SESSIONS_ENABLED = False`.

Gotcha: the 26.09 page says docker-openwisp pre-configures `delete_wifi_clients_and_sessions`, but the installed `/opt/openwisp/celery.py` beat schedule has no such entry and `CELERY_BEAT_SCHEDULE` is
unset, so sessions grow without limit here. A device that pushes no client list (closed firmware through a shim) creates no sessions at all.

Source: `$P/openwisp_monitoring/device/base/models.py:284-330`, `:538-602`; `$P/openwisp_monitoring/device/settings.py:64`; `$P/openwisp_monitoring/device/api/urls.py:40-47`;
`$P/openwisp_monitoring/device/api/filters.py:19-31`; `/opt/openwisp/celery.py`; https://openwisp.io/docs/26.09/monitoring/user/wifi-sessions.html (snapshot
`documents/openwisp-26.09-monitoring-wifi-sessions.html`).

> **Learned 2026-10-05** · OpenWISP monitoring 1.3 (images 26.09.0) · VERIFIED_PRIMARY · Source: /opt/openwisp/openwisp/celery.py in the 26.09.0 image has no Wi-Fi session clean-up entry in its beat schedule · Falsifier: a beat entry that deletes old WifiSession rows in a 26.09.x image
> The 26.09 docs say docker-openwisp schedules the clean-up of old Wi-Fi sessions, but the installed beat schedule has no such task, so sessions accumulate. Add a scheduled clean-up through the custom settings, or accept the growth knowingly.
