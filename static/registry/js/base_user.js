
if(!registry.base.has('forms'))
    registry.base['forms'] = {};

registry.forms['user'] = (function(){

    // TODO This works for demonstration, we should move to querying the server for user verification so people can't hook in by simple javascript.
    // TODO We can do this by enumerating permissions and checking with the server immediately before edits are made
    /*
        This can be done by registering a User UUID to use and then querying a specific URL via AJAX to verify user can
        do such things. Seriously. <3 AJAX.
     */
    var hooked = false;
    var userUuid = null;
    var originals = {};
    var changed = {};

    function getUrl() {
        return '/user/' + userUuid + '/update/';
    }

    function hookEditability(canEdit, userId) {
        if(hooked)
            throw new Error('Attempt to reassign editability!');

        hooked = true;

        var editables = $('input.editable');
        editables.prop('readonly', true);

        if(canEdit) {
            userUuid = userId;
            // Add click listener to make fields readable
            editables.on('click', function () {
                $(this).prop('readonly', false);
            });

            // Add "blur" listeners such that when focus is lost they are made readonly again
            editables.on('blur', function() {
                $(this).prop('readonly', true);
            });

            // When a value has changed mark it for transition.
            editables.on('change', function() {
                var type = $(this).data('field');
                var value = $(this).val();

                // Reset to original if desired
                if(value === originals[type]) {
                    if(type in changed)
                        delete changed[type];

                    return;
                }

                changed[type] = $(this).val();
            });

            // Fill in original values
            editables.each(function() {
               originals[$(this).data('field')] = $(this).val();
            });

            $('a.hn-tab').on('click', updateUser);
        } else {
            editables.addClass('no-input');
        }
    }

    function updateUser() {
        if(userUuid === null)
            return;

        var csrf = $('[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            url: getUrl(),
            type: "POST",
            data: changed,
            cache: false,
            dataType: "json",
            headers: {'X-CSRFToken': csrf},
            success: function(resp) {
                console.log("resp: " + resp.toString());
            },
            failure: function(resp) {
                console.log('failure');
            }
        });

        for (var prop in changed) {
            if(!changed.hasOwnProperty(prop))
                continue;

            if(prop in originals)
                originals[prop] = changed[prop];
        }

        changed = {};
    }

    return {
        'hook': hookEditability,
        'updateUser': updateUser
    };
})();

Object.preventExtensions(registry.forms.user);

$(document).ready(function(){
    //  When user clicks on tab, this code will be executed
    $("#tab-links li").click(function() {
        //  First remove class "active" from currently active tab
        $("#tab-links li").removeClass('active');

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

    $("#checkAll").change(function () {
        $("input:checkbox").prop('checked', $(this).prop("checked"));
    });

    // Highlight a whole row from inbox table
    $("#inbox tr").not(':first').hover(
      function () {
        $(this).children().css("backgroundColor","#f3fef7");
      },
      function () {
        $(this).children().css("backgroundColor","#e3eee7");
      }
    );

});

$(window).bind('beforeunload', registry.forms.user.updateUser);

$("#inbox tr").not(':first').click(function() {
        //  Hide all tab content
        $(".tab").hide();

        //  Here we get the href value of the selected tab
        var selected_tab = $(this).attr("href");

        //  Show the selected tab content
        $(selected_tab).fadeIn();

        //  At the end, we add return false so that the click on the link is not executed
        return true;
});

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