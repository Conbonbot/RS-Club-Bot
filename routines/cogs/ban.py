import sqlite3
import aiosqlite

import discord
from discord.ext import commands
from sqlalchemy.orm import session

from bot import LOGGER
from bot import TESTING
import time
import asyncio

from datetime import datetime
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
from sqlalchemy.sql.selectable import Select
from sqlalchemy import inspect

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import Banned
from routines import sessionmaker

# TODO: Use an actual settings file.



class RSBan(commands.Cog, name='Ban'):

    def __init__(self, bot):
        self.bot = bot
        self.check_ban.start()


    async def check_ban_status(self):
        async with sessionmaker() as session:
            banned_users = (await session.execute(select(Banned))).scalars()
            current_time = int(time.time())
            for user in banned_users:
                if user.unban_timestamp < current_time:
                    await session.delete(user)
            await session.commit()



    @tasks.loop(hours=24.0)
    async def check_ban(self):
        try:
            await self.check_ban_status()
        except Exception as e:
            print("ERROR IN CHECK BAN", e)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, user_id: int, days: int, *reason):
        # Check to see if they've already been banned
        async with sessionmaker() as session:
            person = await session.get(Banned, user_id)
            if person is None:
                user = await self.bot.fetch_user(user_id)
                unban_time = int(time.time()) + (days * 86400)
                str_reason = ' '.join(reason)
                ban_enter = Banned(user_id=user_id, nickname=user.display_name, unban_timestamp=unban_time, reason=str_reason)
                session.add(ban_enter)
                await session.commit()
                await ctx.send(f"User has been banned for {days} days")
            else:
                await ctx.send("That user is already banned")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user_id: int):
        async with sessionmaker() as session:
            person = await session.get(Banned, user_id)
            if person is None:
                await ctx.send("User is not banned")
            else:
                await session.delete(person)
                await session.commit()
                await ctx.send("User has been unbanned")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def current_bans(self, ctx):
        current_time = int(time.time())
        async with sessionmaker() as session:
            banned_users = (await session.execute(select(Banned))).scalars()
            ban_list = [(user.user_id, user.nickname, (user.unban_timestamp-current_time)/86400, user.reason) for user in banned_users]
            for (id, name, days, reason) in ban_list:
                await ctx.send(f"User ID: {id} | Name: {name} | Days until unban: {format(days,'.2f')} | Reason for ban: {reason}")




def setup(bot):
    bot.add_cog(RSBan(bot))
    LOGGER.info('RS Role System loaded')
