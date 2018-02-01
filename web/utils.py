import os

from web import routes


def initialize_routes(app):
    for route in routes.ROUTES_GET:
        app.router.add_get(*route)
