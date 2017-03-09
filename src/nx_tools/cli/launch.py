import os

import click

from . import helpers


logger = logging.getLogger(__name__)


@click.command('launch', short_help='Launch NX.')
@click.argument('nx_version', nargs=1)
@click.option('--latest', is_flag=True,
              help="Launch latest NX build with latest TMG patch.")
@click.option('--vanilla', is_flag=True,
              help="Use NX's internal TMG.")
@click.option('--env-var', is_flag=True,
              help="Use user UGII_TMG_DIR environment variable.")
@click.option('--tmg'
              help="Specify alternate version for TMG.")
@click.option('--cwd', is_flag=True,
              help="Use current directory as working directory.")
@click.pass_obj
def cli(env, nx_version, latest, vanilla, env_var, tmg, cwd):
    if cwd:
        working_dir = os.getcwd()
    else:
        working_dir = env.get_option('start_in')
        if not working_dir or not os.path.exists(working_dir):
            working_dir = 'D:\\'
            click.echo(
                'Working directory defined in configuration "start_in" '
                ' does not exist.\n'
                'Will start in %s.' % working_dir
            )

    logger.debug(helpers.pformat_cli_args(locals()))
    try:
        nx_branch = env.get_nx_branch(nx_version)
    except NXToolsError as e:
        click.echo(str(e))

    if nx_branch.stat == FROZEN:
        click.echo('Frozen NX branch.')
        ugraf = nx_branch.remote
    else:
        builds_list = helpers.list_directories(
            nx_branch.local,
            order=helpers.orders['chronological']
        )
        if latest:
            root = builds_list[0]
        else:
            root = helpers.prompt_idx(builds_list, 'Pick an NX build.')
        ugraf = api.find.ugraf(root)

    tmg_dir = get_tmg_dir(
    if vanilla:
        patch = ''
    elif env_var:
        patch = os.environ['UGII_TMG_DIR']
        click.echo('Not setting UGII_TMG_DIR. Currently set to: %s' % patch)
    else:
        tmg_ver = tmg or nx_version
        try:
            tmg_branch = env.get_tmg_branch(tmg_ver)
        except NXToolsError as e:
            click.echo(str(e))
            return

        patches_list = helpers.list_directories(
            tmg_branch.local,
            order=helpers.order['chronological']
        )
        if latest:
            patch_root = patches_list[0]
        else:
            patch_root = helpers.prompt_idx(patches_list, 'Pick a TMG patch.')

        tmg_dir = api.find.tmg(patch_root)

