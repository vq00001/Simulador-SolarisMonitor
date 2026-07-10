# singleton
from datetime import datetime

import json
import aiomqtt 
from src.config.settings import SERVER_CLIENT_CONFIG, CENTRAL_BROKER_CONFIG
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
        self.cache_paneles : dict[str, int] = {}  # Diccionario para almacenar los paneles en caché
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
        payload = float(payload)
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
                print(f'el error es:{e}')
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
                    msg = "clean_panel"

            case TipoMedicionEnum.POTENCIA.value:
                if payload < 100:
                    print(f"ALERTA: La potencia del panel {panel_uid} es demasiado baja: {payload}.")
                    msg = "clean_panel"
            
            case TipoMedicionEnum.IRRADIANCIA.value:
                if payload > 1000:
                    print(f"Irradiancia alta en panel {panel_uid}")
                    msg = "clean_shadow"

        if msg:
            print(f"Enviando mensaje de retroalimentación al panel {panel_uid}: {msg}")
            await self.publish(msg, f"actuator/{panel_uid}")

    # Logica a ejecutar al recibir un mensaje
    async def do_on_message(self, message):
        topic = str(message.topic).split("/")
        payload = message.payload.decode()
        if len(topic) == 2:
            if topic[0] == "actuator":
                print(f"Se ha corregido el comportamiento del panel con id: {topic}")

            elif topic[0] == "solar_panel_data":
                panel = topic[1]
                payload = json.loads(payload)
                for clave,valor in payload.items():
                    if clave == "tiempo" or clave == "id_panel":
                        continue
                    await self.procesar_datos(panel,clave, valor)
                    await self.retroalimentar(panel, clave, valor)
                    
                

        elif len(topic) == 3:
            await self.procesar_datos(topic[2], topic[1], payload)
            await self.retroalimentar(topic[2], topic[1], payload)
        else :
            print("Mal topic detectado")
            return

    async def publish(self, message: str, topic: str):
        
        hostname, port = self.broker.get_broker_info()
        async with aiomqtt.Client(
            hostname=CENTRAL_BROKER_CONFIG["hostname"],
            port=CENTRAL_BROKER_CONFIG["port"],
            username =  SERVER_CLIENT_CONFIG["username"],
            password = SERVER_CLIENT_CONFIG["password"]
        ) as client:
            await client.publish(topic, message)

    # Función para escuchar mensajes
    async def listen(self):

        hostname, port = self.broker.get_broker_info()
       
        async with aiomqtt.Client(
            hostname=CENTRAL_BROKER_CONFIG["hostname"],
            port=CENTRAL_BROKER_CONFIG["port"],
            username =  SERVER_CLIENT_CONFIG["username"],
            password = SERVER_CLIENT_CONFIG["password"]
        ) as client:

            print("Suscribiendo a topicos...")
            # suscribirse a los topics definidos en la clase
            for t in ServerClient.topics:
                await client.subscribe(t)
            
            print("Comenzando a escuchar paquetes")

            # Llamar a funcion con logica a ejecutar al recibir un mensaje
            async for message in client.messages:
                await self.do_on_message(message)
