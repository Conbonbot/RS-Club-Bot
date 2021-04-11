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

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'routines')))

from routines.tables import Queue, Data, Temp
from routines import sessionmaker

# TODO: Use an actual settings file.
ROLE_CHANNEL_ID = 817000327022247936 if TESTING else 801610229040939038





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
        self.current_mods = ["croid", "influence", "nosanc", "notele", "rse", "suppress", "unity", "veng", "barrage", "laser", "dart", "battery", "solo", "solo2"]




    async def amount(self, level):
        async with sessionmaker.begin() as session:
            people = (await session.execute(select(Queue).where(Queue.level == int(level)))).scalars()
            count = 0
            for person in people:
                count += int(person.amount)
            return count

    @commands.command()
    async def role(self, ctx):
        # role_embed = discord.Embed(
        #    color = discord.Color.green()
        # )
        # role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged everytime someone joins a queue, and ❌ to remove all RS Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        # message = await ctx.send(embed=role_embed)
        # for emoji in self.emojis.keys():
        #    await message.add_reaction(emoji)
        # await ctx.message.delete()
        channel = await self.bot.fetch_channel(ROLE_CHANNEL_ID)
        await ctx.send(
            f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def role_34(self, ctx):
        # role_embed = discord.Embed(
        #    color = discord.Color.red()
        # )
        # role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged when a queue is 3/4, and ❌ to remove all RS 3/4 Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        # message = await ctx.send(embed=role_embed)
        # for emoji in self.emojis.keys():
        #    await message.add_reaction(emoji
        # await ctx.message.delete()
        channel = await self.bot.fetch_channel(ROLE_CHANNEL_ID)
        await ctx.send(
            f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def role_silent(self, ctx):
        # role_embed = discord.Embed(
        #    color = discord.Color.dark_gray()
        # )
        # role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged ONLY when you've joined a queue and it hits 4/4 (and ❌ to remove all RS Silent Roles)", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        # message = await ctx.send(embed=role_embed)
        # for emoji in self.emojis.keys():
        #    await message.add_reaction(emoji)
        # await ctx.message.delete()
        channel = await self.bot.fetch_channel(ROLE_CHANNEL_ID)
        await ctx.send(
            f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.group(invoke_without_command=True)
    async def rsmod(self, ctx):
        right_channel = False
        channel = ""
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
                channel = club_channel
        if right_channel:
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
            extra_embed.add_field(name=str(extras['barrage']),value=f"Barrage: Barrage, best left alone, and if you help only take out capital ships.",inline=False)
            extra_embed.add_field(name=str(extras['suppress']), value=f"Suppress: Suppress present on Battleship(s).",inline=False)
            extra_embed.add_field(name=str(extras['unity']), value=f"Unity: Unity present on Battleship(s).", inline=False)
            extra_embed.add_field(name=str(extras['laser']), value=f"Laser: Laser present on Battleship(s).", inline=False)
            extra_embed.add_field(name=str(extras['battery']), value=f"Battery: Battery present on Battleship(s).",inline=False)
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
        right_channel = False
        channel = ""
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
                channel = club_channel
        if right_channel:
            session = sessionmaker()
            if mod in self.current_mods:
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
                for str_mod in self.current_mods:
                    str_mods += "**" + str_mod + "**" + ", "
                await ctx.send(f"{mod} not found in list, current available mods: {str_mods[:-2]}")
            await session.commit()
            await session.close()
        else:
            msg = await ctx.send(f"{ctx.author.mention}, this command can only be run in #bot-spam")
            await asyncio.sleep(15)
            await ctx.message.delete()
            await msg.delete()

    @rsmod.group()
    async def off(self, ctx, mod):
        right_channel = False
        channel = ""
        for club_channel in self.rs_channel:
            if club_channel == str(ctx.message.channel):
                right_channel = True
                channel = club_channel
        if right_channel:
            session = sessionmaker()
            if mod in self.current_mods:
                user_mods = (await session.get(Data, ctx.author.id))
                setattr(user_mods, mod, False)
                await ctx.send(f"{ctx.author.mention}, {mod} has been removed. When you enter a queue, you'll no longer see {str(discord.utils.get(self.bot.emojis, name=f'{mod}'))} next to your name")
            else:
                str_mods = ""
                for str_mod in self.current_mods:
                    str_mods += "**" + str_mod + "**" + ", "
                await ctx.send(f"{mod} not found in list, current available mods: {str_mods[:-2]}")
            await session.commit()
            await session.close()
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
        if(payload.message_id == 808782626612838420):
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    welcome_message = None
                    if(rs_role != -1):
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'rs{rs_role}'))
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name='🌟'))
                        channel = await self.bot.fetch_channel(payload.channel_id)
                        welcome_message = await channel.send(f"Welcome to the clubs {payload.member.mention}! You've been given the RS{rs_role} Role, and you will get pinged everytime someone joins a queue.\nIf you want to suppress this pings, type !rsc to hide the channels, and type !rsc again to see the channels again.")
                    else:
                        for role in payload.member.roles:
                            if(str(role).startswith("rs")):
                                await payload.member.remove_roles(role)
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(reaction, payload.member)
                    if(welcome_message is not None):
                        await asyncio.sleep(60)
                        await welcome_message.delete()
        elif(payload.message_id == 808782649946669127):
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    welcome_message = None
                    if(rs_role != -1):
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'rs{rs_role} ¾ need1more'))
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name='🌟'))
                        channel = await self.bot.fetch_channel(payload.channel_id)
                        welcome_message = await channel.send(f"Welcome to the clubs {payload.member.mention}! You've been given the RS{rs_role} 3/4 Role, and you will get pinged when a queue hits 3/4.\nIf you want to suppress this pings, type !rsc to hide the channels, and type !rsc again to see the channels again.")
                    else:
                        for role in payload.member.roles:
                            print(role)
                            if(str(role).find("¾ need1more") != -1):
                                await payload.member.remove_roles(role)
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(reaction, payload.member)
                    if(welcome_message is not None):
                        await asyncio.sleep(60)
                        await welcome_message.delete()
        elif(payload.message_id == 808960926517559306): 
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    welcome_message = None
                    if(rs_role != -1):
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'rs{rs_role} s'))
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name='🌟'))
                        channel = await self.bot.fetch_channel(payload.channel_id)
                        welcome_message = await channel.send(f"Welcome to the clubs {payload.member.mention}! You've been given the RS{rs_role} Silent role, and you will get pinged ONLY when a queue you joined hits 4/4.\nIf you want to suppress this pings, type !rsc to hide the channels, and type !rsc again to see the channels again.")
                    else:
                        for role in payload.member.roles:
                            print(role)
                            if(str(role).find(" s") != -1):
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
                        async with sessionmaker.begin() as session:
                            user = await session.get(Temp, (payload.guild_id, payload.user_id, payload.message_id))
                            user.time = int(time.time())
                            level = user.level
                            amount = user.amount

                            queue_user = await session.get(Queue, (payload.guild_id, payload.user_id, amount, level))
                            queue_user.time = int(time.time())

                            
                            channel = await self.bot.fetch_channel(payload.channel_id)
                            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                            await message.remove_reaction(str(payload.emoji), payload.member)
                            await message.delete()
                            await channel.send(f'{payload.member.mention}, you are requed for a RS{level}! ({await self.amount(level)}/4)')
                            user = await session.get(Temp, (payload.guild_id, payload.user_id, payload.message_id))
                            await session.delete(user)
                            await session.flush()
                    elif str(payload.emoji) == '❌':
                        async with sessionmaker.begin() as session:
                            channel = await self.bot.fetch_channel(payload.channel_id)
                            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                            await message.remove_reaction(str(payload.emoji), payload.member)
                            await message.delete()
                            user = (await session.get(Temp, (payload.guild_id, payload.user_id, payload.message_id)))
                            amount = user.amount
                            level = user.level

                            User_leave = (await session.get(Queue, (payload.guild_id, payload.user_id, amount, level)))
                            await session.delete(User_leave)
                            await session.flush()
                        await channel.send(f"{payload.member.mention} has left RS{level} ({await self.amount(level)}/4)")
                        async with sessionmaker.begin() as session:
                            user = await session.get(Temp, (payload.guild_id, payload.user_id, payload.message_id))
                            await session.delete(user)
                            await session.flush()
                    elif(int(payload.member.id) != self.bot.user.id):
                        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                        await message.remove_reaction(str(payload.emoji), payload.member)
                        channel = await self.bot.fetch_channel(payload.channel_id)
                        await channel.send(f"{payload.member.mention} Don't touch that! That's not for you to react to 🤬🤬🤬")
        
                    

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print("on_reaction_remove called")


def setup(bot):
    bot.add_cog(RSRole(bot))
    LOGGER.info('RS Role System loaded')
