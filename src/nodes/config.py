"""
config.py — Dataclasses de configuración y carga desde YAML.

Cada sección del YAML corresponde a un dataclass.
Los campos con default permiten omitirlos en el YAML.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import yaml


# ──────────────────────────────────────────────────────────────────────────────
#  Secciones de configuración
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SimulationConfig:
    tick_rate: float = 0.1          # Segundos reales entre ticks de ambiente
    publish_rate: float = 5.0       # Segundos reales entre publicaciones MQTT
    time_scale: float = 1.0         # Multiplicador de velocidad de simulación
    duration: Optional[float] = None  # Duración en segundos reales; None = ∞


@dataclass
class EnvironmentConfig:
    day_period: float = 86400.0        # Segundos simulados por día
    t_ambient_base: float = 25.0       # Temperatura base (°C)
    t_ambient_amplitude: float = 10.0  # Amplitud de variación térmica (°C)


@dataclass
class PanelPhysicsConfig:
    area: float = 1.72               # Área del panel (m²)
    efficiency: float = 0.20         # Eficiencia de conversión
    max_irradiance: float = 1000.0   # Irradiancia pico (W/m²)
    max_dirt_loss: float = 0.30      # Pérdida máxima por suciedad [0, 1]
    dirt_drift_rate: float = 0.0001  # Drift medio de acumulación de suciedad
    dirt_drift_std: float = 0.00005  # Ruido en la acumulación de suciedad
    temp_irradiance_coeff: float = 0.03  # Calentamiento (°C por W/m²)


@dataclass
class SensorNoiseConfig:
    lux_per_wm2: float = 93.0      # Conversión irradiancia → luminosidad
    irradiance_std: float = 2.0    # Ruido de medición (W/m²)
    temperature_std: float = 0.3   # Ruido de medición (°C)
    luminosity_std: float = 5.0    # Ruido de medición (lux)
    power_std: float = 0.5         # Ruido de medición (W)


@dataclass
class EventConfig:
    rate_per_second: float = 0.005    # Tasa de eventos de sombra por cluster/s
    beta_alpha: float = 2.0           # α de la distribución Beta (intensidad)
    beta_beta: float = 5.0            # β de la distribución Beta (intensidad)
    exp_mean_duration: float = 10.0   # Duración media del evento (s simulados)
    min_duration: float = 1.0         # Duración mínima del evento (s simulados)
    whole_cluster_prob: float = 0.7   # P(afecta al cluster completo)


@dataclass
class MQTTConfig:
    # Valores por defecto alineados con src/config/settings.py
    # (CENTRAL_BROKER_CONFIG) y src/mqtt/panel_client.py (Topic.ROOT).
    # username/password quedan como fallback: el punto de entrada que
    # use src.config.settings puede sobrescribirlos en tiempo de
    # ejecución (ver test_publisher.py).
    broker_host: str = "broker-vm"
    broker_port: int = 8883
    topic_prefix: str = "solar_panel_data"
    qos: int = 0
    keepalive: int = 60
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = False   # True si el broker exige TLS en broker_port


@dataclass
class ClusterConfig:
    id: int
    name: str
    phi_offset: float   # Desfase de fase en el ciclo solar (radianes)
    panel_count: int


# ──────────────────────────────────────────────────────────────────────────────
#  Configuración raíz
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class AppConfig:
    simulation: SimulationConfig
    environment: EnvironmentConfig
    panels: PanelPhysicsConfig
    sensors: SensorNoiseConfig
    events: EventConfig
    mqtt: MQTTConfig
    clusters: list[ClusterConfig]

    @property
    def total_panels(self) -> int:
        return sum(c.panel_count for c in self.clusters)


# ──────────────────────────────────────────────────────────────────────────────
#  Carga desde YAML
# ──────────────────────────────────────────────────────────────────────────────

def load_config(path: str) -> AppConfig:
    """Lee el archivo YAML y construye el AppConfig."""
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return AppConfig(
        simulation=SimulationConfig(**raw.get("simulation", {})),
        environment=EnvironmentConfig(**raw.get("environment", {})),
        panels=PanelPhysicsConfig(**raw.get("panels", {})),
        sensors=SensorNoiseConfig(**raw.get("sensors", {})),
        events=EventConfig(**raw.get("events", {})),
        mqtt=MQTTConfig(**raw.get("mqtt", {})),
        clusters=[ClusterConfig(**c) for c in raw["clusters"]],
    )