/**
 * Created by Matthew on 2/28/2016.
 */

registry.utility = (function() {
    function datepickerHook() {
        $('.dateinput').filter(function() {
            return $(this).attr('datepicker') === '';
        }).each(function() {
            var picker = new Pikaday({field: $(this)[0]});
        });
    }

    return {
        'hookDatepicker': datepickerHook
    }
})();