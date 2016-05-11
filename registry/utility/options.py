from django_enumfield import enum


class ExportOption(enum.Enum):
    CSV = 0
    PDF = 1

    labels = {
        CSV: 'CSV',
        PDF: 'PDF'
    }


class LogLevel(enum.Enum):
    VERBOSE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

    labels = {
        VERBOSE: 'VERBOSE',
        DEBUG: 'DEBUG',
        INFO: 'INFO',
        WARN: 'WARNING',
        ERROR: 'ERROR'
    }


class LogAction(enum.Enum):
    # Log Action Types
    APPT_CREATE = 0
    APPT_DELETE = 1
    APPT_EDIT = 2
    RX_CREATE = 3
    RX_DELETE = 4
    TEST_UPLOAD = 5
    TEST_RELEASE = 6
    PROFILE_VIEW = 7
    PA_ADMIT = 8
    PA_DISCHARGE = 9
    PA_TRANSFER_REQUEST = 10
    PA_TRANSFER_DENIED = 11
    PA_TRANSFER_ACCEPTED = 12
    PA_TRANSFERRED = 13
    MSG_SEND = 14
    ST_CREATE = 15  # Staff Create
    PAGE_ACCESS = 16
    UNKNOWN = 17
    GENERIC = 18
    USER_REGISTER = 19
    USER_LOGIN = 20
    PA_INFO = 21
    USER_LOGOUT = 22

    labels = {
        APPT_CREATE: "APPT NEW",
        APPT_DELETE: "APPT DEL.",
        APPT_EDIT: "APPT EDIT",
        RX_CREATE: "RX NEW",
        RX_DELETE: "RX DEL.",
        TEST_UPLOAD: "TEST UP.",
        TEST_RELEASE: "TEST REL.",
        PROFILE_VIEW: "PROF. VIEW",
        PA_ADMIT: "PA ADMIT",
        PA_DISCHARGE: "PA DISCH.",
        PA_TRANSFER_REQUEST: "PA -> REQ",
        PA_TRANSFER_DENIED: "PA -> DENY",
        PA_TRANSFER_ACCEPTED: "PA -> ACPT",
        PA_TRANSFERRED: "PA -> DONE",
        MSG_SEND: "MAIL",
        ST_CREATE: "STAFF NEW",
        UNKNOWN: "N/A",
        GENERIC: '---',
        USER_REGISTER: 'REGISTER',
        USER_LOGIN: 'LOGIN',
        PAGE_ACCESS: 'ACCESS',
        PA_INFO: 'INFO EXPORT',
        USER_LOGOUT: 'LOGOUT'
    }

    @classmethod
    def aliases(cls, *args, **kwargs):
        return ['actions']


class AdmitOptions(enum.Enum):
    # Admit options
    EMERGENCY = 0
    SURGERY = 1
    OBSERVANCE = 2
    UNKNOWN = 3

    labels = {
        EMERGENCY: 'Emergency',
        SURGERY: 'Surgery',
        OBSERVANCE: 'Observation',
        UNKNOWN: 'Unknown'
    }

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
    # Hospital Roles
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
        MALE: 'Male',
        FEMALE: 'Female'
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
