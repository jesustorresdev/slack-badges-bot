import click
import requests
import json
import base64
from badge_cli.slack_badges_bot_client.badge import badge
#from PIL import Image

@click.group()
def cli():
    pass


@cli.command()
@click.argument('json_file', type=click.File('rb'))
@click.argument('image_file', type=click.File('rb'), required=False)
def create(json_file, image_file):
    r = badge(json_file, image_file)
    click.echo(r)

