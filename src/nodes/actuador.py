from __future__ import annotations

import json
import logging
import random
from typing import Any

import aiomqtt

from src.mqtt.broker import Broker
from src.mqtt.definitions import UserRole
from .simulation import Simulation

logger = logging.getLogger(__name__)


class ActuadorClient:
    """
    Escucha alertas o comandos MQTT y ejecuta acciones correctivas sobre la simulación.

    Acciones soportadas:
    - clean_panel: limpia un panel individual
    - clean_cluster: limpia todos los paneles de un cluster
    - clear_shadows: elimina todos los eventos de sombreado activos
    """

    topics = [
        "solar_panel_alerts/#",
        "solar_panel_control/#",
    ]

    def __init__(self, broker: Broker, simulation: Simulation):
        self.broker = broker
        self.broker_hostname, self.broker_port = broker.get_broker_info()
        self.simulation = simulation

    async def do_on_message(self, message: aiomqtt.Message) -> None:
        topic = str(message.topic)
        payload = message.payload.decode().strip()

        command = self._decode_command(topic, payload)
        if command is None:
            logger.warning("Mensaje ignorado en %s: %s", topic, payload)
            return

        action = str(command["action"])
        target_id = command.get("target_id")
        delay = float(command.get("delay", 0.0))

        logger.info(
            "Comando recibido: action=%s target_id=%s delay=%s topic=%s",
            action,
            target_id,
            delay,
            topic,
        )

        if action == "clean_panel":
            if target_id is None:
                logger.warning("clean_panel requiere target_id")
                return
            await self.simulation.clean_panel(int(target_id), delay)
            return

        if action == "clean_cluster":
            if target_id is None:
                logger.warning("clean_cluster requiere target_id")
                return
            await self.simulation.clean_cluster(int(target_id), delay)
            return

        if action == "clear_shadows":
            await self.simulation.clear_shadow_events(delay)
            return

        logger.warning("Acción no soportada: %s", action)

    async def listen(self) -> None:
        async with aiomqtt.Client(
            hostname=self.broker_hostname,
            port=self.broker_port,
            identifier=UserRole.ACTUADOR
        ) as client:
            for topic in ActuadorClient.topics:
                await client.subscribe(topic)

            async for message in client.messages:
                await self.do_on_message(message)

    def _decode_command(self, topic: str, payload: str) -> dict[str, Any] | None:
        command: dict[str, Any]

        if payload:
            try:
                raw = json.loads(payload)
                if not isinstance(raw, dict):
                    return None
                command = raw
            except json.JSONDecodeError:
                command = {"action": payload.lower()}
        else:
            command = {}

        topic_parts = [part for part in topic.split("/") if part]
        if len(topic_parts) >= 2 and topic_parts[-2] in {"panel", "cluster"}:
            command.setdefault("action", f"clean_{topic_parts[-2]}")
            try:
                command.setdefault("target_id", int(topic_parts[-1]))
            except ValueError:
                pass

        if "action" not in command:
            return None

        if command.get("delay") is None and command["action"] in {
            "clean_panel",
            "clean_cluster",
            "clear_shadows",
        }:
            command["delay"] = random.uniform(1.0, 5.0)

        return command