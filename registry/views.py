from django.shortcuts import render
from django.shortcuts import redirect
from .forms import PatientRegisterForm
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