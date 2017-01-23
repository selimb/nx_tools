import click
import logging

from ._click import confirm, prompt

logger = logging.getLogger(__name__)


def prompt_idx(filenames):
    msg = 'Pick items. [a/n/<list-of-numbers>/?]'
    help_msg = '\n'.join[
            'a - Pick all',
            'n - Pick none',
            '<list-of-numbers> - Comma or space-separated list of indices',
            '? - Print help']
    num_items = len(filenames)
    options = '\n'.join(['%d - %s' % (i, f) for i, f in enumerate(filenames)])
    while 1:
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
@click.option('--build', is_flag=True,
              help="Only update build.")
@click.option('--patch', is_flag=True,
              help="Only update patch.")
def update_cli(nx_version, build, patch):
    from ..api.update import BuildUpdater, TMGUpdater

    updaters = []
    if not patch and not is_frozen_build(nx_version, config):
        updaters.append(BuildUpdater)
    if not build:
        updaters.append(TMGUpdater)

    for updater_constructor in updaters:
        try:
            updater = updater_constructor(nx_version, config)
        except ConfigError:
            # TODO to use or not to use logger for this.
            logger.error('Configuration error:')
            logger.error(ConfigError)
            continue

        new_items = updater.check_new()
        if not new_items:
            click.echo('No new %s.' % updater.item_name_plural)
            continue

        filenames = map(get_filename, new_items)
        num_items = len(new_items)
        if num_items == 1:
            click.echo("One new %s found:" % updater.item_name)
            click.echo(filenames[0])
            yes = confirm('Get this item?', default=True)
            if yes:
                chosen_items = new_items[0]
        else:
            click.echo("%i new %s found:" % (number, updater.item_name_plural))
            idx = prompt_idx(filenames)
            chosen_items = [new_items[i] for i in idx]

        for item in chosen_items:
            click.echo("Fetching %s." % item)
            updater.fetch(item)
