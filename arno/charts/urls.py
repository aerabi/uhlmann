from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<filename>[0-9]+)/$', views.chart, name='chart'),
]