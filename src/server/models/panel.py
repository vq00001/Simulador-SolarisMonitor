from sqlalchemy import Column, Integer, String
from src.server.database.base import Base

class Panel(Base):
    __tablename__ = "panel"

    id = Column(Integer, primary_key=True)
    uid = Column(String, unique = True)