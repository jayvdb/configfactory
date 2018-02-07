from django.template import Library

register = Library()


@register.simple_tag
def has_perm(perm_checker, perm, obj):
    return perm_checker.has_perm(perm, obj)
