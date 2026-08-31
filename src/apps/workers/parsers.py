import json
import logging

import requests
from lxml import html

logger = logging.getLogger(__name__)


class BaseParser:
    def __init__(self, info, link=None):
        self.info = info
        self.map = json.loads(info.map)
        self.link = link
        self.encode = self.map.pop("encode", None)
        self.text_keys = {"title", "description", "text"}
        self.link_keys = {"link"}
        self.status_code = 200

    def get_link(self):
        return self.link or f"{self.info.host}{self.info.link}"

    def get_content(self):
        response = requests.get(self.get_link(), timeout=30)
        self.status_code = response.status_code
        if response.status_code != 200:
            logger.error("Parser received HTTP %s from %s", response.status_code, self.get_link())
        response.raise_for_status()
        return response.content


class HTMLParser(BaseParser):
    def get_items(self):
        tree = html.fromstring(self.get_content())
        parsed = []
        for node in tree.xpath(self.info.root):
            data = {}
            for key, xpath in self.map.items():
                try:
                    value = node.xpath(xpath)[0]
                    if key in self.link_keys and not value.startswith(self.info.host):
                        value = self.info.host + value
                    if self.encode and key in self.text_keys:
                        value = value.encode(self.encode).decode()
                    data[key] = value
                except (AttributeError, IndexError, TypeError, UnicodeError):
                    logger.exception("Could not parse %s from %s", key, self.get_link())
            if data:
                parsed.append(data)
        return parsed

    def get_item(self):
        tree = html.fromstring(self.get_content())
        for node in tree.xpath(self.info.root):
            result = {}
            for key, xpath in self.map.items():
                try:
                    value = node.xpath(xpath)[0]
                    value = value.text_content() if hasattr(value, "text_content") else value
                except (AttributeError, IndexError):
                    value = ""
                result[key] = value
            return result
        return None


class HTMLIteratorParser(HTMLParser):
    max_page = 100

    def __iter__(self):
        self.page = 1
        return self

    def __next__(self):
        if self.status_code != 200 or self.page > self.max_page:
            raise StopIteration
        items = self.get_items()
        self.page += 1
        return items

    def get_link(self):
        link = super().get_link()
        if "{}" in link:
            return link.format(self.page)
        self.page = self.max_page
        return link


PARSERS = {1: HTMLParser, 2: HTMLIteratorParser}


def parser_for(info, *, link=None):
    parser_class = PARSERS.get(info.type)
    if parser_class is None:
        raise ValueError(f"Unsupported parser type {info.type!r}")
    return parser_class(info, link=link)
