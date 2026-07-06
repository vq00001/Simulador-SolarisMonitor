# singleton
import aiomqtt

from src.mqtt.broker import Broker
from src.mqtt.definitions import UserRole
from src.mqtt.panel_client import PanelClient


class ServerClient:

    topics = [
        "+/" + PanelClient.Topic.ROOT,  # escuchar todos los paneles solares
    ]

    # Logica a ejecutar al recibir un mensaje
    async def do_on_message(self, message):
        topic = str(message.topic)
        payload = message.payload.decode()
        print(f"[{topic}] {payload}")

    # Función para escuchar mensajes
    async def listen(self, broker_host: Broker):
        hostname, port = broker_host.get_broker_info()

        async with aiomqtt.Client(
            hostname=hostname, port=port, identifier=UserRole.SERVER
        ) as client:

            # suscribirse a los topics definidos en la clase
            for t in ServerClient.topics:
                await client.subscribe(t)

            # Llamar a funcion con logica a ejecutar al recibir un mensaje
            async for message in client.messages:
                await self.do_on_message(message)
