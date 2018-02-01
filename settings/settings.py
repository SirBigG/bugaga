# -*- coding: utf-8 -*-
import logging
import os


DEBUG_LEVEL = logging.basicConfig(level=logging.DEBUG)

HOST = "0.0.0.0"
PORT = 8888

DB_HOST = "localhost"
DB_NAME = "bugaga"
DB_USER = "Setting username in local settings"
DB_PASSWORD = "Setting local settings"


try:
    from settings.settings_local import *
except ImportError:
    logging.warning("No local settings!")

if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
    ENGINE = "sqlite:///db.sqlite3"
else:
    ENGINE = "postgresql://%s:%s@%s/%s" % (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
