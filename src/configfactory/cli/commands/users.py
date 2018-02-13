import click
from django.core.management import call_command

from configfactory.cli.decorators import setup_django


@click.group('users')
def users_group():
    """Perform users commands."""


@users_group.command('create')
@setup_django
def create_command():
    """Create super user."""
    call_command('createsuperuser')
