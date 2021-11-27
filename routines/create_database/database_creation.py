"""Creates databases before server login."""
import discord
from routines.create_database import CreateDatabaseEvent
from bot import LOGGER
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from ..tables import Base
from .. import engine

class DatabaseCreation(CreateDatabaseEvent):
    """Creates the databases using SQLAlchemy"""
    def actions(self):
        @self.bot.event
        async def on_connect():
            async with engine.begin() as conn:
                await conn.run_sync(
                    Base.metadata.create_all,
                    tables=map(
                        lambda iterr: iterr[1],
                        filter(lambda tup: 'rsqueue_data' not in tup[0], Base.metadata.tables.items())
                    )
                )