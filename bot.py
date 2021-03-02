import os
import random
from attr import __description__
from discord import embeds
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
#TOKEN = os.getenv('DISCORD_TOKEN')
TOKEN = os.getenv('TEMP_DISCORD_TOKEN')

bot = commands.Bot(command_prefix=["+", "!", "-"], intents=intents, case_insensitive=True, help_command=None)


@bot.command()
async def help(ctx):
    role_embed = discord.Embed(
        description = (f'RS Roles + Pings'),
        color = discord.Color.green()
    )
    rs_role_channel = await bot.fetch_channel(801610229040939038)
    role_embed.add_field(name=f"RS Roles", value=f"To start queuing, head over to {rs_role_channel.mention} and select how you'd like to be pinged. There are 3 different options you can select (this is done by reacting to the one of the numbers below each message).", inline=False)
    role_embed.add_field(name=f"Pings (Option 1, #/4)", value=f"React to the [first message](https://discord.com/channels/682479756104564775/801610229040939038/808782626612838420) to get pinged EVERYTIME someone joins a queue.")
    role_embed.add_field(name=f"Pings (Option 2, 3/4)", value=f"React to the [second message](https://discord.com/channels/682479756104564775/801610229040939038/808782649946669127) to get pinged ONLY when a queue is 3/4.")
    role_embed.add_field(name=f"Pings (Option 3, 4/4)", value=f"React to the [third message](https://discord.com/channels/682479756104564775/801610229040939038/808960926517559306) to get pinged ONLY when a queue you've joined hits 4/4.")

    queue_embed = discord.Embed(
        description = (f'Queueing'),
        color = discord.Color.green()
    )
    queue_embed.add_field(name=f"Queuing Commands", value=f"There are currently 4 queueing commands, 3 for joining/leaving queues and 1 for displaying queues. They are +1/2/3 (-1/2/3), !in/i (!out/o), !rs, and !queue/q", inline=False)
    queue_embed.add_field(name=f"+1/2/3 and -1/2/3", value=f"Using +, it will add however many you specify to a queue (for example, +2 in #rs9-club will add 2 players to the current queue). Using -, it will remove however many you specify from a queue (for example, -3 in #rs6-club will remove the 3 players you added from the current queue).")
    queue_embed.add_field(name=f"!in/i and !out/o", value=f"The command !in or !i run in one of the rs channels will add 1 player (you) to the current rs queue, and !out or !o will remove 1 player (you) from the current queue")
    queue_embed.add_field(name=f"!rs", value=f"The !rs command run in one of the rs channels will add 1 player (you) to the current queue.", inline=False)
    queue_embed.add_field(name=f"!queue/q", value=f"This command (!queue or !q) will display the current queue of whatever rs channel you're in.", inline=False)
    queue_embed.add_field(name=f"Additional Parameters", value=f"adding a number to any of the commands that adds players to a queue will specifiy how long you'll remain in a queue before you get timed out (If you don't specifiy a number, it will be 60 minutes). An example is +2 45, which adds 2 players to the queue, and after 45 minutes they will be timed out and removed from the queue.")
    
    await ctx.send(embed=role_embed)
    await ctx.send(embed=queue_embed)
 
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp(
            user_id TEXT,
            message_id TEXT,
            level INTEGER
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