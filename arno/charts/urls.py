from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^api/(?P<filename>[0-9]+)/$', views.get_data, name='get_data'),
    url(r'^api/(?P<filename>[0-9]+)/group/(?P<group>[0-9]+)/$', views.get_data, name='get_data'),
    url(r'^api/(?P<filename>[0-9]+)/group/(?P<group>[0-9]+)/(?P<queries>.*)/$', views.get_data, name='get_data'),
    url(r'^api/records/from/(?P<starting>[A-Za-z0-9 :.-]+)/to/(?P<to>[A-Za-z0-9 :.-]+)/$', views.get_records,
        name='get_records_by_time'),
    url(r'^(?P<filename>[0-9]+)/$', views.chart, name='chart'),
    url(r'^(?P<filename>[0-9]+)/city/(?P<name>[A-Za-z0-9]+)/$', views.chart, name='chart'),
    url(r'^(?P<filename>[0-9]+)/group/(?P<group>[0-9]+)/$', views.chart, name='chart'),
    url(r'^(?P<filename>[0-9]+)/group/(?P<group>[0-9]+)/(?P<queries>.*)/$', views.chart, name='chart'),
    url(r'^migrate/(?P<filename>[0-9]+)/city/(?P<ftp_name>[A-Za-z0-9]+)/year/(?P<year>[0-9]+)/$', views.migrate,
        name='migrate'),
    url(r'^demo/$', views.csv_based_demo, name='demo'),
    url(r'^demo/(?P<solar_max>[0-9]+)/$', views.csv_based_demo, name='demo_plus'),
    url(r'^demo/(?P<solar_max>[0-9]+)/json/$', views.csv_based_demo_json, name='demo_json'),
]
