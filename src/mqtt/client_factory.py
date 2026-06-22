import random
from src.mqtt.connection import MQTTConnection


class MQTTClientFactory:
    def __init__(self, connection: MQTTConnection):
        self.connection = connection

    def publisher(self):
        client_id = f"publisher-{random.randint(0,9999)}"
        return self.connection.create_client(client_id)

    def subscriber(self):
        client_id = f"subscriber-{random.randint(0,9999)}"
        return self.connection.create_client(client_id)