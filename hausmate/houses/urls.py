from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HouseListView.as_view(), name='house_list'),
    url(r'^create', views.HouseCreateView.as_view(), name='house_create'),
    url(r'^(?P<pk>[0-9]+)/$', views.HouseDetailView.as_view(), name='house_detail'),
    url(r'^(?P<pk>[0-9]+)/delete', views.HouseDeleteView.as_view(), name='house_delete'),
    url(r'^(?P<pk>[0-9]+)/update', views.HouseUpdateView.as_view(), name='house_update'),
]
