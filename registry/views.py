import dateutil.parser
import django.utils.timezone as tz

from annoying.decorators import render_to, ajax_request
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, Http404, QueryDict
from django.shortcuts import redirect, get_object_or_404, render

from .forms import *
from .models import *
from .utility.models import *
from .utility.logging import *

logger = HNLogger()


def ajax_success(**kwargs):
    kwargs.update({'success': True})
    return kwargs


def ajax_failure(**kwargs):
    kwargs.update({'success': False})
    return kwargs


def get_user_or_404(uuid):
    return User.objects.get_subclass(pk=get_object_or_404(User, pk=uuid).pk)


def is_safe_request(method):
    while hasattr(method, 'method'):
        method = method.method
    return method in ('GET', 'HEAD')


def read_request_body_to_post(request):
    request.POST = QueryDict(request.body)


def read_request_body_to(request, method='POST'):
    setattr(request, method, QueryDict(request.body))


@render_to('registry/landing.html')
def index(request):
    logger.info(request, repr(request.user.hn_user) if request.user.is_authenticated() else 'Anonymous',
                action=LogAction.PAGE_ACCESS)

    if request.user.is_authenticated():
        return redirect('registry:home')
    else:
        return {}


@render_to('registry/about.html')
def about(request):
    def create_dev(name, role, desc, *links, img=static('registry/img/logo.png')):
        real_links = []
        for l in links:
            real_links.append({'url': l[0], 'text': l[1] if len(l) > 1 and l[1] else l[0]})

        return {'name': name, 'role': role, 'desc': desc, 'img': img, 'links': real_links}

    return {'aboutus': [
        create_dev('Matthew Crocco', 'Development Coordinator', 'Test', ('https://github.com/Matt529', 'Github')),
        create_dev('Lisa Ni', 'Requirements Coordinator', 'Test'),
        create_dev('Anthony Perez', 'Quality Assurance Coordinator', 'Test'),
        create_dev('Alice Fischer', 'Team Coordinator', 'Test'),
        create_dev('Kyle Scagnelli', 'Test Coordinator', 'Test')
    ]}


@render_to('registry/login.html')
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                django_login(request, user)
                logger.action(request, LogAction.USER_LOGIN, '{name} has logged in!', name=str(user.hn_user))
                return redirect(to=reverse('registry:home'))
    else:
        form = LoginForm()
    return {'form': form}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/message_creation.html')
def message_creation(request):
    if request.method == "POST":
        form = MessageCreation(request.POST)
        message = form.save(commit=False)

        message.sender = User.objects.get_subclass(pk=request.user.hn_user.pk)
        message.receiver.inbox.messages.add(message)

        message.save()
    else:
        form = MessageCreation()
    return {'form': form}


@login_required(login_url=reverse_lazy('registry:login'))
def home(request):

    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    form = MessageCreation(request.POST)
    inbox = hn_user.inbox.messages.filter(receiver=hn_user).order_by('-date')

    if rules.test_rule('is_patient', hn_user):
        medical_history = MedicalHistory.objects.filter(patient=hn_user).all()
        return render(request,
                      'registry/users/user_patient.html',
                      {'form': form,
                       'hn_owner': hn_user,
                       'hn_visitor': hn_user,
                       'inbox': inbox,
                       'appointments': hn_user.appointment_set.all(),
                       'medical_conditions': hn_user.conditions.all(),
                       'medical_history': medical_history,
                       }, context_instance=RequestContext(request))

    elif rules.test_rule('is_doctor', hn_user):
        patients = Patient.objects.filter(provider=hn_user)
        not_patients = Patient.objects.exclude(provider=hn_user)
        return render(request,
                      'registry/users/user_doctor.html',
                      {'form': form,
                       'hn_owner': hn_user,
                       'hn_visitor': hn_user,
                       'appointments': hn_user.appointment_set.all(),
                       'not_patients': not_patients,
                       'patients': patients,
                       }, context_instance=RequestContext(request))

    elif rules.test_rule('is_nurse', hn_user):
        pref_patients = Patient.objects.filter(pref_hospital=hn_user.hospital)
        # add in the admitted patients
        admit_patients = Patient.objects.filter(cur_hospital=hn_user.hospital)
        return render(request,
                      'registry/users/user_nurse.html',
                      {'form': form,
                       'hn_owner': hn_user,
                       'appointments': hn_user.appointment_set.all(),
                       'pref_patients': pref_patients,
                       'admit_patients': admit_patients,
                       }, context_instance=RequestContext(request))

    else:
        logs = HNLogEntry.objects.all()
        admin_form = AdminRegistrationForm()
        doc_form = DoctorRegistrationForm()
        nurse_form = NurseRegistrationForm()
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
                       }, context_instance=RequestContext(request))


