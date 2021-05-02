import sqlite3
import aiosqlite

import discord
from discord.ext import commands

from bot import LOGGER
from bot import TESTING
import time
import asyncio

from datetime import datetime
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.sql.selectable import Select

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import Queue, Data, Temp
from routines import sessionmaker




class ServerJoin(commands.Cog, name='OnServerJoin'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        LOGGER.debug(f"Here is the guild: {guild.name}")
        for channel in guild.text_channels:
            LOGGER.debug(f"Channel: {channel}")
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(f"Hello {guild.name}! I'm the bot from The Clubs discord server. You've added me to your server, which means you'll be able to queue for Red Stars without even leaving the comfort of your discord server!")
                await channel.send(f"In order to be connected to The Clubs, I'll need a text channel to show the current queues. Once you have a text channel that I can use, simply run `!connect` in the channel you want and just like that you'll be connected to The Clubs!")
                #await channel.send(f"Also, if you just want to use the bot to run Red Stars without it being connected to The Clubs, just run `!solo_connect` in the channel you want and you'll be able to queue for Red Stars without being connected to The Clubs.")
                #TODO: maybe a solo connect? I'm not sure yet
                break

    @commands.command()
    async def connect(self, ctx):
        await ctx.send(f"This channel has been connected to The Clubs!")
        await ctx.send(f"In order to start running Red Stars, I'll need to know this server's RS pings, and you can set them by typing `!rs_connect # @rs#` where # is the red star level and @rs# is the role itself")
        await ctx.send(f"If your server only supports up to a certain rs level (and you don't want the queue to display who is in a queue nobody in your server can enter, run `!max #` where # is the max level the server can run")

    @commands.command()
    async def rs_connect(self, ctx, level=None, role=None):
        LOGGER.debug(f"rs_connect level: {level} role: {role}")
        if level is None:
            await ctx.send("I need a level in order to set pings up")
        if role is None:
            await ctx.send("I need a role in order to set pings up")
        elif int(level) < 5 or int(level) > 11:
            await ctx.send(f"Currently The Clubs only support RS 5-11, not {level}")

    @commands.command()
    async def max(self, ctx, max=None):
        if max is None:
            await ctx.send("No maximum level given, showing all queues")
        else:
            await ctx.send(f"Maximum level has been set to {max}. I'll only show queue up to RS{max}")

def setup(bot):
    bot.add_cog(ServerJoin(bot))
    LOGGER.info('Server Join System loaded')
