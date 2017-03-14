import functools

import click

_suffix = '\n> '
confirm = functools.partial(click.confirm, prompt_suffix=_suffix)
prompt = functools.partial(click.prompt, prompt_suffix=_suffix)


_invalid_idx_fmt = 'Please enter indices between 0 and %i.'
_msg_single_fmt = '%s [<number>/?]'
_msg_range_fmt = '%s [a/n/<list-of-numbers>/?]'
_help_single = '\n'.join([
    '<number> - Single index',
    '? - Print help'
])
_help_range = '\n'.join([
    'a - Pick all',
    'n - Pick none',
    '<list-of-numbers> - Comma or space-separated list of indices',
    '? - Print help'
])


def prompt_idx_range(items, msg):
    msg_prompt = _msg_range_fmt % msg
    num_items = len(items)
    options = _mk_options(items)
    while True:
        click.echo(options)
        click.echo(msg_prompt)
        ans = prompt(msg_prompt).strip()
        if ans == 'a':
            return range(num_items)
        elif ans == 'n':
            return []

        sep = ',' if ',' in ans else ' '
        try:
            idx = [int(v.strip()) for v in ans.split(sep)]
        except ValueError:
            click.echo(_help_range)
            click.echo()
            continue

        if any([i >= num_items or i < 0 for i in idx]):
            click.echo(_invalid_idx_fmt % (num_items - 1))
            continue

        return idx


def prompt_idx_single(items, msg):
    msg_prompt = _msg_range_fmt % msg
    num_items = len(items)
    options = _mk_options(items)
    while True:
        click.echo(options)
        click.echo(msg_prompt)
        ans = prompt(msg_prompt).strip()
        try:
            idx = int(ans)
        except ValueError:
            click.echo(_help_single)
            click.echo()
            continue

        if idx >= num_items or idx < 0:
            click.echo(_invalid_idx_fmt % (num_items - 1))
            continue

        return idx


def _mk_options(items):
    return '\n'.join(['%d - %s' % (i, f) for i, f in enumerate(items)])
