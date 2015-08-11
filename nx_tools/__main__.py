"""
    nx_tools.__main__
    ~~~~~~~~~~~~~~~~~

    Entry point for nx_tools. Implements technique in click/examples/complex.
    Additionally, to access the configuration, the @pass_object decorator is
    necessary.
"""

import click
import logging
import os
import subprocess
import sys

from ._click import NamedGroup
from .utils import read_config
from .commands import add_task
from .commands import config
from .commands import find_entry
from .commands import launch
from .commands import _list
from .commands import update
from .commands import identifier

__version__ = '1.1.7'

CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())


def make_logger(verbose):
    logger = logging.getLogger(__name__)
    if verbose:
        logger.debug("Verbosity activated.")
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()


def check_for_update():
    logger = logging.getLogger(__name__)
    source = os.path.join('T:\\', 'selimb', 'nx_tools')
    vtxt = os.path.join(source, 'version.txt')
    try:
        new_version = open(vtxt).read().strip()
    except IOError:
        logger.debug("Could not open %s" % vtxt)
        return
    logger.debug("Version at %s : %s" % (vtxt, new_version))
    if new_version <= __version__:
        return
    print("Update is available: %s " % new_version)
    question = " Do you want to upgrade [Y/n]? "
    sys.stdout.write(question)
    answer = raw_input()
    if answer.lower() == 'n':
        return
    print("Changelog available at %s"
          % os.path.join(source, 'CHANGELOG.url'))
    print("The current command will have to be re-run after installation.")
    sys.exit(subprocess.call(os.path.join(source, 'install.bat')))


@click.command('nx_tools', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.option('--no-upgrade', is_flag=True,
              help="Don't prompt for version upgrade.")
@click.version_option(__version__, prog_name='NX Tools')
@click.pass_context
def nx_tools(ctx, verbose, no_upgrade):
    make_logger(verbose)
    if no_upgrade is False:
        check_for_update()
    ctx.obj = read_config()


@click.command('nx_tools_utils', cls=NamedGroup,
               context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.pass_context
def nx_tools_utils(ctx, verbose):
    make_logger(verbose)
    ctx.obj = read_config()


nx_tools.add_command(add_task.cli)
nx_tools.add_command(config.cli)
nx_tools.add_command(launch.cli)
nx_tools.add_command(update.update_cli)
nx_tools.add_command(_list.cli)
nx_tools.add_command(identifier.cli)

nx_tools_utils.add_command(update.check_cli)
nx_tools_utils.add_command(find_entry.cli)

nx_tools_all = click.CommandCollection(sources=[nx_tools, nx_tools_utils])

if __name__ == '__main__':
    nx_tools()
