
from django.conf.urls import url, include
from . import views


def uuid_url(fmt: str):
    return fmt.replace('{uuid}', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


app_name = 'registry'
urlpatterns = [
    # Simple Non-REST URLs
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^register$', views.register, name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.sign_out, name='logout'),
    url(r'^home$', views.home, name='home'),

    # TODO Convert
    url(r'^patient_admit/(?P<patient_uuid>.*)$', views.patient_admit, name='patient_admit'),
    url(r'^patient_discharge/(?P<patient_uuid>.*)$', views.patient_discharge, name='patient_discharge'),
    url(r'^patient_transfer_request/(?P<patient_uuid>.*)$', views.transfer,
        name='transfer_create'),
    url(r'^appt$', views.appt_create, name='appt_create'),
    url(r'^appt/(?P<pk>[0-9]+)$', views.appt_edit, name='appt_edit'),
    url(r'^appt/view/(?P<pk>[0-9]+)$', views.appt_view, name='appt_view'),
    url(r'^appt/(?P<pk>[0-9]+)/delete$', views.appt_delete, name='appt_delete'),
    url(r'^mc/(?P<patient_uuid>.*)$', views.mc_add, name='mc_add'),

    # User Related URLs
    url(uuid_url(r'^user/(?P<uuid>{uuid})/test'), views.medical_tests, name="tests"),
    url(uuid_url(r'^user/(?P<uuid>{uuid})$'), views.user, name='user'),
    url(r'^user', views.user, name='user_create'),
    url(uuid_url(r'^verify/(?P<uuid>{uuid})$'), views.user_verify, name='verify'),

    # RX Related URLs
    #url(r'^rx/(?P<pk>[0-9]+)$', views.rx_op, name='rx'),
    url(r'^rx/create/(?P<patient_uuid>.*)$', views.rx_create, name='rx_create'),
    url(r'^rx/delete/(?P<pk>[0-9]+)$', views.rx_delete, name='rx_delete'),

    # Message Related URLs
    url(uuid_url(r'^msg/(?P<uuid>{uuid})$'), views.msg, name='msg'),
    url(r'^msg$', views.msg, name='msg_create'),

    url(r'^logs/(?P<start>\d{4}-\d{2}-\d{2})/(?P<end>\d{4}-\d{2}-\d{2})$', views.logs, name='logs'),
    url(r'^stats$', views.get_time, name='time'),
    # Get the patient export info
    url(uuid_url(r'^export/(?P<patient_uuid>{uuid})$'), views.seq_check, name='export_patient_info'),
]
