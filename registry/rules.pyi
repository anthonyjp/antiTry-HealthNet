from typing import Union, Callable, TypeVar

from .models.user_models import User, Doctor, Nurse, Patient
from rules.predicates import predicate

T = TypeVar('T', User, Doctor, Nurse, Patient)

def is_user(user_type: T) -> predicate:
    ...

def is_doctor_of(doctor: Doctor, patient: Patient) -> bool:
    ...

def can_view_patient(user: Union[Doctor, Nurse], patient: Patient) -> bool:
    ...