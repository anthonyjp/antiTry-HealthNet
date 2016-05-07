import datetime as dt

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from .models import *
from .utility.options import *

c = Client()

# Create a standard naming scheme so we can understand what you are doing -- Matt

# You don't need failure cases, your cases should test things that would be failures, if they fail the failure cases
# are never reached anyway. -- Matt
"""
The general Naming Scheme for test cases is as follows:
test_[user who is performing act]_[the action being performed]_[optional: user being acted upon]
    _[optional: the thing being acted upon]
Note: _success or _fail will be in all of the tests. The function names are intended to be read how they were written
      in the TestTracker.doc
e.g. test_doc_update_pat_med_info_success

All test cases involving a 'cancel' or a 'view' operation will be tested manually
"""


# create all the dictionaries for all the users
def create_patient_dict(email, password, user_type, name="The L Diablo", dob=dt.datetime.now(), gender=Gender.MALE, height1=7,
                        height2=11, height3=1, weight=100, hunits=Units.CUSTOMARY, wunits=Units.CUSTOMARY, secq=SecQ.Q1,
                        seca="testsec", insurance=INSURANCE_CHOICES[0][0], bloodtype=BloodType.O,
                        contact_name="Test Contact", contact_email="contact@c.com", contact_primary="516-123-4567",
                        contact_secondary='', contact_relationship=Relationship.OTHER, address_line_one="Blah",
                        address_line_two=None, address_city="Bleh", address_state="NY", address_zipcode="12345",
                        conditions=None):
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
        'address1': address_line_one,
        'address2': address_line_two,
        'address_city': address_city,
        'address_state': address_state,
        'address_zipcode': address_zipcode,
        'user_type': user_type,
        'conditions': conditions,
    }


def create_appt_dict(date='07/28/2016', time='12:00', doctor='John J Doe', patient='Anthony Perez',
                     location = 'Anthony'):
    return {
        'date': date,
        'time': time,
        'doctor': doctor,
        'patient': patient,
        'location': location,
    }


def create_admin_dict(email, password, user_type, name="Im An Admin", dob=dt.datetime.now(), gender=Gender.MALE, secq=SecQ.Q1,
                      seca="testsec", address_line_one="Blah", address_line_two=None, address_city="Bleh",
                      address_state="NY", address_zipcode="12345", is_sysadmin=False, hospital=None):
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
        'email': email,
        'password': password,
        'address1': address_line_one,
        'address2': address_line_two,
        'address_city': address_city,
        'address_state': address_state,
        'address_zipcode': address_zipcode,
        'is_sysadmin': is_sysadmin,
        'hospital': hospital,
        'user_type': user_type,
    }


def create_doct_dict(email, password, user_type, name="Im A Doctor", dob=dt.datetime.now(), gender=Gender.MALE, secq=SecQ.Q1,
                     seca="testsec", address_line_one="Blah", address_line_two=None, address_city="Bleh",
                     address_state="NY", address_zipcode="12345", hospitals=None):
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
        'email': email,
        'password': password,
        'address1': address_line_one,
        'address2': address_line_two,
        'address_city': address_city,
        'address_state': address_state,
        'address_zipcode': address_zipcode,
        'user_type': user_type,
        'hospitals': hospitals,
    }


def create_nurse_dict(email, password, user_type, name="Im A Nurse", dob=dt.datetime.now(), gender=Gender.MALE, secq=SecQ.Q1,
                      seca="testsec", address_line_one="Blah", address_line_two=None, address_city="Bleh",
                      address_state="NY", address_zipcode="12345", hospital=None):
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
        'email': email,
        'password': password,
        'address1': address_line_one,
        'address2': address_line_two,
        'address_city': address_city,
        'address_state': address_state,
        'address_zipcode': address_zipcode,
        'hospital': hospital,
        'user_type': user_type,
    }


def create_rx_dict(drug=None, patient='Anthony Perez', doctor='John J Doe', count=400, amount=444, refills=4,
                   time_range=None):
    return {
        'drug': drug,
        'patient': patient,
        'doctor': doctor,
        'count': count,
        'amount': amount,
        'refills': refills,
        'time_range': time_range,
    }


def create_admit_dict(reason=0, admission_time=None, hospital=None, doctor='John J Doe'):
    return {
        'reason': reason,
        'admission_time': admission_time,
        'hospital': hospital,
        'doctor': doctor,
    }


