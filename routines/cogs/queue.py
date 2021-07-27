import asyncio
from asyncio.locks import Condition
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
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect
from sqlalchemy import event

from random import random

from bot import LOGGER
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

from routines.tables import Queue, Data, Temp, Stats, Event, ExternalServer, Talking
from routines import sessionmaker
from routines import engine
import random

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



    async def generate_run_id(self, event=False):
        async with sessionmaker.begin() as session:
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

    async def amount(self, level):
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
            count = 0
            for person in people:
                count += int(person.amount)
            return count
                
    async def queue_time(self, user_id, amount, level):
        print("QUEUE_TIME", user_id, amount, level)
        async with sessionmaker() as session:
            person = (await session.get(Queue, (user_id, amount, level)))
            data =  int((time.time() - int(person.time)) / 60)
            return data

    async def check(self):
        async with sessionmaker() as session:
            results = (await session.execute(select(Queue))).scalars()
            for queue in results:
                minutes = int((time.time() - queue.time) / 60)
                if minutes == queue.length:
                    # Ping the user
                        user = await self.bot.fetch_user(queue.user_id)
                        channel = await self.bot.fetch_channel(queue.channel_id)
                        message = await channel.send(
                            f"{user.mention}, still in for a RS{queue.level}? React ✅ to stay in the queue, and ❌ to leave the queue")
                        await message.add_reaction('✅')
                        await message.add_reaction('❌')
                        # Add their user_id and message_id to database
                        add_temp = Temp(server_id=queue.server_id, channel_id=queue.channel_id, user_id=queue.user_id, message_id=message.id, amount=queue.amount, level=queue.level)
                        session.add(add_temp)
                        await session.commit()
                elif minutes >= queue.length + 5:
                        User_leave = (await session.get(Queue, (queue.user_id, queue.amount, queue.level)))
                        await session.delete(User_leave)
                        await session.commit()
                        user = await self.bot.fetch_user(queue.user_id)
                        channel = await self.bot.fetch_channel(queue.channel_id)
                        await channel.send(f"{user.display_name} has left RS{queue.level} ({await self.amount(queue.level)}/4)")
                        conditions = and_(Temp.user_id == queue.user_id, Temp.level == queue.level)
                        id = (await session.execute(select(Temp).where(conditions))).scalars()
                        for i in id:
                            if i.channel_id == queue.channel_id:
                                message = await channel.fetch_message(i.message_id)
                                await message.delete()
                        conditions = and_(Temp.server_id == queue.server_id, Temp.user_id == queue.user_id, Temp.level == queue.level)
                        await session.execute(delete(Temp).where(conditions))
                        await session.commit()
            await session.commit()
        
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

    async def remove_players(self, ctx, level):
        LOGGER.debug("Queue is 4/4, remove everyone")
        # Print out the queue
        async with sessionmaker() as session:
            people = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
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
                    clubs_string_people += (await self.bot.fetch_user(person.user_id)).mention + " "
                print_people.append((await self.bot.fetch_user(person.user_id)).display_name)
        print_people = list(set(print_people))
        connecting_servers = set(external_server_ids)
        club_channel = await self.bot.fetch_channel(self.club_channels[level])
        club_guild = await self.bot.fetch_guild(clubs_server_id)
        if club == 1:
            # Print queue to clubs server
            await self.print_queue(club_guild, club_channel, level)
            await club_channel.send(f"RS{level} Ready! {clubs_string_people}")
            if len(connecting_servers) + club > 1:
                sending = "```You will now be connected to the other servers that have players in this queue. Any messages you send here will show up on all other servers and visa versa.\n"
                sending += "Note that messages will only be sent from players that were in this queue and messages from other players will be ignored as well as bot commands and bots themselves.\n"
                sending += "Once all players have decided on where to run this Red Star, have someone run !close to close the connection between the servers. If the command is not run, the connection will automatically close after 5 minutes```"
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
                print_str += (await self.bot.fetch_user(user)).mention + " "
            total_str_people.append((server_user[0], print_str))
        async with sessionmaker() as session:
            servers = (await session.execute(select(ExternalServer))).scalars()
            for server in servers:
                # Tell servers the queue has been filled
                if server.server_id not in connecting_servers:
                    if server.min_rs <= level <= server.max_rs:
                        channel = await self.bot.fetch_channel(server.channel_id)
                        await channel.send(f"```The RS{level} queue has been filled.```")
                # Print queue to servers who had players in that queue
                else:
                    channel = await self.bot.fetch_channel(server.channel_id)
                    guild = await self.bot.fetch_guild(server.server_id)
                    try:
                        server_ids = [tup[0] for tup in total_str_people]
                        index = server_ids.index(server.server_id)
                        printing = total_str_people[index][1]
                    except:
                        printing = " "
                    await self.print_queue(guild, channel, level)
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
            rs_run_id = await self.generate_run_id(True)
            await ctx.send(f"Your run id is: {rs_run_id}. Once the run is over, have one person from this queue run this command: `!rsinput {rs_run_id} <score>` (without the <>) and it will input the score into the leaderboards")
        # Track RS Stats and input into talking
        rs_run_id = await self.generate_run_id()
        timestamp = int(time.time())
        async with sessionmaker() as session:
            time_data = int(time.time())
            # Add run to event database
            if self.event:
                event_run = Event(run_id=rs_run_id, score=0, timestamp=time_data)
                session.add(event_run)
                await session.commit()
            queue_people = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
            for person in queue_people:
                print("TRACKING RS STATS AND ADDING TO TALKING DATABASE", person)
                # If it was 4/4 and only one person don't track anything
                if person.amount < 4:
                    user_enter = Stats(user_id=person.user_id, timestamp=time_data, rs_level=person.level, run_id=rs_run_id)
                    session.add(user_enter)

                    user_talking_enter = Talking(run_id=rs_run_id, server_id=person.server_id, user_id=person.user_id, timestamp=timestamp, channel_id=person.channel_id)
                    session.add(user_talking_enter)
                    await session.commit()
                pass
            await session.commit()
        # Remove everyone from the queue
        async with sessionmaker() as session:
            queue_people = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
            for person in queue_people:
                await session.delete(person)
            await session.commit()
        try:
            rs_log_channel = await self.bot.fetch_channel(805228742678806599)
        except:
            rs_log_channel = await self.bot.fetch_channel(806370539148541952)
        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        await rs_log_channel.send(f"RS{level} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")

    async def joining_queue(self, ctx, level):
        # Print to clubs server
        name = ctx.author.display_name
        count = await self.amount(level)
        guild = await self.bot.fetch_guild(clubs_server_id)
        channel = await self.bot.fetch_channel(self.club_channels[level])
        await self.print_queue(guild, channel, level)
        if count == 3:
            await channel.send(f"{name} joined {self.rs_ping_1more[f'RS{level}']} ({count}/4)")
        else:
            await channel.send(f"{name} joined {self.rs_ping[f'RS{level}']} ({count}/4)")
        # Print queues to other servers
        async with sessionmaker() as session:
            servers = (await session.execute(select(ExternalServer))).scalars()
            for server in servers:
                if level <= server.max_rs:
                    guild = await self.bot.fetch_guild(server.server_id)
                    channel = await self.bot.fetch_channel(server.channel_id)
                    await self.print_queue(guild, channel, level)
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
                            await channel.send(f"{name} joined {role_34.mention} ({count}/4)")
                    else:
                        if role is None:
                            print_str = f"{name} joined rs{level} ({count}/4)"
                            print_str += f"\nNo roles were found for rs{level}, specify them with the `!level` command."
                            await channel.send(print_str)
                        else:
                            await channel.send(f"{name} joined {role.mention} ({count}/4)")

    async def leaving_queue(self, ctx, level):
        # Print info in clubs server
        guild = await self.bot.fetch_guild(clubs_server_id)
        channel = await self.bot.fetch_channel(self.club_channels[level])
        await self.print_queue(guild, channel, level, False)
        await channel.send(f"{ctx.author.display_name} has left the RS{level} Queue ({await self.amount(level)}/4)")
        # Print queues to other servers
        async with sessionmaker() as session:
            servers = (await session.execute(select(ExternalServer))).scalars()
            for server in servers:
                if server.min_rs <= level <= server.max_rs:
                    guild = await self.bot.fetch_guild(server.server_id)
                    channel = await self.bot.fetch_channel(server.channel_id)
                    await self.print_queue(guild, channel, level, False)
                    await channel.send(f"{ctx.author.display_name} has left the RS{level} Queue ({await self.amount(level)}/4)")

    @tasks.loop(minutes=1.0)
    async def check_people(self):
        try:
            await self.check()
        except Exception as e:
            if not TESTING:
                self.error, self.index = self.error+1, self.index+1
                check_embed = discord.Embed(
                    title="Failure",
                    color=discord.Color.red()
                )
                check_embed.add_field(name="Timestamp", value=f"{int(time.time())}")
                check_embed.add_field(name="Exception", value=f"{e}")
                check_embed.add_field(name="Error/Total", value=f"{self.error}/{self.index} -> {(self.error)/(self.index)}")
            if TESTING:
                pass
        else:
            if not TESTING:
                self.success, self.index = self.success+1, self.index+1
                check_embed = discord.Embed(
                    title="Success",
                    color=discord.Color.green()
                )
                check_embed.add_field(name="Timestamp", value=f"{int(time.time())}")
                check_embed.add_field(name="Success/Total", value=f"{self.success}/{self.index} -> {(self.success)/(self.index)}")
        finally:
            if not TESTING:
                channel = await self.bot.fetch_channel(858406227523403776)
                await channel.send(embed=check_embed)
    
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
    async def refresh(self, ctx):
        async with sessionmaker() as session:
            conditions  = and_(Queue.user_id == ctx.author.id, Queue.level == self.rs_channel[str(ctx.message.channel)])
            times = (await session.execute(select(Queue).where(conditions))).scalars()
            times.first().time = int(time.time())
            rs_level = f'RS{self.rs_channel[str(ctx.message.channel)]}'
            num_players = f'({await self.amount(self.rs_channel[str(ctx.message.channel)])}/4)'
            await ctx.send(f"{ctx.author.mention}, you are requeued for a {rs_level}! {num_players}")
            await session.commit()

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
        await ctx.send(f"{ctx.author.display_name}, Your corp has been set to {corp}")


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
            async with sessionmaker() as session:
            #await ctx.send(f"The RS{level} queue has been cleared")
                users = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
                for user in users:
                    await session.delete(user)
                await session.commit()
            message = await ctx.send(f"RS{level} Queue cleared")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await message.delete()
        else:
            async with sessionmaker() as session:
                for level in range(5, 12):
                    users = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
                    for user in users:
                        await session.delete(user)
                await session.commit()
            message = await ctx.send("All queues cleared")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await message.delete()


    
            

    @commands.command(name='1', help="Type +1/-1, which will add you/remove you to/from a RS Queue")
    async def _one(self, ctx, length=60):
        await self.everything(ctx, ctx.message.content[0], ctx.message.content[1], length, ctx.channel.id)

    @commands.command(name='2', help="Type +2/-2, which will add you/remove you and another person to/from a RS Queue")
    async def _two(self, ctx, length=60):
        await self.everything(ctx, ctx.message.content[0], ctx.message.content[1], length, ctx.channel.id)

    @commands.command(name='3', help="Type +3/-4, which will add you/remove you and 2 other people to/from a RS Queue")
    async def _three(self, ctx, length=60):
        await self.everything(ctx, ctx.message.content[0], ctx.message.content[1], length, ctx.channel.id)

    async def everything(self, ctx, prefix, count, length, channel_id):
        LOGGER.debug(f"Running the everything command")
        LOGGER.debug(f"Values: Prefix: {prefix}, Count: {count}, length: {length}, channel_id: {channel_id}")
        count = int(count)
        if prefix == "+":
            channel_info = await self.right_channel(ctx)
            channel = channel_info[1]
            if channel_info[0]: 
                if await self.right_role(ctx, channel):
                    if length >= 5 and length <= 11:
                        length = 60
                    # check if adding amount would overfill the queue
                    queue_status = await self.amount(self.rs_channel[channel])
                    if int(queue_status) + count > 4:
                        await ctx.send(f"{ctx.author.mention}, adding {count} people to the queue would overfill the queue")
                    else:
                        # check if they are in any other queues
                        async with sessionmaker() as session:
                            data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars().all()
                            await session.commit()
                        if len(data) == 0:  # They weren't found in the database, add them
                            LOGGER.debug("Adding them to the queue")
                            User_entering_queue = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=count, level=self.rs_channel[channel], time=int(time.time()), length=length, channel_id=channel_id, nickname=ctx.author.display_name)
                            session.add(User_entering_queue)
                            await session.commit()
                            # Check if queue is 4/4
                            if await self.amount(self.rs_channel[channel]) == 4:
                                await self.remove_players(ctx, self.rs_channel[channel])
                            else:
                                await self.joining_queue(ctx, self.rs_channel[channel])
                        else:
                            LOGGER.debug("They were found on multiple queues, find all queues")
                            # see what queue they are on, and either update their current position or new position
                            async with sessionmaker.begin() as session:
                                current_data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars()
                                current_queues = []
                                for data in current_data:
                                    current_queues.append((data.level, data.amount))
                            current_queues.append((self.rs_channel[channel], count))
                            LOGGER.debug(f'Current Queues: {current_queues}')
                            D = {}
                            for (x, y) in current_queues:
                                if x not in D.keys():
                                    D[x] = y
                                else:
                                    D[x] += y
                            final_queues = [(x, D[x]) for x in D.keys()]
                            LOGGER.debug(final_queues)
                            LOGGER.debug("Above is what should be the final queue status")
                            # append the queue they wanna join to
                            for queue in final_queues:
                                if queue[0] == self.rs_channel[channel]:
                                    # Check if adding amount to the queue would make it 4/4
                                    if await self.amount(self.rs_channel[channel]) + count > 4:
                                        pass
                                    else:
                                        # check to see if we need to update their position or add another position
                                        async with sessionmaker() as session:
                                            conditions = and_(Queue.user_id == ctx.author.id, Queue.level == self.rs_channel[channel])
                                            data = (await session.execute(select(Queue).where(conditions))).scalars().all()
                                            await session.commit()
                                            if len(data) == 0:
                                                # They weren't found elsewhere, add them to the new queue
                                                user = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=queue[1], level=self.rs_channel[channel], time=int(time.time()), length=length, channel_id=channel_id, nickname=ctx.author.display_name)
                                                session.add(user)
                                                await session.commit()
                                            else:
                                                # They were found on another queue, so update their position
                                                for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                                    if(data.level == queue[0]):
                                                        pre_amount = data.amount
                                                        user = await session.get(Queue, (ctx.author.id, pre_amount, self.rs_channel[channel]))
                                                        user.amount = int(queue[1])
                                                        user.time = int(time.time())
                                                        user.length = length
                                                        break
                                            await session.commit()
                                        if await self.amount(queue[0]) == 4:
                                            await self.remove_players(ctx, self.rs_channel[channel])
                                        else:
                                            await self.joining_queue(ctx, self.rs_channel[channel])
                else:
                    await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")
            else:
                msg = await ctx.send("Command not run in an RS Channel")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await msg.delete()
        elif prefix == "-":
            LOGGER.debug("- command run, attempting to remove them from queue")
            async with sessionmaker.begin() as session:
                conditions = and_(Queue.user_id == ctx.author.id, Queue.level == self.rs_channel[str(ctx.message.channel)])
                result = (await session.execute(select(Queue).where(conditions))).scalars()
                LOGGER.debug(result)
                if result is None:  # Didn't find them in any queues
                    await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues at the moment")
                else:  # Remove count of them from the queue
                    # Get the level and amount data
                    # Check if removing count would remove more than they are in
                    current_data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars()
                    current_queues = []
                    for data in current_data:
                        current_queues.append((data.level, data.amount))
                    adding_queue = (self.rs_channel[str(ctx.message.channel)], -count)
                    current_queues.append(adding_queue)
                    D = {}
                    for (x, y) in current_queues:
                        if x not in D.keys():
                            D[x] = y
                        else:
                            D[x] += y
                    final_queues = [(x, D[x]) for x in D.keys()]
                    LOGGER.debug(final_queues)
                    LOGGER.debug("above is the final queues of that person")
            for queue in final_queues:
                # Remove only count from the queue they sent the message in
                if queue[0] == self.rs_channel[str(ctx.message.channel)]:
                    LOGGER.debug(queue)
                    if queue[1] <= 0:
                        async with sessionmaker() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                LOGGER.debug(f"data.level: {data.level}, {queue[0]}")
                                if(data.level == queue[0]):
                                    pre_amount = data.amount
                                    LOGGER.debug(f"pre_amount {pre_amount}")
                                    user = await session.get(Queue, (ctx.author.id, pre_amount, self.rs_channel[str(ctx.message.channel)]))
                                    LOGGER.debug(f"User: {user}")
                                    await session.delete(user)
                                    await session.commit()
                                    break
                    else:
                        async with sessionmaker() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                if(data.level == queue[0]):
                                    pre_amount = data.amount
                                    user = await session.get(Queue, (ctx.author.id, pre_amount, self.rs_channel[str(ctx.message.channel)]))
                                    user.amount = int(queue[1])
                                    await session.commit()
                                    break
                            LOGGER.debug("updated the queue they were in")
            await self.print_queue(ctx.guild, ctx.channel, self.rs_channel[str(ctx.message.channel)], False)
            await ctx.send(f"{ctx.author.display_name} has left the RS{self.rs_channel[str(ctx.message.channel)]} Queue ({await self.amount(self.rs_channel[str(ctx.message.channel)])}/4)")
            servers = (await session.execute(select(ExternalServer))).scalars()
            for server in servers:
                level = self.rs_channel[str(ctx.message.channel)]
                if level <= server.max_rs:
                    guild = await self.bot.fetch_guild(server.server_id)
                    channel = await self.bot.fetch_channel(server.channel_id)
                    await self.print_queue(guild, channel, level, False)
                    await channel.send(f"{ctx.author.display_name} has left the RS{level} Queue ({await self.amount(level)}/4)")

    @commands.command(help="type !o or !out, which leaves your current RS Queue")
    async def _out(self, ctx, level=None, external=False):
        if level is None and not external:
            level = self.rs_channel[str(ctx.message.channel)]
        else:
            level = int(level)
        # First check if they are in any RS Queues
        async with sessionmaker() as session:
            results = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars().all()
        if len(results) != 0:  # They were found in an RS Queue
            # remove only one (and delete if they only have one in queue)
            async with sessionmaker() as session:
                current_data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars()
            current_queues = []
            for data in current_data:
                current_queues.append((data.level, data.amount))
            adding_queue = (level, -1)
            current_queues.append(adding_queue)
            D = {}
            for (x, y) in current_queues:
                if x not in D.keys():
                    D[x] = y
                else:
                    D[x] += y
            final_queues = [(x, D[x]) for x in D.keys()]
            for updated_queues in final_queues:
                # Remove only count from the queue they sent the message in
                if updated_queues[0] == level:
                    LOGGER.debug(updated_queues)
                    if updated_queues[1] <= 0:
                        async with sessionmaker.begin() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                LOGGER.debug(f"data.level: {data.level}, {updated_queues[0]}")
                                if(data.level == updated_queues[0]):
                                    pre_amount = data.amount
                                    user = await session.get(Queue, (ctx.author.id, pre_amount, level))
                                    await session.delete(user)
                                    break
                    else:
                        async with sessionmaker.begin() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                if(data.level == updated_queues[0]):
                                    pre_amount = data.amount
                                    user = await session.get(Queue, (ctx.author.id, pre_amount, level))
                                    user.amount = int(updated_queues[1])
                                    LOGGER.debug("updated the queue they were in")
                                    break
            # Print out the new queue
            await self.leaving_queue(ctx, level)
        else:
            await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues")

    @commands.command(help="Use this command (!i or !in) to join a RS Queue")
    async def rs(self, ctx, level=None, length=60, external=False):
        channel_info = await self.right_channel(ctx)
        channel = channel_info[1]
        if ctx.guild.id == clubs_server_id:
            level = self.rs_channel[channel]
        if external or channel_info[0]: 
            if external or await self.right_role(ctx, channel):
                # This is where the fun begins
                if length >= 5 and length <= 11:
                        length = 60
                async with sessionmaker() as session:
                    data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars().all()
                    await session.commit()
                if len(data) == 0:  # They weren't found in the database, add them
                    LOGGER.debug("Adding them to the queue")
                    async with sessionmaker() as session:
                        User_entering_queue = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=1, level=int(level), time=int(time.time()), length=int(length), channel_id=ctx.channel.id, nickname=ctx.author.display_name)
                        session.add(User_entering_queue)
                        await session.commit()
                        # Print out the queue
                        # Check if queue is 4/4
                        if await self.amount(level) == 4:
                            await self.remove_players(ctx, level)
                        else:
                            await self.joining_queue(ctx, level)
                    await session.commit()
                else:
                    async with sessionmaker() as session:
                    # see what queue they are on, and either update their current position or new position
                        current_data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars()
                    # This check is to see if they would be added again to the current queue
                    valid = True
                    for data in current_data:
                        if data.level == level:
                            valid = False
                    if valid:
                        current_queues = []
                        for data in current_data:
                            current_queues.append((data.level, data.amount))
                        adding_queue = (level, 1)
                        current_queues.append(adding_queue)
                        D = {}
                        for (x, y) in current_queues:
                            if x not in D.keys():
                                D[x] = y
                            else:
                                D[x] += y
                        final_queues = [(x, D[x]) for x in D.keys()]
                        for queue in final_queues:
                            if queue[0] == level:
                                # Check if adding amount to the queue would make it 4/4
                                if await self.amount(level) + 1 > 4:
                                    pass
                                else:
                                    # check to see if we need to update their position or add another position
                                    async with sessionmaker() as session:
                                        conditions = and_(Queue.user_id == ctx.author.id, Queue.level == level)
                                        data = (await session.execute(select(Queue).where(conditions))).scalars().all()
                                        await session.commit()
                                    if len(data) == 0:
                                        # They weren't found elsewhere, add them to the new queue
                                        async with sessionmaker() as session:
                                            user = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=queue[1], level=int(level), time=int(time.time()), length=length, channel_id=ctx.channel.id, nickname=ctx.author.display_name)
                                            session.add(user)
                                            await session.commit()
                                    else:
                                        # They were found on another queue, so update their position
                                        for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                            if(data.level == queue[0]):
                                                pre_amount = data.amount
                                                user = await session.get(Queue, (ctx.author.id, pre_amount, level))
                                                user.amount = int(queue[1])
                                                user.time = int(time.time())
                                                user.length = length
                                                await session.commit()
                                                break
                                    if await self.amount(queue[0]) == 4:
                                        await self.remove_players(ctx, level)
                                    else:
                                        await self.joining_queue(ctx, level)
                    else:
                        await ctx.send(f"{ctx.author.mention}, you are already queued for a RS{level}, if you want to add another player to the queue, type +1")
            else:
                await ctx.send(f"{ctx.author.mention}, you aren't RS{level}")

    @commands.command(aliases=["q"], help="(!queue or !q) will show the current RS Queues")
    async def queue(self, ctx, level=None):
        if ctx.guild.id == clubs_server_id:
            level = self.rs_channel[str(ctx.message.channel)]
            await self.print_queue(ctx.guild, ctx.channel, level)
        elif level == None:
            await ctx.send("Please specify an RS Queue to show (`!q #`)")
        else:
            await self.print_queue(ctx.guild, ctx.channel, int(level))

    async def print_queue(self, guild, channel, level, display=True):
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
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
            count = 0
            counting = []
            for person in people:
                counting.append(person.amount)
                count += int(person.amount)
            if count > 0:
                rsmods = []
                user_ids = []
                list_people = []
                for person in (await session.execute(select(Queue).where(Queue.level == level))).scalars():
                    user = await self.bot.fetch_user(person.user_id)
                    user_ids.append(user.id)
                    list_people.append(person.nickname)
                    users_mods = (await session.get(Data, person.user_id))
                    i = 0
                    temp = ""
                    LOGGER.debug(f"Here is users_mods: {users_mods}")
                    if users_mods is not None:
                        for mod in mods:
                            #await ctx.send(f"Mod: {mod} {getattr(users_mods, mod)}")
                            if(getattr(users_mods, mod) == True):
                                temp += " " + (str(extras[mods[i]]))
                            i += 1
                    rsmods.append(temp)
                str_people = ""
                emoji_count = 0
                i = 0
                LOGGER.debug(f"List People {list_people}")
                for person in (await session.execute(select(Queue).where(Queue.level == level))).scalars():
                    for j in range(counting[i]):
                        str_people += str(list(self.emojis)[emoji_count])
                        emoji_count += 1
                    # Server_id, user_id, amount, level
                    str_people += " " + list_people[i] + rsmods[i] + " 🕒 " + str(await self.queue_time(user_ids[i], counting[i], level)) + "m"
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
                queue_embed = discord.Embed(color=role.color, title=f"The Current RS{level} Queue ({await self.amount(level)}/4)", description=str_people)
                await channel.send(embed=queue_embed)
            else:
                if display:
                    await channel.send(f"No RS{level} Queues found, you can start one by typing `!in {level}`")


def setup(bot):
    bot.add_cog(RSQueue(bot))
    LOGGER.debug('RS Queueing loaded')
