import requests
import base64
import json
import click

from PIL import Image

from badge_cli.slack_badges_bot_client import config

def create_badge(json_file, image_file):
    try:
        openbadge_json = json.load(json_file)
        if image_file:
            image_bytes = image_file.read()
            prefix = 'data:image/{};base64,'.format(str(Image.open(image_file).format).lower())
            openbadge_json['image'] = prefix + base64.encodebytes(image_bytes).decode('utf-8')
        r=requests.post(config.BADGES_CREATE, json=openbadge_json)
        return r.text
    except Exception as error:
        click.echo(error)
        return None

def persons():
    try:
        response = requests.get(config.PERSONS_LIST)
        if response.status_code != 200:
            raise Exception(response.status_code)
        response = response.json()
    except Exception as error:
        click.echo(error)
        response = None
    return response


def permissions(person_id=None):
    try:
        response = requests.get(config.PERMISSIONS_LIST)
        if response.status_code != 200:
            raise Exception(response.status_code)
        response = response.json()
    except Exception as error:
        click.echo(error)
        response = None
    return response

def update_permissions(person_id, permission_list, action):
    try:
        data = {
                "person_id": person_id,
                "permissions": permission_list,
                "action": action,
                }
        response = requests.post(config.PERSONS_PERMISSIONS_UPDATE, json=data)
        response = response.json()
    except Exception as error:
        click.echo(error)
        response = None
    return response
