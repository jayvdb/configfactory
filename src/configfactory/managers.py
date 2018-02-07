from django.db import models

from configfactory.shortcuts import get_base_environment_alias


class EnvironmentQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def base(self):
        return self.filter(alias=get_base_environment_alias())

    def non_base(self):
        return self.exclude(alias=get_base_environment_alias())


class EnvironmentManager(models.Manager):

    def get_queryset(self):
        return EnvironmentQuerySet(
            model=self.model,
            using=self.db
        )

    def active(self):
        return self.get_queryset().active()

    def base(self):
        return self.get_queryset().base()

    def non_base(self):
        return self.get_queryset().non_base()


class ComponentQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class ComponentManager(models.Manager):

    def get_queryset(self):
        return ComponentQuerySet(
            model=self.model,
            using=self.db
        )

    def active(self):
        return self.get_queryset().active()


class BackupQuerySet(models.QuerySet):

    def auto(self):
        return self.filter(user__isnull=True)


class BackupManager(models.Manager):

    def get_queryset(self):
        return BackupQuerySet(
            model=self.model,
            using=self.db
        )

    def auto(self):
        return self.get_queryset().auto()


class APISettingsQuerySet(models.QuerySet):

    def enabled(self):
        return self.filter(is_enabled=True)


class APISettingsManager(models.Manager):

    def get_queryset(self):
        return APISettingsQuerySet(
            model=self.model,
            using=self.db
        )

    def active(self):
        return self.get_queryset().enabled()
