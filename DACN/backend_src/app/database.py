
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import settings
from loguru import logger

# Use settings from config
DATABASE_URL = settings.database_url

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Number of connections to keep in pool
    max_overflow=20,  # Max connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL debug logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger.info(f"Database engine created: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")


def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
