import traceback, sys
import click
import requests
import json
import base64
import badge_cli.slack_badges_bot_client as api_client
#from PIL import Image

@click.group()
@click.option('--apihelp', is_flag=True, help='Solicita ayuda de la API')
def cli(apihelp):
    """Comando administrar la aplicacion Slack-Badges-Bot

    Información sobre cada comando:

    badgecli [comando] --help
    """
    if apihelp:
        click.echo('Ayuda!!')


@cli.command()
@click.argument('json_file', type=click.File('rb'))
@click.argument('image_file', type=click.File('rb'), required=False)
def create(json_file, image_file):
    """Comando para crear medallas.

    Más información en la wiki del proyecto:

    https://github.com/alu0100832211/slack-badges-bot/wiki/Creaci%C3%B3n-de-una-medalla
    """
    r = api_client.create_badge(json_file, image_file)
    click.echo(r)

def person_byid(person_id):
    persons = api_client.persons()
    return [person for person in persons if person["id"] == person_id][0]

def persons_summary():
    persons = api_client.persons()
    return {person['id']:person['real_name'] for person in persons}

@cli.command()
@click.option('--persons', '-p', is_flag=True, default=False, help="Lista de las personas registradas")
@click.option('--permissions', '-pm', is_flag=True, help="Lista permisos disponibles o los permisos que tiene una persona")
@click.argument('person_id', required=False)
def list(persons, permissions, person_id):
    """
    Comando para listar personas y permisos.
    """
    try:
        if persons:
            persons = api_client.persons()
            if person_id: # Toda la informacion de una persona en concreta
                response = person_byid(person_id)
            else: # Información general de todas las personas
                response = persons_summary()
        elif permissions:
            if person_id: # Permisos de una persona concreta
                person = person_byid(person_id)
                response = {person['id']:person['permissions']}
            else: # Todos los permisos disponibles
                response = api_client.permissions()

    except Exception as error:
        traceback.print_exc(file=sys.stdout)
        response = str(error)

    if isinstance(response, dict):
        response = json.dumps(response,
                indent=True,
                ensure_ascii=False).encode("utf-8")
    click.echo(response)

@cli.command()
@click.option('--permissions', '-pm', help="modificar los permisos de una persona")
@click.argument('person_id')
@click.argument('permissions', nargs=-1)
def add(json_file):
    """Comando para modificar los permisos de una ersona.

    Más informacion en la página de la wiki:

    https://github.com/alu0100832211/slack-badges-bot/wiki/Modificar-los-permisos-de-una-persona
    """
    response = api_client.add_permission(person_id, permission)
    click.echo(response)

@cli.command()
@click.argument('--permissions', '-pm', help="Quitar permisos")
@click.argument('person_id')
def remove():
    """Comando para quitar permisos a una persona

    Más informacion en la página de la wiki:

    https://github.com/alu0100832211/slack-badges-bot/wiki/Modificar-los-permisos-de-una-persona
    """
    raise NotImplementedError

"""
badgecli create oro.json oro.png
badgecli create oro.json
badgecli list --persons
badgecli list --persons person_id
badgecli list --permissions
badgecli list --permissions person_id
badgecli set --permissions person_id permission permission permission
"""
