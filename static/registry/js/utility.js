/**
 * Created by Matthew on 2/28/2016.
 */

if (!registry.has('utility'))
    registry.module('utility');

registry.utility = (function() {
    function datepickerHook() {
        $('.dateinput').filter(function() {
            return $(this).attr('datepicker') === '';
        }).each(function() {
            new Pikaday({field: $(this)[0], format: 'MM/DD/YYYY', yearRange: [1900, moment().year()]});
            $(this).prop('readonly', true);
        });
    }

    function timepickerHook() {
        $('.timeinput').filter(function() {
            return $(this).attr('timepicker') === '';
        }).each(function() {
            $(this).timepicker({
                'useSelect': true,
                'timeFormat': 'h:i a'
            });

            $(this).on('click', function() {
                $(this).timepicker('show');
            });
        });
    }

    function getCookie(name) {
        if (!_.isNil(Cookies))
            return Cookies.get(name);
        else {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');

                cookieValue = _.chain(cookies).map(function (cookie) {
                    cookie = $.trim(cookie);
                    return {'name': cookie.substring(0, name.length), 'uri': cookie.substring(name.length + 1)};
                }).remove(function (cookie) {
                    return cookie.name !== name;
                }).head().value();
            }

            return cookieValue;
        }
    }

    function csrf() {
        return getCookie('csrftoken');
    }

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf());
            }
        }
    });

    function stopEventBehavior(event) {
        event.preventDefault ? event.preventDefault() : event.returnValue = false;
    }

    function processNextTick(fn) {
        if (_.isFunction(fn))
            setTimeout(fn, 0);  // TODO Poor performance in loops
    }

    window.processNextTick = processNextTick;

    return {
        'hookDatepicker': datepickerHook,
        'hookTimepicker': timepickerHook,
        'getCsrf': registry.getCsrf = csrf,
        'stopEventBehavior': registry.stopEventBehavior = stopEventBehavior,
        'getCookie': getCookie
    }
})();

Object.preventExtensions(registry);
Object.preventExtensions(registry.utility);