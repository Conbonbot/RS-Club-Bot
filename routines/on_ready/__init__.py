"""Parent module for OnReadyEvents."""
import abc

# This is required for the dynamic import chain to work.
import os
from os.path import dirname, basename
__all__ = [basename(f)[:-3] for f in os.listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]

import routines


class OnReadyEvent(routines.Routine):
    """Parent class for OnReadyEvents. Used for dynamic loading."""

    @abc.abstractmethod
    def actions(self):
        """Abstract method for actions."""


# This has to go here to ensure the dynamic import chain works.
from routines.on_ready import *
