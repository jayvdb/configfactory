from multiprocessing import Process, cpu_count

import click
import django
from configfactory.support.config import config
from django.core.management import call_command, execute_from_command_line

from configfactory.support import appenv


@click.command('init')
@click.option('config_path', '--config', envvar=appenv.VAR_CONFIG,
              type=click.Path(writable=True, readable=True, resolve_path=True))
def init_command(config_path):
    """Initialize ConfigFactory."""

    dst, created = config.create(dst=config_path)

    if not created:
        click.echo(f'Configuration file {dst} already exists.')

    # django.setup()
    #
    # call_command('migrate', verbosity=0)
    # click.echo('Database Initialized.')
    #
    # if click.confirm('Would like to create superuser ?'):
    #     call_command('createsuperuser')


@click.command('start')
@click.option(
    '--bind', '-b',
    help='A string of the form: HOST, HOST:PORT, '
         'unix:PATH. An IP is a valid HOST.',
    default=config.getlist('server.bind', default=['127.0.0.1:8080']),
    multiple=True
)
@click.option(
    '--workers', '-w',
    help='The number of worker processes for handling requests.',
    type=click.INT,
    default=cpu_count()
)
@click.option(
    '--reload',
    help='Restart workers when code changes.',
    default=False,
    is_flag=True
)
def start_command(**options):
    """Start ConfigFactory."""

    from configfactory import scheduler
    from configfactory.support.server import ConfigFactoryServer

    server = ConfigFactoryServer(options=options)

    # Create wsgi application process
    server_process = Process(target=server.run)
    server_process.start()

    # Create and start cron application process
    scheduler_process = Process(target=scheduler.run)
    scheduler_process.start()

    # Run multiple processes
    try:
        server_process.join()
        scheduler_process.join()
    except (KeyboardInterrupt, SystemExit):
        print('Shot down signal received...')


@click.command(
    'django',
    add_help_option=False,
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument('argv', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def django_group(ctx, argv):
    """
    Django commands.
    """

    execute_from_command_line(
        argv=[ctx.command_path] + list(argv)
    )
