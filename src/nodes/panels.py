"""
panels.py — Estado de los paneles y cálculo vectorizado de sensores.

Estado interno:
    dirt_factor: (N,) float64 ∈ [0, 1]
        Acumulación de suciedad por panel, modelada como random walk con
        drift positivo. Nunca decrece sola; se resetea con clean_panel().

Todo lo demás (irradiancia, potencia, temperatura, luminosidad) se calcula
en cada tick a partir de dirt_factor + las salidas del EnvModel.
No hay estado adicional: menos memoria, más caché-friendly.
"""
from __future__ import annotations

import asyncio
import logging

import numpy as np

from config import AppConfig

logger = logging.getLogger(__name__)


class PanelSimulator:
    """
    Gestiona el estado de suciedad de los paneles y calcula las lecturas
    de todos los sensores de forma completamente vectorizada (sin loops Python).
    """

    def __init__(self, cfg: AppConfig, n_panels: int) -> None:
        self._cfg = cfg
        self._n = n_panels
        self._rng = np.random.default_rng()

        # Único vector de estado por panel
        self.dirt_factor: np.ndarray = np.zeros(n_panels, dtype=np.float64)

    # ── Actualización de estado ───────────────────────────────────────────────

    def tick_dirt(self) -> None:
        """
        Acumula suciedad en todos los paneles.

        Modelo: random walk con drift positivo
            dirt[i] += drift_rate + N(0, drift_std)

        Resultado clipeado a [0, 1] para mantener el invariante.
        """
        pc = self._cfg.panels
        delta = pc.dirt_drift_rate + self._rng.normal(
            0.0, pc.dirt_drift_std, self._n
        )
        self.dirt_factor = np.clip(self.dirt_factor + delta, 0.0, 1.0)

    # ── Cálculo de sensores ───────────────────────────────────────────────────

    def compute_sensors(
        self,
        solar: np.ndarray,
        shadow: np.ndarray,
        ambient_temp: float,
    ) -> dict[str, np.ndarray]:
        """
        Calcula las lecturas de todos los sensores vectorizadamente.

        Fórmulas:
            irradiance_i = I_max · solar_i · shadow_i · (1 − dirt_i · α) + ε
            power_i      = irradiance_i · area · η + ε
            temperature_i = T_amb + β · irradiance_i + ε
            luminosity_i  = irradiance_i · γ + ε

        Args:
            solar:        intensidad solar por panel (N,), salida de EnvModel.
            shadow:       factor de sombra por panel (N,), salida de EnvModel.
            ambient_temp: temperatura ambiente escalar (°C).

        Returns:
            dict con claves 'irradiance', 'power', 'temperature', 'luminosity'.
            Cada valor es un array (N,) float64.
        """
        pc = self._cfg.panels
        sc = self._cfg.sensors
        rng = self._rng

        # Irradiancia efectiva (W/m²)
        irradiance = (
            pc.max_irradiance
            * solar
            * shadow
            * (1.0 - self.dirt_factor * pc.max_dirt_loss)
        )
        irradiance = np.maximum(
            0.0,
            irradiance + rng.normal(0.0, sc.irradiance_std, self._n),
        )

        # Potencia eléctrica (W)
        power = np.maximum(
            0.0,
            irradiance * pc.area * pc.efficiency
            + rng.normal(0.0, sc.power_std, self._n),
        )

        # Temperatura del panel (°C): calentamiento proporcional a irradiancia
        temperature = (
            ambient_temp
            + pc.temp_irradiance_coeff * irradiance
            + rng.normal(0.0, sc.temperature_std, self._n)
        )

        # Luminosidad (lux)
        luminosity = np.maximum(
            0.0,
            irradiance * sc.lux_per_wm2
            + rng.normal(0.0, sc.luminosity_std, self._n),
        )

        return {
            "irradiance": irradiance,
            "power": power,
            "temperature": temperature,
            "luminosity": luminosity,
        }

    # ── Limpieza de paneles ───────────────────────────────────────────────────

    async def clean_panel(self, panel_id: int, delay: float = 0.0) -> None:
        """
        Resetea la suciedad de un panel individual a cero.

        Args:
            panel_id: índice del panel a limpiar.
            delay:    segundos de espera antes de limpiar (simula el tiempo
                      que tarda la operación de limpieza).

        Raises:
            IndexError: si panel_id está fuera de rango.
        """
        if not 0 <= panel_id < self._n:
            raise IndexError(
                f"Panel ID {panel_id} fuera de rango [0, {self._n - 1}]"
            )
        if delay > 0.0:
            await asyncio.sleep(delay)
        self.dirt_factor[panel_id] = 0.0
        logger.info(f"Panel {panel_id:04d} limpiado (delay={delay:.1f}s)")

    async def clean_panels(
        self,
        panel_ids: list[int] | np.ndarray,
        delay: float = 0.0,
    ) -> None:
        """
        Resetea la suciedad de un conjunto de paneles.

        Args:
            panel_ids: lista o array de índices de paneles.
            delay:     segundos de espera antes de limpiar.
        """
        if delay > 0.0:
            await asyncio.sleep(delay)
        self.dirt_factor[panel_ids] = 0.0
        logger.info(
            f"{len(panel_ids)} paneles limpiados (delay={delay:.1f}s)"
        )
