import os

import asyncio

from aiohttp import web

from web.utils import initialize_routes

import db

from settings import settings


class Application(object):
    def __init__(self, loop=None):
        self.app = web.Application(loop=loop or asyncio.get_event_loop())
        self.engine = db.Engine
        self.session = db.Session()

    def start(self):
        initialize_routes(self.app)
        self.app.router.add_static('/static', os.path.join(os.path.dirname(__file__), 'web', 'static'))
        web.run_app(self.app, host=settings.HOST, port=settings.PORT)


app = Application()
if __name__ == "__main__":
    app.start()
