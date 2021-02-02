import os
import random
from dotenv import load_dotenv
import sqlite3
import datetime
from discord.ext import commands
import discord
import asyncio
import sys
import requests
import numpy as np
from discord.utils import get

class RSQueue(commands.Cog, name='Queue'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["1"], help="Join a RS Queue with this command!")
    async def one(self, ctx):
        global rs_role
        rs_role = {
            "rs5-club" : "5", 
            "rs6-club" : "6",
            "rs7-club" : "7",
            "rs8-club" : "8",
            "rs9-club" : "9",
            "rs10-club" : "10"
        }
        for club_channel in rs_role:
            if(str(ctx.message.channel) == club_channel):
                await ctx.send("adding to queue")
            else:
                await ctx.send("Command not run in an RS Channel")
                break

    @commands.command(aliases=["2"], help="Join a RS Queue with this command!")
    async def two(self, ctx):
        for club_channel in rs_role:
            if(str(ctx.message.channel) == club_channel):
                continue
            else:
                await ctx.send("Command not run in an RS Channel")
                break

    @commands.command(aliases=["3"], help="Join a RS Queue with this command!")
    async def three(self, ctx):
        for club_channel in rs_role:
            if(str(ctx.message.channel) == club_channel):
                continue
            else:
                await ctx.send("Command not run in an RS Channel")
                break



def setup(bot):
    bot.add_cog(RSQueue(bot))
    print('RS Queueing loaded')