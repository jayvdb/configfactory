from django.template import Library

register = Library()


@register.inclusion_tag('tags/pagination.html')
def pagination(request, page_obj, position='left', size=None, next_prev_only: bool=False):
    return {
        'request': request,
        'page_obj': page_obj,
        'position': position,
        'size': size,
        'next_prev_only': next_prev_only
    }
