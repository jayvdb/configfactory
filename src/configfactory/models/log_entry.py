import dictdiffer
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from configfactory import choices, constants
from configfactory.models.component import Component
from configfactory.utils import json, dicthelper
from configfactory.utils.security import decrypt_data


class LogEntry(models.Model):

    action = models.CharField(max_length=255, verbose_name=_('action'))

    action_type = models.CharField(
        max_length=128,
        choices=choices.LOG_ACTION_TYPES,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('action type')
    )

    user = models.ForeignKey('configfactory.User', on_delete=models.SET_NULL,
                             blank=True, null=True, verbose_name=_('user'))

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL,
                                     blank=True, null=True, verbose_name=_('content type'))

    object_id = models.IntegerField(blank=True, null=True, verbose_name=_('object id'),)

    object_repr = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('object repr'))

    old_data_json = models.TextField(blank=True, null=True, verbose_name=_('old data'))

    new_data_json = models.TextField(blank=True, null=True, verbose_name=_('new data'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('action time'))

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        if not self.action and self.action_type:
            self.action = self.get_action_type_display()
        super().save(*args, **kwargs)

    @property
    def old_data(self) -> dict:
        return self._loads(self.old_data_json)

    @old_data.setter
    def old_data(self, data: dict):
        self.old_data_json = json.dumps(data)

    @property
    def new_data(self) -> dict:
        return self._loads(self.new_data_json)

    @new_data.setter
    def new_data(self, data: dict):
        self.new_data_json = json.dumps(data)

    @property
    def diff_data(self):
        return list(
            dictdiffer.diff(
                self.old_data,
                self.new_data
            )
        )

    @cached_property
    def message(self) -> str:
        return strip_tags(self.message_html)

    @cached_property
    def message_html(self):

        if self.action_type == constants.LOG_ACTION_TYPE_CREATE:
            if self.user_id and self.object_id and self.content_type_id:
                return _('<b>%(user)s</b> created %(object)s %(content_type)s.') % {
                    'user': self.user,
                    'object': self.object_repr,
                    'content_type': self.content_type
                }
            elif self.object_id and self.content_type_id:
                return _('%(object)s %(content_type)s '
                         'was successfully created.') % {
                    'object': self.object_repr,
                    'content_type': self.content_type
                }

        elif self.action_type == constants.LOG_ACTION_TYPE_UPDATE:
            if self.user_id and self.object_id and self.content_type_id:
                return _('<b>%(user)s</b> updated %(object)s %(content_type)s.') % {
                    'user': self.user,
                    'object': self.object_repr,
                    'content_type': self.content_type
                }
            elif self.object_id and self.content_type_id:
                return _('%(object)s %(content_type)s '
                         'was successfully updated.') % {
                    'object': self.object_repr,
                    'content_type': self.content_type
                }

        elif self.action_type == constants.LOG_ACTION_TYPE_DELETE:
            if self.user_id and self.object_repr and self.content_type_id:
                return _('<b>%(user)s</b> deleted %(object)s %(content_type)s.') % {
                    'user': self.user,
                    'object': self.object_repr,
                    'content_type': self.content_type
                }
            elif self.object_repr and self.content_type_id:
                return _('%(object)s %(content_type)s '
                         'was successfully deleted.') % {
                    'object': self.object_repr,
                    'content_type': self.content_type
                }

        if self.action:
            return self.action.capitalize()

        return self.action

    def get_object(self):
        if self.content_type and self.object_id:
            return self.content_type.get_object_for_this_type(pk=self.object_id)
        return None

    def get_object_url(self):
        if self.content_type and self.object_id:
            obj = self.get_object()
            if obj and hasattr(obj, 'get_absolute_url'):
                return obj.get_absolute_url()
        return None

    def _loads(self, data_json):
        if not data_json:
            return {}
        data = json.loads(data_json)
        if (
            self.content_type_id
            and self.content_type.model_class() is Component
            and 'settings' in data
        ):
            try:
                environment_data = data['settings']
                environment = list(environment_data.keys())[0]
                if isinstance(environment_data[environment], str):
                    settings_data = json.loads(
                        decrypt_data(environment_data[environment])
                    )
                else:
                    settings_data = environment_data[environment] or {}
                data['settings'][environment] = settings_data
            except (KeyError, IndexError):
                return {}
        return dicthelper.flatten(data)
