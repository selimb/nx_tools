import click


class NamedGroup(click.Group):
    def format_usage(self, ctx, formatter):
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage(self.name, ' '.join(pieces))


class NamedGroupNoArgs(click.Group):
    def format_usage(self, ctx, formatter):
        formatter.write_usage(self.name, 'COMMAND')