class RegistrationTest(TestCase):
    """
    All cases involving Patient registration and Staff Registration (Nurse or Doc)
    """
    # create hospital
    def setUp(self):
        hospital = Hospital(name="Matt", address="Matt", state="Ma", zipcode="06288")
        hospital.save()
    # patient registration cases
    def test_pat_reg_pat_and_user_exists(self):
        email = "test@test.com"
        passwd = 'qwerty123'
        user_type = "Patient"

        c.post(reverse('registry:register'), data=create_patient_dict(email, passwd, user_type))

        user = DjangoUser.objects.get(email=email)

        pat = Patient.objects.get(auth_user_id=user.id)
        self.assertIsInstance(pat, Patient, 'get_subclass did not return patient!')
        self.assertIsInstance(pat, User, 'get_subclass patient is not also user!')
        self.assertIsNotNone(pat.auth_user.username, 'Patient username not set properly!')

    # Note: ec = Emergency Contact
    # success cases
    def test_pat_reg_success_add_ec(self):
        pat = Patient.objects.get(email="test@test.com")
        contact = PatientContact.objects.get(contact_email="contacts@c.com")

        self.assertTrue(pat.contact_set.filter(contact_email=contact.contact_email).exists())

    # failure cases
    def test_pat_reg_fail_incomplete(self):
        email = "test2@test2.com"
        pw = None
        user_type = "Patient"

        c.post(reverse('registry:register'), data=create_patient_dict(email, pw, user_type))
        self.assertFalse(Patient.objects.filter(email=email).exists())


    # staff registration cases
    # Note: The admin registers the staff!
    # success case
    def test_admin_reg_staff_success(self):
        # admin info
        email_admin = "admin@admin.com"
        pw_admin = 'qwerty123'
        user_type_admin = "Admin"
        hospital = Hospital.objects.get(name='Matt')

        # doctor info
        email_doc = "doc@doc.com"
        pw_doc = "qwerty123"
        user_type_doc = "Doc"
        hospitals = Hospital.objects.get(name="Matt")

        # nurse info
        email_nurse = "nurse@nurse.com"
        pw_nurse = "qwerty123"
        user_type_nurse = "Nurse"
        # Shares hospital variable already made for admin info

        # can admin register doctor?
        c.post(reverse('registry:user_create'), data=create_doct_dict(email_doc, pw_doc, hospitals, user_type_doc))
        self.assertTrue(Doctor.objects.filter(email=email_doc).exists())
        # can admin register nurse?
        c.post(reverse('registry:user_create'), data=create_nurse_dict(email_nurse, pw_nurse, hospital, user_type_nurse))
        self.assertTrue(Nurse.objects.filter(email=email_nurse).exists())
        # can admin register admin?
        c.post(reverse('registry:user_create'), data=create_admin_dict(email_admin, pw_admin, hospital, user_type_admin))
        self.assertTrue(Administrator.objects.filter(email=email_admin).exists())


    # failure cases
    def test_admin_reg_staff_fail_incomplete(self):
        # admin info
        email_admin = None
        pw_admin = 'qwerty123'
        user_type_admin = "Admin"
        hospital = Hospital.objects.get(name='Matt')

        # doctor info
        email_doc = None
        pw_doc = "qwerty123"
        user_type_doc = "Doc"
        hospitals = Hospital.objects.get(name="Matt")

        # nurse info
        email_nurse = None
        pw_nurse = "qwerty123"
        user_type_nurse = "Nurse"
        # Shares hospital variable already made for admin info

        # can admin register doctor? Hopefully not!
        c.post(reverse('registry:user_create'), data=create_doct_dict(email_doc, pw_doc, hospitals, user_type_doc))
        self.assertFalse(Doctor.objects.filter(email=email_doc).exists())
        # can admin register nurse? Hopefully not!
        c.post(reverse('registry:user_create'), data=create_nurse_dict(email_nurse, pw_nurse, hospital, user_type_nurse))
        self.assertFalse(Nurse.objects.filter(email=email_nurse).exists())
        # can admin register admin? Hopefully not!
        c.post(reverse('registry:user_create'), data=create_admin_dict(email_admin, pw_admin, hospital, user_type_admin))
        self.assertFalse(Administrator.objects.filter(email=email_admin).exists())


class AppointmentTest(TestCase):
    """
    All things to do with Appointments
    Create, update, cancel, view
    Since doctor, nurse, and patient all create an appointment the same way, there only needs to be one general test
    case for all of them.
    """
    # create tests
    def test_user_create_pat_appt(self):
        c.post(reverse('registry:appt_create'), data=create_appt_dict())
        appt = Appointment.objects.filter(date='07/28/2016', time='12:00', doctor='John J Doe', patient='Anthony Perez',
                                          location='Anthony')
        self.assertTrue(appt.exists())

    # update tests
    def test_user_update_pat_appt(self):
        c.patch(reverse('registry:appt_edit'), data=create_appt_dict(date='07/30/2016'))
        appt = Appointment.objects.filter(date='07/30/2016', time='12:00', doctor='John J Doe', patient='Anthony Perez',
                                          location='Anthony')
        self.assertTrue(appt.exists())

    # cancel tests
    # Note: Nurses cannot cancel appointments
    def test_user_cancel_pat_appt(self):
        pass

    # MUST BE DONE MANUALLY
    # # view tests
    # # Note: Nurses cannot view appointment calendars
    # def test_doc_view_appnt_calendar(self):
    #     pass
    #
    # def test_pat_view_appnt_calendar(self):
    #     pass


