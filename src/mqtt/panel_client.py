import aiomqtt

from src.mqtt.broker import Broker


class PanelClient:
    class Topic:
        ROOT = "solar_panel_data"
        # TEMPERATURE = ROOT + "/temperature"
        # POWER = ROOT + "/power"
        # IRRADIANCE = ROOT + "/irradiance"

    panel_counter = 1

    def __init__(self, broker: Broker):
        self.panel_id = f"panel_{PanelClient.panel_counter}"
        self.broker = broker

        # llevar la cuenta de los paneles solares conectados
        PanelClient.panel_counter += 1

    async def publish(self, message: str, topic: str = Topic.ROOT):
        topic = f"{self.panel_id}/{topic}"
        hostname, port = self.broker.get_broker_info()

        async with aiomqtt.Client(
            hostname=hostname, port=port, identifier=self.panel_id
        ) as client:
            await client.publish(topic, message)
