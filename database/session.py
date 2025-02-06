import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings

# Enable SQLAlchemy logging for debugging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Configure session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # 🚀 Ensure commit before closing session
    except Exception as e:
        db.rollback()  # Rollback if any error occurs
        logging.error(f"Database transaction rolled back due to error: {str(e)}")
        raise
    finally:
        db.close()
