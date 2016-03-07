from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout
from django.contrib.auth.models import User as DjangoUser
from .forms import PatientRegisterForm, LoginForm, AppointmentSchedulingForm
from .forms import DeleteAppForm
from .models.user_models import Patient, User, Doctor
from .models.info_models import Appointment, PatientContact
from django.contrib.auth.decorators import login_required
import rules
from django.utils import timezone
# Create your views here.

@login_required(login_url='/login')
def appt_delete(request, pk):
    delete = get_object_or_404(Appointment, id=pk)
    if request.method == 'POST':
        form = DeleteAppForm(request.POST, instance=delete)
        if form.is_valid():
            delete.delete()
            return redirect('registry:alist')

    else:
        form = DeleteAppForm(instance=delete)

    template_vars = {'form': form}
    return render(request, 'registry/appt_delete.html', template_vars)


@login_required(login_url='/login')
def alist(request):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    current_day = timezone.now().day
    current_month = timezone.now().month
    if (rules.test_rule('is_patient',p)):
        appointments = Appointment.objects.filter(patient__pk=p.pk, time__month=current_month).order_by('time')
    elif (rules.test_rule('is_doctor',p)):
        appointments = Appointment.objects.filter(doctor__pk=p.pk, time__month=current_month).order_by('time')
    else:
        appointments = Appointment.objects.filter(location__pk=p.hospital.pk, time__day=current_day).order_by('time')
        week = Appointment.objects.filter(location__pk=p.hospital.pk, time__day__range=[current_day, current_day+7]).order_by('time')
        return render(request, 'registry/alistnd.html',  {'appointments': appointments, 'hn_user': p, 'week': week})
    return render(request, 'registry/alist.html',  {'appointments': appointments, 'hn_user': p,})


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

            return redirect('registry:index')
    else:
        form = PatientRegisterForm()
    return render(request, 'registry/new.html', {'form': form})


@login_required(login_url='/login')
def apptSchedule(request):
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect('registry:alist')
    else:
        form = AppointmentSchedulingForm()
    return render(request, 'registry/appointment.html', {'form': form})

@login_required(login_url='/login')
def appt_edit(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST, instance=appt)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect('registry:alist')
    else:
        form = AppointmentSchedulingForm(instance=appt)
    return render(request, 'registry/edit_appointment.html', {'form': form})

@login_required(login_url='/login')
def detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'registry/patient.html', {'patient': patient})


def index(request):
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
        form = LoginForm()
    return render(request, 'registry/login.html', {'form': form})

@login_required(login_url='/login')
def home(request):
    p = request.user.hn_user
    hn_user = User.objects.get_subclass(pk=p.pk)
    return render(request, 'registry/base_user.html', {'hn_user': hn_user})

@login_required(login_url='/login')
def doc_nurse(request):
    return render(request, 'registry/doc_nurse.html')

@login_required(login_url='/login')
def admins (request):
    return render(request, 'registry/admin.html')

@login_required(login_url='/login')
def sign_out(request):
    if request.user:
        logout(request)

    return redirect(to=reverse('registry:index'))
