# Import os and regex for Heroku compatibility
import os
import re
from logging.config import fileConfig

# Import Alembic and SQLAlchemy
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url

# Import your database models (adjust if needed)
from database.models.base import Base
from database.session import get_engine

# Load Alembic config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Get database URL from environment or alembic.ini
DATABASE_URL = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

# Convert 'postgres://' to 'postgresql+psycopg2://', required for Heroku
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = re.sub(r"^postgres://", "postgresql+psycopg2://", DATABASE_URL, 1)

# Update Alembic config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Attach the Base metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = get_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
