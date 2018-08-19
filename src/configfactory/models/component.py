from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import ComponentManager
from configfactory.utils import json


class Component(models.Model):

    name = models.CharField(max_length=64, unique=True)

    alias = models.SlugField(unique=True, help_text=_('Unique component alias'))

    settings_json = models.TextField(blank=True, null=True, default='{}')

    schema_json = models.TextField(blank=True, null=True, default='{}')

    is_global = models.BooleanField(default=False, help_text=_('Use only base environment'))

    require_schema = models.BooleanField(default=True, help_text=_('Use json schema validation'))

    strict_keys = models.BooleanField(default=False, help_text=_('Deny to change keys schema'))

    is_active = models.BooleanField(default=True,  verbose_name=_('active'), help_text=_(
        'Designates whether this component should be treated as active. '
        'Unselect this instead of deleting components.'
    ))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('creation datetime'))

    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('modification datetime'))

    objects = ComponentManager()

    class Meta:
        verbose_name = _('component')
        verbose_name_plural = _('components')
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def schema(self):
        return json.loads(self.schema_json)

    @schema.setter
    def schema(self, value):
        self.schema_json = json.dumps(value)

    def get_absolute_url(self):
        return reverse('component', kwargs={
            'alias': self.alias
        })
