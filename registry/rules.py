
import rules
from rules.predicates import predicate
from django.db.models import Q
from registry.models import Patient, Doctor, Nurse, Administrator, User, Appointment, Hospital


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
        transfer_doctor = (patient.admission_status.doctor.uuid == doctor.uuid)
    else:
        transfer_doctor = False
    return provider or transfer_doctor

@predicate
def is_nurse_for(nurse, patient):
    # check only appts that
    appt_list = patient.appointment_set.filter(Q(is_future=False) | Q(is_today=True))
    return nurse.hospital == patient.pref_hospital or appt_list.filter(location=nurse.hospital).exists()

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

has_appointment_check = (is_doctor | is_nurse) & has_appointment
is_doctor_check = is_doctor & is_doctor_of
is_nurse_check = is_nurse & is_nurse_for
# Define Permissions

rules.add_perm('registry.is_admin_or_nurse', is_nurse | is_administrator)

rules.add_perm('registry.create_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.update_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.cancel_appointment', is_patient | is_doctor)

rules.add_perm('registry.rx', is_doctor_check)

rules.add_perm('registry.patient_admit', is_patient & is_admit)
rules.add_perm('registry.patientinfo', is_patient)
rules.add_perm('registry.medinfo', is_doctor | is_nurse)

rules.add_perm('registry.prescriptions', is_doctor)

rules.add_perm('registry.discharge', is_doctor)

rules.add_perm('registry.transfer_request', is_doctor | is_administrator)

rules.add_perm('registry.view_patient', is_doctor | is_nurse)
rules.add_perm('registry.edit_patient', (is_patient & is_self) | is_nurse_check | is_doctor)

rules.add_perm('registry.inbox', is_self)

# Define Rules

rules.add_rule('is_self', is_self)
rules.add_rule('is_patient', is_patient)
rules.add_rule('is_doctor', is_doctor)
rules.add_rule('is_nurse', is_nurse)
rules.add_rule('is_administrator', is_administrator)

rules.add_rule('can_view_patient', has_appointment_check | is_doctor_check | (is_patient & is_self))
rules.add_rule('time_gt', time_gt)