import dateutil.parser
import django.utils.timezone as tz

from annoying.decorators import render_to, ajax_request
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, Http404, QueryDict
from django.shortcuts import redirect, get_object_or_404, render
from easy_pdf.rendering import render_to_pdf, render_to_pdf_response
from ipware.ip import get_real_ip, get_ip

from .forms import *
from .models import *
from .utility.models import *
from .utility.logging import *
from .utility.viewutils import *

logger = HNLogger()

@render_to('registry/landing.html')
def index(request):
    anonymous = get_real_ip(request)
    if anonymous is None:
        anonymous = get_ip(request)
    if anonymous is None:
        anonymous = "Anonymous"

    logger.info(request, repr(request.user.hn_user) if request.user.is_authenticated() else str(anonymous),
                action=LogAction.PAGE_ACCESS)

    if request.user.is_authenticated():
        return redirect('registry:home')
    else:
        return {}


@render_to('registry/about.html')
def about(request):
    """
    The view for the about page
    """
    def create_dev(name, role, desc, *links, img=static('registry/img/logo.png')):
        real_links = []
        for l in links:
            real_links.append({'url': l[0], 'text': l[1] if len(l) > 1 and l[1] else l[0]})

        return {'name': name, 'role': role, 'desc': desc, 'img': img, 'links': real_links}

    return {'aboutus': [
        create_dev('Matthew Crocco', 'Development Coordinator', ('https://github.com/Matt529', 'Github')),
        create_dev('Lisa Ni', 'Requirements Coordinator', 'Contact Information'),
        create_dev('Anthony Perez', 'Quality Assurance Coordinator', 'Contact Information'),
        create_dev('Alice Fischer', 'Team Coordinator', 'Contact Information'),
        create_dev('Kyle Scagnelli', 'Test Coordinator', 'Contact Information')
    ]}


