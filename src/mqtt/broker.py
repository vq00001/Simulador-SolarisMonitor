from src.config.settings import CENTRAL_BROKER_CONFIG


class Broker:
    def __init__(self):
        self.hostname = CENTRAL_BROKER_CONFIG["hostname"]
        self.port = CENTRAL_BROKER_CONFIG["port"]

    def get_broker_info(self):
        return self.hostname, self.port
