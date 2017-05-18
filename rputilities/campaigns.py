import io
from backports import csv

import attr
import click
from temba_client.exceptions import TembaBadRequestError, TembaConnectionError


@attr.s
class CampaignEvent(object):
    relative_to = attr.ib()
    offset = attr.ib(convert=int)
    unit = attr.ib()
    delivery_hour = attr.ib(convert=int)
    message = attr.ib()


def get_campaign_events_from_csv(file_name):
    BASE_COLUMNS = ['relative_to', 'offset', 'unit', 'delivery_hour', 'lang_code', 'message']
    with io.open(file_name, encoding='utf-8') as csv_file:
        has_header = csv.Sniffer().has_header(csv_file.read(2048))
        csv_file.seek(0)
        csv_reader = csv.reader(csv_file)
        base_col_len = len(BASE_COLUMNS)
        if has_header:
            header = next(csv_reader)
            length = len(header)
            if length < base_col_len:
                raise ValueError("Invalid CSV format: A minimum of {0} columns expected".format(base_col_len))
            # Translations are given as optional (lang_code, message) column pairs at the end of each row.
            if length > base_col_len:
                # Translations need to be provided as lang_code, message pairs
                if (length - base_col_len) % 2 != 0:
                    raise ValueError("Invalid CSV format: Pairs of lang_code, message columns expected")
                has_translations = True
            else:
                has_translations = False
        for row in csv_reader:
            event = CampaignEvent(
                relative_to=row[0].strip(),
                offset=row[1].strip(),
                unit=row[2].strip(),
                delivery_hour=row[3].strip(),
                message=row[5].strip()
            )
            lang_code = row[4].strip()
            if has_translations:
                translations = row[base_col_len:]
                full_message = {lang_code: event.message}
                iterator = iter(translations)
                translations = zip(iterator, iterator)
                for code, msg in translations:
                    full_message[code.strip()] = msg.strip()
                event.message = full_message
            yield event


class APIError(Exception):
    """Raised when an error occured with the RapidPro API."""
    def __init__(self, message, extra_data):
        super(APIError, self).__init__(message)
        self.extra_data = extra_data


def create_campaign_events(file_name, campaign_id, client):
    campaign_id = str(campaign_id)
    for idx, event in enumerate(get_campaign_events_from_csv(file_name)):
        try:
            client.create_campaign_event(
                campaign_id,
                relative_to=event.relative_to,
                offset=event.offset,
                unit=event.unit,
                delivery_hour=event.delivery_hour,
                message=event.message
            )
        except TembaConnectionError as exc:
            raise APIError("Cannot connect to supplied RapidPro API, import aborted",
                           extra_data={'row': idx, 'error': str(exc)})
        except TembaBadRequestError as exc:
            raise APIError("A RapidPro error has occured, import aborted", extra_data={'row': idx, 'error': str(exc)})


# -- CLI commands

@click.command(short_help="List Campaigns")
@click.pass_context
def list_campaigns(ctx):
    campaigns = ctx.obj.get_campaigns()
    click.echo("Campaigns:")
    for campaign in campaigns.all():
        click.echo("{0} - {1}".format(campaign.uuid, campaign.name))


@click.command(short_help="List Campaign Events")
@click.argument('campaign', type=click.UUID, required=False)
@click.pass_context
def list_events(ctx, campaign=None):
    events = ctx.obj.get_campaign_events(campaign=campaign)
    click.echo("Campaign Events:")
    for event in events.all():
        click.echo("{0} - {1}".format(event.uuid, event.offset))


@click.command(short_help="Delete all Campaign Events")
@click.argument('campaign', type=click.UUID, required=True)
@click.pass_context
def delete_events(ctx, campaign=None):
    events = ctx.obj.get_campaign_events(campaign=campaign)
    click.echo("Deleting Campaign Events...")
    counter = 0
    for event in events.all():
        ctx.obj.delete_campaign_event(event)
        counter = counter + 1
    click.echo("Deleted {} event{}".format(counter, "s" if counter > 1 else ""))


@click.command(short_help="Create Campaign Events from CSV.")
@click.option('--csv', 'csv_file', required=True, type=click.Path(exists=True, dir_okay=False),
              help="The CSV file to create Campaign Events from")
@click.option('--campaign', type=click.UUID, required=True, help="The Campaign UUID to create Events for")
@click.pass_context
def create_events(ctx, csv_file, campaign):
    """This command loads Campaign Events from the given CSV file and POSTs them
    to the given RapidPro API with the supplied Campaign UUID."""
    click.echo("Starting Campaign Event creation...")
    try:
        create_campaign_events(csv_file, campaign, ctx.obj)
    except APIError as exc:
        click.echo("Cannot connect to supplied RapidPro API, import aborted")
        click.echo(click.style(str(exc), fg='red'))
        click.echo(click.style(str(exc.extra_data), fg='red'))
    else:
        click.echo("Completed successfully")


@click.command(short_help="Show Campaign Events")
@click.argument('event', type=click.UUID, required=True)
@click.pass_context
def show_event(ctx, event=None):
    event = ctx.obj.get_campaign_events(uuid=event).first()
    click.echo("Campaign Event:")
    click.echo({
        'uuid': event.uuid,
        'campaign': event.campaign,
        'relative_to': event.relative_to,
        'offset': event.offset,
        'unit': event.unit,
        'delivery_hour': event.delivery_hour,
        'message': event.message,
        'flow': event.flow,
        'created_on': event.created_on,
    })