@render_to('registry/login.html')
def login(request):
    """
    The view for the login page which displays the form for login
    :param request:
    :return:
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                django_login(request, user)
                logger.action(request, LogAction.USER_LOGIN, '{name} has logged in!', name=str(user.hn_user))
                messages.add_message(request, messages.SUCCESS, 'Successfully Logged In.')
                return redirect(to=reverse('registry:home'))
        else:
            messages.add_message(request, messages.ERROR, 'Invalid Email or Password. Please Try Again.')
            form = LoginForm()
            return {'form': form}
    else:
        form = LoginForm()
    return {'form': form}


@login_required(login_url=reverse_lazy('registry:login'))
def sign_out(request):
    """
    The view for logging out
    :param request:
    :return:
    """
    if request.user:
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Successfully Logged Out.')
    return redirect(to=reverse('registry:index'))


@login_required(login_url=reverse_lazy('registry:login'))
def home(request):
    """
    The view for viewing the home page.
    For a logined in user, it will show the profile page of the logged in user
    :param request:
    :return:
    """
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    form = MessageCreation(request.POST)
    inbox = hn_user.inbox.messages.filter(receiver=hn_user).order_by('-date')

    if rules.test_rule('is_patient', hn_user):
        medical_history = MedicalHistory.objects.filter(patient=hn_user).all()
        medical_tests = MedicalTest.objects.filter(patient=hn_user).all()
        return render(request,
                      'registry/users/user_patient.html',
                      {'form': form,
                       'hn_owner': hn_user,
                       'hn_visitor': hn_user,
                       'inbox': inbox,
                       'appointments': hn_user.appointment_set.all(),
                       'medical_conditions': hn_user.conditions.all(),
                       'medical_history': medical_history,
                       'medical_tests': medical_tests,
                       }, context_instance=RequestContext(request))

    elif rules.test_rule('is_doctor', hn_user):
        patients_list = Patient.objects.filter(provider=hn_user)
        for hos in hn_user.hospitals.all():
            patients_list = patients_list or Patient.objects.filter(admission_status__isnull=False,
                                                                    admission_status__hospital=hos)
        patients_transfer = Patient.objects.filter(admission_status__isnull=False)
        return render(request,
                      'registry/users/user_doctor.html',
                      {'form': form,
                       'test_upload_form': MedicalTestUploadForm(),
                       'hn_owner': hn_user,
                       'hn_visitor': hn_user,
                       'appointments': hn_user.appointment_set.all(),
                       'doctors_patients': patients_list.distinct(),
                       'inbox': inbox,
                       'patients_transfer': patients_transfer,
                       }, context_instance=RequestContext(request))

    elif rules.test_rule('is_nurse', hn_user):
        # if they ever had or have an appointment at the nurse's hospital
        patients_list = Patient.objects.filter(appointment__location=hn_user.hospital).distinct()
        admitted_list = Patient.objects.filter(admission_status__isnull=False,
                                               admission_status__hospital=hn_user.hospital)
        return render(request,
                      'registry/users/user_nurse.html',
                      {'form': form,
                       'hn_owner': hn_user,
                       'inbox': inbox,
                       'appointments': hn_user.hospital.appointment_set.all(),
                       'admitted': admitted_list,
                       'patients': patients_list,
                       }, context_instance=RequestContext(request))

    else:
        logs = HNLogEntry.objects.all()
        admin_form = AdminRegistrationForm()
        doc_form = DoctorRegistrationForm()
        nurse_form = NurseRegistrationForm()
        patients_transfer = Patient.objects.filter(admission_status__isnull=False)
        return render(request,
                      'registry/users/user_admin.html',
                      {'hn_owner': hn_user,
                       'hn_visitor': hn_user,
                       'admin_form': admin_form,
                       'doc_form': doc_form,
                       'nurse_form': nurse_form,
                       'inbox': inbox,
                       'logs': logs,
                       'form': form,
                       'patients_transfer': patients_transfer,
                       }, context_instance=RequestContext(request))


@render_to('registry/register.html')
def register(request):
    """
    The view for the register page
    When successfully registered, it will render back to the homepage
    with a message that says "You have successfully registered. You can now log in."
    This is a logable event if the registration is successful.
    :param request:
    :return:
    """
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            username = '%s%s%s' % (patient.first_name, patient.middle_initial, patient.last_name)
            patient.auth_user = DjangoUser.objects.create_user(username, form.cleaned_data['email'],
                                                               form.cleaned_data['password'])
            patient.inbox = Inbox.objects.create()
            patient.save()
            patient.inbox.save()

            contact = PatientContact(
                    patient=patient,
                    relationship=form.cleaned_data['contact_relationship'],
                    contact_name=form.cleaned_data['contact_name'],
                    contact_primary=form.cleaned_data['contact_primary'],
                    contact_secondary=form.cleaned_data['contact_secondary'],
                    contact_email=form.cleaned_data['contact_email']
            )

            contact.save()
            patient.contact_set.add(contact)
            patient.save()

            try:
                user = User.objects.get(auth_user__email=contact.contact_email)
            except User.DoesNotExist:
                user = None

            print(user)
            if user is not None:
                print("Not Null")
                contact.contact_user = user

            contact.save()


            logger.action(request, LogAction.USER_REGISTER, 'Registered new user: {0!r}', patient)
            messages.add_message(request, messages.SUCCESS, 'Successfully Registered.')
            return redirect('registry:index')
    else:
        form = PatientRegisterForm()
    return {'form': form}

@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_admit.html')
def patient_admit(request, patient_uuid):
    """
    The view for admitting a patient
    This action is logable if successful admittance is made
    :param request:
    :param patient_uuid:  the patient getting admitted
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    location_found = False
    error = ""
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_nurse', user):
        if request.method == "POST":
            form = PatientAdmitForm(request.POST)
            if form.is_valid():
                admit_request = form.save(commit=False)
                for hospital in Hospital.objects.filter(provider_to=admit_request.doctor):
                    if admit_request.hospital == hospital:
                        location_found = True
                        break
                if location_found:
                    timerange = TimeRange.objects.create()
                    admit_request.admission_time = timerange
                    admit_request.save()

                    patient.admission_status = admit_request
                    patient.save()

                    logger.action(request, LogAction.PA_ADMIT, '{0!r} admitted by {1!r} to {2!s}', patient, user,
                                  admit_request.hospital)

                    return redirect('registry:home')
                else:
                    error = "Error: " + str(admit_request.doctor) + " does not work at " + str(admit_request.hospital)
        else:
            form = PatientAdmitForm()

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient, 'error': error}

    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_request.html')
def transfer(request, patient_uuid):
    """
    The view for a transfer request form
    A successful transfer is a logable event
    :param request:
    :param patient_uuid:
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    error = ""
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_administrator', user):
        if request.method == "POST":
            form = PatientTransferForm(request.POST, user=user)
            if form.is_valid():
                transfer_request = form.save(commit=False)

                transfer_request.admitted_by = user.__str__()
                timerange = TimeRange.objects.create()
                timerange.start_time = tz.now()
                transfer_request.admission_time = timerange
                transfer_request.save()
                patient.admission_status.save()
                patient.admission_status.end_admission()
                patient.admission_status = transfer_request
                patient.save()

                logger.action(request, LogAction.PA_TRANSFER_REQUEST,
                                  'Transfer {0!r} to {1!s} by {2!r}', patient, transfer_request.hospital, user)
                return redirect('registry:home')
        else:
            form = PatientTransferForm(user=user)

            if 'next' in request.GET:
                next_location = request.GET['next']

        return {'form': form, 'next_url': next_location, 'patient': patient, 'error': error}
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_discharge.html')
def patient_discharge(request, patient_uuid):
    """
    The view for confirming a discharge of a patient
    This is a logable event if successful
    :param request:
    :param patient_uuid: the patient to be discharged
    :return:
    """
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if not rules.test_rule('is_doctor_check', hn_user, patient):
        return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DischargeForm(request.POST, instance=patient.admission_status)
        if form.is_valid():
            patient.admission_status.end_admission()
            patient.admission_status = None

            logger.action(request, LogAction.PA_DISCHARGE, '{0!r} discharged by {1!r}', patient, hn_user)

            patient.save()
            return redirect('registry:home')

    else:
        form = DischargeForm(instance=patient.admission_status)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_create.html')
def appt_create(request):
    """
    The view for the creation of an appointment.
    It will display the appointment creation form.
    This is a logable event
    :param request:
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    next_location = None
    error = ""
    location_found = False
    if request.method == "POST":
        form = AppointmentSchedulingForm(request.POST, user=user)
        if form.is_valid():
            appointment = form.save(commit=False)
            if rules.test_rule('time_gt', appointment.time, tz.now()):
                for hospital in Hospital.objects.filter(provider_to=appointment.doctor):
                    if appointment.location == hospital:
                        location_found = True
                        break
                if location_found:
                    dlist = Appointment.objects.filter(doctor__pk=appointment.doctor_id, time=appointment.time)
                    patientlist = Appointment.objects.filter(patient__pk=appointment.patient_id, time=appointment.time)
                    if not (dlist.exists() or patientlist.exists()):
                        appointment.save()

                        logger.action(request, LogAction.APPT_CREATE, 'Created for {0!r} to meet with {1!r} by {2!r}',
                                      appointment.patient, appointment.doctor, user)

                        return redirect('registry:home')
                    else:
                        error = "Appointment Error: DateTime conflict"
                else:
                    error = "Appointment Error: Doctor does not work in " + appointment.location.name

            else:
                error = "Appointment Error: That date and time has already happen."
    else:
        if rules.test_rule('is_administrator', user):
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')

        if 'start' in request.GET:
            form = AppointmentSchedulingForm(user=user, initial={'time': dateutil.parser.parse(request.GET['start'])})
        else:
            form = AppointmentSchedulingForm(user=user)

        if 'next' in request.GET:
            next_location = request.GET['next']

    return {'form': form, 'next_url': next_location, 'error': error}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_edit.html')
