# -*- coding: utf-8 -*-
import logging

DEBUG_LEVEL = logging.basicConfig(level=logging.DEBUG)

HOST = "localhost"
PORT = 8888

DB_HOST = "localhost"
DB_NAME = "bugaga"
DB_USER = "Setting username in local settings"
DB_PASSWORD = "Setting local settings"


try:
    from settings.settings_local import *
except ImportError:
    logging.warning("No local settings!")

DB_SETTINGS = (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
