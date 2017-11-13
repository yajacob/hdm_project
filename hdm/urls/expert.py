# -*- coding: utf-8 -*-
from django.conf.urls import url
import hdm.views.expert as expert_views

urlpatterns = [
    url(r'^id/([a-z0-9]+)/$', expert_views.hdm_expert_login, name='expert_login'),
    url(r'^evaluate/$', expert_views.hdm_expert_evaluate, name='expert_evaluate'),
]
