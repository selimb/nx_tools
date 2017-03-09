import logging

import click

from . import _click
from ..api import update as nxup
from ..api.exceptions import NXToolsError
from ..api.config import TMG_KEY, NX_KEY, TRACKED

logger = logging.getLogger(__name__)


def echo_result(r):
    if r.stat != nxup.TASK_SUCCESS:
        click.echo('Error fetching %s.' % r.item)
        click.echo(r.reason)
        return

    click.echo('Fetched %s.' % r.item)


def prompt_idx(items):
    msg = 'Pick items. [a/n/<list-of-numbers>/?]'
    help_msg = '\n'.join([
        'a - Pick all',
        'n - Pick none',
        '<list-of-numbers> - Comma or space-separated list of indices',
        '? - Print help'
    ])
    num_items = len(items)
    options = '\n'.join(['%d - %s' % (i, f) for i, f in enumerate(items)])
    while True:
        click.echo(options)
        ans = _click.prompt(msg).strip()
        print 'ans', ans
        if ans == 'a':
            return range(num_items)
        elif ans == 'n':
            return []

        sep = ',' if ',' in ans else ' '
        try:
            idx = [int(v.strip()) for v in ans.split(sep)]
        except ValueError:
            click.echo(help_msg)
            click.echo()
            return None

        if any([i >= num_items or i < 0 for i in idx]):
            click.echo("Please enter indices between 0 and %i" % (num_items - 1))
            return None

        return idx


@click.command('update', short_help='Updater.')
@click.argument('nx_version', nargs=1)
@click.option('--nx', is_flag=True, help='Only update NX.')
@click.option('--tmg', is_flag=True, help='Only update TMG.')
@click.option('--sync', is_flag=True, help='Update synchronously')
def cli(env, nx_version, nx, tmg, sync):
    delete_zip = env.get_option('delete_zip')
    get_nx = not tmg
    get_tmg = not nx
    updaters = []
    if get_build:
        updaters.append((nxup.NXUpdater, NX_KEY))
    if get_patch:
        updaters.append((nxup.TMGUpdater, TMG_KEY))

    tasks = []
    for updater_cls, project_key in updaters:
        try:
            branch = env.get_branch(project_key, nx_version)
        except NXToolsError as e:
            click.echo(str(e))
            continue

        if branch.stat != TRACKED:
            click.echo(
                'Branch %s of project %s is not tracked. Skipping'
                % (nx_version, project_key)
            )
            continue

        up = updater_cls(branch.local, branch.remote, delete_zip)
        try:
            new_items = up.list_new()
        except exceptions.NXToolsError as e:
            click.echo(str(e))
            continue

        if not new_items:
            click.echo('No new %s items.' % name)
            continue

        fnames = map(utils.get_filename, new_items)
        num_items = len(fnames)
        if num_items == 1:
            click.echo('One new %s item found.' % name)
            click.echo(fnames[0])
            yes = _click.confirm('Get this item?', default=True)
            if yes:
                ids = [0,]
        else:
            click.echo('%i new %s items found.' % (num_items, name))
            ans = None
            while ans is None:
                ans = prompt_idx(fnames)

        chosen_items = (new_items[i] for i in ids)
        tasks.extend(up.make_tasks(chosen_items))

    num_tasks = len(tasks)
    if num_tasks == 0:
        click.echo('Not fetching anything.')
        return

    if sync or num_tasks == 1:
        for t in tasks:
            click.echo('Fetching %s.' % t.item)
            r = nxup.submit_tasks((t,))
            echo_result(r)
    else:
        click.echo('Fetching: ' + ', '.join((t.item for t in tasks)))

        for r in nxup.submit_tasks(tasks):
            echo_result(r)
