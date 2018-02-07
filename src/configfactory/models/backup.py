from django.db import models
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import BackupManager


class Backup(models.Model):

    environments_data = models.TextField(default='[]')

    components_data = models.TextField(default='[]')

    configs_data = models.TextField(default='[]')

    user = models.ForeignKey(
        to='configfactory.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('user'),
    )

    comment = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('comment')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('creation datetime')
    )

    objects = BackupManager()

    class Meta:
        verbose_name = _('backup')
        verbose_name_plural = _('backups')
        ordering = ('-created_at',)

    def __str__(self):
        if self.comment:
            return '{comment} {date}'.format(
                comment=self.comment,
                date=self.created_at
            )
        return str(self.created_at)
