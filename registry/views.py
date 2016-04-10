import logging
import dateutil.parser
import django.utils.timezone as tz

from annoying.decorators import render_to, ajax_request
from django.contrib.admin.models import LogEntry
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, Http404
from django.shortcuts import redirect, get_object_or_404, render

from .forms import *
from .models import *
from .utility.models import *

activity_log = logging.getLogger('hn.activity')
request_log = logging.getLogger('hn.request')
security_log = logging.getLogger('hn.security')


def is_safe_request(method):
    return method == 'GET' or method == 'HEAD'


@render_to('registry/landing.html')
def index(request):
    if request.user.is_authenticated():
        activity_log.info('[%s] %s', request.get_full_path(),
                          str(request.user) if request.user.is_authenticated() else 'Anonymous')
        return redirect('registry:home')
    else:
        activity_log.info('[%s] %s', request.get_full_path(),
                          str(request.user) if request.user.is_authenticated() else 'Anonymous')
        return {}


@render_to('registry/login.html')
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                django_login(request, user)
                return redirect(to=reverse('registry:home'))
    else:
        activity_log.info('[%s] %s', request.get_full_path(),
                          str(request.user) if request.user.is_authenticated() else 'Anonymous')
        form = LoginForm()
    return {'form': form}


@login_required(login_url=reverse_lazy('registry:login'))
def home(request):
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    form = MessageCreation(request.POST)

    if rules.test_rule('is_patient', hn_user):
        return render(request,
                      'registry/users/user_patient.html',
                      {'form': form,
                       'hn_user': hn_user,
                       'appointments': hn_user.appointment_set.all()
                       }, context_instance=RequestContext(request))

    elif rules.test_rule('is_doctor', hn_user) or rules.test_rule('is_nurse', hn_user):
        patients = Patient.objects.filter(provider=hn_user)
        not_patients = Patient.objects.exclude(provider=hn_user)
        return render(request,
                      'registry/users/user_doctor.html',
                      {'form': form,
                       'hn_user': hn_user,
                       'appointments': hn_user.appointment_set.all(),
                       'not_patients': not_patients,
                       'patients': patients,
                       }, context_instance=RequestContext(request))
    else:
        return render(request,
                      'registry/users/user_admin.html',
                      {'hn_user': hn_user,
                       'form': form,
                       }, context_instance=RequestContext(request))


@render_to('registry/register.html')
def register(request):
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            username = '%s%s%s' % (patient.first_name, patient.middle_initial, patient.last_name)
            patient.auth_user = DjangoUser.objects.create_user(username, form.cleaned_data['email'],
                                                               form.cleaned_data['password'])
            patient.inbox = Inbox.objects.create()
            patient.save()
            patient.inbox.save()

            contact = PatientContact(
                    patient=patient,
                    relationship=form.cleaned_data['contact_relationship'],
                    contact_name=form.cleaned_data['contact_name'],
                    contact_primary=form.cleaned_data['contact_primary'],
                    contact_secondary=form.cleaned_data['contact_secondary'],
                    contact_email=form.cleaned_data['contact_email']
            )

            try:
                user = User.objects.get(auth_user__email=form.cleaned_data['contact_email'])
            except User.DoesNotExist:
                user = None

            if user is not None:
                contact.contact_user = user

            contact.save()
            patient.contact_set.add(contact)
            patient.save()

            return redirect('registry:index')
    else:
        form = PatientRegisterForm()
    return {'form': form}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_admit.html')
def patient_admit(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_nurse', user):
        if request.method == "POST":
            form = PatientAdmitForm(request.POST)
            if form.is_valid():
                admit_request = form.save(commit=False)
                timerange = TimeRange(
                        start_time=tz.now(),
                        end_time=None
                )
                timerange.save()
                admit_request.admission_time = timerange
                admit_request.patient = patient.__str__()
                admit_request.admitted_by = user.__str__()
                admit_request.save()
                patient.cur_hospital = admit_request.hospital
                patient.admission_status = admit_request
                patient.save()
                return redirect('registry:home')
        else:
            form = PatientAdmitForm()

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient}

    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_request.html')
