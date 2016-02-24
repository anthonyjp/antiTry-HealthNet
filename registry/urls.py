
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.new, name='new'),
    url(r'^(?P<pk>[0-9]+)/$', views.detail, name='detail'),
]