def appt_edit(request, pk):
    """
    The view for editing an appointment. The form only allows the editing of the hospital and date time
    The possible errors that will occur will be an outdated time or appointment confliction
    A successful edit is a logable event
    :param request:
    :param pk: the idnetifier of the appointment
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_administrator', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')

    initial_appointment = get_object_or_404(Appointment, pk=pk)
    appt = get_object_or_404(Appointment, pk=pk)
    initial_start_time = appt.time
    initial_doctor = appt.doctor.uuid
    error = ""
    if request.method == "POST":
        form = AppointmentEditForm(request.POST, instance=appt, appt_id=pk)
        if form.is_valid():
            appointment = form.save(commit=False)
            appt_list = Appointment.objects.filter(doctor__pk=appointment.doctor_id,
                                                   time=appointment.time)
            if rules.test_rule('time_gt', appointment.time, tz.now()):

                if not appt_list.exists() or (initial_doctor == appointment.doctor.uuid and
                                                      initial_start_time == appointment.time):
                    logger.action(request, LogAction.APPT_EDIT, 'Appt {0!r} to meet with {1!r} edited by {2!r}',
                                  appointment.patient, appointment.doctor, user)
                    appointment.save()
                    return redirect('registry:home')
                else:
                        error = "Appointment Edit Failure: Date/Time Conflicting"
            else:
                error = "Appointment Error: That date and time has already happen."
    else:
        form = AppointmentEditForm(instance=appt, appt_id=pk)
    return {'form': form, 'appt': initial_appointment, 'error': error, 'hn_visitor': user, 'hn_owner': appt.patient}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_view.html')
def appt_view(request, pk):
    """
    The view for viewing an appointment.
    This view is only used for appointments in the past.
    :param request:
    :param pk: appointment identifier
    """
    appt = get_object_or_404(Appointment, pk=pk)
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_doctor', user) and (appt.doctor.uuid != user.uuid):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    elif rules.test_rule('is_patient', user) and (appt.patient.uuid != user.uuid):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    elif rules.test_rule('is_nurse', user) and appt.location != user.hospital:
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    elif rules.test_rule('is_administrator', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    return {'appt': appt}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_delete.html')
def appt_delete(request, pk):
    """
    The view for deleting an appointment.
    The only users allowed to delete the appointment are the patient and doctor that the appointment
    belongs to. This is a confirmation page.
    A successful deletion is a logable event
    :param request:
    :param pk: appointment identifier
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    delete = get_object_or_404(Appointment, id=pk)
    if (rules.test_rule('is_patient', user) and delete.patient.pk != user.pk) or \
            (rules.test_rule('is_doctor', user) and delete.doctor.pk != user.pk):
        return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')

    if request.method == 'POST':
        form = DeleteAppForm(request.POST, instance=delete)
        if form.is_valid():
            logger.action(request, LogAction.APPT_DELETE, 'Appt {0!r} to meet with {1!r} deleted by {2!r}',
                          delete.patient, delete.doctor, user)
            delete.delete()
            return redirect('registry:home')

    else:
        form = DeleteAppForm(instance=delete)

    template_vars = {'form': form}
    return template_vars


