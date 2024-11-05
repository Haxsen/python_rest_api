from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

DATABASE_URL = "postgresql+asyncpg://postgres:chawlian@localhost/db_restaking_ops"

# SQLAlchemy Base
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

class RestakeOperation(Base):
    __tablename__ = "restake_operations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models import Base

class RestakeHistory(Base):
    __tablename__ = "restake_history"

    id = Column(Integer, primary_key=True, index=True)
    restake_operation_id = Column(Integer, ForeignKey("restake_operations.id"))
    amount = Column(Float)
    status = Column(String)
    completed_at = Column(DateTime, default=func.now())

    restake_operation = relationship("RestakeOperation", back_populates="history")

# Link this model to the existing RestakeOperation model
RestakeOperation.history = relationship("RestakeHistory", back_populates="restake_operation", uselist=False)


# Async Engine and Session
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
