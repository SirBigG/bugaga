from datetime import datetime, timedelta

from web import routes

from passlib.hash import pbkdf2_sha256

import jwt

from settings import settings


def initialize_routes(app):
    for route in routes.ROUTES_GET:
        app.router.add_get(*route)
    for route in routes.ROUTES_POST:
        app.router.add_post(*route)


def encrypt_password(password):
    return pbkdf2_sha256.hash(password)


def check_password(password, password_hash):
    return pbkdf2_sha256.verify(password, password_hash)


def get_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return token.decode('utf-8')
