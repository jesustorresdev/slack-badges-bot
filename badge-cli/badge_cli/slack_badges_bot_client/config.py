import configparser
config  = configparser.ConfigParser()
config.read('config.ini') # Duda: por qué no ../config.ini ?
API_URL = config['client']['server']
AUTH = (config['client']['user'], config['client']['password'])

# URLs de funcionalidades
BADGES_CREATE = API_URL + '/badges/create'
PERSONS_LIST = API_URL + '/persons/list'
PERMISSIONS_LIST = API_URL + '/persons/permissions/list'
PERSONS_PERMISSIONS_UPDATE = API_URL + '/persons/permissions/update'
