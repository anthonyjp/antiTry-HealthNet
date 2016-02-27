import rules

from rules.predicates import predicate
from .models.user_models import Patient, Doctor, Nurse, Administrator, User


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

rules.add_perm('registry.create_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.update_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.cancel_appointment', is_patient | is_doctor)

rules.add_perm('registry.patientinfo', is_patient)
rules.add_perm('registry.medinfo', is_doctor | is_nurse)

rules.add_perm('registry.prescriptions', is_doctor)

rules.add_perm('registry.admit_patient', is_doctor | is_nurse)
rules.add_perm('registry.release_patient', is_doctor)

rules.add_perm('registry.view_patient', is_patient | is_doctor | is_nurse)


@predicate
def is_doctor_of(doctor, patient):
    return doctor.patient_set.filter(pk=patient.uuid).exists()


@predicate
def has_appointment(user, patient):
    return user.appointment_set.filter(patient__uuid__exact=patient.uuid).exists()


@predicate
def is_self(user_one, user_two):
    return user_one == user_two


has_appointment_check = (is_doctor | is_nurse) & has_appointment
is_doctor_check = is_doctor & is_doctor_of


rules.add_rule('can_view_patient', has_appointment_check | is_doctor_check | (is_patient & is_self))