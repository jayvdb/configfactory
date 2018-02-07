from django.template import Library

from configfactory.shortcuts import back_url

register = Library()


@register.inclusion_tag('tags/back_btn.html')
def back_btn(request, to, *args, **kwargs):
    url = back_url(to=to, request=request, *args, **kwargs)
    return {
        'url': url,
    }
