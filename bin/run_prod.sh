#!/bin/sh

/bin/sh -c "alembic upgrade head"
/bin/sh -c "gunicorn -b 0.0.0.0:8181 -w 3 wsgi:app"
