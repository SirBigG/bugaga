import requests
import json


class BaseParser(object):
    host_attr = 'host'
    link_attr = 'link'
    client = requests

    def __init__(self, info):
        self.info = info

    def get_map(self):
        return json.loads(self.info.map)

    def get_content(self):
        return self.client.get(getattr(self.info, self.host_attr) + getattr(self.info, self.link_attr)).content

    def get_items(self):
        raise NotImplementedError

    @property
    def items(self):
        return self.get_items()
