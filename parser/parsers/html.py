from lxml import html

from .base import BaseParser


class HtmlParser(BaseParser):

    def get_items(self):
        tree = html.fromstring(self.get_content())
        parsed = list()
        for i in tree.xpath(self.info.root):
            data = {}
            for k, v in self.get_map().items():
                value = i.xpath(v)[0]
                if k in self.links_keys:
                    if not value.startswith(self.info.host):
                        value = self.info.host + value
                if self.encode and k in self.text_keys:
                    value = value.encode(self.encode).decode()
                data.update({k: value})
            parsed.append(data)
        return parsed
