from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views as hdm_views
from .hdm_views.view_result import ViewResult as view_result

urlpatterns = [
    url(r'^$', hdm_views.hdm_home, name='hdm_home'),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^accounts/signup/$', hdm_views.signup, name='signup'),
    url(r'^accounts/password/$', hdm_views.change_password, name='change_password'),
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'registration/password_reset_form.html'}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,  name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^hdm/signup_home/$', hdm_views.signupHome, name='signup_home'),
    url(r'^hdm/model_manage/$', hdm_views.hdm_model_manage, name='hdm_manage_model'),
    url(r'^hdm/model_create/$', hdm_views.hdm_model_create, name='hdm_create_model'),
    url(r'^hdm/model_update/(\d+)/$', hdm_views.hdm_model_update, name='hdm_update_model'),
    url(r'^hdm/model_view/(\d*)/*$', hdm_views.hdm_model_view, name='hdm_view_model'),
    #url(r'^hdm/model_result/(\d+)/([\d,]*)$', view_result.hdm_model_result, name='hdm_model_result'),
    url(r'^hdm/model_result/(\d+)/([\d,]*)$', hdm_views.hdm_model_result, name='hdm_model_result'),
    url(r'^hdm/model_diagram/(\d+)/$', hdm_views.hdm_model_diagram, name='hdm_model_diagram'),
    url(r'^hdm/model_delete/([a-z0-9]+)/$', hdm_views.hdm_model_delete, name='hdm_model_delete'),
    url(r'^hdm/uploadcsvfile$', hdm_views.uploadCSVfile, name='upload_csv_file'),
    url(r'^hdm/expert/([a-z0-9]+)/$', hdm_views.hdm_expert_login, name='expert_login'),
    url(r'^hdm/exp_evaluate/$', hdm_views.hdm_expert_evaluate, name='expert_evaluate'),
    url(r'^hdm/exp_delete/(\d+)/([\d,]*)$', hdm_views.hdm_expert_delete, name='expert_delete'),
    url(r'^hdm/result_csv_download/(\d+)/(\d+)$', hdm_views.hdm_result_csv_download, name='result_csv_download'),
    url(r'^hdm/result_json_download/(\d+)/(\d+)$', hdm_views.hdm_result_json_download, name='result_json_download'),
    url(r'^help/manual/$', hdm_views.help_manual, name='help_manual'),
]
