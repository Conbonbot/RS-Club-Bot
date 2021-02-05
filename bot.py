import os
import random
from dotenv import load_dotenv
import sqlite3
import datetime
from discord.ext import commands
import discord
import asyncio
import sys
import requests
import numpy as np
from discord.utils import get
import discord
import psycopg2

intents = discord.Intents(messages=True, guilds=True)
intents.reactions = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=["+", "!", "-"], intents=intents)


 
# Ready
@bot.event
async def on_ready():
    db = sqlite3.connect('rsqueue.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
            user_id TEXT,
            amount INTEGER,
            level INTEGER,
            time INTEGER,
            length INTEGER,
            channel_id TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data(
            user_id TEXT,
            croid INTEGER DEFAULT 0,
            influence INTEGER DEFAULT 0,
            nosanc INTEGER DEFAULT 0,
            notele INTEGER DEFAULT 0,
            rse INTEGER DEFAULT 0,
            suppress INTEGER DEFAULT 0,
            unity INTEGER DEFAULT 0,
            veng INTEGER DEFAULT 0
        )
    ''')
    #addColumn = "ALTER TABLE main ADD COLUMN channel_id TEXT"
    #cursor.execute(addColumn)
    print(f'{bot.user.name} has connected to Discord!')
    return await bot.change_presence(activity=discord.Activity(type=1, name="RS Queueing"))


intital_extensions = ['cogs.queue', 'cogs.role']

if __name__ == '__main__':
    for extension in intital_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}', file=sys.stderr)
            print(e)





bot.run(TOKEN)