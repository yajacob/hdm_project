# -*- coding: utf-8 -*-
from django.conf.urls import url
import hdm.views.hdm as hdm_views

# HDM management of the models
urlpatterns = [
    #url(r'signup_home/$', hdm_views.signupHome, name='signup_home'),
    url(r'model_manage/$', hdm_views.hdm_model_manage, name='hdm_manage_model'),
    url(r'model_create/$', hdm_views.hdm_model_create, name='hdm_create_model'),
    url(r'model_update/(\d+)/$', hdm_views.hdm_model_update, name='hdm_update_model'),
    url(r'model_view/(\d*)/*$', hdm_views.hdm_model_view, name='hdm_view_model'),
    url(r'model_diagram/(\d+)/$', hdm_views.hdm_model_diagram, name='hdm_model_diagram'),
    url(r'model_delete/([a-z0-9]+)/$', hdm_views.hdm_model_delete, name='hdm_model_delete'),
    url(r'uploadcsvfile$', hdm_views.uploadCSVfile, name='upload_csv_file'),
]
