# -*- coding: utf-8 -*-
import logging
import os


DEBUG_LEVEL = logging.basicConfig(level=logging.DEBUG)

# server settings
HOST = os.getenv('BOT_HOST') or "0.0.0.0"
PORT = os.getenv('BOT_PORT') or 8888

# database settings
DB_HOST = os.getenv('POSTGRES_HOST') or "db"
DB_NAME = os.getenv('POSTGRES_DB') or "bugagadb"
DB_USER = os.getenv('POSTGRES_USER') or "bugaga"
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD') or "bugaga"
DB_PORT = os.getenv('POSTGRES_PORT') or "5432"

# JWT settings
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

# Bot settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or ''


# if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
#     ENGINE = "sqlite:////web/db.sqlite3"
# else:

ENGINE = "postgresql://%s:%s@%s:%s/%s" % (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
