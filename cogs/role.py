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
from discord.ext.commands import Cog, command

class RSRole(commands.Cog, name='Role'):

    def __init__(self, bot):
        self.bot = bot
        self.emojis = {
            '6️⃣' : 6,
            '7️⃣' : 7,
            '8️⃣' : 8,
            '9️⃣' : 9,
            '🔟' : 10,
            '⏸️' : 11,
            '❌' : -1,
        }
        self.extras = {
            'croid' : discord.utils.get(self.bot.emojis, name='croid')
        }

    @commands.command()
    async def role(self, ctx):
        role_embed = discord.Embed(
            color = discord.Color.green()
        )
        role_embed.add_field(name="React below to recieve the corresponding RS Role, and ❌ to remove all RS Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        message = await ctx.send(embed=role_embed)
        for emoji in self.emojis.keys():
            await message.add_reaction(emoji)
        await ctx.message.delete()

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
        await ctx.send(str(croid) + str(influence) + str(nosanc) + str(notele) + str(rse) + str(suppress) + str(unity) + str(veng) + str(barrage))




    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Example payload below
        #<RawReactionActionEvent message_id=806247306047389696 user_id=805960284543385650 channel_id=805959424081920025 guild_id=805959424081920022 
        # emoji=<PartialEmoji animated=False name='6️⃣' id=None> event_type='REACTION_ADD' 
        # member=<Member id=805960284543385650 name='RS Club Bot' discriminator='3869' bot=True nick=None 
        # guild=<Guild id=805959424081920022 name='RS Club Temp Server' shard_id=None chunked=False member_count=3>>>
        if(payload.message_id == 806269333008678985):
            reaction = str(payload.emoji)
            try:
                rs_role = self.emojis[reaction]
            except:
                rs_role = -2
            if(not payload.member.bot):
                if(rs_role != -2):
                    if(rs_role != -1):
                        await payload.member.add_roles(discord.utils.get(payload.member.guild.roles, name=f'RS{rs_role}'))
                    else:
                        for role in payload.member.roles:
                            if(str(role).startswith("RS")):
                                await payload.member.remove_roles(role)
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.remove_reaction(reaction, payload.member)
        
                    

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        print("on_reaction_remove called")
    



def setup(bot):
    bot.add_cog(RSRole(bot))
    print('RS Role System loaded')