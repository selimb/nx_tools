import logging

import click

from ._click import confirm, prompt

logger = logging.getLogger(__name__)


def echo_result(r):
    if r.stat != 0:
        click.echo('Error fetching %s.' % r.item_name)
        click.echo(r.reason)
    click.echo('Fetched %s.' % r.item_name)


def prompt_idx(items):
    msg = 'Pick items. [a/n/<list-of-numbers>/?]'
    help_msg = '\n'.join[
            'a - Pick all',
            'n - Pick none',
            '<list-of-numbers> - Comma or space-separated list of indices',
            '? - Print help']
    num_items = len(items)
    options = '\n'.join(['%d - %s' % (i, f) for i, f in enumerate(items)])
    while True:
        click.echo(options)
        ans = prompt(msg).strip()
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
            continue

        if any([i >= num_items or i < 0 for i in idx]):
            click.echo("Please enter indices between 0 and %i" % num_items - 1)


@click.command('update', short_help='Updater.')
@click.argument('nx_version', nargs=1)
@click.option('--nx', is_flag=True, help='Only update NX.')
@click.option('--tmg', is_flag=True, help='Only update TMG.')
@click.option('--sync', is_flag=True, help='Update synchronously')
def update_cli(nx_version, nx, tmg, sync):
    from ..api import update

    get_nx = not tmg
    get_tmg = not nx
    tasks = []
    updaters = []
    if get_build:
        updaters.append((NXUpdater, 'NX'))
    if get_patch:
        updaters.append((TMGUpdater, 'TMG'))

    for updater_cls, name in providers:
        # TODO: get config from somewhere
        try:
            u = updater_cls.from_config(config, nx_version)
        except exceptions.ConfigError as e:
            msg = 'Error in %s configuration.\n%s' % (name, str(e))
            click.echo(msg)
            continue

        try:
            new_items = u.list_new()
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
            yes = confirm('Get this item?', default=True)
            if yes:
                ids = [0,]
        else:
            click.echo('%i new %s items found.' % (num_items, name))
            ids = prompt_idx(fnames)

        chosen_items = (new_items[i] for i in ids)
        tasks.extend(u.make_tasks(chosen_items))

    num_tasks = len(tasks)
    if num_tasks == 0:
        click.echo('Not fetching anything.')
        return

    if sync or num_tasks == 1:
        for t in tasks:
            click.echo('Fetching %s.' % t.item_name)
            r = update.submit_tasks((t,))
            echo_result(r)
    else:
        click.echo('Fetching:\n' + '\n'.join((t.item_name for t in tasks)))
        results = update.submit_tasks(tasks)
        for r in results:
            echo_result(r)
