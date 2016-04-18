if (!registry.has('data.logrender'))
    registry.module('data.logrender');

registry.data.logrender = (function () {

    const csrf = registry.has('forms.user') ? registry.forms.user.csrf : $('[name="csrfmiddlewaretoken"]').val();
    var rendered = false;
    var rendering = false;

    const table = $('#log-table');
    const body = table.find('tbody');

    function cleanRender() {
        body.find('tr').remove();
        rendered = false;
    }

    function renderLogs(options) {
        if (rendering)
            return;

        if (rendered)
            cleanRender();

        var from = options.from || null;
        var to = options.to || null;
        var loglevel = options.level || 2;
        var ignorereq = options.ignore || 'none';

        if (!from)
            from = "1990-01-01";

        if (!to)
            to = moment().format('YYYY-MM-DD');

        if (moment(from).isAfter(moment(to)))
            to = from;

        rendering = true;
        $.ajax({
            url: '/logs/' + from + '/' + to,
            type: 'GET',
            data: {'level': loglevel, 'ignore': ignorereq},
            headers: {'X-CSRFToken': csrf},
            success: function (resp) {
                console.dir(resp);
                if (resp.success && resp.entries) {

                    _(resp.entries).reverse().each(function (e) {
                        var html = '' +
                            '<tr class="log-row %s">' +
                            '   <td>%s</td>' +
                            '   <td>%s</td>' +
                            '   <td>%s</td>' +
                            '   <td>%s</td>' +
                            '   <td id="log-message-col">%s</td>' +
                            '</tr>';

                        var time = moment(e.timestamp).format('MMMM Do, YYYY [at] h:mm:ss,SSS a');
                        var msg = e.message.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/g, function (match) {
                            return sprintf('<a target="_blank" class="hn-link log" href="/user/%s">%s</a>', match, match);
                        });
                        body.prepend(sprintf(html, e.class, time, e.level, e.action, e.location, msg));

                        rendered = true;
                        rendering = false;
                    });
                }
            },
            failure: function (resp) {
                console.log('Failed!');
                console.dir(resp);
                rendering = true;
            }
        })
    }

    return {
        "renderLogs": renderLogs
    }
})();

$(document).ready(function () {

    function datePickerToStandardDate(datepickerVal) {
        return moment(datepickerVal, 'MM/DD/YYYY').format('YYYY-MM-DD');
    }

    function renderHook() {
        var start = datePickerToStandardDate(startDatePicker.val());
        var end = datePickerToStandardDate(endDatePicker.val());

        registry.data.logrender.renderLogs({
            from: start,
            to: end
        });
    }

    var startDatePicker = $("#log-start-date");
    var endDatePicker = $("#log-end-date");

    startDatePicker.val('01/01/1990');
    endDatePicker.val(moment().format('MM/DD/YYYY'));

    startDatePicker.change(renderHook);
    endDatePicker.change(renderHook);
});