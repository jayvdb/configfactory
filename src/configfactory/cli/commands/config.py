import click
from django.core.management import call_command

from configfactory.cli.decorators import setup_django


@click.group('config')
def config_group():
    """Perform config commands."""
