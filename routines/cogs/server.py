import asyncio
from asyncio.locks import Condition
import time
from aiosqlite.core import LOG

import discord
import sqlite3
from discord import role
from discord.ext.commands.core import has_permissions
from discord.utils import get
import psycopg2

from datetime import datetime
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.orm import load_only, session
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect
from sqlalchemy import event

from random import random

from bot import LOGGER
from bot import TESTING

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import ExternalServer, Queue, Talking, Stats
from routines import sessionmaker
from routines import engine

import requests

from discord import Webhook, AsyncWebhookAdapter
import aiohttp

from dotenv import load_dotenv
load_dotenv()

if TESTING:
    clubs_server_id = 805959424081920022
else:
    clubs_server_id = 682479756104564775

rs_club_webhooks = {
    "5" : os.getenv("RS5_WEBHOOK"),
    "6" : os.getenv("RS6_WEBHOOK"),
    "7" : os.getenv("RS7_WEBHOOK"),
    "8" : os.getenv("RS8_WEBHOOK"),
    "9" : os.getenv("RS9_WEBHOOK"),
    "10" : os.getenv("RS10_WEBHOOK"),
    "11" : os.getenv("RS11_WEBHOOK")
}

class ServerJoin(commands.Cog, name='OnServerJoin'):

    def __init__(self, bot):
        self.bot = bot
        self.check_talk.start()
        self.emojis = {
            "1️⃣": 1,
            "2️⃣": 2,
            "3️⃣": 3,
            "4️⃣": 4
        }
        self.rs_channel = {
            "rs5-club": 5,
            "rs6-club": 6,
            "rs7-club": 7,
            "rs8-club": 8,
            "rs9-club": 9,
            "rs10-club": 10,
            "rs11-club": 11,
            "bot-spam": -1
        }
        if TESTING:
            self.club_channels = {
                5 : 805963630004535368,
                6 : 805963657442885663,
                7 : 805963675198160906,
                8 : 805963696077013054,
                9 : 805963717921079346,
                10 : 805963741430415372,
                11 : 806270120791244910
            }
        else:
            self.club_channels = {
                5 : 682479950774665310,
                6 : 682480009377611776,
                7 : 682480069754486826,
                8 : 682480117464956968,
                9 : 682480172351750144,
                10 : 773594029371424779,
                11 : 798387540910276628,
            }

    async def queue_time(self, user_id, amount, level):
        async with sessionmaker.begin() as session:
            person = (await session.get(Queue, (user_id, amount, level)))
            data =  int((time.time() - int(person.time)) / 60)
            return data

    async def amount(self, level):
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
            count = 0
            for person in people:
                count += int(person.amount)
            return count

    async def right_channel(self, ctx, rs_club_server=True):
        right_channel = False
        channel = ""
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
                channel = club_channel
        return (right_channel, channel)

    async def right_role(self, ctx, channel, rs_club_server=True):
        has_right_role = False
        for role in ctx.author.roles:
            if str(role)[2:].isnumeric():  # Checks main role (rs#)
                if int(str(role)[2:]) >= int(self.rs_channel[channel]):
                    has_right_role = True
                    break
            elif str(role)[2:-12].isnumeric():  # Checks 3/4 role (rs# 3/4 1more)
                if int(str(role)[2:-12]) >= int(self.rs_channel[channel]):
                    has_right_role = True
                    break
            elif str(role)[2:-2].isnumeric():  # Checks silent role (rs# s)
                if int(str(role)[2:-2]) >= int(self.rs_channel[channel]):
                    has_right_role = True
                    break
        return has_right_role

    async def talk(self):
        async with sessionmaker() as session:
            talking = (await session.execute(select(Talking))).scalars()
            for talk in talking:
                minutes = int((time.time() - talk.timestamp)/60)
                if minutes > 5:
                    await session.delete(talk)
            await session.commit()


    @tasks.loop(minutes=10.0)
    async def check_talk(self):
        try:
            await self.talk()
        except Exception as e:
            print("ERROR IN CHECK TALK:", e)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        LOGGER.debug(f"Here is the guild: {guild.name}")
        for channel in guild.text_channels:
            LOGGER.debug(f"Channel: {channel}")
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(f"Hello {guild.name}! I'm the bot from The Clubs discord server. You've added me to your server, which means you'll be able to queue for Red Stars without even leaving the comfort of your discord server!")
                await channel.send(f"In order to be connected to The Clubs, I'll need a text channel to show the current queues. Once you have a text channel that I can use, simply run `!connect # %` in the channel you want where # is the minimum rs level of your server abd % is the maximum (i.e. `!connect 5 9`) and just like that you'll be connected to The Clubs!")
                await channel.send(f"NOTE: The `!connect # %` command can ONLY be run by an administrator of this server.")
                break

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def connect(self, ctx, min_rs=None, max_rs=None):
        if max_rs is None or min_rs is None:
            await ctx.send("Please specify this server's min and max rs level in the `!connect` command, i.e. `!connect 5 9`")
        if int(max_rs) < int(min_rs):
            await ctx.send("Your server's maximum rs level should be higher than your minimum.")
        elif int(min_rs) > 4 and int(max_rs) < 12:
            async with sessionmaker() as session: # check to see if the server is already in the database
                data = (await session.execute(select(ExternalServer).where(ExternalServer.server_id == ctx.guild.id))).scalars().all()
            if len(data) == 0: # Add the server to the ExternalServer Database
                async with sessionmaker() as session:
                    LOGGER.debug("Adding server to database")
                    webhook = await ctx.channel.create_webhook(name="Global Chat Webhook (The Clubs)")
                    Server_enter = ExternalServer(server_id=ctx.guild.id, server_name=ctx.guild.name, channel_id=ctx.channel.id, webhook=str(webhook.url), min_rs=int(min_rs), max_rs=int(max_rs), global_chat=False)
                    session.add(Server_enter)
                    await session.commit()
                    print_str = "This server has been connected to The Clubs!\n"
                    print_str += f"The min/max rs of this server has been set to: rs{min_rs}-rs{max_rs}\n"
                    print_str += "If you messed up the max rs level of this server while running the `!connect` command, just run the command again with the correct rs level(s) and it will update the rs level of the server.\n"
                    print_str += "Now comes the fun part, setting up the rs level of users on this server!\n"
                    print_str += "Below is everything you'll need to know about setting this up, and if you need to see this again, run `!help external`, or to see all functions of this bot, `!help`\n"
                    await ctx.send(print_str)
                    external_embed = discord.Embed(title='External', color=discord.Color.green())
                    if TESTING:
                        external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=805960284543385650&permissions=537193536&scope=bot) and follow the steps")
                    else:
                        external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=809871917946634261&permissions=537193536&scope=bot) and follow the steps")
                    external_embed.add_field(name="First Time Setup", value=f"Run `!connect # %` (where `#` is the minimum rs level of your server and `%` is the maximum), and your server will be connected to The Clubs.")
                    external_embed.add_field(name="Setting up max RS levels", value=f"To change the min/max RS level of your server, run `!connect # %` where `#` is the minimum rs level of your server and `%` is the maximum.")
                    external_embed.add_field(name="Users and Queues", value=f"To allow users to join queues, they'll need to have a role specifying their rs level. In order to do this, use the `!level # @<>` command, where # is the rs level, and @<> is the role that players in that rs level have. If you want to change the role, simply run the command again.")
                    external_embed.add_field(name="Seeing Roles", value=f"Use the `!current` command to show what roles are currently connected to the bot. If you want to add more, use the `!level # @<>` command.")
                    external_embed.add_field(name="Disconnecting", value=f"If you want this server to be disconnected from The Clubs, have an admin run the `!disconnect` command.")
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disconnect(self, ctx):
        async with sessionmaker() as session:
            server = await session.get(ExternalServer, ctx.guild.id)
            if server is None:
                await ctx.send("This server is already not connected to The Clubs")
            else:
                await session.delete(server)
                await session.commit()
                await ctx.send("The server has been disconnected from The Clubs")
    @commands.command()
    async def current(self, ctx):
        async with sessionmaker() as session:
            server = await session.get(ExternalServer, ctx.guild.id)
            role_ids = [getattr(server, "rs" + str(i)) for i in range(5,12)]
            print_str = "Below is what pings are currently set up on this server. If you want to add more, use the `!level` command:\n```"
            print_str += f"Min RS: rs{server.min_rs}\n"
            index = 5
            for role in role_ids:
                if role is not None:
                    full_role = discord.utils.get(ctx.guild.roles, id=role)
                    print_str += f"RS{index}: {full_role.name}\n"
                index += 1
            print_str += f"Max RS: rs{server.max_rs} ```"
            await ctx.send(print_str)

    @commands.command()
    @has_permissions(manage_roles=True)
    async def level(self, ctx, level, role):
        async with sessionmaker() as session:
            server = await session.get(ExternalServer, ctx.guild.id)
            if server.min_rs <= int(level) <= server.max_rs:
                rs_level = "rs" + str(level)
                setattr(server, rs_level, int(role[3:-1]))
                await session.commit()
                await ctx.send(f"RS{level} pings set to {role}")
            else:
                if server.min_rs > int(level):
                    await ctx.send(f"{level} is below your server's current min rs of rs{server.min_rs}. If you want to change this, run `!connect {level} {server.max_rs}`")
                else:
                    await ctx.send(f"{level} is above your server's current max rs of rs{server.max_rs}. If you want to change this, run `!connect {server.max_rs} {level}`")


    @commands.command(aliases=["in", "i"])
    async def _in(self, ctx, level=None, length=60):
        if ctx.guild.id == clubs_server_id: # Run the command as usual
            level = self.rs_channel[str(ctx.message.channel)]
            await ctx.invoke(self.bot.get_command('rs'), level=int(level), length=length)
        else:
            # Check if they have the right role with Externalserver (or if it is above it)
            if level is None:
                # Get their current rs level and add them to the queue
                async with sessionmaker() as session:
                    server = await session.get(ExternalServer, ctx.guild.id)
                    role_ids = []
                    for i in range(5,12):
                        if getattr(server, "rs" + str(i)) is not None:
                            role_ids.append((i, getattr(server, "rs" + str(i))))
                    role_ids = role_ids[::-1]
                    confirmed_roles = []
                    for user_roles in ctx.author.roles:
                        for (rs_level, id) in role_ids:
                            if user_roles.id == id:
                                confirmed_roles.append(rs_level)
                    confirmed_roles.sort(reverse=True)
                    if len(confirmed_roles) == 0:
                        await ctx.send("You have no roles matching any known rs levels on this server.")
                    else:
                        level = confirmed_roles[0]
                        print("ADDING THEM TO THE QUEUE")
                        await ctx.invoke(self.bot.get_command('rs'), level=int(level), length=length, external=True)
            else:
                async with sessionmaker() as session:
                    server = await session.get(ExternalServer, ctx.guild.id)
                    level_role = getattr(server, "rs" + str(level))
                    if level_role is not None:
                        role_ids = []
                        for i in range(5,12):
                            if getattr(server, "rs" + str(i)) is not None:
                                role_ids.append((i, getattr(server, "rs" + str(i))))
                        role_ids = role_ids[::-1]
                        confirmed_roles = []
                        has_role = False
                        for user_roles in ctx.author.roles:
                            for (rs_level, id) in role_ids:
                                if user_roles.id == id:
                                    if int(rs_level) >= int(level):
                                        has_role = True
                                        break
                        if has_role:
                            await ctx.invoke(self.bot.get_command('rs'), level=int(level), length=length, external=True)
                    else:
                        await ctx.send(f"RS{level} role not set up on this server. Set it with the `!level` command.")

    @commands.command(aliases=["o"])
    async def out(self, ctx, level=None):
        if ctx.guild.id == clubs_server_id: # Run the command as usual
            level = self.rs_channel[str(ctx.message.channel)]
            await ctx.invoke(self.bot.get_command('_out'), level=level)
        else:
            if level is None:
                async with sessionmaker() as session:
                    current_queues = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars()
                    if current_queues is None:
                        await ctx.send("You are currently not in any queues")
                    else:
                        levels = [queue.level for queue in current_queues]
                        print("LEVELS", levels)
                        if len(levels) > 1:
                            sending = "You were found in these queues, please specify which queue you want to leave: "
                            sending += ', '.join(levels)
                            await ctx.send(sending)
                        elif len(levels) == 1:
                            print("Removing level", levels[0])
                            await ctx.invoke(self.bot.get_command('_out'), level=int(levels[0]), external=True)
            else:   
                await ctx.invoke(self.bot.get_command('_out'), level=level, external=True)

    @commands.command()
    async def close(self, ctx):
        async with sessionmaker() as session:
            user_talking = await session.get(Talking, ctx.author.id)
            if user_talking is None:
                await ctx.send("You are not currently connected to any servers.")
            else:
                run_id = user_talking.run_id
                servers = (await session.execute(select(Talking).where(Talking.run_id == run_id))).scalars()
                for server in servers:
                    channel = await self.bot.fetch_channel(server.channel_id)
                    await channel.send(f"```The connection has been closed by {ctx.author.display_name}.```")
                    await session.delete(server)
            await session.commit()




    @commands.Cog.listener()
    async def on_message(self, message):
        # <Message id=859239790952185876 channel=<TextChannel id=858484759994040370 name='rs-queues' position=1 nsfw=False news=False category_id=858484643632381953> type=<MessageType.default: 0> 
        # author=<Member id=384481151475122179 name='Conbonbot' discriminator='0680' bot=False nick=None guild=<Guild id=858484643632381952 name='Testing Server' shard_id=None chunked=False member_count=2>> flags=<MessageFlags value=0>>

        # See if the talking database has anything in it
        active_global = False
        async with sessionmaker() as session:
            data_check = (await session.execute(select(Talking))).scalars()
            if data_check is not None:
                active_global = True
        if active_global:
            total_info = []
            total_servers = []
            club_server_info = ()
            async with sessionmaker() as session:
                current_talking = (await session.execute(select(Talking))).scalars()
                for user in current_talking:
                    total_info.append((user.server_id, user.user_id, user.channel_id, user.timestamp))
                    total_servers.append(user.server_id)
                    if user.server_id == clubs_server_id:
                        club_server_info = (user.server_id, user.user_id, user.channel_id, user.timestamp)
            total_servers = list(set(total_servers))
            # TOTAL INFO -> SERVER ID, USER_ID, CHANNEL_ID, TIMESTAMP
            # Check if the message was sent from the select people and in the right channel
            if message.guild.id in [info[0] for info in total_info] and message.author.id in [info[1] for info in total_info] and message.channel.id in [info[2] for info in total_info]:
                if not message.author.bot:
                    if not (message.content.startswith('!') or message.content.startswith('+') or message.content.startswith('-') or message.content.startswith('%')):
                        # cut out bot messages and commands
                        async with sessionmaker() as session:
                            total_stuff = []
                            print("Total server data", total_servers)
                            for data in total_servers:
                                if data == clubs_server_id:
                                    print("CLUBS", clubs_server_id)
                                    rs_level = (await session.get(Stats, (club_server_info[1], club_server_info[3]))).rs_level
                                    clubs_webhook_string = "RS" + str(rs_level) + "_WEBHOOK"
                                    total_stuff.append((os.getenv(clubs_webhook_string), data))
                                else:
                                    server = await session.get(ExternalServer, data)
                                    total_stuff.append((server.webhook, data))
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
