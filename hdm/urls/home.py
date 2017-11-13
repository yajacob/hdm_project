from django.conf.urls import url, include
from django.contrib import admin, auth
import hdm.views.home as home_views
import hdm.views.auth as auth_views

urlpatterns = [
    url(r'help/$', home_views.help_manual, name='help_manual'),
    url(r'^signup_home/$', auth_views.signupHome, name='signup_home'),
]
