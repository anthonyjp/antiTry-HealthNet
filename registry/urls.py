
from django.conf.urls import url, include
from . import views

app_name = 'registry'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home$', views.index, name='home'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^appointment/$', views.apptSchedule, name='apptSchedule'),
    url(r'^admin/$', views.admin, name='admin')
]
