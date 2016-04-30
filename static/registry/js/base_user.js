if (!registry.has('forms.user'))
    registry.module('forms.user');

registry.forms['user'] = (function(){

    /*
        This can be done by registering a User UUID to use and then querying a specific URL via AJAX to verify user can
        do such things. Seriously. <3 AJAX.
     */
    var hooked = false;
    var csrf = registry.utility.getCsrf();
    var originals = {};
    var changed = {};

    const editables = $('input.editable');
    var userUuid = null;

    function getVerifyUrl(userUuid) {
        return '/verify/' + userUuid;
    }

    function getUpdateUrl(userUuid) {
        return '/user/' + userUuid;
    }

    function initEditables(canEdit) {
        // Add click listener to make fields readable
        if(canEdit) {
            editables.on('click', function () {
                $(this).prop('readonly', false);
            });

            // Add "blur" listeners such that when focus is lost they are made readonly again
            editables.on('blur', function () {
                $(this).prop('readonly', true);
            });

            // When a value has changed mark it for transition.
            editables.on('change', function () {
                var type = $(this).data('field');
                var value = $(this).val();

                // Reset to original if desired
                if (value === originals[type]) {
                    if (type in changed)
                        delete changed[type];

                    return;
                }

                changed[type] = $(this).val();
            });

            // Fill in original values
            editables.each(function () {
                originals[$(this).data('field')] = $(this).val();
            });

            editables.parsley();

            $('a.hn-tab').on('click', updateUser);
            console.log("User can edit");
        } else {
            editables.addClass('no-input');
            console.log("User cannot edit");
        }
    }

    function hookEditability(userId) {
        if (hooked)
            throw new Error('Attempt to reassign editability!');

        hooked = true;

        editables.prop('readonly', true);

        $.ajax({
            url: getVerifyUrl(userId),
            type: "GET",
            data: {},
            cache: false,
            dataType: "json",
            headers: {'X-CSRFToken': csrf},
            success: function(resp) {
                initEditables(resp['can_edit']);
                userUuid = resp['user_id'];
            },
            failure: function(resp) {
                console.log('failure');
                console.dir(resp);
            }
        });
    }

    function clearChanged() {
        for (var prop in changed) {
            if(!changed.hasOwnProperty(prop))
                continue;

            if(prop in originals)
                originals[prop] = changed[prop];
        }

        changed = {};
    }

    function revertChanged() {
        for (var prop in originals) {
            if (!originals.hasOwnProperty(prop))
                continue;

            if (prop in changed) {
                editables.filter(function () {
                    return $(this).data('field') === prop;
                }).each(function () {
                    $(this).val(originals[prop]);
                });
            }
        }

        changed = {};
    }

    function updateUser() {
        if (!hooked || userUuid == null || Object.size(changed) <= 0)
            return;

        vex.dialog.confirm({
            message: "Do you want to submit the current changes to the user profile?",
            callback: function (value) {
                if (value) {
                    $.ajax({
                        url: getUpdateUrl(userUuid),
                        type: "PATCH",
                        data: changed,
                        cache: false,
                        dataType: "json",
                        headers: {'X-CSRFToken': csrf},
                        success: function (resp) {
                            console.log("resp: ");
                            console.dir(resp);
                        },
                        failure: function (resp) {
                            console.log('failure');
                        }
                    });
                    clearChanged();
                } else {
                    revertChanged();
                    clearChanged();
                }
            }
        });
    }

    function isRequestUser(uuid) {
        return userUuid === uuid;
    }

    return {
        'hook': hookEditability,
        'updateUser': updateUser,
        'csrf': csrf,
        'isAuthUser': isRequestUser
    };
})();

Object.preventExtensions(registry.forms.user);

