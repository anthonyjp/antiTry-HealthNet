from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from django.http import HttpResponseNotFound, HttpResponse, Http404

from .forms import PatientRegisterForm, LoginForm, AppointmentSchedulingForm, PrescriptionCreation
from .forms import DeleteAppForm
from .forms import MessageCreation
#from .forms import PatientRegisterForm, LoginForm, AppointmentSchedulingForm, PrescriptionCreation,
#from .forms import DeleteAppForm
from .forms import *
from .models.user_models import Patient, User
from .models.info_models import Appointment, PatientContact
from .utility.models import TimeRange
from datetime import datetime, timedelta

import dateutil.parser
import rules
import json
import logging

from django.utils import timezone
# Create your views here.

activitylog = logging.getLogger('hn.activity')
requestlog = logging.getLogger('hn.request')
securitylog = logging.getLogger('hn.security')

@login_required(login_url='/login')
def pres_create(request):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    #next is where it goes if you cancel
    next = None
    if rules.test_rule('is_doctor',p):
        if request.method == "POST":
            form = PrescriptionCreation(request.POST, user=p)
            if form.is_valid():
                pres = form.save(commit=False)
                timeRange = TimeRange(
                    start_time=form.cleaned_data['start_time'],
                    end_time=form.cleaned_data['end_time']
                )
                if (timeRange.start_time < timeRange.end_time) and (timeRange.end_time > datetime.now()):
                        timeRange.save()
                        pres.time_range = timeRange
                        pres.doctor = p
                        pres.save()
                        return redirect('registry:calendar')
        else:
            form = PrescriptionCreation(user=p)

            if 'next' in request.GET:
                next = request.GET['next']
        return render(request, 'registry/pres_create.html', {'form': form,  'next_url': next})
    return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')



@login_required(login_url=reverse_lazy('registry:login'))
def appt_delete(request, pk):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    if rules.test_rule('is_nurse',p):
        return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    delete = get_object_or_404(Appointment, id=pk)
    if rules.test_rule('is_patient',p):
        if delete.patient.pk != p.pk:
            return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if rules.test_rule('is_doctor',p):
        if delete.doctor.pk != p.pk:
            return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteAppForm(request.POST, instance=delete)
        if form.is_valid():
            delete.delete()
            return redirect('registry:calendar')

    else:
        form = DeleteAppForm(instance=delete)

    template_vars = {'form': form}
    return render(request, 'registry/appt_delete.html', template_vars)

@login_required(login_url=reverse_lazy('registry:login'))
def pres_delete(request, pk):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    if rules.test_rule('is_nurse',p):
        return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    delete = get_object_or_404(Prescription, id=pk)
    if rules.test_rule('is_patient',p):
            return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if rules.test_rule('is_doctor',p):
        if delete.doctor.pk != p.pk:
            return HttpResponseNotFound('<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeletePresForm(request.POST, instance=delete)
        if form.is_valid():
            delete.delete()
            return redirect('registry:calendar')

    else:
        form = DeletePresForm(instance=delete)

    template_vars = {'form': form}
    return render(request, 'registry/pres_delete.html', template_vars)


def register(request):
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            username = '%s%s%s' % (patient.first_name, patient.middle_initial, patient.last_name)
            patient.auth_user = DjangoUser.objects.create_user(username, form.cleaned_data['email'],
                                                         form.cleaned_data['password'])
            patient.save()

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
    return render(request, 'registry/new.html', {'form': form})

@login_required(login_url='/login')
def appt_calendar(request):
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    return render(request, 'registry/calendar.html', {'appointments': hn_user.appointment_set.all()})


@login_required(login_url=reverse_lazy('registry:login'))
def appt_schedule(request):
    #next is where it goes if you cancel
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    next = None
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST, user=p)
        if form.is_valid():
            appointment = form.save(commit=False)
            list = Appointment.objects.filter(doctor__pk=appointment.doctor_id).filter(time__hour=appointment.time.hour).filter(time__day=appointment.time.day)
            patientlist = Appointment.objects.filter(patient__pk=appointment.patient_id).filter(time__hour=appointment.time.hour).filter(time__day=appointment.time.day)
            if not (list.exists() or patientlist.exists()):
                appointment.save()
                return redirect('registry:home')
    else:
        if 'start' in request.GET:
            form = AppointmentSchedulingForm(user=p, initial={'time': dateutil.parser.parse(request.GET['start'])})
        else:
            form = AppointmentSchedulingForm(user=p)

        if 'next' in request.GET:
            next = request.GET['next']

    return render(request, 'registry/appt_create.html', {'form': form, 'next_url': next})


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
            list = Appointment.objects.filter(doctor__pk=appointment.doctor_id).filter(time__hour=appointment.time.hour).filter(time__day=appointment.time.day)
            if initial_doctor == appointment.doctor.uuid:
                if initial_start_time == appointment.time:
                    appointment.save()
                    return redirect('registry:calendar')
                else:
                    if not (list.exists()):
                        appointment.save()
                        return redirect('registry:calendar')
            else:
                if not (list.exists()):
                    appointment.save()
                    return redirect('registry:calendar')
            error = "Appointment Edit Failure: Date/Time Conflicting"
    else:
        form = AppointmentEditForm(instance=appt, appt_id=pk)
    return render(request, 'registry/appt_edit.html', {'form': form, 'appt': initial_appointment, 'error': error})


