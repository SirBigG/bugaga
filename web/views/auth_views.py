import json

from aiohttp import web
from aiohttp import hdrs

import db

from models.auth import User


class UserView(web.View):
    async def post(self):

        return web.Response(body=json.dumps(classifiers), content_type="application/json",
                            headers={hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*'})
