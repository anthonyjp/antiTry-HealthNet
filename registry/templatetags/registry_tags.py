from django import template
from django.utils.safestring import mark_safe
from django_enumfield.enum import Enum
from ..utility.strings import camelcase_to_slug, camelcase_to_snakecase

import inspect
import registry.utility.options as options

compat_enums = {
    'blood': options.BloodType,
    'gender': options.Gender,
    'relation': options.Relationship,
    'security': options.SecurityQuestion,
    'units': options.Units
}

registered_enums = {}

for fqname, enum in inspect.getmembers(options, lambda x: inspect.isclass(x) and x is Enum):

    # Populate Defaults, Lowercase Name, Snakecase Name and Slug Name
    key_all_lowercase = fqname.lower()
    key_snake = camelcase_to_snakecase(fqname)
    key_slug = camelcase_to_slug(fqname)

    # BloodType, bloodtype, blood-type, blood_type, Blood-Type
    registered_enums.update({
        fqname: enum,
        key_all_lowercase: enum,
        key_snake: enum,
        key_slug: enum,
        key_slug.lower(): enum
    })

    # Handle aliases, if provided
    if hasattr(enum, 'aliases'):
        alias_f = getattr(enum, 'aliases', lambda x: [])
        if callable(alias_f):
            aliases = alias_f(enum)
            if aliases is list:
                for alias in aliases:
                    registered_enums[alias] = enum
            elif aliases is str:
                registered_enums[aliases] = enum

# Register compatibility names, compatible with older system
registered_enums.update(compat_enums)


register = template.Library()


@register.filter(name="stringify")
def stringify(obj):
    return mark_safe(str(obj))


@register.simple_tag
def labelify(value, enum):
    return registered_enums[enum].label(value)
