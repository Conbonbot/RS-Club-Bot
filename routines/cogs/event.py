import asyncio
from asyncio.locks import Condition
import re
import time
from aiosqlite.core import LOG

import discord
import sqlite3
from discord import player
from discord import embeds
import psycopg2

from datetime import datetime
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.log import echo_property
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect
from sqlalchemy import event

from random import random

from bot import LOGGER
from bot import TESTING

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import Queue, Data, Temp, Stats, Event
from routines import sessionmaker
from routines import engine

if TESTING:
    rs_leaderboard_channel_id = 867107483951955968
    rs_leaderboard_message_id = 867135930652950600
    guild_id = 805959424081920022
else:
    rs_leaderboard_channel_id = 867107639695114281

class RSEvent(commands.Cog, name='Event'):

    def __init__(self, bot):
        self.bot = bot
        self.leaderboard_loop.start()


    async def update_leaderboard(self):
        async with sessionmaker() as session:
            all_events = (await session.execute(select(Event).where(Event.score != 0))).scalars()
            # Check each run in event
            player_data = []
            for event in all_events:
                run_stats = (await session.execute(select(Stats).where(Stats.run_id == event.run_id))).scalars()
                for run in run_stats:
                    player_data.append([run.user_id, event.score])
        # Add up all player data
        D = {}
        for (x, y) in player_data:
            if x not in D.keys():
                D[x] = y
            else:
                D[x] += y
        full_data = [[x, D[x]] for x in D.keys()]
        full_data.sort(key = lambda x: x[1], reverse=True)
        # Work around the longest name
        longest_name = 0
        guild = await self.bot.fetch_guild(guild_id)
        for i in range(len(full_data)):
            full_data[i][0] = (await guild.fetch_member(full_data[i][0])).display_name
            if len(full_data[i][0]) > longest_name:
                longest_name = len(full_data[i][0])
        # Now build the leaderboard

        max_players = 50
        # String will be 5 long for position, longest_name + 2 (1 space on each side) for user, and 1+len(full_data[0][1])
        if longest_name % 2 == 0:
            leaderboard_string = "```" + f"Rank |" + " "*(int(longest_name/2)) + "User" + " "*(int(longest_name/2)-2) + "| Score\n"
        else:
            leaderboard_string = "```" + f"Rank |" + " "*(int(longest_name/2)) + "User" + " "*(int(longest_name/2)-1) + "| Score\n"
        for i in range(len(full_data)):
            if i < max_players:
                leaderboard_string += f"#{i+1}" + " " *(int(5)-int(len(f"#{i}"))) + f"| " + f"{full_data[i][0]}" + " "*(1+longest_name-int(len(full_data[i][0]))) + "| " + f"{full_data[i][1]}\n"
        leaderboard_string += "```"
        leaderboard_embed = discord.Embed(title=f"RS Event Leaderboard", description=leaderboard_string, color=discord.Color.green())
        channel = await self.bot.fetch_channel(rs_leaderboard_channel_id)
        message = await channel.fetch_message(rs_leaderboard_message_id)
        await message.edit(embed=leaderboard_embed)
                

    @tasks.loop(minutes=15.0)
    async def leaderboard_loop(self):
        try:
            await self.update_leaderboard()
        except Exception as e:
            print(f"Error: {e}")


    @commands.command(aliases=["stats", "s"])
    async def rsstats(self, ctx, name=None):
        async with sessionmaker() as session:
            if name is None:
                users = (await session.execute(select(Stats).where(Stats.user_id == ctx.author.id))).scalars()
            else:
                users = (await session.execute(select(Stats).where(Stats.user_id == int(name)))).scalars()
            stats = {'rs5' : 0, 'rs6' : 0, 'rs7' : 0, 'rs8' : 0, 'rs9' : 0, 'rs10' : 0, 'rs11' : 0}
            for user in users:
                stats[f'rs{user.rs_level}'] += 1
            stats_string = "```RS#  | Amount\n"
            for i in range(5, 12):
                if stats[f'rs{i}'] != 0:
                    stats_string += f"RS{i}" + " " * (int(5)-int(len(f"RS{i}"))) + f"| {stats[f'rs{i}']}\n"
            stats_string += "```"
            if name is None:
                stats_embed = discord.Embed(title=f"RS Stats for {ctx.author.display_name}", description=stats_string, color=discord.Color.green())
            else:
                full_user = await self.bot.fetch_user(int(name))
                stats_embed = discord.Embed(title=f"RS Stats for {full_user.display_name}", description=stats_string, color=discord.Color.green())
            await ctx.send(embed=stats_embed)

    @commands.command()
    async def rsinput(self, ctx, id, score):
        id = int(id)
        score = int(score)
        async with sessionmaker() as session:
            event = await session.get(Event, id)
            users = (await session.execute(select(Stats).where(Stats.run_id == id))).scalars()
            ids = [user.user_id for user in users]
            if ctx.author.id in ids:
                if event.score == 0:
                    event.score = score
                    await ctx.send(f"Score successfully set to {score}")
                else:
                    await ctx.send(f"This run has already been counted with a score of {event.score}")
            else:
                await ctx.send(f"Only users in that rs can set the score of their rs.")
            await session.commit()




    



def setup(bot):
    bot.add_cog(RSEvent(bot))
    LOGGER.debug('RS Event Loaded')
