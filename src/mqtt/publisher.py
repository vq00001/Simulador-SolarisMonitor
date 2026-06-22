class Publisher:
    def __init__(self, client, topic: str):
        self.client = client
        self.topic = topic

    def start(self):
        self.client.loop_start()

    def publish(self, message, verbose=False):
        
        if verbose:
            print(f"Publishing to {self.topic}: {message}")

        result = self.client.publish(self.topic, message)

        if verbose and result[0] == 0:
            print(f"MID: {result[1]}, Sent -> {message}")

        elif verbose and result[0] != 0:
            print(f"Publish failed. mid: {result[1]}. Error code: {result[0]}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()