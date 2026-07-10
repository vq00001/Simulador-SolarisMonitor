import asyncio
from src.mqtt.broker import Broker
from src.server.handlers.server_client import ServerClient
from dotenv import load_dotenv

async def main():   
    load_dotenv()
    broker = Broker()
    server = ServerClient(broker)
    await server.llenar_cache()
    await server.listen()

if __name__ == "__main__":
    asyncio.run(main())