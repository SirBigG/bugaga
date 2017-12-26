import json
import aiohttp
import hashlib

from .parsers import PARSERS

from web.models.parser import ParsedItem

from server import app


class ParseHandler(object):
    client = aiohttp.ClientSession()

    def __init__(self, map_instance):
        self.map = map_instance
        self.session = app.session()

    async def fetch_data(self):
        return await self.client.get(self.map.link)

    def create_items(self):
        to_create = list()
        for i in PARSERS.get(self.map.type)(self.map.map).parse(self.fetch_data()):
            item = self.create_item(i)
            if item:
                to_create.append(item)
        self.session.add_all(to_create)
        self.session.commit()

    def get_item_hash(self, i):
        return hashlib.md5(':'.join([i[k] for k, _ in json.loads(self.map.map)['map']] + [self.map.link])).hexdigest()

    def is_new(self, _hash):
        return self.session.query(ParsedItem).filter(hash=_hash).exists()

    def create_item(self, i):
        _hash = self.get_item_hash(i)
        if self.is_new(_hash):
            return ParsedItem(hash=_hash, category_id=self.map.category_id, data=json.dumps(i))
