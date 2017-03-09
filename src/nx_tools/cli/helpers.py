import click

_suffix = '\n> '
confirm = functools.partial(click.confirm, prompt_suffix=_suffix)
prompt = functools.partial(click.prompt, prompt_suffix=_suffix)
