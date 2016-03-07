/**
 * Created by Matthew on 2/28/2016.
 */

registry.utility = (function() {
    function datepickerHook() {
        $('.dateinput').filter(function() {
            return $(this).attr('datepicker') === '';
        }).each(function() {
            new Pikaday({field: $(this)[0], format: 'MM/DD/YYYY', yearRange: [1900, moment().year()]});
            $(this).attr('readonly', true);
        });
    }

    function timepickerHook() {
        $('.timeinput').filter(function() {
            return $(this).attr('timepicker') === '';
        }).each(function() {
            $(this).timepicker({
                'timeFormat': 'h:i a'
            });
        });
    }

    return {
        'hookDatepicker': datepickerHook,
        'hookTimepicker': timepickerHook
    }
})();