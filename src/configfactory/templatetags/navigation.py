from collections import namedtuple

from django.template import Library
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

register = Library()

TabItem = namedtuple('Tab', ['title', 'active', 'url'])


@register.inclusion_tag('tags/tabs.html')
def profile_nav(request):

    resolver_match = request.resolver_match
    url_name = resolver_match.url_name

    items = [
        TabItem(
            title=_('Personal info'),
            active=url_name == 'profile',
            url=reverse('profile')
        ),
        TabItem(
            title=_('Password'),
            active=url_name == 'change_password',
            url=reverse('change_password')
        ),
    ]

    return {
        'request': request,
        'items': items,
        'nav_type': 'pills'
    }


@register.inclusion_tag('tags/tabs.html')
def group_edit_nav(request, group):

    resolver_match = request.resolver_match
    url_name = resolver_match.url_name

    items = [
        TabItem(
            title=_('Base'),
            active=url_name == 'update_group',
            url=reverse('update_group', kwargs={
                'pk': group.pk
            })
        ),
        TabItem(
            title=_('Environments'),
            active=url_name == 'group_environments',
            url=reverse('group_environments', kwargs={
                'pk': group.pk
            })
        ),
        TabItem(
            title=_('Components'),
            active=url_name == 'group_components',
            url=reverse('group_components', kwargs={
                'pk': group.pk
            })
        ),
        TabItem(
            title=_('API Settings'),
            active=url_name == 'group_api_settings',
            url=reverse('group_api_settings', kwargs={
                'pk': group.pk
            })
        ),
    ]

    return {
        'request': request,
        'items': items,
        'nav_type': 'pills'
    }


@register.inclusion_tag('tags/tabs.html')
def user_edit_nav(request, user):

    resolver_match = request.resolver_match
    url_name = resolver_match.url_name

    items = [
        TabItem(
            title=_('Base'),
            active=url_name == 'update_user',
            url=reverse('update_user', kwargs={
                'pk': user.pk
            })
        ),
        TabItem(
            title=_('Environments'),
            active=url_name == 'user_environments',
            url=reverse('user_environments', kwargs={
                'pk': user.pk
            })
        ),
        TabItem(
            title=_('Components'),
            active=url_name == 'user_components',
            url=reverse('user_components', kwargs={
                'pk': user.pk
            })
        ),
        TabItem(
            title=_('API Settings'),
            active=url_name == 'user_api_settings',
            url=reverse('group_api_settings', kwargs={
                'pk': user.pk
            })
        ),
    ]

    return {
        'request': request,
        'items': items,
        'nav_type': 'pills'
    }

