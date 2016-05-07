
import rules
from rules.predicates import predicate
from django.db.models import Q
from registry.models import Patient, Doctor, Nurse, Administrator, User, Appointment, Hospital


@predicate
def always_true(*args, **kwargs):
    return True


@predicate
def always_false(*args, **kwargs):
    return False


# Define All Predicates
def is_user(user_type):
    @predicate
    def validate(user):
        return isinstance(user, user_type)

    return validate

is_generic_user = is_user(User)
is_patient = is_user(Patient)
is_doctor = is_user(Doctor)
is_nurse = is_user(Nurse)
is_administrator = is_user(Administrator)


@predicate
def is_admit(patient):
    return patient.is_admitted()


@predicate
def is_doctor_of(doctor, patient):
    provider = doctor.providers.filter(pk=patient.uuid).exists()
    if patient.admission_status is not None:
        transfer_doctor = doctor.hospitals.filter(hospital=patient.admission_status.hospital).exists()
    else:
        transfer_doctor = False
    return provider or transfer_doctor


@predicate
def is_nurse_for(nurse, patient):
    admit_hospital = False
    if patient.admission_status is not None:
        if patient.admission_status.hospital == nurse.hospital:
            admit_hospital = True
    has_appt = patient.appointment_set.filter(location=nurse.hospital).exists()
    return admit_hospital or has_appt


@predicate
def is_admin_for(admin, patient):
    admit_hospital = False
    if patient.admission_status is not None:
        if patient.admission_status.hospital == admin.hospital:
            admit_hospital = True
    return admit_hospital


@predicate
def has_appointment(user, patient):
    return user.appointment_set.filter(patient__uuid__exact=patient.uuid).exists()


@predicate
def is_self(user_one, user_two):
    if not is_generic_user(user_one) or not is_generic_user(user_two):
        return False

    if not issubclass(type(user_one), User):
        user_one = User.objects.get_subclass(pk=user_one.pk)

    if not issubclass(type(user_two), User):
        user_two = User.objects.get_subclass(pk=user_two.pk)

    return user_one == user_two


@predicate
def time_gt(time1, time2):
    return time1 > time2


@predicate
def is_doctor_at(doctor, hospital):
    return doctor.hospitals.filter(self=hospital).exists()


@predicate
def an_profile(visitor, owner):
    return is_nurse(owner) | is_administrator(owner)


@predicate
def can_med_edit(visitor, owner):
    if not is_patient(owner):
        return False
    return is_doctor_check(visitor)


@predicate
def view_patient(visitor, owner):
    return is_patient(owner)

has_appointment_check = (is_doctor | is_nurse) & has_appointment
is_doctor_check = is_doctor & is_doctor_of
is_nurse_check = is_nurse & is_nurse_for
is_admit_patient = is_patient & is_admit
is_admin_check = is_administrator & is_admin_for

# Define Permissions

rules.add_perm('registry.is_admin_or_nurse', is_nurse | is_administrator)

rules.add_perm('registry.create_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.update_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.cancel_appointment', is_patient | is_doctor)

rules.add_perm('registry.rx', is_doctor_check)

rules.add_perm('registry.patient_admit', is_patient & is_admit)
rules.add_perm('registry.patientinfo', is_patient)
rules.add_perm('registry.medinfo', is_doctor | is_nurse)

rules.add_perm('registry.prescriptions', is_doctor_check)

rules.add_perm('registry.discharge', is_doctor)

rules.add_perm('registry.transfer_request', is_doctor | is_administrator)

rules.add_perm('registry.user.view.personal', always_true)
rules.add_perm('registry.user.edit.personal', is_self)
rules.add_perm('registry.user.view.medical', is_self | is_doctor | is_nurse)
rules.add_perm('registry.user.edit.medical', is_self | is_doctor | is_nurse)
rules.add_perm('registry.user.view.insurance', is_self | is_doctor | is_administrator)
rules.add_perm('registry.user.edit.insurance', is_self | is_administrator)
# rules.add_perm('registry.view_patient', is_doctor | is_nurse)
rules.add_perm('registry.edit_patient', (is_patient & is_self) | is_nurse_check | is_doctor)

rules.add_perm('registry.inbox', is_self)

rules.add_perm('registry.view_patient.admin', is_admin_for)
rules.add_perm('registry.view_patient.nurse', is_nurse_for)
rules.add_perm('registry.view_patient.doctor', is_doctor_of)
rules.add_perm('registry.view_patient.self', (is_patient & is_self))
rules.add_perm('registry.view_patient',
               view_patient & ((is_patient & is_self) | is_admin_check | is_nurse_check | is_doctor_check))
rules.add_perm('registry.view_an', an_profile)

# Define Rules

rules.add_rule('is_self', is_self)
rules.add_rule('is_patient', is_patient)
rules.add_rule('is_doctor', is_doctor)
rules.add_rule('is_nurse', is_nurse)
rules.add_rule('is_administrator', is_administrator)

rules.add_rule('can_view_patient', has_appointment_check | is_doctor_check | (is_patient & is_self))
rules.add_rule('time_gt', time_gt)