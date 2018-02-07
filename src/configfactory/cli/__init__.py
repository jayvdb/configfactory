import click
from django.utils.module_loading import import_string

from configfactory.support import appenv

commands = (
    'start_command',
    'init_command',
    'config.config_group',
    'users.users_group',
)

dev_commands = (
    'django_command',
)


@click.group()
def cli():
    pass


def add_commands(commands):
    for command_path in commands:
        command_path = 'configfactory.cli.commands.{path}'.format(path=command_path)
        command = import_string(command_path)
        cli.add_command(command)


def main():

    # Set default application environment variables
    appenv.set_defaults()

    # Add base commands
    add_commands(commands)

    # Add development commands
    if appenv.debug_enabled():
        add_commands(dev_commands)

    cli()


if __name__ == '__main__':
    main()
