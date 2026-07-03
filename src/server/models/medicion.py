from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app.db.base import Base

class Medicion(Base):
    __tablename__ = "medicion"

    id = Column(Integer, primary_key=True)
    #sensor_id = Column(Integer, ForeignKey("sensor.id"))
    panel_id = Column (Integer, ForeignKey("panel.id"))
    tipo_medicion_id = Column(Integer, ForeignKey("tipo_medicion.id"))
    valor = Column(Float)
    timestamp = Column(DateTime)