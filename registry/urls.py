
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^patient/new/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
]
