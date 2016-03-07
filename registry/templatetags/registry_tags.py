from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="stringify")
def stringify(obj):
    return mark_safe(str(obj))