from itertools import chain


def model_to_dict(instance, fields=None, exclude=None):
    """
    Convert model instance to dictionary representation.
    """

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

        if isinstance(data[f.name], list):
            data[f.name] = [o.pk for o in data[f.name]]

    return data
