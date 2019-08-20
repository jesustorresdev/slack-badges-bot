import requests
import base64
import json

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
        return error

def persons():
    try:
        response = requests.get(config.PERSONS_LIST)
        response = response.json()
    except Exception as error:
        response = str(error)
    return response


def permissions(person_id=None):
    try:
        response = requests.get(config.PERMISSIONS_LIST)
        response = response.json()
    except Exception as error:
        response = error
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
        import traceback, sys
        traceback.print_exc(file=sys.stdout)
        response = str(error)
    return response
