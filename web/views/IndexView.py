import json

from aiohttp import web
from aiohttp import hdrs

import db

from models.category import Category


class IndexView(web.View):
    async def get(self):
        return web.Response(text="Hello")


class ClassifierListView(web.View):
    async def get(self):
        classifiers = [{'id': i.id, 'slug': i.slug,
                        'title': i.title} for i in db.Session().query(Category).filter(Category.is_active == True)]
        return web.Response(body=json.dumps(classifiers), content_type="application/json",
                            headers={hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*'})
