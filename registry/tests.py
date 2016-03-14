from django.test import TestCase, Client

from django.core.urlresolvers import reverse
from .models.user_models import *

from .utility.options import *

import datetime as dt

c = Client()

# Create your tests here.


def create_patient_dict(email, password, name="The L Diablo", dob=dt.datetime.now(), gender=Gender.MALE, height1=7,
                        height2=11, height3=1, weight=100, hunits=Units.CUSTOMARY, wunits=Units.CUSTOMARY, secq=SecQ.Q1,
                        seca="testsec", insurance=INSURANCE_CHOICES[0][0], bloodtype=BloodType.O,
                        contact_name="Test Contact", contact_email="contact@c.com", contact_primary="516-123-4567",
                        contact_secondary='', contact_relationship=Relationship.OTHER):
    bits = name.split(sep=' ')
    if len(bits) < 2:
        raise ValueError('Name must have at least two parts, detected %d' % len(bits))
    elif len(bits) == 2:
        fname = bits[0]
        lname = bits[1]
        minitial = ''
    else:
        fname = bits[0]
        minitial = bits[1]
        lname = bits[2]

    return {
        'first_name': fname,
        'middle_initial': minitial,
        'last_name': lname,
        'date_of_birth': dob.strftime('%m/%d/%Y'),
        'gender': gender,
        'security_question': secq,
        'security_answer': seca,
        'height_0': hunits,
        'height_1': height1,
        'height_2': height2,
        'height_3': height3,
        'weight_0': wunits,
        'weight_1': weight,
        'insurance': insurance,
        'blood_type': bloodtype,
        'email': email,
        'password': password,
        'contact_name': contact_name,
        'contact_email': contact_email,
        'contact_primary': contact_primary,
        'contact_secondary': contact_secondary,
        'contact_relationship': contact_relationship,
    }


class PatientTest(TestCase):
    def setUp(self):
        doctor = Doctor(first_name="Sir", last_name="No", date_of_birth=dt.date(1985, 5, 29), gender=Gender.MALE, security_question=SecQ.Q1, security_answer="YEP")
        doctor.auth_user = DjangoUser.objects.create_user(username="DoctorNo", email="doc@doc.com", password="qwerty123")
        doctor.save()

    def test_patient_registration(self):
        email = "test@test.com"
        passwd = 'qwerty123'

        c.post(reverse('registry:register'), data=create_patient_dict(email, passwd))

        user = DjangoUser.objects.get(email=email)

        pat = Patient.objects.get(auth_user_id=user.id)
        self.assertIsInstance(pat, Patient, 'get_subclass did not return patient!')
        self.assertIsInstance(pat, User, 'get_subclass patient is not also user!')
        self.assertIsNotNone(pat.auth_user.username, 'Patient username not set properly!')