@require_http_methods(['GET', 'HEAD', 'PATCH', 'POST', 'OPTIONS'])
@require_http_methods_not_none(['GET', 'HEAD', 'PATCH'], 'uuid')
def user(request, uuid=None):
    if request.method == 'PATCH':
        read_request_body_to(request, request.method)
        if 'admit' in request.PATCH:
            admit_user(request, uuid)
        else:
            return update_user(request, uuid)
    elif request.method == 'POST':
        return user_create(request)
    elif request.method == 'OPTIONS':
        return list_user(request)
    elif is_safe_request(request.method):
        return view_user(request, uuid)


@ajax_request
@login_required(login_url=reverse_lazy('registry:login'))
def user_create(request):
    if 'user-type' not in request.POST:
        return ajax_failure()

    user_type = request.POST['user-type']

    if user_type == 'admin':
        return admin_create(request)
    elif user_type == 'nurse':
        return nurse_create(request)
    elif user_type == 'doctor':
        return doctor_create(request)
    else:
        return ajax_failure()


@ajax_request
def admin_create(request):
    """
    The view for creating an admin
    A successful registration will be logged.
    :param request:
    :return:
    """
    form = AdminRegistrationForm(request.POST)
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if form.is_valid():
        admin = form.save(commit=False)
        username = '{!s}'.format(admin)
        admin.auth_user = DjangoUser.objects.create_user(username, form.cleaned_data['email'],
                                                         form.cleaned_data['password'])
        admin.save()
        logger.action(request, LogAction.ST_CREATE, 'Admin {0!r} created by {1!r}', admin, user, user)
        return ajax_success()

    return ajax_failure()


@ajax_request
def doctor_create(request):
    formData = QueryDict(mutable=True)
    formData.update(request.POST)
    formData.update(({'hospitals': request.POST['hospitals[]']}))
    form = DoctorRegistrationForm(formData)
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if form.is_valid():
        doc = form.save(commit=False)
        username = '{!s}'.format(doc)
        doc.auth_user = DjangoUser.objects.create_user(username, form.cleaned_data['email'],
                                                       form.cleaned_data['password'])

        doc.save()

        for hospital in form.cleaned_data['hospitals']:
            doc.hospitals.add(hospital)

        doc.save()
        logger.action(request, LogAction.ST_CREATE, 'Doctor {0!r} created by {1!r}', doc, user, user)
        return ajax_success()

    return ajax_failure(formErrors=form.errors)


