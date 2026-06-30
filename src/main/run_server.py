import asyncio
from src.mqtt.broker import Broker
from src.mqtt.server_client import ServerClient

async def main():   
    broker = Broker()
    server = ServerClient()
    await server.listen(broker)

if __name__ == "__main__":
    asyncio.run(main())