# Merge PersonalInformation and MedicalInformation, all users can update their own information
class Information(TestCase):
    """
    Update user personal and/or medical information
    All users can edit their own information
    """
    # success case
    def test_user_update_info_success(self):

        pass

    # failure cases
    def test_user_update_info_fail_blank(self):
        pass

    # MANUALLY #
    # *** View Medical Information *** #
    # success cases; cannot fail
    def test_user_view_info_success(self):
        pass


# We've decided this will all be done manually; just have to check for file.
# class ExportInfo(TestCase):
#     """
#     Needs to deal with Success and Failure
#     """
#     # success case
#     def test_export_info_success(self):
#         pass
#
#     # failure cases
#     def test_export_info_fail_incorrect_sec_qs(self):
#         pass
#
#     def test_export_info_fail_clicks_no(self):
#         pass
#
#     def test_export_info_fail_cancel(self):
#         pass


class Prescription(TestCase):
    """
    Deals with adding and deleting prescriptions
    """

    def setUp(self):
        drug = Drug(name="The Lisa Special", providers="Lisa", side_effects="Insomnia", msds_link='www.google.com')
        drug.save()
        time_range_rx = TimeRange(start_time="2016-07-30 04:44", end_time="2016-08-30 04:44")
        time_range_rx.save()

    # *** Adding Prescriptions *** #
    # success case
    def test_doc_add_rx_success(self):
        c.post(reverse('registry:rx_create'), data=create_rx_dict(drug=Drug.objects.get(name="The Lisa Special"),
                                                                  time_range=TimeRange.objects.get
                                                                  (start_time="2016-07-30 04:44")))
        rx = Prescription.objects.get(drug=Drug.objects.get(name="The Lisa Special"))
        self.assertTrue(rx.exists())

    # failure cases
    def test_doc_add_rx_fail_incomplete(self):
        c.post(reverse('registry:rx_create'), data=create_rx_dict(time_range=TimeRange.objects.get
        (start_time="2016-07-30 04:44")))
        rx = Prescription.objects.get(drug=None)
        self.assertFalse(rx.exists())

    # MANUAL FOR NOW #
    # *** Deleting Prescriptions *** #
    # success case
    def test_doc_del_rx_success(self):
# c.delete(reverse('registry:rx_create'), data=)


# Not sure how to test this function as there is no view or model for it. Only an html confirmation page
# class Discharge(TestCase):
#
#     # success case
#     def test_doc_discharge_pat_success(self):
#         pass


class Admit(TestCase):
    """
    Nurse and doctor handle this the same way
    """

    def setUp(self):
        time_range_admit = TimeRange(start_time="2016-07-31 04:44", end_time=None)
        time_range_admit.save()

    # success cases
    def test_user_admit_pat(self):
        # Initially the end_date of admission_time is set to null
        c.post(reverse('registry:patient_admit'), data=create_admit_dict(admission_time=TimeRange.get
        (start_time="2016-07-31 04:44", end_time=None),
                                                                         hospital=Hospital.objects.get(name='Matt')))
        admit = AdmissionInfo.objects.get(end_time=None)
        self.assertTrue(admit.exists())

    # MANUALLY #
    # failure cases
    def test_user_admit_pat_fail_incorrect(self):
        pass


# Note: pm = Private Message
# Note: dne = recipient does not exist
class PrivateMessage(TestCase):

    """
    Deals with sending and viewing Private Messaging between
    patients, doctors, nurses, and admins.
    """

    # Only need to test User in general, not one for each user type
    # all use the same system, it's its own module.

    # *** Send Private Messages *** #
    # success cases
    def test_user_send_pm_success(self):
        pass

    # failure cases #
    # patient fails
    def test_user_send_pm_fail_dne(self):
        pass

    def test_user_send_pm_fail_incomplete(self):
        pass

    # cancel test; will be done manually
    def test_user_send_pm_fail_cancel(self):
        pass

    # MANUALLY #
    # *** View Private Messages *** #
    # success cases; no failures for viewing
    def test_user_view_pm_success(self):
        pass


class MedicalResults(TestCase):
    # *** Upload *** #
    # success case
    def test_doc_upload_med_res_success(self):
        pass

    # failure cases
    def test_doc_upload_med_res_fail_incomplete(self):
        pass

    # *** Release *** #
    # success case
    def test_doc_release_med_res_success(self):
        pass


class Transfer(TestCase):
    """
    Note: only a Doctor or an Administrator
    """

    # success case
    def test_user_transfer_pat_success(self):
        pass

    # failure case
    def test_user_transfer_pat_fail_same_hosp(self):
        pass

    def test_user_transfer_pat_fail_no_doctor(self):
        pass