from django_enumfield import enum


class LogAction(enum.Enum):
    # Log Action Types
    APPT_CREATE = 0
    APPT_DELETE = 1
    APPT_EDIT = 2
    PRES_CREATE = 3
    PRES_DELETE = 4
    TEST_UPLOAD = 5
    TEST_RELEASE = 6
    PROFILE_VIEW = 7
    PA_ADMIT = 8
    PA_DISCHARGE = 9
    PA_TRANSFER = 10
    MSG_SEND = 11
    ST_CREATE = 12


class AdmitOptions(enum.Enum):
    # Admit options
    EMERGENCY = 0
    SURGERY = 1
    OBSERVANCE = 2

# Insurance Choices
INSURANCE_CHOICES = (
    ('Self Insured', 'Self Insured'),
    ('Blue Cross Blue Shield', 'Blue Cross Blue Shield'),
    ('Super Legit MI', 'Super Legit Medical Insurance'),
    ('Not Legit MI', 'Not Legit Medical Insurance')
)


# Emergency Contact Relationships
class Relationship(enum.Enum):
    SPOUSE = 0
    MOTHER = 1
    FATHER = 2
    BROTHER = 3
    SISTER = 4
    FAMILY = 5
    FRIEND = 6
    OTHER = 7


# Blood Type
class BloodType(enum.Enum):
    A = 0
    B = 1
    AB = 2
    O = 3
    UNKNOWN = 4

    labels = {
        A: 'A',
        B: 'B',
        AB: 'AB',
        O: 'O',
        UNKNOWN: '--'
    }


class Role(enum.Enum):
    #Hospital Roles
    ADMIN = 0
    DOCTOR = 1
    NURSE = 2


    labels = {
        ADMIN: 'Admin',
        DOCTOR: 'Doctor',
        NURSE: 'Nurse'
    }


class Gender(enum.Enum):
    # Gender Choices
    MALE = 0
    FEMALE = 1

    labels = {
        MALE: 'M',
        FEMALE: 'F'
    }


# Security Questions for security purposes
class SecurityQuestion(enum.Enum):
    Q1 = 0

    labels = {
        Q1: "What is your mother's maiden name?",
    }


# Unit terms for which system of unit measurement
class Units(enum.Enum):
    CUSTOMARY = 0
    METRIC = 1

    labels = {
        METRIC: 'Metric',
        CUSTOMARY: 'US Customary'
    }
