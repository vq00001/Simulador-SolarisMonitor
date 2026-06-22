from src.mqtt.connection import MQTTConnection
from src.mqtt.client_factory import MQTTClientFactory
from src.mqtt.suscriber import Subscriber
from src.topics.panel_topics import PanelTopics

conn = MQTTConnection()
factory = MQTTClientFactory(conn)

client = factory.subscriber()
sub = Subscriber(client, PanelTopics.Solar.TEMPERATURE)

sub.start()