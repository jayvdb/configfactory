import click
from art import text2art
from django.utils.module_loading import import_string

from configfactory.support import appenv

base_commands = (
    'start_command',
    'init_command',
    'users.users_group',
)

development_commands = (
    'django_command',
)


@click.group()
def cli():
    pass


def add_commands(commands):
    for command_path in commands:
        command_path = f'configfactory.cli.commands.{command_path}'
        command = import_string(command_path)
        cli.add_command(command)


def main():

    # Set default application environment variables
    appenv.set_env_production_defaults()

    # Add base commands
    add_commands(base_commands)

    # Add development commands
    if appenv.is_development():
        add_commands(development_commands)

    cli()


if __name__ == '__main__':
    main()
