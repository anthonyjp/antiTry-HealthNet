from django_enumfield import enum

INSURANCE_CHOICES = (
    ('Self Insured', 'Self Insured'),
    ('Blue Cross Blue Shield', 'Blue Cross Blue Shield'),
    ('Super Legit MI', 'Super Legit Medical Insurance'),
    ('Not Legit MI', 'Not Legit Medical Insurance')
)


class Relationship(enum.Enum):
    SPOUSE = 0
    MOTHER = 1
    FATHER = 2
    BROTHER = 3
    SISTER = 4
    FAMILY = 5
    FRIEND = 6
    OTHER = 7


class BloodType(enum.Enum):
    A = 0
    B = 1
    AB = 2
    O = 3
    UNKNOWN = 4

    labels = {
        UNKNOWN: '--'
    }


class Gender(enum.Enum):
    MALE = 0
    FEMALE = 1

    labels = {
        MALE: 'M',
        FEMALE: 'F'
    }


class SecurityQuestion(enum.Enum):
    Q1 = 0

    labels = {
        Q1: "What is your mother's maiden name?",
    }


class Units(enum.Enum):
    CUSTOMARY = 0
    METRIC = 1

    labels = {
        METRIC: 'Metric',
        CUSTOMARY: 'US Customary'
    }
