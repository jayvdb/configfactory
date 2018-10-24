from django.template.library import Library

from configfactory.utils.http import query_params

register = Library()
register.simple_tag(func=query_params, name='query_params')
