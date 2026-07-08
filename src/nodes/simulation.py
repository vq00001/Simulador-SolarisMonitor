"""
simulation.py — Encargado del loop principal.

Cada tick real de tick_rate segundos:
  1. Actualiza el ambiente (ciclo solar, temperatura, eventos de sombra)
  2. Acumula suciedad en los paneles
  3. Calcula todos los sensores vectorizadamente
  4. Publica por MQTT si ha pasado publish_rate segundos reales

El tiempo simulado avanza a tick_rate × time_scale segundos por tick,
lo que permite comprimir el ciclo día/noche para pruebas.
"""

from __future__ import annotations

import asyncio
import logging

import aiomqtt
import numpy as np

from .config import AppConfig
from .environment import EnvModel
from .panels import PanelSimulator
from .publisher import MQTTPublisher

logger = logging.getLogger(__name__)


class Simulation:
    """
    Coordina EnvModel, PanelSimulator y MQTTPublisher en el tick loop.

    Expone también métodos de actuación (limpieza de paneles individuales/clusters).
    """

    def __init__(self, cfg: AppConfig, client_cls=aiomqtt.Client) -> None:
        self._cfg = cfg
        self._client_cls = client_cls
        self.n_panels: int = cfg.total_panels

        # Mapeo panel → cluster: int array (N,)
        self.panel_cluster: np.ndarray = self._build_cluster_map()

        # Componentes principales
        self.env = EnvModel(cfg, self.n_panels, self.panel_cluster)
        self.panels = PanelSimulator(cfg, self.n_panels)

        logger.info(
            f"Simulación inicializada: {self.n_panels} paneles en "
            f"{len(cfg.clusters)} clusters."
        )

    # ------------ Loop principal de la simulación -----------------------------------

    async def run(self) -> None:
        """
        Ejecuta el loop principal hasta que se cumpla cfg.duration
        o el usuario interrumpa con Ctrl+C.
        """
        sc = self._cfg.simulation
        tick_dt_real = sc.tick_rate             # segundos reales por tick
        sim_dt = tick_dt_real * sc.time_scale   # segundos simulados por tick
        publish_interval = sc.publish_rate      # segundos reales entre publishes

        t_sim: float = 0.0
        t_real_last_publish: float = -publish_interval  # fuerza publish en t=0

        logger.info(
            f"Iniciando: tick={tick_dt_real}s, publish={publish_interval}s, "
            f"time_scale={sc.time_scale}x"
            + (
                f", duración={sc.duration}s"
                if sc.duration
                else ", sin límite de tiempo"
            )
        )

        loop = asyncio.get_running_loop()

        self.publisher = MQTTPublisher(self._cfg, client_cls=self._client_cls)

        async with self.publisher as publisher:
            t_real_start = loop.time()

            while True:
                tick_wall_start = loop.time()
                t_real = tick_wall_start - t_real_start

                # 1. Actualizar ambiente
                self.env.update(t_sim, sim_dt)

                # 2. Acumular suciedad
                self.panels.tick_dirt()

                # 3. Calcular sensores
                sensors = self.panels.compute_sensors(
                    solar=self.env.solar,
                    shadow=self.env.shadow,
                    ambient_temp=self.env.ambient_temp,
                )

                # 4. Publicar si ha pasado el intervalo real
                if t_real - t_real_last_publish >= publish_interval:
                    await publisher.publish_all(sensors, self.n_panels)
                    t_real_last_publish = t_real

                # 5. Comprobar condición de parada
                if sc.duration is not None and t_real >= sc.duration:
                    logger.info(
                        f"Simulación finalizada tras {t_real:.1f}s reales "
                        f"({t_sim:.1f}s simulados)."
                    )
                    break

                # Avanzar tiempo simulado
                t_sim += sim_dt

                # Dormir el tiempo restante del tick
                tick_elapsed = loop.time() - tick_wall_start
                sleep_time = max(0.0, tick_dt_real - tick_elapsed)
                await asyncio.sleep(sleep_time)

    # ------------ Funciones de actuación (limpieza de paneles) -----------------------------

    async def clean_panel(self, panel_id: int, delay: float = 0.0) -> None:
        """
        Limpia un panel individual.

        Args:
            panel_id: índice del panel.
            delay:    segundos reales de espera antes de limpiar.
        """
        await self.panels.clean_panel(panel_id, delay)

    async def clean_cluster(self, cluster_id: int, delay: float = 0.0) -> None:
        """
        Limpia todos los paneles de un cluster.

        Args:
            cluster_id: ID del cluster (según config.yaml).
            delay:      segundos reales de espera antes de limpiar.
        """
        panel_ids = self.get_cluster_panels(cluster_id)
        if len(panel_ids) == 0:
            logger.warning(f"Cluster {cluster_id} no tiene paneles asignados.")
            return
        await self.panels.clean_panels(panel_ids, delay)

    async def clear_shadow_events(self, delay: float = 0.0) -> None:
        """
        Elimina todos los eventos de sombra activos.

        Esto simula una corrección del ambiente, por ejemplo una nube que se disipa.
        """
        if delay > 0.0:
            await asyncio.sleep(delay)
        self.env.clear_shadow_events()
        logger.info(f"Eventos de sombra eliminados (delay={delay:.1f}s)")

    def get_cluster_panels(self, cluster_id: int) -> np.ndarray:
        """Devuelve los índices de los paneles pertenecientes al cluster dado."""
        return np.where(self.panel_cluster == cluster_id)[0]

    # ----------- Funciones internas ------------------------------------------------------

    def _build_cluster_map(self) -> np.ndarray:
        """
        Construye el array panel_cluster: panel_cluster[i] = cluster_id del panel i.
        Los paneles se asignan secuencialmente según el orden de clusters en el YAML.
        """
        mapping = np.empty(self.n_panels, dtype=np.int64)
        offset = 0
        for cluster in self._cfg.clusters:
            mapping[offset : offset + cluster.panel_count] = cluster.id
            offset += cluster.panel_count
        return mapping
