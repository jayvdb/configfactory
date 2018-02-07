from django.template import Library
from django.utils.safestring import mark_safe

from configfactory import constants

register = Library()


@register.simple_tag
def boolean_icon(value):
    class_ = 'check text-green' if value else 'close text-red'
    return mark_safe("""
        <i class="fa fa-{}"></i>
    """.format(class_))


@register.simple_tag
def action_icon(value):
    icon_map = {
        constants.LOG_ACTION_TYPE_CREATE: 'plus-circle',
        constants.LOG_ACTION_TYPE_UPDATE: 'pencil',
        constants.LOG_ACTION_TYPE_DELETE: 'minus-circle',
    }
    color_map = {
        constants.LOG_ACTION_TYPE_CREATE: 'green',
        constants.LOG_ACTION_TYPE_UPDATE: 'blue',
        constants.LOG_ACTION_TYPE_DELETE: 'red',
    }
    icon = icon_map.get(value, 'info')
    color = color_map.get(value, 'aqua')
    return mark_safe("""
        <i class="fa fa-{} text-{}"></i>
    """.format(icon, color))
