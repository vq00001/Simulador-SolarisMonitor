"""
test.py

Ejecuta la simulación completa conectándose al broker MQTT,
usando las credenciales y datos de conexión de src/config/settings.py.
Se ejecuta hasta presionar Ctrl+C.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time
from pathlib import Path

# Bootstrap de sys.path: este archivo vive en src/nodes y se ejecuta con
# imports "planos" (from config import ...), pero src.config.settings
# requiere que la raíz del proyecto esté en sys.path. Se agrega acá para
# no tener que reestructurar el resto de los imports del módulo nodes.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import aiomqtt

from config import load_config
from simulation import Simulation
from src.config.settings import CENTRAL_BROKER_CONFIG, PANEL_CLIENT_CONFIG


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

async def main():

    setup_logging()

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    cfg = load_config(config_path)

    # src/config/settings.py es la fuente de verdad para la conexión real
    # al broker; se sobrescriben acá los valores del YAML (que quedan
    # como fallback para correr sin este archivo).
    cfg.mqtt.broker_host = CENTRAL_BROKER_CONFIG["hostname"]
    cfg.mqtt.broker_port = CENTRAL_BROKER_CONFIG["port"]
    cfg.mqtt.qos = CENTRAL_BROKER_CONFIG["qos"]
    cfg.mqtt.keepalive = CENTRAL_BROKER_CONFIG["keepalive"]
    # Todos los nodos (paneles) usan la misma credencial por ahora.
    cfg.mqtt.username = PANEL_CLIENT_CONFIG["username"]
    cfg.mqtt.password = PANEL_CLIENT_CONFIG["password"]

    sim = Simulation(
        cfg,
        client_cls=aiomqtt.Client,
    )

    start = time.perf_counter()

    try:

        await sim.run()

    except asyncio.CancelledError:

        elapsed = time.perf_counter() - start

        publisher = sim.publisher

        sensors = sim.panels.compute_sensors(
            solar=sim.env.solar,
            shadow=sim.env.shadow,
            ambient_temp=sim.env.ambient_temp,
        )

        print()

        print("-" * 60)
        print("ESTADÍSTICAS DE LA SIMULACIÓN")
        print("-" * 60)

        print(f"Paneles:            {sim.n_panels}")
        print(f"Mensajes enviados:  {publisher.messages_sent}")
        print(f"Bytes enviados:     {publisher.bytes_sent}")
        print(f"Tiempo ejecución:   {elapsed:.2f} s")
        print(
            f"Mensajes/segundo:   "
            f"{publisher.messages_sent/elapsed:.2f}"
        )

        print()

        print(
            f"Potencia media:      "
            f"{sensors['power'].mean():8.2f} W"
        )

        print(
            f"Temperatura media:   "
            f"{sensors['temperature'].mean():8.2f} °C"
        )

        print(
            f"Irradiancia media:   "
            f"{sensors['irradiance'].mean():8.2f} W/m²"
        )

        print(
            f"Luminosidad media:   "
            f"{sensors['luminosity'].mean():8.2f} lux"
        )

        print("-" * 60)


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Simulación interrumpida por el usuario.")