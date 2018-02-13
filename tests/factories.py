import factory.alchemy

from models.category import Category
from models.parser import ParserMap
from models.auth import User

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
    host = 'host'
    map = '{"key1": "xpath"}'
    root = "root_xpath"
    type = 1
    period = 15
    period_type = "minutes"


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = 'commit'

    username = factory.Sequence(lambda n: 'username%d' % n)
