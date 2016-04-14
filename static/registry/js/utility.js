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

    return {
        'hookDatepicker': datepickerHook,
        'hookTimepicker': timepickerHook
    }
})();