# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import reverse_lazy
#from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (
    LoginView, LogoutView, 
    PasswordResetView, PasswordResetDoneView, 
    PasswordChangeView, PasswordChangeDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView,
)

#from hdm.views.auth import SignupView, SignupHomeView, ChangePassword
import hdm.views.auth as auth_views

urlpatterns = [
    #url(r'^login/$', auth_views.login, {'template_name': 'auth/login.html'}, name='login'),
    url(r'^login/$', LoginView.as_view(template_name='auth/login.html'), name='login'),
    #url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    #url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_form.html'}, name='password_reset'),
    url(r'password_reset/$', PasswordResetView.as_view(template_name='registration/password_reset_form.html'),  name='password_reset'),
    #url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.html'}, name='password_reset_done'),
    url(r'password_reset/done/$', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),  name='password_reset_done'),

    #url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    #url(r'^password_reset/done/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^password_reset/done/$', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    url(r'^signup/$', auth_views.signup, name='signup'),
    url(r'^change_password/$', auth_views.change_password, name='change_password'),
]
