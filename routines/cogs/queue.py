import asyncio
from asyncio.locks import Condition
import time
from aiosqlite.core import LOG

import discord
import sqlite3

from datetime import datetime
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect

from bot import LOGGER
from bot import TESTING

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import Queue, Data, Temp
from routines import sessionmaker

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
        self.check_people.start()
        self.current_mods = ["croid", "influence", "nosanc", "notele", "rse", "suppress", "unity", "veng", "barrage", "laser", "dart", "battery", "solo", "solo2"]
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
        self.total_info = []



    async def amount(self, level):
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
            count = 0
            for person in people:
                count += int(person.amount)
            return count

        


    async def queue_time(self, server_id, user_id, amount, level):
        async with sessionmaker.begin() as session:
            person = (await session.get(Queue, (server_id, user_id, amount, level)))
            data =  int((time.time() - int(person.time)) / 60)
            return data



    @tasks.loop(minutes=1.0)
    async def check_people(self):
        # This command will run every minute, and check if someone has been in a queue for over n minutes
        LOGGER.debug("Attempting to check the time")
        print("Checking the time")
        async with sessionmaker.begin() as session:
            results = (await session.execute(select(Queue))).scalars()
            for queue_time in results:
                minutes = int((time.time() - queue_time.time) / 60)
                if minutes == queue_time.length:
                    # Ping the user
                        user = await self.bot.fetch_user(queue_time.user_id)
                        channel = await self.bot.fetch_channel(queue_time.channel_id)
                        message = await channel.send(
                            f"{user.mention}, still in for a RS{queue_time.level}? React ✅ to stay in the queue, and ❌ to leave the queue")
                        await message.add_reaction('✅')
                        await message.add_reaction('❌')
                        # Add their user_id and message_id to database
                        add_temp = Temp(server_id=queue_time.server_id, user_id=queue_time.user_id, message_id=message.id, amount=queue_time.amount, level=queue_time.level)
                        session.add(add_temp)
                elif minutes >= queue_time.length + 5:
                        User_leave = (await session.get(Queue, (queue_time.server_id, queue_time.user_id, queue_time.amount, queue_time.level)))
                        await session.delete(User_leave)
                        await session.commit()
                        user = await self.bot.fetch_user(queue_time.user_id)
                        channel = await self.bot.fetch_channel(queue_time.channel_id)
                        await channel.send(f"{user.display_name} has left RS{queue_time.level} ({await self.amount(queue_time.level)}/4)")
                        conditions = and_(Temp.user_id == queue_time.user_id, Temp.level == queue_time.level)
                        id = (await session.execute(select(Temp).where(conditions))).scalars()
                        for i in id:
                            message = await channel.fetch_message(i.message_id)
                            await message.delete()
                        conditions = and_(Temp.server_id == queue_time.server_id, Temp.user_id == queue_time.user_id, Temp.level == queue_time.level)
                        await session.execute(delete(Temp).where(conditions))
                        await session.commit()





    @commands.command(aliases=["r", "^", "staying", "re", "stayin", "YOUGOTILISTARED"])
    async def refresh(self, ctx):
        async with sessionmaker.begin() as session:
            condtitions = and_(Queue.user_id == ctx.author.id, level=self.rs_channel[str(ctx.message.channel)])
            times = (await session.execute(select(Queue).where(condtitions))).scalars()
            times.first().time = int(time.time())
            rs_level = f'RS{self.rs_channel[str(ctx.message.channel)]}'
            num_players = f'({await self.amount(self.rs_channel[str(ctx.message.channel)])}/4)'
            await ctx.send(f"{ctx.author.mention}, you are requeued for a {rs_level}! {num_players}")

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
    @commands.has_role("mod")
    async def transfer(self, ctx):
        db = sqlite3.connect("rsqueue.sqlite")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM data", ())
        results = cursor.fetchall()
        print(results)
        await ctx.send("Starting to transfer data")
        async with sessionmaker.begin() as session:
            for result in results:
                #self.current_mods = ["croid", "influence", "nosanc", "notele", "rse", "suppress", "unity", "veng", "barrage", "laser", "dart", "battery", "solo", "solo2"]
                new_data = []
                for i in range(1, len(result)):
                    if result[i] == 0:
                        new_data.append(False)
                    else:
                        new_data.append(True)
                rs_mod_data = Data(user_id=int(result[0]), croid=new_data[0], influence=new_data[1], nosanc=new_data[2], notele=new_data[3], rse=new_data[4], suppress=new_data[5], unity=new_data[6], veng=new_data[7], barrage=new_data[8], laser=new_data[9], dart=new_data[10], battery=new_data[11], solo=new_data[12], solo2=new_data[13])
                session.add(rs_mod_data)
        await ctx.send("Finished!")

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
                #await ctx.send(f"The RS{level} queue has been cleared")
                users = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
                for user in users:
                    await session.delete(user)
                message = await ctx.send(f"RS{level} Queue cleared")
                await asyncio.sleep(5)
                await ctx.message.delete()
                await message.delete()

        else:
            async with sessionmaker.begin() as session:
                await session.query(Queue).delete()
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
            right_channel = False
            channel = ""
            for club_channel in self.rs_channel:
                if club_channel == str(ctx.message.channel):
                    right_channel = True
                    channel = club_channel
            if right_channel:
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
                if has_right_role:
                    # check if adding amount would overfill the queue
                    queue_status = await self.amount(self.rs_channel[channel])
                    if int(queue_status) + count > 4:
                        await ctx.send(f"{ctx.author.mention}, adding {count} people to the queue would overfill the queue")
                    else:
                        # check if they are in any other queues
                        async with sessionmaker.begin() as session:
                            data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars().all()
                        if len(data) == 0:  # They weren't found in the database, add them
                            LOGGER.debug("Adding them to the queue")
                            async with sessionmaker.begin() as session:
                                User_entering_queue = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=count, level=self.rs_channel[channel], time=int(time.time()), length=length, channel_id=channel_id)
                                session.add(User_entering_queue)
                            # Check if queue is 4/4
                            if await self.amount(self.rs_channel[channel]) == 4:
                                LOGGER.debug("Queue is 4/4, remove everyone")
                                # Print out the queue
                                async with sessionmaker.begin() as session:
                                    people = await session.execute(select(Queue).where(Queue.level == self.rs_channel[channel])).scalars()
                                    string_people = ""
                                    print_people = []
                                    LOGGER.debug(people)
                                    for person in people:
                                        string_people += (await self.bot.fetch_user(person.user_id)).mention + " "
                                        print_people.append((await ctx.guild.fetch_member(person.user_id)).display_name)
                                    await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                    await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                                    await ctx.send("Meet where?")
                                    # Remove everyone from the queue
                                    queue_people = (await session.execute(select(Queue).where(Queue.level == self.rs_channel[channel]))).scalars()
                                    for person in queue_people:
                                        await session.delete(person)
                                    rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                    formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                    await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                            else:
                                LOGGER.debug("Queue ain't 4/4, print out el queue")
                                await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                count = await self.amount(self.rs_channel[channel])
                                if count == 3:
                                    await ctx.send(f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                                else:
                                    await ctx.send(f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
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
                                        async with sessionmaker.begin() as session:
                                            conditions = and_(Queue.user_id == ctx.author.id, Queue.level == self.rs_channel[channel])
                                            data = (await session.execute(select(Queue).where(conditions))).scalars().all()
                                            if len(data) == 0:
                                                # They weren't found elsewhere, add them to the new queue
                                                LOGGER.debug("I have reached this line")
                                                user = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=queue[1], level=self.rs_channel[channel], time=int(time.time()), length=length, channel_id=channel_id)
                                                session.add(user)
                                            else:
                                                # They were found on another queue, so update their position
                                                for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                                    if(data.level == queue[0]):
                                                        pre_amount = data.amount
                                                        user = await session.get(Queue, (ctx.guild.id, ctx.author.id, pre_amount, self.rs_channel[channel]))
                                                        user.amount = int(queue[1])
                                                        user.time = int(time.time())
                                                        user.length = length
                                                        break
                                        if await self.amount(queue[0]) == 4:
                                            async with sessionmaker.begin() as session:
                                                people = (await session.execute(select(Queue).where(Queue.level == self.rs_channel[channel]))).scalars()
                                                string_people = ""
                                                print_people = []
                                                for person in people:
                                                    string_people += (await self.bot.fetch_user(person.user_id)).mention + " "
                                                    print_people.append((await ctx.guild.fetch_member(person.user_id)).display_name)
                                                await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                                await ctx.send(f"RS{self.rs_channel[channel]} Ready! {string_people}")
                                                await ctx.send("Meet where?")
                                                # Remove everyone from the queue
                                                queue_people = (await session.execute(select(Queue).where(Queue.level == self.rs_channel[channel]))).scalars()
                                                for person in queue_people:
                                                    await session.delete(person)
                                                # Print out the rs log
                                                rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                                formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                                await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                        else:
                                            await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                            count = await self.amount(self.rs_channel[channel])
                                            if count == 3:
                                                await ctx.send(f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                                            else:
                                                await ctx.send(f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
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
                        async with sessionmaker.begin() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                LOGGER.debug(f"data.level: {data.level}, {queue[0]}")
                                if(data.level == queue[0]):
                                    pre_amount = data.amount
                                    LOGGER.debug(f"pre_amount {pre_amount}")
                                    user = await session.get(Queue, (ctx.guild.id, ctx.author.id, pre_amount, self.rs_channel[str(ctx.message.channel)]))
                                    LOGGER.debug(f"User: {user}")
                                    await session.delete(user)
                                    break
                            LOGGER.debug("Removed them from the queue")
                    else:
                        async with sessionmaker.begin() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                if(data.level == queue[0]):
                                    pre_amount = data.amount
                                    user = await session.get(Queue, (ctx.guild.id, ctx.author.id, pre_amount, self.rs_channel[str(ctx.message.channel)]))
                                    user.amount = int(queue[1])
                                    break
                            LOGGER.debug("updated the queue they were in")
            await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)], False)
            await ctx.send(f"{ctx.author.display_name} has left the RS{self.rs_channel[str(ctx.message.channel)]} Queue ({await self.amount(self.rs_channel[str(ctx.message.channel)])}/4)")

    @commands.command(aliases=["o"], help="type !o or !out, which leaves your current RS Queue")
    async def out(self, ctx):
        # First check if they are in any RS Queues
        async with sessionmaker.begin() as session:
            results = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars().all()
        if len(results) != 0:  # They were found in an RS Queue
            # remove only one (and delete if they only have one in queue)
            async with sessionmaker.begin() as session:
                current_data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars()
                current_queues = []
                for data in current_data:
                    current_queues.append((data.level, data.amount))
                adding_queue = (self.rs_channel[str(ctx.message.channel)], -1)
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
                if updated_queues[0] == self.rs_channel[str(ctx.message.channel)]:
                    LOGGER.debug(updated_queues)
                    if updated_queues[1] <= 0:
                        async with sessionmaker.begin() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                LOGGER.debug(f"data.level: {data.level}, {updated_queues[0]}")
                                if(data.level == updated_queues[0]):
                                    pre_amount = data.amount
                                    LOGGER.debug(f"pre_amount {pre_amount}")
                                    user = await session.get(Queue, (ctx.guild.id, ctx.author.id, pre_amount, self.rs_channel[str(ctx.message.channel)]))
                                    LOGGER.debug(f"User: {user}")
                                    await session.delete(user)
                                    break
                            LOGGER.debug("Removed them from the queue")
                    else:
                        async with sessionmaker.begin() as session:
                            for data in (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars():
                                if(data.level == updated_queues[0]):
                                    pre_amount = data.amount
                                    user = await session.get(Queue, (ctx.guild.id, ctx.author.id, pre_amount, self.rs_channel[str(ctx.message.channel)]))
                                    user.amount = int(updated_queues[1])
                                    break
                            LOGGER.debug("updated the queue they were in")
            # Print out the new queue
            await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)], False)
            await ctx.send(f"{ctx.author.display_name} has left the RS{self.rs_channel[str(ctx.message.channel)]} Queue ({await self.amount(self.rs_channel[str(ctx.message.channel)])}/4)")
        else:
            await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues")

    @commands.command(aliases=["in", "i"], help="Use this command (!i or !in) to join a RS Queue")
    async def rs(self, ctx, length=60):
        right_channel = False
        channel = ""
        add_level = self.rs_channel[str(ctx.message.channel)]
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
                channel = club_channel
        if right_channel:
            has_right_role = False
            for role in ctx.author.roles:
                if str(role)[2:].isnumeric():  # Check main rs role
                    if int(str(role)[2:]) >= int(self.rs_channel[channel]):
                        has_right_role = True
                        break
                elif str(role)[2:-12].isnumeric():  # Check 3/4 role
                    if int(str(role)[2:-12]) >= int(self.rs_channel[channel]):
                        has_right_role = True
                        break
                elif str(role)[2:-2].isnumeric():  # Checks silent role (rs# s)
                    if int(str(role)[2:-2]) >= int(self.rs_channel[channel]):
                        has_right_role = True
                        break
                # if(str(role) == f'RS{self.rs_channel[channel]}' or int(str(role)[2:]) > self.rs_channel[channel]):
                #    has_right_role = True
            if has_right_role:
                # This is where the fun begins
                async with sessionmaker.begin() as session:
                    data = (await session.execute(select(Queue).where(Queue.user_id == ctx.author.id))).scalars().all()
                if len(data) == 0:  # They weren't found in the database, add them
                    LOGGER.debug("Adding them to the queue")
                    async with sessionmaker.begin() as session:
                        User_entering_queue = Queue(server_id=ctx.guild.id, user_id=ctx.author.id, amount=1, level=self.rs_channel[channel], time=int(time.time()), length=length, channel_id=ctx.channel.id)
                        session.add(User_entering_queue)
                    # Print out the queue
                    # Check if queue is 4/4
                    if await self.amount(self.rs_channel[channel]) == 4:
                        LOGGER.debug("Queue is 4/4, remove everyone")
                        # Print out the queue
                        async with sessionmaker.begin() as session:
                            people = await session.execute(select(Queue).where(Queue.level == self.rs_channel[channel])).scalars()
                            string_people = ""
                            print_people = []
                            LOGGER.debug(people)
                            for person in people:
                                string_people += (await self.bot.fetch_user(person.user_id)).mention + " "
                                print_people.append((await ctx.guild.fetch_member(person.user_id)).display_name)
                            await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                            await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                            await ctx.send("Meet where?")
                            # Remove everyone from the queue
                            queue_people = (await session.execute(select(Queue).where(Queue.level == self.rs_channel[channel]))).scalars()
                            for person in queue_people:
                                await session.delete(person)
                            rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                            formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                    else:
                        await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                        count = await self.amount(self.rs_channel[channel])
                        if count == 3:
                            await ctx.send(f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                        else:
                            await ctx.send(f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                else:
                    # see what queue they are on, and either update their current position or new position
                    current_queues = await self.sql_command("SELECT level, amount FROM main WHERE user_id=?", [(ctx.author.id)])
                    # Check to see if they are trying to update the position of a queue they are in
                    valid = True
                    for (x, y) in current_queues:
                        if x == self.rs_channel[str(ctx.message.channel)]:
                            valid = False
                    if valid:
                        current_queues.append((self.rs_channel[str(ctx.message.channel)], 1))
                        LOGGER.debug(current_queues)
                        D = {}
                        for (x, y) in current_queues:
                            if x not in D.keys():
                                D[x] = y
                            else:
                                D[x] += y
                        final_queues = [(x, D[x]) for x in D.keys()]
                        LOGGER.debug(final_queues)
                        # append the queue they wanna join to the 
                        for queue in final_queues:
                            if queue[0] == self.rs_channel[channel]:
                                # Check if adding amount to the queue would make it 4/4
                                if await self.amount(self.rs_channel[channel]) + 1 > 4:
                                    pass
                                else:
                                    # check to see if we need to update their position or add another position
                                    if len(await self.sql_command("SELECT amount FROM main WHERE user_id=? AND level=?", (ctx.author.id, self.rs_channel[channel]))) == 0:
                                        # They weren't found elsewhere, add them to the new queue
                                        await self.sql_command("INSERT INTO main(user_id, amount, level, time, length, channel_id) VALUES(?,?,?,?,?,?)", (ctx.author.id, int(queue[1]), self.rs_channel[channel], int(time.time()), length, ctx.channel.id))
                                    else:
                                        # They were found on another queue, so update their position
                                        await self.sql_command(f"UPDATE main SET amount=?, time=?, length=? WHERE user_id=? AND level=?", (int(queue[1]), int(time.time()), length, ctx.author.id, self.rs_channel[channel]))
                                    if await self.amount(queue[0]) == 4:
                                        people = await self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                        string_people = ""
                                        print_people = []
                                        for person in people:
                                            string_people += (await self.bot.fetch_user(person[0])).mention + " "
                                            print_people.append((await ctx.guild.fetch_member(person[0])).display_name)
                                        
                                        await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                                        await ctx.send("Meet where?")
                                        rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                        await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                        # Remove everyone from the queue
                                        asyncio.run(await self.sql_command("DELETE FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])]))
                                        # Print the logs to rs-log
                                        rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                        await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                    else:
                                        await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                        count = await self.amount(self.rs_channel[channel])
                                        if count == 3:
                                            await ctx.send(f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                                        else:
                                            await ctx.send(f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                    else:
                        await ctx.send(f"{ctx.author.mention}, you are already queued for a RS{self.rs_channel[channel]}, if you want to add another player to the queue, type +1")
            else:
                await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")

    @commands.command(aliases=["q"], help="(!queue or !q) will show the current RS Queues")
    async def queue(self, ctx):
        await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])

    async def print_queue(self, ctx, level, display=True):
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
            'solo2': discord.utils.get(self.bot.emojis, name='solo2')
        }
        queue_embed = discord.Embed(color=discord.Color.red())
        #people = await self.sql_command("SELECT amount FROM main WHERE level=?", [level])
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == level))).scalars()
            count = 0
            counting = []
            for person in people:
                counting.append(person.amount)
                count += int(person.amount)
            if count > 0:
                #people_printing = await self.sql_command("SELECT user_id FROM main WHERE level=?", [level])
                list_people = []
                user_ids = []
                rsmods = []
                for person in (await session.execute(select(Queue).where(Queue.level == level))).scalars():
                    list_people.append((await ctx.guild.fetch_member(person.user_id)).display_name)
                    user_ids.append((await ctx.guild.fetch_member(person.user_id)).id)
                    #result = await self.sql_command("SELECT * FROM data WHERE user_id=?", [(await ctx.guild.fetch_member(people[0])).id])
                    users_mods = (await session.get(Data, person.user_id))
                    i = 0
                    temp = ""
                    for mod in self.current_mods:
                        #await ctx.send(f"Mod: {mod} {getattr(users_mods, mod)}")
                        if(getattr(users_mods, mod) == True):
                            temp += " " + (str(extras[self.current_mods[i]]))
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
                    str_people += " " + list_people[i] + rsmods[i] + " 🕒 " + str(await self.queue_time(ctx.guild.id, user_ids[i], counting[i], self.rs_channel[str(ctx.message.channel)])) + "m"
                    str_people += "\n"
                    i += 1
                queue_embed.add_field(
                    name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({await self.amount(self.rs_channel[str(ctx.message.channel)])}/4)",
                    value=str_people, inline=False)
                await ctx.send(embed=queue_embed)
            else:
                if display:
                    await ctx.send(f"No RS{self.rs_channel[str(ctx.message.channel)]} Queues found, you can start one by typing +1")


def setup(bot):
    bot.add_cog(RSQueue(bot))
    LOGGER.debug('RS Queueing loaded')
