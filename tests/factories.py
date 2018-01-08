import factory.alchemy

from web.models.category import Category
from web.models.parser import ParserMap

from .common import Session


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'

    slug = factory.Sequence(lambda n: 'category%d' % n)
    title = 'title'


class ParserMapFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ParserMap
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'

    link = 'link'
    map = '{"key1": "xpath"}'
    root = "root_xpath"
    type = 1
    period = 15
    period_type = "minutes"
