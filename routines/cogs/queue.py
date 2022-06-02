import asyncio
from asyncio.locks import Condition
from logging import Logger
import re
from tabnanny import check
import time
from aiosqlite.core import LOG

import discord
import sqlite3
from discord.utils import get
from dotenv.main import load_dotenv
import psycopg2

from datetime import datetime
from discord.ext import commands, tasks
from psycopg2 import extensions
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.orm import selectinload, session
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect
from sqlalchemy import event

from random import random

from discord import Embed
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

import numpy as np

from discord import Webhook, AsyncWebhookAdapter
import aiohttp

from bot import LOGGER, RSClubBot
from bot import TESTING

import sys, os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))
load_dotenv()

rs_club_webhooks = {
    "5" : os.getenv("RS5_WEBHOOK"),
    "6" : os.getenv("RS6_WEBHOOK"),
    "7" : os.getenv("RS7_WEBHOOK"),
    "8" : os.getenv("RS8_WEBHOOK"),
    "9" : os.getenv("RS9_WEBHOOK"),
    "10" : os.getenv("RS10_WEBHOOK"),
    "11" : os.getenv("RS11_WEBHOOK")
}

club_channels = {
    5 : os.getenv("RS5_CHANNEL"),
    6 : os.getenv("RS6_CHANNEL"),
    7 : os.getenv("RS7_CHANNEL"),
    8 : os.getenv("RS8_CHANNEL"),
    9 : os.getenv("RS9_CHANNEL"),
    10 : os.getenv("RS10_CHANNEL"),
    11 : os.getenv("RS11_CHANNEL")
}

error_channel_id = os.getenv("ERROR_CHANNEL")


from routines.tables import Queue, Data, Temp, Stats, Event, ExternalServer, Talking, Banned, Feedback
from routines import sessionmaker
from routines import engine
import random


import cProfile
import pstats

if TESTING:
    clubs_server_id = 805959424081920022
else:
    clubs_server_id = 682479756104564775

# TODO: Use an actual settings file for these and channel/message ids.
RS_GROUPS = {
    'prod': {
        'rs_ping': {
            "RS5": "<@&785786197531295755>",
            "RS6": "<@&785786579826245642>",
            "RS7": "<@&785786709517795328>",
            "RS8": "<@&785786792350711808>",
            "RS9": "<@&785786898920374273>",
            "RS10": "<@&785786957782319104>",
            "RS11": "<@&800957912180457494>"
        },
        'rs_ping_1more': {
            "RS5": "<@&800958080208732231>",
            "RS6": "<@&805597027458744321>",
            "RS7": "<@&805597168849256489>",
            "RS8": "<@&805597260455870515>",
            "RS9": "<@&805596918956556308>",
            "RS10": "<@&805597317856100353>",
            "RS11": "<@&805598218666770432>"
        }
    },
    'testing': {
        'rs_ping': {
            "RS5": "<@&806018027383422998>",
            "RS6": "<@&806018102797402122>",
            "RS7": "<@&806018133835513876>",
            "RS8": "<@&806018135106519040>",
            "RS9": "<@&806018147487711313>",
            "RS10": "<@&806018150256082984>",
            "RS11": "<@&806261078295183400>"
        },
        'rs_ping_1more': {
            "RS5": "<@&806018333517938688>",
            "RS6": "<@&806018337804910592>",
            "RS7": "<@&806018340203397140>",
            "RS8": "<@&806018343696990208>",
            "RS9": "<@&806018346269016084>",
            "RS10": "<@&806018349183139890>",
            "RS11": "<@&806261118158372936>"
        }
    },
}

if TESTING:
    LOGGER.debug('Loading testing settings.')
    RS_GROUPS = RS_GROUPS.get('testing')
else:
    LOGGER.info('Loading PRODUCTION settings.')
    RS_GROUPS = RS_GROUPS.get('prod')

