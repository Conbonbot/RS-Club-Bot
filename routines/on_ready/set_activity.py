"""Set bot activity after server login."""
import discord
from routines.on_ready import OnReadyEvent
from bot import LOGGER


class SetActivity(OnReadyEvent):
    """Set bot activity on server login."""
    def actions(self):
        @self.bot.event
        async def on_ready():
            LOGGER.info(f'{self.bot.user.name} has connected to Discord!')
            LOGGER.debug('Found the following channels:')
            for channel in self.bot.get_all_channels():
                LOGGER.debug(channel)
            return await self.bot.change_presence(activity=discord.Activity(type=1, name="RS Queueing"))
