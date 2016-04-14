import datetime as dt

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from .utility.options import *

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


class RegistrationTest(TestCase):
    """
    All cases involving Patient registration, Unknown Patient Registration
    Staff Registration (Nurse or Doc)
    """
    # patient registration cases
    def setUp(self):
        doctor = Doctor(first_name="Sir", last_name="No", date_of_birth=dt.date(1985, 5, 29), gender=Gender.MALE,
                        security_question=SecQ.Q1, security_answer="YEP")
        doctor.auth_user = DjangoUser.objects.create_user(username="DoctorNo", email="doc@doc.com", password="qwerty123")
        doctor.save()

    def test_pat_reg_pat_and_user_exist(self):
        email = "test@test.com"
        passwd = 'qwerty123'

        c.post(reverse('registry:register'), data=create_patient_dict(email, passwd))

        user = DjangoUser.objects.get(email=email)

        pat = Patient.objects.get(auth_user_id=user.id)
        self.assertIsInstance(pat, Patient, 'get_subclass did not return patient!')
        self.assertIsInstance(pat, User, 'get_subclass patient is not also user!')
        self.assertIsNotNone(pat.auth_user.username, 'Patient username not set properly!')

    ### Note: ec = Emergency Contact
    # success cases
    def test_pat_reg_succes_add_ec(self):
        pass

    def test_pat_reg_success_ec_dropdown(self):
        pass

    # failure cases
    def test_pat_reg_fail_incomplete(self):
        pass

    def test_pat_reg_fail_cancel(self):
        pass

    # unknown patient registration cases
    # success case
    def test_unknown_pat_reg_success(self):
        # pick case 42 or 43, doesn't matter
        pass

    # failure case
    def test_unknown_pat_reg_fail_cancel(self):
        pass

    # staff registration cases
    # Note: The admin registers the staff!
    # success case
    def test_staff_reg_success(self):
        pass

    # failure cases
    def test_staff_reg_fail_incomplete(self):
        pass

    def test_staff_reg_fail_cancel(self):
        pass


class AppointmentTest(TestCase):
    """
    All things to do with Appointments
    Create, update, cancel, view
    """
    # create tests
    # for all these methods include success, failure due to insufficient info, cancel, and time conflict
    def test_doc_create_pat_appnt(self):
        pass

    def test_nurse_create_pat_appnt(self):
        pass

    def test_pat_create_pat_appnt(self):
        pass

    # update tests
    def test_doc_update_pat_appnt(self):
        pass

    def test_nurse_update_pat_appnt(self):
        pass

    def test_pat_update_pat_appnt(self):
        pass

    # cancel tests
    # Note: Nurses cannot cancel appointments
    def test_doc_cancel_pat_appnt(self):
        pass

    def test_pat_cancel_pat_appnt(self):
        pass

    # view tests
    # Note: Nurses cannot view appointment calendars
    def test_doc_view_appnt_calendar(self):
        pass

    def test_pat_view_appnt_calendar(self):
        pass


class PersonalInformation(TestCase):
    """
    Update patient personal information
    """
    # success case
    def test_pat_update_info_success(self):
        pass

    # failure cases
    def test_pat_update_info_fail_clear_field(self):
        pass

    def test_pat_update_info_fail_cancel(self):
        pass

class MedicalInformation(TestCase):
    """
    Deals with updating and viewing medical information
    """
    # *** Update Medical Information *** #
    # success cases
    def test_doc_update_pat_med_info_success(self):
        pass
    def test_nurse_update_pat_med_info_success(self):
        pass

    # failure cases
    def test_doc_update_pat_med_info_fail_clear_field(self):
        pass

    def test_doc_update_pat_med_info_cancel(self):
        pass

    def test_nurse_update_pat_med_info_fail_clear_field(self):
        pass

    def test_nurse_update_pat_med_info_cancel(self):
        pass

    # *** View Medical Information *** #
    # success cases; cannot fail
    def test_doc_view_pat_med_info_success(self):
        pass

    def test_nurse_view_pat_med_info_success(self):
        pass


class ActivityLogStats(TestCase):
    """
    Admin performs these operations
    Needs to deal with Success and Failure
    """
    # success cases
    def view_activity_log_success(self):
        pass

    def view_stats_success(self):
        pass

    # failure cases
    def view_activity_log_fail(self):
        pass

    def view_stats_fail(self):
        pass


