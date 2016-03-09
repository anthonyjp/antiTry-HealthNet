from django import template
from django.utils.safestring import mark_safe

from registry.utility.options import *

registered_enums = {
    'blood': BloodType,
    'gender': Gender,
    'relation': Relationship,
    'security': SecurityQuestion,
    'units': Units
}

register = template.Library()

@register.filter(name="stringify")
def stringify(obj):
    return mark_safe(str(obj))

@register.simple_tag
def labelify(value, enum):
    return registered_enums[enum].label(value)