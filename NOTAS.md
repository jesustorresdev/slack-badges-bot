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

La única ruta que he puesto indica que un POST HTTP a /badges/create debe crear un badge con los parámetros enviados
en la petición. Esos parámetros recibido por AIOHttp se recuperan con request.query('algo').

Los TODO indican lo que falta por hacer. Por un lado create() puede fallar y lo hará con una excepción. Si eso
pasa hay que terminar el método indicado el error. Igualmente estamos confiando en que los usuarios del API no meten
la pata y ponen todos los parámetros que debe de la forma que deben hacerlo. No podemos nunca confiar en los usuarios
ni aunque el cliente del API lo hagamos nosotros mismos. Hay que comprobar que los ha indicado un valor para cada
argumento obligatorio de create().

Si estuviéramos haciendo una aplicación normal, WebServices tendría que tener un método start() que llame a
app.run_app(). Pero no podemos hacer eso porque esa es una llamada bloqueante. Es decir, entra en un bucle infinito
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

## Configuración

## Metadatos

Verás que los archivos tienen información sobre el autor, licencia, fecha. Lo usual en Python es indicar así el autor o
autores. Algunos editores se pueden configurar para que lo hagan automáticamente.
