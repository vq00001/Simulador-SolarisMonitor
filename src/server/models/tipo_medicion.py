from sqlalchemy import Column, Integer, String
from src.server.database.base import Base

class TipoMedicion(Base):
    __tablename__ = "tipo_medicion"

    id = Column(Integer, primary_key=True)
    tipo = Column(String)
    unidad_medida = Column(String)