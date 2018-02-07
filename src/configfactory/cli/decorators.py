import functools

import click
import django


def setup_django(func):
    """Setup Django context."""
    @click.pass_context
    def inner(ctx, *args, **kwargs):
        django.setup()
        return ctx.invoke(func, *args, **kwargs)
    return functools.update_wrapper(inner, func)
