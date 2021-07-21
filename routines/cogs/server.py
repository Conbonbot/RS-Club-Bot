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

from routines.tables import ExternalServer, ExternalUsers
from routines import sessionmaker
from routines import engine

import requests

from discord import Webhook, AsyncWebhookAdapter
import aiohttp

if TESTING:
    clubs_server_id = 805959424081920022
else:
    clubs_server_id = 682479756104564775

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
                    Server_enter = ExternalServer(server_id=ctx.guild.id, server_name=ctx.guild.name, channel_id=ctx.channel.id, webhook=str(webhook.url), max_rs=int(max_rs), global_chat=False)
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
                    external_embed.add_field(name="Users and Queues", value=f"To allow users to join queues, they'll need to have a role specifying their rs level. In order to do this, use the `!rs_level # @<>` command, where # is the rs level, and @<> is the role that players in that rs level have. If you want to change the role, simply run the command again.")
                    external_embed.add_field(name="Joining Queues", value=f"Use the `!in #`/`!i #` command to join a queue, where `#` is the rs level you want to join. If `#` is not specified, it will default to your current rs level.")
                    external_embed.add_field(name="Leaving Queues", value=f"Use the `!out`/`!o` command to leave a queue.")
                    external_embed.add_field(name="Showing Queues", value=f"Use the `!q #` (where `#` is a rs level) command to show you the queue for rs#")
                    await ctx.send(embed=external_embed)
            else: # They were found in the database, update their max rs level
                async with sessionmaker() as session:
                    server = (await session.get(ExternalServer, ctx.guild.id))
                    server.max_rs = int(max_rs)
                    await session.commit()
                    await ctx.send(f"This server has already been connected to The Clubs, but now the max rs level of this server is {max_rs}")
        else:
            await ctx.send(f"The Clubs only support RS 5-11, {max_rs} is outside that range.")


    @commands.Cog.listener()
    async def on_message(self, message):
        # <Message id=859239790952185876 channel=<TextChannel id=858484759994040370 name='rs-queues' position=1 nsfw=False news=False category_id=858484643632381953> type=<MessageType.default: 0> 
        # author=<Member id=384481151475122179 name='Conbonbot' discriminator='0680' bot=False nick=None guild=<Guild id=858484643632381952 name='Testing Server' shard_id=None chunked=False member_count=2>> flags=<MessageFlags value=0>>

        # Get global active servers
        async with sessionmaker() as session:
            total_servers = (await session.execute(select(ExternalServer))).scalars()
            global_active_servers = 0
            ids = []
            server_ids_check = []
            for server in total_servers:
                ids.append(server.channel_id)
                server_ids_check.append((server.channel_id, server.global_chat))
                if server.global_chat:
                    global_active_servers += 1
        # Check if the message was sent from a server with global chat
        check = False
        print("SERVER ID STUFF: ", server_ids_check)
        for server, chat in server_ids_check:
            if message.channel.id == server:
                if chat:
                    check = True
        print("GLOBAL ACTIVE SERVERS:", global_active_servers)
        if global_active_servers > 1 and message.channel.id in ids and check:
            if not message.author.bot:
                if not (message.content.startswith('!') or message.content.startswith('+') or message.content.startswith('-') or message.content.startswith('%')):
                    print("HELLO THERE")
                    # cut out bot messages and commands
                    async with sessionmaker() as session:
                        total_servers = (await session.execute(select(ExternalServer).where(ExternalServer.global_chat == True))).scalars()
                        total_stuff = [(server.webhook, server.server_id) for server in total_servers]
                        print("TOTAL STUFF", total_stuff, message.guild.id)
                        for webhook_url, server_id in total_stuff:
                            if server_id != message.guild.id:
                                # Send the message with webhooks
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
                server_info = []
                for server in total_servers:
                    if server.global_chat and server.server_id != ctx.guild.id:
                        global_active_servers += 1
                        server_info.append(server.channel_id)
                send = "Global chat has been enabled, any messages you send in here will show up in all other servers that have global chat enabled.\n"
                send += f"There {'are' if global_active_servers != 1 else 'is'} currently {global_active_servers} other {'servers' if global_active_servers != 1 else 'server'} with global chat enabled."
                await ctx.send(send)
                if not str(ctx.channel.name).endswith("enabled"):
                    new_name = ctx.channel.name + " enabled"
                    await ctx.channel.edit(name=new_name)
                for name in server_info:
                    channel = await self.bot.fetch_channel(name)
                    await channel.send(f"{ctx.guild.name} has joined global chat, current (other) servers with global chat enabled: {global_active_servers}")

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
                if new_name.endswith("enabled"):
                    await ctx.channel.edit(name=new_name[:-8])
                total_servers = (await session.execute(select(ExternalServer))).scalars()
                server_info = []
                global_active_servers = 0
                for server in total_servers:
                    if server.global_chat and server.server_id != ctx.guild.id:
                        global_active_servers += 1
                        server_info.append(server.channel_id)
                print("SERVER INFO", server_info)
                for name in server_info:
                    channel = await self.bot.fetch_channel(name)
                    await channel.send(f"{ctx.guild.name} has left global chat, current servers with global chat enabled: {global_active_servers}")
        else:
            await ctx.send("global chat is already disabled. To turn it on run `!startglobal`")

    @commands.command()
    async def rate(self, ctx):
        print("Rate limit:")
        print(self.bot.is_ws_ratelimited())



        

def setup(bot):
    bot.add_cog(ServerJoin(bot))
    LOGGER.info('Server Join System loaded')