def patient_transfer_request(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_administer', user):
        if request.method == "POST":
            form = PatientTransferForm(request.POST, user=user)
            if form.is_valid():
                transfer_request = form.save(commit=False)
                transfer_request.admitted_by = user.__str__()
                transfer_request.save()
                patient.transfer_status = transfer_request
                patient.save()
                return redirect('registry:home')
        else:
            form = PatientTransferForm(user=user)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient}
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_approve.html')
def patient_transfer_approve(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_administer', user):
        if request.method == "POST":
            form = ApproveTransferForm(request.POST, instance=patient.transfer_status)
            if form.is_valid():
                transfer_request = patient.transfer_status
                old_admit = patient.admission_status
                old_admit.admission_time.end_time = tz.now()
                old_admit.save()
                new_time = TimeRange(start_time=tz.now())
                new_time.save()
                new_admit = AdmissionInfo(patient=str(patient), admitted_by=transfer_request.admitted_by,
                                          hospital=transfer_request.hospital, reason=transfer_request.reason,
                                          admission_time=new_time)
                new_admit.save()
                patient.transfer_status = None
                patient.admission_status = None
                patient.admission_status = new_admit
                patient.save()
                return redirect('registry:home')
        else:
            form = ApproveTransferForm(instance=patient.transfer_status)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient}
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_delete.html')
def patient_transfer_delete(request, patient_uuid):
    p = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', p) or rules.test_rule('is_patient', p):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', p):
        if patient.provider.uuid != p.uuid:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteTransferForm(request.POST, instance=patient.transfer_status)
        if form.is_valid():
            patient.transfer_status = None
            patient.save()
            return redirect('registry:home')

    else:
        form = DeleteTransferForm(instance=patient.transfer_status)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_discharge.html')
def patient_discharge(request, patient_uuid):
    p = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', p) or rules.test_rule('is_patient', p):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', p):
        if patient.provider.uuid != p.uuid:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteAdmitForm(request.POST, instance=patient.admission_status)
        if form.is_valid():
            admit_info = patient.admission_status
            admit_info.admission_time.end_time = tz.now()
            admit_info.save()
            patient.admission_status = None
            patient.transfer_status = None
            patient.save()
            return redirect('registry:home')

    else:
        form = DeleteAdmitForm(instance=patient.admission_status)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_create.html')
def appt_schedule(request):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)

    next_location = None
    error = ""
    location_found = False
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST, user=p)
        if form.is_valid():
            appointment = form.save(commit=False)
            if rules.test_rule('time_gt', appointment.time, tz.now()):
                for hospital in appointment.doctor.hospitals.all():
                    if appointment.location == hospital:
                        location_found = True
                if location_found:
                    dlist = Appointment.objects.filter(
                        doctor__pk=appointment.doctor_id,
                        time__hour=appointment.time.hour,
                        time__day=appointment.time.day)
                    patientlist = Appointment.objects.filter(
                        patient__pk=appointment.patient_id,
                        time__hour=appointment.time.hour,
                        time__day=appointment.time.day)
                    if not (dlist.exists() or patientlist.exists()):
                        appointment.save()
                        return redirect('registry:home')
                    else:
                        error = "Appointment Error: DateTime conflict"
                else:
                    error = "Appointment Error: Doctor does not work in " + appointment.location.name
            else:
                error = "Appointment Error: That date and time has already happen."
    else:
        if 'start' in request.GET:
            form = AppointmentSchedulingForm(user=p, initial={'time': dateutil.parser.parse(request.GET['start'])})
        else:
            form = AppointmentSchedulingForm(user=p)

        if 'next' in request.GET:
            next_location = request.GET['next']

    return {'form': form, 'next_url': next_location, 'error': error}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_edit.html')
def appt_edit(request, pk):
    initial_appointment = get_object_or_404(Appointment, pk=pk)
    appt = get_object_or_404(Appointment, pk=pk)
    initial_start_time = appt.time
    initial_doctor = appt.doctor.uuid
    error = ""
    if request.method == "POST":
        form = AppointmentEditForm(request.POST, instance=appt, appt_id=pk)
        if form.is_valid():
            appointment = form.save(commit=False)
            appt_list = Appointment.objects.filter(doctor__pk=appointment.doctor_id).filter(
                    time__hour=appointment.time.hour).filter(time__day=appointment.time.day)
            if rules.test_rule('time_gt', appointment.time, tz.now()):
                if initial_doctor == appointment.doctor.uuid:
                    if initial_start_time == appointment.time:
                        appointment.save()
                        return redirect('registry:home')
                    else:
                        if not (appt_list.exists()):
                            appointment.save()
                            return redirect('registry:home')
                else:
                    if not (appt_list.exists()):
                        appointment.save()
                        return redirect('registry:home')
                error = "Appointment Edit Failure: Date/Time Conflicting"
            else:
                error = "Appointment Error: That date and time has already happen."
    else:
        form = AppointmentEditForm(instance=appt, appt_id=pk)
    return {'form': form, 'appt': initial_appointment, 'error': error}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_delete.html')
