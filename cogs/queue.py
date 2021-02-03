import os
import random
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

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=1.0)
    async def printer(self):
        self.index += 1

    @commands.command()
    async def clear(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)


    @commands.command(aliases=["1"], help="Join a RS Queue with this command!")
    async def one(self, ctx):
        if ctx.prefix == "+":
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
                    # This is where the fun begins
                    db = sqlite3.connect('rsqueue.sqlite')
                    cursor = db.cursor()
                    # check if they are in any other queues
                    sql = "SELECT user_id FROM main WHERE user_id=?" 
                    cursor.execute(sql, [(ctx.author.id)])
                    if(len(cursor.fetchall()) == 0): # They weren't found in the database, add them
                        sql = "INSERT INTO main(user_id, amount, level) VALUES(?,?,?)"
                        val = (ctx.author.id, 1, self.rs_channel[channel])
                        cursor.execute(sql, val)
                        # Print out the queue
                        # Check if queue is 4/4
                        sql = "SELECT amount FROM main WHERE level=?"
                        cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                        people = cursor.fetchall()
                        count = 0
                        counting = []
                        for person in people:
                            counting.append(person[0])
                            count += int(person[0])
                        if(count == 4):
                            # Print out the queue
                            sql = "SELECT user_id FROM main WHERE level=?"
                            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
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
                            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                        else:
                            queue_embed = discord.Embed(
                                color = discord.Color.red()
                            )
                            sql = "SELECT amount FROM main WHERE level=?"
                            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                            people = cursor.fetchall()
                            count = 0
                            counting = []
                            for person in people:
                                counting.append(person[0])
                                count += int(person[0])
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
                            await ctx.send(embed=queue_embed)
                            await ctx.send(f"{ctx.author.mention} joined RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
                        db.commit()
                        cursor.close()
                        db.close()
                    else:
                        await ctx.send(f"{ctx.author.mention}, you are already in a RS Queue")
                else:
                    await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")
            else:
                msg = await ctx.send("Command not run in an RS Channel")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await msg.delete
        elif ctx.prefix == "-":
            db = sqlite3.connect('rsqueue.sqlite')
            cursor = db.cursor()
            # check if they are in any other queues
            sql = "SELECT amount FROM main WHERE user_id=?" 
            cursor.execute(sql, [(ctx.author.id)])
            result = cursor.fetchall()
            if(len(result) == 0): # Didn't find them in any queues
                await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues at the moment")
            else: # Remove 1 of them from the queue 
                # Get level
                sql = "SELECT level FROM main WHERE user_id=?"
                cursor.execute(sql, [(ctx.author.id)])
                levels = cursor.fetchall()
                sql = "DELETE FROM main WHERE user_id=?"
                cursor.execute(sql, [(ctx.author.id)])
                if(result[0][0] > 1):
                    sql = "INSERT INTO main(user_id, amount, level) VALUES(?,?,?)"
                    val = (ctx.author.id, int(result[0][0])-1, levels[0][0])
                    cursor.execute(sql, val)
                sql = "SELECT amount FROM main WHERE level=?"
                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                people = cursor.fetchall()
                count = 0
                counting = []
                for person in people:
                    counting.append(person[0])
                    count += int(person[0])
                await ctx.send(f"{ctx.author.display_name} has left the RS{levels[0][0]} Queue ({count}/4)")
            db.commit()
            cursor.close()
            db.close()



        
        

    @commands.command(aliases=["2"], help="Join a RS Queue with this command!")
    async def two(self, ctx):
        if ctx.prefix == "+":
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
                    # This is where the fun begins
                    db = sqlite3.connect('rsqueue.sqlite')
                    cursor = db.cursor()
                    # check if they are in any other queues
                    sql = "SELECT user_id FROM main WHERE user_id=?" 
                    cursor.execute(sql, [(ctx.author.id)])
                    if(len(cursor.fetchall()) == 0): # They weren't found in the database, add them
                        # Check if there is enough space, and remove excess
                        sql = "SELECT amount FROM main WHERE level=?"
                        cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                        people = cursor.fetchall()
                        count = 0
                        counting = []
                        for person in people:
                            counting.append(person[0])
                            count += int(person[0])
                        if(count > 2):
                            await ctx.send(f"{ctx.author.mention}, The queue would be more than full if you added 2 people")
                        else:
                            sql = "INSERT INTO main(user_id, amount, level) VALUES(?,?,?)"
                            val = (ctx.author.id, 2, self.rs_channel[channel])
                            cursor.execute(sql, val)
                            # Print out the queue
                            sql = "SELECT amount FROM main WHERE level=?"
                            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                            people = cursor.fetchall()
                            count = 0
                            counting = []
                            for person in people:
                                counting.append(person[0])
                                count += int(person[0])
                            print(count)
                            if(count == 4):
                                # Print out the queue
                                sql = "SELECT user_id FROM main WHERE level=?"
                                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
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
                                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                            else:
                                queue_embed = discord.Embed(
                                    color = discord.Color.red()
                                )
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
                                await ctx.send(embed=queue_embed)
                                await ctx.send(f"{ctx.author.mention} joined RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
                            db.commit()
                            cursor.close()
                            db.close()
                    else:
                        await ctx.send(f"{ctx.author.mention}, you are already in a RS Queue")
                else:
                    await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")
            else:
                msg = await ctx.send("Command not run in an RS Channel")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await msg.delete
        elif ctx.prefix == "-":
            db = sqlite3.connect('rsqueue.sqlite')
            cursor = db.cursor()
            # check if they are in any other queues
            sql = "SELECT amount FROM main WHERE user_id=?" 
            cursor.execute(sql, [(ctx.author.id)])
            result = cursor.fetchall()
            if(len(result) == 0): # Didn't find them in any queues
                await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues at the moment")
            else: # Remove 2 of them from the queue 
                # Get level
                sql = "SELECT level FROM main WHERE user_id=?"
                cursor.execute(sql, [(ctx.author.id)])
                levels = cursor.fetchall()
                sql = "DELETE FROM main WHERE user_id=?"
                cursor.execute(sql, [(ctx.author.id)])
                sql = "INSERT INTO main(user_id, amount, level) VALUES(?,?,?)"
                if(result[0][0] >= 2): # Result[0][0] is the amount of people they have in a queue
                    val = (ctx.author.id, int(result[0][0])-2, levels[0][0])
                    cursor.execute(sql, val)
                elif(result[0][0] == 1):
                    val = (ctx.author.id, int(result[0][0])-1, levels[0][0])
                    cursor.execute(sql, val)
                sql = "SELECT amount FROM main WHERE level=?"
                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                people = cursor.fetchall()
                count = 0
                counting = []
                for person in people:
                    counting.append(person[0])
                    count += int(person[0])
                await ctx.send(f"{ctx.author.display_name} has left the RS{levels[0][0]} Queue ({count}/4)")
            db.commit()
            cursor.close()
            db.close()

    @commands.command(aliases=["3"], help="Join a RS Queue with this command!")
    async def three(self, ctx):
        if ctx.prefix == "+":
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
                    # This is where the fun begins
                    db = sqlite3.connect('rsqueue.sqlite')
                    cursor = db.cursor()
                    # check if they are in any other queues
                    sql = "SELECT user_id FROM main WHERE user_id=?" 
                    cursor.execute(sql, [(ctx.author.id)])
                    if(len(cursor.fetchall()) == 0): # They weren't found in the database, add them
                        # Check if there is enough space, and remove excess
                        sql = "SELECT amount FROM main WHERE level=?"
                        cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                        people = cursor.fetchall()
                        count = 0
                        counting = []
                        for person in people:
                            counting.append(person[0])
                            count += int(person[0])
                        if(count > 1):
                            await ctx.send(f"{ctx.author.mention}, The queue would be more than full if you added 3 people")
                        else:
                            sql = "INSERT INTO main(user_id, amount, level) VALUES(?,?,?)"
                            val = (ctx.author.id, 3, self.rs_channel[channel])
                            cursor.execute(sql, val)
                            # Print out the queue
                            sql = "SELECT amount FROM main WHERE level=?"
                            cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                            people = cursor.fetchall()
                            count = 0
                            counting = []
                            for person in people:
                                counting.append(person[0])
                                count += int(person[0])
                            if(count == 4):
                                # Print out the queue
                                sql = "SELECT user_id FROM main WHERE level=?"
                                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
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
                                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                            else:
                                queue_embed = discord.Embed(
                                    color = discord.Color.red()
                                )
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
                                await ctx.send(embed=queue_embed)
                                await ctx.send(f"{ctx.author.mention} joined RS{self.rs_channel[str(ctx.message.channel)]} ({count}/4)")
                            db.commit()
                            cursor.close()
                            db.close()
                    else:
                        await ctx.send(f"{ctx.author.mention}, you are already in a RS Queue")
                else:
                    await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")
            else:
                msg = await ctx.send("Command not run in an RS Channel")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await msg.delete
        elif ctx.prefix == '-':
            db = sqlite3.connect('rsqueue.sqlite')
            cursor = db.cursor()
            # check if they are in any other queues
            sql = "SELECT amount FROM main WHERE user_id=?" 
            cursor.execute(sql, [(ctx.author.id)])
            result = cursor.fetchall()
            if(len(result) == 0): # Didn't find them in any queues
                await ctx.send(f"{ctx.author.mention}, You aren't in an RS Queues at the moment")
            else: # Remove 2 of them from the queue 
                # Get level
                sql = "SELECT level FROM main WHERE user_id=?"
                cursor.execute(sql, [(ctx.author.id)])
                levels = cursor.fetchall()
                sql = "DELETE FROM main WHERE user_id=?"
                cursor.execute(sql, [(ctx.author.id)])
                sql = "INSERT INTO main(user_id, amount, level) VALUES(?,?,?)"
                if(result[0][0] == 3): # Result[0][0] is the amount of people they have in a queue
                    val = (ctx.author.id, int(result[0][0])-3, levels[0][0])
                    cursor.execute(sql, val)
                elif(result[0][0] == 2):
                    val = (ctx.author.id, int(result[0][0])-2, levels[0][0])
                    cursor.execute(sql, val)
                elif(result[0][0] == 1):
                    val = (ctx.author.id, int(result[0][0])-1, levels[0][0])
                    cursor.execute(sql, val)
                sql = "SELECT amount FROM main WHERE level=?"
                cursor.execute(sql, [(self.rs_channel[str(ctx.message.channel)])])
                people = cursor.fetchall()
                count = 0
                counting = []
                for person in people:
                    counting.append(person[0])
                    count += int(person[0])
                await ctx.send(f"{ctx.author.display_name} has left the RS{levels[0][0]} Queue ({count}/4)")
            db.commit()
            cursor.close()
            db.close()
        

    @commands.command(aliases=["o"], help="Leave your current RS Queue")
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

    @commands.command(aliases=["q"])
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