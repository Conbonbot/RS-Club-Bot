import sqlite3

import discord
from discord.ext import commands

from bot import LOGGER
from bot import TESTING

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


    def sql_command(self, sql, val, data='rsqueue.sqlite'):
        db = sqlite3.connect(data)
        cursor = db.cursor()
        cursor.execute(sql, val)
        results = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return results


    def amount(self, level):
        people = self.sql_command("SELECT amount FROM main WHERE level=?", [(level)])
        count = 0
        counting = []
        for person in people:
            counting.append(person[0])
            count += int(person[0])
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

    @rsmod.group()
    async def on(self, ctx, mod):
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        stuff = cursor.execute('select * from data')
        current_mods = [description[0] for description in stuff.description]
        current_mods = current_mods[1:]
        db.commit()
        cursor.close()
        db.close()
        mod = mod.lower()
        if mod in current_mods:
            # Check to see if they already are in the data table
            results = self.sql_command("SELECT user_id FROM data WHERE user_id=?", [ctx.author.id])
            if len(results) == 0:
                self.sql_command(f"INSERT INTO data(user_id, {mod}) VALUES(?,?)", (ctx.author.id, 1))
            else:
                self.sql_command(f"UPDATE data SET {mod}=? WHERE user_id=?", (1, ctx.author.id))
            await ctx.send(
                f"{ctx.author.mention}, {mod} has been added. When you enter a queue, you'll see {str(discord.utils.get(self.bot.emojis, name=f'{mod}'))} next to your name")
        else:
            str_mods = ""
            for str_mod in current_mods:
                str_mods += "**" + str_mod + "**" + ", "
            await ctx.send(f"{mod} not found in list, current available mods: {str_mods[:-2]}")

    @rsmod.group()
    async def off(self, ctx, mod):
        db = sqlite3.connect('rsqueue.sqlite')
        cursor = db.cursor()
        stuff = cursor.execute('select * from data')
        current_mods = [description[0] for description in stuff.description]
        current_mods = current_mods[1:]
        db.commit()
        cursor.close()
        db.close()
        mod = mod.lower()
        if mod in current_mods:
            self.sql_command(f"UPDATE data SET {mod}=? WHERE user_id=?", (0, ctx.author.id))
            await ctx.send(
                f"{ctx.author.mention}, {mod} has been removed. When you enter a queue, you'll no longer see {str(discord.utils.get(self.bot.emojis, name=f'{mod}'))} next to your name")
        else:
            str_mods = ""
            for str_mod in current_mods:
                str_mods += "**" + str_mod + "**" + ", "
            await ctx.send(f"{mod} not found in list, current available mods: {str_mods[:-2]}")


def setup(bot):
    bot.add_cog(RSRole(bot))
    LOGGER.info('RS Role System loaded')
