from django.utils.translation import ugettext_lazy as _

from configfactory import constants

LOG_ACTION_TYPES = (
    (constants.LOG_ACTION_TYPE_CREATE, _('create')),
    (constants.LOG_ACTION_TYPE_UPDATE, _('update')),
    (constants.LOG_ACTION_TYPE_DELETE, _('delete')),
)