@render_to('registry/register.html')
def register(request):
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

            try:
                user = User.objects.get(auth_user__email=form.cleaned_data['contact_email'])
            except User.DoesNotExist:
                user = None

            if user is not None:
                contact.contact_user = user

            contact.save()
            patient.contact_set.add(contact)
            patient.save()

            logger.action(request, LogAction.USER_REGISTER, 'Registered new user: {0!r}', patient)

            return redirect('registry:index')
    else:
        form = PatientRegisterForm()
    return {'form': form}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_admit.html')
def patient_admit(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_nurse', user):
        if request.method == "POST":
            form = PatientAdmitForm(request.POST, user)
            if form.is_valid():
                admit_request = form.save(commit=False)
                timerange = TimeRange.objects.create()
                admit_request.admission_time = timerange
                admit_request.save()

                patient.admission_status = admit_request
                patient.save()

                logger.action(request, LogAction.PA_ADMIT, '{0!r} admitted by {1!r} to {2!s}', patient, user,
                              admit_request.hospital)

                return redirect('registry:home')
        else:
            form = PatientAdmitForm(user)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient}

    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_request.html')
def patient_transfer_request(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_administer', user):
        if request.method == "POST":
            form = PatientTransferForm(request.POST, user=user)
            if form.is_valid():
                transfer_request = form.save(commit=False)
                transfer_request.admitted_by = user.__str__()
                transfer_request.save()
                patient.transfer_status = transfer_request
                patient.save()

                logger.action(request, LogAction.PA_TRANSFER_REQUEST,
                              'Transfer {0!r} to {1!s} by {2!r}', patient, transfer_request.hospital, user)
                return redirect('registry:home')
        else:
            form = PatientTransferForm(user=user)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient}
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_approve.html')
def patient_transfer_approve(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    # next_location is where it goes if you cancel
    next_location = None
    if rules.test_rule('is_doctor', user) or rules.test_rule('is_administer', user):
        if request.method == "POST":
            form = ApproveTransferForm(request.POST, instance=patient.transfer_status)
            if form.is_valid():
                transfer_request = patient.transfer_status

                old_admit = patient.admission_status
                old_admit.admission_time.end_time = tz.now()
                old_admit.end_admission()

                new_admit = AdmissionInfo.objects.create(hospital=transfer_request.hospital,
                                                         reason=transfer_request.reason,
                                                         admission_time=TimeRange.objects.create(),
                                                         doctor=transfer_request.doctor)

                patient.transfer_status = None
                patient.admission_status = new_admit
                patient.save()

                logger.action(request, LogAction.PA_TRANSFER_ACCEPTED, '{0!r} to {1!s} accepted by {2!r}', patient,
                              old_admit.hospital, user)
                logger.action(request, LogAction.PA_TRANSFERRED, '{0!r} to {1!s}', patient, new_admit.hospital)

                return redirect('registry:home')
        else:
            form = ApproveTransferForm(instance=patient.transfer_status)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'patient': patient}
    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_transfer_delete.html')
