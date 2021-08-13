"""Setup help command."""
from routines.cogs import queue
import discord
from routines.commands import CommandRoutine

from bot import LOGGER
from bot import TESTING

class Help(CommandRoutine):
    def actions(self):
        @self.bot.group(invoke_without_command=True)
        async def help(ctx, option=None):
            if option is None:
                send = ""
                send += "There are multiple sections to the help command, and they can be accessed by adding another parameter to the help command, to specify the group you would like more information on. Below is the current categories to the help command:"
                send += "```Roles (their types and how to get them): type `!help roles` (or role/r)```"
                send += "```The Queueing System (how to join, leave, add a friend, etc.): type `!help queue` (or q/queues)```"
                send += "```Rsmods (showing mods when you enter a queue to alert players what mods are on your ships/whatever else you want them to know): type `!help rsmod` (or rs/rsmods)```"
                send += "```External Servers and The Clubs: type `!help external` (or e)```"
                send += "```Other useful commands: type `!help other` (or o)```"
                send += "Also there's `!github` if you want to see my horrible open source code!"
                await ctx.send(send)
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
                queue_embed.add_field(name=f"External Servers", value=f"These commands shown above will also work in servers outside of The Clubs, and function very much the same. If you want to join a queue of a **lower** rs level than what your current role is (i.e. An rs9 player joining an rs7 queue), append the rs level at the end of the command (`+1 7` for example). The same applies for the `!queue` command, only it shows the rs level of the queue you specify.")
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
                    external_embed.add_field(name="Connecting your server to the clubs", value=f"If you want to connect your corporation's discord server to The Clubs so you can run Red Stars from the comfort of your discord server, simply add the bot to your discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=805960284543385650&permissions=54224276544&scope=bot%20applications.commands) and follow the steps")
                external_embed.add_field(name="First Time Setup", value=f"Run `!connect # %` (where `#` is the minimum rs level of your server and `%` is the maximum), and your server will be connected to The Clubs.")
                external_embed.add_field(name="Setting up max RS levels", value=f"To change the min/max RS level of your server, run `!connect # %` where `#` is the minimum rs level of your server and `%` is the maximum.")
                external_embed.add_field(name="Users and Queues", value=f"To allow users to join queues, they'll need to have a role specifying their rs level. In order to do this, use the `!level # type @<>` command, where `#` is the rs level, and `type` is either `all`, `3/4`, or `silent`. This allows users to decide if how they want to get notified (everytime, when the queue is 3/4, or not at all) `@<>` is the role that players in that rs level have. If you want to change the role, simply run the command again.")
                external_embed.add_field(name="Seeing Roles", value=f"Use the `!current` command to show what roles are currently connected to the bot. If you want to add more, use the `!level # type @<>` command.")
                external_embed.add_field(name="Turning on/off the Queueing System", value=f"If you want to turn off the queueing system (pinging roles, showing queues, queue commands, etc.), run the `!hide` command to have the bot turn off the queueing system in this server. If you want to turn it back on, use the `!show` command. Note this command can only be run by an administrator of the server.")
                external_embed.add_field(name="Disconnecting", value=f"If you want this server to be disconnected from The Clubs, have an admin run the `!disconnect` command.")
                external_embed.add_field(name="Joining/Leaving/Showing Queues", value=f"Go to the queue section of the `!help` command to get information on the queueing system (`!help q`).")
                await ctx.send(embed=external_embed)
            else:
                await ctx.send(f"{option} is not a valid option to the `!help` command, the current options are `role`, `queue`, `rsmod`, `external`, and `other`")

