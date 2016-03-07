
from django.conf.urls import url, include
from . import views

app_name = 'registry'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^appointment/create$', views.apptSchedule, name='appt_create'),
    url(r'^admins/$', views.admins, name='admins'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^patient/$', views.patient, name='patient'),
    url(r'^appointment/update/(?P<pk>[0-9]+)/$', views.apptUpdate, name='appt_update')
]
