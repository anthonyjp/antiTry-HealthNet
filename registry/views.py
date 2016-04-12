import json
import logging
from datetime import datetime, timedelta

import dateutil.parser
from django.contrib.admin.models import LogEntry
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render

from .forms import *
from .utility.models import TimeRange
from .models import *

activity_log = logging.getLogger('hn.activity')
request_log = logging.getLogger('hn.request')
security_log = logging.getLogger('hn.security')


@login_required(login_url=reverse_lazy('registry:login'))
def rx_create(request, patient_uuid):
    """
    The view for the prescription creation form
    Only doctors can view this
    :param request:
    :param patient_uuid: the patient uuid to limit the drop down patient menu
    :return: the page view
    """
    error = ""
    p = User.objects.get_subclass(pk=request.user.hn_user.pk)
    # next_location is where it goes if you cancel
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
                if datetime.now() < timerange.start_time < timerange.end_time:
                    timerange.save()
                    rx.time_range = timerange
                    rx.doctor = p
                    rx.save()
                    # This will log the fact that at each hospital the doctor worked at that this doctor
                    # had created a prescription
                    for hospital in rx.doctor.hospitals.all():
                        new_log_item = LogItem(
                            date=datetime.now(),
                            action=LogAction.PRES_CREATE,
                            user_action=p.uuid,
                            user_patient=rx.patient.uuid,
                            user_staff_affected=rx.doctor.uuid,
                            location=hospital
                        )
                        new_log_item.save()

                    return redirect('registry:patient_viewing', patient_uuid=patient_uuid)
                else:
                    error = "Time Range is invalid"
        else:
            form = PrescriptionCreation(uuid=patient_uuid)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return render(request, 'registry/data/rx_create.html', {'form': form, 'next_url': next_location,
                                                                'error': error})
    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
def rx_delete(request, pk):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    if rules.test_rule('is_nurse', p) or rules.test_rule('is_patient', p):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    # If the doctor viewing is not the writer of the prescription
    delete = get_object_or_404(Prescription, id=pk)
    if rules.test_rule('is_doctor', p):
        if delete.doctor.uuid != p.uuid:
            return HttpResponseNotFound(
                '<h1>You did not write this prescription.</h1><a href="/"> Return to home</a>')
    # Delete the prescription!
    if request.method == 'POST':
        form = DeletePresForm(request.POST, instance=delete)
        if form.is_valid():
            for hospital in delete.doctor.hospitals.all():
                new_log_item = LogItem(
                    date=datetime.now(),
                    action=LogAction.PRES_DELETE,
                    user_action=p.uuid,
                    user_patient=delete.patient.uuid,
                    user_staff_affected=delete.doctor.uuid,
                    location=hospital
                )
            new_log_item.save()
            delete.delete()
            return redirect('registry:home')

    else:
        form = DeletePresForm(instance=delete)

    template_vars = {'form': form}
    return render(request, 'registry/data/rx_delete.html', template_vars)


