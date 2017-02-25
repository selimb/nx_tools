import logging
import os
import subprocess
import sys

from pkg_resources import parse_version

import click

from . import __version__, cli
from .cli._click import CONTEXT_SETTINGS, NamedGroup, confirm, prompt

logger = logging.getLogger(__name__)

def update():
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


@click.command('nx_tools_utils', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.pass_context
def nx_tools_utils(ctx, verbose):
    make_logger(verbose)
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
    if not no_update:
        update()


nx_tools.add_command(cli.add_task)
nx_tools.add_command(cli.config)
nx_tools.add_command(cli.launch)
nx_tools.add_command(cli.update)
nx_tools.add_command(cli._list)
nx_tools.add_command(cli.indentifier)

nx_tools_utils.add_command(cli.check)
nx_tools_utils.add_command(cli.find_entry)
