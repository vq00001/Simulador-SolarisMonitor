from sqlalchemy import Column, Integer, ForeignKey, String
from src.server.database.base import Base

class Sensor(Base):
    __tablename__ = "sensor"

    id = Column(Integer, primary_key=True)
    panel_id = Column(Integer, ForeignKey("panel.id"))
    tipo = Column(Integer, ForeignKey("tipo_medicion.id"))