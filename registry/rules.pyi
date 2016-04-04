from typing import Union, TypeVar

from rules.predicates import predicate

from registry.models import User, Doctor, Nurse, Patient

T = TypeVar('T', User)

def is_user(user_type: T) -> predicate:
    ...

def is_doctor_of(doctor: Doctor, patient: Patient) -> bool:
    ...

def can_view_patient(user: Union[Doctor, Nurse], patient: Patient) -> bool:
    ...