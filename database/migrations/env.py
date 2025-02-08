# --- Begin changes in env.py ---
import os
import re
from logging.config import fileConfig

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

# Instead of reading DATABASE_URL from the environment or alembic.ini,
# import it from your settings.
from core.config import settings
DATABASE_URL = settings.DATABASE_URL

# If your URL uses the "postgres://" scheme, adjust it to use the proper dialect.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = re.sub(r"^postgres://", "postgresql+psycopg2://", DATABASE_URL, 1)

# Update Alembic config with the correct URL.
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
