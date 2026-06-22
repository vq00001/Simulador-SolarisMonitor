from src.mqtt.connection import MQTTConnection
from src.mqtt.client_factory import MQTTClientFactory
from src.mqtt.publisher import Publisher
from src.topics.panel_topics import PanelTopics

import time

conn = MQTTConnection()
factory = MQTTClientFactory(conn)

client = factory.publisher()
pub = Publisher(client, PanelTopics.Solar.TEMPERATURE)

pub.start()

while True:

    m = input("Enter a temperature reading (or 'exit' to quit): ")
    if m == 'exit':
        break

    pub.publish(m, verbose=True)

pub.stop()