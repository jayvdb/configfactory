from django.db import models
from django.utils.translation import ugettext_lazy as _


class Config(models.Model):

    environment = models.SlugField(verbose_name=_('environment alias'))

    component = models.SlugField(verbose_name=_('component alias'))

    data = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('config')
        verbose_name_plural = _('configs')
        unique_together = ('environment', 'component')
