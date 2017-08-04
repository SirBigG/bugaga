# -*- coding: utf-8 -*-
from web.views.IndexView import IndexView


ROUTES = (
    ("GET", "/", IndexView),
)
