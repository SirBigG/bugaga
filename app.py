import json
import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask.views import MethodView

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from sqlalchemy.orm import sessionmaker, scoped_session

from db import Engine

from models.auth import User
from models.category import Category
from models.parser import ParserMap, ParsedItem, AdvertParserMap, Link, Advert

from settings import settings

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

if settings.DEBUG:
    app.debug = True

session = scoped_session(sessionmaker(bind=Engine))


class AdvertModelView(ModelView):
    column_editable_list = ("category",)
    column_formatters = dict(data=lambda v, c, m, p: json.loads(m.data))
    page_size = 200


class AdvertListView(MethodView):
    per_page = 20

    @staticmethod
    def next_prev_links(page, items_count, category, request):
        _base_url = f"{request.scheme}://{request.host}{request.path}"
        if category:
            _base_url = f"{_base_url}?category={category}"

        _prev_page = f"{_base_url}&page={page - 1}" if page > 1 else None
        _next_page = f"{_base_url}&page={page + 1}"
        if items_count == 0:
            _next_page = None
        return _prev_page, _next_page

    def get(self):
        category = request.args.get('category')
        page = request.args.get('page') or 1
        query = session.query(Advert).filter(Advert.created > datetime.now() - timedelta(days=7))
        if category:
            query = query.filter(Advert.category == category)
        _items = [{"data": json.loads(item.data), "link": item.link} for item in
                  query.order_by(Advert.created.desc()).limit(self.per_page).offset((int(page) - 1) * self.per_page)]
        _prev, _next = self.next_prev_links(int(page), len(_items), category, request)
        return jsonify(items=_items, next=_next, previous=_prev)


class NewsListView(MethodView):
    per_page = 20

    @staticmethod
    def next_prev_links(page, items_count, request):
        _base_url = f"{request.scheme}://{request.host}{request.path}"
        _prev_page = f"{_base_url}&page={page - 1}" if page > 1 else None
        _next_page = f"{_base_url}&page={page + 1}"
        if items_count == 0:
            _next_page = None
        return _prev_page, _next_page

    def get(self):
        page = request.args.get('page') or 1
        query = session.query(ParsedItem)
        _items = [{"data": json.loads(item.data), "created": item.created} for item in
                  query.order_by(ParsedItem.created.desc()).limit(self.per_page).offset((int(page) - 1) * self.per_page)]
        _prev, _next = self.next_prev_links(int(page), len(_items), request)
        return jsonify(items=_items, next=_next, previous=_prev)


# Create admin
admin = Admin(app, name='microblog', template_mode='bootstrap3', url="/admin/advert")
admin.add_view(ModelView(User, session))
admin.add_view(ModelView(Category, session))
admin.add_view(ModelView(ParserMap, session))
admin.add_view(ModelView(ParsedItem, session))
admin.add_view(ModelView(AdvertParserMap, session))
admin.add_view(ModelView(Link, session))
admin.add_view(AdvertModelView(Advert, session))

# API urls
app.add_url_rule('/adverts', view_func=AdvertListView.as_view('advert_list'))
app.add_url_rule('/news', view_func=NewsListView.as_view('news_list'))