def appt_delete(request, pk):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    if rules.test_rule('is_nurse', p):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    delete = get_object_or_404(Appointment, id=pk)
    if rules.test_rule('is_patient', p):
        if delete.patient.pk != p.pk:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if rules.test_rule('is_doctor', p):
        if delete.doctor.pk != p.pk:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteAppForm(request.POST, instance=delete)
        if form.is_valid():
            delete.delete()
            return redirect('registry:home')

    else:
        form = DeleteAppForm(instance=delete)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/users/patient_viewing.html')
def patient_viewing(request, patient_uuid):
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)

    rxs = Prescription.objects.filter(doctor=hn_user, patient=patient)

    return {'hn_user': hn_user, 'patient': patient, 'rxs': rxs}


@login_required(login_url=reverse_lazy('registry:login'))
def sign_out(request):
    if request.user:
        logout(request)

    return redirect(to=reverse('registry:index'))


# LogEntry Action flags meaning:
# ADDITION = 1
# CHANGE = 2
# DELETION = 3


def get_log_data():
    logs = LogEntry.objects.all()
    action_list = []
    for l in logs:
        time = str(l.action_time)
        user_id = str(l.user)
        object_repr = str(l.object_repr)
        action_flag = int(l.action_flag)

        if action_flag == 1:
            log_action = user_id + " added a new " + object_repr + " at [" + time + "]."
            action_list.append(log_action)
        if action_flag == 2:
            log_action = user_id + " changed their " + object_repr + " at [" + time + "]."
            action_list.append(log_action)
        if action_flag == 3:
            log_action = user_id + " deleted their " + object_repr + " at [" + time + "]."
            action_list.append(log_action)

    return action_list


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/log.html')
def log_actions(request):
    fro = tz.now() - datetime.timedelta(days=1)
    to = tz.now()

    if 'from' in request.GET:
        fro = dateutil.parser.parse(request.GET['from'])
    if 'to' in request.GET:
        to = dateutil.parser.parse(request.GET['to'])

    return {"action_list": get_log_data(), 'from': fro, 'to': to}


@login_required(login_url=reverse_lazy('registry:login'))
def user(request, uuid):
    if request.method == 'POST':
        return update_user(request, uuid)
    elif is_safe_request(request.method):
        return view_user(request, uuid)


@render_to("registry/base/base_user.html")
def view_user(request, uuid):
    owner = User.objects.get_subclass(pk=uuid)
    visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)

    return {"hn_user": owner, "hn_visitor": visitor}


@ajax_request
def update_user(request, uuid):
    try:
        user = User.objects.get_subclass(pk=uuid)
    except User.DoesNotExist:
        return {'error': 'User does not exit'}

    successes = []
    failures = []
    for key, value in request.POST.items():
        if hasattr(user, key):
            setattr(user, key, value)
            successes.append(key)
        else:
            failures.append(key)

    user.save()
    return {'successes': successes, 'failures': failures}


@login_required(login_url=reverse_lazy('registry:login'))
def rx_op(request, pk):
    if request.method == 'GET':
        return rx_view(request, pk)
    elif request.method == 'PATCH':
        return rx_update(request, pk)
    elif request.method == 'DELETE':
        return rx_delete(request, pk)

    return Http404('Not a Possible Action')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/rx_create.html')
def rx_create(request, patient_uuid):
    error = ""
    p = User.objects.get_subclass(pk=request.user.hn_user.pk)

    # next_location is where it goes if you cancel
    # EXCUSE ME
    next_location = None

    if rules.test_rule('is_doctor', p):
        if request.method == "POST":
            form = PrescriptionCreation(request.POST, uuid=patient_uuid)
            if form.is_valid():
                rx = form.save(commit=False)
                timerange = TimeRange(
                        start_time=form.cleaned_data['start_time'],
                        end_time=form.cleaned_data['end_time']
                )
                if tz.now() < timerange.start_time < timerange.end_time:
                    timerange.save()
                    rx.time_range = timerange
                    rx.doctor = p
                    rx.save()
                    return redirect('registry:patient_viewing', patient_uuid=patient_uuid)
                else:
                    error = "Time Range is invalid"
        else:
            form = PrescriptionCreation(uuid=patient_uuid)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'error': error}

    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


def rx_view(request, pk):
    return Http404()


@ajax_request
def rx_update(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if hn_user.has_perm('registry.rx', rx.patient):
        return {}
    else:
        return {'error': 'Forbidden'}


@render_to('registry/data/rx_delete.html')
@ajax_request
def rx_delete(request, pk):
    rx = get_object_or_404(Prescription, id=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if not hn_user.has_perm('registry.rx', rx.patient) or rx.doctor.uuid != hn_user.uuid:
        return {'error': 'Forbidden'}

    rx.delete()

    return {}
