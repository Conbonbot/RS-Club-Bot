import asyncio
import time

import discord
import sqlite3

from datetime import datetime
from discord.ext import commands, tasks

from bot import LOGGER
from bot import TESTING

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


# TODO: migrate to a helper lib that can be used across the entire project.



class RSQueue(commands.Cog, name='Queue'):

    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.check_people.start()
        self.current_mods = ["croid", "influence", "nosanc", "notele", "rse", "suppress", "unity", "veng", "barrage"]
        self.rs_channel = {
            "rs5-club": 5,
            "rs6-club": 6,
            "rs7-club": 7,
            "rs8-club": 8,
            "rs9-club": 9,
            "rs10-club": 10,
            "rs11-club": 11,
        }
        self.rs_ping = RS_GROUPS['rs_ping']
        self.rs_ping_1more = RS_GROUPS['rs_ping_1more']
        self.emojis = {
            "1️⃣": 1,
            "2️⃣": 2,
            "3️⃣": 3,
            "4️⃣": 4
        }


    def sql_command(self, sql, val, data='rsqueue.sqlite'):
        db = sqlite3.connect(data)
        cursor = db.cursor()
        cursor.execute(sql, val)
        results = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return results


    def amount(self, level):
        print(level)
        people = self.sql_command("SELECT amount FROM main WHERE level=?", [(level)])
        count = 0
        counting = []
        for person in people:
            counting.append(person[0])
            count += int(person[0])
        return count


    def queue_time(self, user_id, level):
        LOGGER.debug(f"Running the time command. User ID: {user_id}, level: {level}")
        db = sqlite3.connect("rsqueue.sqlite")
        cursor = db.cursor()
        sql = "SELECT time FROM main WHERE user_id=? AND level=?"
        val = (user_id, level)
        cursor.execute(sql, val)
        person = cursor.fetchone()
        db.commit()
        cursor.close()
        db.close()
        LOGGER.debug("Results from the database: ", person)
        for p in person:
            return int((time.time() - int(p)) / 60)

    def cog_unload(self):
        self.check_people.cancel()

    @tasks.loop(minutes=1.0)
    async def check_people(self):
        # This command will run every minute, and check if someone has been in a queue for over n minutes
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT time, length, user_id, level, channel_id FROM main")
        times = cursor.fetchall()
        for queue_time in times:
            # LOGGER.debug(queue_time)
            # LOGGER.debug(int(time.time()), queue_time[0], int(time.time())-queue_time[0], int((time.time()-queue_time[0])/60))
            minutes = int((time.time() - queue_time[0]) / 60)
            if minutes == queue_time[1]:
                # Ping the user
                user = await self.bot.fetch_user(queue_time[2])
                channel = await self.bot.fetch_channel(queue_time[4])
                message = await channel.send(
                    f"{user.mention}, still in for a RS{queue_time[3]}? React ✅ to stay in the queue, and ❌ to leave the queue")
                await message.add_reaction('✅')
                await message.add_reaction('❌')
                # Add their user_id and message_id to database
                sql = "INSERT INTO temp(user_id, message_id, level) VALUES(?,?,?)"
                val = (user.id, message.id, queue_time[3])
                cursor.execute(sql, val)
                pass
            elif minutes >= queue_time[1] + 5:
                self.sql_command("DELETE FROM main WHERE user_id=? AND level=?", (queue_time[2], queue_time[3]))
                user = await self.bot.fetch_user(queue_time[2])
                channel = await self.bot.fetch_channel(queue_time[4])
                await channel.send(f"{user.display_name} has left RS{queue_time[3]} ({self.amount(queue_time[3])}/4)")
                idx = self.sql_command( "SELECT message_id FROM temp WHERE user_id=? AND level=?", (queue_time[2], queue_time[3]))
                LOGGER.debug(queue_time[4], idx[0][0])
                message = await channel.fetch_message(idx[0][0])
                await message.delete()
                self.sql_command("DELETE FROM temp WHERE user_id=? AND level=?", (queue_time[2], queue_time[3]))
                pass
        db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=["r", "^", "staying", "re", "stayin", "YOUGOTILISTARED"])
    async def refresh(self, ctx):
        self.sql_command( "UPDATE main SET time=? WHERE user_id=? AND level=?", (int(time.time()), ctx.author.id, self.rs_channel[str(ctx.message.channel)]))
        rs_level = f'RS{self.rs_channel[str(ctx.message.channel)]}'
        num_players = f'({self.amount(self.rs_channel[str(ctx.message.channel)])}/4)'
        await ctx.send(f"{ctx.author.mention}, you are requeued for a {rs_level}! {num_players}")

    @commands.command(pass_context=True)
    async def corp(self, ctx, corp):
        member = await ctx.guild.fetch_member(ctx.author.id)
        LOGGER.debug(member.display_name)
        if member.display_name.startswith("["):
            name = member.display_name[member.display_name.find("]") + 2:]
        else:
            name = member.display_name
        nick = f"[{corp}] " + name
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
            self.sql_command("DELETE FROM main WHERE level=?", [(level)])
            await ctx.send(f"The RS{level} queue has been cleared")
        else:
            db = sqlite3.connect('rsqueue.sqlite')
            cursor = db.cursor()
            cursor.execute("DELETE FROM main")
            db.commit()
            cursor.close()
            db.close()
            await ctx.send("All Queues have been cleared")

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
                    queue_status = self.amount(self.rs_channel[channel])
                    if int(queue_status) + count > 4:
                        await ctx.send(
                            f"{ctx.author.mention}, adding {count} people to the queue would overfill the queue")
                    else:
                        # check if they are in any other queues
                        database_check = self.sql_command("SELECT user_id FROM main WHERE user_id=?", [(ctx.author.id)])
                        LOGGER.debug(database_check)
                        if len(database_check) == 0:  # They weren't found in the database, add them
                            LOGGER.debug("Adding them to the queue")
                            self.sql_command("INSERT INTO main(user_id, amount, level, time, length, channel_id) VALUES(?,?,?,?,?,?)", (ctx.author.id, count, self.rs_channel[channel], int(time.time()), length, channel_id))
                            # Check if queue is 4/4
                            if self.amount(self.rs_channel[channel]) == 4:
                                LOGGER.debug("Queue is 4/4, remove everyone")
                                # Print out the queue
                                people = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                string_people = ""
                                print_people = []
                                LOGGER.debug(people)
                                for person in people:
                                    string_people += (await self.bot.fetch_user(person[0])).mention + " "
                                    print_people.append((await ctx.guild.fetch_member(person[0])).display_name)
                                await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                                await ctx.send("Meet where?")
                                rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                await rs_log_channel.send(
                                    f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                # Remove everyone from the queue
                                self.sql_command("DELETE FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                            else:
                                LOGGER.debug("Queue ain't 4/4, print out el queue")
                                await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                count = self.amount(self.rs_channel[channel])
                                if count == 3:
                                    await ctx.send(f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                                else:
                                    await ctx.send(f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                        else:
                            LOGGER.debug("They were found on multiple queues, find all queues")
                            # see what queue they are on, and either update their current position or new position
                            current_queues = self.sql_command("SELECT level, amount FROM main WHERE user_id=?", [(ctx.author.id)])
                            current_queues.append((self.rs_channel[str(ctx.message.channel)], count))
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
                                    if self.amount(self.rs_channel[channel]) + count > 4:
                                        pass
                                    else:
                                        # check to see if we need to update their position or add another position
                                        if (len(self.sql_command("SELECT amount FROM main WHERE user_id=? AND level=?", (ctx.author.id, self.rs_channel[channel]))) == 0):
                                            # They weren't found elsewhere, add them to the new queue
                                            self.sql_command("INSERT INTO main(user_id, amount, level, time, length, channel_id) VALUES(?,?,?,?,?,?)", (ctx.author.id, int(queue[1]), self.rs_channel[channel],int(time.time()), length, channel_id))
                                        else:
                                            # They were found on another queue, so update their position
                                            self.sql_command(f"UPDATE main SET amount=?, time=?, length=? WHERE user_id=? AND level=?", (int(queue[1]), int(time.time()), length, ctx.author.id, self.rs_channel[channel]))
                                        if self.amount(queue[0]) == 4:
                                            people = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                            string_people = ""
                                            print_people = []
                                            for person in people:
                                                string_people += (await self.bot.fetch_user(person[0])).mention + " "
                                                print_people.append(
                                                    (await ctx.guild.fetch_member(person[0])).display_name)
                                            await ctx.send(
                                                f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                                            await ctx.send("Meet where?")
                                            rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                            formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                            await rs_log_channel.send(
                                                f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                            # Remove everyone from the queue
                                            self.self.sql_command("DELETE FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                        else:
                                            await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                            count = self.amount(self.rs_channel[channel])
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
                await msg.delete
        elif prefix == "-":
            LOGGER.debug("- command run, attempting to remove them from queue")
            result = self.sql_command("SELECT amount FROM main WHERE user_id=? AND level=?", (ctx.author.id, self.rs_channel[str(ctx.message.channel)]))
            LOGGER.debug(result)
            if len(result) == 0:  # Didn't find them in any queues
                await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues at the moment")
            else:  # Remove count of them from the queue
                # Get the level and amount data
                # Check if removing count would remove more than they are in
                current_queues = self.sql_command("SELECT level, amount FROM main WHERE user_id=?", [(ctx.author.id)])
                # would return [(11, 2), (10, 3)] for example
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
                            self.sql_command("DELETE FROM main WHERE user_id=? AND level=?", (ctx.author.id, int(queue[0])))
                            LOGGER.debug("Removed them from the queue")
                        else:
                            self.sql_command("UPDATE main SET amount=? WHERE user_id=? AND level=?", (int(queue[1]), ctx.author.id, self.rs_channel[str(ctx.message.channel)]))
                            LOGGER.debug("updated the queue they were in")
                people = self.sql_command("SELECT amount FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                count = 0
                counting = []
                for person in people:
                    counting.append(person[0])
                    count += int(person[0])
                await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)], False)
                await ctx.send(
                    f"{ctx.author.display_name} has left the RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)")

    @commands.command(aliases=["o"], help="type !o or !out, which leaves your current RS Queue")
    async def out(self, ctx):
        # First check if they are in any RS Queues
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        sql = "SELECT user_id FROM main WHERE user_id=?"
        cursor.execute(sql, [ctx.author.id])
        results = cursor.fetchall()
        if len(results) != 0:  # They were found in an RS Queue
            # remove only one (and delete if they only have one in queue)
            current_queues = self.sql_command("SELECT level, amount FROM main WHERE user_id=?", [(ctx.author.id)])
            # would return [(11, 2), (10, 3)] for example
            adding_queue = (self.rs_channel[str(ctx.message.channel)], -1)
            current_queues.append(adding_queue)
            updated_queues = {}
            for (x, y) in current_queues:
                if x not in updated_queues.keys():
                    updated_queues[x] = y
                else:
                    updated_queues[x] += y
            final_queues = [(x, updated_queues[x]) for x in updated_queues.keys()]
            for updated_queues in final_queues:
                # Remove only count from the queue they sent the message in
                if updated_queues[0] == self.rs_channel[str(ctx.message.channel)]:
                    LOGGER.debug(updated_queues)
                    if updated_queues[1] <= 0:
                        self.sql_command("DELETE FROM main WHERE user_id=? AND level=?", (ctx.author.id, int(updated_queues[0])))
                        LOGGER.debug("Removed them from the queue")
                    else:
                        self.sql_command("UPDATE main SET amount=? WHERE user_id=? AND level=?",(int(updated_queues[1]), ctx.author.id, self.rs_channel[str(ctx.message.channel)]))
                        LOGGER.debug("updated the queue they were in")
            # Print out the new queue
            await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)], False)
            await ctx.send(
                f"{ctx.author.display_name} has left the RS{self.rs_channel[str(ctx.message.channel)]} Queue ({self.amount(self.rs_channel[str(ctx.message.channel)])}/4)")
        else:
            await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues")
        db.commit()
        cursor.close()
        db.close()

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
                db = sqlite3.connect('rsqueue.sqlite')
                cursor = db.cursor()
                # check if they are in any other queues
                sql = "SELECT user_id FROM main WHERE user_id=?"
                cursor.execute(sql, [ctx.author.id])
                if len(cursor.fetchall()) == 0:  # They weren't found in the database, add them
                    self.sql_command( "INSERT INTO main(user_id, amount, level, time, length, channel_id) VALUES(?,?,?,?,?,?)", (ctx.author.id, 1, add_level, int(time.time()), length, ctx.channel.id))
                    # Print out the queue
                    # Check if queue is 4/4
                    people = self.sql_command("SELECT amount FROM main WHERE level=?", [(add_level)])
                    count = 0
                    counting = []
                    for person in people:
                        counting.append(person[0])
                        count += int(person[0])
                    if count == 4:
                        # Print out the queue
                        sql = "SELECT user_id FROM main WHERE level=?"
                        cursor.execute(sql, [add_level])
                        people = cursor.fetchall()
                        string_people = ""
                        print_people = []
                        for person in people:
                            string_people += (await self.bot.fetch_user(person[0])).mention + " "
                            print_people.append((await ctx.guild.fetch_member(person[0])).display_name)
                        await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                        await ctx.send("Meet where?")
                        rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                        await rs_log_channel.send(
                            f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                        # Remove everyone from the queue
                        sql = "DELETE FROM main WHERE level=?"
                        cursor.execute(sql, [add_level])
                    else:
                        await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                        count = self.amount(self.rs_channel[channel])
                        if count == 3:
                            await ctx.send(
                                f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                        else:
                            await ctx.send(
                                f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                    db.commit()
                    cursor.close()
                    db.close()
                else:
                    # see what queue they are on, and either update their current position or new position
                    current_queues = self.sql_command("SELECT level, amount FROM main WHERE user_id=?", [(ctx.author.id)])
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
                                if self.amount(self.rs_channel[channel]) + 1 > 4:
                                    pass
                                else:
                                    # check to see if we need to update their position or add another position
                                    if len(self.sql_command("SELECT amount FROM main WHERE user_id=? AND level=?", (ctx.author.id, self.rs_channel[channel]))) == 0:
                                        # They weren't found elsewhere, add them to the new queue
                                        self.sql_command("INSERT INTO main(user_id, amount, level, time, length, channel_id) VALUES(?,?,?,?,?,?)", (ctx.author.id, int(queue[1]), self.rs_channel[channel], int(time.time()), length, ctx.channel.id))
                                    else:
                                        # They were found on another queue, so update their position
                                        self.sql_command(f"UPDATE main SET amount=?, time=?, length=? WHERE user_id=? AND level=?", (int(queue[1]), int(time.time()), length, ctx.author.id, self.rs_channel[channel]))
                                    if self.amount(queue[0]) == 4:
                                        people = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                        string_people = ""
                                        print_people = []
                                        for person in people:
                                            string_people += (await self.bot.fetch_user(person[0])).mention + " "
                                            print_people.append((await ctx.guild.fetch_member(person[0])).display_name)
                                        await ctx.send(
                                            f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                                        await ctx.send("Meet where?")
                                        rs_log_channel = await self.bot.fetch_channel(805228742678806599)
                                        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                        await rs_log_channel.send(
                                            f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                        # Remove everyone from the queue
                                        self.sql_command("DELETE FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                    else:
                                        await self.print_queue(ctx, self.rs_channel[str(ctx.message.channel)])
                                        count = self.amount(self.rs_channel[channel])
                                        if count == 3:
                                            await ctx.send(
                                                f"{ctx.author.mention} joined {self.rs_ping_1more[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                                        else:
                                            await ctx.send(
                                                f"{ctx.author.mention} joined {self.rs_ping[f'RS{self.rs_channel[channel]}']} ({count}/4)")
                    else:
                        await ctx.send(
                            f"{ctx.author.mention}, you are already queued for a RS{self.rs_channel[channel]}, if you want to add another player to the queue, type +1")
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
        queue_embed = discord.Embed(
            color=discord.Color.red()
        )
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        sql = "SELECT amount FROM main WHERE level=?"
        cursor.execute(sql, [level])
        people = cursor.fetchall()
        count = 0
        counting = []
        for person in people:
            counting.append(person[0])
            count += int(person[0])
        if count > 0:
            sql = "SELECT user_id FROM main WHERE level=?"
            cursor.execute(sql, [level])
            people_printing = cursor.fetchall()
            list_people = []
            user_ids = []
            rsmods = []
            for people in people_printing:
                list_people.append((await ctx.guild.fetch_member(people[0])).display_name)
                user_ids.append((await ctx.guild.fetch_member(people[0])).id)
                result = self.sql_command("SELECT * FROM data WHERE user_id=?", [(await ctx.guild.fetch_member(people[0])).id])
                stuff = cursor.execute('select * from data')
                names = [description[0] for description in stuff.description]
                LOGGER.debug(names)
                names = names[1:]
                temp = ""
                if len(result) != 0:
                    for i in range(1, len(result[0])):
                        if result[0][i] == 1:
                            temp += " " + (str(extras[names[i - 1]]))
                rsmods.append(temp)
            str_people = ""
            emoji_count = 0
            for i in range(len(people_printing)):
                for j in range(counting[i]):
                    str_people += str(list(self.emojis)[emoji_count])
                    emoji_count += 1
                str_people += " " + list_people[i] + rsmods[i] + " 🕒 " + str(
                    self.queue_time(user_ids[i], self.rs_channel[str(ctx.message.channel)])) + "m"
                str_people += "\n"
            queue_embed.add_field(
                name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({self.amount(self.rs_channel[str(ctx.message.channel)])}/4)",
                value=str_people, inline=False)
            await ctx.send(embed=queue_embed)
        else:
            if display:
                await ctx.send(
                    f"No RS{self.rs_channel[str(ctx.message.channel)]} Queues found, you can start one by typing +1")
        db.commit()
        cursor.close()
        db.close()


def setup(bot):
    bot.add_cog(RSQueue(bot))
    LOGGER.debug('RS Queueing loaded')
