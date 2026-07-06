import asyncio
import contextlib
from pathlib import Path

from src.config.settings import CENTRAL_BROKER_CONFIG
from src.mqtt.broker import Broker
from src.nodes.actuador import ActuadorClient
from src.nodes.config import load_config
from src.nodes.simulation import Simulation


async def main() -> None:
    config_path = Path(__file__).resolve().parents[1] / "nodes" / "config.yaml"
    cfg = load_config(str(config_path))
    cfg.mqtt.broker_host = CENTRAL_BROKER_CONFIG["hostname"]
    cfg.mqtt.broker_port = CENTRAL_BROKER_CONFIG["port"]

    broker = Broker()
    simulation = Simulation(cfg)
    actuator = ActuadorClient(broker, simulation)

    simulation_task = asyncio.create_task(simulation.run())
    actuator_task = asyncio.create_task(actuator.listen())

    try:
        await simulation_task
    finally:
        actuator_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await actuator_task


if __name__ == "__main__":
    asyncio.run(main())
