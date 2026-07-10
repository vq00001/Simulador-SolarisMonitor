from src.server.database.base import Base
from src.server.database.session import engine
from sqlalchemy import create_engine
import os


# Importar modelos para que SQLAlchemy los registre
from src.server.models.panel import Panel
from src.server.models.medicion import Medicion
from src.server.models.tipo_medicion import TipoMedicion
from src.config.settings import DATABASE_URL_SYNC


DATABASE_URL = os.getenv[DATABASE_URL_SYNC]  

engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(bind=engine)