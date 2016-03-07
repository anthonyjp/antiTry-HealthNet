
from django.conf.urls import url, include
from . import views

app_name = 'registry'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.sign_out, name='logout'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^appointment/create$', views.apptSchedule, name='appt_create'),
    url(r'^admins/$', views.admins, name='admins'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^home/$', views.home, name='home'),
    url(r'^appointment/update/(?P<pk>[0-9]+)/$', views.apptUpdate, name='appt_update'),
    url(r'^appointment$', views.alist, name='alist'),
    url(r'^appointment/(?P<pk>[0-9]+)/delete/$', views.appt_delete, name='appt_delete'),
]
