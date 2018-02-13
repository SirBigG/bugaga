# -*- coding: utf-8 -*-
import logging
import os


DEBUG_LEVEL = logging.basicConfig(level=logging.DEBUG)

# server settings
HOST = "0.0.0.0"
PORT = 8888

# database settings
DB_HOST = "localhost"
DB_NAME = "bugaga"
DB_USER = "Setting username in local settings"
DB_PASSWORD = "Setting local settings"

# JWT settings
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20


try:
    from settings.settings_local import *
except ImportError:
    logging.warning("No local settings!")

if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
    ENGINE = "sqlite:///db.sqlite3"
else:
    ENGINE = "postgresql://%s:%s@%s/%s" % (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
