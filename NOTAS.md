# Notas para aclarar algunas cosas.

##

Para que un proyecto de Python sea más sencillo de desarrollar y desplegar con las mismas versiones de paquetes
para los que se desarrollo se usa Pipenv. El Pipfile que acompaña al proyecto indica las dependencias para desarrollar
y desplegar el programa. Usando los comandos de pipenv es sencillo instalar todo lo necesario de una sola vez.

## Entidades

Aunque hay pocas entidades como para ponerlas en un solo archivo entities.py, ese archivo esta dentro del directorio
entities/ para mantener la misma estructura de directorios que con los otros componentes de la arquitectura.

Así, si el número de entidades creciera, sería sencillo ponerlas en diferentes módulos dentro de entities/.

En todo caso, para facilitar el acceso a las entidades, entities/__init__.py importa el contenido de
entities/entities.py en paquete 'entities'. Así a los badges se puede acceder como entities.Badge y no como
entities.entities.Badge.

Además no he usado UUID como tipo directamente si no EntityID. Eso facilitar sustituir fácilmente un tipo de
identificador por otro.

## Servicios

Son el nivel aplicación. Donde se implementan los casos de uso como "crear un badge" o "list todos los que hay".

El problema es que crear un badge necesita persistencia y eso es parte de la ultima capa, las de infraestructura.
Sin embargo, los niveles interiores no deben depender de los exteriores. Entonces ¿cómo lo hacemos para un servicio
use un adaptador sin depende de él? Pues usamos inyección de dependencias con el paquete punq.

En services/badge.py indico que la clase depende de EntityRepository. EntityRepository es una clase abstract.
En Python hay varias formas de definir eso pero una es heredar de abc.ABC y marcar los métodos con @abc.abstractmethod.
Así la clase no podrá ser instanciada y sólo se podrá usar para heredar desde otra clase.

EntityRepository es una clase abstracta porque ninguno de sus métodos ha sido implementado. Sirve para indicar
que cualquier repositorio de entidades que BadgeService puede usar debe respetar esa interfaz en concreto. Lo que hace
la inyección de dependencias automaticamente es hacerle llegar a BadgeService un objeto de una clase que implemente un
repositorio de verdad. Por ejemplo, le podría inyectar un objeto de EntityJsonRepository, que implementa el repositorio
usando archivos JSON.

Cómo decide punq qué inyectar, lo veremos más adelante.

## Puertos y adaptadores

En el ejemplo de la persistencia se ve claramente como conecta la capa de infraestructura con los servicios. A
EntityRepository se lo llama puerto, porque define lo que la aplicación espera si quiere usar un repositorio. Mientras
que la implementación EntityJsonRepository de EntityRepositoryPort es un adaptador. Los puertos son independientes de
la tecnología. Los adaptadores no (en el caso anterior, JSON)

Los puerto realmente son parte del nivel aplicación, junto con servicios. Los adaptadores, por el contrario son del
nivel infraestructura.

El puerto EntityRepository es un puerto secundario. Se llama así porque es uno de esos puertos que la aplicación
necesita para hacer su trabajo. Es decir, es la aplicación la que usa el puerto.

Pero hay otros puerto es son aquellos por los que la aplicación recibe comandos. Por ejemplo, el puerto de una web,
un bot o una API. Esos puertos son primarios.

En los puertos primarios la implementación están dentro de la capa de aplicación, con los servicios. Mientras que el
adaptador es cliente del puerto. Es decir, el adaptador es una clase que usa el puerto.

Por ejemplo, el adaptador api.WebService es primario porque recibe eventos del mundo y pide cosas a la aplicación.
Para hacer su trabajo no tiene que implementar un puerto sino que tiene que usar un puerto. El nuestro ejemplo
BadgeService es el puerto, porque expone a la capa de infraestructura como puede usar la aplicación. 