def patient_transfer_delete(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', user) or rules.test_rule('is_patient', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', user):
        if patient.provider.uuid != user.uuid:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteTransferForm(request.POST, instance=patient.transfer_status)
        if form.is_valid():
            patient.transfer_status = None
            patient.save()

            logger.action(request, LogAction.PA_TRANSFER_DENIED, '{0!r} to {1!s} denied by {2!r}', patient,
                          patient.cur_hospital, user)

            return redirect('registry:home')

    else:
        form = DeleteTransferForm(instance=patient.transfer_status)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/patient_discharge.html')
def patient_discharge(request, patient_uuid):
    user = User.objects.get_subclass(pk=request.user.hn_user.pk)
    if rules.test_rule('is_nurse', user) or rules.test_rule('is_patient', user):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    patient = get_object_or_404(Patient, uuid=patient_uuid)
    if rules.test_rule('is_doctor', user):
        if patient.provider.uuid != user.uuid:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteAdmitForm(request.POST, instance=patient.admission_status)
        if form.is_valid():
            admit_info = patient.admission_status
            admit_info.admission_time.end_time = tz.now()
            admit_info.save()

            logger.action(request, LogAction.PA_DISCHARGE, '{0!r} discharged by {1!r}', patient, user)

            patient.admission_status = None
            patient.transfer_status = None
            patient.save()
            return redirect('registry:home')

    else:
        form = DeleteAdmitForm(instance=patient.admission_status)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_create.html')
def appt_schedule(request):
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
                    dlist = Appointment.objects.filter(
                        doctor__pk=appointment.doctor_id,
                        time__hour=appointment.time.hour,
                        time__day=appointment.time.day)
                    patientlist = Appointment.objects.filter(
                        patient__pk=appointment.patient_id,
                        time__hour=appointment.time.hour,
                        time__day=appointment.time.day)
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
    initial_appointment = get_object_or_404(Appointment, pk=pk)
    appt = get_object_or_404(Appointment, pk=pk)
    initial_start_time = appt.time
    initial_doctor = appt.doctor.uuid
    error = ""
    if request.method == "POST":
        form = AppointmentEditForm(request.POST, instance=appt, appt_id=pk)
        if form.is_valid():
            appointment = form.save(commit=False)
            appt_list = Appointment.objects.filter(doctor__pk=appointment.doctor_id).filter(
                    time__hour=appointment.time.hour).filter(time__day=appointment.time.day)
            if rules.test_rule('time_gt', appointment.time, tz.now()):
                if initial_doctor == appointment.doctor.uuid:
                    if initial_start_time == appointment.time:
                        appointment.save()
                        return redirect('registry:home')
                    else:
                        if not (appt_list.exists()):
                            appointment.save()
                            return redirect('registry:home')
                else:
                    if not (appt_list.exists()):
                        appointment.save()
                        return redirect('registry:home')
                error = "Appointment Edit Failure: Date/Time Conflicting"
            else:
                error = "Appointment Error: That date and time has already happen."
    else:
        form = AppointmentEditForm(instance=appt, appt_id=pk)
    return {'form': form, 'appt': initial_appointment, 'error': error}


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/appt_delete.html')
def appt_delete(request, pk):
    q = request.user.hn_user
    p = User.objects.get_subclass(pk=q.pk)
    if rules.test_rule('is_nurse', p):
        return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    delete = get_object_or_404(Appointment, id=pk)
    if rules.test_rule('is_patient', p):
        if delete.patient.pk != p.pk:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if rules.test_rule('is_doctor', p):
        if delete.doctor.pk != p.pk:
            return HttpResponseNotFound(
                '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')
    if request.method == 'POST':
        form = DeleteAppForm(request.POST, instance=delete)
        if form.is_valid():
            delete.delete()
            return redirect('registry:home')

    else:
        form = DeleteAppForm(instance=delete)

    template_vars = {'form': form}
    return template_vars


@login_required(login_url=reverse_lazy('registry:login'))
def sign_out(request):
    if request.user:
        logout(request)

    return redirect(to=reverse('registry:index'))


