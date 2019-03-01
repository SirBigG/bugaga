import json
import os

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from sqlalchemy.orm import sessionmaker, scoped_session

from db import Engine

from models.auth import User
from models.category import Category
from models.parser import ParserMap, ParsedItem, AdvertParserMap, Link, Advert

# TODO: Monkey path remove it after flask-admin is updated
from flask_admin.contrib.sqla import fields
from flask_admin._compat import text_type
from sqlalchemy.orm.util import identity_key


def get_pk_from_identity(obj):
    res = identity_key(instance=obj)
    cls, key = res[0], res[1]
    return u':'.join(text_type(x) for x in key)


fields.get_pk_from_identity = get_pk_from_identity

# Create application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or '123456790'

session = scoped_session(sessionmaker(bind=Engine))


class AdvertModelView(ModelView):
    column_editable_list = ("category",)
    column_formatters = dict(data=lambda v, c, m, p: json.loads(m.data))
    page_size = 200


if __name__ == '__main__':
    # Create admin
    admin = Admin(app, name='microblog', template_mode='bootstrap3', url="/admin/advert")
    admin.add_view(ModelView(User, session))
    admin.add_view(ModelView(Category, session))
    admin.add_view(ModelView(ParserMap, session))
    admin.add_view(ModelView(ParsedItem, session))
    admin.add_view(ModelView(AdvertParserMap, session))
    admin.add_view(ModelView(Link, session))
    admin.add_view(AdvertModelView(Advert, session))

    # Start app
    app.debug = True
    app.run('0.0.0.0', 8181)
