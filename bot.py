#!/bin/python3
import logging
import os

import discord
import sqlite3

from discord.ext import commands
from dotenv import load_dotenv

import routines

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

DB_TABLES = [
    'main(user_id TEXT, amount INTEGER, level INTEGER, time INTEGER, length INTEGER, channel_id TEXT)',
    'data(user_id TEXT, croid INTEGER DEFAULT 0, influence INTEGER DEFAULT 0, nosanc INTEGER DEFAULT 0, notele INTEGER DEFAULT 0, rse INTEGER DEFAULT 0, suppress INTEGER DEFAULT 0, unity INTEGER DEFAULT 0, veng INTEGER DEFAULT 0,barrage INTEGER DEFAULT 0, laser INTEGER DEFAULT 0, battery INTEGER DEFAULT 0, dart INTEGER DEFAULT 0, solo INTEGER DEFAULT 0, solo2 INTEGER DEFAULT 0)',
    'temp(user_id TEXT, message_id TEXT, level INTEGER)',
]


class RSClubBot(commands.Bot):
    def __init__(self, token: str, **kwargs):
        """Initializes database, routines and runs bot.

        Args:
            token: The token for the discord connection.
        """
        self._prep_db()
        super(RSClubBot, self).__init__(**kwargs)
        routines.setup_coroutines(self)
        self.run(token)

    @staticmethod
    def _prep_db():
        """Makes sure the database has the required tables for the bot."""
        with sqlite3.connect('rsqueue.sqlite') as db:
            cursor = db.cursor()
            # TODO: Cleanup at some point.
            # addColumn = "ALTER TABLE data ADD COLUMN laser INTEGER DEFAULT 0"
            # cursor.execute(addColumn)
            # addColumn = "ALTER TABLE data ADD COLUMN dart INTEGER DEFAULT 0"
            # cursor.execute(addColumn)
            # addColumn = "ALTER TABLE data ADD COLUMN solo INTEGER DEFAULT 0"
            # cursor.execute(addColumn)
            # addColumn = "ALTER TABLE data ADD COLUMN battery INTEGER DEFAULT 0"
            # cursor.execute(addColumn)
            # addColumn = "ALTER TABLE data ADD COLUMN solo2 INTEGER DEFAULT 0"
            # cursor.execute(addColumn)
            for table in DB_TABLES:
                LOGGER.debug(f'Creating DB table: {table}')
                cursor.execute(f'CREATE TABLE IF NOT EXISTS {table}')


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