Es muy común que en los puertos sean siempre clases abstractas para sustituir fácilmente unas implementaciones por
otras. Pero en este caso no parece que vayamos a tener otra implementación de la interfaz de gestión de las insignias.
No tendría sentido tener una clase abstracta con la interfaz de BadgeService solo para luego heredar de ella para
implementar BadgeService.

En el caso de los puertos primarios, no siempre es necesario que sean clases abstractas o interfaces. Mientras que
para los puertos secundarios es lo más común para aprovechar la inyección de dependencias.

## WebService

api.WebService es un adaptador primario que recibe varios servicios que necesita. El constructor crea la web.Application
de aiohttp y configura las rutas llamando a self._setup_routes.

Te pego el código del que hablo porque, como verás después, al hacer la parte de Slack he optado por una forma que
hace que la clase WebService no puede tener método start(). Asi que en el repositorio hay una versión algo diferente
a la que te comento. 

~~~
"""Servicio web de gestión de la aplicación.
"""
from aiohttp import web
import json

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class WebService:

    def __init__(self, config: ConfigService, badge_service: BadgeService):
        self.config = config
        self.badge_service = badge_service
        self.app = web.Application()
        self._setup_routes()

    async def create_badge(self, request):
        # TODO: Comprobar argumentos en request y añadir manejo de errores y excepciones
        self.badge_service.create(name=request.query['name'], description=request.query['description'],
                                  criteria=request.query['criteria'], image=request.query['image'])
        return web.Response(text=json.dumps({'status': 'success'}), status=200)

    async def start(self):
        # TODO: Estudiar si es conveniente que este runner maneje las señales del sistema
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.config['HTTP_HOST'], port=self.config['HTTP_PORT'])
        await site.start()

        # site se ejecuta de forma ininterrumpida. Limpiar runner cuando site se detenga definitivamente.
        await runner.cleanup()

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge)
~~~

La única ruta que he puesto indica que un POST HTTP a /badges/create debe crear un badge con los parámetros enviados
en la petición. Esos parámetros recibido por AIOHttp se recuperan con request.query('algo').

Los TODO indican lo que falta por hacer. Por un lado create() puede fallar y lo hará con una excepción. Si eso
pasa hay que terminar el método indicado el error. Igualmente estamos confiando en que los usuarios del API no meten
la pata y ponen todos los parámetros que debe de la forma que deben hacerlo. No podemos nunca confiar en los usuarios
ni aunque el cliente del API lo hagamos nosotros mismos. Hay que comprobar que los ha indicado un valor para cada
argumento obligatorio de create().

Si estuviéramos haciendo una aplicación normal, WebServices tendría que tener un método start() que llame a
web.run_app(app). Pero no podemos hacer eso porque esa es una llamada bloqueante. Es decir, entra en un bucle infinito
donde se reciben eventos de la API y se atienden. El problema es que eso es incompatible con el API cliente de Slack
que tiene sus propios eventos y necesita su propio bucle de mensajes.

Así que todo apunta a que es mejor idea lanzar la aplicación de forma asíncrona usando web.AppRunner. El AppRunner
tiene una corrutina llamada runner(). Lo único que tenemos que hacer es que nuestro bucle de mensajes llame a esa
corrutina periódicamente para atender los eventos del WebService.

Observa que en la corrutina WebService.start() dice await site.start(). La magia del tema es que la corrutina start
hace una iteración y vuelve al bucle de mensajes (gracias al await retorna de WebService.start()). Ḿás tarde el bucle
hará que la ejecución de site.start() se repita por donde salío y vuelva a salir. Y así sucesivamente. site.start()
no terminará de verdad hasta que no le pidamos al servidor que muera. Y entonces es cuando se ejecuta la siguiente línea
de WebService.start(). La que dice runner.cleanup().

Esa es la gracia de las corrutinas en Python y otros lenguajes.

## Aplicación de Slack (I)

