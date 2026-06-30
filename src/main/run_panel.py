from src.mqtt.broker import Broker
from src.mqtt.panel_client import PanelClient
import asyncio
import time

async def main():    
    broker = Broker()
    panel_client = PanelClient(broker)

    # Simular la publicación de datos del panel solar
    for i in range(5):
        message = f"Panel {panel_client.panel_id} - Power: {i * 10}W"
        print(f"Publishing message: {message}")
        await panel_client.publish(message, PanelClient.Topic.ROOT)
        await asyncio.sleep(1)  # Esperar 1 segundo antes de enviar el siguiente mensaje

if __name__ == "__main__":
    
    asyncio.run(main())