@login_required(login_url=reverse_lazy('registry:login'))
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
                        start_time=datetime.now(),
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
                new_log_item = LogItem(
                    date=datetime.now(),
                    action=LogAction.PA_ADMIT,
                    user_action=user.uuid,
                    user_patient=patient.uuid,
                    user_staff_affected=None,
                    location=admit_request.hospital
                )
                new_log_item.save()
                return redirect('registry:home')
        else:
            form = PatientAdmitForm()

            if 'next' in request.GET:
                next_location = request.GET['next']
        return render(request, 'registry/data/patient_admit.html', {'form': form, 'next_url': next_location,
                                                                    'patient': patient})
    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
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
                new_log_item = LogItem(
                    date=datetime.now(),
                    action=LogAction.PA_TRANSFER_REQUEST,
                    user_action=user.uuid,
                    user_patient=patient.uuid,
                    user_staff_affected=None,
                    location=transfer_request.hospital
                )
                new_log_item.save()
                return redirect('registry:home')
        else:
            form = PatientTransferForm(user=user)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return render(request, 'registry/data/patient_transfer_request.html', {'form': form, 'next_url': next_location,
                                                                               'patient': patient})
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
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
                old_admit.admission_time.end_time = datetime.now()
                old_admit.save()
                new_time = TimeRange(start_time=datetime.now())
                new_time.save()
                new_admit = AdmissionInfo(patient=patient.__str__(), admitted_by=transfer_request.admitted_by,
                                          hospital=transfer_request.hospital, reason=transfer_request.reason,
                                          admission_time=new_time)
                new_admit.save()
                patient.transfer_status = None
                patient.admission_status = None
                patient.admission_status = new_admit
                patient.save()
                new_log_item = LogItem(
                    date=datetime.now(),
                    action=LogAction.PA_TRANSFER_ACCEPTED,
                    user_action=user.uuid,
                    user_patient=patient.uuid,
                    user_staff_affected=None,
                    location=old_admit.hospital
                )
                new_log_item.save()
                second_log_item = LogItem(
                    date=datetime.now(),
                    action=LogAction.PA_TRANSFERRED,
                    user_action=user.uuid,
                    user_patient=patient.uuid,
                    user_staff_affected=None,
                    location=new_admit.hospital
                )
                second_log_item.save()
                return redirect('registry:home')
        else:
            form = ApproveTransferForm(instance=patient.transfer_status)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return render(request, 'registry/data/patient_transfer_approve.html', {'form': form, 'next_url': next_location,
                                                                               'patient': patient})
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
def patient_transfer_delete(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', user) or rules.test_rule('is_patient', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', user):
        if patient.provider.uuid != user.uuid:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteTransferForm(request.POST, instance=patient.transfer_status)
        if form.is_valid():
            patient.transfer_status = None
            patient.save()
            new_log_item = LogItem(
                date=datetime.now(),
                action=LogAction.PA_TRANSFER_DENIED,
                user_action=user.uuid,
                user_patient=patient.uuid,
                user_staff_affected=None,
                location=patient.cur_hospital
            )
            new_log_item.save()
            return redirect('registry:home')

    else:
        form = DeleteTransferForm(instance=patient.transfer_status)

    template_vars = {'form': form}
    return render(request, 'registry/data/patient_transfer_delete.html', template_vars)


@login_required(login_url=reverse_lazy('registry:login'))
def patient_discharge(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', user) or rules.test_rule('is_patient', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', user):
        if patient.provider.uuid != user.uuid:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteAdmitForm(request.POST, instance=patient.admission_status)
        if form.is_valid():
            admit_info = patient.admission_status
            admit_info.admission_time.end_time = datetime.now()
            admit_info.save()
            new_log_item = LogItem(
                date=datetime.now(),
                action=LogAction.PA_DISCHARGE,
                user_action=user.uuid,
                user_patient=patient.uuid,
                user_staff_affected=None,
                location=patient.cur_hospital
            )
            new_log_item.save()
            patient.admission_status = None
            patient.transfer_status = None
            patient.save()
            return redirect('registry:home')

    else:
        form = DeleteAdmitForm(instance=patient.admission_status)

    template_vars = {'form': form}
    return render(request, 'registry/data/patient_discharge.html', template_vars)


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
    return render(request, 'registry/register.html', {'form': form})


@login_required(login_url=reverse_lazy('registry:login'))
def appt_schedule(request):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    next_location = None
    error = ""
    location_found = False
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST, user=user)
        if form.is_valid():
            appointment = form.save(commit=False)
            if rules.test_rule('time_gt', appointment.time, datetime.now()):
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
                        new_log_item = LogItem(
                            date=datetime.now(),
                            action=LogAction.APPT_CREATE,
                            user_action=user.uuid,
                            user_patient=appointment.patient.uuid,
                            user_staff_affected=appointment.doctor.uuid,
                            location=appointment.location
                        )
                        new_log_item.save()
                        return redirect('registry:home')
                    else:
                        error = "Appointment Error: DateTime conflict"
                else:
                    error = "Appointment Error: Doctor does not work in " + appointment.location.name
            else:
                error = "Appointment Error: That date and time has already happen."
    else:
        if 'start' in request.GET:
            form = AppointmentSchedulingForm(user=user, initial={'time': dateutil.parser.parse(request.GET['start'])})
        else:
            form = AppointmentSchedulingForm(user=user)

        if 'next' in request.GET:
            next_location = request.GET['next']

    return render(request, 'registry/data/appt_create.html', {'form': form, 'next_url': next_location, 'error': error})


