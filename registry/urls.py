
from django.conf.urls import url, include
from . import views


def uuid_url(fmt: str):
    return fmt.replace('{uuid}', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


app_name = 'registry'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
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
    url(r'^user$', views.list_user, name='list_user'),
    url(r'^message_creation', views.message_creation, name='message_creation'),
    url(uuid_url(r'^user/(?P<uuid>{uuid})$'), views.user, name='user'),
    url(uuid_url(r'^user/(?P<patient_uuid>{uuid})/rx$'), views.rx_create, name='rx_create'),
    url(uuid_url(r'^user/(?P<patient_uuid>{uuid})/rx/(?P<pk>[0-9]+)'), views.rx_delete, name='rx_delete'),
    url(uuid_url(r'^verify/(?P<uuid>{uuid})$'), views.verify_user, name='verify'),
    url(r'^mc/(?P<patient_uuid>.*)$', views.mc_add, name='mc_add'),
    url(r'^transfer$', views.create_transfer, name='transfer_create'),
    url(r'^transfer/(?P<pk>[0-9]+)$', views.transfers, name='transfer'),
    url(r'^rx/(?P<pk>[0-9]+)$', views.rx_op, name='rx'),
    url(r'^msg$', views.create_msg, name='msg_create'),
    url(uuid_url(r'^msg/(?P<uuid>{uuid})$'), views.msg, name='msg'),

]
