# -*- coding: utf-8 -*-
from web.views.IndexView import IndexView
from web.views.classifier_views import ClassifierListView


ROUTES_GET = (
    ("/", IndexView),
    ("/api/classifiers/", ClassifierListView)
)