$(document).ready(function(){
    //  When user clicks on tab, this code will be executed
    $("#tab-links").find("li").click(function () {
        //  First remove class "active" from currently active tab
        $("#tab-links").find("li").removeClass('active');

        //  Now add class "active" to the selected/clicked tab
        $(this).addClass("active");

        //  Hide all tab content
        $(".tab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).find("a").attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return true;
    });

    $("#innertab-links").find("li").click(function () {
        //  First remove class "active" from currently active tab
        $("#innertab-links").find("li").removeClass('active');

        //  Now add class "active" to the selected/clicked tab
        $(this).addClass("active");

        //  Hide all tab content
        $(".innertab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).find("a").attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return true;
    });

    var checkAll = $("#checkAll");
    checkAll.change(function () {
        $("#msg-checkbox").prop('checked', $(this).prop("checked"));
    });

    checkAll.on('msg:uncheck', function () {
        if (checkAll.is(':checked'))
            checkAll.click();
    });

    $('#msg-checkbox').change(function () {
        if (!$(this).is(':checked'))
            checkAll.trigger('msg:uncheck');
    });

    var inbox = $("#inbox");

    $('#patientSearchBar').keyup(function()
	{
		searchTable($(this).val());
	});

    var messageOpenHandler = function () {
        //  Hide all tab content

        var selected_tab = $(this).parent('tr').attr("href");
        var uuid = $(this).parent('tr').data('message-id');

        $.ajax({
            url: 'msg/' + uuid,
            type: 'GET',
            data: {},
            success: function (response) {

                var data = response;

                var sender = data.sender["name"];
                var date = moment(data["date"]).format('MMMM Do YYYY [at] h:mm:ss a');
                var title = data["title"];
                var content = registry.escapeHtml(data["content"]).replace(/(?:\r\n|\r|\n)/g, '<br />');

                $("#message_sender").text(sender);
                $("#message_date").text(date);
                $("#message_title").text(title);
                $("#message_content").html(content);

                $(".tab").hide();
                //  Show the selected tab content
                $(selected_tab).fadeIn();
            }
        });

        return true;
    };

    $("#newMessage").click(function () {

        var div = $("#msg-create-form-html").clone();
        document.getElementById("msgCreation").reset();
        div.css("display", "block");
        div.find('span.help-inline').remove();

        vex.dialog.buttons.YES.text = 'Submit';
        vex.dialog.open({
            //message: '',
            message: div,
            callback: function (data) {
                if (data) {
                    var vexContent = $('.vex-content');
                    var receiver = vexContent.find('#id_receiver').find(':selected').val();
                    var title = vexContent.find('#id_title').val();
                    var content = vexContent.find('#id_content').val();

                    $.ajax({
                        url: '/msg',
                        type: 'POST',
                        data: {
                            'receiver': registry.escapeHtml(receiver),
                            'content': content,
                            'title': registry.escapeHtml(title)
                        },
                        headers: {'X-CSRFToken': registry.forms.user.csrf},
                        success: function (resp) {
                            if (resp.success && registry.forms.user.isAuthUser(receiver)) {
                                var time = moment(resp.timestamp).format('MMMM D, YYYY, h:mm a');
                                time = time.replace(/ am/g, ' a.m.').replace(/ pm/g, ' p.m.');
                                inbox.find('tbody').prepend(sprintf(
                                    '<tr data-message-id="%s" class="inbox-row" href="#tab7" id="TEMP-MESSAGE-ID-FOR-CLICK">' +
                                    '<td class="inboxBody check-box-wrapper">' +
                                    '<input id="msg-checkbox" type="checkbox"/>' +
                                    '</td>' +
                                    '<td class="inboxBody">%s</td>' +
                                    '<td class="inboxBody">%s</td>' +
                                    '<td class="inboxBody">%s</td>' +
                                    '</tr>', resp.id, resp.sender, title, time));

                                var t = $('#TEMP-MESSAGE-ID-FOR-CLICK');
                                t.find('td').not('.check-box-wrapper').click(messageOpenHandler);
                                t.attr('id', null);

                            }

                            vex.close();
                        },
                        failure: function (resp) {
                            console.log('Failure');
                            console.dir(resp);
                            vex.close();
                        }
                    })
                }
            }
        });
    });


    inbox.find("td").not('.check-box-wrapper').click(messageOpenHandler);

    $("#id-delete-msg").click(function () {
        var mIds = [];

        inbox.find('input:checked').not('#checkAll').each(function () {
            var td = $(this).parent('td');
            mIds.push(td.parent('tr').data('message-id'));
        });

        var handleMessages = function (messages, failures) {
            messages = _.without(messages, failures);
            _.each(messages, function (mId) {
                $('.inbox-row[data-message-id=\'' + mId + '\']').remove();
            });

            checkAll.trigger('msg:uncheck');
        };

        $.ajax({
            url: 'msg/' + mIds[0],
            type: 'DELETE',
            data: {'messages': mIds},
            headers: {'X-CSRFToken': registry.forms.user.csrf},
            success: function (resp) {
                handleMessages(mIds, resp.fails);
            },
            failure: function (resp) {
                handleMessages(mIds, resp.fails);
            }
        })
    });

});

function closeForm() {
    vex.close()
}

function searchTable(inputVal)
{

	var table = $('#patient');
	table.find('tr').each(function(index, row)
	{
		var allCells = $(row).find('td');
		if(allCells.length > 0)
		{
			var found = false;

			allCells.each(function(index, td)
			{
				var regExp = new RegExp(inputVal, 'i');
				if(regExp.test($(td).text()))
				{
					found = true;
					return false;
				}
			});
			if(found == true)$(row).show();
            else{
                $(row).hide();
                //$('#patient').append(notfound);
            }
        }
	});
}

$(window).bind('beforeunload', registry.forms.user.updateUser);

$("#buttons").click(function() {
        //  Hide all tab content
        $(".tab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).find("a").attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return true;
});

$("#presbuttons").click(function() {
        //  Hide all tab content
        $(".tab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).find("a").attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return true;
});

$("#button").click(function() {
        //  Hide all tab content
        $(".tab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).find("a").attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return true;
});
