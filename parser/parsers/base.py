import requests
import json


class BaseParser(object):
    host_attr = 'host'
    link_attr = 'link'
    client = requests

    def __init__(self, info, link=None):
        self.info = info
        self.map = json.loads(self.info.map)
        self.link = link
        self.encode = self.map.pop('encode', None)
        self.text_keys = ['title', 'description', 'text']
        self.links_keys = ['link']
        self.status_code = None

    def get_map(self):
        return self.map

    def get_link(self):
        return self.link if self.link else getattr(self.info, self.host_attr) + getattr(self.info, self.link_attr)

    def get_response(self):
        return self.client.get(self.get_link())

    def get_content(self):
        response = self.get_response()
        self.status_code = response.status_code
        return response.content

    def get_items(self):
        raise NotImplementedError

    def get_item(self):
        raise NotImplemented

    @property
    def items(self):
        return self.get_items()
