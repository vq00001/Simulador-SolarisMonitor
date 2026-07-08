"""
main.py — Punto de entrada de la simulación.

Uso:
    python main.py                 # usa config.yaml en el directorio actual
    python main.py mi_config.yaml  # usa un archivo de configuración alternativo
"""
from __future__ import annotations

import asyncio
import logging
import sys

from config import load_config
from simulation import Simulation

if sys.platform == "win32":
    # aiomqtt necesita add_reader/add_writer para registrar el socket,
    # y el ProactorEventLoop (el loop por defecto en Windows) no los
    # soporta. Se fuerza el SelectorEventLoop, que sí los implementa.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


async def main() -> None:
    setup_logging()

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    cfg = load_config(config_path)

    sim = Simulation(cfg)
    await sim.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Simulación interrumpida por el usuario.")