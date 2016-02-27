from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404

from .forms import PatientRegisterForm
from .models.user_models import Patient
# Create your views here.


def new(request):
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
    return render(request, 'registry/detail.html', {'patient': patient})


def index(request):
    return render(request,'registry/landing.html')

def register(request):
    return render(request, 'registry/register.html')

def login(request):
    return render(request, 'registry/Log_In.html')