@ajax_request
def nurse_create(request):
    """
    Nurse creation view. It will display the form and also receive the form submission
    Nurse creation is a logable event
    :param request:
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    form = NurseRegistrationForm(request.POST)

    if form.is_valid():
        nurse = form.save(commit=False)
        username = '{!s}'.format(nurse)
        nurse.auth_user = DjangoUser.objects.create_user(username, form.cleaned_data['email'],
                                                         form.cleaned_data['password'])
        nurse.save()
        logger.action(request, LogAction.ST_CREATE, 'Nurse {0!r} created by {1!r}', nurse, user, user)
        return ajax_success()

    return ajax_failure()


@ajax_request
def list_user(request):
    """
    The view for anything that needs to list users/get user information.
    :param request:
    :return:
    """
    users = User.objects.all()

    res = [{'img': static('registry/img/logo.png'),
            'profileUrl': reverse('registry:user', args=(hn_user.uuid,)),
            'name': str(hn_user),
            'type': hn_user.get_user_type()} for hn_user in [User.objects.get_subclass(pk=user.pk) for user in users]]

    return ajax_success(users=res)


@login_required(login_url=reverse_lazy('registry:login'))
@render_to("registry/base/base_user.html")
def view_user(request, uuid):
    """
    The view for looking at another user's profile.
    :param request:
    :param uuid: the intended user's profile
    :return:
    """
    owner = User.objects.get_subclass(pk=uuid)
    visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if rules.test_rule('is_self', owner, visitor):
        return redirect(to=reverse('registry:home'))

    rxs = None
    if rules.test_rule('is_patient', owner):
        mc = None
        mh = mc
        if visitor.has_perm('registry.edit_patient', owner):
            rxs = owner.prescription_set.filter()
            mc = owner.conditions.all()
            mh = MedicalHistory.objects.filter(patient=owner).all()
            if rules.test_rule('is_doctor', visitor):
                mt = MedicalTest.objects.filter(patient=owner).order_by('-timestamp').all()
            else:
                mt = MedicalTest.objects.filter(patient=owner, released=True).order_by('-timestamp').all()
        return {"hn_owner": owner, "hn_visitor": visitor, 'rxs': rxs, 'medical_conditions': mc, 'medical_history': mh,
                'medical_tests': mt}
    return {"hn_owner": owner, "hn_visitor": visitor}


@login_required(login_url=reverse_lazy('registry:login'))
@ajax_request
def admit_user(request, uuid):
    """
    The admit user request
    This is written in ajax format
    :param request:
    :param uuid: the patient being admitted
    :return:
    """
    admitter = User.objects.get_subclass(pk=request.user.hn_user.pk)
    admittee = User.objects.get_subclass(pk=get_object_or_404(User, uuid=uuid).pk)

    if admitter.has_perm('registry.admit'):
        form = PatientAdmitForm(request.PATCH)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.admission_time = TimeRange.objects.create()
            admission.patient = str(admittee)
            admission.admitted_by = str(admitter)
            admission.save()

            admittee.admission_status = admission
            admittee.save()

            logger.action(request, LogAction.PA_ADMIT, '{0!r} admitted by {1!r} to {2!s}', admittee, admitter,
                          admission.hospital)
            return ajax_success()

    return ajax_failure()


@login_required(login_url=reverse_lazy('registry:login'))
@ajax_request
def update_user(request, uuid):
    """
    The view for updating a user
    :param request:
    :param uuid: the user being updated
    :return:
    """
    try:
        user = User.objects.get_subclass(pk=uuid)
    except User.DoesNotExist:
        return ajax_failure(error='User does not exist')

    successes = []
    failures = []
    for key, value in request.PATCH.items():
        if hasattr(user, key):
            setattr(user, key, value)
            successes.append(key)
        else:
            failures.append(key)

    user.save()
    return ajax_success(successes=successes, failures=failures)


@require_http_methods(['GET'])
@ajax_request
def user_verify(request, uuid):
    hn_visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)
    hn_owner = get_user_or_404(uuid)

    perms = {
        'view.personal': hn_visitor.has_perm('registry.user.view.personal', hn_owner),
        'view.medical': hn_visitor.has_perm('registry.user.view.medical', hn_owner),
        'view.insurance': hn_visitor.has_perm('registry.user.view.insurance', hn_owner),
        'edit.personal': hn_visitor.has_perm('registry.user.edit.personal', hn_owner),
        'edit.medical': hn_visitor.has_perm('registry.user.edit.medical', hn_owner),
        'edit.insurance': hn_visitor.has_perm('registry.user.edit.insurance', hn_owner)
    }

    return ajax_success(perms=perms, user_id=uuid)


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/mc_add.html')
def mc_add(request, patient_uuid):
    """
    The view for adding a medical condition.
    :param request:
    :param patient_uuid: The identifier of the intended patient
    :return:
    """
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_nurse', user):
        if request.method == "POST":
            form = MedicalConditionAdd(request.POST)
            if form.is_valid():
                condition = form.save(commit=False)
                condition.save()
                patient.conditions.add(condition)
                patient.save()
                return redirect('registry:user', uuid=patient_uuid)
        else:
            form = MedicalConditionAdd()

        return {'form': form}

    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@require_http_methods(['GET', 'PATCH', 'DELETE'])
@login_required(login_url=reverse_lazy('registry:login'))
def rx_op(request, pk=None, patient_uuid=None):
    """
    The view for deciding which prescription view to go to.
    :param request:
    :param pk: the prescription identifier
    :param patient_uuid: the patient indentifier
    :return:
    """
    if request.method == 'GET':
        return rx_view(request, pk)
    elif request.method == 'PATCH':
        return rx_update(request, pk)
    elif request.method == 'DELETE':
        return rx_delete(request, pk)


# @require_http_methods(['GET'])
@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/rx_create.html')
def rx_create(request, patient_uuid):
    """
    Prescription creation view
    This is not in ajax form
    Written by Lisa Ni--
    :param request:
    :param patient_uuid: the patient who the prescription is getting assigned to
    :return:
    """
    error = ""
    p = User.objects.get_subclass(pk=request.user.hn_user.pk)
    # next_location is where it goes if you cancel
    next_location = None

    if rules.test_rule('is_doctor', p):
        if request.method == "POST":
            form = PrescriptionCreation(request.POST, uuid=patient_uuid)
            if form.is_valid():
                rx = form.save(commit=False)
                timerange = TimeRange(
                        start_time=form.cleaned_data['start_time'],
                        end_time=form.cleaned_data['end_time']
                )
                if tz.now() < timerange.start_time < timerange.end_time:
                    timerange.save()
                    rx.time_range = timerange
                    rx.doctor = p
                    rx.save()

                    logger.action(request, LogAction.RX_CREATE, 'Prescribed by {0!r} to {1!r}', rx.doctor, rx.patient)
                    return redirect('registry:user', uuid=patient_uuid)
                else:
                    error = "Time Range is invalid. Start time cannot be in the past and the end time must be after" \
                            " start time."
        else:
            form = PrescriptionCreation(uuid=patient_uuid)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'error': error}

    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/rx_delete.html')
def rx_delete(request, pk):
    """
    Prescription deletion view
    I understand that it's not ajax format, but it works.
    Written by Lisa Ni
    :param request:
    :param pk: the id of the prescription
    :return:
    """
    rx = get_object_or_404(Prescription, id=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if not hn_user.has_perm('registry.rx', rx.patient) or rx.doctor.uuid != hn_user.uuid:
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')

    if request.method == 'POST':
        form = DeletePresForm(request.POST, instance=rx)
        if form.is_valid():
            patient = rx.patient
            logger.action(request, LogAction.RX_DELETE, 'Deleting a prescription from {0!r} by {1!r}',
                          rx.doctor, rx.patient)
            rx.delete()
            return redirect('registry:user', uuid=patient.uuid)
    else:
        form = DeletePresForm(instance=rx)

    template_vars = {'form': form}
    return template_vars

def rx_view(request, pk):
    return Http404()


@ajax_request
def rx_update(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if hn_user.has_perm('registry.rx', rx.patient):
        return ajax_success()
    else:
        return ajax_failure(error='Forbidden')


"""
@render_to('registry/data/rx_delete.html')
@ajax_request
def rx_delete(request, pk):
    rx = get_object_or_404(Prescription, id=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if not hn_user.has_perm('registry.rx', rx.patient) or rx.doctor.uuid != hn_user.uuid:
        return ajax_failure(error='Forbidden')


    rx.delete()

    return ajax_success()
"""

@require_http_methods(['POST'])
@login_required(login_url=reverse_lazy('registry:login'))
def transfers(request, pk):
    if request.method == 'POST':
        return {}


@require_http_methods(['POST'])
@login_required(login_url=reverse_lazy('registry:login'))
def transfer_create(request):
    """
    The view for transferring a patient.
    A successful and valid form submission will be logged.
    :param request:
    :return:
    """
    transferer = User.objects.get_subclass(pk=request.user.hn_user.pk)
    transferee = get_user_or_404(request.POST['whom'])

    if transferer.has_perm('registry.transfer_request'):
        form = PatientTransferForm(request.POST, user=transferer)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.admitted_by = str(transferer)
            transfer.save()

            transferee.transfer_status = transfer
            transferee.save()

            logger.action(request, LogAction.PA_TRANSFER_REQUEST,
                          'Transfer {0!r} to {1!s} by {2!r}', transferee, transfer.hospital, transferee)
            return ajax_success()

    return ajax_failure()


@require_http_methods(['GET', 'POST', 'DELETE'])
@require_http_methods_not_none(['GET', 'DELETE'], 'uuid')
@login_required(login_url=reverse_lazy('registry:login'))
def msg(request, uuid=None):
    """
    The view for determining what message related view the patient is requesting
    :param request:
    :param uuid: the identifer of the message
    :return:
    """
    if is_safe_request(request.method):
        return msg_view(request, uuid)
    elif request.method == 'POST':
        return msg_create(request)
    else:
        read_request_body_to(request, request.method)
        if request.method == 'DELETE':
            return msg_delete(request, uuid)


@ajax_request
def msg_create(request):
    """
    The view for creating a message
    :param request:
    :return:
    """
    form = MessageCreation(request.POST)

    if not form.is_valid():
        return ajax_failure()

    message = form.save(commit=False)

    message.sender = sender = User.objects.get_subclass(pk=request.user.hn_user.pk)
    message.receiver.inbox.messages.add(message)

    message.save()
    return ajax_success(id=message.uuid, sender=str(sender), timestamp=message.date.isoformat())


@ajax_request
def msg_delete(request, uuid):
    """
    The view for deletion of a message
    :param request:
    :param uuid: the identifier of a message
    :return:
    """
    failures = []

    try:
        if 'messages[]' in request.DELETE:
            mIdList = request.DELETE.getlist('messages[]')
            failures.extend(mIdList)
            for mId in mIdList:
                try:
                    msg = Message.objects.get(uuid=mId)
                    msg.delete()

                    failures.remove(mId)
                except Message.DoesNotExist:
                    pass
        else:
            try:
                msg = Message.objects.get(uuid=uuid)
                msg.delete()
            except Message.DoesNotExist:
                failures.append(uuid)
    except:
        return ajax_failure(fails=failures)

    return ajax_success(fails=failures)


@ajax_request
def msg_view(request, uuid):
    """
    The view for viewing a message
    :param request:
    :param uuid: the message identifer
    :return:
    """
    msg = Message.objects.get(uuid=uuid)
    return ajax_success(sender={'name': str(msg.sender), 'uuid': msg.sender.uuid}, content=msg.content, date=msg.date,
                        title=msg.title)


@require_http_methods(['GET', 'POST', 'PATCH'])
@login_required(login_url=reverse_lazy('registry:login'))
def appt(request):
    """
    The view for determinating which appt view the user is requesting
    :param request:
    :return:
    """
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    elif request.method == 'PATCH':
        pass


@require_http_methods(['GET'])
@login_required(login_url=reverse_lazy('registry:login'))
@ajax_request
def logs(request, start, end):
    """
    The view for gathering logs
    :param request:
    :param start: the start date of the timerange
    :param end: the end date of the timerange
    :return:
    """
    start_time = dateutil.parser.parse(start)
    end_time = dateutil.parser.parse(end)

    if start_time <= end_time:
        end_time += datetime.timedelta(days=1)

        log_level = int(request.GET['level']) if 'level' in request.GET and LogLevel.VERBOSE <= int(
            request.GET['level']) <= LogLevel.ERROR else LogLevel.INFO

        if 'ignore' in request.GET:
            ignore_req = request.GET['ignore'].lower()
            if ignore_req == 'both':
                start_time = end_time = None
            elif ignore_req == 'start':
                start_time = None
            elif ignore_req == 'end':
                end_time = None

        log_entries = logger.get_logs(start_time, end_time, log_level, True)

        result = []

        for entry in log_entries:
            from registry.templatetags.registry_tags import loggify
            result.append({
                'level': LogLevel.label(entry.level),
                'action': LogAction.label(entry.action),
                'location': entry.where,
                'timestamp': entry.timestamp,
                'message': entry.message,
                'class': loggify(entry.level)
            })
    else:
        result = []

    return ajax_success(entries=result)


@login_required(login_url=reverse_lazy('registry:login'))
def get_time(request):
    """
    The view for getting a time range for stats
    :param request:
    :return:
    """
    error = ""
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if not rules.test_rule('is_administrator', hn_user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TimeFrame(request.POST)
        # check whether it's valid:
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']

            if start > end:
                error = "Time Range is invalid. End time must be after start time."
            else:
                return stats(request, start, end)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TimeFrame()
    show = True
    return render(request, 'registry/components/admit_stats.html', {'show': show, 'form': form, 'error': error})


@login_required(login_url=reverse_lazy('registry:login'))
def stats(request, start, end):
    """
    The view for gathering stats from a time range
    :param request:
    :param start: the start date
    :param end: the end date
    :return:
    """
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if not rules.test_rule('is_administrator', hn_user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    start_time = start
    end_time = end
    admin = User.objects.get_subclass(pk=request.user.hn_user.pk)
    dCount = Doctor.objects.filter(hospitals=admin.hospital).count()
    nCount = Nurse.objects.filter(hospital=admin.hospital).count()
    aCount = Administrator.objects.filter(hospital=admin.hospital).count()
    pCount = Patient.objects.filter(admission_status__isnull=False, admission_status__hospital=admin.hospital).count()
    admitCount = MedicalHistory.objects.filter(admission_details__hospital=admin.hospital,
                                               admission_details__admission_time__start_time__gte=start_time).count()
    rxCount = Prescription.objects.filter(doctor__hospitals=admin.hospital,
                                          time_range__start_time__gte=start_time).count()
    admits = MedicalHistory.objects.filter(admission_details__hospital=admin.hospital,
                                           admission_details__admission_time__start_time__gte=start_time,
                                           admission_details__admission_time__end_time__lte=end_time + datetime.timedelta(
                                               days=1))
    emeAdmits = MedicalHistory.objects.filter(admission_details__hospital=admin.hospital,
                                              admission_details__admission_time__start_time__gte=start_time,
                                              admission_details__admission_time__end_time__lte=end_time + datetime.timedelta(
                                                  days=1), admission_details__reason=0).count()
    surAdmits = MedicalHistory.objects.filter(admission_details__hospital=admin.hospital,
                                              admission_details__admission_time__start_time__gte=start_time,
                                              admission_details__admission_time__end_time__lte=end_time + datetime.timedelta(
                                                  days=1), admission_details__reason=1).count()
    obsAdmits = MedicalHistory.objects.filter(admission_details__hospital=admin.hospital,
                                              admission_details__admission_time__start_time__gte=start_time,
                                              admission_details__admission_time__end_time__lte=end_time + datetime.timedelta(
                                                  days=1), admission_details__reason=2).count()
    unkAdmits = MedicalHistory.objects.filter(admission_details__hospital=admin.hospital,
                                              admission_details__admission_time__start_time__gte=start_time,
                                              admission_details__admission_time__end_time__lte=end_time + datetime.timedelta(
                                                  days=1), admission_details__reason=3).count()
    timeFrame = 0
    for admit in admits:
        delta = admit.admission_details.admission_time.end_time - admit.admission_details.admission_time.start_time
        timeFrame += delta.days
    if admitCount == 0:
        admitAvg = 0
    else:
        admitAvg = timeFrame / admitCount
    apptCount = Appointment.objects.filter(location=admin.hospital, time__gte=start_time,
                                           time__lte=end_time + datetime.timedelta(days=1)).count()

    template_vars = {'start_time': start_time, 'end_time': end_time, 'dCount': dCount, 'nCount': nCount,
                     'aCount': aCount, 'pCount': pCount, 'admitCount': admitCount, 'rxCount': rxCount,
                     'admitAvg': admitAvg, 'emeAdmits': emeAdmits, 'obsAdmits': obsAdmits, 'surAdmits': surAdmits,
                     'unkAdmits': unkAdmits, 'apptCount': apptCount}

    return render(request, 'registry/components/admit_stats.html', template_vars)





import csv
from django.http import HttpResponse


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/security_question.html')
def seq_check(request, patient_uuid):
    """
    The view for answering a security question before moving onto exporting information
    :param request:
    :param patient_uuid: the patient who's information will get exported
    :return:
    """
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    hn_visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)
    error = ""
    if not rules.test_rule('has_relationship', hn_visitor, patient):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')

    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['security_answer']
            if answer == hn_visitor.security_answer:
                logger.action(request, LogAction.PA_INFO, 'Medical information of {0!r} exported by {1!r}',
                              patient, hn_visitor)
                return patient_export(request, patient_uuid, ExportOption.label(int(form.cleaned_data['export_type'])))
            else:
                error = "Incorrect answer"
    else:
        form = ExportForm(secq=SecurityQuestion.label(patient.security_question))
    template_vars = {'form': form, 'error': error, 'patient': patient_uuid}
    return template_vars


def export_patient_info(request, patient_uuid):
    """
    This is the view for creating a CSV file of a patient medical information.
    Written by Lisa Ni
    :param request:
    :param patient_uuid: the patient whose information is being exported
    :return: the cvs file
    """
    return patient_export_csv(request, patient_uuid)


@require_http_methods(['POST'])
@login_required(login_url=reverse_lazy('registry:login'))
def patient_export(request, uuid, type):
    type = type.lower()

    if type == 'csv':
        return patient_export_csv(request, uuid)
    elif type == 'pdf':
        return patient_export_pdf(request, uuid)


@ajax_request
def patient_export_csv(request, uuid):
    from django.template import loader, Context
    user = get_user_or_404(uuid)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{!s}.csv"'.format(user)

    csv_data = [(
        'uuid',
        'first_name',
        'middle_initial',
        'last_name',
        'date_of_birth',
        'gender',
        'security_question',
        'security_answer',
        'address_line_one',
        'address_line_two',
        'address_city',
        'address_state',
        'address_zipcode',
        'height',
        'width',
        'provider',
        'admission_status',
        'pref_hospital',
        'blood_type',
        'insurance',
        'conditions'
    ), [
        str(user.uuid),
        user.first_name,
        user.middle_initial,
        user.last_name,
        user.date_of_birth.isoformat(),
        Gender.label(user.gender),
        SecQ.label(user.security_question),
        user.security_answer,
        user.address_line_one,
        user.address_line_two,
        user.address_city,
        user.address_state,
        user.address_zipcode,
        str(user.height),
        str(user.weight),
        str(user.provider),
        str(user.is_admitted()),
        str(user.pref_hospital),
        BloodType.label(user.blood_type),
        user.insurance,
        ','.join(["%s:%s" % (mc.name, mc.desc) for mc in user.conditions.all()])
    ]]

    tmpl = loader.get_template('registry/data/export/csv_export.csv')
    ctxt = Context({
        'data': csv_data
    })

    response.write(tmpl.render(ctxt))
    return response


@ajax_request
def patient_export_pdf(request, uuid):
    from django.template import loader, Context

    patient = get_user_or_404(uuid)
    creator = get_user_or_404(request.user.hn_user.pk)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{!s}.pdf"'.format(patient)

    address = (
        ('Address Line One', patient.address_line_one),
        ('Address Line Two', patient.address_line_two if patient.address_line_two != '' else ' '),
        ('City', patient.address_city),
        ('State', patient.address_state),
        ('Zip Code', patient.address_zipcode)
    )

    medical = (
        ('Primary Provider', str(patient.provider)),
        ('Preferred Hospital', str(patient.pref_hospital)),
        ('Gender', 'Male' if patient.gender == Gender.MALE else 'Female'),
        ('Blood Type', BloodType.label(patient.blood_type)),
        ('Height', patient.height),
        ('Weight', patient.weight),
        ('Insurance', patient.insurance)
    )

    ctxt = Context({
        'pagesize': 'A4',
        'title': str(patient),
        'user': patient,
        'address': address,
        'medical': medical,
        'conditions': patient.conditions.all(),
        'creator': creator
    })
    pdf = render_to_pdf('registry/data/export/pdf_export.html', ctxt)
    response.write(pdf)

    return response


@require_http_methods(['GET', 'POST', 'PUT'])
@require_http_methods_not_none(['GET', 'POST', 'PUT'], 'uuid')
@login_required(login_url=reverse_lazy('registry:login'))
def medical_tests(request, uuid):
    if request.method == 'GET':
        return medical_tests_create(request, uuid)
    elif request.method == 'POST':
        return medical_tests_create(request, uuid)
    elif request.method == 'PUT':
        read_request_body_to(request, 'PUT')
        return medical_tests_update(request, uuid)


@render_to('registry/data/medical_test_upload.html')
def medical_tests_create(request, uuid):
    creator = get_user_or_404(request.user.hn_user.pk)

    if request.method == 'POST':
        form = MedicalTestUploadForm(request.POST, files=request.FILES)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            result_note = Note.objects.create(author=creator, timestamp=tz.now(), content=form.cleaned_data['content'])
            result_note.save()

            for a in form.cleaned_data['attachments']:
                result_note.attachment_set.add(Attachment.objects.create(file=a, note=result_note))

            result_note.save()

            test = MedicalTest.objects.create(timestamp=tz.now(), results=result_note, sign_off_user=creator,
                                              patient=patient)
            test.notes.add(result_note)

            test.save()

            return redirect('registry:home')
        else:
            print(form.errors)
    else:
        form = MedicalTestUploadForm()

    return {'form': form}


@ajax_request
def medical_tests_update(request, uuid):
    patient = get_user_or_404(uuid)
    print(request.PUT)
    id = int(request.PUT['test-id'])

    test = MedicalTest.objects.filter(pk=id, patient=patient)
    if test.exists():
        test = test.first()
        test.released = True
        test.save()
        return ajax_success()

    return ajax_failure()
