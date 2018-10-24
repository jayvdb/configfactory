import sys

import click

from configfactory import __version__


def print_version(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    click.echo('\n'.join([
        f'ConfigFactory {__version__}',
        f'Python {sys.version}'
    ]), color=ctx.color)
    ctx.exit()


version_option = click.Option(
    ['-V', '--version'],
    help='Show version information.',
    expose_value=False,
    callback=print_version,
    is_flag=True,
    is_eager=True
)
