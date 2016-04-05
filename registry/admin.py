from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

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
admin.site.register(PatientContact)
admin.site.register(Contact)
admin.site.register(Hospital)
admin.site.register(Drug)
admin.site.register(Prescription)
admin.site.register(Inbox)

admin.site.unregister(DjangoUser)


class DjangoUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = DjangoUser


class DjangoUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = DjangoUser


class DjangoUserAdmin(UserAdmin):
    form = DjangoUserChangeForm
    add_form = DjangoUserCreationForm
    add_fieldsets = (
        (None, {
            'fields': ('email','username', 'password1', 'password2', 'first_name', 'last_name')
        }),
    )
    UserAdmin.fieldsets[0][1]['fields'] = ('email', 'username', 'password')

admin.site.register(DjangoUser, DjangoUserAdmin)
