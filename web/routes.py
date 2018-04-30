# -*- coding: utf-8 -*-
from web.views.IndexView import IndexView
from web.views.classifier_views import ClassifierListView
from web.views.auth_views import RegisterView, LoginView
from web.views.parser_views import PostsListView


ROUTES_GET = (
    ("/", IndexView),
    ("/api/p/classifiers/", ClassifierListView),
    ("/api/p/posts/", PostsListView),
)

ROUTES_POST = (
    ("/api/registration/", RegisterView),
    ("/api/login/", LoginView),
)
