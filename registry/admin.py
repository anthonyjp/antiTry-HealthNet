from django.contrib import admin
from .models.user_models import Patient
from .models.data_models import Hospital

# Register your models here.

admin.site.register(Patient)
admin.site.register(Hospital)