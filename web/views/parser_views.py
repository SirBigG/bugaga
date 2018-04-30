import json

from aiohttp import web
from aiohttp import hdrs

import db

from models.parser import ParsedItem


class PostsListView(web.View):
    async def get(self):
        posts = [json.loads(i.data) for i in db.Session().query(ParsedItem).all()]
        return web.Response(body=json.dumps(posts), content_type="application/json",
                            headers={hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*'})
