import logging
import os
from pkg_resources import parse_version
import subprocess
import sys

import click

from . import helpers
from ..__version__ import __version__
# from . import _list
# from . import update
# from . import launch
# from . import solve
# from . import check
# from . import identify


logger = logging.getLogger(__name__)
CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())


class NamedGroup(click.Group):
    def format_usage(self, ctx, formatter):
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage(self.name, ' '.join(pieces))


@click.command('nx_tools', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.option('--no-update', is_flag=True,
              help="Don't prompt for version update.")
@click.version_option(__version__, prog_name='NX Tools')
@click.pass_context
def nx_tools(ctx, verbose, no_update):
    # TODO: Get env
    make_logger(verbose)
    logger.debug('nx_tools called:')
    logger.debug(ctx.args)
    if no_update:
        return

    dist_root = os.path.join('T:\\', 'selimb', 'nx_tools')
    new_version = fetch_latest_version(dist_root)
    if not new_version:
        return
    click.echo(
        'Update is available.\n  New: %s\n  Current: %s'
        % (new_version, __version__)
    )
    do_update = helpers.confirm('Do you want to update?', default=False)
    if do_update:
        install(dist_root)


@click.command('nx_tools_utils', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.pass_context
def nx_tools_utils(ctx, verbose):
    make_logger(verbose)
    logger.debug('nx_tools_utils called:')
    logger.debug(ctx.args)


def fetch_latest_version(dist_root):
    vtxt = os.path.join(dist_root, 'version.txt')
    try:
        new_version = open(vtxt).read().strip()
    except IOError:
        logger.debug("Could not open %s" % vtxt)
        return None

    logger.debug("Version at %s : %s" % (vtxt, new_version))
    if parse_version(new_version) <= parse_version(__version__):
        return None

    return new_version


def install(dist_root):
    click.echo('Changelog available at %s'
               % os.path.join(dist_root, 'CHANGELOG.url'))
    click.echo('The current command will have to be re-run after installation.')
    sys.exit(subprocess.call(os.path.join(dist_root, 'install.bat')))


def make_logger(verbose):
    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Verbosity activated.")
    else:
        logging.basicConfig()


# nx_tools.add_command(_list.cli)
# nx_tools.add_command(update.cli)
# nx_tools.add_command(launch.cli)
# nx_tools.add_command(patch.cli)
# nx_tools.add_command(solve.cli)

# nx_tools_utils.add_command(check.cli)
# nx_tools_utils.add_command(identify.cli)
