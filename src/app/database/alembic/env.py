# alembic/env.py

import os
import sys
import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv


# -----------------------------------------------------------------------------
# 1) Find project root by looking for src/security up the tree
# -----------------------------------------------------------------------------
current_path = os.path.abspath(__file__)
MAX_DEPTH = 10
depth = 0

def has_security_folder(path: str) -> bool:
    return os.path.isdir(os.path.join(path, "src", "security"))

while depth < MAX_DEPTH and not has_security_folder(current_path):
    parent = os.path.dirname(current_path)
    if parent == current_path:
        break
    current_path = parent
    depth += 1

# now current_path is your project root (or as high as we could climb)
project_root = current_path
sys.path.insert(0, project_root)        # so `import models` works
# -----------------------------------------------------------------------------
# 2) Load .local-env or .test-env if present
# -----------------------------------------------------------------------------
security_dir = os.path.join(project_root, "src", "security")
for fname in (".local-env", ".test-env"):
    path = os.path.join(security_dir, fname)
    if os.path.isfile(path):
        load_dotenv(path)
        print(f"Loaded environment from {path}")
        break
else:
    print("No .local-env or .test-env found; using existing os.environ")

# -----------------------------------------------------------------------------
# 3) Alembic Config
# -----------------------------------------------------------------------------
config = context.config

# override sqlalchemy.url from env vars
DB_NAME     = "integrations_db"
DB_PASSWORD = "mierda69"
DB_HOST     = "localhost"
DB_USER     = "user"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# optional debug print; comment out in production
print(f"Using DB at {DB_HOST}; DB_NAME={DB_NAME}; DB_USER={DB_USER}")

# logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# -----------------------------------------------------------------------------
# 4) Target metadata for `--autogenerate`
# -----------------------------------------------------------------------------
from models import Base   # adjust if your models are elsewhere
target_metadata = Base.metadata

# -----------------------------------------------------------------------------
# 5) Offline / Online migration runners
# -----------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# -----------------------------------------------------------------------------
# 6) Entry point
# -----------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
