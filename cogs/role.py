import os
import random
from discord import embeds, message
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
from discord.ext.commands import Cog, command

class RSRole(commands.Cog, name='Role'):

    def __init__(self, bot):
        self.bot = bot
        self.emojis = {
            '5️⃣' : 5,
            '6️⃣' : 6,
            '7️⃣' : 7,
            '8️⃣' : 8,
            '9️⃣' : 9,
            '🔟' : 10,
            '⏸️' : 11,
            '❌' : -1,
        }
        self.extras = {
            'croid' : discord.utils.get(self.bot.emojis, name='croid'),
            'influence' : discord.utils.get(self.bot.emojis, name='influence'),
            'nosanc' : discord.utils.get(self.bot.emojis, name='nosanc'),
            'notele' : discord.utils.get(self.bot.emojis, name='notele'),
            'rse' : discord.utils.get(self.bot.emojis, name='rse'),
            'suppress' : discord.utils.get(self.bot.emojis, name='suppress'),
            'unity' : discord.utils.get(self.bot.emojis, name='unity'),
            'veng' : discord.utils.get(self.bot.emojis, name='veng'),
            'barrage' : discord.utils.get(self.bot.emojis, name='barrage')
        }

    @commands.command()
    async def role(self, ctx):
        #role_embed = discord.Embed(
        #    color = discord.Color.green()
        #)
        #role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged everytime someone joins a queue, and ❌ to remove all RS Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        #message = await ctx.send(embed=role_embed)
        #for emoji in self.emojis.keys():
        #    await message.add_reaction(emoji)
        #await ctx.message.delete()
        channel = await self.bot.fetch_channel(801610229040939038)
        await ctx.send(f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def role_34(self, ctx):
        #role_embed = discord.Embed(
        #    color = discord.Color.red()
        #)
        #role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged when a queue is 3/4, and ❌ to remove all RS 3/4 Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        #message = await ctx.send(embed=role_embed)
        #for emoji in self.emojis.keys():
        #    await message.add_reaction(emoji)
        #await ctx.message.delete()
        channel = await self.bot.fetch_channel(801610229040939038)
        await ctx.send(f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def role_silent(self, ctx):
        #role_embed = discord.Embed(
        #    color = discord.Color.dark_gray()
        #)
        #role_embed.add_field(name="React below to recieve the corresponding RS Role and be pinged ONLY when you've joined a queue and it hits 4/4 (and ❌ to remove all RS Silent Roles)", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        #message = await ctx.send(embed=role_embed)
        #for emoji in self.emojis.keys():
        #    await message.add_reaction(emoji)
        #await ctx.message.delete()
        channel = await self.bot.fetch_channel(801610229040939038)
        await ctx.send(f"If you want your roles changes, check out this channel and react to how you'd like to be pinged: {channel.mention}")

    @commands.command()
    async def extra(self, ctx):
        croid = discord.utils.get(self.bot.emojis, name='croid')
        influence = discord.utils.get(self.bot.emojis, name='influence')
        nosanc = discord.utils.get(self.bot.emojis, name='nosanc')
        notele = discord.utils.get(self.bot.emojis, name='notele')
        rse = discord.utils.get(self.bot.emojis, name='rse')
        suppress = discord.utils.get(self.bot.emojis, name='suppress')
        unity = discord.utils.get(self.bot.emojis, name='unity')
        veng = discord.utils.get(self.bot.emojis, name='veng')
        barrage = discord.utils.get(self.bot.emojis, name='barrage')
        #await ctx.send(str(croid) + str(influence) + str(nosanc) + str(notele) + str(rse) + str(suppress) + str(unity) + str(veng) + str(barrage))
        extra_embed = discord.Embed(
            color = discord.Color.blue()
        )
        extra_embed.add_field(name="Mod Settings", value=f"\nChoose any mods or information you want others to know about, most are self explanatory.\n\n {str(croid)}: Would like help getting croid.\n\n {str(influence)}: Need influence, need full clear.\n\n {str(nosanc)}: No Sanctuary on Battleships.\n\n {str(rse)}: Will provide RSE.\n\n {str(veng)}: Vengeance Player.\n\n {str(notele)}: No Teleport on either Battleship or Transport.\n\n {str(barrage)}: Barrage, best left alone, and if you help only take out capital ships.\n\n {str(suppress)}: Suppress present on Battleship(s).\n\n {str(unity)}: Unity present on Battleship(s).")
        message = await ctx.send(embed=extra_embed)
        for emoji in self.extras.keys():
            await message.add_reaction(discord.utils.get(self.bot.emojis, name=emoji))
        await ctx.message.delete()


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
        
                    

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print("on_reaction_remove called")
    



def setup(bot):
    bot.add_cog(RSRole(bot))
    print('RS Role System loaded')