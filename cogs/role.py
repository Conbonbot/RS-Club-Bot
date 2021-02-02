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

    @commands.command(help="React to the message to join a rs level")
    async def role(self, ctx):
        role_embed = discord.Embed(
            color = discord.Color.green()
        )
        role_embed.add_field(name="React below to recieve the corresponding RS Role, and ❌ to remove all RS Roles", value="Current Levels: 6️⃣, 7️⃣, 8️⃣, 9️⃣, 🔟, ⏸️, ❌")
        message = await ctx.send(embed=role_embed)
        emojis = ['6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '⏸️', '❌']
        for emoji in emojis:
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print(self, payload)



def setup(bot):
    bot.add_cog(RSRole(bot))
    print('RS Role System loaded')