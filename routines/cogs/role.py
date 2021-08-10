import sqlite3
import aiosqlite

import discord
from discord.ext import commands

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

from routines.tables import Queue, Data, Temp, ExternalServer, Reactions
from routines import sessionmaker

# TODO: Use an actual settings file.
ROLE_CHANNEL_ID = 817000327022247936 if TESTING else 801610229040939038

if TESTING:
    clubs_server_id = 805959424081920022
else:
    clubs_server_id = 682479756104564775



class RSRole(commands.Cog, name='Role'):

    def __init__(self, bot):
        self.bot = bot
        self.emojis = {
            '5️⃣': 5,
            '6️⃣': 6,
            '7️⃣': 7,
            '8️⃣': 8,
            '9️⃣': 9,
            '🔟': 10,
            '⏸️': 11,
            '❌': -1,
        }
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
        




    async def amount(self, level):
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
            count = 0
            for person in people:
                count += int(person.amount)
            return count

    async def find(self, selection, id):
        # gets user, channel, guild
        await self.bot.wait_until_ready()
        selection = selection.lower()
        if selection in ("u", "user", "users"):
            user = self.bot.get_user(id)
            if user is None:
                try:
                    user = await self.bot.fetch_user(id)
                except:
                    user = -1
            return user
        elif selection in ("c", "channel", "channels"):
            channel = self.bot.get_channel(id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(id)
                except:
                    channel = -1
            return channel
        elif selection in ("g", "guild", "guilds"):
            guild = self.bot.get_guild(id)
            if guild is None:
                try:
                    guild = await self.bot.fetch_guild(id)
                except:
                    guild = -1
            return guild

    # TODO: work on the commands below

    @commands.command()
    async def role(self, ctx):
        #role_embed = discord.Embed(
        #   color = discord.Color.green()
        #)
        #role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged everytime someone joins a queue, and ❌ to remove all RS Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        #message = await ctx.send(embed=role_embed)
        #for emoji in self.emojis.keys():
        #   await message.add_reaction(emoji)
        #await ctx.message.delete()
        channel = await self.bot.fetch_channel(ROLE_CHANNEL_ID)
        await ctx.send(
            f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def role_34(self, ctx):
        #role_embed = discord.Embed(
        #   color = discord.Color.red()
        #)
        #role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged when a queue is 3/4, and ❌ to remove all RS 3/4 Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        #message = await ctx.send(embed=role_embed)
        #for emoji in self.emojis.keys():
        #   await message.add_reaction(emoji)
        #await ctx.message.delete()
        channel = await self.bot.fetch_channel(ROLE_CHANNEL_ID)
        await ctx.send(
            f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def role_silent(self, ctx):
        #role_embed = discord.Embed(
        #   color = discord.Color.dark_gray()
        #)
        #role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged ONLY when you've joined a queue and it hits 4/4 (and ❌ to remove all RS Silent Roles)", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        #message = await ctx.send(embed=role_embed)
        #for emoji in self.emojis.keys():
        #   await message.add_reaction(emoji)
        #await ctx.message.delete()
        channel = await self.bot.fetch_channel(ROLE_CHANNEL_ID)
        await ctx.send(
            f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.group(invoke_without_command=True)
    async def rsmod(self, ctx):
        right_channel = False
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
        if right_channel or ctx.guild.id != clubs_server_id:
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
                'mass': discord.utils.get(self.bot.emojis, name='mass'),
            }
            # LOGGER.debug(self.extras)
            LOGGER.debug(str(extras['croid']))
            # await ctx.send(str(croid) + str(influence) + str(nosanc) + str(notele) + str(rse) + str(suppress) + str(unity) + str(veng) + str(barrage))
            extra_embed = discord.Embed(
                color=discord.Color.blue(),
                description="Current Mods"
            )
            extra_embed.add_field(name=str(extras['croid']), value=f"Croid: Would like help getting croid.", inline=False)
            extra_embed.add_field(name=str(extras['influence']), value=f"Influence: would like a full system clear.",inline=False)
            extra_embed.add_field(name=str(extras['nosanc']), value=f"Nosanc: No Sanctuary on Battleships.", inline=False)
            extra_embed.add_field(name=str(extras['rse']), value=f"RSE: Will provide RSE.", inline=False)
            extra_embed.add_field(name=str(extras['veng']), value=f"Veng: Vengeance present on Battleship(s).",inline=False)
            extra_embed.add_field(name=str(extras['notele']),value=f"Notele: No Teleport on either Battleship or Transport.", inline=False)
            extra_embed.add_field(name=str(extras['suppress']), value=f"Suppress: Suppress present on Battleship(s).",inline=False)
            extra_embed.add_field(name=str(extras['unity']), value=f"Unity: Unity present on Battleship(s).", inline=False)
            extra_embed.add_field(name=str(extras['battery']), value=f"Battery: Battery present on Battleship(s).",inline=False)
            extra_embed.add_field(name=str(extras['laser']), value=f"Laser: Laser present on Battleship(s).", inline=False)
            extra_embed.add_field(name=str(extras['mass']), value=f"Mass: Mass Battery present on Battleship(s).",inline=False)
            extra_embed.add_field(name=str(extras['barrage']),value=f"Barrage: Barrage, best left alone, and if you help only take out capital ships.",inline=False)
            extra_embed.add_field(name=str(extras['dart']), value=f"Dart: Dart launcher present on Battleship(s).",inline=False)
            extra_embed.add_field(name=str(extras['solo']),value=f"solo: Can solo one planet without any help from others.", inline=False)
            extra_embed.add_field(name=str(extras['solo2']), value=f"solo2: Can solo two planets without any help.",inline=False)
            

            await ctx.send(embed=extra_embed)
            await ctx.send(
                "If you'd like any of these to show up when you enter a queue, type `!rsmod on ModName`, and it will be added. If you'd like to remove it, type `!rsmod off ModName`")
            # for emoji in self.extras.keys():
            #    await message.add_reaction(discord.utils.get(self.bot.emojis, name=emoji))
        else:
            msg = await ctx.send(f"{ctx.author.mention}, this command can only be run in #bot-spam")
            await asyncio.sleep(15)
            await ctx.message.delete()
            await msg.delete()

    @rsmod.group()
    async def on(self, ctx, mod):
        mods = [(str(column))[5:] for column in inspect(Data).c]
        mods = mods[1:]
        right_channel = False
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
        if right_channel or ctx.guild.id != clubs_server_id:
            async with sessionmaker() as session:
                if mod in mods:
                    # Check to see if they already are in the data table
                    results = (await session.get(Data, ctx.author.id))
                    if results is None:
                        mod_insert = Data(**{'user_id': ctx.author.id, mod: True})
                        session.add(mod_insert)
                    else:
                        user_mods = (await session.get(Data, ctx.author.id))
                        setattr(user_mods, mod, True)
                    await ctx.send(f"{ctx.author.mention}, {mod} has been added. When you enter a queue, you'll see {str(discord.utils.get(self.bot.emojis, name=f'{mod}'))} next to your name")
                else:
                    str_mods = ""
                    for str_mod in mods:
                        str_mods += "**" + str_mod + "**" + ", "
                    await ctx.send(f"{mod} not found in list, current available mods: {str_mods[:-2]}")
                await session.commit()
        else:
            msg = await ctx.send(f"{ctx.author.mention}, this command can only be run in #bot-spam")
            await asyncio.sleep(15)
            await ctx.message.delete()
            await msg.delete()

    @rsmod.group()
    async def off(self, ctx, mod):
        mods = [(str(column))[5:] for column in inspect(Data).c]
        mods = mods[1:]
        right_channel = False
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
        if right_channel or ctx.guild.id != clubs_server_id:   
            async with sessionmaker() as session:
                if mod in mods:
                    user_mods = (await session.get(Data, ctx.author.id))
                    setattr(user_mods, mod, False)
                    await ctx.send(f"{ctx.author.mention}, {mod} has been removed. When you enter a queue, you'll no longer see {str(discord.utils.get(self.bot.emojis, name=f'{mod}'))} next to your name")
                else:
                    str_mods = ""
                    for str_mod in mods:
                        str_mods += "**" + str_mod + "**" + ", "
                    await ctx.send(f"{mod} not found in list, current available mods: {str_mods[:-2]}")
                await session.commit()
        else:
            msg = await ctx.send(f"{ctx.author.mention}, this command can only be run in #bot-spam")
            await asyncio.sleep(15)
            await ctx.message.delete()
            await msg.delete()

    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Example payload below
        #<RawReactionActionEvent message_id=806247306047389696 user_id=805960284543385650 channel_id=805959424081920025 guild_id=805959424081920022 
        # emoji=<PartialEmoji animated=False name='6️⃣' id=None> event_type='REACTION_ADD' 
        # member=<Member id=805960284543385650 name='RS Club Bot' discriminator='3869' bot=True nick=None 
        # guild=<Guild id=805959424081920022 name='RS Club Temp Server' shard_id=None chunked=False member_count=3>>>
        async with sessionmaker() as session:
            server = await session.get(Reactions, payload.guild_id)
        if(payload.message_id == 858406627220258836 or payload.message_id == server.rs_message_id): # Regular roles
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    welcome_message = None
                    if(rs_role != -1):
                        if payload.guild_id == clubs_server_id:
                            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'rs{rs_role}'))
                            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name='🌟'))
                            channel = await self.find('c', payload.channel_id)
                            welcome_message = await channel.send(f"Welcome to the clubs {payload.member.mention}! You've been given the RS{rs_role} Role, and you will get pinged everytime someone joins a queue.\nIf you want to suppress these RS pings, type !rsc to hide the channels, and type !rsc again to see the channels again.")
                        else:
                            async with sessionmaker() as session:
                                server = await session.get(ExternalServer, payload.guild_id)
                                rs_str = "rs" + rs_role
                                role_id = getattr(server, rs_str)
                                await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, id=role_id))
                            channel = await self.find('c', payload.channel_id)
                            welcome_message = await channel.send(f"Welcome {payload.member.mention}! You've been given the RS{rs_role} Role, and you will get pinged everytime someone joins a queue of this red star level.\n If you want to stop receiving these pings, react with ❌ to remove the role.")
                    else:
                        if payload.guild_id == clubs_server_id:
                            for role in payload.member.roles:
                                if(str(role).startswith("rs")):
                                    await payload.member.remove_roles(role)
                        else:
                            async with sessionmaker() as session:
                                server = await session.get(ExternalServer, payload.guild_id)
                                rs_str = "rs" + rs_role
                                role_id = getattr(server, rs_str)
                            for role in payload.member.roles:
                                if role.id == role_id:
                                    await payload.member.remove_roles(role)
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(reaction, payload.member)
                    if(welcome_message is not None):
                        await asyncio.sleep(60)
                        await welcome_message.delete()
        elif(payload.message_id == 858406639621898250 or payload.message_id == server.rs_34_message_id): # 3/4 roles
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    welcome_message = None
                    if(rs_role != -1):
                        if payload.guild_id == clubs_server_id:
                            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'rs{rs_role} ¾ need1more'))
                            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name='🌟'))
                            channel = await self.find('c', payload.channel_id)
                            welcome_message = await channel.send(f"Welcome to the clubs {payload.member.mention}! You've been given the RS{rs_role} 3/4 Role, and you will get pinged when a queue of this red star level hits 3/4.\nIf you want to suppress these RS pings, type !rsc to hide the channels, and type !rsc again to see the channels again.")
                        else:
                            async with sessionmaker() as session:
                                server = await session.get(ExternalServer, payload.guild_id)
                                rs_str = "rs" + rs_role + "_34"
                                role_id = getattr(server, rs_str)
                                await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, id=role_id))
                            channel = await self.find('c', payload.channel_id)
                            welcome_message = await channel.send(f"Welcome {payload.member.mention}! You've been given the RS{rs_role} 3/4 Role, and you will get pinged when a queue a queue of this red star level hits 3/4.\n If you want to stop receiving these pings, react with ❌ to remove the role.")
                    else:
                        if payload.guild_id == clubs_server_id:
                            for role in payload.member.roles:
                                print(role)
                                if(str(role).find("¾ need1more") != -1):
                                    await payload.member.remove_roles(role)
                        else:
                            async with sessionmaker() as session:
                                server = await session.get(ExternalServer, payload.guild_id)
                                rs_str = "rs" + rs_role + "_34"
                                role_id = getattr(server, rs_str)
                            for role in payload.member.roles:
                                if role.id == role_id:
                                    await payload.member.remove_roles(role)
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(reaction, payload.member)
                    if(welcome_message is not None):
                        await asyncio.sleep(60)
                        await welcome_message.delete()
        elif(payload.message_id == 858406648041439282 or payload.message_id == server.rs_silent_message_id): # silent roles
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    welcome_message = None
                    if(rs_role != -1):
                        if payload.guild_id == clubs_server_id:
                            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'rs{rs_role} s'))
                            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name='🌟'))
                            channel = await self.find('c', payload.channel_id)
                            welcome_message = await channel.send(f"Welcome to the clubs {payload.member.mention}! You've been given the RS{rs_role} Silent role, and you will get pinged ONLY when a queue you joined hits 4/4.\nIf you want to hide the hide the rs channels, type !rsc to hide them, and type !rsc to see them again.")
                        else:
                            async with sessionmaker() as session:
                                server = await session.get(ExternalServer, payload.guild_id)
                                rs_str = "rs" + rs_role + "_silent"
                                role_id = getattr(server, rs_str)
                                await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, id=role_id))
                            channel = await self.find('c', payload.channel_id)
                            welcome_message = await channel.send(f"Welcome {payload.member.mention}! You've been given the RS{rs_role} Role, and you will get pinged ONLY when a queue you've joined hits 4/4.\nEnjoy your stay.")
                    else:
                        if payload.guild_id == clubs_server_id:
                            for role in payload.member.roles:
                                print(role)
                                if(str(role).find(" s") != -1):
                                    await payload.member.remove_roles(role)
                        else:
                            async with sessionmaker() as session:
                                server = await session.get(ExternalServer, payload.guild_id)
                                rs_str = "rs" + rs_role + "_silent"
                                role_id = getattr(server, rs_str)
                            for role in payload.member.roles:
                                if role.id == role_id:
                                    await payload.member.remove_roles(role)
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(reaction, payload.member)
                    if(welcome_message is not None):
                        await asyncio.sleep(60)
                        await welcome_message.delete()
        else:
            async with sessionmaker.begin() as session:
                results = (await session.execute(select(Temp).where(Temp.message_id == payload.message_id))).scalars()
            if len(results.all()) != 0:
                if(int((await session.execute(select(Temp).where(Temp.message_id == payload.message_id))).scalars().first().user_id) == int(payload.member.id)):
                    if str(payload.emoji) == '✅':
                        async with sessionmaker() as session:
                            # Get user and update timestamp
                            user = await session.get(Temp, (payload.guild_id, payload.channel_id, payload.user_id))
                            user.time = int(time.time())
                            level = user.level
                            amount = user.amount
                            queue_user = await session.get(Queue, (payload.user_id, amount, level))
                            queue_user.time = int(time.time())
                            await session.commit()
                            # Send a requeued message
                            channel = await self.find('c', payload.channel_id)
                            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                            await message.remove_reaction(str(payload.emoji), payload.member)
                            await message.delete()
                            await channel.send(f'{payload.member.mention}, you are requed for a RS{level}! ({await self.amount(level)}/4)')
                            # Delete them from the temp database
                            user = await session.get(Temp, (payload.guild_id, payload.channel_id, payload.user_id))
                            await session.delete(user)
                            await session.commit()
                    elif str(payload.emoji) == '❌':
                        async with sessionmaker() as session:
                            # Get the channel and message
                            channel = await self.find('c', payload.channel_id)
                            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                            # Remove the reaction and the message
                            await message.remove_reaction(str(payload.emoji), payload.member)
                            await message.delete()
                            # Get the user from the temp database
                            user = await session.get(Temp, (payload.guild_id, payload.channel_id, payload.user_id))
                            amount = user.amount
                            level = user.level
                            # Kick the user from the queue 
                            User_leave = (await session.get(Queue, (payload.user_id, amount, level)))
                            count = (await self.amount(level))-1
                            await channel.send(f"{User_leave.nickname} has left RS{level} ({count}/4)")
                            servers = (await session.execute(select(ExternalServer))).scalars()
                            for server in servers:
                                if server.min_rs <= User_leave.level <= server.max_rs:
                                    channel = await self.find('c', server.channel_id)
                                    await channel.send(f"{User_leave.nickname} has left RS{User_leave.level} ({count}/4)")
                            await session.delete(User_leave)
                            await session.commit()
                            # Remove them from the temp database
                            user = await session.get(Temp, (payload.guild_id, payload.channel_id, payload.user_id))
                            await session.delete(user)
                            await session.commit()
                    elif(int(payload.member.id) != self.bot.user.id):
                        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                        await message.remove_reaction(str(payload.emoji), payload.member)
                        channel = await self.find('c', payload.channel_id)
                        await channel.send(f"{payload.member.mention} Don't touch that! That's not for you to react to 🤬🤬🤬")
        
                    

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print("on_reaction_remove called")


def setup(bot):
    bot.add_cog(RSRole(bot))
    LOGGER.info('RS Role System loaded')
