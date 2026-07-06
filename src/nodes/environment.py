"""
environment.py — Modelo ambiental global.

Gestiona:
  - Ciclo solar día/noche por cluster (onda seno con desfase φ (phi))
  - Temperatura del ambiente diaria
  - Eventos estocásticos de sombreado (nubes, aviones, etc.)

Los outputs son arrays (N,) de float64 que el PanelSimulator consume
directamente sin copias intermedias.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from config import AppConfig

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
#  Evento de sombreado
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ShadowEvent:
    """
    Representa un evento activo de sombreado sobre un subconjunto de paneles.

    Atributos:
        panel_mask:  bool (N,) — qué paneles están afectados.
        intensity:   fracción de luz solar bloqueada ∈ [0, 1].
        remaining:   segundos simulados que le quedan al evento.
    """
    panel_mask: np.ndarray
    intensity: float
    remaining: float


# ──────────────────────────────────────────────────────────────────────────────
#  Modelo ambiental
# ──────────────────────────────────────────────────────────────────────────────

class EnvModel:
    """
    Actualiza el estado ambiental en cada tick y expone tres propiedades:
        .solar        → intensidad solar por panel ∈ [0, 1]
        .shadow       → factor de sombreado combinado por panel ∈ [0, 1]
        .ambient_temp → temperatura ambiente escalar (°C)
    """

    def __init__(
        self,
        cfg: AppConfig,
        n_panels: int,
        panel_cluster: np.ndarray,
    ) -> None:
        """
        Args:
            cfg:           configuración completa.
            n_panels:      número total de paneles.
            panel_cluster: int (N,) — índice de cluster para cada panel.
        """
        self._cfg = cfg
        self._n = n_panels
        self._panel_cluster = panel_cluster
        self._rng = np.random.default_rng()

        # Desfase de fase solar por panel (derivado del cluster al que pertenece)
        phi_by_cluster: dict[int, float] = {
            c.id: c.phi_offset for c in cfg.clusters
        }
        self._phi: np.ndarray = np.array(
            [phi_by_cluster[cid] for cid in panel_cluster],
            dtype=np.float64,
        )

        # Lista de eventos de sombreado activos
        self._events: list[ShadowEvent] = []

        # Salidas cacheadas, actualizadas en cada tick
        self._solar: np.ndarray = np.zeros(n_panels, dtype=np.float64)
        self._shadow: np.ndarray = np.ones(n_panels, dtype=np.float64)
        self._ambient_temp: float = cfg.environment.t_ambient_base

    # ------------ Interfaz pública ------------------------------------------------------

    def update(self, t_sim: float, dt: float) -> None:
        """
        Avanza el ambiente un tick de dt segundos simulados.

        Args:
            t_sim: tiempo simulado acumulado (segundos).
            dt:    incremento de tiempo simulado por tick.
        """
        self._update_solar(t_sim)
        self._update_ambient_temp(t_sim)
        self._tick_events(dt)
        self._spawn_events(dt)
        self._rebuild_shadow()

    @property
    def solar(self) -> np.ndarray:
        """Intensidad solar fraccional por panel ∈ [0, 1]."""
        return self._solar

    @property
    def shadow(self) -> np.ndarray:
        """Factor de sombra combinado por panel ∈ [0, 1]."""
        return self._shadow

    @property
    def ambient_temp(self) -> float:
        """Temperatura ambiente actual (°C)."""
        return self._ambient_temp

    @property
    def active_event_count(self) -> int:
        """Número de eventos de sombreado activos en este momento."""
        return len(self._events)

    # ------------ Funciones internas ------------------------------------------------------

    def _update_solar(self, t_sim: float) -> None:
        """
        Ciclo día-noche modelado como una onda seno desplazada:

            solar_i(t) = max(0, sin(2π·(t mod T)/T − π/2 + φ_i))

        El término −π/2 centra el pico al mediodía (t = T/4).
        """
        T = self._cfg.environment.day_period
        self._solar = np.maximum(
            0.0,
            np.sin(2.0 * np.pi * (t_sim % T) / T - np.pi / 2.0 + self._phi),
        )

    def _update_ambient_temp(self, t_sim: float) -> None:
        """Temperatura ambiente: onda seno que sigue al ciclo solar."""
        env = self._cfg.environment
        T = env.day_period
        self._ambient_temp = (
            env.t_ambient_base
            + env.t_ambient_amplitude
            * np.sin(2.0 * np.pi * t_sim / T - np.pi / 2.0)
        )

    def _tick_events(self, dt: float) -> None:
        """Decrementa los timers y elimina eventos expirados."""
        for event in self._events:
            event.remaining -= dt
        self._events = [e for e in self._events if e.remaining > 0.0]

    def _spawn_events(self, dt: float) -> None:
        """
        Genera nuevos eventos de sombreado para cada cluster.

        La llegada sigue un proceso de Poisson con tasa rate_per_second:
            P(evento en dt) = 1 − exp(−rate · dt)

        La intensidad sigue una Beta(α, β) ∈ [0, 1].
        La duración sigue una Exponencial(mean) con piso en min_duration.
        Los paneles afectados son todo el cluster o un subconjunto aleatorio.
        """
        ec = self._cfg.events
        rng = self._rng

        for cluster in self._cfg.clusters:
            p_spawn = 1.0 - np.exp(-ec.rate_per_second * dt)
            if rng.random() >= p_spawn:
                continue

            cluster_panels = np.where(self._panel_cluster == cluster.id)[0]
            if len(cluster_panels) == 0:
                continue

            # Paneles afectados: cluster completo o subconjunto
            if rng.random() < ec.whole_cluster_prob:
                affected = cluster_panels
            else:
                n_affected = int(rng.integers(1, max(2, len(cluster_panels))))
                affected = rng.choice(cluster_panels, size=n_affected, replace=False)

            mask = np.zeros(self._n, dtype=bool)
            mask[affected] = True

            intensity = float(rng.beta(ec.beta_alpha, ec.beta_beta))
            duration = max(
                ec.min_duration,
                float(rng.exponential(ec.exp_mean_duration)),
            )

            self._events.append(ShadowEvent(
                panel_mask=mask,
                intensity=intensity,
                remaining=duration,
            ))

            logger.debug(
                f"[{cluster.name}] Nuevo evento: intensidad={intensity:.2f}, "
                f"duración={duration:.1f}s, paneles={len(affected)}"
            )

    def _rebuild_shadow(self) -> None:
        """
        Recalcula el factor de sombra combinando todos los eventos activos
        de forma multiplicativa:

            shadow_i = ∏(1 − intensity_k)  para k activo sobre panel i

        Dos sombras del 50% dejan pasar el 25%, que es físicamente correcto.
        """
        shadow = np.ones(self._n, dtype=np.float64)
        for event in self._events:
            shadow[event.panel_mask] *= (1.0 - event.intensity)
        self._shadow = shadow

    def clear_shadow_events(self) -> None:
        """Elimina todos los eventos de sombreado activos y restablece la sombra."""
        self._events.clear()
        self._shadow = np.ones(self._n, dtype=np.float64)
