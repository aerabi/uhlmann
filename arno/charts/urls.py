from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<filename>[0-9]+)/$', views.chart, name='chart'),
    url(r'^(?P<filename>[0-9]+)/group/(?P<group>[0-9]+)/$', views.chart, name='chart'),
    url(r'^(?P<filename>[0-9]+)/group/(?P<group>[0-9]+)/positive/$', views.chart_positive, name='chart_positive'),
    url(r'^demo/$', views.csv_based_demo, name='demo'),
    url(r'^demo/(?P<solar_max>[0-9]+)/$', views.csv_based_demo, name='demo_plus'),
    url(r'^demo/(?P<solar_max>[0-9]+)/json/$', views.csv_based_demo_json, name='demo_json'),
]
