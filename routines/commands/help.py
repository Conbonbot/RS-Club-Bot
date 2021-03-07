"""Setup help command."""
import discord
from routines.commands import CommandRoutine

from bot import LOGGER
from bot import TESTING

class Help(CommandRoutine):
    def actions(self):
        @self.bot.command()
        async def help(ctx):
            print(ctx)
            role_embed = discord.Embed(
                description='RS Roles + Pings',
                color=discord.Color.green()
            )
            # TODO: temporary for now
            rs_role_channel = await self.bot.fetch_channel(801610229040939038)
            role_embed.add_field(name=f"RS Roles", value=f"To start queuing, head over to {rs_role_channel.mention} and select how you'd like to be pinged. There are 3 different options you can select (this is done by reacting to the one of the numbers below each message).", inline=False)
            role_embed.add_field(name=f"Pings (Option 1, #/4)", value=f"React to the [first message](https://discord.com/channels/682479756104564775/801610229040939038/808782626612838420) to get pinged EVERYTIME someone joins a queue.")
            role_embed.add_field(name=f"Pings (Option 2, 3/4)", value=f"React to the [second message](https://discord.com/channels/682479756104564775/801610229040939038/808782649946669127) to get pinged ONLY when a queue is 3/4.")
            role_embed.add_field(name=f"Pings (Option 3, 4/4)", value=f"React to the [third message](https://discord.com/channels/682479756104564775/801610229040939038/808960926517559306) to get pinged ONLY when a queue you've joined hits 4/4.")

            queue_embed = discord.Embed(
                description=f'Queueing',
                color=discord.Color.green()
            )
            queue_embed.add_field(name=f"Queuing Commands", value=f"There are currently 4 queueing commands, 3 for joining/leaving queues and 1 for displaying queues. They are +1/2/3 (-1/2/3), !in/i (!out/o), !rs, and !queue/q", inline=False)
            queue_embed.add_field(name=f"+1/2/3 and -1/2/3", value=f"Using +, it will add however many you specify to a queue (for example, +2 in #rs9-club will add 2 players to the current queue). Using -, it will remove however many you specify from a queue (for example, -3 in #rs6-club will remove the 3 players you added from the current queue).")
            queue_embed.add_field(name=f"!in/i and !out/o", value=f"The command !in or !i run in one of the rs channels will add 1 player (you) to the current rs queue, and !out or !o will remove 1 player (you) from the current queue")
            queue_embed.add_field(name=f"!rs", value=f"The !rs command run in one of the rs channels will add 1 player (you) to the current queue.", inline=False)
            queue_embed.add_field(name=f"!queue/q", value=f"This command (!queue or !q) will display the current queue of whatever rs channel you're in.", inline=False)
            queue_embed.add_field(name=f"Additional Parameters", value=f"adding a number to any of the commands that adds players to a queue will specifiy how long you'll remain in a queue before you get timed out (If you don't specifiy a number, it will be 60 minutes). An example is +2 45, which adds 2 players to the queue, and after 45 minutes they will be timed out and removed from the queue.")

            await ctx.send(embed=role_embed)
            await ctx.send(embed=queue_embed)
