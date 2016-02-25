
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^/patient/new$', views.new, name='new'),
    url(r'^/detail/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
]
