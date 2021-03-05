"""Parent module for CommandRoutines."""
import abc
import routines

# This is required for the dynamic import chain to work.
import os
from os.path import dirname, basename
__all__ = [basename(f)[:-3] for f in os.listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]


class CommandRoutine(routines.Routine):
    """Parent class for commands. Used for dynamic loading."""

    @abc.abstractmethod
    def actions(self):
        """Abstract method for actions."""


# This has to go here to ensure the dynamic import chain works.
from routines.commands import *
