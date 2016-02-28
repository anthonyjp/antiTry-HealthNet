/**
 * Created by Matthew on 2/28/2016.
 */

registry.utility = (function() {
    function datepickerHook() {
        $('.dateinput').filter(function() {
            return $(this).attr('datepicker') === '';
        }).each(function() {
            new Pikaday({field: $(this)[0], format: 'MM/DD/YYYY'});
            $(this).attr('readonly', true);
        });
    }

    return {
        'hookDatepicker': datepickerHook
    }
})();