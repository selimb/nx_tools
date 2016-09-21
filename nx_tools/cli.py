"""
    nx_tools.cli
    ~~~~~~~~~~~~~~~~~

    CLI Entry point for nx_tools
    Additionally, to access the configuration, the @pass_object decorator is
    necessary.
"""

import click
import functools
from pkg_resources import parse_version
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
from .commands.update import  import update
from .commands import identifier

prompt = functools.partial(click.prompt, prompt_suffix='\n> ')
CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())

class NamedGroup(click.Group):
    def format_usage(self, ctx, formatter):
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage(self.name, ' '.join(pieces))


class NamedGroupNoArgs(click.Group):
    def format_usage(self, ctx, formatter):
        formatter.write_usage(self.name, 'COMMAND')


def make_logger(verbose):
    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Verbosity activated.")
    else:
        logging.basicConfig()


def pformat_cli_args(locs):
    """Pretty format locals."""
    return 'ARGS\n' + '\n'.join(('%s : %s' % (k, v) for k, v in locs.iteritems()
                                if k[:4] != 'conf' and k[:3] != 'log'))


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
    if parse_version(new_version) <= parse_version(__version__):
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


@click.command('update', short_help='Updater.')
@click.argument('nx_version', nargs=1)
@click.option('--build', is_flag=True,
              help="Only update build.")
@click.option('--patch', is_flag=True,
              help="Only update patch.")
@click.pass_obj
def update_cli(config, nx_version, build, patch):
    from .commands.update import BuildUpdater, TMGUpdater
    logger.debug(utils.pformat_cli_args(locals()))

    updaters = []
    if not patch and not is_frozen_build(nx_version, config):
        updaters.append(BuildUpdater)
    if not build:
        updaters.append(TMGUpdater)

    for updater_constructor in updaters:
        try:
            updater = updater_constructor(nx_version, config)
        except ConfigError:
            logger.error('Configuration error:')
            logger.error(ConfigError)
            continue

        new_items = updater.check_new()
        if not new_items:
            click.echo('No new %s.' % updater.item_name_plural)
            continue

        idx = []
        filenames = '\n'.join(map(get_filename, new_items))
        number = len(new_items)
        if number == 1:
            click.echo("One new %s found:" % updater.item_name)
            click.echo(filenames)
            yes = parse_yes_no(prompt('Get this item? (y/n)'))
            if yes:
                idx = [0,]
        else:
            click.echo("%i new %s found:" % (number, updater.item_name_plural))
            click.echo(filenames)
            ans = prompt('Pick items. (a/n/<list-of-numbers>/?').strip()
            idx = None
            while (not idx)
                if ans == 'a':
                    idx = enumerate(new_items)
                elif ans == 'n':
                    idx = []
                else:
                    sep = ',' if ',' in ans else ' '
                    try:
                        idx = [int(v.strip()) for v in ans.split(sep)]
                    except ValueError:
                        # Print help message
                        raise NotImplementedError
                    continue
            assert (idx is not None)
        items = [new_items[i] for i in idx]
        for item in items:
            click.echo("Fetching %s." % item)
            updater.fetch(item)


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
    logger.debug('nx_tools called:')
    logger.debug(ctx.args)
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
    logger.debug('nx_tools_utils called:')
    logger.debug(ctx.args)
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
