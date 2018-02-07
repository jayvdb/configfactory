from django.db import models
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import APISettingsManager


class APISettings(models.Model):

    group = models.OneToOneField('auth.Group', on_delete=models.CASCADE,
                                 verbose_name=_('group'), related_name='api_settings')

    is_enabled = models.BooleanField(default=False, verbose_name=_('enabled'),
                                     help_text=_('Designates whether this group is enabled for API.'))

    token = models.CharField(max_length=48, verbose_name=_('Token'), unique=True)

    objects = APISettingsManager()

    class Meta:
        verbose_name = _('api settings')
        verbose_name_plural = _('api settings')

    def __str__(self):
        return _('%(group)s API settings') % {
            'group': self.group
        }
