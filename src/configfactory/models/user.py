from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('email address'),
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        if self.first_name and self.last_name:
            return self.get_full_name()
        return self.username
