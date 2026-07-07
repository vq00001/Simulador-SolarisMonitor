# singleton
import datetime

import aiomqtt 
from src.mqtt.definitions import UserRole
from src.mqtt.panel_client import PanelClient
from src.mqtt.broker import Broker
from src.server.database.session import SessionLocal
from src.server.enums.tipos_medicion import TipoMedicionEnum
from src.server.services.medicion_services import registrar_medicion
from src.server.services.tipo_medicion_services import get_by_tipo
from src.server.services.panel_services import get_panel_by_uid, get_panel_by_uid_or_create

class ServerClient:

    topics = [
        "+/" + PanelClient.Topic.ROOT,    # escuchar todos los paneles solares
    ]
    
    async def __init__(self, broker: Broker):
        self.broker = broker
        # Se inicializan caches para evitar consultar base de datos
        self.cache_paneles : dict[str, tuple[int,int,int]] = {}  # Diccionario para almacenar los paneles en caché
        self.cache_sensores : dict[tuple[int,int], int] = {}  # Diccionario para almacenar los sensores en caché
        self.tipos = {}  # Diccionario para almacenar los tipos de medición en caché
        

    async def llenar_cache(self):
        async with SessionLocal() as session:
            for tipo in TipoMedicionEnum:
                self.tipos[tipo.value] = get_by_tipo(session,tipo.value).id

    async def get_panel_id(self, session, panel_uid: str) -> int:
        """
        Obtiene el ID del panel a partir de su UID.
        Usa la caché si existe, si no, la consulta y la registra.
        """
        panel = self.cache_paneles.get(panel_uid, 0)
        if panel == 0:
            panel = await get_panel_by_uid_or_create(session, panel_uid)
            self.cache_paneles[panel_uid] = panel.id
        
        return panel.id

    async def procesar_datos(self,panel_uid: str, tipo_medicion: str, payload: float):
        """
        Procesa los datos recibidos en el mensaje y registra la medición en la base de datos.
        """
        async with SessionLocal() as session:
            try:
                panel_id = await self.get_panel_id(session, panel_uid)
                await registrar_medicion(
                                    session,
                                    panel_id=panel_id, 
                                    tipo_medicion_id=self.tipos[tipo_medicion], 
                                    valor=payload, 
                                    timestamp=datetime.now()
                )
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    async def retroalimentar(self, panel_uid: str, tipo_medicion: str, payload: float):
        """
        Envia retroalimentación a un actuador para que repare la situacion si corresponde
        """
        msg = None
        match tipo_medicion:
            case TipoMedicionEnum.TEMPERATURA.value:
                if payload > 80:
                    print(f"ALERTA: La temperatura del panel {panel_uid} es demasiado alta: {payload}°C. Activando sistema de enfriamiento.")
                    msg = "ENFRIAR"
                elif payload < 15:
                    print(f"ALERTA: La temperatura del panel {panel_uid} es demasiado baja: {payload}°C.")
                    msg = "CALENTAR"

            case TipoMedicionEnum.LUMINOSIDAD.value:
                if payload < 100:
                    print(f"ALERTA: La luminosidad del panel {panel_uid} es demasiado baja: {payload}.")
                    msg = "AUMENTAR_LUMINOSIDAD"

                elif payload > 1000:
                    print(f"ALERTA: La luminosidad del panel {panel_uid} es demasiado alta: {payload}. Bro Wtf se cae el sol ")    
                    msg = "CORRE"

        if msg:
            print(f"Enviando mensaje de retroalimentación al panel {panel_uid}: {msg}")
            await self.publish(msg, f"{panel_uid}/actuador")

    # Logica a ejecutar al recibir un mensaje
    async def do_on_message(self, message):
        root, panel_uid, tipo_medicion = str(message.topic).split("/")
        payload = message.payload.decode()
        await self.procesar_datos(panel_uid,tipo_medicion,payload)
        await self.retroalimentar(panel_uid, tipo_medicion, payload)

    async def publish(self, message: str, topic: str):
        
        hostname, port = self.broker.get_broker_info()
        async with aiomqtt.Client(
            hostname=hostname,
            port=port,
            identifier=self.panel_id
        ) as client:
            await client.publish(topic, message)

    # Función para escuchar mensajes
    async def listen(self):

        hostname, port = self.broker.get_broker_info()
       
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