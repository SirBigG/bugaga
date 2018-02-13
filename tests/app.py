from aiohttp import web

from web.utils import initialize_routes

test_app = web.Application()

initialize_routes(test_app)
