# -*- coding: utf-8 -*-
from aiohttp import web


class IndexView(web.View):
    async def get(self):
        return web.Response(text="Hello")
