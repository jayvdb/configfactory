import click

from configfactory.cli import commands
from configfactory.cli.utils import version_option
from configfactory.support import env


def main():

    # Set environment defaults
    env.setdefaults()

    # Create CLI instance
    cli = click.Group()

    # Add version option
    cli.params.append(version_option)

    # Add base commands
    cli.add_command(commands.start_command)
    cli.add_command(commands.init_command)

    # Add development commands
    if env.is_local():
        cli.add_command(commands.django_group)

    cli()


if __name__ == '__main__':
    main()
