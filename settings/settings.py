# -*- coding: utf-8 -*-
import logging
import os


DEBUG_LEVEL = logging.basicConfig(level=logging.DEBUG)

DEBUG = True if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV' else False

# server settings
HOST = os.getenv('BOT_HOST', '0.0.0.0')
PORT = os.getenv('BOT_PORT', 8888)

# database settings
DB_HOST = os.getenv('POSTGRES_HOST', 'db')
DB_NAME = os.getenv('POSTGRES_DB', 'bugagadb')
DB_USER = os.getenv('POSTGRES_USER', 'bugaga')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'bugaga')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# JWT settings
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

# Bot settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')


# if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
#     ENGINE = "sqlite:////web/db.sqlite3"
# else:

ENGINE = "postgresql://%s:%s@%s:%s/%s" % (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

# S3 DO secrets
DO_SPACE_KEY = os.getenv('DO_SPACE_KEY')
DO_SPACE_SECRET = os.getenv('DO_SPACE_SECRET')
DO_SPACE_REGION = os.getenv('DO_SPACE_REGION')
DO_SPACE_NAME = os.getenv('DO_SPACE_NAME')
