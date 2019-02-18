import json
import hashlib
from urllib import parse

import db

from .parsers import PARSERS

from models.parser import ParsedItem, Advert, Link


class ParseHandler(object):

    def __init__(self, map_instance, session=None):
        self.map = map_instance
        self.session = db.Session() if session is None else session

    def create_items(self):
        tt = list()
        to_create = list()
        for i in PARSERS.get(self.map.type)(self.map).get_items():
            item = self.get_item(i)
            if item:
                to_create.append(item)
                tt.append(i)
        self.session.add_all(to_create)
        self.session.commit()
        return tt

    def get_item_hash(self, i):
        _map = json.loads(self.map.map)
        _map.pop('encode', None)
        return hashlib.md5((':'.join([i[k] for k in _map.keys()]) + self.map.link).encode('utf-8')
                           ).hexdigest()

    def is_new(self, _hash):
        q = self.session.query(ParsedItem).filter(ParsedItem.hash == _hash)
        return not self.session.query(q.exists()).scalar()

    def get_item(self, data):
        _hash = self.get_item_hash(data)
        if self.is_new(_hash):
            return ParsedItem(hash=_hash, category_id=self.map.category_id, data=json.dumps(data))


class LinkParseHandler(ParseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    def create_items(self):
        to_create = list()
        for items in PARSERS.get(self.map.type)(self.map):
            # If more than ten parsed items just skip
            if self.counter >= 10:
                break
            for i in items:
                item = self.get_item(i)
                if item:
                    to_create.append(item)
            self.session.add_all(to_create)
            self.session.commit()
            to_create = list()

    def is_new(self, link):
        q = self.session.query(Link).filter(Link.link == link)
        return not self.session.query(q.exists()).scalar()

    def get_item(self, data):
        # Clean link before checking
        _link = parse.urlparse(data["link"])
        _link = f'{_link.scheme}://{_link.netloc}{_link.path}'
        if self.is_new(_link):
            return Link(link=_link)
        self.counter += 1


class AdvertParseHandler(ParseHandler):
    def create_adverts(self):
        for link in self.session.query(Link).filter(Link.is_parsed.is_(False)).filter(Link.link.contains(self.map.host)):
            item = PARSERS.get(self.map.type)(self.map, link=link.link).get_item()
            if item:
                self.session.add(Advert(data=json.dumps(item), link=link.link))
            link.is_parsed = True
            self.session.commit()