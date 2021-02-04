import os
import random
from sqlite3.dbapi2 import DatabaseError
from typing import final
from discord import channel
from dotenv import load_dotenv
import sqlite3
import datetime
from discord.ext import commands, tasks
import discord
import asyncio
import sys
import requests
import numpy as np
from discord.utils import get
from datetime import datetime
import time

class RSQueue(commands.Cog, name='Queue'):

    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.printer.start()
        self.rs_channel = {
            "rs5-club" : 5, 
            "rs6-club" : 6,
            "rs7-club" : 7,
            "rs8-club" : 8,
            "rs9-club" : 9,
            "rs10-club" : 10,
            "rs11-club" : 11
        }
        self.rs_ping = {
            "RS5" : "806018027383422998",
            "RS6" : "806018102797402122",
            "RS7" : "806018133835513876",
            "RS8" : "806018135106519040",
            "RS9" : "806018147487711313",
            "RS10" : "806018150256082984",
            "RS11" : "806261078295183400"
        }
        self.rs_ping_1more = {
            "RS5" : "806018333517938688",
            "RS6" : "806018337804910592",
            "RS7" : "806018340203397140",
            "RS8" : "806018343696990208",
            "RS9" : "806018346269016084",
            "RS10" : "806018349183139890",
            "RS11" : "806261118158372936"
        }
        self.emojis = {
            "1️⃣" : 1,
            "2️⃣" : 2,
            "3️⃣" : 3,
            "4️⃣" : 4
        }

    

    # This executes an sql command to a database
    def sql_command(self, sql, val, data='rsqueue.sqlite'):
        db = sqlite3.connect(data)
        cursor = db.cursor()
        cursor.execute(sql, val)
        results = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return results

    # This returns how many people are in a current RS queue
    def amount(self, level):
        people = self.sql_command("SELECT amount FROM main WHERE level=?", [(level)])
        count = 0
        counting = []
        for person in people:
            counting.append(person[0])
            count += int(person[0])
        return count

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=1.0)
    async def printer(self):
        self.index += 1

    @commands.command()
    async def clear(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)

    @commands.command(name='1', help="Type +1/-1, which will add you/remove you to/from a RS Queue")
    async def _one(self, ctx):
        message = list(ctx.message.content)
        await self.everything(ctx, message[0], message[1])

    @commands.command(name='2', help="Type +2/-2, which will add you/remove you and another person to/from a RS Queue")
    async def _two(self, ctx):
        message = list(ctx.message.content)
        await self.everything(ctx, message[0], message[1])
    
    @commands.command(name='3', help="Type +3/-4, which will add you/remove you and 2 other people to/from a RS Queue")
    async def _three(self, ctx):
        message = list(ctx.message.content)
        await self.everything(ctx, message[0], message[1])

    async def everything(self, ctx, prefix, count):
        count = int(count)
        if prefix == "+":
            right_channel = False
            channel = ""
            for club_channel in self.rs_channel:
                if(club_channel == str(ctx.message.channel)):
                    right_channel = True
                    channel = club_channel
            if(right_channel):
                has_right_role = False
                for role in ctx.author.roles:
                    if(str(role)[2:].isnumeric()):
                        if(int(str(role)[2:]) >= int(self.rs_channel[channel])):
                            has_right_role = True
                            break
                    #if(str(role) == f'RS{self.rs_channel[channel]}' or int(str(role)[2:]) > self.rs_channel[channel]):
                    #    has_right_role = True
                if(has_right_role):
                    # check if adding amount would overfill the queue
                    queue_status = self.amount(self.rs_channel[channel])
                    if(int(queue_status) + count > 4):
                        await ctx.send(f"{ctx.author.mention}, adding {count} people to the queue would overfill the queue")                
                    # check if they are in any other queues
                    database_check = self.sql_command("SELECT user_id FROM main WHERE user_id=?", [(ctx.author.id)])
                    print(database_check)
                    if(len(database_check) == 0): # They weren't found in the database, add them
                        self.sql_command("INSERT INTO main(user_id, amount, level) VALUES(?,?,?)", (ctx.author.id, count, self.rs_channel[channel]))
                        # Check if queue is 4/4
                        if(self.amount(self.rs_channel[channel]) == 4):
                            # Print out the queue
                            people = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                            string_people = ""
                            print_people = []
                            for person in people:
                                string_people += (await self.bot.fetch_user(person[0])).mention + " "
                                print_people.append((await self.bot.fetch_user(person[0])).display_name)
                            await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                            await ctx.send("Meet where?")
                            rs_log_channel = await self.bot.fetch_channel(806370539148541952)
                            formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                            # Remove everyone from the queue
                            self.sql_command("DELETE FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                        else:
                            queue_embed = discord.Embed(
                                color = discord.Color.red()
                            )
                            people = self.sql_command("SELECT amount FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                            count = 0
                            counting = []
                            for person in people:
                                counting.append(person[0])
                                count += int(person[0])
                            people_printing = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                            list_people = []
                            for people in people_printing:
                                print((await self.bot.fetch_user(people[0])).display_name)
                                list_people.append((await self.bot.fetch_user(people[0])).display_name)
                            str_people = ""
                            emoji_count = 0
                            for i in range(len(people_printing)):
                                for j in range(counting[i]):
                                    str_people += str(list(self.emojis)[emoji_count])
                                    emoji_count += 1
                                str_people += " " + list_people[i]
                                str_people += "\n"
                            queue_embed.add_field(name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)", value=str_people, inline=False)
                            await ctx.send(embed=queue_embed)
                            await ctx.send(f"{ctx.author.mention} joined RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
                    else:
                        # see what queue they are on, and either update their current position or new position
                        current_queues = self.sql_command("SELECT level, amount FROM main WHERE user_id=?", [(ctx.author.id)])
                        current_queues.append((self.rs_channel[str(ctx.message.channel)],count))
                        print(current_queues)
                        D = {}
                        for (x, y) in current_queues:
                            if x not in D.keys():
                                D[x] = y
                            else:
                                D[x] += y
                        final_queues = [(x, D[x]) for x in D.keys()]
                        print(final_queues)
                        # append the queue they wanna join to the 
                        for queue in final_queues:
                            if(queue[0] == self.rs_channel[channel]):
                                # Check if adding amount to the queue would make it 4/4
                                if(self.amount(self.rs_channel[channel])+count > 4):
                                    pass
                                else:
                                    # check to see if we need to update their position or add another position
                                    if(len(self.sql_command("SELECT amount FROM main WHERE user_id=? AND level=?", (ctx.author.id, self.rs_channel[channel]))) == 0):
                                        # They weren't found elsewhere, add them to the new queue
                                        self.sql_command("INSERT INTO main(user_id, amount, level) VALUES(?,?,?)", (ctx.author.id, int(queue[1]),self.rs_channel[channel]))
                                    else:
                                        # They were found on another queue, so update their position
                                        self.sql_command(f"UPDATE main SET amount=? WHERE user_id=? AND level=?", (int(queue[1]), ctx.author.id, self.rs_channel[channel]))
                                    if(self.amount(queue[0]) == 4):
                                        people = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                        string_people = ""
                                        print_people = []
                                        for person in people:
                                            string_people += (await self.bot.fetch_user(person[0])).mention + " "
                                            print_people.append((await self.bot.fetch_user(person[0])).display_name)
                                        await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                                        await ctx.send("Meet where?")
                                        rs_log_channel = await self.bot.fetch_channel(806370539148541952)
                                        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                        await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                                        # Remove everyone from the queue
                                        self.sql_command("DELETE FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])                                    
                                    else:
                                        queue_embed = discord.Embed(
                                            color = discord.Color.red()
                                        )
                                        people = self.sql_command("SELECT amount FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                        count = 0
                                        counting = []
                                        for person in people:
                                            counting.append(person[0])
                                            count += int(person[0])
                                        people_printing = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                                        list_people = []
                                        for people in people_printing:
                                            print((await self.bot.fetch_user(people[0])).display_name)
                                            list_people.append((await self.bot.fetch_user(people[0])).display_name)
                                        str_people = ""
                                        emoji_count = 0
                                        for i in range(len(people_printing)):
                                            for j in range(counting[i]):
                                                str_people += str(list(self.emojis)[emoji_count])
                                                emoji_count += 1
                                            str_people += " " + list_people[i]
                                            str_people += "\n"
                                        queue_embed.add_field(name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)", value=str_people, inline=False)
                                        await ctx.send(embed=queue_embed)
                                        await ctx.send(f"{ctx.author.mention} joined RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
                else:
                    await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")
            else:
                msg = await ctx.send("Command not run in an RS Channel")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await msg.delete
        elif prefix == "-":
            result = self.sql_command("SELECT amount FROM main WHERE user_id=? AND level=?", (ctx.author.id, self.rs_channel[str(ctx.message.channel)]))
            print(result)
            if(len(result) == 0): # Didn't find them in any queues
                await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues at the moment")
            else: # Remove count of them from the queue 
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
                print(final_queues)
                # TODO: check if any of the queue[1] is less than or equal to 0,
                #       if it is, remove the queue as a whole, otherwise update the queue
                for queue in final_queues:
                    # Remove only count from the queue they sent the message in
                    if (queue[0] == self.rs_channel[str(ctx.message.channel)]):
                        print(queue)
                        if(queue[1] <= 0):
                            self.sql_command("DELETE FROM main WHERE user_id=? AND level=?", (ctx.author.id, int(queue[0])))
                        else:
                            self.sql_command("UPDATE main SET amount=? WHERE user_id=? AND level=?", (int(queue[1]), ctx.author.id, self.rs_channel[str(ctx.message.channel)]))
                people = self.sql_command("SELECT amount FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                count = 0
                counting = []
                for person in people:
                    counting.append(person[0])
                    count += int(person[0])
                queue_embed = discord.Embed(
                    color = discord.Color.red()
                )
                people = self.sql_command("SELECT amount FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                count = 0
                counting = []
                for person in people:
                    counting.append(person[0])
                    count += int(person[0])
                if(count > 0):
                    people_printing = self.sql_command("SELECT user_id FROM main WHERE level=?", [(self.rs_channel[str(ctx.message.channel)])])
                    list_people = []
                    for people in people_printing:
                        print((await self.bot.fetch_user(people[0])).display_name)
                        list_people.append((await self.bot.fetch_user(people[0])).display_name)
                    str_people = ""
                    emoji_count = 0
                    for i in range(len(people_printing)):
                        for j in range(counting[i]):
                            str_people += str(list(self.emojis)[emoji_count])
                            emoji_count += 1
                        str_people += " " + list_people[i]
                        str_people += "\n"
                    queue_embed.add_field(name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)", value=str_people, inline=False)
                    await ctx.send(embed=queue_embed)
                await ctx.send(f"{ctx.author.display_name} has left the RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)")
        

    @commands.command(aliases=["o"], help="type !o or !out, which leaves your current RS Queue")
    async def out(self, ctx):
        # First check if they are in any RS Queues
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        sql = "SELECT user_id FROM main WHERE user_id=?"
        cursor.execute(sql, [(ctx.author.id)])
        results = cursor.fetchall()
        if(len(results) != 0): # They were found in an RS QUeue
            sql = "DELETE FROM main WHERE user_id=?"
            cursor.execute(sql, [(ctx.author.id)])
            # Print out the new queue
            sql = "SELECT amount FROM main WHERE level=?"
            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
            people = cursor.fetchall()
            try:
                count = 0
                for c in people:
                    count += int(c[0])
            except:
                count = 0
            await ctx.send(f"{ctx.author.mention} has left RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
        else:
            await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues")
        db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=["in", "rs"], help="Use this command (!i or !in) to join a RS Queue")
    async def i(self, ctx, level=None):
        right_channel = False
        channel = ""
        add_level = self.rs_channel[str(ctx.message.channel)]
        if(level is None):
            for club_channel in self.rs_channel:
                if(club_channel == str(ctx.message.channel)):
                    right_channel = True
                    channel = club_channel
        else:
            add_level = level
        if(right_channel):
            has_right_role = False
            for role in ctx.author.roles:
                if(str(role)[2:].isnumeric()):
                    if(int(str(role)[2:]) >= int(self.rs_channel[channel])):
                        has_right_role = True
                        break
                #if(str(role) == f'RS{self.rs_channel[channel]}' or int(str(role)[2:]) > self.rs_channel[channel]):
                #    has_right_role = True
            if(has_right_role):
                # This is where the fun begins
                db = sqlite3.connect('rsqueue.sqlite')
                cursor = db.cursor()
                # check if they are in any other queues
                sql = "SELECT user_id FROM main WHERE user_id=?" 
                cursor.execute(sql, [(ctx.author.id)])
                if(len(cursor.fetchall()) == 0): # They weren't found in the database, add them
                    self.sql_command("INSERT INTO main(user_id, amount, level) VALUES(?,?,?)", (ctx.author.id, 1, add_level))
                    # Print out the queue
                    # Check if queue is 4/4
                    people = self.sql_command("SELECT amount FROM main WHERE level=?", [(add_level)])
                    count = 0
                    counting = []
                    for person in people:
                        counting.append(person[0])
                        count += int(person[0])
                    if(count == 4):
                        # Print out the queue
                        sql = "SELECT user_id FROM main WHERE level=?"
                        cursor.execute(sql, [(add_level)])
                        people = cursor.fetchall()
                        string_people = ""
                        print_people = []
                        for person in people:
                            string_people += (await self.bot.fetch_user(person[0])).mention + " "
                            print_people.append((await self.bot.fetch_user(person[0])).display_name)
                        await ctx.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Ready! {string_people}")
                        await ctx.send("Meet where?")
                        rs_log_channel = await self.bot.fetch_channel(806370539148541952)
                        formated_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                        await rs_log_channel.send(f"RS{self.rs_channel[str(ctx.message.channel)]} Started at {formated_date} PST \nUsers: {', '.join(print_people)}")
                        # Remove everyone from the queue
                        sql = "DELETE FROM main WHERE level=?"
                        cursor.execute(sql, [(add_level)])
                    else:
                        queue_embed = discord.Embed(
                            color = discord.Color.red()
                        )
                        sql = "SELECT amount FROM main WHERE level=?"
                        cursor.execute(sql, [(add_level)])
                        people = cursor.fetchall()
                        count = 0
                        counting = []
                        for person in people:
                            counting.append(person[0])
                            count += int(person[0])
                        sql = "SELECT user_id FROM main WHERE level=?"
                        cursor.execute(sql, [(add_level)])
                        people_printing = cursor.fetchall()
                        list_people = []
                        for people in people_printing:
                            print((await self.bot.fetch_user(people[0])).display_name)
                            list_people.append((await self.bot.fetch_user(people[0])).display_name)
                        str_people = ""
                        emoji_count = 0
                        for i in range(len(people_printing)):
                            for j in range(counting[i]):
                                str_people += str(list(self.emojis)[emoji_count])
                                emoji_count += 1
                            str_people += " " + list_people[i]
                            str_people += "\n"
                        queue_embed.add_field(name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)", value=str_people, inline=False)
                        await ctx.send(embed=queue_embed)
                        await ctx.send(f"{ctx.author.mention} joined RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
                    db.commit()
                    cursor.close()
                    db.close()
                else:
                    await ctx.send(f"{ctx.author.mention}, you are already in a RS Queue")
            else:
                await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")

    @commands.command(aliases=["q"], help="(!queue or !q) will show the current RS Queues")
    async def queue(self, ctx):
        queue_embed = discord.Embed(
            color = discord.Color.red()
        )
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        sql = "SELECT amount FROM main WHERE level=?"
        cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
        people = cursor.fetchall()
        count = 0
        counting = []
        for person in people:
            counting.append(person[0])
            count += int(person[0])
        if(count > 0):
            sql = "SELECT user_id FROM main WHERE level=?"
            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
            people_printing = cursor.fetchall()
            list_people = []
            for people in people_printing:
                print((await self.bot.fetch_user(people[0])).display_name)
                list_people.append((await self.bot.fetch_user(people[0])).display_name)
            str_people = ""
            emoji_count = 0
            for i in range(len(people_printing)):
                for j in range(counting[i]):
                    str_people += str(list(self.emojis)[emoji_count])
                    emoji_count += 1
                str_people += " " + list_people[i]
                str_people += "\n"
            queue_embed.add_field(name=f"The Current RS{self.rs_channel[str(ctx.message.channel)]} Queue ({count}/4)", value=str_people, inline=False)
            message = await ctx.send(embed=queue_embed)
        else:
            await ctx.send(f"No RS{self.rs_channel[str(ctx.message.channel)]} Queues found, you can start one by typing +1")
        db.commit()
        cursor.close()
        db.close()



def setup(bot):
    bot.add_cog(RSQueue(bot))
    print('RS Queueing loaded')