slack.SlackApplication sería el bot. Como api.WebService, tiene acceso director a BadgeService y otros servicios
del núcleo de la aplicación. Por lo tanto, no hay necesidad de complicar las cosas haciendo que las peticiones
vaya por el API usando request. Esa sería una opción si este bot tuviera que acceder a servicios en otro proceso
o en otra máquina (por ejemplo, porque hemos decidido diseñarla usando una arquitectura de microservicios). Pero,
como digo, no es el caso.

Al igual que el WebServices, slack.SlackApplication recibe por el constructor los puertos de la capa de aplicación
que va a usar. Es decir, BadgeService y otros.

Te pego el código del que hablo porque, como verás después, he optado por otra opción que no tiene nada que ver.
Asi que en el repositorio hay una versión muy diferente. Pero creo que la explicación merece la pena.

~~~
"""Aplicación de Slack
"""
import slack

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class SlackApplication:

    def __init__(self, config: ConfigService, badge_service: BadgeService):
        self.config = config
        self.badge_service = badge_service
        self.web_client = None
        self.rtm_client = slack.RTMClient(token=config['SLACK_APPLICATION_TOKEN'], run_async=True)
        self._setup_events()

    async def message(self, **payload):
        """Atender los mensajes dirigido a la aplicación.
        """
        if self.web_client is None:
            self.web_client = payload["web_client"]

        data = payload["data"]
        channel_id = data.get("channel")

        message_text = data['text']
        message_words = message_text.split()

        # if message_words[0] == self.id:
        #     if message_words[1] == "badges":
        #         if message_words[2] == list
        #             self.list_badges(web_client, channel_id)

    async def start(self):
        await self.rtm_client.start()

    def _setup_events(self):
        self.rtm_client.on(event="message", callback=self.message)
~~~

Respecto a la creación del objeto RTMClient pasa un poco como con el run_app() de web.Application(). Por defecto,
run_async=False, por lo que el start() se bloquea. Básicamente usa el loop que le indicas y uno global que le da
la librería asyncio y lo lanza en un bucle infinito para procesar los eventos del cliente.

Pero si le dices run_async=True, start() devuelve un futuro para que tu lo uses en tu propio loop. Es decir, en ese caso
pasarle loop al crear el cliente no sirve de nada. Mas o menos eso se entiende a leer la doc y es fácil comprobarlo
mirando el código (ventajas de que sea software libre)

Ese futuro que devuelve start() pasárselo al bucle cuando lo pongamos en marcha. Básicamente es lo mismo una función
async (corrutina) que una función normal que devuelve un futuro. El WebService.start() se define async mientras que 
SlackApplication.start() podría ser así:

~~~
 def start(self):
        return self.rtm_client.start()
~~~

Un método normal que devuelve un futuro. Como veremos más tarde que ambos se le pasan igual al bucle de mensajes de la
aplicación. En todo caso, por mantener cierto parecido entre WebService y SlackApplication, he optado porque
SlackApplication.start() sea una corrutina (async) y, entonces, en lugar de return se usa await con el futuro.

~~~
 async def start(self):
        await self.rtm_client.start()
~~~

Hay un detalle importante es la creación del slack.WebClient. En tu código se esperan los eventos en:

~~~
async def message()
~~~

ese async es correcto porque message es una corrutina. Va a ser llamando desde el bucle de mensajes que se encajar
de la ejecución de RTMClient. Pero dentro de message() llamas a métodos del objeto WebClient. Esos métodos, por defecto
son bloqueantes, no asíncronos. Así que el WebClient hará una petición a los servidores de Slack y hasta que no
devuelvan una petición y WebClient los procese, el código de message() no continuará. El problema es que message() ha
sido definido como async porque se supone que funciona de forma asíncrona. Es decir, no debe bloquearse nunca. Las
funciones que pueden bloquearse deben ser ser async o devolver un futuro para retornar temporalmente el control al
bucle de mensajes. Cuando las peticiones está completas y se puede continuar, el bucle de mensajes debe volver a saltar
a dónde se suspendió la ejecución. Mientras el bucle se encarga de atender otras peticiones, por ejemplo peticiones
del API, por medio de api.WebService, o lo que sea.

