from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout
from django.contrib.auth.models import User as DjangoUser
from .forms import PatientRegisterForm, LoginForm, AppointmentSchedulingForm, AppointmentForm
from .models.user_models import Patient, User
from .models.info_models import Appointment, PatientContact
# Create your views here.

def alist(request):
    appointments = Appointment.objects.filter().order_by('time')
    return render(request, 'registry/alist.html',  {'appointments': appointments})


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

#@login_required(login_url='/login')
def apptSchedule(request):
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect('registry:index')
    else:
        form = AppointmentSchedulingForm()
    return render(request, 'registry/appointment.html', {'form': form})

def apptUpdate(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect('registry/calender.html', pk=appointment.pk)
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'registry/edit_appointment.html', {'appointment': form})


def appt_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'registry/appointment_detail.html', {'appointment': appointment})

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

def home(request):
    patient =  request.user.hn_user
    return render(request, 'registry/base_user.html', {'patient': patient})

def doc_nurse(request):
    return render(request, 'registry/doc_nurse.html')

def admins (request):
    return render(request, 'registry/admin.html')


def sign_out(request):
    if request.user:
        logout(request)

    return redirect(to=reverse('registry:index'))