class RSQueue(commands.Cog, name='Queue'):

    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.success = 0
        self.error = 0
        self.event = False
        self.check_people.start()
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
        self.rs_ping = RS_GROUPS['rs_ping']
        self.rs_ping_1more = RS_GROUPS['rs_ping_1more']
        self.emojis = {
            "1️⃣": 1,
            "2️⃣": 2,
            "3️⃣": 3,
            "4️⃣": 4
        }
        
        self.failed_embed = discord.Embed(title="Failure", color=discord.Color.red())
        self.success_embed = discord.Embed(title="Success", color=discord.Color.green())

    # slash command testing
    @cog_ext.cog_slash(
        name="display_queue",
        description="Displays the queue of a specific rs level",
        options=[
            create_option(
                name="level",
                description="The rs level",
                option_type=4,
                required=True
            )
        ]
    )
    async def display_queue(self, ctx: SlashContext, level: int):
        if 5 <= level <= 11:
            async with sessionmaker() as session:
                queues = list((await session.execute(select(Queue))).scalars())
                force = False
                if ctx.guild.id == clubs_server_id:
                    force = True
                server = await session.get(ExternalServer, ctx.guild.id)
                if force or server.show:
                    embed = await self.print_queue(ctx.guild, ctx.channel, level, queues, display=False, slash=True)
                    if embed is None:
                        await ctx.send(f"No RS{level} Queues found, you can start one by typing `!in {level}`", hidden=True)
                    else:
                        await ctx.send(embed=embed, hidden=True)
                else:
                    await ctx.send("The queueing system has been turned off on this server. If you want to turn it back on, have an admin run the `!show` command", hidden=True)
        else:
            await ctx.send(f"RS{level} not found. specify a level between 5 and 11", hidden=True)

    async def get(self, data, type, value, all=False):
        if not all:
            for single in data:
                if getattr(single, type) == value:
                    return single
            else:
                return -1
        else:
            instances = []
            for single in data:
                if getattr(single, type) == value:
                    instances.append(single)
            return instances
            
    @commands.command()
    async def feedback_connect(self, ctx, server_id: int):
        if ctx.author.id == 384481151475122179:
            async with sessionmaker() as session:
                channel = (await session.get(ExternalServer, server_id)).channel_id
                feedback_add = Feedback(server_id=server_id, channel_id=channel)
                session.add(feedback_add)
                await session.commit()
            await ctx.send("Connected")
        else:
            await ctx.send("This command can only be used by Conbonbot")

    @commands.command()
    async def feedback_disconnect(self, ctx, server_id: int):
        if ctx.author.id == 384481151475122179:
            async with sessionmaker() as session:
                feedback = await session.get(Feedback, server_id)
                await session.delete(feedback)
                await session.commit()
            await ctx.send("Disconnected")
        else:
            await ctx.send("This command can only be used by Conbonbot")
        
    async def generate_run_id(self, session, event=False):
        if event:
            runs = (await session.execute(select(Event))).scalars()
        else:
            runs = (await session.execute(select(Talking))).scalars()
        ids = []
        for run in runs:
            ids.append(run.run_id)
        rand = random.randrange(1000000, 9000000)
        while rand in ids:
            rand = random.randrange(1000000, 9000000)
        return rand

    async def amount(self, session, level):
        count = 0
        level_queues = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
        for person in level_queues:
            count += int(person.amount)
        return count

    async def find(self, selection, id):
        # gets user, channel, guild
        await self.bot.wait_until_ready()
        selection = selection.lower()
        if selection in ("u", "user", "users"):
            user = self.bot.get_user(id)
            if user is None:
                try:
                    user = await self.bot.fetch_user(id)
                except:
                    user = -1
            return user
        elif selection in ("c", "channel", "channels"):
            channel = self.bot.get_channel(id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(id)
                except:
                    channel = -1
            return channel
        elif selection in ("g", "guild", "guilds"):
            guild = self.bot.get_guild(id)
            if guild is None:
                try:
                    guild = await self.bot.fetch_guild(id)
                except:
                    guild = -1
            return guild

    async def right_channel(self, ctx):
        right = False
        channel = ""
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right = True
                channel = club_channel
        return (right, channel)

    async def right_role(self, ctx, channel):
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

    async def remove_players(self, ctx, session, level):
        LOGGER.debug("Queue is 4/4, remove everyone")
        # Print out the queue
        people = list((await session.execute(select(Queue).where(Queue.level == level))).scalars())
        servers = list((await session.execute(select(ExternalServer).where(ExternalServer.show == True))).scalars())
        
        clubs_string_people = ""
        print_people = []
        external_server_ids = []
        server_user_ids = []
        LOGGER.debug(people)
        club = 0
        for person in people:
            if person.server_id != clubs_server_id:
                external_server_ids.append(person.server_id)
                server_user_ids.append((person.server_id, person.user_id))
            else:
                club = 1
                clubs_string_people += (await self.find('u', person.user_id)).mention + " "
            print_people.append(person.nickname)
        print_people = list(set(print_people))
        connecting_servers = set(external_server_ids)
        club_channel = await self.find('c', club_channels[level])
        club_guild = await self.find('g', clubs_server_id)
        if club == 1:
            # Print queue to clubs server
            await self.print_queue(session, club_guild, club_channel, level)
            await club_channel.send(f"RS{level} Ready! {clubs_string_people}")
            if len(connecting_servers) + club > 1:
                sending = "```You will now be connected to the other servers that have players in this queue. Any messages you send here will show up on all other servers and visa versa.\n"
                sending += "Note that messages will only be sent from players that were in this queue and messages from other players will be ignored as well as bot commands and bots themselves.\n"
                sending += "Once all players have decided on where to run this Red Star, have someone run !close to close the connection between the servers. If the command is not run, the connection will automatically close after 5 minutes.```"
                await club_channel.send(sending)
            else:
                await club_channel.send("Meet where?")
            connecting_servers.add(clubs_server_id)
        else:
            await club_channel.send(f"```The RS{level} queue has been filled.```")
        result = {}
        for sub in server_user_ids:
            if sub[0] in result:
                result[sub[0]] = (*result[sub[0]], *sub[1:])
            else:
                result[sub[0]] = sub
        total_list = list(result.values())
        total_str_people = []
        for server_user in total_list:
            print_str = ""
            for user in server_user[1:]:
                print_str += (await self.find('u', user)).mention + " "
            total_str_people.append((server_user[0], print_str))
        for server in servers:
            # Tell servers the queue has been filled
            if server.show and server.server_id not in connecting_servers:
                if server.min_rs <= level <= server.max_rs:
                    channel = await self.find('c', server.channel_id)
                    if channel != -1:
                        await channel.send(f"```The RS{level} queue has been filled.```")
            # Print queue to servers who had players in that queue
            elif server.show:
                guild = await self.find('g', server.server_id)
                channel = await self.find('c', server.channel_id)
                if guild != -1 and channel != -1:
                    try:
                        server_ids = [tup[0] for tup in total_str_people]
                        index = server_ids.index(server.server_id)
                        printing = total_str_people[index][1]
                    except:
                        printing = " "
                    await self.print_queue(session, guild, channel, level)
                    await channel.send(f"RS{level} Ready! {printing}")
                    if len(connecting_servers) > 1:
                        sending = "```You will now be connected to the other servers that have players in this queue. Any messages you send here will show up on all other servers and visa versa.\n"
                        sending += "Note that messages will only be sent from players that were in this queue and messages from other players will be ignored as well as bot commands and bots themselves.\n"
                        sending += "Once all players have decided on where to run this Red Star, have someone run !close to close the connection between the servers. If the command is not run, the connection will automatically close after 5 minutes.```"
                        await channel.send(sending)
                    else:
                        await channel.send("Meet where?")
        # Get RS Event data stuff
        if self.event:
            rs_run_id = await self.generate_run_id(session, True)
            await ctx.send(f"Your run id is: {rs_run_id}. Once the run is over, have one person from this queue run this command: `!rsinput {rs_run_id} <score>` (without the <>) and it will input the score into the leaderboards")
        # Track RS Stats and input into talking
        rs_run_id = await self.generate_run_id(session)
        timestamp = int(time.time())
        time_data = int(time.time())
        # Add run to event database
        if self.event:
            event_run = Event(run_id=rs_run_id, score=0, timestamp=time_data)
            session.add(event_run)
        queue_people = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
        for person in queue_people:
            print("TRACKING RS STATS AND ADDING TO TALKING DATABASE", person)
            # If it was 4/4 and only one person don't track anything
            if person.amount < 4:
                user_enter = Stats(user_id=person.user_id, timestamp=time_data, rs_level=person.level, run_id=rs_run_id)
                session.add(user_enter)
                if len(connecting_servers) > 1: # Only add them to the talking database if there's more than one total server
                    user_talking_enter = Talking(run_id=rs_run_id, server_id=person.server_id, user_id=person.user_id, timestamp=timestamp, channel_id=person.channel_id)
                    session.add(user_talking_enter)
        # Remove everyone from the queue
        await session.execute(delete(Queue).where(Queue.level == level))
        rs_log_channel = await self.find('c', 805228742678806599)
        if rs_log_channel == -1:
            rs_log_channel = await self.find('c', 806370539148541952)
        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        await rs_log_channel.send(f"RS{level} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")

    async def joining_queue(self, ctx, session, level):
        # Print to clubs server
        name = ctx.author.display_name
        count = await self.amount(session, level)
        guild = await self.find('g', clubs_server_id)
        channel = await self.find('c', club_channels[level])
        await self.print_queue(session, guild, channel, level)
        if count == 3:
            await channel.send(f"{name} joined {self.rs_ping_1more[f'RS{level}']} {self.rs_ping[f'RS{level}']} ({count}/4)")
        else:
            await channel.send(f"{name} joined {self.rs_ping[f'RS{level}']} ({count}/4)")
        # Print queues to other servers
        for server in list((await session.execute(select(ExternalServer).where(ExternalServer.show == True))).scalars()):
            if  server.min_rs <= level <= server.max_rs:
                guild = await self.find('g', server.server_id)
                channel = await self.find('c', server.channel_id)
                if guild != -1 and channel != -1:
                    await self.print_queue(session, guild, channel, level)
                    rs_level = "rs" + str(level)
                    rs_level_34 = "rs" + str(level) + "_34"
                    role_id = getattr(server, rs_level)
                    role_id_34 = getattr(server, rs_level_34)
                    role = discord.utils.get(guild.roles, id=role_id)
                    role_34 = discord.utils.get(guild.roles, id=role_id_34)
                    if count == 3:
                        if role_34 is None:
                            print_str = f"{name} joined rs{level} ({count}/4)"
                            print_str += f"\nNo roles were found for rs{level} 3/4, specify them with the `!level` command."
                            await channel.send(print_str)
                        else:
                            if role is None:
                                await channel.send(f"{name} joined {role_34.mention} ({count}/4)")
                            else:
                                await channel.send(f"{name} joined {role_34.mention} {role.mention} ({count}/4)")
                    else:
                        if role is None:
                            print_str = f"{name} joined rs{level} ({count}/4)"
                            print_str += f"\nNo roles were found for rs{level}, specify them with the `!level` command."
                            await channel.send(print_str)
                        else:
                            await channel.send(f"{name} joined {role.mention} ({count}/4)")

    async def leaving_queue(self, ctx, session, level):
        # Print info in clubs server
        queues = list((await session.execute(select(Queue).where(Queue.level == level))).scalars())
        servers = list((await session.execute(select(ExternalServer).where(ExternalServer.show == True))).scalars())
        queue_status = await self.amount(session, level)
        guild = await self.find('g', clubs_server_id)
        channel = await self.find('c', club_channels[level])
        await self.print_queue(session, guild, channel, level, False)
        await channel.send(f"{ctx.author.display_name} has left the RS{level} Queue ({queue_status}/4)")
        # Print queues to other servers
        for server in servers:
            if server.min_rs <= level <= server.max_rs:
                guild = await self.find('g', server.server_id)
                channel = await self.find('c', server.channel_id)
                if guild != -1 and channel != -1:
                    await self.print_queue(session, guild, channel, level, queues, False)
                    await channel.send(f"{ctx.author.display_name} has left the RS{level} Queue ({queue_status}/4)")
    
    async def check(self, session, error_channel):
        msg = ""
        queues = list((await session.execute(select(Queue))).scalars())
        for queue in queues:
            msg += f"Checking rs{queue.level}\n"
            minutes = int((time.time() - queue.time) / 60)
            if(queue.length-minutes > 5):
                msg += f"- {queue.nickname} has been in the queue for {minutes} minutes, {queue.length-minutes} minutes left until user is pinged\n"
            else:
                msg += f"- {queue.nickname} has been in the queue for {minutes} minutes, {queue.length-minutes+5} minutes until the user is removed\n"
            if minutes == queue.length:
                msg += f"-- Attempting to ping {queue.nickname}\n"
                # Ping the user
                user = await self.find('u', queue.user_id)
                channel = await self.find('c', queue.channel_id)
                message = await channel.send(f"{user.mention}, still in for an RS{queue.level}? React ✅ to stay in the queue, and ❌ to leave the queue")
                await message.add_reaction('✅')
                await message.add_reaction('❌')
                msg += "-- Sent message\n"
                # Add their user_id and message_id to database
                add_temp = Temp(server_id=queue.server_id, channel_id=queue.channel_id, user_id=queue.user_id, message_id=message.id, timestamp=int(time.time()+500), amount=queue.amount, level=queue.level)
                session.add(add_temp)
                msg += "-- Added to temporary database\n"
            elif minutes >= queue.length + 5:
                msg += f"-- Attempting to remove the user from the queue\n"
                # Get user and delete them from the queue database
                User_leave = (await session.get(Queue, (queue.user_id, queue.level)))
                await session.delete(User_leave)
                msg += "-- Removed from queue\n"
                # get club channel and send leaving message to all servers
                msg += "-- Sending message to servers\n"
                the_clubs_channel = await self.find('c', club_channels[queue.level])
                count = await self.amount(session, queue.level)
                await the_clubs_channel.send(f"{queue.nickname} has left RS{queue.level} ({count}/4)")
                servers = (await session.execute(select(ExternalServer).where(ExternalServer.show == True))).scalars()
                for server in servers:
                    if server.min_rs <= queue.level <= server.max_rs:
                        channel = await self.find('c', server.channel_id)
                        if channel != -1:
                            await channel.send(f"{queue.nickname} has left RS{queue.level} ({count}/4)")
                # Remove 'still in for a...' message (if it works)
                conditions  = and_(Temp.user_id == queue.user_id, Temp.level == queue.level)
                temps = list((await session.execute(select(Temp).where(conditions))).scalars())
                for temp in temps:
                    channel = await self.find('c', temp.channel_id)
                    message = discord.utils.get(await channel.history(limit=1000).flatten(), id=temp.message_id)
                    if message is not None:
                        await message.delete()
                        await session.delete(temp)
                        msg += "--- Removed Message\n"
        if(msg != ""):
            await error_channel.send(msg)

    @tasks.loop(minutes=1.0)
    async def check_people(self):
        channel = await self.find('c', error_channel_id)
        try:
            async with sessionmaker.begin() as session:
                await self.check(session, channel)
        except Exception as e:
            self.error, self.index = self.error+1, self.index+1
            self.failed_embed.clear_fields()
            self.failed_embed.add_field(name="Timestamp", value=f"{int(time.time())}")
            if len(e) > 1000:
                self.failed_embed.add_field(name="Exception", value="Error too long to show")
            else:
                self.failed_embed.add_field(name="Exception", value=f"{e}")
            self.failed_embed.add_field(name="Error/Total", value=f"{self.error}/{self.index} -> {(self.error)/(self.index)}")
            await channel.send(embed=self.failed_embed)
        else:
            self.success, self.index = self.success+1, self.index+1
            self.success_embed.clear_fields()
            self.success_embed.add_field(name="Timestamp", value=f"{int(time.time())}")
            self.success_embed.add_field(name="Success/Total", value=f"{self.success}/{self.index} -> {(self.success)/(self.index)}")
            await channel.send(embed=self.success_embed)

    @check_people.error
    async def on_check_people_error(self):
        channel = await self.find('c', error_channel_id)
        await channel.send("Check people has stopped. Restarting...")
        self.check_people.stop()
        self.check_people.start()



    @commands.command()
    async def add_bot(self, ctx, level, amount):
        if TESTING:
            async with sessionmaker() as session:
                user = Queue(server_id=ctx.guild.id, user_id=809871917946634261, amount=int(amount), level=int(level), time=int(time.time()), length=25, channel_id=ctx.channel.id, nickname="RS Club Temp Bot")
                session.add(user)
                await session.commit()
            await ctx.send("Added")
        else:
            await ctx.send("This command can only be used in testing")

    @commands.command()
    async def add_me(self, ctx, level: int, amount: int, length: int):
        if TESTING:
            async with sessionmaker() as session:
                user = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=amount, level=level, time=int(time.time()), length=length, channel_id=ctx.channel.id, nickname=ctx.author.display_name)
                session.add(user)
                await session.commit()
            await ctx.send("Added")
        else:
            await ctx.send("This command can only be used in testing")

    @commands.command()
    async def restart_tasks(self, ctx):
        self.check_people.restart()
        await ctx.send("Tasks have been restarted")

    @commands.command()
    async def github(self, ctx):
        await ctx.send(f"Here's the github link to the bot (https://github.com/Conbonbot/RS-Club-Bot). If you want to contribute feel free to make a pull request!")
    
    @commands.command()
    @commands.has_role("mod")
    async def run_check(self, ctx):
        await self.check_people.__call__()
        message = await ctx.send("Ran background task check_people()")
        await asyncio.sleep(5)
        await ctx.message.delete()
        await message.delete()

    @commands.command()
    @commands.has_role("mod")
    async def clear_cache(self, ctx):
        engine.clear_compiled_cache()
        message = await ctx.send("Engine's cache has been cleared")
        await asyncio.sleep(10)
        await ctx.message.delete()
        await message.delete()

    @commands.command(aliases=["r", "^", "staying"])
    async def refresh(self, ctx, level=None):
        if level is not None:
            level = int(level)
            async with sessionmaker() as session:
                user = await session.get(Queue, (ctx.author.id, level))
                if user is not None:
                    user.time = int(time.time())
                    queues = list((await session.execute(select(Queue))).scalars())
                    num_players = f'({await self.amount(level, queues)}/4)'
                    await ctx.send(f"{ctx.author.mention}, you are requeued for an RS{level}! {num_players}")
                    await session.commit()
                else:
                    await ctx.send(f"You aren't in any rs{level} queues")
        else:
            if ctx.guild.id == clubs_server_id:
                level = self.rs_channel[str(ctx.message.channel)]
                async with sessionmaker() as session:
                    user = await session.get(Queue, (ctx.author.id, level))
                    user.time = int(time.time())
                    queues = list((await session.execute(select(Queue))).scalars())
                    num_players = f'({await self.amount(level, queues)}/4)'
                    await ctx.send(f"{ctx.author.mention}, you are requeued for an RS{level}! {num_players}")
                    await session.commit()
            else:
                async with sessionmaker() as session:
                    user_queues = list((await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars())
                    if len(user_queues) == 0:
                        await ctx.send(f"{ctx.author.mention}, you aren't in any rs queues")
                    elif len(user_queues) == 1:
                        level = user_queues.first().level
                        user = await session.get(Queue, (ctx.author.id, level))
                        user.time = int(time.time())
                        queues = list((await session.execute(select(Queue))).scalars())
                        num_players = f'({await self.amount(level, queues)}/4)'
                        await ctx.send(f"{ctx.author.mention}, you are requeued for an RS{level}! {num_players}")
                        await session.commit()
                    else:
                        levels = [str(queue.level) for queue in user_queues]
                        await ctx.send(f"You were found in these queues `{', '.join(levels)}`. Specify which one you'd like to refresh by adding the rs level to the end of the command.")
   
    @commands.command()
    async def reset(self, ctx, level=None):
        async with sessionmaker.begin() as session:
            if level is None:
                await ctx.send("Please specify an rs level")
            else:
                count = await self.amount(session, int(level))
                if count > 3:
                    await session.execute(delete(Queue).where(Queue.level == int(level)))
                    await ctx.send("The queue has been reset")
                else:
                    await ctx.send("The queue is not stuck at 4/4")

    @commands.command(pass_context=True)
    async def corp(self, ctx, *corp):
        member = await ctx.guild.fetch_member(ctx.author.id)
        LOGGER.debug(member.display_name)
        if member.display_name.startswith("["):
            name = member.display_name[member.display_name.find("]") + 2:]
        else:
            name = member.display_name
        nick = f"[{' '.join(corp)}] " + name
        await member.edit(nick=nick)
        await ctx.send(f"{ctx.author.display_name}, Your corp has been set to {' '.join(corp)}")

    @commands.command()
    async def rsc(self, ctx):
        role = discord.utils.get(ctx.author.guild.roles, name='🌟')
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            msg = await ctx.send("The RS Channels have been hidden")
            await asyncio.sleep(15)
            await ctx.message.delete()
            await msg.delete()
        else:
            await ctx.author.add_roles(role)
            msg = await ctx.send("The RS Channels have been restored")
            await asyncio.sleep(15)
            await ctx.message.delete()
            await msg.delete()

    @commands.command()
    @commands.has_role("mod")
    async def clear(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)

    @commands.command()
    @commands.has_role("mod")
    async def clear_database(self, ctx, level=None):
        if level is not None:
            async with sessionmaker.begin() as session:
                await session.execute(delete(Queue).where(Queue.level == int(level)))
            message = await ctx.send(f"RS{level} Queue cleared")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await message.delete()
        else:
            await ctx.send("Please specify an rs level to clear")

    async def remove_temp_data(self):
        LOGGER.info("Running remove_temp")
        async with sessionmaker.begin() as session:
            temps = list((await session.execute(select(Temp))).scalars())
            for temp in temps:
                if(temp.timestamp <= int(time.time())):
                    channel = await self.find('c', temp.channel_id)
                    await session.delete(temp)
                    if(channel != -1):
                        message = discord.utils.get(await channel.history(limit=1000).flatten(), id=temp.message_id)
                        if(message is not None):
                            await message.delete()
    
    async def clear_temp(self):
        while True:
            await asyncio.gather(asyncio.sleep(3600), self.remove_temp_data())
    
    @commands.command()
    @commands.has_role("mod")
    async def start_temp_clear(self, ctx):
        await ctx.send("Task has been started")
        await self.clear_temp()
        
    
    @commands.command(name='1', help="Type +1/-1, which will add you/remove you to/from a RS Queue")
    async def _one(self, ctx, level=None, length=25):
        if ctx.message.content[0] == "+":
            await self.entering_queue_basic_checks(ctx, level, length, ctx.message.content[1])
        elif ctx.message.content[0] == "-":
            await self.removing_from_queue_check(ctx, level, ctx.message.content[1])

    @commands.command(name='2', help="Type +2/-2, which will add you/remove you and another person to/from a RS Queue")
    async def _two(self, ctx, level=None, length=25):
        if ctx.message.content[0] == "+":
            await self.entering_queue_basic_checks(ctx, level, length, ctx.message.content[1])
        elif ctx.message.content[0] == "-":
            await self.removing_from_queue_check(ctx, level, ctx.message.content[1])

    @commands.command(name='3', help="Type +3/-4, which will add you/remove you and 2 other people to/from a RS Queue")
    async def _three(self, ctx, level=None, length=25):
        if ctx.message.content[0] == "+":
            await self.entering_queue_basic_checks(ctx, level, length, ctx.message.content[1])
        elif ctx.message.content[0] == "-":
            await self.removing_from_queue_check(ctx, level, ctx.message.content[1])

    async def entering_queue_basic_checks(self, ctx, level, length, count, only_allow_one=False):
        async with sessionmaker.begin() as session:
            able_to_join = False
            run_from_external = False
            entering_queue_level = level
            # Check if the person has been banned
            person = await session.get(Banned, ctx.author.id)
            if person is None:
                # Check if command was run inside of The Clubs Server
                if ctx.guild.id == clubs_server_id:
                    level = self.rs_channel[str(ctx.message.channel)]
                    # check if command was sent in an rs channel
                    if level != -1: 
                        has_right_role = False
                        for role in ctx.author.roles:
                            if str(role)[2:].isnumeric():  # Checks main role (rs#)
                                if int(str(role)[2:]) >= int(self.rs_channel[str(ctx.message.channel)]):
                                    has_right_role = True
                                    break
                            elif str(role)[2:-12].isnumeric():  # Checks 3/4 role (rs# 3/4 1more)
                                if int(str(role)[2:-12]) >= int(self.rs_channel[str(ctx.message.channel)]):
                                    has_right_role = True
                                    break
                            elif str(role)[2:-2].isnumeric():  # Checks silent role (rs# s)
                                if int(str(role)[2:-2]) >= int(self.rs_channel[str(ctx.message.channel)]):
                                    has_right_role = True
                                    break
                        if has_right_role:
                            able_to_join = True
                            entering_queue_level = level
                        else:
                            await ctx.send(f"{ctx.author.mention}, you aren't RS{level}")
                    else:
                        msg = await ctx.send("Command not run in an RS Channel")
                        await asyncio.sleep(10)
                        await ctx.message.delete()
                        await msg.delete()
                # Command was run outside of The Clubs Server (external)
                else:
                    run_from_external = True
                    server = await session.get(ExternalServer, ctx.guild.id)
                    # Check if the server is set up with the clubs
                    if server is not None:
                        # Check if the queueing system is active
                        if server.show:
                            # Check if the server's queue channel is the one the command was set in
                            if server.channel_id == ctx.channel.id:
                                if level is None:
                                    role_ids = []
                                    role_types = ["rs", "rs_34", "rs_silent"]
                                    for role in role_types:
                                        for i in range(5,12):
                                            check_role = role[:2] + str(i) + role[2:]
                                            if getattr(server, check_role) is not None:
                                                role_ids.append((i, getattr(server, check_role)))
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
                                        entering_queue_level = confirmed_roles[0]
                                        able_to_join = True
                                else:
                                    # check main, 3/4, and silent roles
                                    level_role = getattr(server, "rs" + str(level))
                                    level_34_role = getattr(server, "rs" + str(level) + "_34")
                                    level_silent_role = getattr(server, "rs" + str(level) + "_silent")
                                    if level_role is not None or level_34_role is not None or level_silent_role is not None:
                                        role_ids = []
                                        role_types = ["rs", "rs_34", "rs_silent"]
                                        for role in role_types:
                                            for i in range(5,12):
                                                check_role = role[:2] + str(i) + role[2:]
                                                if getattr(server, check_role) is not None:
                                                    role_ids.append((i, getattr(server, check_role)))
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
                                            able_to_join = True
                                    else:
                                        await ctx.send(f"RS{level} role not set up on this server. Set it with the `!level` command.")
                            # Command not run in the server's queue channel
                            else:
                                msg = await ctx.send("Command not run in your server's queueing channel")
                                await asyncio.sleep(10)
                                await ctx.message.delete()
                                await msg.delete()
                        # Server's queueing system was disabled
                        else:
                            msg = await ctx.send("The queueing system has been turned off on this server. If you want to turn it back on, have an admin run the `!show` command")
                            await asyncio.sleep(45)
                            await ctx.message.delete()
                            await msg.delete()
                    else:
                        message = await ctx.send("The bot has not been configured for queueing yet, run `!help e` and follow the directions")
                        await asyncio.sleep(60)
                        await ctx.message.delete()
                        await message.delete()
            # Person was banned from using the bot
            else:
                await ctx.send("You are currently banned from using the bot.")
            # Run the further_checking method if everything else passes
            if able_to_join:
                await self.queue_further_checks(ctx, session, entering_queue_level, length, count, run_from_external, only_allow_one)

    async def queue_further_checks(self, ctx, session, level, length, count, external, only_allow_one):
        # Check for only_allow_one
        count = int(count)
        level = int(level)
        allowed_to_join = True
        reason = ""
        user_current_queue = await session.get(Queue, (ctx.author.id, level))
        if only_allow_one:
            user_current_queue = await session.get(Queue, (ctx.author.id, level))
            if user_current_queue is not None:
                allowed_to_join = False
                if user_current_queue.channel_id != ctx.channel.id:
                    original_guild = await self.find("g", user_current_queue.server_id)
                    reason = f"you are trying to add yourself to a queue you are in from a different server. run the command ({ctx.message.content}) in the \"{original_guild.name}\" server"
                else:
                    reason = "you are already in the queue you are trying to join. If you want to add yourself again to the queue, use the `+1` command"
        if allowed_to_join:
            current_queue_status = await self.amount(session, level)
            # Check if queue would be more than 4/4 if they were added
            if current_queue_status + count > 4:
                await ctx.send(f"{ctx.author.mention}, the queue is currently at {current_queue_status}/4, adding {count} would overfill the queue")
            else:
                # Check if they don't exist on this queue
                if user_current_queue is None:
                    user = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=count, level=level, time=int(time.time()), length=int(length), channel_id=ctx.channel.id, nickname=ctx.author.display_name)
                    session.add(user)
                # They were found in this queue, so update their position
                else:
                    user_current_queue.amount += count
                    user_current_queue.time = int(time.time())
                    user_current_queue.length = int(length)
                if current_queue_status + count < 4:
                    await self.joining_queue(ctx, session, level)
                else:
                    await self.remove_players(ctx, session, level)
                    
        # Not allowed to join the queue because of {reason}
        else:
            await ctx.send(f"{ctx.author.mention}, {reason}")

    async def removing_from_queue_check(self, ctx, level, amount):
        amount = int(amount)
        async with sessionmaker.begin() as session:
            # Get the queues they are in
            user_queues = list((await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars())
            if len(user_queues) == 0: # Not found in any queues
                await ctx.send(f"{ctx.author.mention}, You aren't in any RS Queues at the moment")
            # They were found in some queue
            else:
                # Check if the command was sent in The Clubs Server
                if ctx.guild.id == clubs_server_id:
                    level = self.rs_channel[str(ctx.message.channel)]
                    await self.remove_from_queue(ctx, session, level, amount)
                else:
                    server = await session.get(ExternalServer, ctx.guild.id)
                    # Check if the server is set up with the bot
                    if server is not None:
                        # Check if the server queueing system is active
                        if server.show:
                            # Check if the commmand was sent in the server's rs channel
                            if server.channel_id == ctx.channel.id:
                                # Check if the level is none
                                if level is None:
                                    # Check if command was run the server's queueing channel
                                    if server.channel_id == ctx.channel.id:
                                        levels_of_current_queues = [str(queue.level) for queue in user_queues]
                                        if len(user_queues) > 1:
                                            sending = "You were found in these queues, please specify which queue you want to leave: "
                                            sending += ', '.join(levels_of_current_queues)
                                            await ctx.send(sending)
                                        else:
                                            await self.remove_from_queue(ctx, session, levels_of_current_queues[0], amount)
                                # Remove them with the level they want
                                else:
                                    await self.remove_from_queue(ctx, session, level, amount)
                            # The command was not run the server's queueing channel
                            else:
                                msg = await ctx.send("Command not run in your server's queueing channel")
                                await asyncio.sleep(10)
                                await ctx.message.delete()
                                await msg.delete()
                        # The server has the queueing system turned off
                        else:
                            msg = await ctx.send("The queueing system has been turned off on this server. If you want to turn it back on, have an admin run the `!show` command")
                            await asyncio.sleep(45)
                            await ctx.message.delete()
                            await msg.delete()
                    # Server is not configured with the bot
                    else:
                        msg = await ctx.send("The bot has not been configured for queueing yet, run `!help e` and follow the directions")
                        await asyncio.sleep(60)
                        await ctx.message.delete()
                        await msg.delete()
                        
    async def remove_from_queue(self, ctx, session, level, amount):
        level = int(level)
        current_queue = await session.get(Queue, (ctx.author.id, level))
        # If they are removing themselves from the queue as a whole, remove them from the database
        if amount >= current_queue.amount:
            await session.delete(current_queue)
        # Update their database entry with the new amount
        else:
            current_amount = current_queue.amount
            current_queue.amount = current_amount - amount
        await self.leaving_queue(ctx, session, level)

    @commands.command(help="Use this command (!i or !in) to join a RS Queue")
    async def rs(self, ctx, level=None, length=25):
        await self.entering_queue_basic_checks(ctx, level, length, 1, True)

    @commands.command(aliases=["q"], help="(!queue or !q) will show the current RS Queues")
    async def queue(self, ctx, level=None):
        async with sessionmaker.begin() as session:
            servers = list((await session.execute(select(ExternalServer))).scalars())
            if ctx.guild.id == clubs_server_id:
                level = self.rs_channel[str(ctx.message.channel)]
                await self.print_queue(session, ctx.guild, ctx.channel, level)
            else:
                server = await self.get(servers, "server_id", ctx.guild.id)
                if server != -1 and server.show:
                    if level == None:
                        await ctx.send("Please specify an RS Queue to show with `!q #` or see all queues with `!q all/a`")
                    elif level == "all" or level == "a":
                        print_queues = []
                        for i in range(5,12):
                            print_queues.append(await self.print_queue(session, ctx.guild, ctx.channel, i, display=False))
                        printed = False
                        for check in print_queues:
                            if check:
                                printed = True
                        if not printed:
                            await ctx.send("No queues were found.")
                    else:
                        await self.print_queue(session, ctx.guild, ctx.channel, int(level))
                else:
                    msg = await ctx.send("The queueing system has been turned off on this server. If you want to turn it back on, have an admin run the `!show` command")
                    await asyncio.sleep(45)
                    await ctx.message.delete()
                    await msg.delete()

    async def print_queue(self, session, guild, channel, level, display=True, slash=False):
        rs_mods = list((await session.execute(select(Data))).scalars())
        extras = {
            'croid': discord.utils.get(self.bot.emojis, name='croid'),
            'influence': discord.utils.get(self.bot.emojis, name='influence'),
            'nosanc': discord.utils.get(self.bot.emojis, name='nosanc'),
            'notele': discord.utils.get(self.bot.emojis, name='notele'),
            'rse': discord.utils.get(self.bot.emojis, name='rse'),
            'suppress': discord.utils.get(self.bot.emojis, name='suppress'),
            'unity': discord.utils.get(self.bot.emojis, name='unity'),
            'veng': discord.utils.get(self.bot.emojis, name='veng'),
            'barrage': discord.utils.get(self.bot.emojis, name='barrage'),
            'laser': discord.utils.get(self.bot.emojis, name='laser'),
            'dart': discord.utils.get(self.bot.emojis, name='dart'),
            'battery': discord.utils.get(self.bot.emojis, name='battery'),
            'solo': discord.utils.get(self.bot.emojis, name='solo'),
            'solo2': discord.utils.get(self.bot.emojis, name='solo2'),
            'mass': discord.utils.get(self.bot.emojis, name='mass')
        }
        mods = [(str(column))[5:] for column in inspect(Data).c]
        mods = mods[1:]
        people = list((await session.execute(select(Queue).where(Queue.level == level))).scalars())
        count = 0
        counting = []
        for person in people:
            counting.append(person.amount)
            count += int(person.amount)
        if count > 0:
            rsmods = []
            user_ids = []
            list_people = []
            for person in people:
                user = await self.find('u', person.user_id)
                user_ids.append(user.id)
                list_people.append(person.nickname)
                users_mods = await self.get(rs_mods, "user_id", person.user_id)
                i = 0
                temp = ""
                LOGGER.debug(f"Here is users_mods: {users_mods}")
                if users_mods != -1:
                    for mod in mods:
                        if(getattr(users_mods, mod) == True):
                            temp += " " + (str(extras[mods[i]]))
                        i += 1
                rsmods.append(temp)
            str_people = ""
            emoji_count = 0
            i = 0
            LOGGER.debug(f"List People {list_people}")
            for person in people:
                for j in range(counting[i]):
                    str_people += str(list(self.emojis)[emoji_count])
                    emoji_count += 1
                # Server_id, user_id, amount, level
                str_people += " " + list_people[i] + rsmods[i] + " 🕒 " + str(int((time.time() - int(person.time)) / 60)) + "m"
                str_people += "\n"
                i += 1
            # Get cool colors for the embed
            if guild.id == clubs_server_id:
                role_id = int((self.rs_ping[f'RS{level}'])[3:-1])
            else:
                server = await session.get(ExternalServer, guild.id)
                rs_level = "rs" + str(level)
                role_id = getattr(server, rs_level)
                if role_id is None:
                    rs_level = "rs" + str(level) + "_34"
                    role_id = getattr(server, rs_level)
                if role_id is None:
                    rs_level = "rs" + str(level) + "_silent"
                    role_id = getattr(server, rs_level)
            role = discord.utils.get(guild.roles, id=role_id)
            if role is not None:
                queue_embed = discord.Embed(color=role.color, title=f"The Current RS{level} Queue ({await self.amount(session, level)}/4)", description=str_people)
            else:
                queue_embed = discord.Embed(color=discord.Color.red(), title=f"The Current RS{level} Queue ({await self.amount(session, level)}/4)", description=str_people)
            if not slash:
                await channel.send(embed=queue_embed)
                return True
            else:
                return queue_embed
        else:
            if display:
                await channel.send(f"No RS{level} Queues found, you can start one by typing `!in {level}`")
            else:
                return False


def setup(bot):
    bot.add_cog(RSQueue(bot))
    LOGGER.debug('RS Queueing loaded')
