import os

import click

from . import helpers


logger = logging.getLogger(__name__)


@click.command('list', short_help='List NX/TMG items')
@click.argument('nx_version', nargs=1)
@click.option('--nx', is_flag=True,
              help='Only list NX items.')
@click.option('--tmg', is_flag=True,
              help='Only list TMG items.')
@click.option('--absolute', is_flag=True,
              help='List absolute paths.')
@click.pass_obj
def cli(env, nx_version, nx, tmg, absolute):
    logger.debug(utils.pformat_cli_args(locals()))
    projects = []
    if not tmg:
        projects.append((NX_KEY, nx_version))
    if not nx:
        projects.append((TMG_KEY, nx_version))
    for project_key, name in projects:
        try:
            branch = env.get_branch(project_key)
        except NXToolsError as e:
            click.echo(str(e))
            continue

        if branch.stat == FROZEN:
            click.echo('%s branch "%s" is frozen.' % (name, nx_version))
            click.echo(branch.remote)


    raise NotImplementedError
