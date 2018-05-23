# -*- coding: utf-8 -*-
import logging
import os


DEBUG_LEVEL = logging.basicConfig(level=logging.DEBUG)

# server settings
HOST = os.getenv('BOT_HOST') or "0.0.0.0"
PORT = os.getenv('BOT_PORT') or 8888

# database settings
DB_HOST = os.getenv('BOT_DB_HOST') or "localhost"
DB_NAME = os.getenv('BOT_DB_NAME') or "bugaga"
DB_USER = os.getenv('BOT_DB_USER') or "Setting username in local settings"
DB_PASSWORD = os.getenv('BOT_DB_PASS') or "Setting local settings"
DB_PORT = os.getenv('BOT_DB_PORT') or "5432"

# JWT settings
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

# Bot settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or ''


try:
    from settings.settings_local import *
except ImportError:
    logging.warning("No local settings!")

if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
    ENGINE = "sqlite:////web/db.sqlite3"
else:
    ENGINE = "postgresql://%s:%s@%s:%s/%s" % (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
