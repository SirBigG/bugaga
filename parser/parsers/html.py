import logging

from lxml import html

from .base import BaseParser


class HtmlParser(BaseParser):

    def get_items(self):
        tree = html.fromstring(self.get_content())
        parsed = list()
        for i in tree.xpath(self.info.root):
            data = {}
            for k, v in self.get_map().items():
                try:
                    value = i.xpath(v)[0]
                    if k in self.links_keys:
                        if not value.startswith(self.info.host):
                            value = self.info.host + value
                    if self.encode and k in self.text_keys:
                        value = value.encode(self.encode).decode()
                    data.update({k: value})
                except Exception as e:
                    logging.error(e)
            if data:
                parsed.append(data)
        return parsed

    def get_item(self):
        tree = html.fromstring(self.get_content())
        for i in tree.xpath(self.info.root):
            try:
                to_return = dict()
                for k, v in self.get_map().items():
                    try:
                        value = i.xpath(v)[0].text_content()
                    except AttributeError:
                        try:
                            value = i.xpath(v)[0]
                        except IndexError:
                            value = ""
                    except IndexError:
                        value = ""
                    to_return.update({k: value})
                return to_return
            except Exception as e:
                logging.error(e)


class HtmlIterParser(HtmlParser):
    def __init__(self, info):
        super().__init__(info)
        self.page = 1
        # TODO: migrate this setting to environment variables
        self.max_page = 100

    def __iter__(self):
        return self

    def __next__(self):
        if self.status_code == 200 and self.page <= self.max_page:
            self.page += 1
            return self.get_items()
        else:
            logging.error(self.status_code)
            raise StopIteration

    def get_link(self):
        link = super().get_link()
        if "{}" in link:
            self.page = self.max_page
            return link
        return link.format(self.page)
