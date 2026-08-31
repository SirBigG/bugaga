# AgroMega API Django migration

The new Django service is being built alongside the legacy Flask/aiohttp application. The legacy processes remain the
production entrypoints until the Django implementation is verified against a recent copy of the production database.

## Target runtime

- Python 3.14
- Django 6.1
- Django Ninja 1.6.3
- PostgreSQL 15+ using the existing database and table names
- AgroMega OpenID Connect at `https://agromega.in.ua/o`

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

## Docker Hub deployment

The legacy `sirbigg/bugaga:latest` image continues to run `bot` and `scheduler` during the migration. Django is built
from `Dockerfile.django` and published under a separate immutable tag in the same Docker Hub repository:

```bash
just publish django-YYYYMMDD-N
```

Set `BUGAGA_DJANGO_IMAGE=sirbigg/bugaga:django-YYYYMMDD-N` in the server shell or Compose `.env` file. Do not place it
only in `project.env`: Compose image interpolation happens before a service's `env_file` is loaded. Then deploy without
building source code on the server:

```bash
just pull
just deploy
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