# LogEntry Action flags meaning:
# ADDITION = 1
# CHANGE = 2
# DELETION = 3


def get_log_data():
    logs = HNLogEntry.objects.all()
    action_list = []
    for l in logs:
        time = str(l.action_time)
        user_id = str(l.user)
        object_repr = str(l.object_repr)
        action_flag = int(l.action_flag)

        if action_flag == 1:
            log_action = user_id + " added a new " + object_repr + " at [" + time + "]."
            action_list.append(log_action)
        if action_flag == 2:
            log_action = user_id + " changed their " + object_repr + " at [" + time + "]."
            action_list.append(log_action)
        if action_flag == 3:
            log_action = user_id + " deleted their " + object_repr + " at [" + time + "]."
            action_list.append(log_action)

    return action_list


@require_http_methods(['GET'])
@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/log.html')
def log_actions(request):
    fro = tz.now() - datetime.timedelta(days=1)
    to = tz.now()

    if 'from' in request.GET:
        fro = dateutil.parser.parse(request.GET['from'])
    if 'to' in request.GET:
        to = dateutil.parser.parse(request.GET['to'])

    return {"action_list": get_log_data(), 'from': fro, 'to': to}


@require_http_methods(['GET', 'HEAD', 'PATCH'])
@login_required(login_url=reverse_lazy('registry:login'))
def user(request, uuid):
    if request.method == 'PATCH':
        read_request_body_to(request, request.method)
        if 'admit' in request.PATCH:
            admit_user(request, uuid)
        else:
            return update_user(request, uuid)
    elif is_safe_request(request.method):
        return view_user(request, uuid)


@require_http_methods(['GET'])
@login_required(login_url=reverse_lazy('registry:login'))
@ajax_request
def list_user(request):
    users = User.objects.all()

    res = [{'img': static('registry/img/logo.png'),
            'profileUrl': reverse('registry:user', args=(hn_user.uuid,)),
            'name': str(hn_user),
            'type': hn_user.get_user_type()} for hn_user in [User.objects.get_subclass(pk=user.pk) for user in users]]

    return ajax_success(users=res)


@render_to("registry/base/base_user.html")
def view_user(request, uuid):
    owner = User.objects.get_subclass(pk=uuid)
    visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)

    rxs = None
    if rules.test_rule('is_doctor', visitor) and visitor.has_perm('registry.view_patient'):
        rxs = owner.prescription_set.filter(doctor=visitor)
    elif rules.test_rule('is_self', owner, visitor):
        rxs = owner.prescription_set

    return {"hn_owner": owner, "hn_visitor": visitor, 'rxs': rxs}


@ajax_request
def admit_user(request, uuid):
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

            admittee.cur_hospital = admission.hospital
            admittee.admission_status = admission
            admittee.save()

            logger.action(request, LogAction.PA_ADMIT, '{0!r} admitted by {1!r} to {2!s}', admittee, admitter,
                          admission.hospital)
            return {'success': True}

    return {'success': False}


@ajax_request
def update_user(request, uuid):
    try:
        user = User.objects.get_subclass(pk=uuid)
    except User.DoesNotExist:
        return {'error': 'User does not exit'}

    successes = []
    failures = []
    for key, value in request.PATCH.items():
        if hasattr(user, key):
            setattr(user, key, value)
            successes.append(key)
        else:
            failures.append(key)

    user.save()
    return {'successes': successes, 'failures': failures}


@require_http_methods(['GET'])
@ajax_request
def user_verify(request, uuid):
    hn_visitor = User.objects.get_subclass(pk=request.user.hn_user.pk)
    hn_owner = get_user_or_404(uuid)

    resp = {'can_edit': hn_visitor.has_perm('registry.edit_patient', hn_owner) if rules.test_rule('is_patient',
                                                                                                  hn_owner) else hn_visitor.uuid == hn_owner.uuid}
    if resp['can_edit']:
        resp['user_id'] = uuid

    return ajax_success(**resp)


