# AgroMega API Django migration

The Django service runs alongside the legacy Flask/aiohttp application during migration. The API and Admin have moved
to Django; the legacy `bot` and `scheduler` remain production entrypoints until the Celery schedules described below
are explicitly enabled.

## Target runtime

- Python 3.14
- Django 6.1
- Django Ninja 1.6.3
- PostgreSQL 15+ using the existing database and table names
- AgroMega OpenID Connect at `https://agromega.in.ua/o`
- Celery 5.6 with Redis as a small durable broker
- Celery Beat schedules stored in PostgreSQL and managed from Django Admin

The existing data tables are represented by unmanaged Django models. Django migrations must only create Django auth,
session, admin-log, content-type, and local OIDC identity tables.

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
schedules are disabled. `just workers-enable` is intentionally separate and must not be used while the matching legacy
processes are still running.

## Docker Hub deployment

The legacy `sirbigg/bugaga:latest` image continues to run `bot` and `scheduler` during the migration. Django and its
Celery worker/beat processes use one image built from `Dockerfile.django` and published under a separate immutable tag:

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

## Bot and scheduler migration

The replacement keeps the externally visible behavior but removes the unsupported Python 3.11 runtime dependencies:

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

### Staged production rollout

All steps use the immutable Django image. They do not require an API or PostgreSQL outage.

1. Keep `BUGAGA_BOT_ENABLED=false` and `BUGAGA_SCHEDULER_ENABLED=false` in `project.env`.
2. Deploy the new Django image first. Its normal `migrate` step creates only Django/Celery schedule tables and
   `workers_workerstate`; unmanaged legacy tables are not changed.
3. Run `just deploy-workers`, `just production-workers-schedules`, and inspect `just production-workers-logs`. Confirm exactly one
   `celery-beat-next` container is running. The worker is inert because schedules and feature flags are disabled.
4. Bot cutover: stop only the legacy `bot`; set `BUGAGA_BOT_ENABLED=true`; recreate `celery-worker-next`; then enable
   only **AgroMega Telegram polling** in Django Admin. Send `/start` from a test chat and confirm the user is subscribed.
5. Scheduler cutover: wait for the current legacy scheduler cycle to finish and stop only legacy `scheduler`; set
   `BUGAGA_SCHEDULER_ENABLED=true`; recreate `celery-worker-next`; then enable **AgroMega parsing pipeline** and
   **AgroMega daily news summary** in Admin. Verify one cycle's counts, Telegram delivery, images, classifications, and
   summary timing before removing the old containers.

Changing `project.env` does not change an already running container. Recreate the worker after each flag change.
Schedules can also be enabled together with `just production-workers-enable`, but Admin is safer for the independent cutovers.

### Rollback

Disable the affected PeriodicTask in Admin first (or use `just production-workers-disable` for all three). Check
`just production-workers-active` and `just production-workers-logs`; wait for any active pipeline task to finish before restarting the corresponding legacy
container; the advisory lock cannot coordinate with legacy SQLAlchemy code. Set the feature flag back to `false` and
recreate the worker. API/Admin and Redis can remain online throughout rollback.

## Production schema capture

Run from the directory containing the production Compose file:

```bash
just schema-dump
```

Create a full, private backup immediately before cutover:

```bash
just backup
```

Neither file may be committed. The full dump contains production data, including Telegram identifiers.

### Database upgrade prerequisite

The captured production dump reports PostgreSQL 9.6.9, while Django 6.1 requires PostgreSQL 15 or newer. Do not mount
the existing PostgreSQL 9.6 `data/` directory into the PostgreSQL 16 container. The supported cutover is a logical
backup and restore into a new empty PostgreSQL 16 volume:

1. Stop all legacy writers (`bot`, `scheduler`, and `admin`) for the final backup window.
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

The first release preserves the routes and response shapes consumed by `am-core`:

- `GET /news`
- `GET /news/<id>`
- `GET /news/sitemap`
- `GET /adverts`
- `GET /categories`

The obsolete aiohttp registration/login API and the unauthenticated `/telegram/admin` endpoint are not part of the new
public API.
