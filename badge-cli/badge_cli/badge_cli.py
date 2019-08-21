import traceback, sys
import click
import requests
import json
import base64
import badge_cli.slack_badges_bot_client as api_client

from cachetools import cached, TTLCache
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
    """Crear medallas.

    Más información en la wiki del proyecto:

    https://github.com/alu0100832211/slack-badges-bot/wiki/Creaci%C3%B3n-de-una-medalla
    """
    r = api_client.create_badge(json_file, image_file)
    click.echo(r)

#TODO: Caché no funciona siempre hace la petición
@cached(TTLCache(maxsize=1, ttl=180))
def person_byid(person_id):
    persons = api_client.persons()
    return [person for person in persons if person["id"] == person_id][0]

@cached(TTLCache(maxsize=1, ttl=180))
def persons_summary():
    persons = api_client.persons()
    return {person['id']:person['real_name'] for person in persons}

@cli.command()
@click.option('--persons', '-p', is_flag=True, default=False, help="Lista de las personas registradas")
@click.option('--permissions', '-pm', is_flag=True, help="Lista permisos disponibles o los permisos que tiene una persona")
@click.argument('person_id', required=False)
def list(persons, permissions, person_id):
    """
    Listar personas y permisos.
    """
    response = None
    if persons:
        persons = api_client.persons()
        if person_id: # Toda la informacion de una persona en concreta
            response = person_byid(person_id)
        else: # Información general de todas las personas
            response = persons_summary()
        click.echo(json.dumps(response, indent=True))
    elif permissions:
        if person_id: # Permisos de una persona concreta
            person = person_byid(person_id)
            response = {person['id']:person['permissions']}
        else: # Todos los permisos disponibles
            response = api_client.permissions()
        click.echo(json.dumps(response, indent=True))
    else: #mostrar ayuda
        with click.Context(list) as ctx:
            click.echo(list.get_help(ctx))

@cli.command()
@click.option('--set', '-s', 'set_', is_flag=True, help="Especificar los permisos de una persona")
@click.option('--add', '-a', 'add_', is_flag=True, help="Modificar los permisos de una persona")
@click.option('--remove', '-rm', 'remove_', is_flag=True, help="Quitar los permisos de una persona")
@click.argument('person_id')
@click.argument('permissions_list', nargs=-1)
def perm(set_, add_, remove_, person_id, permissions_list):
    """Modificar los permisos de una ersona.

    Más informacion en la página de la wiki:

    https://github.com/alu0100832211/slack-badges-bot/wiki/Modificar-los-permisos-de-una-persona
    """
    if set_:
        action = 'set'
    elif add_:
        action = 'add'
    elif remove_:
        action = 'remove'
    else:
        action = 'no action specified'
    permissions_list = [permission for permission in permissions_list]
    response = api_client.update_permissions(person_id, permissions_list, action)
    if response:
        click.echo(response)
"""
badgecli create oro.json oro.png
badgecli create oro.json
badgecli list --persons
badgecli list --persons person_id
badgecli list --permissions
badgecli list --permissions person_id
badgecli perm --set
"""
