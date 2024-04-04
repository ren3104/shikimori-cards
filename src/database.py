from sqlalchemy import URL, Connection
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_scoped_session,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy import (
    Column,
    Integer,
    Date,
    JSON
)
from alembic.migration import MigrationContext
from alembic.autogenerate import produce_migrations
from alembic.operations import Operations
from alembic.operations.ops import OpContainer

import os
import asyncio
from contextlib import asynccontextmanager


engine = create_async_engine(
    url=URL.create(
        (
            "postgresql+asyncpg"
            if os.environ.get("VERCEL") else
            "sqlite+aiosqlite"
        ),
        username=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        database=os.environ.get("POSTGRES_DATABASE", "local.db")
    ),
    echo=False,
    poolclass=NullPool # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops
)
async_session = async_scoped_session(
    async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    ),
    scopefunc=asyncio.current_task
)


class Base(DeclarativeBase):
    pass


class BingoCard(Base):
    __tablename__ = "bingo_cards"

    user_id = Column(Integer, primary_key=True)
    season_date = Column(Date)
    last_history_id = Column(Integer)
    stats = Column(JSON, nullable=False)


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def migrate() -> None:
    # https://stackoverflow.com/a/67238665

    def _migrate(connection: Connection) -> None:
        mig_ctx = MigrationContext.configure(connection)
        mig_script = produce_migrations(mig_ctx, Base.metadata)
        operation = Operations(mig_ctx)
        for outer_op in mig_script.upgrade_ops.ops:
            if isinstance(outer_op, OpContainer):
                for inner_op in outer_op.ops:
                    operation.invoke(inner_op)
            else:
                operation.invoke(outer_op)
    
    # async with get_db_session() as db:
    async with engine.begin() as conn:
        await conn.run_sync(_migrate)


@asynccontextmanager
async def get_db_session():
    async with async_session() as session:
        yield session
