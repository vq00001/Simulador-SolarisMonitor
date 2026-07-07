# singleton
from datetime import datetime

import json
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
        "solar_panel_data" + "/+",  # escuchar todos los paneles solares
        "actuator" + "/response" + "/+"
    ]
    
    def __init__(self, broker: Broker):
        self.broker = broker
        # Se inicializan caches para evitar consultar base de datos
        self.cache_paneles : dict[str, tuple[int,int,int]] = {}  # Diccionario para almacenar los paneles en caché
        self.cache_sensores : dict[tuple[int,int], int] = {}  # Diccionario para almacenar los sensores en caché
        self.tipos = {}  # Diccionario para almacenar los tipos de medición en caché
        

    async def llenar_cache(self):
        async with SessionLocal() as session:
            for tipo in TipoMedicionEnum:
                self.tipos[tipo.value] = (await get_by_tipo(session,tipo.value)).id

    async def get_panel_id(self, session, panel_uid: str) -> int:
        """
        Obtiene el ID del panel a partir de su UID.
        Usa la caché si existe, si no, la consulta y la registra.
        """
        panel = self.cache_paneles.get(panel_uid, 0)
        if panel == 0:
            panel = await get_panel_by_uid_or_create(session, panel_uid)
            panel = panel.id
            self.cache_paneles[panel_uid] = panel
        
        return panel


    async def procesar_datos(self,panel_uid: str, tipo_medicion: str, payload: float):
        """
        Procesa los datos recibidos en el mensaje y registra la medición en la base de datos.
        """
        payload = int(payload)
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
                await session.commit()
                print("Commit hecho")
            except Exception as e:
                session.rollback()
                raise e

    async def retroalimentar(self, panel_uid: str, tipo_medicion: str, payload: float):
        """
        Envia retroalimentación a un actuador para que repare la situacion si corresponde
        """
        msg = None
        payload = int(payload)
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
        topic = str(message.topic).split("/")
        payload = message.payload.decode()
        if len(topic) == 2:
            if topic[0] == "actuator":
                pass

            elif topic[0] == "solar_panel_data":
                panel = topic[1]
                payload = json.loads(payload)
                for clave,valor in payload.items():
                    await self.procesar_datos(panel,clave, valor)
                    await self.retroalimentar(panel, clave, valor)
                

        elif len(topic) == 3:
            await self.procesar_datos(topic[2], topic[1], payload)
            await self.retroalimentar(topic[2], topic[1], payload)
        else :
            print("Mal topic detectado")
            return;

    async def publish(self, message: str, topic: str):
        
        hostname, port = self.broker.get_broker_info()
        async with aiomqtt.Client(
            hostname="localhost",
            port=1883
        ) as client:
            await client.publish(topic, message)

    # Función para escuchar mensajes
    async def listen(self):

        hostname, port = self.broker.get_broker_info()
       
        async with aiomqtt.Client(
            hostname="localhost",
            port=1883, 
        ) as client:

            print("VOY A EMPEZAR A SUSCRIBIRME A COSAS")
            # suscribirse a los topics definidos en la clase
            for t in ServerClient.topics:
                await client.subscribe(t)
            
            print("VOY A EMPEZAR A ESUCHAR")

            # Llamar a funcion con logica a ejecutar al recibir un mensaje
            async for message in client.messages:
                await self.do_on_message(message)

            print("Termine de escuchar?")