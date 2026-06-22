import time

class Subscriber:
    def __init__(self, client, topic: str):
        self.client = client
        self.topic = topic

    def start(self):
        def on_message(client, userdata, msg):
            payload = msg.payload.decode()
            print(f"[{msg.topic}] {payload}")

            with open(f"{client._client_id.decode()}.log", "a") as f:
                f.write(f"{time.time()} | {msg.topic} | {payload}\n")

        self.client.subscribe(self.topic)
        self.client.on_message = on_message
        self.client.loop_forever()