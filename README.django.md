# AgroMega API Django service

The production API, Admin, Telegram bot, parsing pipeline, and daily summary run entirely on Django and Celery. The
retired Flask/aiohttp/SQLAlchemy runtime and its standalone bot and scheduler have been removed.

## Target runtime

- Python 3.14
- Django 6.1
- Django Ninja 1.6.3
- PostgreSQL 15+ using the existing database and table names
- AgroMega OpenID Connect at `https://agromega.in.ua/o`
- Celery 5.6 with Redis as a small durable broker
- Celery Beat schedules stored in PostgreSQL and managed from Django Admin

The existing catalog data tables are represented by unmanaged Django models in `apps.legacy`; the name describes their
database origin, not an active legacy runtime. Django migrations must only create Django auth, session, admin-log,
content-type, local OIDC identity, worker-state, and Celery schedule tables.

## Local checks

```bash
just setup
just verify
```

To start the Django service beside the legacy application on local port `8282`:

```bash
just up
```

To start Redis, one two-thread Celery worker, and the single Celery Beat scheduler:

```bash
just workers-start
just workers-schedules
just workers-logs
```

`workers-schedules` creates or updates all managed schedules but leaves their current enabled state unchanged. New
schedules are disabled. Use `just workers-enable` only after the environment and required secrets are ready.

## Docker Hub deployment

Django and its Celery worker/beat processes use one image built from `Dockerfile.django` and published under an
immutable tag:

```bash
just publish django-YYYYMMDD-N
```

Set `BUGAGA_DJANGO_IMAGE=sirbigg/bugaga:django-YYYYMMDD-N` in the server shell or Compose `.env` file. Do not place it
only in `project.env`: Compose image interpolation happens before a service's `env_file` is loaded. Then deploy without
building source code on the server:

```bash
just pull
just deploy
just deploy-workers
just production-workers-schedules
```

Keep the immutable tag in production rather than `django-latest`; changing the tag back provides a direct application
rollback. The database migration itself has a separate rollback procedure.

`docker-compose.django-service.yml` is the production-ready fragment for the existing server Compose project. It adds
the `django` service without requiring changes to the existing `db` service. Copy the definition into the general
Compose file, or run it as an additional Compose file. The image serves Django admin static assets through WhiteNoise,
so Nginx only needs to proxy application traffic to `127.0.0.1:8282`.

The production fragment overrides the image user with `0:0` because the current server runtime cannot initialize the
image's non-root user and fails while changing ownership of `/dev/stdout`. The image itself remains non-root by default;
remove this compatibility override after Docker Engine, containerd, and runc are upgraded and verified on the server.
It also limits Gunicorn to one worker because the current production host has 1 GB of RAM; scale the worker count only
after increasing available memory.

The Django Ninja documentation is available at `/docs`, health at `/health`, and the OIDC-protected administration at
`/admin/`.

## Celery workloads

The Celery workloads preserve the externally visible behavior of the retired standalone bot and scheduler:

- `bugaga.poll_telegram` polls Telegram every five seconds through Celery Beat. There is no separate bot container.
  The last processed Telegram `update_id` is stored in the Django-owned `workers_workerstate` table.
- `bugaga.run_pipeline` preserves the legacy order: parse news, notify subscribed Telegram users, discover and parse
  adverts, then classify uncategorized adverts.
- `bugaga.create_daily_summary` runs at 19:00 in `Europe/Kyiv`, calls the configured OpenAI model, and preserves the
  legacy summary title, URL, HTML conversion, and 18:00 UTC database timestamp. It also checks for an existing summary
  before writing, making retries idempotent.
- PostgreSQL session advisory locks prevent overlapping poll, pipeline, and summary executions. Beat must still run as
  exactly one container; Celery itself warns that multiple beat schedulers emit duplicate tasks.
- Expired Telegram/pipeline messages are discarded instead of building a stale queue after a long outage.

The Celery worker uses a two-thread pool. A long parsing/classification task can occupy one thread while short Telegram
poll tasks continue on the other. BLAS thread counts are limited to one to fit the current small production host.