class ExportInfo(TestCase):
    """
    Needs to deal with Success and Failure
    """
    # success case
    def test_export_info_success(self):
        pass

    # failure cases
    def test_export_info_fail_incorrect_sec_qs(self):
        pass

    def test_export_info_fail_clicks_no(self):
        pass

    def test_export_info_fail_cancel(self):
        pass


class Prescription(TestCase):
    """
    Deals with adding and deleting prescriptions
    """
    # *** Adding Prescriptions *** #
    # success case
    def test_doc_add_rx_success(self):
        pass

    # failure cases
    def test_doc_add_rx_fail_incomplete(self):
        pass

    def test_doc_add_rx_fail_cancel(self):
        pass

    # *** Deleting Prescriptions *** #
    # success case
    def test_doc_del_rx_success(self):
        pass

    # failure case
    def test_doc_del_rx_cancel(self):
        pass


### Need to add admin capable of doing this as well?
### Test tracker doesn't plan for this though
class Discharge(TestCase):

    # success case
    def test_doc_discharge_pat_success(self):
        pass

    # failure cases
    def test_doc_discharge_pat_fail_cancel(self):
        pass

class Admit(TestCase):

    # success cases
    def test_doc_admit_pat(self):
        pass

    def test_nurse_admit_pat(self):
        pass

    # failure cases
    def test_doc_admit_pat_fail_incorrect(self):
        pass

    def test_doc_admit_pat_fail_cancel(self):
        pass

    def test_nurse_admit_pat_fail_incorrect(self):
        pass

    def test_nurse_admit_pat_fail_cancel(self):
        pass


### Note: pm = Private Message
### Note: dne = recepient does not exist
class PrivateMessage(TestCase):

    """
    Deals with sending and viewing Private Messaging between
    patients, doctors, nurses, and admins.
    """

    # *** Send Private Messages *** #
    # success cases
    def test_pat_send_pm_success(self):
        pass

    def test_doc_send_pm_success(self):
        pass

    def test_nurse_send_pm_success(self):
        pass

    def test_admin_send_pm_success(self):
        pass

    # failure cases #
    # patient fails
    def test_pat_send_pm_fail_dne(self):
        pass

    def test_pat_send_pm_fail_incomplete(self):
        pass

    def test_pat_send_pm_fail_cancel(self):
        pass

    # doctor fails
    def test_doc_send_pm_fail_dne(self):
        pass

    def test_doc_send_pm_fail_incomplete(self):
        pass

    def test_doc_send_pm_fail_cancel(self):
        pass

    # nurse fails
    def test_nurse_send_pm_fail_dne(self):
        pass

    def test_nurse_send_pm_fail_incomplete(self):
        pass

    def test_nurse_send_pm_fail_cancel(self):
        pass

    # admin fails
    def test_admin_send_pm_fail_dne(self):
        pass

    def test_admin_send_pm_fail_incomplete(self):
        pass

    def test_admin_send_pm_fail_cancel(self):
        pass

    # *** View Private Messages *** #
    # success cases; no failures for viewing
    def test_pat_view_pm_success(self):
        pass

    def test_doc_view_pm_success(self):
        pass

    def test_nurse_view_pm_success(self):
        pass

    def test_admin_view_pm_success(self):
        pass

class MedicalResults(TestCase):
    # *** Upload *** #
    # success case
    def test_doc_upload_med_res_success(self):
        pass

    # failure cases
    def test_doc_upload_med_res_fail_incomplete(self):
        pass
    def test_doc_upload_med_res_fail_cancel(self):
        pass

    # *** Release *** #
    # success case
    def test_doc_release_med_res__success(self):
        pass

    # failure case
    def test_doc_release_med_res_fail_cancel(self):
        pass

class Transfer(TestCase):
    # success case
    def test_doc_transfer_pat_success(self):
        pass
    def test_admin_transfer_pat_success(self):
        pass

    # failure case
    def test_doc_transfer_pat_fail_same_hosp(self):
        pass
    def test_doc_transfer_pat_fail_no_doctor(self):
        pass
    def test_admin_transfer_pat_fail_same_hosp(self):
        pass
    def test_admin_transfer_pat_fail_no_doctor(self):
        pass