def index(request):
    if request.user.is_authenticated():
        activitylog.info('[%s] %s', request.get_full_path(), str(request.user) if request.user.is_authenticated() else 'Anonymous')
        return redirect('registry:home')
    else:
        activitylog.info('[%s] %s', request.get_full_path(), str(request.user) if request.user.is_authenticated() else 'Anonymous')
        return render(request,'registry/landing.html')


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                django_login(request, user)
                return redirect(to=reverse('registry:home'))
    else:
        activitylog.info('[%s] %s', request.get_full_path(), str(request.user) if request.user.is_authenticated() else 'Anonymous')
        form = LoginForm()
    return render(request, 'registry/login.html', {'form': form})


@login_required(login_url=reverse_lazy('registry:login'))
def home(request):
    p = request.user.hn_user
    hn_user = User.objects.get_subclass(pk=p.pk)
    form = MessageCreation(request.POST)
    #pres_form = PrescriptionCreation(request.POST)

    if rules.test_rule('is_patient', hn_user):
        return render(request,
                      'registry/user_patient.html',
                      {'form': form,
                       'hn_user': hn_user,
                       'appointments': hn_user.appointment_set.all()
                       })

    elif rules.test_rule('is_doctor', hn_user):
        return render(request,
                      'registry/user_doctor.html',
                      {'form': form,
                      # 'pres_form': pres_form,
                       'hn_user': hn_user,
                       'appointments': hn_user.appointment_set.all()
                       })
    else:
        return render(request, 'registry/user_admin.html', {'hn_user': hn_user})


@login_required(login_url=reverse_lazy('registry:login'))
def home_updated(request, form):
    p = request.user.hn_user
    hn_user = User.objects.get_subclass(pk=p.pk)
    return render(request, 'registry/base_user.html', {'hn_user': hn_user})


@login_required(login_url=reverse_lazy('registry:login'))
def sign_out(request):
    if request.user:
        logout(request)

    return redirect(to=reverse('registry:index'))


from django.contrib.admin.models import LogEntry
# LogEntry Action flags meaning:
# ADDITION = 1
# CHANGE = 2
# DELETION = 3

def Logs():
    logs = LogEntry.objects.all()
    action_list = []
    for l in logs:
        time = str(l.action_time)
        user_id = str(l.user)
        object_repr = str(l.object_repr)
        action_flag = int(l.action_flag)
        log_action = ""
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
def Log_actions(request):
    fro = datetime.now() - timedelta(days=1)
    to = datetime.now()

    if 'from' in request.GET:
        fro = dateutil.parser.parse(request.GET['from'])
    if 'to' in request.GET:
        to = dateutil.parser.parse(request.GET['to'])

    return render(request, "registry/log.html", context={"action_list": Logs(), 'from': fro, 'to': to})


@login_required(login_url=reverse_lazy('registry:login'))
def view_user(request, pk):
    owner = User.objects.get_subclass(pk=pk)
    visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)

    return render(request, "registry/base_user.html", context={"hn_user": owner, "hn_visitor": visitor})


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
        return HttpResponse(json.dumps({'successes': successes, 'failures': failures}), content_type='application/json', status=200)
    else:
        return Http404('Not a Possible Action')

