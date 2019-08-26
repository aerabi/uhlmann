from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ftp/$', views.ftp_form, name='ftp'),
    url(r'^ftp/submit/$', views.ftp_form_submit, name='ftp'),
]
