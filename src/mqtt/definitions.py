
from dataclasses import dataclass

@dataclass(frozen=True)
class SensorMessage:
    topic: str
    value: float
    timestamp: str

class UserRole:
    ADMIN = "admin"
    SOLAR_PANEL = "panel"
    VISUALIZER = "visualizer"
    SERVER = "server"
    ACTUADOR = "actuador"