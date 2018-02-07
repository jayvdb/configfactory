from itertools import chain

from django.conf import settings


def get_db_table(model):

    prefix = settings.DATABASE_DB_TABLES_PREFIX

    if prefix and not prefix.endswith('_'):
        prefix = '{}_'.format(prefix)

    db_table = model._meta.db_table

    if settings.DATABASE_DB_TABLES_REPLACE:
        db_table = settings.DATABASE_DB_TABLES.get(db_table, db_table)

    if prefix and not db_table.startswith(prefix):
        return '{prefix}{db_table}'.format(
            prefix=prefix,
            db_table=db_table
        )

    return db_table


def set_db_table(sender, **kwargs):
    sender._meta.db_table = get_db_table(sender)


def model_to_dict(instance, fields=None, exclude=None):
    """
    Convert model instance to dictionary representation.
    """

    from django.db import models

    if hasattr(instance, 'to_dict'):
        return instance.to_dict()

    opts = instance._meta
    data = {}
    for f in chain(
            opts.concrete_fields,
            opts.private_fields,
            opts.many_to_many
    ):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)

        if isinstance(f, models.ManyToManyField):
            data[f.name] = list(data[f.name].values_list('pk', flat=True))

    return data
