import requests
import json


class BaseParser(object):
    host_attr = 'host'
    link_attr = 'link'
    client = requests

    def __init__(self, info):
        self.info = info
        self.map = json.loads(self.info.map)
        self.encode = self.map.pop('encode', None)
        self.text_keys = ['title', 'description', 'text']
        self.links_keys = ['link']

    def get_map(self):
        return self.map

    def get_content(self):
        return self.client.get(getattr(self.info, self.host_attr) + getattr(self.info, self.link_attr)).content

    def get_items(self):
        raise NotImplementedError

    @property
    def items(self):
        return self.get_items()
