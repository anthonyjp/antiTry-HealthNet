
from django.conf.urls import url, include
from . import views


def uuid_url(fmt: str):
    return fmt.replace('{uuid}', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


app_name = 'registry'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.sign_out, name='logout'),
    url(r'^home$', views.home, name='home'),
    url(r'^log$', views.log_actions, name='activity_log'),
    url(r'^appt$', views.appt_schedule, name='appt_create'),
    url(r'^appt/calendar$', views.appt_calendar, name='calendar'),
    url(r'^appt/(?P<pk>[0-9]+)$', views.appt_edit, name='appt_edit'),
    url(r'^appt/(?P<pk>[0-9]+)/delete$', views.appt_delete, name='appt_delete'),
    url(uuid_url(r'^user/{uuid}$'), views.view_user, name='user_view'),
    url(uuid_url(r'^user/{uuid}/update$'), views.update_user, name='user_update'),
    url(r'^rx/create$', views.rx_create, name='pres_create'),
    url(r'^rx/(?P<pk>[0-9]+)/delete/$', views.pres_delete, name='pres_delete'),
]
