# -*- coding: utf-8 -*-
from web.views.IndexView import IndexView, ClassifierListView


ROUTES_GET = (
    ("/", IndexView),
    ("/api/classifiers/", ClassifierListView)
)
