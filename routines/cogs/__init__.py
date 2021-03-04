"""Parent Module for Cogs."""
from discord.ext import commands

# This is required for the dynamic import chain to work.
import os
from os.path import dirname, basename
__all__ = [basename(f)[:-3] for f in os.listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]


class Cog(commands.Cog):
    """Parent class for Cogs. Used for dynamic loading."""


# This has to go here to ensure the dynamic import chain works.
from routines.cogs import *
