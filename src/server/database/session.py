from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from src.config.settings import DATABASE_URL

DATABASE_URL_ = DATABASE_URL

engine = create_async_engine(DATABASE_URL_)

SessionLocal = sessionmaker(bind=engine, autoflush=False,
                             autocommit=False, class_=AsyncSession, expire_on_commit=False)