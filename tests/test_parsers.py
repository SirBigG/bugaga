import json
import unittest
from unittest import mock

from .constants import TEST_HTML
from .utils import MockResponse
from .factories import ParserMapFactory, CategoryFactory
from .common import Session

from parser.parsers import HtmlParser


class HtmlParserTests(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.rollback()
        Session.remove()

    @mock.patch('requests.get', return_value=MockResponse(TEST_HTML))
    def test_parse(self, mock_):
        category = CategoryFactory()
        parser_map = ParserMapFactory(map=json.dumps({"title": './/div[@class="content"]/text()',
                                                      "link": './/a/@href'}),
                                      root='//div[@class="item"]',
                                      category_id=category.id)
        items = HtmlParser(parser_map).items
        self.assertEqual(len(items), 2)
