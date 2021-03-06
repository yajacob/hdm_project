# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.http import request
from . import auth, hdm, expert, result, api, home
import hdm.views.home as home_views

urlpatterns = [
    url(r'^$', home_views.hdm_home, name='hdm_home'),
    url(r'^home/', include(home)),
    url(r'^api/', include(api)),
    url(r'^auth/', include(auth)),
    url(r'^hdm/', include(hdm)),
    url(r'^expert/', include(expert)),
    url(r'^result/', include(result)),
]
