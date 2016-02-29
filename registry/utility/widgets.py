from django.forms import widgets, MultiValueField, fields

from pint import UnitRegistry
from .options import Units

ureg = UnitRegistry()


class HeightWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        _widgets = (
            widgets.Select(choices=Units.choices(), attrs={'class': 'hn-measurement unit-select height'}),
            widgets.NumberInput(attrs={'customary': True, 'class': 'hn-measurement height', 'min': 0, 'max': 7}),
            widgets.NumberInput(attrs={'customary': True, 'class': 'hn-measurement height', 'min': 0, 'max': 11}),
            widgets.NumberInput(attrs={'metric': True, 'class': 'hn-measurement height', 'min': 20, 'max': 280})
        )

        super(HeightWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            height = value * ureg.centimeters
            return [Units.label(Units.CUSTOMARY), int(height.to(ureg.feet).magnitude),
                    int(height.to(ureg.inches).magnitude % 12)]
        return [Units.label(Units.CUSTOMARY), 0, 0]

    def format_output(self, rendered_widgets):
        metric_div = '<div class="customary"><span>%s\'</span><span>%s"</span></div>' % \
                     (rendered_widgets[1], rendered_widgets[2])
        customary_div = '<div class="metric">%scm</div>' % rendered_widgets[3]

        value = '%s<div class="hn-measurement wrapper">%s</div>' % \
                (rendered_widgets[0], ''.join([metric_div, customary_div]))
        return value


class WeightWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        _widgets = (
            widgets.Select(choices=Units.choices(), attrs={'class': 'hn-measurement unit-select weight'}),
            widgets.NumberInput(attrs={'customary': True, 'class': 'hn-measurement weight', 'min': 1})
        )

        self.name = ''
        super(WeightWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            w = value * ureg.milligrams
            return [Units.label(Units.CUSTOMARY), int(w.to(ureg.lb))]
        return [Units.label(Units.CUSTOMARY), 0]

    def format_output(self, rendered_widgets):
        value = '%s<div class="hn-measurement wrapper">%s<span id="weight-label">lbs</span></div>' % \
                (rendered_widgets[0], ''.join(rendered_widgets[1:]))
        return value


class HeightField(MultiValueField):
    widget = HeightWidget()

    def __init__(self, *args, **kwargs):
        _fields = (
            fields.ChoiceField(),
            fields.IntegerField(min_value=0, max_value=8, required=True),
            fields.IntegerField(min_value=0, max_value=11, required=True),
            fields.IntegerField(min_value=1, max_value=280, required=False)
        )
        super(HeightField, self).__init__(_fields, *args, **kwargs)

    def compress(self, data_list):
        units = data_list[0]

        if units == Units.CUSTOMARY:
            feet = data_list[1] * ureg.feet
            inches = data_list[2] * ureg.inches
            return (feet + inches).to(ureg.centimeters).magnitude
        elif units == Units.METRIC:
            return data_list[3]
        else:
            return 0


class WeightField(MultiValueField):
    widget = WeightWidget()

    def __init__(self, *args, **kwargs):
        _fields = (
            fields.ChoiceField(),
            fields.IntegerField(min_value=0),
            fields.IntegerField(min_value=0)
        )
        super(WeightField, self).__init__(_fields, *args, **kwargs)

    def compress(self, data_list):
        units = data_list[0]

        if units == Units.CUSTOMARY:
            pounds = data_list[1] * ureg.lb
            return pounds.to(ureg.milligrams).magnitude
        elif units == Units.METRIC:
            kilos = data_list[1] * ureg.kilograms
            return kilos.to(ureg.milligrams).magnitude
        else:
            return 0
