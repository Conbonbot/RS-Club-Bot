#!/bin/python3
from importlib.metadata import metadata
import logging
import os

import discord

import psycopg2

from discord.ext import commands
from dotenv import load_dotenv

from sqlalchemy.sql.functions import char_length
import argparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.engine.url import URL
import asyncio

import routines
from discord_slash import SlashCommand, SlashContext



load_dotenv()

PROD_TOKEN = os.getenv('DISCORD_TOKEN')
TEMP_TOKEN = os.getenv('TEMP_DISCORD_TOKEN')

TOKEN = PROD_TOKEN or TEMP_TOKEN

# If the TEMP token is defined we treat the environment as testing.
TESTING = isinstance(TEMP_TOKEN, str)

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
if DEBUG and not TESTING:
    raise ValueError('No DEBUG on production! (it may slow things down). Please disable debugging.')
LOG_LEVEL = logging.DEBUG if DEBUG or TESTING else logging.INFO
logging.basicConfig(level=LOG_LEVEL)

LOGGER = logging.getLogger(__name__)

if not TOKEN:
    raise ValueError(
        'Found no discord token, please specify a DISCORD_TOKEN or TEMP_DISCORD_TOKEN environment variable.')


class RSClubBot(commands.Bot):
    def __init__(self, token: str, **kwargs):
        """Initializes database, routines and runs bot.
        Args:
            token: The token for the discord connection.
        """
        super(RSClubBot, self).__init__(**kwargs)
        routines.setup_coroutines(self)
        self.run(token)

    




if __name__ == '__main__':
    if TESTING:
        intents = discord.Intents.default()
    else:
        intents = discord.Intents(messages=True, guilds=True)
        intents.reactions = True
    bot = RSClubBot(
        token=TOKEN,
        command_prefix=["+", "!", "-"],
        intents=intents,
        case_insensitive=True,
        help_command=None
    )
    bot.run(TOKEN)