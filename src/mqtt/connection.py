from paho.mqtt import client as mqtt_client
from src.config.settings import CENTRAL_BROKER_CONFIG

class MQTTConnection:
    def __init__(self):
        self.broker = CENTRAL_BROKER_CONFIG["broker"]
        self.port = CENTRAL_BROKER_CONFIG["port"]

    def create_client(self, client_id: str) -> mqtt_client.Client:
        client = mqtt_client.Client(
            client_id=client_id,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                print(f"{client_id} connected")
            else:
                print(f"{client_id} failed: {reason_code}")

        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client