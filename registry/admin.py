from django.contrib import admin
from .models.user_models import *
from .models.info_models import *

# Register your models here.

admin.site.register(Patient)
admin.site.register(Administrator)
admin.site.register(Nurse)
admin.site.register(Doctor)
admin.site.register(AdmissionInfo)
admin.site.register(MedicalHistory)
admin.site.register(MedicalTest)
admin.site.register(MedicalData)
admin.site.register(Appointment)
admin.site.register(TimeRange)
admin.site.register(Hospital)
admin.site.register(Drug)
