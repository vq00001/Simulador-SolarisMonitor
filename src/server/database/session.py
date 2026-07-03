from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL = os.environ["DATABASE_URL"]  

engine = create_async_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False,
                             autocommit=False, class_=AsyncSession, expire_on_commit=False)