import json
import unittest
from unittest import mock

from tests.factories import CategoryFactory, ParserMapFactory
from tests.utils import MockResponse
from tests.common import Session
from tests.constants import TEST_HTML

from parser.handlers import ParseHandler

from models.parser import ParsedItem


class ParserHandlerTests(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.rollback()
        Session.remove()

    @mock.patch('requests.get', return_value=MockResponse(TEST_HTML))
    def test_create_items(self, mock_response):
        category = CategoryFactory()
        map_ = ParserMapFactory(is_active=True, map=json.dumps({"title": './/div[@class="content"]/text()',
                                                                "link": './/a/@href'}),
                                root='//div[@class="item"]',
                                category_id=category.id, type=1
                                )
        ParseHandler(map_, self.session).create_items()
        self.assertEqual(self.session.query(ParsedItem).count(), 2)
