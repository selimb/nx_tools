import logging
import os
from pkg_resources import parse_version
import subprocess
import sys

import click

from .. import __version__
from .. import api
from ..constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH
from ._click import CONTEXT_SETTINGS, NamedGroup, confirm, prompt
from . import update


logger = logging.getLogger(__name__)

def check_for_update():
    source = os.path.join('T:\\', 'selimb', 'nx_tools')
    vtxt = os.path.join(source, 'version.txt')
    try:
        new_version = open(vtxt).read().strip()
    except IOError:
        logger.debug("Could not open %s" % vtxt)
        return
    logger.debug("Version at %s : %s" % (vtxt, new_version))
    if parse_version(new_version) <= parse_version(__version__):
        return

    click.echo('Update is available.\n  New: %s\n  Current: %s'
               % (new_version, __version__))
    do_update = confirm('Do you want to update?', default=False)
    if not do_update:
        return
    click.echo('Changelog available at %s'
               % os.path.join(source, 'CHANGELOG.url'))
    click.echo('The current command will have to be re-run after installation.')
    sys.exit(subprocess.call(os.path.join(source, 'install.bat')))


def make_logger(verbose):
    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Verbosity activated.")
    else:
        logging.basicConfig()


def inject_env(ctx):
    config_paths = [DEFAULT_CONFIG_PATH,]
    if os.path.exists(USER_CONFIG_PATH):
        config_paths.append(USER_CONFIG_PATH)
    ctx.obj = api.config.Environment(config_paths)


@click.command('nx_tools_utils', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.pass_context
def nx_tools_utils(ctx, verbose):
    make_logger(verbose)
    inject_env(ctx)
    logger.debug('nx_tools_utils called:')
    logger.debug(ctx.args)


@click.command('nx_tools', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.option('--no-update', is_flag=True,
              help="Don't prompt for version update.")
@click.version_option(__version__, prog_name='NX Tools')
@click.pass_context
def nx_tools(ctx, gui, verbose, no_update):
    make_logger(verbose)
    logger.debug('nx_tools called:')
    logger.debug(ctx.args)
    if no_update is False:
        check_for_update()
    inject_env(ctx)


nx_tools.add_command(update.cli)