@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/mc_add.html')
def mc_add(request, patient_uuid):
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
                return redirect('registry:home')
        else:
            form = MedicalConditionAdd()

        return {'form': form}

    return HttpResponseNotFound(
        '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


@require_http_methods(['GET', 'PATCH', 'DELETE'])
@login_required(login_url=reverse_lazy('registry:login'))
def rx_op(request, pk):
    if request.method == 'GET':
        return rx_view(request, pk)
    elif request.method == 'PATCH':
        return rx_update(request, pk)
    elif request.method == 'DELETE':
        return rx_delete(request, pk)


@require_http_methods(['GET'])
@login_required(login_url=reverse_lazy('registry:login'))
@render_to('registry/data/rx_create.html')
def rx_create(request, patient_uuid):
    error = ""
    p = User.objects.get_subclass(pk=request.user.hn_user.pk)

    # next_location is where it goes if you cancel
    # EXCUSE ME
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
                    error = "Time Range is invalid"
        else:
            form = PrescriptionCreation(uuid=patient_uuid)

            if 'next' in request.GET:
                next_location = request.GET['next']
        return {'form': form, 'next_url': next_location, 'error': error}

    return HttpResponseNotFound(
            '<h1>You do not have permission to perform this action</h1><a href="/"> Return to home</a>')


def rx_view(request, pk):
    return Http404()


@ajax_request
def rx_update(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if hn_user.has_perm('registry.rx', rx.patient):
        return {}
    else:
        return {'error': 'Forbidden'}


@render_to('registry/data/rx_delete.html')
@ajax_request
def rx_delete(request, pk):
    rx = get_object_or_404(Prescription, id=pk)
    hn_user = User.objects.get_subclass(pk=request.user.hn_user.pk)

    if not hn_user.has_perm('registry.rx', rx.patient) or rx.doctor.uuid != hn_user.uuid:
        return {'error': 'Forbidden'}

    rx.delete()

    return {}


@require_http_methods(['POST'])
@login_required(login_url=reverse_lazy('registry:login'))
def transfers(request, pk):
    if request.method == 'POST':
        return {}


@require_http_methods(['POST'])
@login_required(login_url=reverse_lazy('registry:login'))
def transfer_create(request):
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


@require_http_methods(['POST'])
@login_required(login_url=reverse_lazy('registry:login'))
@ajax_request
def msg_create(request):
    form = MessageCreation(request.POST)

    if not form.is_valid():
        return ajax_failure()

    message = form.save(commit=False)

    message.sender = sender = User.objects.get_subclass(pk=request.user.hn_user.pk)
    message.receiver.inbox.messages.add(message)

    message.save()

    return ajax_success(id=message.uuid, sender=str(sender), timestamp=message.date.isoformat())


@require_http_methods(['GET', 'DELETE'])
@login_required(login_url=reverse_lazy('registry:login'))
def msg(request, uuid):
    if is_safe_request(request.method):
        return view_msg(request, uuid)
    else:
        read_request_body_to(request, request.method)
        if request.method == 'DELETE':
            return delete_msg(request, uuid)


# TODO Combine msg, create_msg and delete_msg and get UUIDs from Request Data
@ajax_request
def delete_msg(request, uuid):
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
def view_msg(request, uuid):
    msg = Message.objects.get(uuid=uuid)
    return ajax_success(sender={'name': str(msg.sender), 'uuid': msg.sender.uuid}, content=msg.content, date=msg.date,
                        title=msg.title)


@require_http_methods(['GET'])
@login_required(login_url=reverse_lazy('registry:login'))
@ajax_request
def logs(request, start, end):
    start_time = dateutil.parser.parse(start)
    end_time = dateutil.parser.parse(end)

    if start_time > end_time:
        start_time, end_time = end_time, start_time

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

    print(start_time, end_time)
    log_entries = logger.get_logs(start_time, end_time, log_level, True)
    print(log_entries)

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

    return ajax_success(entries=result)
