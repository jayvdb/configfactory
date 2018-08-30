import click

from configfactory.cli import commands
from configfactory.support import appenv


@click.group()
def cli():
    pass


def main():

    # Set default application environment variables
    appenv.set_production_defaults()

    # Add base commands
    cli.add_command(commands.start_command)
    cli.add_command(commands.init_command)

    # Add development commands
    if appenv.is_development():
        cli.add_command(commands.django_group)

    cli()


if __name__ == '__main__':
    main()
