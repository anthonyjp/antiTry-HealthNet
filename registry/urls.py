
from django.conf.urls import url, include
from . import views

app_name = 'registry'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.sign_out, name='logout'),
    url(r'^appointment/create$', views.appt_schedule, name='appt_create'),
    url(r'^home/$', views.home, name='home'),
    url(r'^appointment/calendar$', views.appt_calendar, name='calendar'),
    url(r'^appointment/update/(?P<pk>[0-9]+)/$', views.appt_edit, name='appt_edit'),
    url(r'^appointment/(?P<pk>[0-9]+)/delete/$', views.appt_delete, name='appt_delete'),
    url(r'^log$', views.Log_actions, name='activity_log'),
    url(r'^user/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', views.view_user, name='user_view'),
    url(r'^user/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/update/$', views.update_user, name='user_update'),

]
