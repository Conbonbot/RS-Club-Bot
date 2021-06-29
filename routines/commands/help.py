"""Setup help command."""
import discord
from routines.commands import CommandRoutine

from bot import LOGGER
from bot import TESTING

class Help(CommandRoutine):
    def actions(self):
        @self.bot.group(invoke_without_command=True)
        async def help(ctx, option=None):
            if option is None:
                await ctx.send("There are multiple sections to the help command, and they can be accessed by adding another parameter to the help command, to specify the group you would like more information on. Below is the current categories to the help command:")
                await ctx.send("```Roles (their types and how to get them): type `!help roles` (or role/r)```")
                await ctx.send("```The Queueing System (how to join, leave, add a friend, etc.): type `!help queue` (or q/queues)```")
                await ctx.send("```Rsmods (showing mods when you enter a queue to alert players what mods are on your ships/whatever else you want them to know): type `!help rsmod` (or rs/rsmods)```")
                await ctx.send("```External Servers and The Clubs: type `!help external` (or e)```")
                await ctx.send("```Other useful commands: type `!help other` (or o)```")
            elif option == "roles" or option == "role" or option == "r":
                role_embed = discord.Embed(
                    title='RS Roles + Pings',
                    color=discord.Color.green()
                )
                if TESTING:
                    rs_role_channel = await self.bot.fetch_channel(806269015344414762)
                    role_embed.add_field(name=f"RS Roles", value=f"To start queuing, head over to {rs_role_channel.mention} and select how you'd like to be pinged. There are 3 different options you can select (this is done by reacting to the one of the numbers below each message).", inline=False)
                    role_embed.add_field(name=f"Pings (Option 1, #/4)", value=f"React to the [first message] to get pinged EVERYTIME someone joins a queue.")
                    role_embed.add_field(name=f"Pings (Option 2, 3/4)", value=f"React to the [second message] to get pinged ONLY when a queue is 3/4.")
                    role_embed.add_field(name=f"Pings (Option 3, 4/4)", value=f"React to the [third message] to get pinged ONLY when a queue you've joined hits 4/4.")

                else:
                    rs_role_channel = await self.bot.fetch_channel(801610229040939038)
                    role_embed.add_field(name=f"RS Roles", value=f"To start queuing, head over to {rs_role_channel.mention} and select how you'd like to be pinged. There are 3 different options you can select (this is done by reacting to the one of the numbers below each message).", inline=False)
                    role_embed.add_field(name=f"Pings (Option 1, #/4)", value=f"React to the [first message](https://discord.com/channels/682479756104564775/801610229040939038/858406627220258836) to get pinged EVERYTIME someone joins a queue.")
                    role_embed.add_field(name=f"Pings (Option 2, 3/4)", value=f"React to the [second message](https://discord.com/channels/682479756104564775/801610229040939038/858406639621898250) to get pinged ONLY when a queue is 3/4.")
                    role_embed.add_field(name=f"Pings (Option 3, 4/4)", value=f"React to the [third message](https://discord.com/channels/682479756104564775/801610229040939038/858406648041439282) to get pinged ONLY when a queue you've joined hits 4/4.")
                await ctx.send(embed=role_embed)
            elif option == "queue" or option == "q" or option == "queues":
                queue_embed = discord.Embed(
                    title='Queueing',
                    color=discord.Color.green()
                )
                queue_embed.add_field(name=f"Queuing Commands", value=f"There are currently 4 queueing commands, 3 for joining/leaving queues and 1 for displaying queues. They are +1/2/3 (-1/2/3), !in/i (!out/o), !rs, and !queue/q", inline=False)
                queue_embed.add_field(name=f"+1/2/3 and -1/2/3", value=f"Using +, it will add however many you specify to a queue (for example, +2 in #rs9-club will add 2 players to the current queue). Using -, it will remove however many you specify from a queue (for example, -3 in #rs6-club will remove the 3 players you added from the current queue).")
                queue_embed.add_field(name=f"!in/i and !out/o", value=f"The command !in or !i run in one of the rs channels will add 1 player (you) to the current rs queue, and !out or !o will remove 1 player (you) from the current queue")
                queue_embed.add_field(name=f"!rs", value=f"The !rs command run in one of the rs channels will add 1 player (you) to the current queue.", inline=False)
                queue_embed.add_field(name=f"!queue/q", value=f"This command (!queue or !q) will display the current queue of whatever rs channel you're in.", inline=False)
                queue_embed.add_field(name=f"Additional Parameters", value=f"adding a number to any of the commands that adds players to a queue will specifiy how long you'll remain in a queue before you get timed out (If you don't specifiy a number, it will be 60 minutes). An example is +2 45, which adds 2 players to the queue, and after 45 minutes they will be timed out and removed from the queue.")
                await ctx.send(embed=queue_embed)
            elif option == "rsmod" or option == "rs" or option == "rsmods":
                rsmod_embed = discord.Embed(
                    title=f'RS Mods',
                    color=discord.Color.green()
                )
                rsmod_embed.add_field(name=f"RS Mods", value=f"There are currently 14 different mods you can tell players about when you join a queue. They are: ```croid, influence, nosanc, rse, veng, notele, barrage, suppress, unity, laser, battery, mass, dart, solo, solo2``` If you'd like to get more information based on each mod, type `!rsmod`.", inline=False)
                rsmod_embed.add_field(name=f"Adding Mods", value=f"If you want to add one of these mods so they show up next to your name when you are in a queue, type `!rsmod on ModName` and that mod will show up when you join a queue. Note: ModName is NOT case sensitive.")
                rsmod_embed.add_field(name=f"Removing Mods", value=f"If you want to remove one of these mods so it no longer shows up when you are in a queue, type `!rsmod off ModName`. Note: ModName is NOT case sensitive.")
                try:
                    conbonbot_user = await self.bot.fetch_user(384481151475122179)
                except:
                    rsmod_embed.add_field(name=f"Requesting Mods", value=f"If you want more mods, ping me at Conbonbot#0680.")
                else:
                    rsmod_embed.add_field(name=f"Requesting Mods", value=f"If you want more mods, ping {conbonbot_user.mention} (Conbonbot#0680)")
                await ctx.send(embed=rsmod_embed)
            elif option == "other" or option == "o":
                other_embed = discord.Embed(
                    title='Other',
                    color=discord.Color.green()
                )
                other_embed.add_field(name="Other Commands", value=f"Other useful commands are `!rsc`, `!refresh`, and `!corp`. They are explained in more detail below.", inline=False)
                other_embed.add_field(name="!rsc", value=f"If you want to take a break from the pings (and the channels) without removing the roles, type `!rsc`, and it will remove your 🌟 role, which will hide the channels and the pings. If you want to get back to the action after typing `!rsc`, just do the command again, and it will add the 🌟 role, which allows you to see and interact with the RS channels", inline=False)
                other_embed.add_field(name="!refresh", value=f"When you enter a queue, you will be queued for 60 minutes, unless you specify a time parameter when you enter a queue (if you want to know how to do that, check out `!help q`). If you want to refresh your spot in the queue, which essentially sets how long you've been in a queue back to 0 minutes, type `!refresh`, `!r`, `!^`, or `!staying`.", inline=False)
                other_embed.add_field(name="!corp", value=f"If you want to set your corp (which changes your nickname to include your corp), type `!corp CorpName` and it will set your nickname to be [CorpName] UserName. If you want to include your corporation's % bonus, specify it in the corp command like this `!corp CorpName (bonus%)`")
                await ctx.send(embed=other_embed)
            elif option == "external" or option == "e":
                external_embed = discord.Embed(
                    title='External',
                    color=discord.Color.green()
                )
                if TESTING:
                    external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=809871917946634261&permissions=8&scope=bot) and follow the steps")
                else:
                    external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=805960284543385650&permissions=8&scope=bot) and follow the steps")
                external_embed.add_field(name="First Time Setup", value=f"Run `!connect #` (where `#` is the max rs level of your server), and your server will be connected to The Clubs.")
                external_embed.add_field(name="Setting up max RS levels", value=f"To change the max RS level of your server, run `!connect #` where `#` is the max rs level of your server.")
                external_embed.add_field(name="Users (RS Level + Pings)", value=f"Each user of your discord server will have to run the `!user # %` command which sets up how a user should be pinged when a user enters a specific queue. `#` refers to the user's current rs level, and `%` refers to how the user would like to be notified when someone enters a queue of their rs level. `%` could be `all`, `3/4`, or `silent`.")
                external_embed.add_field(name="Users (RS Level + Pings) cont.", value=f"If `%` is set to `all`, the user will be pinged everytime someone joins a queue of their rs level. If `%` is set to `3/4`, they will be pinged when the queue of their rs level is 3/4. If `%` is set to `silent`, they will not be pinged when someone joins a queue of their rs level.")
                external_embed.add_field(name="Multiple RS Levels", value=f"If a user wants to be notified when someone joins a queue of a different rs level than their current rs level, run the `!user # %` command again with `#` as whatever rs level they want that is below their current rs level.")
                external_embed.add_field(name="Removing Users (RS Level + Pings)", value=f"If a user wants to remove how they'll be pinged for a queue (that they previously wanted to), they can remove it by running `!remove #` where `#` is the rs level they do not want to be notified of.")
                external_embed.add_field(name="Seeing RS Level and Pings", value=f"If you want to see what your current rs level + pings are (from the `!user # %` command), run `!current` and it will show you.")
                await ctx.send(embed=external_embed)
            else:
                await ctx.send(f"{option} is not a valid option to the `!help` command, the current options are `role`, `queue`, `rsmod`, and `other`")

