from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

# Creates the SQLAlchemy engine and session
settings = get_settings()
postgres_url = settings.postgres_url
engine = create_engine(
    postgres_url,
    pool_pre_ping=True
)

# Creates a configured "Session" class, allowing
# us to use this session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()