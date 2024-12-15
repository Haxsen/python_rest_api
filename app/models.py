from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.config import DATABASE_URL

# SQLAlchemy Base
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

class RestakeOperation(Base):
    __tablename__ = "restake_operations"
    operation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to link RestakeHistory (one-to-one)
    restake_history = relationship("RestakeHistory", back_populates="restake_operation", uselist=False)

class RestakeHistory(Base):
    __tablename__ = "restake_history"

    restake_operation_id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("restake_operations.operation_id"))
    amount = Column(Float)
    status = Column(String)
    completed_at = Column(DateTime, default=func.now())

    # Back reference from RestakeHistory to RestakeOperation
    restake_operation = relationship("RestakeOperation", back_populates="restake_history")

# Async Engine and Session
engine = create_async_engine(DATABASE_URL, echo=True)

# Sessionmaker setup
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Initialize the database by creating tables."""
    async with engine.begin() as conn:
        # Create all tables in the Base metadata (this handles all models)
        await conn.run_sync(Base.metadata.create_all)
