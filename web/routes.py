# -*- coding: utf-8 -*-
from web.views.IndexView import IndexView
from web.views.classifier_views import ClassifierListView
from web.views.auth_views import RegisterView, LoginView


ROUTES_GET = (
    ("/", IndexView),
    ("/api/classifiers/", ClassifierListView),
)

ROUTES_POST = (
    ("/api/registration/", RegisterView),
    ("/api/login/", LoginView),
)
