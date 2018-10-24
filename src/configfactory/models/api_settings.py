from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import APISettingsManager


class APISettings(models.Model):

    group = models.OneToOneField('auth.Group', on_delete=models.CASCADE, blank=True, null=True,
                                 verbose_name=_('group'), related_name='api_settings')

    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,
                             verbose_name=_('user'), related_name='api_settings')

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

    @property
    def user_or_group(self):
        if self.user_id:
            return self.user
        return self.group

    def clean(self):
        if self.group_id and self.user_id:
            raise ValidationError(_('API settings cannot be set for group and user at the same time.'))
        elif not self.group_id and not self.user_id:
            raise ValidationError(_('Group or user must be set.'))
