from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<filename>[0-9]+)/$', views.chart, name='chart'),
    url(r'^demo/$', views.demo, name='demo'),
    url(r'^demo/(?P<solar_max>[0-9]+)/$', views.demo, name='demo'),
]
