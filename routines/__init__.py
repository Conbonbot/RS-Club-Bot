"""Dynamic co-routine module loader."""
from discord.ext import commands

from bot import LOGGER

import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy.sql.functions import char_length
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as maker
import asyncio

postgres_URL = URL.create('postgresql+asyncpg',
                          database=os.getenv('DATABASE'),
                          username=os.getenv('NAME'),
                          password=os.getenv('PASSWORD'),
                          host=os.getenv('HOST'))


#engine = create_async_engine(postgres_URL, echo=True, poolclass=NullPool)
engine = create_async_engine(postgres_URL, echo=True, pool_size=10, max_overflow=20)
sessionmaker = maker(bind=engine, expire_on_commit=False, class_=AsyncSession)



class Routine(object):
    """Base class for all events and commands."""
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @classmethod
    def get_actions(cls):
        actions = getattr(cls, 'actions', None)
        return actions


def setup_coroutines(bot: commands.bot):
    """Main entrypoint to dynamically configure bot routines."""
    LOGGER.debug('Registering co-routines.')
    on_ready_setup(bot)
    command_setup(bot)
    cog_setup(bot)


def on_ready_setup(bot: commands.bot):
    """Configures on_ready coroutines."""
    from routines.on_ready import OnReadyEvent
    for event in OnReadyEvent.__subclasses__():
        LOGGER.debug(f'Registering event: {event.__name__}')
        setup = event(bot)
        setup.actions()


def command_setup(bot: commands.bot):
    """Configures command coroutines."""
    from routines.commands import CommandRoutine
    for cmd in CommandRoutine.__subclasses__():
        LOGGER.debug(f'Registering command: {cmd.__name__}')
        setup = cmd(bot)
        setup.actions()


def cog_setup(bot):
    """Configures cogs."""
    from routines.cogs import __all__
    for cog in __all__:
        LOGGER.debug(f'Registering cog: {cog}')
        bot.load_extension(f'routines.cogs.{cog}')
