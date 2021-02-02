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

    #@commands.command()
    #async def clear(self, ctx, limit: int):
    #    await ctx.channel.purge(limit=limit)


    @commands.command(aliases=["1"], help="Join a RS Queue with this command!")
    async def one(self, ctx):
        right_channel = False
        channel = ""
        for club_channel in self.rs_channel:
            if(club_channel == str(ctx.message.channel)):
                right_channel = True
                channel = club_channel
        if(right_channel):
            has_right_role = False
            for role in ctx.author.roles:
                if(str(role) == f'RS{self.rs_channel[channel]}'):
                    has_right_role = True
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
                    sql = "SELECT amount FROM main WHERE level=?"
                    cursor.execute(sql, [(self.rs_channel[channel])])  
                    total_people = cursor.fetchall()
                    count = 0
                    print(total_people)
                    for people in total_people:
                        count += int(people[0])
                    print(count)
                    db.commit()
                    cursor.close()
                    db.close()
            else:
                await ctx.send(f"{ctx.author.mention}, you aren't RS{self.rs_channel[channel]}")
        else:
            msg = await ctx.send("Command not run in an RS Channel")
            await asyncio.sleep(10)
            await ctx.message.delete()
            await msg.delete
            

    @commands.command(aliases=["2"], help="Join a RS Queue with this command!")
    async def two(self, ctx):
        for club_channel in self.rs_channel:
            if(str(ctx.message.channel) == club_channel):
                continue
            else:
                await ctx.send("Command not run in an RS Channel")
                break

    @commands.command(aliases=["3"], help="Join a RS Queue with this command!")
    async def three(self, ctx):
        for club_channel in self.rs_channel:
            if(str(ctx.message.channel) == club_channel):
                continue
            else:
                await ctx.send("Command not run in an RS Channel")
                break

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



def setup(bot):
    bot.add_cog(RSQueue(bot))
    print('RS Queueing loaded')