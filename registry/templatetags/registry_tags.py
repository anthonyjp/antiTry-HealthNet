from django import template
from django.utils.safestring import mark_safe
from django_enumfield.enum import Enum
from ..models import User
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

for fqname, enum in inspect.getmembers(options, lambda x: inspect.isclass(x) and issubclass(x, Enum)):
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
            sig = inspect.signature(alias_f)

            # check the function can be called properly
            # That is it has no required positional arguments
            for param in sig.parameters.values():
                if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and param.default == inspect.Parameter.empty:
                    break
            else:
                # Call and register aliases, if possible
                aliases = alias_f()
                if isinstance(aliases, list):
                    for alias in aliases:
                        registered_enums[alias] = enum
                elif isinstance(aliases, str):
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


@register.simple_tag
def loggify(value):
    return 'log-%s' % (options.LogLevel.label(value).lower())


@register.filter
def naify(value, replace=None):
    return str(value) if (not isinstance(value, str) or value and value.lower() != 'none') else \
        ('N/A' if replace is None else str(replace))


@register.filter
def superify(value):
    try:
        user = User.objects.get_subclass(pk=value.pk)
    except User.DoesNotExist:
        return str(value)

    return str(user)
