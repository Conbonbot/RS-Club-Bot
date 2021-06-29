import asyncio
from asyncio.locks import Condition
import time
from aiosqlite.core import LOG

import discord
import sqlite3
import psycopg2

from datetime import datetime
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.orm import session
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect
from sqlalchemy import event

from random import random

from bot import LOGGER
from bot import TESTING

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import ExternalServer, ExternalUsers, Queue, Data, Temp
from routines import sessionmaker
from routines import engine

import requests

from discord import Webhook, AsyncWebhookAdapter
import aiohttp



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
                await channel.send(f"In order to be connected to The Clubs, I'll need a text channel to show the current queues. Once you have a text channel that I can use, simply run `!connect #` in the channel you want where # is the max rs level of your server and just like that you'll be connected to The Clubs!")
                await channel.send(f"NOTE: The `!connect #` command can ONLY be run by an administrator of this server.")
                break

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def connect(self, ctx, max_rs=None):
        if max_rs is None:
            await ctx.send("Please specify this server's max rs level in the `!connect` command, i.e. `!connect 9`")
        elif int(max_rs) > 4 and int(max_rs) < 12:
            async with sessionmaker() as session: # check to see if the server is already in the database
                data = (await session.execute(select(ExternalServer).where(ExternalServer.server_id == ctx.guild.id))).scalars().all()
            if len(data) == 0: # Add the server to the ExternalServer Database
                async with sessionmaker() as session:
                    LOGGER.debug("Adding server to database")
                    webhook = await ctx.channel.create_webhook(name="Global Chat Webhook (The Clubs)")
                    Server_enter = ExternalServer(server_id=ctx.guild.id, channel_id=ctx.channel.id, webhook=str(webhook.url), max_rs=int(max_rs), global_chat=False)
                    session.add(Server_enter)
                    await session.commit()

                    await ctx.send("This server has been connected to The Clubs!")
                    await ctx.send(f"The max rs of this server has been set to: rs{max_rs}")
                    await ctx.send("If you messed up the max rs level of this server while running the `!connect` command, just run the command again with the correct rs level and it will update the rs level of the server.")
                    await ctx.send("Now comes the fun part, setting up the rs level of users on this server!")
                    await ctx.send("Below is everything you'll need to know about setting this up, and if you need to see this again, run `!help external`, or to see all functions of this bot, `!help`.")

                    external_embed = discord.Embed(title='External', color=discord.Color.green())
                    if TESTING:
                        external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=809871917946634261&permissions=8&scope=bot) and follow the steps")
                    else:
                        external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=805960284543385650&permissions=8&scope=bot) and follow the steps")
                    external_embed.add_field(name="First Time Setup", value=f"Run `!connect #` (where `#` is the max rs level of your server), and your server will be connected to The Clubs.")
                    external_embed.add_field(name="Setting up max RS levels", value=f"To change the max RS level of your server, run `!connect #` where `#` is the max rs level of your server.")
                    external_embed.add_field(name="Users (RS Level + Pings)", value=f"Each user of your discord server will have to run the `!user # %` command which sets up how a user should be pinged when a user enters a specific queue. `#` refers to the user's current rs level, and `%` refers to how the user would like to be notified when someone enters a queue of their rs level. `%` could be `all`, `3/4`, or `silent`.")
                    external_embed.add_field(name="Users (RS Level + Pings) cont.", value=f"If `%` is set to `all`, the user will be pinged everytime someone joins a queue of their rs level. If `%` is set to `3/4`, they will be pinged when the queue of their rs level is 3/4. If `%` is set to `silent`, they will not be pinged when someone joins a queue of their rs level.")
                    external_embed.add_field(name="Multiple RS Levels", value=f"If a user wants to be notified when someone joins a queue of a different rs level than their current rs level, run the `!user # %` command again with `#` as whatever rs level they want that is below their current rs level.")
                    external_embed.add_field(name="Removing Users (RS Level + Pings)", value=f"If a user wants to remove how they'll be pinged for a queue (that they previously wanted to), they can remove it by running `!remove #` where `#` is the rs level they do not want to be notified of.")
                    external_embed.add_field(name="Seeing RS Level and Pings", value=f"If you want to see what your current rs level + pings are (from the `!user # %` command), run `!current` and it will show you.")
                    await ctx.send(embed=external_embed)
            else: # They were found in the database, update their max rs level
                async with sessionmaker() as session:
                    server = (await session.get(ExternalServer, ctx.guild.id))
                    setattr(server, max_rs, int(max_rs))

                    await session.commit()
                    await ctx.send(f"This server has already been connected to The Clubs, but now the max rs level of this server is {max_rs}")
        else:
            await ctx.send(f"The Clubs only support RS 5-11, {max_rs} is outside that range.")

    @commands.command()
    async def user(self, ctx, rs_level=None, ping=None):
        if rs_level is None or ping is None:
            await ctx.send("Please specify the RS Level (5-11) and how you'd like to be pinged (all, 3/4, silent)")
        else:
            rs_level = int(rs_level)
            if rs_level < 5:
                await ctx.send(f"{rs_level} is below The Clubs minimum rs level of rs5")
            elif rs_level > 11:
                await ctx.send(f"RS 11 is currently the highest rs level, you can't be rs{rs_level}")
            else:
                if ping == "all" or ping == "3/4" or ping == "silent":
                    ping_number = 1 if ping == "all" else 2 if ping == "3/4" else 3 if ping == "silent" else ""
                    # This is where stuff actually happens
                    async with sessionmaker() as session:
                        conditions = and_(ExternalUsers.user_id == ctx.author.id, ExternalUsers.rs_level == rs_level)
                        data = (await session.execute(select(ExternalUsers).where(conditions))).scalars().all()
                    if len(data) == 0: # Add them to the database
                        async with sessionmaker() as session:
                            user = ExternalUsers(server_id=ctx.guild.id, user_id=ctx.author.id, rs_level=rs_level, pings=ping_number)
                            session.add(user)
                            await session.commit()
                            send = f"You'll now be able to join queues up to rs{rs_level}"
                            if ping_number == 1:
                                await ctx.send(send + f" and notified everytime someone joins the rs{rs_level} queue")
                            elif ping_number == 2:
                                await ctx.send(send + f" and notified when the rs{rs_level} queue hits 3/4")
                            elif ping_number == 3:
                                await ctx.send(send + f" but won't get pinged when someone joins")
                    else: # Update their pings
                        async with sessionmaker() as session:
                            User = (await session.get(ExternalUsers, (ctx.guild.id, ctx.author.id, rs_level)))
                            User.pings = ping_number
                            await session.commit()
                            await ctx.send(f"Changed pings for rs{rs_level}, set to {ping}")
                else:
                    await ctx.send("Specify `all`, `3/4`, or `silent` on how you'd like to be pinged.")

    @commands.command()
    async def remove(self, ctx, rs_level=None):
        if rs_level is None:
            await ctx.send("Please specify the RS Level")
        else:
            rs_level = int(rs_level)
            if rs_level < 5:
                await ctx.send(f"{rs_level} is below The Clubs minimum rs level of rs5, you won't have a profile for rs{rs_level}")
            elif rs_level > 11:
                await ctx.send(f"RS 11 is currently the highest rs level, you can't be rs{rs_level}")
            else:       
                async with sessionmaker() as session:
                    User_leave = (await session.get(ExternalUsers, (ctx.guild.id, ctx.author.id, rs_level)))
                    await session.delete(User_leave)
                    await session.commit()
                    await ctx.send(f"You'll stop recieving notifications for rs{rs_level} queues")

    @commands.command()
    async def current(self, ctx):
        async with sessionmaker() as session:
            no_data = True
            conditions = and_(ExternalUsers.server_id == ctx.guild.id, ExternalUsers.user_id == ctx.author.id)
            total_data = (await session.execute(select(ExternalUsers).where(conditions))).scalars()
            for data in total_data:
                no_data = False
                say = "all" if data.pings == 1 else "3/4" if data.pings == 2 else "silent" if data.pings == 3 else ""
                await ctx.send(f"RS{data.rs_level}: {say}")
            if no_data:
                await ctx.send("No data found, use the `!user` command to recieve notifications for queues")


    @commands.Cog.listener()
    async def on_message(self, message):
        # <Message id=859239790952185876 channel=<TextChannel id=858484759994040370 name='rs-queues' position=1 nsfw=False news=False category_id=858484643632381953> type=<MessageType.default: 0> 
        # author=<Member id=384481151475122179 name='Conbonbot' discriminator='0680' bot=False nick=None guild=<Guild id=858484643632381952 name='Testing Server' shard_id=None chunked=False member_count=2>> flags=<MessageFlags value=0>>

        # Get global active servers
        async with sessionmaker() as session:
            total_servers = (await session.execute(select(ExternalServer))).scalars()
            global_active_servers = 0
            for server in total_servers:
                if server.global_chat:
                    global_active_servers += 1
        print("GLOBAL ACTIVE SERVERS:", global_active_servers)
        if global_active_servers > 1:
            if not message.author.bot:
                if not (message.content.startswith('!') or message.content.startswith('+') or message.content.startswith('-') or message.content.startswith('%')):
                    # cut out bot messages and commands
                    async with sessionmaker() as session:
                        total_servers = (await session.execute(select(ExternalServer))).scalars()
                        total_stuff = [(server.webhook, server.server_id) for server in total_servers]
                        print("TOTAL STUFF", total_stuff, message.guild.id) 
                        for webhook_url, server_id in total_stuff:
                            if server_id != message.guild.id:
                                user = await self.bot.fetch_user(message.author.id)
                                async with aiohttp.ClientSession() as session:
                                    webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
                                    if len(message.attachments) == 0:
                                        await webhook.send(message.content, username=message.author.display_name, avatar_url=str(user.avatar_url))
                                    else:
                                        for attachment in message.attachments:
                                            await webhook.send(content=None, username=message.author.display_name, avatar_url=str(user.avatar_url), file=(await attachment.to_file()))
        

   
    @commands.command()
    async def startglobal(self, ctx):
        # Check to see if it is already enabled
        async with sessionmaker() as session:
            server = (await session.get(ExternalServer, ctx.guild.id))
        if not server.global_chat:
            async with sessionmaker() as session:
                server = (await session.get(ExternalServer, ctx.guild.id))
                server.global_chat = True
                await session.commit()
                total_servers = (await session.execute(select(ExternalServer))).scalars()
                global_active_servers = 0
                for server in total_servers:
                    if server.global_chat and server.server_id != ctx.guild.id:
                        global_active_servers += 1
                send = "Global chat has been enabled, any messages you send in here will show up in all other servers that have global chat enabled.\n"
                send += f"There {'are' if global_active_servers != 1 else 'is'} currently {global_active_servers} other {'servers' if global_active_servers != 1 else 'server'} with global chat enabled."
                await ctx.send(send)
                new_name = ctx.channel.name + " (enabled)"
                await ctx.channel.edit(name=new_name)

        else:
            await ctx.send("global chat is already enabled. To turn it off run `!stopglobal`")


    @commands.command()
    async def stopglobal(self, ctx):
        # Check to see if it is already enabled
        async with sessionmaker() as session:
            server = (await session.get(ExternalServer, ctx.guild.id))
        if server.global_chat:
            async with sessionmaker() as session:
                server = (await session.get(ExternalServer, ctx.guild.id))
                server.global_chat = False
                await session.commit()
                await ctx.send("Global chat has been disabled.")
                new_name = ctx.channel.name
                await ctx.channel.edit(name=new_name[:-8])
        else:
            await ctx.send("global chat is already disabled. To turn it on run `!startglobal`")



        

def setup(bot):
    bot.add_cog(ServerJoin(bot))
    LOGGER.info('Server Join System loaded')
