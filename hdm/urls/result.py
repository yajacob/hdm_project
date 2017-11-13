# -*- coding: utf-8 -*-
from django.conf.urls import url
import hdm.views.result as result_views

urlpatterns = [
    url(r'^(\d+)/([\d,]*)$', result_views.hdm_model_result, name='hdm_model_result'),
    url(r'^csv_download/(\d+)/(\d+)$', result_views.hdm_result_csv_download, name='result_csv_download'),
    url(r'^json_download/(\d+)/(\d+)$', result_views.hdm_result_json_download, name='result_json_download'),
]
