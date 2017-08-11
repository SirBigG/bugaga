import json

from lxml.html import fromstring


class HTMLParser(object):
    def __init__(self, map_string):
        _map = json.loads(map_string)
        self.root = _map['root']
        self.map = _map['map']

    def parse(self, content):
        return self._load_items(fromstring(content).findall(self.root))

    def _load_items(self, items):
        _items = list()
        for i in items:
            converted = dict()
            for k, path in self.map.items():
                converted.update({k: i.find(path)})
            _items.append(converted)
        return _items


PARSERS = {1: HTMLParser}
