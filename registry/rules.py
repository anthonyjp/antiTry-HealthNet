import rules
from rules.predicates import predicate

from registry.models import Patient, Doctor, Nurse, Administrator, User


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
def is_doctor_of(doctor, patient):
    return doctor.patient_set.filter(pk=patient.uuid).exists()

@predicate
def has_appointment(user, patient):
    return user.appointment_set.filter(patient__uuid__exact=patient.uuid).exists()


@predicate
def is_self(user_one, user_two):
    return user_one == user_two


@predicate
def time_gt(time1, time2):
    return time1 > time2


has_appointment_check = (is_doctor | is_nurse) & has_appointment
is_doctor_check = is_doctor & is_doctor_of

# Define Permissions

rules.add_perm('registry.create_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.update_appointment', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.cancel_appointment', is_patient | is_doctor)

rules.add_perm('registry.rx', is_doctor_check)

rules.add_perm('registry.patientinfo', is_patient)
rules.add_perm('registry.medinfo', is_doctor | is_nurse)

rules.add_perm('registry.prescriptions', is_doctor)

rules.add_perm('registry.admit', is_doctor | is_nurse)
rules.add_perm('registry.discharge', is_doctor)

rules.add_perm('registry.transfer_request', is_doctor | is_administrator)

rules.add_perm('registry.view_patient', is_patient | is_doctor | is_nurse)
rules.add_perm('registry.edit_patient', (is_patient & is_self) | is_nurse | is_doctor)

rules.add_perm('registry.inbox', is_self)

# Define Rules

rules.add_rule('is_patient', is_patient)
rules.add_rule('is_doctor', is_doctor)
rules.add_rule('is_nurse', is_nurse)
rules.add_rule('is_administrator', is_administrator)

rules.add_rule('can_view_patient', has_appointment_check | is_doctor_check | (is_patient & is_self))
rules.add_rule('time_gt', time_gt)