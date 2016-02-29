from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404

from .forms import PatientRegisterForm, LoginForm
from .models.user_models import Patient
# Create your views here.


def register(request):
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('detail', pk=post.pk)
    else:
        form = PatientRegisterForm()
    return render(request, 'registry/new.html', {'form': form})


def detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'registry/patient.html', {'patient': patient})


def index(request):
    return render(request,'registry/landing.html')

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = LoginForm()
    return render(request, 'registry/login.html', {'form' : form})

def patient(request):
    return render(request, 'registry/patient.html')

def doc_nurse(request):
    return render(request, 'registry/doc_nurse.html')

def admin (request):
    return render(request, 'registry/admin.html')
