import sys
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ------------------------------------------------------------------
# [MODIFIED 1] ตั้งค่า Path และ Import
# ------------------------------------------------------------------
# เพิ่ม Path ของ Project Root เพื่อให้ Python มองเห็นโฟลเดอร์ 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import settings เพื่อเอา URL ของ Database
from app.core.config import settings

# Import Base เพื่อเอา Metadata (โครงสร้างตาราง)
# หมายเหตุ: ต้องมั่นใจว่าใน app/models/__init__.py มีการ import model ย่อยๆ มาครบแล้ว
from app.models import Base 
# ------------------------------------------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------------
# [MODIFIED 2] เชื่อมต่อ Metadata
# ------------------------------------------------------------------
# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata
# ------------------------------------------------------------------

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # [MODIFIED] ใช้ URL จาก settings โดยตรง
    url = settings.DATABASE_URL
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # ------------------------------------------------------------------
    # [MODIFIED 3] Overwrite Database URL
    # ------------------------------------------------------------------
    # อ่าน config เดิม
    configuration = config.get_section(config.config_ini_section, {})
    # เขียนทับ sqlalchemy.url ด้วยค่าจาก .env (settings)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()