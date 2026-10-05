---
Title: Nautobot operations and recovery
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source, its bundled documentation, and the PostgreSQL 16 client tools; the cited lines win over this summary
Scope: >-
  Backing up and restoring the Nautobot database and file stores, restore rehearsal, health checks, Prometheus metrics, logging, performance, security
  settings, authentication backends, tokens, and Celery worker and scheduler inspection
Last reviewed: 2026-10-05
Summary: Nine verified operations recipes for running and recovering Nautobot 3.2.3, each with a gotcha and a source line; restore ordering is labelled as practice where Nautobot documents none.
---

# Nautobot operations and recovery

Verified against: Nautobot 3.2.3 (installed source and bundled docs), `django-health-check` 3.20.8, `django-prometheus` 2.5.0, Celery 5.6.3, PostgreSQL 16.15 client tools, checked 2026-10-05.

Source paths are relative to `site-packages/`; `docs/...` is the page under `nautobot/project-static/docs/`. Commands run inside the Nautobot or database container (`docker exec <container> ...`) or
the Nautobot venv. Placeholders: `https://nautobot.example`, `$NAUTOBOT_TOKEN`, `$NAUTOBOT_DB_NAME`.

## Summary

| Job                   | Use                              | Key syntax                              | Trap                                                               | Section |
| --------------------- | -------------------------------- | --------------------------------------- | ------------------------------------------------------------------ | ------- |
| Back up               | `pg_dump -Fc` + file stores      | `pg_dump -Fc -f nautobot.dump`          | `dumpdata` is a migration tool, not a backup                       | [1](#1-backup) |
| Restore               | `pg_restore` into an empty DB    | `pg_restore --no-owner -d ...`          | same Nautobot and app versions first                               | [2](#2-restore-and-rehearsal) |
| Is it up              | `/health/`, `health_check`       | `curl .../health/?format=json`          | HTTP check and CLI check differ                                    | [3](#3-health-checks) |
| Metrics               | `METRICS_ENABLED`                | `/metrics/`                             | guide says `METRICS_AUTHENTICATION`; it is `METRICS_AUTHENTICATED` | [4](#4-prometheus-metrics) |
| Logs                  | `LOGGING` dict                   | `"nautobot"` logger                     | worker stdout is captured at WARNING                               | [5](#5-logging) |
| Slow pages or Jobs    | depth, page size, ORM hints      | `select_related`, `prefetch_related`    | N+1 in Jobs is invisible until scale                               | [6](#6-performance) |
| Lock it down          | core security settings           | `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | `EXEMPT_VIEW_PERMISSIONS` opens to anonymous                       | [7](#7-security-settings) |
| Sign-in and tokens    | SSO, LDAP, Token                 | `AUTHENTICATION_BACKENDS`               | `ObjectPermissionBackend` must stay                                | [8](#8-authentication-and-tokens) |
| Workers and scheduler | `nautobot-server celery inspect` | `inspect ping --destination ...`        | no reply is not proof of no worker                                 | [9](#9-workers-and-scheduler) |

## Contents

- [Summary](#summary)
- [1. Backup](#1-backup)
- [2. Restore and rehearsal](#2-restore-and-rehearsal)
- [3. Health checks](#3-health-checks)
- [4. Prometheus metrics](#4-prometheus-metrics)
- [5. Logging](#5-logging)
- [6. Performance](#6-performance)
- [7. Security settings](#7-security-settings)
- [8. Authentication and tokens](#8-authentication-and-tokens)
- [9. Workers and scheduler](#9-workers-and-scheduler)

## 1. Backup

Decision: the database is the system of record; back it up with PostgreSQL's own tools. Then copy the file stores that live outside it.

```bash
# database: custom format, compressed, restorable selectively and in parallel
pg_dump -Fc -h "$DB_HOST" -U "$DB_USER" -d "$NAUTOBOT_DB_NAME" -f "nautobot-$(date +%Y%m%d_%H%M).dump"
pg_restore --list nautobot-*.dump > /dev/null && echo "dump readable"
# file stores (defaults under NAUTOBOT_ROOT, normally /opt/nautobot)
tar -czf nautobot-files-$(date +%Y%m%d_%H%M).tgz -C "$NAUTOBOT_ROOT" media jobs nautobot_config.py
```

| Store                     | Default                                      | Back up?                                                          |
| ------------------------- | -------------------------------------------- | ----------------------------------------------------------------- |
| PostgreSQL database       | `NAUTOBOT_DB_NAME` (`nautobot`)              | yes: all objects, change log, Job results, Job input/output files |
| `MEDIA_ROOT`              | `$NAUTOBOT_ROOT/media`                       | yes: image attachments and other uploads (`FileSystemStorage`)    |
| `JOBS_ROOT`               | `$NAUTOBOT_ROOT/jobs` (`NAUTOBOT_JOBS_ROOT`) | yes, unless the Jobs there are deployed from version control      |
| `GIT_ROOT`                | `$NAUTOBOT_ROOT/git` (`NAUTOBOT_GIT_ROOT`)   | optional: rebuilt by re-syncing each Git repository               |
| `STATIC_ROOT`             | `$NAUTOBOT_ROOT/static`                      | no: rebuilt by `collectstatic` (`post_upgrade` runs it)           |
| `nautobot_config.py`, env | config path                                  | yes, without secrets in clear text; keep `SECRET_KEY` with it     |
| Redis                     | cache and Celery broker                      | no: transient                                                     |

Gotcha: Job input and output files use `db_file_storage` (the `nautobotjobfiles` storage), so they are in the database dump, not in `MEDIA_ROOT`. `nautobot-server dumpdata` is documented for moving
between PostgreSQL and MySQL (with `--exclude auth.permission`, and warnings against `--natural-primary` and `--natural-foreign`); it is slow, large, and not a substitute for `pg_dump`. Nautobot's own
backup page only refers to the PostgreSQL and MySQL manuals.

Source: `nautobot/core/settings.py:54,137,150,307-321,618,771`; `docs/user-guide/administration/upgrading/database-backup.html`,
`docs/user-guide/administration/migration/migrating-from-postgresql.html`; `pg_dump --help`, `pg_restore --help` (PostgreSQL 16.15).

## 2. Restore and rehearsal

Decision: restore onto the same Nautobot version and the same app versions that wrote the dump, into an empty database, with web, worker and scheduler stopped. Rehearse on a scratch host on a
schedule; a backup never restored is unproven.

```bash
# 1. stop web, worker, scheduler; keep postgres and redis running
# 2. recreate an empty database owned by the Nautobot role
dropdb --if-exists "$NAUTOBOT_DB_NAME" && createdb -O "$DB_USER" "$NAUTOBOT_DB_NAME"
# 3. restore
pg_restore --no-owner --exit-on-error -j 4 -d "$NAUTOBOT_DB_NAME" nautobot-YYYYMMDD_hhmm.dump
# 4. file stores
tar -xzf nautobot-files-YYYYMMDD_hhmm.tgz -C "$NAUTOBOT_ROOT"
# 5. bring the schema to the running code and rebuild derived state
nautobot-server showmigrations | grep '\[ \]'      # anything unapplied?
nautobot-server post_upgrade                       # migrate, trace_paths, collectstatic, stale content types, caches
# 6. verify, then start web, worker, scheduler
nautobot-server validate_models
nautobot-server health_check
```

Rehearsal checks (practice, not a Nautobot procedure): object counts per key model match the source (`GET /api/dcim/devices/?limit=1` `count`); the latest change-log entry is the expected time; a Git
repository re-syncs; one read-only Job runs to `SUCCESS`; an API token from the source still authenticates.

Gotcha: restoring a dump from a newer Nautobot or app version into older code fails or leaves unknown tables; upgrade the code first. `pg_restore -1` (single transaction) cannot be combined with `-j`.
Scheduled Jobs resume as soon as the scheduler starts, so disable them on a rehearsal copy that can reach production devices.

Source: `nautobot/core/management/commands/post_upgrade.py:101-158`; `nautobot-server help` (lists `validate_models`, `health_check`, `showmigrations`); `pg_restore --help` and its refusal "cannot
specify both --single-transaction and multiple jobs" (PostgreSQL 16.15). The step order is UNVERIFIED as a Nautobot-documented procedure; it follows the commands' documented effects.

## 3. Health checks

Decision: probe each component separately: web over HTTP, the app's dependencies with the CLI, workers with Celery ping, beat with its heartbeat file.

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://nautobot.example/health/          # 200 healthy, 500 any check failed
curl -s "https://nautobot.example/health/?format=json"                            # per-check detail
nautobot-server health_check                                                       # exit 0 when healthy; -s/--subset to narrow
nautobot-server celery inspect ping --destination celery@$HOSTNAME                 # worker liveness
[ $(find "$NAUTOBOT_CELERY_BEAT_HEARTBEAT_FILE" -mmin -0.1 | wc -l) -eq 1 ] || false   # beat liveness
pg_isready; redis-cli ping
```

`/health/` passes when the server runs, reaches the database, has applied all migrations, reaches Redis, can write to storage, and is not too busy to answer. `health_check` checks the same
dependencies but not the web server. Worker file probes: set `CELERY_HEALTH_PROBES_AS_FILES = True` with `CELERY_WORKER_HEARTBEAT_FILE` and `CELERY_WORKER_READINESS_FILE`.

Gotcha: `/health/` returning 200 says nothing about workers; Jobs can sit `PENDING` with a healthy web tier. `redis-cli ping` can answer before Redis has loaded its data.

Source: `nautobot/core/urls.py:86`, `health_check/views.py:88-110`, `health_check/urls.py`, `nautobot/extras/health_checks.py:19-126`, `nautobot/core/settings.py:669-674,1083-1099`; `nautobot-server
help health_check`; `docs/user-guide/administration/guides/health-checks.html`.

## 4. Prometheus metrics

Decision: enable metrics on the web tier for request, database and cache figures; worker Job counters come from the worker processes.

```python
# nautobot_config.py (or env NAUTOBOT_METRICS_ENABLED / NAUTOBOT_METRICS_AUTHENTICATED)
METRICS_ENABLED = True
METRICS_AUTHENTICATED = True              # require login or API token on /metrics/
METRICS_DISABLED_APPS = []                # app names whose custom metrics to skip
CELERY_WORKER_PROMETHEUS_PORTS = [8080]   # worker metrics HTTP port; a range when several workers share a host
```

```bash
curl -s -H "Authorization: Token $NAUTOBOT_TOKEN" https://nautobot.example/metrics/ | grep -E '^nautobot_|^health_check_'
```

Nautobot-specific series: `health_check_database_info`, `health_check_redis_backend_info`, `nautobot_app_metrics_processing_ms` (web); `nautobot_worker_started_jobs`, `nautobot_worker_finished_jobs`,
`nautobot_worker_exception_jobs`, `nautobot_worker_singleton_conflict` (worker), plus django-prometheus request, model, database and cache series.

Gotcha: the setting is `METRICS_AUTHENTICATED` (settings reference and code); the Prometheus guide page names it `METRICS_AUTHENTICATION`, which does nothing. With the default settings file,
`METRICS_ENABLED` also swaps the database and cache backends to the `django_prometheus` ones; a custom `DATABASES` or `CACHES` must do that itself. Multi-process uWSGI needs `prometheus_multiproc_dir`
and cleanup of stale files.

Source: `nautobot/core/settings.py:176-181,516-518,1059-1063,1154`, `nautobot/core/urls.py:126-132`, `nautobot/core/views/__init__.py:731-767`;
`docs/user-guide/administration/configuration/settings.html` (METRICS_AUTHENTICATED), `docs/user-guide/administration/guides/prometheus-metrics.html`.

## 5. Logging

Decision: define `LOGGING` in `nautobot_config.py` as a standard Django dict; Nautobot's own loggers are under `nautobot`. Job logs are stored in the database per Job result and do not depend on this.

```python
LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "formatters": {"normal": {"format": "%(asctime)s %(levelname)-7s %(name)s: %(message)s"}},
    "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "normal"}},
    "loggers": {"django": {"handlers": ["console"], "level": "INFO"},
                "nautobot": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO"}},
}
# structured JSON logs:
# from nautobot.core.settings_funcs import setup_structlog_logging
# setup_structlog_logging(LOGGING, INSTALLED_APPS, MIDDLEWARE, log_level="INFO", debug_db=False, plain_format=False)
```

Gotcha: Celery redirects worker stdout and stderr into logging at `WARNING` (`CELERY_WORKER_REDIRECT_STDOUTS_LEVEL`), so `print()` in a Job shows as a warning in worker logs and not at all in the Job
result; use `self.logger`. `SANITIZER_PATTERNS` masks `username`/`password`/`secret` values in stored tracebacks, exception messages and the Job console log, not in ordinary `self.logger` lines.

Source: `nautobot/core/templates/nautobot_config.py.j2:140-190`, `nautobot/core/settings.py:297-302,1129-1133`, `nautobot/core/celery/backends.py:57,92`, `nautobot/extras/jobs_console_log.py:45`;
`docs/user-guide/administration/configuration/settings.html` (LOGGING).

## 6. Performance

Decision: fix the query shape before adding hardware: ask for less (`depth`, `limit`, field-scoped GraphQL), fetch related rows in bulk, and size workers to the Job mix.

| Lever            | Setting or syntax                                                            | Note                                                       |
| ---------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------- |
| REST nesting     | `?depth=0` (default) to `10`                                                 | each level multiplies serialisation                        |
| Page size        | `?limit=`; `MAX_PAGE_SIZE` (1000), `PAGINATE_COUNT` (50)                     | `MAX_PAGE_SIZE = 0` lets one request fetch everything      |
| M2M in REST      | `?exclude_m2m=true` (default in 3.x)                                         | include only when needed                                   |
| ORM in Jobs      | `.select_related("location", "platform")`, `.prefetch_related("interfaces")` | one query per relation, not per row                        |
| N+1 tests        | `AssertNoRepeatedQueries(self, threshold=10)`                                | from `nautobot.apps.testing`                               |
| Large list views | `LOCATION_LIST_DEFAULT_MAX_DEPTH`, `PREFIX_LIST_DEFAULT_MAX_DEPTH`           | Constance settings                                         |
| Cache            | `CACHES["default"]` django-redis, Redis DB 1, `TIMEOUT` 300                  | `CONTENT_TYPE_CACHE_TIMEOUT` defaults to 0 (off)           |
| Workers          | `nautobot-server celery worker --queues <q> --concurrency N`                 | raise for I/O-bound Jobs; separate queues for long Jobs    |
| Prefetch         | `CELERY_WORKER_PREFETCH_MULTIPLIER` (4)                                      | lower to 1 for long Jobs so one worker does not hoard them |
| Job limits       | `CELERY_TASK_SOFT_TIME_LIMIT` 300 s, `CELERY_TASK_TIME_LIMIT` 600 s          | per-Job overrides `soft_time_limit`, `time_limit`          |

Gotcha: GraphQL has no query cost or depth limiter in 3.2.3 (none found in `nautobot/core/graphql/`); a deep nested query is bounded only by the request timeout and the per-field optimiser
(`graphene-django-optimizer`). Use saved queries and review them.

Source: `nautobot/core/settings.py:1059-1076,1126,1140-1146`, `nautobot/core/graphql/generators.py:7,109`, `nautobot/core/api/serializers.py:55-120`;
`docs/user-guide/administration/configuration/settings.html` (MAX_PAGE_SIZE), `docs/user-guide/administration/guides/celery-queues.html`, `docs/development/apps/api/testing.html`.

## 7. Security settings

Decision: set these explicitly in production; Nautobot's built-in defaults are permissive or empty.

| Setting                                                     | 3.2.3 default                         | Set to                                                                                |
| ----------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------- |
| `SECRET_KEY` (`NAUTOBOT_SECRET_KEY`)                        | `""`                                  | 50+ random characters (`nautobot-server generate_secret_key`); same on every web node |
| `ALLOWED_HOSTS` (`NAUTOBOT_ALLOWED_HOSTS`, space-separated) | `[]`                                  | the FQDNs users and tools use                                                         |
| `CSRF_TRUSTED_ORIGINS` (comma-separated env)                | `[]`                                  | `https://nautobot.example` behind a TLS-terminating proxy                             |
| `SECURE_PROXY_SSL_HEADER`                                   | `("HTTP_X_FORWARDED_PROTO", "https")` | keep; make the proxy set the header                                                   |
| `SESSION_COOKIE_AGE`                                        | `1209600` (2 weeks)                   | shorter, e.g. `43200`                                                                 |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE`                           | `False`                               | `True` where shared workstations are used                                             |
| `EXEMPT_VIEW_PERMISSIONS`                                   | `[]`                                  | leave empty                                                                           |
| `DEBUG`                                                     | `False`                               | `False`                                                                               |
| `X_FRAME_OPTIONS`                                           | `"DENY"`                              | keep                                                                                  |
| `CORS_ALLOW_ALL_ORIGINS`                                    | `False`                               | keep; list origins in `CORS_ALLOWED_ORIGINS`                                          |
| `WEBHOOK_ALLOWED_HOSTS`                                     | `[]`                                  | the webhook receivers' hosts                                                          |

Gotcha: `EXEMPT_VIEW_PERMISSIONS` makes listed models readable by anonymous users too, and `['*']` exempts all but sensitive models. Changing `SECRET_KEY` logs every user out; no 3.2.3 core code
outside settings reads it (searched), so stored data is not encrypted with it. There is no `LOGIN_REQUIRED` setting in 3.2.3 (absent from settings and docs).

Source: `nautobot/core/settings.py:134,342-344,530-546,548,619-621,766-768,1032-1039`, `nautobot/core/templates/nautobot_config.py.j2:13-18,91-116`, `nautobot/core/constants.py:112`;
`docs/user-guide/administration/configuration/settings.html` (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, EXEMPT_VIEW_PERMISSIONS, SECRET_KEY, SESSION_COOKIE_AGE).

## 8. Authentication and tokens

Decision: SSO through `social-auth-app-django` (installed 5.9.0) or LDAP through `django-auth-ldap` (installed 5.3.0); always keep Nautobot's object permission backend in `AUTHENTICATION_BACKENDS`.

```python
# OIDC/OAuth2 example (Okta); redirect URI is https://nautobot.example/complete/okta-openidconnect/
AUTHENTICATION_BACKENDS = ["social_core.backends.okta_openidconnect.OktaOpenIdConnect",
                           "nautobot.core.authentication.ObjectPermissionBackend"]
SOCIAL_AUTH_OKTA_OPENIDCONNECT_KEY = os.environ["OIDC_CLIENT_ID"]
SOCIAL_AUTH_OKTA_OPENIDCONNECT_SECRET = os.environ["OIDC_CLIENT_SECRET"]
EXTERNAL_AUTH_DEFAULT_GROUPS = ["read-only"]

# LDAP example
import ldap
from django_auth_ldap.config import LDAPSearch
AUTHENTICATION_BACKENDS = ["django_auth_ldap.backend.LDAPBackend", "nautobot.core.authentication.ObjectPermissionBackend"]
AUTH_LDAP_SERVER_URI = "ldaps://ldap.example"
AUTH_LDAP_BIND_DN = "CN=svc-nautobot,OU=Service,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = os.environ["LDAP_BIND_PASSWORD"]
AUTH_LDAP_USER_SEARCH = LDAPSearch("OU=Users,DC=example,DC=com", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
```

```bash
# tokens: fields user, key (40 chars), expires, write_enabled, description
curl -s -X POST -u "$NB_USER:$NB_PASS" -H "Content-Type: application/json" https://nautobot.example/api/users/tokens/ \
  -d '{"description": "ci reader", "write_enabled": false, "expires": "2027-01-01T00:00:00Z"}'
curl -s -H "Authorization: Token $NAUTOBOT_TOKEN" "https://nautobot.example/api/users/tokens/?q=ci"   # filters: id, key, write_enabled, created, expires, description, q
```

Rotation: create the new token, move the consumer, then `DELETE /api/users/tokens/<id>/`; Nautobot has no automatic rotation, only `expires`.

Gotcha: the SSO docs say `ObjectPermissionBackend` must stay in the list (excluding it is an error); without it object permissions do not apply. `write_enabled: false` is the cheapest
least-privilege control for readers. Basic-auth provisioning needs a password Django can authenticate (local or LDAP); an SSO-only user has none. The token list has no user filter (strict filtering
returns 400 for `?user=`).

Source: `nautobot/core/settings.py:258-268,749-752`, `nautobot/users/models.py:241-270`, `nautobot/users/filters.py:92-97`, `nautobot/users/api/urls.py`;
`docs/user-guide/administration/configuration/authentication/sso.html`,
`.../authentication/ldap.html`, `docs/user-guide/platform-functionality/rest-api/authentication.html`.

## 9. Workers and scheduler

Decision: when Jobs stall, check in this order: a worker answers ping, it consumes the Job's queue, the task is active or reserved, the scheduler's heartbeat is fresh.

```bash
nautobot-server celery inspect ping                        # every worker; -d/--destination celery@<host> for one
nautobot-server celery inspect active_queues               # queues each worker consumes
nautobot-server celery inspect active                      # running tasks
nautobot-server celery inspect reserved                    # prefetched, not started
nautobot-server celery inspect scheduled                   # ETA/countdown tasks
nautobot-server celery inspect stats                       # pool size, totals, rusage
nautobot-server celery inspect registered                  # task names the worker knows
nautobot-server celery inspect ping -t 5 -j                # longer timeout, JSON output
```

Staff users also have `/worker-status/` in the UI (workers and configured queues). Job results are stored in the database (`CELERY_RESULT_BACKEND =
"nautobot.core.celery.backends.NautobotDatabaseBackend"`); the beat scheduler is `nautobot.core.celery.schedulers:NautobotDatabaseScheduler`, so schedules live in the database.

Gotcha: `inspect` broadcasts over the Redis broker and waits 1.0 second by default (`--timeout`); a busy worker can miss it, so retry with `-t 5` before declaring it dead. A Job whose queue no
worker consumes stays
`PENDING` with no error. `nautobot-server celery inspect --help` prints Nautobot's own help; read Celery's options with `python -m celery inspect --help` or `--list`.

Source: `nautobot/core/urls.py:95`, `nautobot/core/views/__init__.py:290-295`, `nautobot/core/settings.py:1102-1167`; `python -m celery inspect --help` and `--list` (Celery 5.6.3);
`docs/user-guide/administration/guides/health-checks.html`, `docs/user-guide/administration/guides/celery-queues.html`.

> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: nautobot/core/settings.py line 177 reads NAUTOBOT_METRICS_AUTHENTICATED into METRICS_AUTHENTICATED · Falsifier: a 3.2.x release that reads a METRICS_AUTHENTICATION setting
> The metrics authentication setting is `METRICS_AUTHENTICATED` (env `NAUTOBOT_METRICS_AUTHENTICATED`); the bundled Prometheus guide calls it `METRICS_AUTHENTICATION`, which has no effect. Check the setting name against settings.py.