Para que slack.WebClient no sea bloqueante hay que pasarle también run_async=True. Y en cada método que uses del objeto
hay que poner delante un await.

En todo caso lo de crear bien WebClient no hay que preocuparse. Como se ve en el ejemplo, una de las cosas que trae
payload es un objeto WebClient en payload\["web_client"\]. RTMClient lo crea con las mismas opciones con las que él fue
creado, opción run_async incluida.

Mirando tu función message parece que has optado por crear un bot así:

https://api.slack.com/bot-users

pero eso parece más bien para hacer un asistente inteligente. Yo creo que tiene mas sentido usar comandos:

https://api.slack.com/slash-commands

que es algo más propio de utilidades. Eso implica un cambio de enfoque porque para eso no hace falta el RTMClient.

Y por eso hay una parte 2 de este apartado.

## Aplicación de Slack (II)

Crear un comando slash es mucho más sencillo:

https://api.slack.com/slash-commands

Básicamente en la configuración de la aplicación se debe indicar la URL (Request URL, indica la documentación) de esta
aplicación a donde Slack mandará los mensajes que envien los usuarios. En este contexto de API HTTP es lo se llaman un
webhook. En la documentación hay un buen ejemplo de los campos con los que llega la petición.

Vamos, que Slack quiere una API, como la que ya hemos hecho. Solo que en este caso la usarán ellos. Así lo dice la
documentación:

    When a slash command is invoked, Slack sends an HTTP POST to the Request URL you specified above. This request
    contains a data payload describing the source command and who invoked it, like a really detailed knock at the door.

Así que solo tenemos que crear otra aplicación con AIOHttp, similar a api.WebService. 

Como nota curiosa, para hacer un webhook o una API no hace falta AIOHttp. Con Flask nos hubiera servidor. Como
recordarás nos metimos con AIOHttp porque lo necesitaba la librería SlackClient. Bien, pues al optar por esta hacer
un comando slash ya no necesitamos esa librería. Ahora podríamos volver a plantearnos usar Flask. Sin embargo,
no vamos a tirar todo lo que hemos hecho ¿verdad?

Bueno, en el nuevo slack.SlackApplication se ve la idea. En este caso no se usa ningún await porque las acciones
son inmeditas. Si, por ejemplo, usáramos una base de datos, deberíamos usar una librería de base de datos asíncrona
y await por todos lados.

El asunto es que ahora tenemos dos aplicaciones AIOHttp que deben funcionar el mismo servidor y puerto. En realidad,
que deben funcionar en la misma aplicación AIOHttp. No tiene sentido SlackApplication y WebService tengan cada uno
su start() porque en realidad deberíamos de integrarlas para que funcionen como la misma web.Application, solo que
en URL que no entren en conflicto. Por eso he quitado el start() a api.WebService y he puesto parte de su código
en el modulo app.py. Ese será el módulo principal de la aplicación.

Además, como solo hay una aplicación, no hace falta al AppRunner, que era para poder crear 
nuestro propio bucle de mensajes que también manejara RTMClient. Ahora todo está en manos de web.Application y
del bucle que crea web.run_app()

En este módulo se crea una web.Application y tanto WebService como SlackApplication se añaden como subaplicaciones. 

## Configuración

El proveedor de configuración también es un servicio. En esta caso le he indicado que herede UserDict para que comporte
como un diccionario. Así es más sencillo acceder a las variables de configuración.

## Metadatos

Verás que los archivos tienen información sobre el autor, licencia, fecha. Lo usual en Python es indicar así el autor o
autores. Algunos editores se pueden configurar para que lo hagan automáticamente.
