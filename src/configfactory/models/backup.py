from django.db import models
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import BackupManager
from configfactory.utils import json


class Backup(models.Model):

    environments_data = models.TextField(default='{}')

    components_data = models.TextField(default='{}')

    configs_data = models.TextField(default='{}')

    user = models.ForeignKey('configfactory.User', on_delete=models.SET_NULL,
                             blank=True, null=True, verbose_name=_('user'))

    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('comment'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('creation datetime'))

    objects = BackupManager()

    class Meta:
        verbose_name = _('backup')
        verbose_name_plural = _('backups')
        ordering = ('-created_at',)

    def __str__(self):
        if self.comment:
            return f'{self.comment} {self.created_at}'
        return str(self.created_at)

    @property
    def environments(self):
        return json.loads(self.environments_data)

    @environments.setter
    def environments(self, value):
        self.environments_data = json.dumps(value)

    @property
    def components(self):
        return json.loads(self.components_data)

    @components.setter
    def components(self, value):
        self.components_data = json.dumps(value)

    @property
    def configs(self):
        return json.loads(self.configs_data)

    @configs.setter
    def configs(self, value):
        self.configs_data = json.dumps(value)
