# -*- coding: utf-8 -*-
import os
import asyncio
from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web import routes
from settings import settings


class Application(object):
    def __init__(self, loop=None):
        self.app = web.Application(loop=loop or asyncio.get_event_loop())
        self.engine = create_engine("postgresql://%s:%s@%s/%s" % settings.DB_SETTINGS)
        self.session = sessionmaker(bind=self.engine)

    def start(self):
        for route in routes.ROUTES:
            self.app.router.add_route(*route)
        self.app.router.add_static('/static', os.path.join(os.path.dirname(__file__), 'web', 'static'))
        web.run_app(self.app, host=settings.HOST, port=settings.PORT)


app = Application()
if __name__ == "__main__":
    app.start()
