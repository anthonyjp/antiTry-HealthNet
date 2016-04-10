
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
    url(r'^patient_admit/(?P<patient_uuid>.*)$', views.patient_admit, name='patient_admit'),
    url(r'^patient_discharge/(?P<patient_uuid>.*)$', views.patient_discharge, name='patient_discharge'),
    url(r'^patient_transfer_request/(?P<patient_uuid>.*)$', views.patient_transfer_request,
        name='patient_transfer_request'),
    url(r'^patient_transfer_approve/(?P<patient_uuid>.*)$', views.patient_transfer_approve,
        name='patient_transfer_approve'),
    url(r'^patient_transfer_delete/(?P<patient_uuid>.*)$', views.patient_transfer_delete,
        name='patient_transfer_delete'),
    url(r'^log$', views.log_actions, name='logs'),
    url(r'^appt$', views.appt_schedule, name='appt_create'),
    url(r'^appt/(?P<pk>[0-9]+)$', views.appt_edit, name='appt_edit'),
    url(r'^appt/(?P<pk>[0-9]+)/delete$', views.appt_delete, name='appt_delete'),
    url(r'^patient_viewing/(?P<patient_uuid>.*)$', views.patient_viewing, name='patient_viewing'),
    url(uuid_url(r'^user/{uuid}/update$'), views.update_user, name='user_update'),
    url(r'^rx/create/(?P<patient_uuid>.*)$', views.rx_create, name='rx_create'),
    url(r'^rx/(?P<pk>[0-9]+)/delete/$', views.rx_delete, name='rx_delete'),
]