@login_required(login_url=reverse_lazy('registry:login'))
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
            if rules.test_rule('time_gt', appointment.time, datetime.now()):
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
    return render(request, 'registry/data/appt_edit.html', {'form': form, 'appt': initial_appointment, 'error': error})


@login_required(login_url=reverse_lazy('registry:login'))
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
    return render(request, 'registry/data/appt_delete.html', template_vars)


def index(request):
    if request.user.is_authenticated():
        activity_log.info('[%s] %s', request.get_full_path(),
                          str(request.user) if request.user.is_authenticated() else 'Anonymous')
        return redirect('registry:home')
    else:
        activity_log.info('[%s] %s', request.get_full_path(),
                          str(request.user) if request.user.is_authenticated() else 'Anonymous')
        return render(request, 'registry/landing.html')


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
    return render(request, 'registry/login.html', {'form': form})


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
                       })

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
                       })
    else:
        loglist = hn_user.cur_hospital.logItem.all()
        return render(request,
                      'registry/users/user_admin.html',
                      {'hn_user': hn_user,
                       'form': form,
                       'loglist': loglist
                       })


@login_required(login_url=reverse_lazy('registry:login'))
def patient_viewing(request, patient_uuid):
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # rx_form = PrescriptionCreation(request.POST, user=hn_user)
    rxs = Prescription.objects.filter(doctor=hn_user, patient=patient)
    for hospital in hn_user.hospitals.all():
        new_log_item = LogItem(
            date=datetime.now(),
            action=LogAction.PROFILE_VIEW,
            user_action=hn_user.uuid,
            user_patient=patient.uuid,
            user_staff_affected=None,
            location=hospital
        )
        new_log_item.save()
    return render(request,
                  'registry/users/patient_viewing.html',
                  {'hn_user': hn_user,
                   'patient': patient,
                   #'rx_form': rx_form,
                   'rxs': rxs})


# @login_required(login_url=reverse_lazy('registry:login'))
# def home_updated(request, form):
#     p = request.user.hn_user
#     hn_user = User.objects.get_subclass(pk=p.pk)
#     return render(request, 'registry/base_user.html', {'hn_user': hn_user})


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
def log_actions(request):
    fro = datetime.now() - timedelta(days=1)
    to = datetime.now()

    if 'from' in request.GET:
        fro = dateutil.parser.parse(request.GET['from'])
    if 'to' in request.GET:
        to = dateutil.parser.parse(request.GET['to'])

    return render(request, "registry/log.html", context={"action_list": get_log_data(), 'from': fro, 'to': to})


@login_required(login_url=reverse_lazy('registry:login'))
def view_user(request, pk):
    owner = User.objects.get_subclass(pk=pk)
    visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)

    return render(request, "registry/base/base_user.html",
                  context={"hn_user": owner, "hn_visitor": visitor})


@login_required(login_url=reverse_lazy('registry:login'))
def update_user(request, pk):
    try:
        user = User.objects.get_subclass(pk=pk)
    except User.DoesNotExist:
        user = None

    if user and request.method == 'POST':
        successes = []
        failures = []
        for key, value in request.POST.items():
            if hasattr(user, key):
                setattr(user, key, value)
                successes.append(key)
            else:
                failures.append(key)

        user.save()
        return HttpResponse(json.dumps({'successes': successes, 'failures': failures}), content_type='application/json',
                            status=200)
    else:
        return Http404('Not a Possible Action')
