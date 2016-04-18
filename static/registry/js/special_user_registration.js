/**
 * Created by Matthew on 4/18/2016.
 */

$(document).ready(function () {
    var nurseForm = $('#nurse-reg-form');

    $('#nurse-reg-submit').click(function () {
        var fname = nurseForm.find('input#id_first_name').val();
        var mi = nurseForm.find('#id_middle_initial').val();
        var lname = nurseForm.find('input#id_last_name').val();
        var dob = nurseForm.find('input#id_date_of_birth').val();
        var gender = nurseForm.find('#id_gender').find(':selected').val();
        var addressOne = nurseForm.find('input#id_address_line_one').val();
        var addressTwo = nurseForm.find('input#id_address_line_two').val();
        var addressCity = nurseForm.find('input#id_address_city').val();
        var addressState = nurseForm.find('#id_address_state').find(':selected').val();
        var addressZipCode = nurseForm.find('input#id_address_zipcode').val();
        var email = nurseForm.find('input#id_email').val();
        var pwd = nurseForm.find('input#id_password').val();
        var secq = nurseForm.find('#id_security_question').find(':selected').val();
        var seca = nurseForm.find('input#id_security_answer').val();
        var hospital = nurseForm.find('#id_hospital').find(':selected').val();

        $.ajax({
            url: '/user/create',
            type: 'POST',
            data: {
                'user-type': 'nurse',
                'first_name': fname,
                'last_name': lname,
                'middle_initial': mi,
                'date_of_birth': dob,
                'gender': gender,
                'address_line_one': addressOne,
                'address_line_two': addressTwo,
                'address_city': addressCity,
                'address_state': addressState,
                'address_zipcode': addressZipCode,
                'email': email,
                'password': pwd,
                'security_question': secq,
                'security_answer': seca,
                'hospital': hospital
            },
            headers: {'X-CSRFToken': registry.getCsrf(nurseForm)},
            success: function (resp) {
                if (resp.success)
                    document.location.reload();
                else {
                    console.log('Failed!');
                }
            },
            failure: function (resp) {
                console.log('Failed!');
            }
        })
    });

    var doctorForm = $('#doctor-reg-form');
    $('#doctor-reg-submit').click(function () {

        var fname = doctorForm.find('input#id_first_name').val();
        var mi = doctorForm.find('#id_middle_initial').val();
        var lname = doctorForm.find('input#id_last_name').val();
        var dob = doctorForm.find('input#id_date_of_birth').val();
        var gender = doctorForm.find('#id_gender').find(':selected').val();
        var addressOne = doctorForm.find('input#id_address_line_one').val();
        var addressTwo = doctorForm.find('input#id_address_line_two').val();
        var addressCity = doctorForm.find('input#id_address_city').val();
        var addressState = doctorForm.find('#id_address_state').find(':selected').val();
        var addressZipCode = doctorForm.find('input#id_address_zipcode').val();
        var email = doctorForm.find('input#id_email').val();
        var pwd = doctorForm.find('input#id_password').val();
        var secq = doctorForm.find('#id_security_question').find(':selected').val();
        var seca = doctorForm.find('input#id_security_answer').val();
        var hospital = doctorForm.find('#id_hospitals').find(':selected').val();


        $.ajax({
            url: '/user/create',
            type: 'POST',
            data: {
                'user-type': 'doctor',
                'first_name': fname,
                'last_name': lname,
                'middle_initial': mi,
                'date_of_birth': dob,
                'gender': gender,
                'address_line_one': addressOne,
                'address_line_two': addressTwo,
                'address_city': addressCity,
                'address_state': addressState,
                'address_zipcode': addressZipCode,
                'email': email,
                'password': pwd,
                'security_question': secq,
                'security_answer': seca,
                'hospitals': hospital
            },
            headers: {'X-CSRFToken': registry.getCsrf(doctorForm)},
            success: function (resp) {
                if (resp.success)
                    document.location.reload();
                else {
                    console.log('Failed!');
                }
            },
            failure: function (resp) {
                console.log('Failed!');
            }
        })
    });

    var adminForm = $('#admin-reg-form');

    $('#admin-reg-submit').click(function () {
        var fname = adminForm.find('input#id_first_name').val();
        var mi = adminForm.find('#id_middle_initial').val();
        var lname = adminForm.find('input#id_last_name').val();
        var dob = adminForm.find('input#id_date_of_birth').val();
        var gender = adminForm.find('#id_gender').find(':selected').val();
        var addressOne = adminForm.find('input#id_address_line_one').val();
        var addressTwo = adminForm.find('input#id_address_line_two').val();
        var addressCity = adminForm.find('input#id_address_city').val();
        var addressState = adminForm.find('#id_address_state').find(':selected').val();
        var addressZipCode = adminForm.find('input#id_address_zipcode').val();
        var email = adminForm.find('input#id_email').val();
        var pwd = adminForm.find('input#id_password').val();
        var secq = adminForm.find('#id_security_question').find(':selected').val();
        var seca = adminForm.find('input#id_security_answer').val();
        var hospital = adminForm.find('#id_hospital').find(':selected').val();

        $.ajax({
            url: '/user/create',
            type: 'POST',
            data: {
                'user-type': 'admin',
                'first_name': fname,
                'last_name': lname,
                'middle_initial': mi,
                'date_of_birth': dob,
                'gender': gender,
                'address_line_one': addressOne,
                'address_line_two': addressTwo,
                'address_city': addressCity,
                'address_state': addressState,
                'address_zipcode': addressZipCode,
                'email': email,
                'password': pwd,
                'security_question': secq,
                'security_answer': seca,
                'hospital': hospital
            },
            headers: {'X-CSRFToken': registry.getCsrf(adminForm)},
            success: function (resp) {
                if (resp.success)
                    document.location.reload();
                else {
                    console.log('Failed!');
                }
            },
            failure: function (resp) {
                console.log('Failed!');
            }
        })
    });
});