# -*- coding: utf-8 -*-
from django.conf.urls import url
import hdm.views.api as api_views

urlpatterns = [
    url(r'^incon/$', api_views.get_inconsistency, name='get_inconsistency'),
]
