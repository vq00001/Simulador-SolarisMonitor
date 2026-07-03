# singleton
import aiomqtt 
from src.mqtt.definitions import UserRole
from src.mqtt.panel_client import PanelClient
from src.mqtt.broker import Broker
from src.server.enums.tipos_medicion import TipoMedicionEnum
from src.server.services.tipo_medicion_services import get_by_tipo
from src.server.services.panel_services import get_panel_by_uid

class ServerClient:

    topics = [
        "+/" + PanelClient.Topic.ROOT,    # escuchar todos los paneles solares
    ]
    
    def __init__(self):
        # Se inicializan caches para evitar consultar base de datos
        self.cache_paneles : dict[str, tuple[int,int,int]] = {}  # Diccionario para almacenar los paneles en caché
        self.cache_sensores : dict[tuple[int,int], int] = {}  # Diccionario para almacenar los sensores en caché
        self.tipos = {}  # Diccionario para almacenar los tipos de medición en caché
        for tipo in TipoMedicionEnum:
            self.tipos[tipo.value] = get_by_tipo(tipo.value).id

    def procesar_datos(session, msg):
        """
        Procesa los datos recibidos en el mensaje y registra la medición en la base de datos.
        """
        topic = str(msg.topic)
        _, panel_uid, tipo_medicion = topic.split("/")
        payload = msg.payload.decode()

        panel_id = get_panel_id(session, panel_uid)
        #Buscar sensor con tipo y panel_id
        sensor = session.query(Sensor).filter_by(panel_id=panel_id, tipo_medicion_id=tipo_medicion).first()

    
    # Logica a ejecutar al recibir un mensaje
    async def do_on_message(self, message):
        topic = str(message.topic)
        payload = message.payload.decode()
        print(f"[{topic}] {payload}")

    # Función para escuchar mensajes
    async def listen(self, broker_host: Broker):

        hostname, port = broker_host.get_broker_info()
       
        async with aiomqtt.Client(
            hostname=hostname,
            port=port,
            identifier=UserRole.SERVER
        ) as client:

            # suscribirse a los topics definidos en la clase
            for t in ServerClient.topics:
                await client.subscribe(t)

            # Llamar a funcion con logica a ejecutar al recibir un mensaje
            async for message in client.messages:
                await self.do_on_message(message)