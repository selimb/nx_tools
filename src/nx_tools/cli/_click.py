import functools

import click

_suffix = '\n> '
confirm = functools.partial(click.confirm, prompt_suffix=_suffix)
prompt = functools.partial(click.prompt, prompt_suffix=_suffix)
CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())


class NamedGroup(click.Group):
    def format_usage(self, ctx, formatter):
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage(self.name, ' '.join(pieces))
