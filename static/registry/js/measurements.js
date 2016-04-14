/**
 * Created by Matthew on 2/28/2016.
 */

if (!registry.has('forms'))
    registry.module('forms');

// TODO Generalize and Document

registry.forms['measurement'] = (function() {
    const UNITS = {
        'METRIC' : {
            'name': 'metric',
            'weight': 'kg'
        },
        'CUSTOMARY': {
            'name' : 'customary',
            'weight': 'lbs'
        }
    };

    const INT_TO_UNITS = [
        UNITS.CUSTOMARY,
        UNITS.METRIC
    ];

    var unit = UNITS.CUSTOMARY;
    var wrappers = $('.hn-measurement.wrapper');
    var weightModified = false;

    function unitPredicate(unit) {
        return function(i, elem) {
            return $(elem).hasClass(unit.name);
        }
    }

    function filterAndApply(jqobj, unit, fn) {
        jqobj.filter(unitPredicate(unit)).each(fn);
    }

    function initialize() {
        wrappers.each(function() {
            filterAndApply($(this).children(), UNITS.METRIC, function() {
                $(this).hide();
                $(this).children().each(function () {
                    $(this).attr('required', false)
                })
            });
        });
    }

    function setUnit(newUnit) {
        wrappers.each(function() {
            if($(this).find('.weight').length > 0 && !weightModified)
                return;
            else if($(this).find('.height').length > 0 && weightModified)
                return;

            var children = $(this).children();
            filterAndApply(children, unit, function() {
                $(this).hide();
                $(this).children().each(function() {
                    $(this).attr('required', false);
                });
            });

            filterAndApply(children, newUnit, function() {
                $(this).show();
                $(this).children().each(function() {
                    $(this).attr('required', true);
                });
            });
        });

        if(weightModified)
            $('span#weight-label').text(newUnit.weight);

        unit = newUnit;
        weightModified = false;
    }

    $('.hn-measurement.unit-select')
        .change(function() {
            var selectedUnit = INT_TO_UNITS[$(this).find('option:selected').first().attr('value')];
            weightModified = $(this).hasClass('weight');
            setUnit(selectedUnit, $(this).next());
        });

    return {
        'init': initialize,
        'setUnit': setUnit
    }
})();

registry.forms.measurement.init();