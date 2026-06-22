
from dataclasses import dataclass

@dataclass(frozen=True)
class SensorMessage:
    topic: str
    value: float
    timestamp: str

