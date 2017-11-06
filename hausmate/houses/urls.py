from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HouseListView.as_view(), name='house_list'),
    url(r'^create', views.HouseCreateView.as_view(), name='house_create'),
    url(r'^(?P<pk>[0-9]+)/$', views.HouseDetailView.as_view(), name='house_detail'),
    url(r'^(?P<pk>[0-9]+)/delete', views.HouseDeleteView.as_view(), name='house_delete'),
    url(r'^(?P<pk>[0-9]+)/update', views.HouseUpdateView.as_view(), name='house_update'),
    url(r'^(?P<house_id>[0-9]+)/roommates/create', views.RoommateCreateView.as_view(), name='roommate_create'),
    url(r'^(?P<house_id>[0-9]+)/bills/create', views.BillCreateView.as_view(), name='bill_create'),
    url(r'^(?P<house_id>[0-9]+)/bills/(?P<pk>[0-9]+)/$', views.BillDetailView.as_view(), name='bill_detail'),
    url(r'^payments/(?P<payment_id>[0-9]+)/pay', views.PaymentEventCreateView.as_view(), name='payment_event_create'),
]
