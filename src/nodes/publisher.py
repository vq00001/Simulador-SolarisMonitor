"""
publisher.py — Publicación asíncrona de mensajes MQTT.

Mantiene una única conexión persistente al broker y publica todos los
paneles de forma concurrente con asyncio.gather.

Por cada panel se publican dos formas del mismo dato, en paralelo:

1. JSON combinado (topic: "{topic_prefix}/{panel_id:04d}"):
    {
        "id_panel":    int,
        "tiempo":      float,   # segundos desde epoch (Unix timestamp)
        "luminosidad": float,   # lux
        "potencia":    float,   # W
        "irradiancia": float,   # W/m²
        "temperatura": float    # °C
    }

2. Topics por métrica separada (compatibles con src/mqtt), uno por
   sensor (topic: "{topic_prefix}/{metric}/{panel_id:04d}"):
    {
        "value":     float,
        "timestamp": str
    }
   metrics: temperature, power, irradiance, luminosity
"""
from __future__ import annotations

import asyncio
import json
import logging
import time

import numpy as np
import aiomqtt

from config import AppConfig
from src.config.settings import PANEL_CLIENT_CONFIG

logger = logging.getLogger(__name__)

# Métricas publicadas también en topics individuales, además del JSON
# combinado. Los nombres coinciden con las claves del dict `sensors`
# que produce PanelSimulator.compute_sensors().
PER_METRIC_TOPICS: tuple[str, ...] = (
    "temperature",
    "power",
    "irradiance",
    "luminosity",
)


class MQTTPublisher:
    """
    Context manager asíncrono que gestiona la conexión MQTT y la publicación
    de los mensajes de todos los paneles.

    Uso:
        async with MQTTPublisher(cfg) as publisher:
            await publisher.publish_all(sensors, n_panels)
    """

    def __init__(self, cfg: AppConfig, client_cls = aiomqtt.Client) -> None:
        self._cfg = cfg
        self._client_cls = client_cls
        self._client = None  # type: ignore[assignment]

    async def __aenter__(self) -> MQTTPublisher:
        mc = self._cfg.mqtt
        self._client = self._client_cls(
            hostname=mc.broker_host,
            port=mc.broker_port,
            keepalive=mc.keepalive,
            username=CONFIG.SERVER_CLIENT_CONFIG["username"],
            password=CONFIG.SERVER_CLIENT_CONFIG["password"],
        )
        await self._client.__aenter__()
        logger.info(
            f"Conectado al broker MQTT en {mc.broker_host}:{mc.broker_port}"
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client is not None:
            await self._client.__aexit__(*args)
            logger.info("Conexión MQTT cerrada.")

    async def publish_all(
        self,
        sensors: dict[str, np.ndarray],
        n_panels: int,
    ) -> None:
        """
        Publica un mensaje JSON por cada panel de forma concurrente.

        Para QoS 0 (fire-and-forget) esto es prácticamente instantáneo.
        Para QoS 1/2 habría que controlar la concurrencia con un Semaphore.

        Args:
            sensors:  dict con arrays (N,) de irradiance, power,
                      temperature, luminosity.
            n_panels: número total de paneles.
        """
        if self._client is None:
            raise RuntimeError(
                "MQTTPublisher debe usarse como context manager asíncrono."
            )

        timestamp = round(time.time(), 3)
        mc = self._cfg.mqtt

        tasks = [
            self._publish_one(
                panel_id=i,
                timestamp=timestamp,
                sensors=sensors,
                topic_prefix=mc.topic_prefix,
                qos=mc.qos,
            )
            for i in range(n_panels)
        ]
        await asyncio.gather(*tasks)
        logger.debug(f"Publicados {n_panels} mensajes (t={timestamp})")

    # ------------ Funciones internas ------------------------------------------------------

    async def _publish_one(
        self,
        panel_id: int,
        timestamp: float,
        sensors: dict[str, np.ndarray],
        topic_prefix: str,
        qos: int,
    ) -> None:
        # 1. JSON combinado (formato original, se mantiene como fallback)
        payload = json.dumps({
            "id_panel":    panel_id,
            "tiempo":      timestamp,
            "luminosidad": round(float(sensors["luminosity"][panel_id]), 4),
            "potencia":    round(float(sensors["power"][panel_id]), 4),
            "irradiancia": round(float(sensors["irradiance"][panel_id]), 4),
            "temperatura": round(float(sensors["temperature"][panel_id]), 4),
        })
        topic = f"{topic_prefix}/{panel_id:04d}"

        # 2. Topics por métrica separada, en paralelo con el combinado
        metric_tasks = [
            self._client.publish(
                f"{topic_prefix}/{metric}/{panel_id:04d}",
                json.dumps({
                    "value": round(float(sensors[metric][panel_id]), 4),
                    "timestamp": str(timestamp),
                }),
                qos=qos,
            )
            for metric in PER_METRIC_TOPICS
        ]

        await asyncio.gather(
            self._client.publish(topic, payload, qos=qos),
            *metric_tasks,
        )