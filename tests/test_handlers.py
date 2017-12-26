import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web.models.parser import Base
from web.models.category import Category, Base as CategoryBase


TEST_HTML = '<head><title>Title</title></head><body><div class="container">' \
            '<div class="item"><a href="http://test.com/item1">Title item</a>' \
            '<div class="content">Content</div></div>' \
            '<div class="item"><a href="http://test.com/item1">Title item</a>' \
            '<div class="content">Content</div></div></div></body>'


class ParserHandlerTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(self.engine)
        self.session = Session()
        CategoryBase.metadata.create_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.category = Category(slug='category', title='Category')
        self.session.add(self.category)
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_fetch_data(self):
        pass

    def test_parse_data(self):
        pass

    def test_is_new(self):
        pass

    def test_create_item(self):
        pass

    def test_send_to_channels(self):
        pass
