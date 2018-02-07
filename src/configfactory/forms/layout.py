from crispy_forms.layout import HTML
from django.utils.translation import ugettext_lazy as _


class Back(HTML):

    def __init__(self, url):
        html = '<a class="btn btn-default" href="{url}">{title}</a>'.format(
            url=url,
            title=_('Back')
        )
        super().__init__(html)
