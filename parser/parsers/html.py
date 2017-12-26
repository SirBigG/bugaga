from lxml import html

from .base import BaseParser


class HtmlParser(BaseParser):

    def get_items(self):
        tree = html.fromstring(self.get_content())
        parsed = list()
        for i in tree.xpath(self.info.root):
            parsed.append({k: i.xpath(v)[0] for k, v in self.get_map().items()})
        return parsed
