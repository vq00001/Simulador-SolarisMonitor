from src.server.database.base import Base
from src.server.database.session import engine
from sqlalchemy import create_engine
import os

# Importar modelos para que SQLAlchemy los registre
from server.models import panel, sensor, medicion, tipo_medicion

DATABASE_URL = os.environ["DATABASE_URL_SYNC"]  

engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(bind=engine)