### Django 6.1 compatibility pin

The released `django-celery-beat` 2.9.0 metadata still caps Django below 6.1. This project pins the exact reviewed
upstream commit `8049336cf61c38a281244fba2431caf438e93b73`, which added Django 6.1 to the upstream test matrix and was
merged after all checks passed. Replace the Git dependency with the next compatible PyPI release once available; do
not silently override the released package's dependency metadata.

### Production operations

Keep `BUGAGA_BOT_ENABLED=true` and `BUGAGA_SCHEDULER_ENABLED=true` in production. They are operational kill switches:
changing either value requires recreating `celery-worker` because editing `project.env` does not change an existing
container.

For a routine immutable-image deployment:

1. Run `just pull`, `just deploy`, and `just deploy-workers`.
2. Run `just production-workers-schedules` to reconcile the database schedules without changing their enabled state.
3. Confirm exactly one `celery-beat` container is running and inspect `just production-workers-logs`.
4. Verify Telegram polling plus one parsing and summary cycle after a workload change.

The service names were finalized from `celery-worker-next`/`celery-beat-next` to `celery-worker`/`celery-beat`. During
that one-time Compose update, disable the periodic schedules and stop/remove the old `*-next` containers before
starting the renamed services. Never allow both Beat containers to run concurrently.

### Rollback

Disable the affected PeriodicTask in Admin first (or use `just production-workers-disable` for all three). Check
`just production-workers-active` and `just production-workers-logs`, then wait for any active pipeline task to finish.
Set the affected feature flag to `false`, recreate the worker, and roll the immutable image tag back if necessary.
API/Admin and Redis can remain online throughout an application-image rollback.

## Production schema capture

Run from the directory containing the production Compose file:

```bash
just schema-dump
```

Create a full, private backup before a database migration or other high-risk maintenance:

```bash
just backup
```

Neither file may be committed. The full dump contains production data, including Telegram identifiers.

### Migrating an old PostgreSQL 9.6 environment

The captured production dump reports PostgreSQL 9.6.9, while Django 6.1 requires PostgreSQL 15 or newer. Do not mount
the existing PostgreSQL 9.6 `data/` directory into the PostgreSQL 16 container. The supported cutover is a logical
backup and restore into a new empty PostgreSQL 16 volume:

1. Disable Celery schedules and stop all application writers for the final backup window.
2. Create the final custom-format backup with `just backup`.
3. Restore it into a new empty PostgreSQL 16 database with `pg_restore --no-owner --no-privileges`.
4. Run `python manage.py migrate --settings=config.settings.production`; unmanaged legacy tables are not altered.
5. Compare row counts, run the API smoke checks, and only then switch Nginx and restart writers.

This repository's production dump was test-restored into PostgreSQL 16 successfully. Django migrations and read-only
ORM access preserved the legacy row counts, and all compatibility endpoints returned HTTP 200 over HTTPS.

## OIDC client

Register a confidential authorization-code client in `am-core` with:

- client ID: `agromega-parser`
- redirect URI: `https://api.agromega.in.ua/oidc/callback/`
- post-logout redirect URI: `https://api.agromega.in.ua/admin/`
- scopes: `openid profile email`
- signing algorithm: `RS256`

The service authorizes Django Admin from the provider's `is_staff` claim. Synchronizing `is_superuser` is disabled by
default and can be enabled explicitly with `OIDC_SYNC_SUPERUSER=true`.

Copy `project.env.example` to the server's existing private `project.env` and replace placeholder secrets. Nginx must
forward `Host` and `X-Forwarded-Proto`, and only Nginx should expose the service publicly.

## Compatibility endpoints

The service preserves the routes and response shapes consumed by `am-core`:

- `GET /news`
- `GET /news/<id>`
- `GET /news/sitemap`
- `GET /adverts`
- `GET /categories`

The retired aiohttp registration/login API and the unauthenticated `/telegram/admin` endpoint are not part of the
public API.
