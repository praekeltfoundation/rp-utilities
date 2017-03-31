import click

from temba_client.v2 import TembaClient

from .campaigns import list_campaigns, list_events, create_events


class Context(object):
    def __init__(self, url, token):
        self.client = TembaClient(url, token)


pass_context = click.make_pass_decorator(Context)


@click.group()
@click.option('--url', envvar='RAPIDPRO_URL', type=click.STRING, help="URL to use for RapidPro API access")
@click.option('--token', envvar='RAPIDPRO_TOKEN', help="Auth token to use for RapidPro API access")
@click.pass_context
def cli(ctx, url, token):
    ctx.obj = TembaClient(url, token)


@cli.group(short_help="Manage Campaigns")
@click.pass_context
def campaigns(ctx):
    pass


@campaigns.group(short_help="Manage Campaign Events")
@click.pass_context
def events(ctx):
    pass


campaigns.add_command(list_campaigns, name='list')
events.add_command(create_events, name='create')
events.add_command(list_events, name='list')
