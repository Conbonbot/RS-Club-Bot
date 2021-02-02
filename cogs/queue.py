import os
import random
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

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        self.index += 1



    @commands.command(aliases=["1"], help="Join a RS Queue with this command!")
    async def one(self, ctx):
        global rs_channel
        rs_channel = {
            "rs5-club" : "5", 
            "rs6-club" : "6",
            "rs7-club" : "7",
            "rs8-club" : "8",
            "rs9-club" : "9",
            "rs10-club" : "10"
        }
        global rs_ping
        rs_ping = {
            "RS5" : "806018027383422998",
            "RS6" : "806018102797402122",
            "RS7" : "806018133835513876",
            "RS8" : "806018135106519040",
            "RS9" : "806018147487711313",
            "RS10" : "806018150256082984"
        }
        global rs_ping_1more
        rs_ping_1more = {
            "RS5" : "806018333517938688",
            "RS6" : "806018337804910592",
            "RS7" : "806018340203397140",
            "RS8" : "806018343696990208",
            "RS9" : "806018346269016084",
            "RS10" : "806018349183139890"
        }
        for club_channel in rs_channel:
            if(str(ctx.message.channel) == club_channel):
                await ctx.send("adding to queue")
            else:
                await ctx.send("Command not run in an RS Channel")
                break

    @commands.command(aliases=["2"], help="Join a RS Queue with this command!")
    async def two(self, ctx):
        for club_channel in rs_channel:
            if(str(ctx.message.channel) == club_channel):
                continue
            else:
                await ctx.send("Command not run in an RS Channel")
                break

    @commands.command(aliases=["3"], help="Join a RS Queue with this command!")
    async def three(self, ctx):
        for club_channel in rs_channel:
            if(str(ctx.message.channel) == club_channel):
                continue
            else:
                await ctx.send("Command not run in an RS Channel")
                break



def setup(bot):
    bot.add_cog(RSQueue(bot))
    print('RS Queueing loaded')